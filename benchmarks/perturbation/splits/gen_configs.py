#!/usr/bin/env python3
"""Generate per-(method, variant, split, domain) YAML configs for the
prompt-variant experiment.

Writes to benchmarks/perturbation/configs/promptvariant/promptvariant_<method>_<variant>_<split>_<domain>.yaml
and points results_dir at benchmarks/perturbation/results/<same-stem>/ so the
variant runs do not collide with baseline result trees.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIGS_DIR = REPO_ROOT / "benchmarks" / "perturbation" / "configs" / "promptvariant"
SPLITS_DIR = Path(__file__).resolve().parent

# Use t4+grounded scoring to match the paper's Table 6 baseline numbers.
SCORE_DEFAULTS = dict(
    score_method="llm",
    score_model="google/gemini-3-flash-preview",
    score_threshold=4,
    score_substring_gate=True,
    score_subdir="llm_t4_grounded",
)


def _yaml_list(items: list[str], indent: int = 2) -> str:
    pad = " " * indent
    return "\n".join(f"{pad}- {x}" for x in items)


def emit_config(method: str, variant: str, split_name: str, domain: str,
                paper_labels: list[str], model: str) -> Path:
    stem = f"promptvariant_{method}_{variant}_{split_name}_{domain}"
    cfg_path = CONFIGS_DIR / f"{stem}.yaml"
    input_dir = f"benchmarks/perturbation/data/perturbations_filtered/{domain}/all"
    results_dir = f"benchmarks/perturbation/results/{stem}"
    lines = [
        "system: openaireview",
        f"input_dir: {input_dir}",
        f"results_dir: {results_dir}",
        "max_tokens: 13000",
        "min_perturbations: 5",
        f"score_method: {SCORE_DEFAULTS['score_method']}",
        f"score_model: {SCORE_DEFAULTS['score_model']}",
        f"score_threshold: {SCORE_DEFAULTS['score_threshold']}",
        f"score_substring_gate: {str(SCORE_DEFAULTS['score_substring_gate']).lower()}",
        f"score_subdir: {SCORE_DEFAULTS['score_subdir']}",
        "review_models:",
        f"  - {model}",
        "review_methods:",
        f"  - {method}",
        f"prompt_variant: {variant}",
        "paper_subset:",
        _yaml_list(paper_labels),
        "",
    ]
    cfg_path.write_text("\n".join(lines))
    return cfg_path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", required=True,
                    help="Split name; reads splits/<name>.json (e.g. val, test, fastval)")
    ap.add_argument("--method", required=True, choices=["zero_shot", "progressive"])
    ap.add_argument("--variants", default="math_v1,math_v2",
                    help="Comma-separated list of variant names (e.g. math_v1,math_v2)")
    ap.add_argument("--domains", default="",
                    help="Comma-separated subset of domains (default: all domains in split)")
    ap.add_argument("--model", default="deepseek/deepseek-v4-flash")
    ap.add_argument("--splits-dir", type=Path, default=SPLITS_DIR)
    args = ap.parse_args()

    split_path = args.splits_dir / f"{args.split}.json"
    split = json.loads(split_path.read_text())
    domains = [d for d in split["domains"]
               if not args.domains or d in args.domains.split(",")]
    variants = [v for v in args.variants.split(",") if v]

    written: list[Path] = []
    for variant in variants:
        for domain in domains:
            labels = split["domains"][domain]["paper_labels"]
            if not labels:
                continue
            p = emit_config(args.method, variant, args.split, domain, labels, args.model)
            written.append(p)
    print(f"Wrote {len(written)} configs to {CONFIGS_DIR}")
    for p in written:
        print(f"  {p.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
