#!/usr/bin/env python3
"""Aggregate perturbation benchmark results into a markdown report.

Reads the results directory structure produced by `run_pipeline.py` and
`run_competitor_benchmark.py`. Accepts one or more `--results-dir` to
produce a single combined report across lengths. Output goes to stdout by
default, or to `--out FILE`.

Usage:
    # Single results dir (prints to stdout)
    python benchmarks/perturbation/generate_report.py benchmarks/perturbation/results_short

    # Combined short + medium, written to a file
    python benchmarks/perturbation/generate_report.py \\
        benchmarks/perturbation/results_short \\
        benchmarks/perturbation/results_medium \\
        --out benchmarks/perturbation/reports/combined.md
"""

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # degrade gracefully: config display skipped

# ---------------------------------------------------------------------------
# Cost table (mirrors src/reviewer/evaluate.py)
# ---------------------------------------------------------------------------

COST_PER_1M = {
    "anthropic/claude-opus-4-6": {"prompt": 5.0, "completion": 25.0},
    "anthropic/claude-opus-4-5": {"prompt": 5.0, "completion": 25.0},
    "google/gemini-3.1-pro-preview": {"prompt": 2.0, "completion": 12.0},
    "google/gemini-3-flash-preview": {"prompt": 0.50, "completion": 3.00},
    "z-ai/glm-5": {"prompt": 0.80, "completion": 2.56},
    "z-ai/glm-4.6": {"prompt": 0.39, "completion": 1.90},
    "qwen/qwen3-235b-a22b-2507": {"prompt": 0.071, "completion": 0.10},
    "moonshotai/kimi-k2.5": {"prompt": 0.45, "completion": 2.20},
    "openai/gpt-5.2-pro": {"prompt": 21.0, "completion": 168.0},
}
DEFAULT_COST = {"prompt": 5.0, "completion": 25.0}


def slug_to_full_model(slug: str) -> str:
    """Map a model slug (e.g. 'glm-4.6') to the full name ('z-ai/glm-4.6')."""
    for full_name in COST_PER_1M:
        if full_name.split("/")[-1] == slug:
            return full_name
    return slug


def compute_cost(full_model: str, prompt_tokens: int, completion_tokens: int) -> float:
    rates = COST_PER_1M.get(full_model, DEFAULT_COST)
    return (prompt_tokens / 1_000_000 * rates["prompt"]
            + completion_tokens / 1_000_000 * rates["completion"])


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class CellResult:
    """One (model, method, paper) result cell."""
    model_slug: str
    method: str
    paper_label: str
    length: str
    error_type: str
    # from score JSON
    n_injected: int = 0
    n_detected: int = 0
    detected: list = field(default_factory=list)
    missed: list = field(default_factory=list)
    n_total_comments: int = 0
    # from review JSON
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float = 0.0
    # per-error breakdown (filled after cross-ref with manifest)
    by_error: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_ground_truth(results_dir: Path) -> dict[str, dict[str, str]]:
    """Return {paper_label: {perturbation_id: error_type}} from manifests."""
    gt: dict[str, dict[str, str]] = {}
    for path in sorted(results_dir.glob("perturb/*/paper_*/*_perturbations.json")):
        paper_label = path.parent.name
        data = json.loads(path.read_text())
        gt[paper_label] = {
            p["perturbation_id"]: p["error"]
            for p in data.get("perturbations", [])
        }
    return gt


def _extract_tokens_from_review(review_dir: Path, method: str, model_slug: str):
    """Read the most recent review JSON and extract token counts + cost."""
    review_jsons = sorted(review_dir.glob("*.json"), key=lambda p: p.stat().st_mtime)
    if not review_jsons:
        return 0, 0, 0.0
    try:
        data = json.loads(review_jsons[-1].read_text())
    except (json.JSONDecodeError, OSError):
        return 0, 0, 0.0

    if "methods" not in data:
        return 0, 0, 0.0

    # Find the method block matching this cell (e.g. "progressive/google/gemini-3-flash-preview").
    # Match on the method field inside the block, preferring the primary method
    # over progressive_original.
    for key, mdata in data["methods"].items():
        if mdata.get("method", "").replace(" ", "_").lower() == method and model_slug in key:
            return (
                mdata.get("prompt_tokens", 0),
                mdata.get("completion_tokens", 0),
                mdata.get("cost_usd", 0.0),
            )

    # Fallback: sum all method blocks (e.g. for formats without a method field)
    prompt = sum(m.get("prompt_tokens", 0) for m in data["methods"].values())
    comp = sum(m.get("completion_tokens", 0) for m in data["methods"].values())
    cost = sum(m.get("cost_usd", 0.0) for m in data["methods"].values())
    return prompt, comp, cost


def load_results(results_dir: Path, length: str, gt: dict[str, dict[str, str]]) -> list[CellResult]:
    """Walk score directories and build CellResult list."""
    cells: list[CellResult] = []

    # Score JSONs live at: <model>/<error_type>/<method>/paper_NNN/score/<score_method>/*.json
    for score_path in sorted(results_dir.glob("*/*/*/paper_*/score/*/*.json")):
        parts = score_path.relative_to(results_dir).parts
        if len(parts) < 7 or parts[4] != "score":
            continue
        model_slug, error_type, method, paper_label = parts[0], parts[1], parts[2], parts[3]
        if model_slug == "perturb":
            continue

        score_data = json.loads(score_path.read_text())

        cell = CellResult(
            model_slug=model_slug,
            method=method,
            paper_label=paper_label,
            length=length,
            error_type=error_type,
            n_injected=score_data.get("n_injected", 0),
            n_detected=score_data.get("n_detected", 0),
            detected=score_data.get("detected", []),
            missed=score_data.get("missed", []),
            n_total_comments=score_data.get("n_total_comments", 0),
        )

        # Per-error breakdown from manifest
        if paper_label in gt:
            by_error: dict[str, list[int]] = defaultdict(lambda: [0, 0])
            for pid, etype in gt[paper_label].items():
                by_error[etype][1] += 1
                if pid in cell.detected:
                    by_error[etype][0] += 1
            cell.by_error = {k: tuple(v) for k, v in by_error.items()}

        # Token counts from review JSON
        review_dir = score_path.parents[2] / "review"
        pt, ct, cost = _extract_tokens_from_review(review_dir, method, model_slug)
        cell.prompt_tokens = pt
        cell.completion_tokens = ct
        cell.cost_usd = cost

        cells.append(cell)

    return cells


# ---------------------------------------------------------------------------
# Report printing
# ---------------------------------------------------------------------------

def print_config(cfg: dict) -> None:
    print("## Configuration\n")
    print("| Setting | Value |")
    print("|---------|-------|")
    print(f"| Papers | {cfg.get('max_papers', '?')} |")
    print(f"| Length | {cfg.get('length', '?')} |")
    print(f"| Error type | {cfg.get('error_type', '?')} |")
    print(f"| Perturb model | {cfg.get('perturb_model', '?')} |")
    print(f"| Score method | {cfg.get('score_method', '?')} |")
    print(f"| Score model | {cfg.get('score_model', '?')} |")
    print(f"| Review models | {', '.join(cfg.get('review_models', []))} |")
    print(f"| Review methods | {', '.join(cfg.get('review_methods', []))} |")
    print()


def print_ground_truth(gt: dict[str, dict[str, str]]) -> None:
    print("## Ground Truth Summary\n")

    error_counts: dict[str, int] = defaultdict(int)
    total = 0

    for paper_label, perts in sorted(gt.items()):
        for etype in perts.values():
            error_counts[etype] += 1
            total += 1

    print(f"**{len(gt)} papers**, {total} perturbations total:")
    for etype in sorted(error_counts):
        print(f"  - {etype}: {error_counts[etype]}")
    print()


def _pct(det: int, tot: int) -> str:
    return f"{det / tot * 100:.1f}%" if tot else "—"


def _method_order(methods) -> list[str]:
    """Render coarse first, then zero_shot / progressive* / others alphabetically."""
    preferred = ["coarse", "zero_shot", "progressive",
                 "progressive_consolidated", "progressive_preconsol"]
    seen = set(methods)
    out = [m for m in preferred if m in seen]
    out.extend(sorted(m for m in seen if m not in preferred))
    return out


def print_overall_by_method(cells: list[CellResult]) -> None:
    print("## Overall recall — per method (aggregated over models, papers, lengths)\n")
    print("| method | n_injected | n_detected | recall |")
    print("|--------|-----------:|-----------:|-------:|")
    agg: dict[str, dict[str, int]] = defaultdict(lambda: {"inj": 0, "det": 0})
    for c in cells:
        agg[c.method]["inj"] += c.n_injected
        agg[c.method]["det"] += c.n_detected
    for m in _method_order(agg.keys()):
        g = agg[m]
        print(f"| {m} | {g['inj']} | {g['det']} | {_pct(g['det'], g['inj'])} |")
    print()


def print_recall_by_model_method(cells: list[CellResult]) -> None:
    methods = _method_order({c.method for c in cells})
    models = sorted({c.model_slug for c in cells})

    print("## Recall — per model × method\n")
    print("| model | " + " | ".join(methods) + " |")
    print("|-------|" + "|".join("------" for _ in methods) + "|")
    agg: dict[tuple[str, str], dict[str, int]] = defaultdict(lambda: {"inj": 0, "det": 0})
    for c in cells:
        agg[(c.model_slug, c.method)]["inj"] += c.n_injected
        agg[(c.model_slug, c.method)]["det"] += c.n_detected
    for model in models:
        row = [f"| {model}"]
        for m in methods:
            g = agg.get((model, m))
            if g is None or g["inj"] == 0:
                row.append("—")
            else:
                row.append(f"{_pct(g['det'], g['inj'])} ({g['det']}/{g['inj']})")
        print(" | ".join(row) + " |")
    print()


def print_recall_by_length_method(cells: list[CellResult]) -> None:
    lengths = sorted({c.length for c in cells})
    if len(lengths) <= 1:
        return
    methods = _method_order({c.method for c in cells})
    print("## Recall — per length × method\n")
    print("| length | " + " | ".join(methods) + " |")
    print("|--------|" + "|".join("------" for _ in methods) + "|")
    agg: dict[tuple[str, str], dict[str, int]] = defaultdict(lambda: {"inj": 0, "det": 0})
    for c in cells:
        agg[(c.length, c.method)]["inj"] += c.n_injected
        agg[(c.length, c.method)]["det"] += c.n_detected
    for length in lengths:
        row = [f"| {length}"]
        for m in methods:
            g = agg.get((length, m))
            if g is None or g["inj"] == 0:
                row.append("—")
            else:
                row.append(f"{_pct(g['det'], g['inj'])} ({g['det']}/{g['inj']})")
        print(" | ".join(row) + " |")
    print()


def print_recall_by_length_model_method(cells: list[CellResult]) -> None:
    """Detailed breakdown — only emitted when we have multiple lengths."""
    lengths = sorted({c.length for c in cells})
    if len(lengths) <= 1:
        return
    methods = _method_order({c.method for c in cells})
    models = sorted({c.model_slug for c in cells})
    print("## Recall — per length × model × method\n")
    print("| length | model | " + " | ".join(methods) + " |")
    print("|--------|-------|" + "|".join("------" for _ in methods) + "|")
    agg: dict[tuple[str, str, str], dict[str, int]] = defaultdict(lambda: {"inj": 0, "det": 0})
    for c in cells:
        agg[(c.length, c.model_slug, c.method)]["inj"] += c.n_injected
        agg[(c.length, c.model_slug, c.method)]["det"] += c.n_detected
    for length in lengths:
        for model in models:
            row = [f"| {length} | {model}"]
            for m in methods:
                g = agg.get((length, model, m))
                if g is None or g["inj"] == 0:
                    row.append("—")
                else:
                    row.append(f"{_pct(g['det'], g['inj'])} ({g['det']}/{g['inj']})")
            print(" | ".join(row) + " |")
    print()


def print_recall_by_error_type_x_method(cells: list[CellResult]) -> None:
    """Compact error-type × method grid (aggregated across models)."""
    etypes = sorted({et for c in cells for et in c.by_error})
    if not etypes:
        return
    methods = _method_order({c.method for c in cells})
    print("## Recall — per error type × method (aggregated across models and lengths)\n")
    print("| method | " + " | ".join(etypes) + " | overall |")
    print("|--------|" + "|".join("--------" for _ in etypes) + "|---------|")
    per: dict[tuple[str, str], list[int]] = defaultdict(lambda: [0, 0])
    totals: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for c in cells:
        for et, (det, tot) in c.by_error.items():
            per[(c.method, et)][0] += det
            per[(c.method, et)][1] += tot
            totals[c.method][0] += det
            totals[c.method][1] += tot
    for m in methods:
        parts = [f"| {m}"]
        for et in etypes:
            det, tot = per[(m, et)]
            parts.append(f"{det}/{tot} ({_pct(det, tot)})")
        det, tot = totals[m]
        parts.append(f"{det}/{tot} ({_pct(det, tot)})")
        print(" | ".join(parts) + " |")
    print()


def print_recall_by_error_type(cells: list[CellResult]) -> None:
    print("## Recall by Error Type — per (model, method)\n")

    etypes = sorted({et for c in cells for et in c.by_error})
    if not etypes:
        return
    header = "| model | method | " + " | ".join(etypes) + " | overall |"
    sep = "|-------|--------|" + "|".join("--------" for _ in etypes) + "|---------|"
    print(header)
    print(sep)

    groups: dict[tuple, dict[str, list[int]]] = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    totals: dict[tuple, list[int]] = defaultdict(lambda: [0, 0])

    for c in cells:
        key = (c.model_slug, c.method)
        for etype, (det, tot) in c.by_error.items():
            groups[key][etype][0] += det
            groups[key][etype][1] += tot
            totals[key][0] += det
            totals[key][1] += tot

    for (model, method) in sorted(groups):
        parts = [f"| {model}", method]
        for etype in etypes:
            det, tot = groups[(model, method)][etype]
            parts.append(f"{det}/{tot} ({_pct(det, tot)})")
        det, tot = totals[(model, method)]
        parts.append(f"{det}/{tot} ({_pct(det, tot)})")
        print(" | ".join(parts) + " |")
    print()


def print_token_usage(cells: list[CellResult]) -> None:
    print("## Token Usage and Cost\n")
    print("| model | cells | prompt tokens | completion tokens | cost (USD) |")
    print("|-------|-------|---------------|-------------------|------------|")

    groups: dict[str, dict] = defaultdict(lambda: {"cells": 0, "prompt": 0, "comp": 0, "cost": 0.0})
    for c in cells:
        groups[c.model_slug]["cells"] += 1
        groups[c.model_slug]["prompt"] += c.prompt_tokens
        groups[c.model_slug]["comp"] += c.completion_tokens
        if c.cost_usd > 0:
            groups[c.model_slug]["cost"] += c.cost_usd
        else:
            groups[c.model_slug]["cost"] += compute_cost(
                slug_to_full_model(c.model_slug), c.prompt_tokens, c.completion_tokens
            )

    total_cells = 0
    total_prompt = 0
    total_comp = 0
    total_cost = 0.0

    for model in sorted(groups):
        g = groups[model]
        total_cells += g["cells"]
        total_prompt += g["prompt"]
        total_comp += g["comp"]
        total_cost += g["cost"]
        print(f"| {model} | {g['cells']} | {g['prompt']:,} | {g['comp']:,} | ${g['cost']:.4f} |")

    print(f"| **total** | **{total_cells}** | **{total_prompt:,}** | **{total_comp:,}** | **${total_cost:.4f}** |")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _infer_length(results_dir: Path, cfg: dict) -> str:
    if cfg.get("length"):
        return cfg["length"]
    name = results_dir.name
    for lbl in ("short", "medium", "long"):
        if lbl in name:
            return lbl
    return name


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Aggregate perturbation benchmark results into a markdown report.",
    )
    parser.add_argument(
        "results_dirs",
        nargs="+",
        type=Path,
        help="One or more results directories. When multiple are given, "
             "cells from each are concatenated so the report spans both.",
    )
    parser.add_argument(
        "--out", type=Path, default=None,
        help="Write the report to this path (default: stdout).",
    )
    args = parser.parse_args()

    # Redirect stdout to file if requested
    out_fp = None
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        out_fp = args.out.open("w")
        sys.stdout = out_fp

    try:
        all_cells: list[CellResult] = []
        all_gt: dict[str, dict[str, str]] = {}
        configs: list[tuple[Path, dict]] = []

        for rd in args.results_dirs:
            if not rd.is_dir():
                print(f"Error: {rd} is not a directory", file=sys.stderr)
                sys.exit(1)
            cfg: dict = {}
            config_path = rd / "config.yaml"
            if yaml and config_path.exists():
                with config_path.open() as f:
                    cfg = yaml.safe_load(f) or {}
            length = _infer_length(rd, cfg)
            gt = load_ground_truth(rd)
            cells = load_results(rd, length, gt)
            all_cells.extend(cells)
            # Namespace gt by results_dir to avoid paper_label collisions across lengths
            for paper_label, perts in gt.items():
                all_gt[f"{length}:{paper_label}"] = perts
            configs.append((rd, cfg))

        if not all_cells:
            print("No results found.", file=sys.stderr)
            sys.exit(1)

        # Header
        print("# Perturbation Benchmark Report\n")
        if len(configs) == 1:
            print_config(configs[0][1])
        else:
            print("## Sources\n")
            for rd, cfg in configs:
                length = _infer_length(rd, cfg)
                print(f"- `{rd}` (length={length}, "
                      f"models={cfg.get('review_models') or cfg.get('coarse_models', '?')})")
            print()

        print_ground_truth(all_gt)

        # Summary tables
        print_overall_by_method(all_cells)
        print_recall_by_length_method(all_cells)
        print_recall_by_model_method(all_cells)
        print_recall_by_length_model_method(all_cells)

        # Error-type breakdowns
        print_recall_by_error_type_x_method(all_cells)
        print_recall_by_error_type(all_cells)

        # Cost
        print_token_usage(all_cells)
    finally:
        if out_fp is not None:
            sys.stdout = sys.__stdout__
            out_fp.close()
            print(f"Report: {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
