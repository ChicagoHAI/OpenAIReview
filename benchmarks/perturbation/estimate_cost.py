#!/usr/bin/env python3
"""Estimate the cost of a perturbation benchmark run from its YAML config.

Uses per-paper token estimates calibrated from actual runs. These are rough
averages — actual costs vary by paper length within a bin and by model
verbosity.

Usage:
    python benchmarks/perturbation/estimate_cost.py benchmarks/perturbation/configs/surface_errors.yaml
"""

import argparse
import sys
from pathlib import Path

import yaml

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

# ---------------------------------------------------------------------------
# Per-paper token estimates by (length, method), calibrated from actual runs.
# Each value is (prompt_tokens, completion_tokens) per paper.
# ---------------------------------------------------------------------------

TOKEN_ESTIMATES = {
    # length -> method -> (prompt, completion)
    "short": {
        "zero_shot":   (12_000,   2_000),
        "progressive": (75_000,  17_000),
        "local":       (75_000,  17_000),  # similar to progressive
    },
    "medium": {
        "zero_shot":   (35_000,   3_000),
        "progressive": (200_000, 45_000),
        "local":       (200_000, 45_000),
    },
    "long": {
        "zero_shot":   (40_000,   2_500),
        "progressive": (280_000, 55_000),
        "local":       (280_000, 55_000),
    },
}

# Perturb stage: 1 call per paper (prompt = candidates + template)
PERTURB_TOKENS = {"short": (8_000, 1_000), "medium": (15_000, 1_500), "long": (25_000, 2_000)}

# Score stage: ~5 perturbations per paper, ~500 prompt + 200 completion each
SCORE_TOKENS_PER_PERTURBATION = (500, 200)
AVG_PERTURBATIONS_PER_PAPER = 5


def compute_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    rates = COST_PER_1M.get(model, DEFAULT_COST)
    return (prompt_tokens / 1_000_000 * rates["prompt"]
            + completion_tokens / 1_000_000 * rates["completion"])


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Estimate the cost of a perturbation benchmark run.",
    )
    parser.add_argument("config", type=Path, help="Path to YAML config file")
    args = parser.parse_args()

    with args.config.open() as f:
        cfg = yaml.safe_load(f) or {}

    n_papers = cfg.get("max_papers", 2)
    length = cfg.get("length", "short")
    perturb_model = cfg.get("perturb_model", "google/gemini-3-flash-preview")
    score_model = cfg.get("score_model", "google/gemini-3-flash-preview")
    review_models = cfg.get("review_models", [])
    review_methods = cfg.get("review_methods", [])

    if length not in TOKEN_ESTIMATES:
        print(f"Warning: unknown length '{length}', using 'short' estimates", file=sys.stderr)
        length = "short"

    n_cells = n_papers * len(review_models) * len(review_methods)

    print(f"Config: {args.config.name}")
    print(f"  {n_papers} {length} papers × {len(review_models)} models × {len(review_methods)} methods = {n_cells} review cells")
    print()

    # --- Perturb stage ---
    perturb_pt, perturb_ct = PERTURB_TOKENS[length]
    perturb_pt_total = perturb_pt * n_papers
    perturb_ct_total = perturb_ct * n_papers
    perturb_cost = compute_cost(perturb_model, perturb_pt_total, perturb_ct_total)

    # --- Review stage ---
    review_costs = {}
    total_review_pt = 0
    total_review_ct = 0
    for model in review_models:
        for method in review_methods:
            est = TOKEN_ESTIMATES[length].get(method, TOKEN_ESTIMATES[length]["zero_shot"])
            pt = est[0] * n_papers
            ct = est[1] * n_papers
            cost = compute_cost(model, pt, ct)
            review_costs[(model, method)] = (pt, ct, cost)
            total_review_pt += pt
            total_review_ct += ct

    # --- Score stage ---
    n_score_calls = n_papers * AVG_PERTURBATIONS_PER_PAPER * len(review_models) * len(review_methods)
    score_pt_total = SCORE_TOKENS_PER_PERTURBATION[0] * n_score_calls
    score_ct_total = SCORE_TOKENS_PER_PERTURBATION[1] * n_score_calls
    score_cost = compute_cost(score_model, score_pt_total, score_ct_total)

    # --- Print breakdown ---
    print("## Estimated Cost Breakdown\n")
    print("| stage | model | prompt tokens | completion tokens | cost (USD) |")
    print("|-------|-------|---------------|-------------------|------------|")
    print(f"| perturb | {perturb_model} | {perturb_pt_total:,} | {perturb_ct_total:,} | ${perturb_cost:.4f} |")

    total_cost = perturb_cost
    for (model, method), (pt, ct, cost) in sorted(review_costs.items()):
        print(f"| review ({method}) | {model} | {pt:,} | {ct:,} | ${cost:.4f} |")
        total_cost += cost

    print(f"| score | {score_model} | {score_pt_total:,} | {score_ct_total:,} | ${score_cost:.4f} |")
    total_cost += score_cost

    total_pt = perturb_pt_total + total_review_pt + score_pt_total
    total_ct = perturb_ct_total + total_review_ct + score_ct_total
    print(f"| **total** | | **{total_pt:,}** | **{total_ct:,}** | **${total_cost:.4f}** |")
    print()
    print(f"Estimated total: ${total_cost:.2f}")


if __name__ == "__main__":
    main()
