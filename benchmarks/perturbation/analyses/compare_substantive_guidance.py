#!/usr/bin/env python3
"""Compare generator prompts with substantive-guidance OFF vs ON.

TODO: split into `run_substantive_guidance.py` (generates raw JSON) and
`report_substantive_guidance.py` (tables/plots from the JSON). Same split as
run_pipeline.py / generate_report.py. Deferred until a plot is warranted.

Holds the perturbation setup fixed (same papers, same context_mode, same
verifier) and changes only whether the generator prompt explicitly teaches the
typo-shaped vs substantive-error distinction.

Outputs:
  - perturbation artifacts + raw JSON summary under
    <results_dir>/substantive_guidance_compare/
  - rendered markdown report under benchmarks/perturbation/reports/
"""

import argparse
import json
import shutil
import statistics
import sys
from datetime import date
from pathlib import Path

_THIS = Path(__file__).resolve()
_PERTURB_PKG = _THIS.parents[1]
_BENCHMARKS = _PERTURB_PKG.parent
if str(_BENCHMARKS) not in sys.path:
    sys.path.insert(0, str(_BENCHMARKS))

from perturbation.run_pipeline import (  # type: ignore  # noqa: E402
    load_config, load_papers, paper_length, run,
)


GUIDANCE_VARIANTS = (("off", False), ("on", True))


def _openaireview_cli() -> str:
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


def _perturb_for_variant(cfg, variant_name: str, substantive_guidance: bool, papers: list[dict], base_out: Path) -> Path:
    variant_dir = base_out / variant_name
    variant_dir.mkdir(parents=True, exist_ok=True)

    for i, paper in enumerate(papers, start=1):
        paper_label = f"paper_{i:03d}"
        perturb_dir = variant_dir / "perturb" / cfg.error_type / paper_label
        perturb_dir.mkdir(parents=True, exist_ok=True)

        print(
            f"\n[{variant_name}] Paper {i:03d}/{len(papers)} "
            f"({paper_length(paper):,} words, context={cfg.context_mode})"
        )

        tmp_path = perturb_dir / f"paper_{i:03d}.md"
        tmp_path.write_text(paper["text"])

        cmd = [
            _openaireview_cli(), "perturb", str(tmp_path),
            "--error_type", cfg.error_type,
            "--output-dir", str(perturb_dir),
            "--model", cfg.perturb_model,
            "--context-mode", cfg.context_mode,
            "--context-window", str(cfg.context_window),
            "--related-passages-max", str(cfg.related_passages_max),
            "--verifier-model", cfg.verifier_model,
            "--verifier-reasoning", cfg.verifier_reasoning,
            "--verifier-max-workers", str(cfg.verifier_max_workers),
        ]
        if not substantive_guidance:
            cmd.append("--no-substantive-guidance")
        if cfg.skip_verifier:
            cmd.append("--skip-verifier")

        rc = run(cmd)
        if rc != 0:
            print(f"  [{variant_name}] perturb failed (exit {rc}), skipping paper")
    return variant_dir


def _collect_manifests(variant_dir: Path, error_type: str) -> list[dict]:
    root = variant_dir / "perturb" / error_type
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


def _per_variant_summary(manifests: list[dict]) -> dict:
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

    generation_yield = (n_generated / n_candidates) if n_candidates else 0.0
    verifier_acceptance_rate = (n_accepted / n_valid_structural) if n_valid_structural else 0.0
    acceptance_rate = (n_accepted / n_generated) if n_generated else 0.0

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


def _write_report(summaries: dict[str, dict], cfg, out_path: Path) -> None:
    lines = [
        f"# Substantive-guidance comparison — {date.today().isoformat()}",
        "",
        f"- error_type: `{cfg.error_type}` · length: `{cfg.length}` · max_papers: `{cfg.max_papers}`",
        f"- context_mode: `{cfg.context_mode}`",
        f"- generator: `{cfg.perturb_model}`",
        f"- verifier: `{cfg.verifier_model}` (reasoning={cfg.verifier_reasoning})",
        "",
        "## Summary",
        "",
        "| Guidance | Papers | Cands | Gen | Gen yield | Valid (1-4) | Accepted (1-5) | Verif accept | End-to-end | Tokens/cand | Multiplier |",
        "|----------|-------:|------:|----:|----------:|------------:|---------------:|-------------:|-----------:|------------:|-----------:|",
    ]
    base_tpc = summaries.get("off", {}).get("mean_prompt_tokens_per_candidate") or None
    for variant_name, _ in GUIDANCE_VARIANTS:
        s = summaries.get(variant_name, {})
        tpc = s.get("mean_prompt_tokens_per_candidate")
        tpc_s = f"{tpc:.0f}" if tpc is not None else "—"
        if base_tpc and tpc:
            mult = f"{tpc/base_tpc:.2f}×"
        elif variant_name == "off" and tpc is not None:
            mult = "1.00×"
        else:
            mult = "—"
        lines.append(
            f"| {variant_name} | {s.get('n_papers', 0)} | {s.get('n_candidates', 0)} | "
            f"{s.get('n_generated', 0)} | {s.get('generation_yield', 0.0):.1%} | "
            f"{s.get('n_valid_structural', 0)} | {s.get('n_accepted', 0)} | "
            f"{s.get('verifier_acceptance_rate', 0.0):.1%} | "
            f"{s.get('acceptance_rate', 0.0):.1%} | {tpc_s} | {mult} |"
        )

    lines += [
        "",
        "## Verifier verdicts (test #5)",
        "",
        "| Guidance | Substantive | Typo-shaped | Not-an-error | Parse-error |",
        "|----------|------------:|------------:|-------------:|------------:|",
    ]
    for variant_name, _ in GUIDANCE_VARIANTS:
        v = summaries.get(variant_name, {}).get("verifier", {}) or {}
        lines.append(
            f"| {variant_name} | {v.get('substantive', 0)} | {v.get('typo-shaped', 0)} | "
            f"{v.get('not-an-error', 0)} | {v.get('parse-error', 0)} |"
        )

    lines += [
        "",
        "## Verifier quote source",
        "",
        "| Guidance | Generator-picked | Random-sampled | None available |",
        "|----------|-----------------:|---------------:|---------------:|",
    ]
    for variant_name, _ in GUIDANCE_VARIANTS:
        q = summaries.get(variant_name, {}).get("quote_source", {}) or {}
        lines.append(
            f"| {variant_name} | {q.get('generator', 0)} | {q.get('random-sampled', 0)} | "
            f"{q.get('none-available', 0)} |"
        )

    lines += [
        "",
        "## Metric definitions",
        "",
        "- **off** removes the explicit typo-shaped vs substantive-error framing but keeps the same context mode, quote policy, and verifier.",
        "- **on** includes the typo-shaped vs substantive-error framing.",
        "- **Gen yield** = n_generated / n_candidates.",
        "- **Verif accept** = n_accepted / n_valid_structural.",
        "- **End-to-end** = n_accepted / n_generated.",
        "- **Tokens/cand** = mean prompt tokens per candidate, averaged across paper×error_type calls.",
        "- **Multiplier** is relative to guidance `off`.",
    ]

    out_path.write_text("\n".join(lines) + "\n")
    print(f"\nReport written to {out_path}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Compare substantive-guidance prompt variants")
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
        help="Override perturb output dir (default: <results_dir>/substantive_guidance_compare).",
    )
    p.add_argument(
        "--report-dir",
        type=Path,
        default=Path("benchmarks/perturbation/reports"),
        help="Directory for the rendered markdown report (default: benchmarks/perturbation/reports).",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_config(args.config)

    base_out = args.out_dir or (Path(cfg.results_dir) / "substantive_guidance_compare")
    base_out.mkdir(parents=True, exist_ok=True)
    args.report_dir.mkdir(parents=True, exist_ok=True)

    if args.report_only:
        print("--report-only: skipping perturb calls.")
    else:
        papers = load_papers(cfg)
        print(f"Running perturb under substantive-guidance variants: {tuple(name for name, _ in GUIDANCE_VARIANTS)}\n")
        for variant_name, substantive_guidance in GUIDANCE_VARIANTS:
            _perturb_for_variant(cfg, variant_name, substantive_guidance, papers, base_out)

    summaries = {}
    for variant_name, _ in GUIDANCE_VARIANTS:
        manifests = _collect_manifests(base_out / variant_name, cfg.error_type)
        summaries[variant_name] = _per_variant_summary(manifests)

    stem = f"substantive_guidance_comparison_{date.today().isoformat()}"
    report_path = args.report_dir / f"{stem}.md"
    _write_report(summaries, cfg, report_path)

    json_path = base_out / f"{stem}.json"
    json_path.write_text(json.dumps(summaries, indent=2))
    print(f"Raw JSON: {json_path}")


if __name__ == "__main__":
    main()
