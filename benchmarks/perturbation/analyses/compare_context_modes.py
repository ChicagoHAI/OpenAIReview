#!/usr/bin/env python3
"""Compare three generator-context modes: none | window | related.

TODO: split into `run_context_modes.py` (data generation → raw JSON) and
`report_context_modes.py` (reads JSON → tables/plots). Mirror the
run_pipeline.py / generate_report.py split at the top level. Deferred until
there's a plot to add alongside the table.

Runs `openaireview perturb` for the same set of papers under all three
context modes, segregating outputs by mode. Then reads each mode's manifests
and emits a markdown report that compares:

  - mean prompt tokens per candidate (the multiplier across modes)
  - n_generated / n_valid_structural / n_accepted_by_verifier
  - acceptance_rate (overall)
  - verifier verdict bucket counts (typo-shaped / not-an-error / substantive)

Usage:
  # Fresh run: re-executes perturb under each mode.
  python compare_context_modes.py configs/default.yaml

  # Report-only: skip perturb, just re-read existing manifests.
  python compare_context_modes.py configs/default.yaml --report-only

Layout:

  <results_dir>/
    context_compare/
      none/   perturb/<error_type>/paper_001/...
      window/ perturb/<error_type>/paper_001/...
      related/perturb/<error_type>/paper_001/...
      context_mode_comparison_<YYYY-MM-DD>.json   # raw summary
  benchmarks/perturbation/reports/
    context_mode_comparison_<YYYY-MM-DD>.md        # rendered report
"""

import argparse
import json
import shutil
import statistics
import subprocess
import sys
from dataclasses import replace
from datetime import date
from pathlib import Path

# Reuse the pipeline runner's Config + load_papers so papers are identical
# across modes. This file lives at benchmarks/perturbation/analyses/, so add
# the parent to sys.path.
_THIS = Path(__file__).resolve()
_PERTURB_PKG = _THIS.parents[1]
_BENCHMARKS = _PERTURB_PKG.parent
if str(_BENCHMARKS) not in sys.path:
    sys.path.insert(0, str(_BENCHMARKS))

from perturbation.run_pipeline import (  # type: ignore  # noqa: E402
    Config, load_config, load_papers, paper_length, model_slug, run,
)
from perturbation.extract import CONTEXT_MODES  # type: ignore  # noqa: E402


def _openaireview_cli() -> str:
    """Resolve the openaireview entry point. Prefer the one next to the running
    Python interpreter (venv-aware), then fall back to PATH."""
    sibling = Path(sys.executable).parent / "openaireview"
    if sibling.exists():
        return str(sibling)
    found = shutil.which("openaireview")
    if found:
        return found
    raise RuntimeError(
        "Could not find the `openaireview` CLI. Install the package "
        "(`pip install -e .`) or run this script with the venv's Python."
    )


def _perturb_for_mode(
    cfg: Config,
    mode: str,
    papers: list[dict],
    base_out: Path,
) -> Path:
    """Run openaireview perturb under a given context_mode for all papers.

    Returns the mode-specific perturb output directory, which mirrors the
    default pipeline layout: <mode_dir>/perturb/<error_type>/paper_XXX/
    """
    mode_dir = base_out / mode
    mode_dir.mkdir(parents=True, exist_ok=True)

    for i, paper in enumerate(papers, start=1):
        paper_label = f"paper_{i:03d}"
        perturb_dir = mode_dir / "perturb" / cfg.error_type / paper_label
        perturb_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n[{mode}] Paper {i:03d}/{len(papers)} ({paper_length(paper):,} words)")

        tmp_path = perturb_dir / f"paper_{i:03d}.md"
        tmp_path.write_text(paper["text"])

        cmd = [
            _openaireview_cli(), "perturb", str(tmp_path),
            "--error_type", cfg.error_type,
            "--output-dir", str(perturb_dir),
            "--model", cfg.perturb_model,
            "--context-mode", mode,
            "--context-window", str(cfg.context_window),
            "--related-passages-max", str(cfg.related_passages_max),
            "--verifier-model", cfg.verifier_model,
            "--verifier-reasoning", cfg.verifier_reasoning,
            "--verifier-max-workers", str(cfg.verifier_max_workers),
        ]
        if cfg.skip_verifier:
            cmd.append("--skip-verifier")
        rc = run(cmd)
        if rc != 0:
            print(f"  [{mode}] perturb failed (exit {rc}), skipping paper")
    return mode_dir


def _collect_manifests(mode_dir: Path, error_type: str) -> list[dict]:
    """Read every *_perturbations.json under <mode_dir>/perturb/<error_type>/."""
    root = mode_dir / "perturb" / error_type
    manifests: list[dict] = []
    if not root.exists():
        return manifests
    for paper_dir in sorted(root.iterdir()):
        if not paper_dir.is_dir():
            continue
        matches = list(paper_dir.glob("*_perturbations.json"))
        if not matches:
            continue
        manifest = json.loads(matches[0].read_text())
        manifest["_paper_label"] = paper_dir.name
        manifests.append(manifest)
    return manifests


def _per_mode_summary(manifests: list[dict]) -> dict:
    """Aggregate stats across papers for a single mode."""
    if not manifests:
        return {
            "n_papers": 0,
            "n_candidates": 0,
            "n_generated": 0,
            "n_valid_structural": 0,
            "n_accepted": 0,
            "generation_yield": 0.0,
            "verifier_acceptance_rate": 0.0,
            "acceptance_rate": 0.0,
            "mean_prompt_tokens_per_candidate": None,
            "mean_prompt_tokens_total": None,
            "verifier": {
                "substantive": 0, "typo-shaped": 0,
                "not-an-error": 0, "parse-error": 0,
            },
            "quote_source": {
                "generator": 0, "random-sampled": 0, "none-available": 0,
            },
        }

    n_candidates = sum(m.get("n_candidates", 0) for m in manifests)
    n_generated = sum(m.get("n_generated", 0) for m in manifests)
    n_valid_structural = sum(m.get("n_valid_structural", m.get("n_valid", 0)) for m in manifests)
    n_accepted = sum(m.get("n_injected", 0) for m in manifests)

    # Aggregated (not averaged) to weight each perturbation equally.
    generation_yield = (n_generated / n_candidates) if n_candidates else 0.0
    verifier_acceptance_rate = (n_accepted / n_valid_structural) if n_valid_structural else 0.0
    acceptance_rate = (n_accepted / n_generated) if n_generated else 0.0

    # Prompt tokens — look at generator_stats.{surface,formal}.prompt_tokens
    # and n_candidates. We report two numbers: mean tokens per candidate
    # (controls for paper size) and mean total prompt tokens per call.
    tokens_per_candidate: list[float] = []
    total_prompt_tokens: list[int] = []
    for m in manifests:
        g = m.get("generator_stats", {}) or {}
        for _etype, s in g.items():
            pt = s.get("prompt_tokens")
            nc = s.get("n_candidates")
            if pt is None or not nc:
                continue
            total_prompt_tokens.append(pt)
            tokens_per_candidate.append(pt / nc)

    def _mean(xs):
        return statistics.fmean(xs) if xs else None

    # Verifier verdicts.
    verifier = {"substantive": 0, "typo-shaped": 0, "not-an-error": 0, "parse-error": 0}
    quote_source = {"generator": 0, "random-sampled": 0, "none-available": 0}
    for m in manifests:
        v = m.get("verifier", {}) or {}
        for k in verifier:
            verifier[k] += v.get(k, 0)
        qs = v.get("quote_source", {}) or {}
        for k in quote_source:
            quote_source[k] += qs.get(k, 0)

    return {
        "n_papers": len(manifests),
        "n_candidates": n_candidates,
        "n_generated": n_generated,
        "n_valid_structural": n_valid_structural,
        "n_accepted": n_accepted,
        "generation_yield": generation_yield,
        "verifier_acceptance_rate": verifier_acceptance_rate,
        "acceptance_rate": acceptance_rate,
        "mean_prompt_tokens_per_candidate": _mean(tokens_per_candidate),
        "mean_prompt_tokens_total": _mean(total_prompt_tokens),
        "verifier": verifier,
        "quote_source": quote_source,
    }


def _write_report(
    summaries: dict[str, dict],
    cfg: Config,
    out_path: Path,
) -> None:
    """Write a markdown comparison report."""
    lines = [
        f"# Context-mode comparison — {date.today().isoformat()}",
        "",
        f"- error_type: `{cfg.error_type}` · length: `{cfg.length}` · max_papers: `{cfg.max_papers}`",
        f"- generator: `{cfg.perturb_model}`",
        f"- verifier: `{cfg.verifier_model}` (reasoning={cfg.verifier_reasoning})",
        "",
        "## Summary",
        "",
        "| Mode | Papers | Cands | Gen | Gen yield | Valid (1-4) | Accepted (1-5) | Verif accept | End-to-end | Tokens/cand | Multiplier |",
        "|------|-------:|------:|----:|----------:|------------:|---------------:|-------------:|-----------:|------------:|-----------:|",
    ]
    base_tpc = summaries.get("none", {}).get("mean_prompt_tokens_per_candidate") or None
    for mode in summaries:
        s = summaries.get(mode, {})
        tpc = s.get("mean_prompt_tokens_per_candidate")
        tpc_s = f"{tpc:.0f}" if tpc is not None else "—"
        if base_tpc and tpc:
            mult = f"{tpc/base_tpc:.2f}×"
        elif mode == "none" and tpc is not None:
            mult = "1.00×"
        else:
            mult = "—"
        lines.append(
            f"| {mode} | {s.get('n_papers', 0)} | {s.get('n_candidates', 0)} | "
            f"{s.get('n_generated', 0)} | {s.get('generation_yield', 0.0):.1%} | "
            f"{s.get('n_valid_structural', 0)} | {s.get('n_accepted', 0)} | "
            f"{s.get('verifier_acceptance_rate', 0.0):.1%} | "
            f"{s.get('acceptance_rate', 0.0):.1%} | {tpc_s} | {mult} |"
        )

    lines += [
        "",
        "## Summary (compact)",
        "",
        "| Mode | Papers | Cands | Gen | Gen yield | Accepted (1-5) | End-to-end |",
        "|------|-------:|------:|----:|----------:|---------------:|-----------:|",
    ]
    for mode in summaries:
        s = summaries.get(mode, {})
        lines.append(
            f"| {mode} | {s.get('n_papers', 0)} | {s.get('n_candidates', 0)} | "
            f"{s.get('n_generated', 0)} | {s.get('generation_yield', 0.0):.1%} | "
            f"{s.get('n_accepted', 0)} | {s.get('acceptance_rate', 0.0):.1%} |"
        )

    lines += [
        "",
        "## Verifier verdicts (test #5)",
        "",
        "| Mode | Substantive | Typo-shaped | Not-an-error | Parse-error |",
        "|------|------------:|------------:|-------------:|------------:|",
    ]
    for mode in summaries:
        v = summaries.get(mode, {}).get("verifier", {}) or {}
        lines.append(
            f"| {mode} | {v.get('substantive', 0)} | {v.get('typo-shaped', 0)} | "
            f"{v.get('not-an-error', 0)} | {v.get('parse-error', 0)} |"
        )

    lines += [
        "",
        "## Verifier quote source",
        "",
        "How the verifier's contradicts-quote was sourced. In `none` mode the generator "
        "produces no quote, so the verifier draws a random related passage from the paper; "
        "in `window` / `related` modes the generator picks one.",
        "",
        "| Mode | Generator-picked | Random-sampled | None available |",
        "|------|-----------------:|---------------:|---------------:|",
    ]
    for mode in summaries:
        q = summaries.get(mode, {}).get("quote_source", {}) or {}
        lines.append(
            f"| {mode} | {q.get('generator', 0)} | {q.get('random-sampled', 0)} | "
            f"{q.get('none-available', 0)} |"
        )

    lines += [
        "",
        "## Metric definitions",
        "",
        "- **Gen yield** = n_generated / n_candidates — how liberally the generator produces "
        "perturbations given its available context. Higher is not better by itself.",
        "- **Verif accept** = n_accepted / n_valid_structural — of perturbations that passed "
        "structural tests 1–4, the fraction the verifier rated substantive.",
        "- **End-to-end** = n_accepted / n_generated — the product of structural validity and "
        "verifier acceptance.",
        "- **Tokens/cand** = mean prompt tokens per candidate, averaged across paper×error_type calls.",
        "- **Multiplier** is relative to the `none` mode (the cheapest baseline).",
    ]

    out_path.write_text("\n".join(lines) + "\n")
    print(f"\nReport written to {out_path}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Compare generator context modes")
    p.add_argument("config", type=Path, help="Path to YAML config (same schema as run_pipeline.py)")
    p.add_argument(
        "--report-only",
        action="store_true",
        help="Skip perturb calls; just re-read existing manifests and emit the report.",
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Override base output dir (default: <results_dir>/context_compare).",
    )
    p.add_argument(
        "--report-dir",
        type=Path,
        default=Path("benchmarks/perturbation/reports"),
        help="Directory for the rendered markdown report (default: benchmarks/perturbation/reports).",
    )
    p.add_argument(
        "--modes",
        default=",".join(CONTEXT_MODES),
        help=f"Comma-separated subset of context modes to run (default: all of {CONTEXT_MODES}).",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_config(args.config)

    base_out = args.out_dir or (Path(cfg.results_dir) / "context_compare")
    base_out.mkdir(parents=True, exist_ok=True)
    args.report_dir.mkdir(parents=True, exist_ok=True)

    modes = tuple(m.strip() for m in args.modes.split(",") if m.strip())
    unknown = [m for m in modes if m not in CONTEXT_MODES]
    if unknown:
        raise SystemExit(f"Unknown context mode(s): {unknown}. Valid: {CONTEXT_MODES}")

    if args.report_only:
        print("--report-only: skipping perturb calls.")
        papers = []  # unused in report-only
    else:
        papers = load_papers(cfg)
        print(f"Running perturb under modes: {modes}\n")
        for mode in modes:
            cfg_for_mode = replace(cfg, context_mode=mode)
            _perturb_for_mode(cfg_for_mode, mode, papers, base_out)

    summaries = {}
    for mode in modes:
        manifests = _collect_manifests(base_out / mode, cfg.error_type)
        summaries[mode] = _per_mode_summary(manifests)

    stem = f"context_mode_comparison_{date.today().isoformat()}"
    out_path = args.report_dir / f"{stem}.md"
    _write_report(summaries, cfg, out_path)

    json_path = base_out / f"{stem}.json"
    json_path.write_text(json.dumps(summaries, indent=2))
    print(f"Raw JSON: {json_path}")


if __name__ == "__main__":
    main()
