#!/usr/bin/env python
"""Dry-run cost estimator for the conference accept-vs-reject study.

For each paper in the manifest and each model in the config, estimate the
total USD cost of running the configured method with the planned caps.

Approximation: input doc tokens ≈ max_pages × TOKENS_PER_PAGE (skip PDF
parsing entirely — much faster and accurate within the multiplier noise
band). Multipliers per method are derived from real benchmark runs and
model prices come from OpenRouter's live listings.

Run:
    python estimate_cost.py --config configs/baseline.yaml
    python estimate_cost.py --config configs/coarse_v2.yaml
    python estimate_cost.py --max-pages 30              # ad-hoc
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

# Resolve repo paths.
HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent

# Defaults — overridden by YAML config and/or CLI flags in main().
DEFAULT_MAX_PAGES = 20
DEFAULT_MAX_TOKENS = 20_000
# Average tokens per page in NeurIPS/ICLR-style ML papers (~9.5pt body text,
# 2-column). Calibrated to match observed input-token counts on v2_small runs.
DEFAULT_TOKENS_PER_PAGE = 1000

# Runtime values, populated in main().
MAX_PAGES: int = DEFAULT_MAX_PAGES
MAX_TOKENS: int = DEFAULT_MAX_TOKENS
TOKENS_PER_PAGE: int = DEFAULT_TOKENS_PER_PAGE

# Calibrated against real Apr 2026 v2_small=100 papers runs at max_pages=10
# (≈10K input doc tokens). Multipliers are (total tokens sent to LLM) ÷
# (max_pages × TOKENS_PER_PAGE).
#   progressive qwen: 85K prompt / 19K completion / paper → 8.5x / 1.9x
#   zero_shot   qwen: 12K prompt /  2K completion / paper → 1.2x / 0.2x
#   coarse      qwen: ~$0.062 all-in real cost back-solved at qwen effective
#                     rate (~$0.13/$0.19 per M) ≈ 30x / 10x. Has higher noise
#                     (no per-paper token counts emitted by the runner).
METHOD_MULTIPLIERS = {
    "progressive": {"prompt":  8.5, "completion":  1.9},
    "zero_shot":   {"prompt":  1.2, "completion":  0.2},
    "coarse":      {"prompt": 30.0, "completion": 10.0},
}
# Default — overridden by the config's `method:` field in main().
PROMPT_MULT = METHOD_MULTIPLIERS["progressive"]["prompt"]
COMPLETION_MULT = METHOD_MULTIPLIERS["progressive"]["completion"]

# OpenRouter prices (USD per token). Re-verified 2026-04-27 via openrouter.ai
# per-model pages. Refresh when adding models or pricing changes.
MODEL_PRICES = {
    "google/gemini-3-flash-preview": {"prompt": 0.50e-6,  "completion": 3.00e-6},
    "z-ai/glm-4.6":                  {"prompt": 0.39e-6,  "completion": 1.90e-6},
    "qwen/qwen3-235b-a22b-2507":     {"prompt": 0.071e-6, "completion": 0.10e-6},
    "qwen/qwen3.6-35b-a3b":          {"prompt": 0.16e-6,  "completion": 0.97e-6},
    "z-ai/glm-4.7-flash":            {"prompt": 0.06e-6,  "completion": 0.40e-6},
    "deepseek/deepseek-v4-flash":    {"prompt": 0.14e-6,  "completion": 0.28e-6},
    "google/gemini-2.5-flash":       {"prompt": 0.30e-6,  "completion": 2.50e-6},
    "google/gemini-2.5-flash-lite":  {"prompt": 0.10e-6,  "completion": 0.40e-6},
    "google/gemini-3.1-flash-lite-preview": {"prompt": 0.25e-6, "completion": 1.50e-6},
    "anthropic/claude-sonnet-4.6":   {"prompt": 3.00e-6,  "completion": 15.00e-6},
    "anthropic/claude-opus-4.7":     {"prompt": 5.00e-6,  "completion": 25.00e-6},
    "openai/gpt-5-mini":             {"prompt": 0.25e-6,  "completion": 2.00e-6},
    "openai/gpt-5.4-mini":           {"prompt": 0.75e-6,  "completion": 4.50e-6},
    "openai/gpt-5.5":                {"prompt": 5.00e-6,  "completion": 30.00e-6},
}


def estimate_paper() -> int:
    """Return the assumed effective input token count per paper.

    Approximated as min(MAX_PAGES × TOKENS_PER_PAGE, MAX_TOKENS). Avoids
    parsing every PDF on disk — the multiplier noise band (~±30%) swamps
    any per-paper variation a real token count would expose.
    """
    return min(MAX_PAGES * TOKENS_PER_PAGE, MAX_TOKENS)


def load_config(path: str) -> dict:
    """Load a YAML run-config file. Returns {} if path is None."""
    if not path:
        return {}
    cfg_path = Path(path)
    if not cfg_path.is_absolute():
        cfg_path = cfg_path if cfg_path.exists() else HERE / path
    if not cfg_path.exists():
        sys.exit(f"config file not found: {path}")
    with cfg_path.open() as f:
        return yaml.safe_load(f) or {}


def main() -> None:
    global MAX_PAGES, MAX_TOKENS, TOKENS_PER_PAGE, PROMPT_MULT, COMPLETION_MULT

    ap = argparse.ArgumentParser()
    ap.add_argument("--config", help="YAML config file (same schema as run_study.py).")
    ap.add_argument("--manifest", type=Path,
                    help="Path to manifest JSON. Overrides config's 'manifest'.")
    ap.add_argument("--max-pages", type=int, default=None,
                    help=f"Override max pages (default: {DEFAULT_MAX_PAGES}).")
    ap.add_argument("--max-tokens", type=int, default=None,
                    help=f"Override max tokens (default: {DEFAULT_MAX_TOKENS}).")
    ap.add_argument("--tokens-per-page", type=int, default=None,
                    help=f"Override tokens-per-page (default: {DEFAULT_TOKENS_PER_PAGE}).")
    ap.add_argument("--method", choices=list(METHOD_MULTIPLIERS.keys()), default=None,
                    help="Override method (else read from config).")
    args = ap.parse_args()

    cfg = load_config(args.config)
    MAX_PAGES = args.max_pages if args.max_pages is not None \
        else cfg.get("max_pages", DEFAULT_MAX_PAGES)
    MAX_TOKENS = args.max_tokens if args.max_tokens is not None \
        else cfg.get("max_tokens", DEFAULT_MAX_TOKENS)
    TOKENS_PER_PAGE = args.tokens_per_page if args.tokens_per_page is not None \
        else DEFAULT_TOKENS_PER_PAGE
    # Coarse configs use `competitor: coarse` (no `method:` field); fall back
    # to that. Otherwise read `method:` (progressive/zero_shot).
    method = args.method or cfg.get("method") or cfg.get("competitor", "progressive")
    if method in METHOD_MULTIPLIERS:
        PROMPT_MULT = METHOD_MULTIPLIERS[method]["prompt"]
        COMPLETION_MULT = METHOD_MULTIPLIERS[method]["completion"]
    else:
        print(f"  (no multiplier preset for method={method!r}; using progressive defaults)")

    manifest_path = args.manifest or Path(cfg.get("manifest", "manifest.json"))
    if not manifest_path.is_absolute():
        manifest_path = HERE / manifest_path
    manifest = json.loads(manifest_path.read_text())
    papers = manifest["papers"]
    models = cfg.get("models") or manifest["models"]

    if args.config:
        print(f"Config: {args.config}")
        if cfg.get("name"):
            print(f"Experiment: {cfg['name']}")
    print(f"{len(papers)} papers × {len(models)} models, "
          f"method={method}, max_pages={MAX_PAGES}, "
          f"tokens_per_page={TOKENS_PER_PAGE} "
          f"(prompt {PROMPT_MULT}x, completion {COMPLETION_MULT}x)\n")

    n_per_paper = estimate_paper()
    prompt_tok = n_per_paper * PROMPT_MULT
    comp_tok = n_per_paper * COMPLETION_MULT

    # Interval band:
    #   LOW  = optimistic anchor (matches the real-qwen-anchored projections
    #          surfaced earlier in this study; assumes premium models bill
    #          near listed and benefit from prompt caching).
    #   HIGH = listed prices × 1.3 (typical OpenRouter real cost when papers
    #          route through non-cheapest providers; cheap open-weights
    #          observed at 1.5–2x listed but premium models stay closer).
    LOW_MULT, HIGH_MULT = 0.65, 1.3

    print(f"Per paper: ~{n_per_paper:,} input tokens → "
          f"{int(prompt_tok):,} prompt + {int(comp_tok):,} completion sent to LLM\n")

    n_papers = len(papers)
    print(f"{'model':40s}  {'$/paper (low–high)':>22s}  {'×' + str(n_papers) + ' papers (low–high)':>30s}")
    print("-" * 100)
    g_low = g_high = 0.0
    for m in models:
        if m not in MODEL_PRICES:
            print(f"  {m:40s}  (no pricing entry — skipped)")
            continue
        price = MODEL_PRICES[m]
        per_paper = prompt_tok * price["prompt"] + comp_tok * price["completion"]
        lo = per_paper * LOW_MULT
        hi = per_paper * HIGH_MULT
        total_lo = lo * n_papers
        total_hi = hi * n_papers
        g_low += total_lo
        g_high += total_hi
        print(f"  {m:40s}  ${lo:>8.4f} – ${hi:<8.4f}  ${total_lo:>10.2f} – ${total_hi:<10.2f}")
    print("-" * 100)
    print(f"  {'GRAND TOTAL':40s}  {'':>22s}  ${g_low:>10.2f} – ${g_high:<10.2f}")

    by_group: dict[str, int] = {}
    for p in papers:
        by_group[p.get("group") or "snor"] = by_group.get(p.get("group") or "snor", 0) + 1
    if len(by_group) > 1:
        print()
        print("Papers by group: " + "  ".join(f"{g}={n}" for g, n in by_group.items()))

    print()
    print("Notes:")
    print(f"  - Multipliers calibrated against real Apr 2026 v2_small runs at "
          f"max_pages=10.")
    print(f"  - Range = point × [{LOW_MULT}, {HIGH_MULT}]: low ≈ optimistic "
          f"(prompt-caching wins, premium-tier providers); high ≈ typical real "
          f"(OpenRouter routes to non-cheapest providers, cheap open-weights "
          f"can hit 1.5–2x listed).")


if __name__ == "__main__":
    main()
