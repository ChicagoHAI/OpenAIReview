#!/usr/bin/env python3
"""Aggregate perturbation benchmark results and print a report to stdout.

Reads the results directory structure produced by run_pipeline.py and prints
tables summarizing recall, error-type breakdowns, token usage, and cost.

Usage:
    python benchmarks/perturbation/generate_report.py benchmarks/perturbation/results_short
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


def print_recall_by_model_method(cells: list[CellResult]) -> None:
    print("## Recall by Model x Method\n")
    print("| model | method | gt | detected | recall |")
    print("|-------|--------|----|----------|--------|")

    groups: dict[tuple, dict] = defaultdict(lambda: {"gt": 0, "det": 0})
    for c in cells:
        groups[(c.model_slug, c.method)]["gt"] += c.n_injected
        groups[(c.model_slug, c.method)]["det"] += c.n_detected

    for (model, method) in sorted(groups):
        g = groups[(model, method)]
        recall = g["det"] / g["gt"] * 100 if g["gt"] else 0
        print(f"| {model} | {method} | {g['gt']} | {g['det']} | {recall:.1f}% |")
    print()


def print_recall_by_error_type(cells: list[CellResult]) -> None:
    print("## Recall by Error Type\n")

    all_etypes: set[str] = set()
    for c in cells:
        all_etypes.update(c.by_error.keys())
    etypes = sorted(all_etypes)

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
            pct = det / tot * 100 if tot else 0
            parts.append(f"{det}/{tot} ({pct:.0f}%)")
        det, tot = totals[(model, method)]
        pct = det / tot * 100 if tot else 0
        parts.append(f"{det}/{tot} ({pct:.0f}%)")
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

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Aggregate perturbation benchmark results and print a report to stdout.",
    )
    parser.add_argument(
        "results_dir",
        type=Path,
        help="Results directory produced by run_pipeline.py",
    )
    args = parser.parse_args()

    results_dir = args.results_dir
    if not results_dir.is_dir():
        print(f"Error: {results_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    # Load config
    cfg: dict = {}
    config_path = results_dir / "config.yaml"
    if yaml and config_path.exists():
        with config_path.open() as f:
            cfg = yaml.safe_load(f) or {}
    length = cfg.get("length", results_dir.name)

    # Load ground truth
    gt = load_ground_truth(results_dir)

    # Load score + review data
    cells = load_results(results_dir, length, gt)

    if not cells:
        print("No results found.", file=sys.stderr)
        sys.exit(1)

    # Print report
    print("# Perturbation Benchmark Report\n")
    if cfg:
        print_config(cfg)
    print_ground_truth(gt)
    print_recall_by_model_method(cells)
    print_recall_by_error_type(cells)
    print_token_usage(cells)


if __name__ == "__main__":
    main()
