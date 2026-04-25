#!/usr/bin/env python3
"""Run the perturbation benchmark's perturb → review → score pipeline with
`coarse` as the reviewer instead of `openaireview review`.

Reuses the existing `perturb` and `score` CLI commands (via subprocess);
the review step dispatches to `competitors.coarse_adapter` which shells
out to `coarse_driver.py` inside coarse's venv.

Usage:
  # Pre-flight estimate (no LLM calls)
  python benchmarks/perturbation/run_competitor_benchmark.py \\
      benchmarks/perturbation/configs/coarse_short.yaml --estimate-cost

  # Full run
  python benchmarks/perturbation/run_competitor_benchmark.py \\
      benchmarks/perturbation/configs/coarse_short.yaml --parallel 3

Output layout (shares perturb artifacts with the openaireview pipeline
when `results_dir` points at the same directory):

  <results_dir>/
    perturb/<error_type>/paper_00N/...
    <model_slug>/<error_type>/coarse/paper_00N/review/*.json
    <model_slug>/<error_type>/coarse/paper_00N/score/<score_method>/*.json
    coarse_cost_estimate_<config>.json   (when --estimate-cost)
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import MISSING, asdict, dataclass, field, fields
from pathlib import Path

import yaml
from datasets import load_dataset

sys.path.insert(0, str(Path(__file__).resolve().parent))
from competitors import (
    CostJob,
    Job,
    estimate_coarse_cost,
    model_slug,
    run_coarse_review,
)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

@dataclass
class Config:
    max_papers: int = 2
    length: str = field(default="short", metadata={"choices": ["short", "medium", "long"]})
    error_type: str = field(default="surface", metadata={"choices": ["surface", "formal", "all"]})
    score_method: str = field(default="llm", metadata={"choices": ["llm", "fuzzy", "semantic"]})
    perturb_model: str = "google/gemini-3-flash-preview"
    score_model: str = "google/gemini-3-flash-preview"
    coarse_models: list[str] = field(default_factory=lambda: ["google/gemini-3-flash-preview"])
    results_dir: str = "results"


def load_config(path: Path) -> Config:
    with path.open() as f:
        data = yaml.safe_load(f) or {}
    valid_keys = {f.name for f in fields(Config)}
    unknown = set(data) - valid_keys
    if unknown:
        raise ValueError(f"Unknown config keys in {path}: {sorted(unknown)}")
    for f in fields(Config):
        choices = f.metadata.get("choices")
        if choices is None or f.name not in data:
            continue
        if data[f.name] not in choices:
            raise ValueError(
                f"{path}: {f.name}={data[f.name]!r} not in choices {choices}"
            )
    return Config(**data)


# ---------------------------------------------------------------------------
# Helpers (mirrors run_pipeline.py)
# ---------------------------------------------------------------------------

def paper_length(paper: dict) -> int:
    text = re.sub(r'\\[a-zA-Z]+\*?', ' ', paper['text'])
    text = re.sub(r'[\{\}\$\[\]]', ' ', text)
    return len(text.split())


def _openaireview_bin() -> str:
    """Find the openaireview CLI — prefer the current venv, else PATH."""
    here = Path(sys.executable).parent / "openaireview"
    if here.exists():
        return str(here)
    return "openaireview"


def run(cmd: list[str]) -> int:
    if cmd and cmd[0] == "openaireview":
        cmd = [_openaireview_bin()] + cmd[1:]
    print(f"    $ {' '.join(str(c) for c in cmd)}", flush=True)
    return subprocess.run(cmd).returncode


def load_papers(cfg: Config) -> list[dict]:
    print("Loading proof-pile dataset (streaming)...")
    ds = load_dataset(
        "hoskinson-center/proof-pile",
        split="train",
        streaming=True,
        trust_remote_code=True,
    )

    papers_short: list[dict] = []
    papers_medium: list[dict] = []
    papers_long: list[dict] = []
    if cfg.length == "short":
        target = papers_short
    elif cfg.length == "medium":
        target = papers_medium
    else:
        target = papers_long

    inspected = 0
    for paper in ds:
        meta = json.loads(paper["meta"]) if isinstance(paper["meta"], str) else paper["meta"]
        if meta.get("config", "") != "arxiv":
            continue
        inspected += 1
        n = paper_length(paper)
        if 2000 < n <= 7000:
            papers_short.append(paper)
        elif 7000 < n <= 17000:
            papers_medium.append(paper)
        else:
            papers_long.append(paper)
        if len(target) >= cfg.max_papers:
            break

    print(
        f"Inspected {inspected} arxiv papers "
        f"(short={len(papers_short)}, medium={len(papers_medium)}, long={len(papers_long)})"
    )
    print(f"Collected {len(target)} arxiv papers for length={cfg.length}\n")
    return target


# ---------------------------------------------------------------------------
# Pipeline stages
# ---------------------------------------------------------------------------

def perturb(papers: list[dict], cfg: Config) -> None:
    """Generate perturbations for each paper (skips if already present)."""
    results_dir = Path(cfg.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    for i, paper in enumerate(papers, start=1):
        paper_label = f"paper_{i:03d}"
        perturb_dir = results_dir / "perturb" / cfg.error_type / paper_label
        perturb_dir.mkdir(parents=True, exist_ok=True)

        existing_manifest = list(perturb_dir.glob("*_perturbations.json"))
        existing_corrupted = list(perturb_dir.glob("*_corrupted.md"))
        if existing_manifest and existing_corrupted:
            print(f"  [skip] perturb exists for {paper_label} ({existing_corrupted[0].name})")
            continue

        print(f"{'='*60}\nPaper {i:03d}/{len(papers)}  ({paper_length(paper):,} words)\n{'='*60}")
        tmp_path = perturb_dir / f"paper_{i:03d}.md"
        tmp_path.write_text(paper["text"])

        print(f"\n  [1] Perturb  (model: {model_slug(cfg.perturb_model)})")
        rc = run(["openaireview", "perturb", str(tmp_path),
                  "--error_type", cfg.error_type,
                  "--output-dir", str(perturb_dir),
                  "--model", cfg.perturb_model])
        if rc != 0:
            print(f"  perturb failed (exit {rc}), skipping paper")


def _corrupted_paths(cfg: Config, papers: list[dict]) -> list[tuple[str, Path]]:
    """Return [(paper_label, corrupted.md path), ...] in order."""
    results_dir = Path(cfg.results_dir)
    out: list[tuple[str, Path]] = []
    for i, _paper in enumerate(papers, start=1):
        paper_label = f"paper_{i:03d}"
        perturb_dir = results_dir / "perturb" / cfg.error_type / paper_label
        corrupted = max(perturb_dir.glob("*_corrupted.md"),
                        key=lambda p: p.stat().st_mtime, default=None)
        if corrupted is None:
            print(f"  [warn] no corrupted paper for {paper_label}")
            continue
        out.append((paper_label, corrupted))
    return out


def review(papers: list[dict], cfg: Config, parallel: int) -> None:
    """Run coarse on each (paper, model) pair, parallel up to `parallel`."""
    results_dir = Path(cfg.results_dir)
    pairs = _corrupted_paths(cfg, papers)
    if not pairs:
        print("No corrupted papers found; run perturb first.")
        return

    jobs: list[Job] = []
    for model in cfg.coarse_models:
        slug = model_slug(model)
        for paper_label, corrupted in pairs:
            review_dir = results_dir / slug / cfg.error_type / "coarse" / paper_label / "review"
            review_dir.mkdir(parents=True, exist_ok=True)
            jobs.append(Job(
                paper=corrupted,
                model=model,
                out_json=review_dir / f"{corrupted.stem}.json",
                paper_label=paper_label,
            ))

    print(f"\n  [2] Review  ({len(jobs)} jobs across {len(cfg.coarse_models)} models, "
          f"parallel={parallel})")
    results = run_coarse_review(jobs, parallel=parallel)

    n_ok = sum(1 for r in results if r.ok)
    print(f"\n  [2] Review done: {n_ok}/{len(results)} succeeded")
    for r in results:
        if not r.ok:
            print(f"    FAILED: {r.job.paper_label} / {model_slug(r.job.model)}: {r.error[:200]}")


def score(papers: list[dict], cfg: Config) -> None:
    """Score each coarse review against its perturbation manifest."""
    results_dir = Path(cfg.results_dir)

    for i, paper in enumerate(papers, start=1):
        paper_label = f"paper_{i:03d}"
        perturb_dir = results_dir / "perturb" / cfg.error_type / paper_label
        manifest = max(perturb_dir.glob("*_perturbations.json"),
                       key=lambda p: p.stat().st_mtime, default=None)
        if not manifest:
            print(f"  No manifest for {paper_label}, skipping score")
            continue

        for model in cfg.coarse_models:
            slug = model_slug(model)
            review_dir = results_dir / slug / cfg.error_type / "coarse" / paper_label / "review"
            score_dir = results_dir / slug / cfg.error_type / "coarse" / paper_label / "score" / cfg.score_method
            score_dir.mkdir(parents=True, exist_ok=True)

            review_json = max(review_dir.glob("*.json"),
                              key=lambda p: p.stat().st_mtime, default=None)
            if not review_json:
                print(f"  No review for {slug}/{paper_label}, skipping")
                continue

            print(f"\n  [3] Score   ({slug} / {paper_label})")
            rc = run(["openaireview", "score", str(manifest), str(review_json),
                      "--model", cfg.score_model,
                      "--method", cfg.score_method,
                      "--output-dir", str(score_dir)])
            if rc != 0:
                print(f"  score failed (exit {rc}), continuing")


# ---------------------------------------------------------------------------
# Cost estimate
# ---------------------------------------------------------------------------

def estimate_cost(papers: list[dict], cfg: Config, config_path: Path, parallel: int) -> None:
    """Run coarse's pre-flight cost estimator on each (paper, model); print table."""
    results_dir = Path(cfg.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    pairs = _corrupted_paths(cfg, papers)

    if not pairs:
        print("\n  [warn] no corrupted papers found — estimating against original text.")
        # Write originals so extract_file has something to read
        pairs = []
        for i, paper in enumerate(papers, start=1):
            paper_label = f"paper_{i:03d}"
            perturb_dir = results_dir / "perturb" / cfg.error_type / paper_label
            perturb_dir.mkdir(parents=True, exist_ok=True)
            p = perturb_dir / f"{paper_label}.md"
            if not p.exists():
                p.write_text(paper["text"])
            pairs.append((paper_label, p))

    jobs: list[CostJob] = []
    tmp_dir = results_dir / "_cost_tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    for model in cfg.coarse_models:
        slug = model_slug(model)
        for paper_label, md_path in pairs:
            jobs.append(CostJob(
                paper=md_path, model=model, paper_label=paper_label,
                out_json=tmp_dir / f"{paper_label}__{slug}.json",
            ))

    print(f"\n  Estimating cost for {len(jobs)} (paper, model) pairs (parallel={parallel})...")
    results = estimate_coarse_cost(jobs, parallel=parallel)

    # Build a table: rows = papers, columns = models
    slugs = [model_slug(m) for m in cfg.coarse_models]
    by_pair: dict[tuple[str, str], float] = {}
    words_by_paper: dict[str, int] = {
        label: paper_length(p) for (label, p), _ in zip(
            [(lbl, paper) for lbl, paper in
             zip([f"paper_{i:03d}" for i in range(1, len(papers)+1)], papers)],
            range(len(papers)))
    }
    token_by_pair: dict[tuple[str, str], int] = {}
    for r in results:
        key = (r.job.paper_label, model_slug(r.job.model))
        by_pair[key] = r.total_cost_usd if r.ok else 0.0
        token_by_pair[key] = r.token_estimate if r.ok else 0

    # Print
    print("\n" + "="*80)
    print(f"Cost estimate — {config_path}")
    print("="*80)
    labels = sorted({k[0] for k in by_pair})
    header = f"{'paper':<14} {'words':>8}   " + "  ".join(f"{s:>30}" for s in slugs)
    print(header)
    print("-" * len(header))
    totals = {s: 0.0 for s in slugs}
    for label in labels:
        row = f"{label:<14} {words_by_paper.get(label, 0):>8,}   "
        for s in slugs:
            cost = by_pair.get((label, s), 0.0)
            totals[s] += cost
            row += f"{'$'+format(cost,'.4f'):>30}  "
        print(row.rstrip())
    print("-" * len(header))
    total_total = sum(totals.values())
    totals_row = f"{'TOTAL':<14} {'':>8}   " + "  ".join(
        f"{'$'+format(totals[s],'.4f'):>30}" for s in slugs)
    print(totals_row)
    print(f"\nConfig total: ${total_total:.4f}")
    print(f"(coarse applies a 1.3x buffer → ~${total_total * 1.3:.4f} upper bound)")

    # Persist
    out_path = results_dir / f"coarse_cost_estimate_{config_path.stem}.json"
    out_path.write_text(json.dumps({
        "config": str(config_path),
        "models": cfg.coarse_models,
        "per_pair": {f"{p}__{s}": v for (p, s), v in by_pair.items()},
        "per_model_totals": totals,
        "total_usd": total_total,
        "buffered_usd": total_total * 1.3,
    }, indent=2))
    print(f"\nSaved: {out_path}")


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def report(cfg: Config, config_path: Path) -> None:
    """Call the report generator to write a markdown summary."""
    report_gen = Path(__file__).parent / "generate_report.py"
    out_dir = Path(cfg.results_dir).parent / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    import datetime as _dt
    stamp = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"{Path(cfg.results_dir).name}_{stamp}.md"
    rc = run([sys.executable, str(report_gen), cfg.results_dir, "--out", str(out_path)])
    if rc != 0:
        print(f"  report generation failed (exit {rc})")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _schema_help() -> str:
    lines = ["config schema (set these in the YAML file):", ""]
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
        description="Run the perturbation benchmark with coarse as the reviewer",
        epilog=_schema_help(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("config", type=Path, help="Path to YAML config file")
    parser.add_argument("--stages", type=str, default="perturb,review,score,report",
                        help="Comma-separated subset: perturb,review,score,report")
    parser.add_argument("--estimate-cost", action="store_true",
                        help="Print pre-flight cost estimate and exit (no LLM calls)")
    parser.add_argument("--parallel", type=int, default=1,
                        help="Concurrent (paper, model) pairs during review (default: 1)")
    args = parser.parse_args()
    valid = {"perturb", "review", "score", "report"}
    args.stages = [s.strip() for s in args.stages.split(",") if s.strip()]
    invalid = set(args.stages) - valid
    if invalid:
        parser.error(f"--stages: unknown stage(s) {sorted(invalid)}; valid: {sorted(valid)}")
    return args


def main() -> None:
    args = parse_args()
    cfg = load_config(args.config)

    results_dir = Path(cfg.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    resolved = asdict(cfg)
    with (results_dir / f"coarse_config_{args.config.stem}.yaml").open("w") as f:
        yaml.safe_dump(resolved, f, sort_keys=False)
    print("Resolved config:")
    print(yaml.safe_dump(resolved, sort_keys=False))

    papers = load_papers(cfg)

    if args.estimate_cost:
        # Need perturb outputs to estimate on the corrupted text; run perturb if missing
        if "perturb" in args.stages:
            perturb(papers, cfg)
        estimate_cost(papers, cfg, args.config, parallel=max(2, args.parallel))
        print("\n(Exiting after estimate. Re-run without --estimate-cost to execute.)")
        return

    print(f"Stages to run: {', '.join(args.stages)}\n")
    if "perturb" in args.stages:
        perturb(papers, cfg)
    if "review" in args.stages:
        review(papers, cfg, parallel=args.parallel)
    if "score" in args.stages:
        score(papers, cfg)
    if "report" in args.stages:
        report(cfg, args.config)
    print(f"\nAll done. Results in {cfg.results_dir}/")


if __name__ == "__main__":
    main()
