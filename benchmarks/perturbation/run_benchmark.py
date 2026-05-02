#!/usr/bin/env python3
"""Unified runner for the perturbation benchmark.

Replaces the previous stack of `run_pipeline.py`, `run_competitor_benchmark.py`,
`run_reviewer3_benchmark.py`, and `run_all_domains.py`. One CLI handles:

  * Single config (positional)              — like the old run_pipeline.
  * Many configs (--configs <glob>)         — like the old run_all_domains.
  * Any system (`system:` in YAML)  — openaireview | coarse | reviewer3.
  * Stage selection (--stages)              — prepare,review,score,report.
  * Pre-flight cost estimate (--estimate-cost) for systems that support it.

Pipeline stages (always in this order):
  prepare → review → score → report

Within review, all configs that share a system are gathered into one
scheduler so workers stay busy across domain boundaries. Different systems
run in their own outer threads, concurrently.

Usage:
  # single domain
  python run_benchmark.py configs/cs_CC.yaml
  # many domains
  python run_benchmark.py --configs configs/full_*.yaml \\
      --parallel-openaireview 2 --parallel-coarse 8
  # cost preview (no LLM calls)
  python run_benchmark.py configs/cs_CC_coarse.yaml --estimate-cost

YAML schema (see Config dataclass for full list):
  system: openaireview | coarse | reviewer3   # required
  input_dir: <path>                               # required
  results_dir: <path>                             # required
  models: [<model>, ...]                          # required (openaireview, coarse)
  methods: [zero_shot|local|progressive, ...]     # required for openaireview
  max_tokens: 13000
  min_perturbations: 0
  paper_subset: [paper_001, ...]                  # optional filter
  score_method: llm | fuzzy | semantic
  score_model: <model>
  # reviewer3 extras
  review_mode: author | journal
  poll_interval_s: 5
  poll_timeout_s: 1200
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import subprocess
import sys
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import MISSING, asdict, dataclass, field, fields
from pathlib import Path
from typing import Any

import yaml

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _prepare import discover_units, prepare_units, write_paper_index  # noqa: E402
from systems import SYSTEMS, System, ReviewJob, get_system  # noqa: E402

# Re-export generate_report as a callable function (refactored to expose it).
from generate_report import generate_report  # noqa: E402


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

@dataclass
class Config:
    system: str = field(default="openaireview",
                            metadata={"choices": ["openaireview", "coarse", "reviewer3"]})
    input_dir: str = ""
    results_dir: str = ""
    max_tokens: int = 13000
    min_perturbations: int = 0
    paper_subset: list[str] = field(default_factory=list)
    score_method: str = field(default="llm", metadata={"choices": ["llm", "fuzzy", "semantic"]})
    score_model: str = "google/gemini-3-flash-preview"
    # OAIR + COARSE
    models: list[str] = field(default_factory=list)
    # OAIR
    methods: list[str] = field(default_factory=list)
    # REVIEWER3
    review_mode: str = field(default="author", metadata={"choices": ["author", "journal"]})
    poll_interval_s: float = 5.0
    poll_timeout_s: float = 1200.0
    # Legacy aliases (read on load, normalized into models/methods).
    review_models: list[str] = field(default_factory=list)
    review_methods: list[str] = field(default_factory=list)
    coarse_models: list[str] = field(default_factory=list)


def _infer_system(data: dict, path: Path) -> str:
    if data.get("coarse_models"):
        return "coarse"
    if data.get("review_models") or data.get("review_methods"):
        return "openaireview"
    if data.get("review_mode") or "reviewer3" in path.name:
        return "reviewer3"
    return "openaireview"


def load_config(path: Path) -> Config:
    with path.open() as f:
        data = yaml.safe_load(f) or {}
    valid = {f.name for f in fields(Config)}
    unknown = set(data) - valid
    if unknown:
        raise ValueError(f"Unknown config keys in {path}: {sorted(unknown)}")
    if "system" not in data:
        data["system"] = _infer_system(data, path)
    for f in fields(Config):
        choices = f.metadata.get("choices")
        if choices is None or f.name not in data:
            continue
        if data[f.name] not in choices:
            raise ValueError(f"{path}: {f.name}={data[f.name]!r} not in choices {choices}")
    cfg = Config(**data)
    # Normalize legacy field names.
    if not cfg.models:
        cfg.models = cfg.review_models or cfg.coarse_models
    if not cfg.methods:
        cfg.methods = cfg.review_methods
    if not cfg.input_dir:
        raise ValueError(f"{path}: input_dir is required")
    if not cfg.results_dir:
        raise ValueError(f"{path}: results_dir is required")
    if cfg.system in ("openaireview", "coarse") and not cfg.models:
        raise ValueError(f"{path}: system={cfg.system!r} requires `models`")
    if cfg.system == "openaireview" and not cfg.methods:
        raise ValueError(f"{path}: system=openaireview requires `methods`")
    return cfg


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]


def _abs_path(p: str) -> Path:
    pp = Path(p)
    return pp if pp.is_absolute() else (REPO_ROOT / pp).resolve()


def _openaireview_bin() -> str:
    here = Path(sys.executable).parent / "openaireview"
    return str(here) if here.exists() else "openaireview"


_print_lock = threading.Lock()


def _log(msg: str) -> None:
    with _print_lock:
        print(msg, flush=True)


def run_score(cmd: list[str], tag: str) -> int:
    if cmd and cmd[0] == "openaireview":
        cmd = [_openaireview_bin()] + cmd[1:]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        _log(f"[score:{tag}] (exit {proc.returncode})\n{proc.stdout}{proc.stderr}")
    return proc.returncode


# ---------------------------------------------------------------------------
# Stage 1 — prepare
# ---------------------------------------------------------------------------

def prepare(cfg: Config, results_dir: Path) -> list:
    input_dir = _abs_path(cfg.input_dir)
    if not input_dir.is_dir():
        raise SystemExit(f"input_dir does not exist: {input_dir}")
    results_dir.mkdir(parents=True, exist_ok=True)

    units = discover_units(input_dir, results_dir)
    if not units:
        raise SystemExit(f"No (paper, error_type) units found under {input_dir}")
    write_paper_index(units, results_dir)
    kept_units, report = prepare_units(units, results_dir,
                                       max_tokens=cfg.max_tokens,
                                       min_perturbations=cfg.min_perturbations)
    (results_dir / "prepare_report.json").write_text(json.dumps(report, indent=2))

    if cfg.paper_subset:
        kept_units = [u for u in kept_units if u.paper_label in cfg.paper_subset]

    n_total = len(report["units"])
    n_excluded = sum(1 for u in report["units"] if u.get("excluded_by_min_perturbations"))
    _log(f"[prepare {results_dir.name}] {len(kept_units)}/{n_total} units kept "
         f"(excluded by min_perturbations={cfg.min_perturbations}: {n_excluded})")
    return kept_units


# ---------------------------------------------------------------------------
# Stage 2 — review (per-cell scheduler, possibly across many configs)
# ---------------------------------------------------------------------------

def _review_one_system(
    system: System,
    jobs_by_cell: dict[tuple, list[ReviewJob]],
    parallel_per_cell: int,
) -> None:
    total = sum(len(v) for v in jobs_by_cell.values())
    if total == 0:
        _log(f"[review/{system.name}] all reviews already complete")
        return
    _log(f"[review/{system.name}] dispatching {total} jobs across "
         f"{len(jobs_by_cell)} cell(s); parallel_per_cell={parallel_per_cell}")

    counters = {"done": 0, "failed": 0}
    lock = threading.Lock()

    def report_done(tag: str, ok: bool) -> None:
        with lock:
            counters["done"] += 1
            if not ok:
                counters["failed"] += 1
            if counters["done"] % 10 == 0 or counters["done"] == total or not ok:
                _log(f"[review/{system.name}] {counters['done']}/{total} "
                     f"({counters['failed']} failed)  last={tag}")

    def cell_worker(cell_key, jobs: list[ReviewJob]) -> None:
        results = system.run_jobs(cell_key, jobs, parallel_per_cell)
        for r in results:
            report_done(r.job.tag, r.ok)

    with ThreadPoolExecutor(max_workers=max(1, len(jobs_by_cell))) as outer:
        for cell_key, jobs in jobs_by_cell.items():
            outer.submit(cell_worker, cell_key, jobs)


def review(
    grouped: dict[System, list[tuple[Config, Path, list]]],
    parallel_overrides: dict[str, int],
    default_parallel: int,
) -> None:
    threads: list[threading.Thread] = []
    for system, entries in grouped.items():
        jobs_by_cell: dict[tuple, list[ReviewJob]] = defaultdict(list)
        for cfg, results_dir, units in entries:
            for cell_key, job in system.build_jobs(units, asdict(cfg), results_dir):
                jobs_by_cell[cell_key].append(job)
        parallel = parallel_overrides.get(system.name, default_parallel)
        t = threading.Thread(target=_review_one_system,
                             args=(system, dict(jobs_by_cell), parallel),
                             name=f"review-{system.name}")
        t.start()
        threads.append(t)
    for t in threads:
        t.join()


# ---------------------------------------------------------------------------
# Stage 3 — score
# ---------------------------------------------------------------------------

def score(
    grouped: dict[System, list[tuple[Config, Path, list]]],
) -> None:
    n_total = n_done = n_skip = n_fail = 0
    for system, entries in grouped.items():
        for cfg, results_dir, units in entries:
            for cell_key, job in system.build_jobs(units, asdict(cfg), results_dir):
                # Walk the score dir whether or not review was done this run.
                # Score dir mirrors review dir but ends with `score/<method>/`.
                review_dir = job.review_dir
                paper_label_dir = review_dir.parent
                score_dir = paper_label_dir / "score" / cfg.score_method
                score_dir.mkdir(parents=True, exist_ok=True)
                if any(score_dir.glob("*_score.json")):
                    n_skip += 1
                    continue
                review_json = system.pick_review_for_score(review_dir)
                if not review_json:
                    n_skip += 1
                    continue
                # Locate the staged manifest: every unit has it under
                # results_dir/perturb/<error_type>/<paper_label>/.
                err, paper = job.paper_label.split("/", 1)
                manifest_dir = results_dir / "perturb" / err / paper
                manifests = list(manifest_dir.glob("*_perturbations.json"))
                if not manifests:
                    n_skip += 1
                    continue
                manifest = max(manifests, key=lambda p: p.stat().st_mtime)
                rc = run_score(
                    ["openaireview", "score", str(manifest), str(review_json),
                     "--model", cfg.score_model,
                     "--method", cfg.score_method,
                     "--output-dir", str(score_dir)],
                    tag=job.tag,
                )
                n_total += 1
                if rc == 0:
                    n_done += 1
                else:
                    n_fail += 1
    _log(f"[score] done={n_done} failed={n_fail} skipped={n_skip} (total attempted={n_total})")


# ---------------------------------------------------------------------------
# Stage 4 — report
# ---------------------------------------------------------------------------

def report(results_dirs: list[Path], out_path: Path | None = None) -> Path | None:
    if not results_dirs:
        return None
    md = generate_report(results_dirs)
    if out_path is None:
        # Write next to the (first) results dir's parent under reports/.
        reports_dir = results_dirs[0].parent / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        stamp = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        stem = "_".join(d.name for d in results_dirs)
        out_path = reports_dir / f"{stem}_{stamp}.md"
    out_path.write_text(md)
    _log(f"[report] wrote {out_path}")
    return out_path


# ---------------------------------------------------------------------------
# Cost estimate
# ---------------------------------------------------------------------------

def estimate_cost(
    grouped: dict[System, list[tuple[Config, Path, list]]],
    parallel: int,
) -> None:
    for system, entries in grouped.items():
        if not system.supports_cost_estimate():
            _log(f"[cost/{system.name}] system does not support cost estimation; skipping")
            continue
        for cfg, results_dir, units in entries:
            cr = system.estimate_cost(units, asdict(cfg), results_dir, parallel=parallel)
            _log(f"\n[cost/{system.name}/{results_dir.name}] {len(cr.rows)} jobs, "
                 f"total ${cr.total_usd:.4f} (1.3x buffer ~ ${cr.total_usd * 1.3:.4f})")
            for row in cr.rows:
                tag = "OK" if row["ok"] else f"ERR: {row['error'][:60]}"
                _log(f"  {row['unit']:<32} {row['model_slug']:<30} "
                     f"${row['cost_usd']:.4f} (tokens~{row['tokens']})  {tag}")
            out = results_dir / f"cost_estimate_{system.name}.json"
            out.write_text(json.dumps({
                "system": system.name,
                "total_usd": cr.total_usd,
                "rows": cr.rows,
            }, indent=2))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _schema_help() -> str:
    lines = ["config schema (set in YAML):", ""]
    for f in fields(Config):
        if f.default is not MISSING:
            default = f.default
        elif f.default_factory is not MISSING:  # type: ignore[misc]
            default = f.default_factory()
        else:
            default = "<required>"
        type_name = getattr(f.type, "__name__", str(f.type))
        line = f"  {f.name}: {type_name} = {default!r}"
        choices = f.metadata.get("choices")
        if choices:
            line += f"  (choices: {' | '.join(choices)})"
        lines.append(line)
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Unified runner for the perturbation benchmark.",
        epilog=_schema_help(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("config", nargs="?", type=Path,
                        help="Single config YAML (mutually exclusive with --configs).")
    parser.add_argument("--configs", nargs="+", type=Path, default=None,
                        help="Multiple config YAMLs (glob expansion done by your shell).")
    parser.add_argument("--stages", default="prepare,review,score,report",
                        help="Comma-separated subset: prepare,review,score,report.")
    parser.add_argument("--estimate-cost", action="store_true",
                        help="Print cost estimate and exit (no LLM calls).")
    parser.add_argument("--parallel-per-cell", type=int, default=1,
                        help="Default workers per cell; overridable per system.")
    parser.add_argument("--parallel-openaireview", type=int, default=None,
                        help="Override parallel-per-cell for the openaireview system.")
    parser.add_argument("--parallel-coarse", type=int, default=None,
                        help="Override parallel-per-cell for the coarse system.")
    parser.add_argument("--parallel-reviewer3", type=int, default=None,
                        help="Override parallel-per-cell for the reviewer3 system.")
    args = parser.parse_args()
    if not args.config and not args.configs:
        parser.error("provide a positional config or --configs")
    if args.config and args.configs:
        parser.error("use either positional config or --configs, not both")
    valid = {"prepare", "review", "score", "report"}
    args.stages = [s.strip() for s in args.stages.split(",") if s.strip()]
    invalid = set(args.stages) - valid
    if invalid:
        parser.error(f"--stages: unknown {sorted(invalid)}; valid: {sorted(valid)}")
    return args


def main() -> None:
    args = parse_args()
    config_paths = [args.config] if args.config else args.configs
    configs = [(p, load_config(p)) for p in config_paths]

    overrides = {}
    if args.parallel_openaireview is not None:
        overrides["openaireview"] = args.parallel_openaireview
    if args.parallel_coarse is not None:
        overrides["coarse"] = args.parallel_coarse
    if args.parallel_reviewer3 is not None:
        overrides["reviewer3"] = args.parallel_reviewer3

    # Resolve results dirs and dump resolved configs.
    grouped: dict[System, list[tuple[Config, Path, list]]] = defaultdict(list)
    for path, cfg in configs:
        results_dir = _abs_path(cfg.results_dir)
        results_dir.mkdir(parents=True, exist_ok=True)
        with (results_dir / "config.yaml").open("w") as f:
            yaml.safe_dump(asdict(cfg), f, sort_keys=False)
        units = []
        if "prepare" in args.stages or args.estimate_cost or "review" in args.stages or "score" in args.stages:
            units = prepare(cfg, results_dir) if "prepare" in args.stages or args.estimate_cost \
                else _discover_only(cfg, results_dir)
        grouped[get_system(cfg.system)].append((cfg, results_dir, units))

    if args.estimate_cost:
        estimate_cost(grouped, parallel=max(2, args.parallel_per_cell))
        _log("\n(Exiting after cost estimate.)")
        return

    if "review" in args.stages:
        review(grouped, overrides, default_parallel=args.parallel_per_cell)
    if "score" in args.stages:
        score(grouped)
    if "report" in args.stages:
        results_dirs = [results_dir for entries in grouped.values()
                        for _cfg, results_dir, _u in entries]
        report(results_dirs)
    _log("[run_benchmark] done")


def _discover_only(cfg: Config, results_dir: Path) -> list:
    """When --stages skips prepare, still discover already-staged units."""
    input_dir = _abs_path(cfg.input_dir)
    units = discover_units(input_dir, results_dir)
    if cfg.paper_subset:
        units = [u for u in units if u.paper_label in cfg.paper_subset]
    return units


if __name__ == "__main__":
    main()
