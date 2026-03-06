"""Run RAG improvement experiments.

Phase 1: Single paper (inference-molecular) with all variants.
Phase 2: Best variants on all 4 papers.

Usage:
    uv run python scripts/run_experiments.py              # Phase 1
    uv run python scripts/run_experiments.py --phase 2    # Phase 2 (all papers)
    uv run python scripts/run_experiments.py --dry-run    # Verify configs
"""

import argparse
import datetime
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT.parent / "src"))

from reviewer.evaluate import compute_cost, evaluate, print_report
from reviewer.method_progressive import PROGRESSIVE_VARIANTS, review_progressive
from reviewer.method_rag import RAG_VARIANTS, review_rag
from reviewer.method_zero_shot import review_zero_shot
from reviewer.models import ReviewResult

ALL_VARIANTS = {"zero_shot": {}, **RAG_VARIANTS, **{k: {} for k in PROGRESSIVE_VARIANTS}}

BENCHMARK_FILE = ROOT / "data" / "benchmark.jsonl"
RESULTS_DIR = ROOT / "results"

DEFAULT_LARGE_MODEL = os.environ.get("LARGE_MODEL", "anthropic/claude-opus-4-5")
DEFAULT_SMALL_MODEL = os.environ.get("SMALL_MODEL", "anthropic/claude-haiku-4-5")
DEFAULT_JUDGE_MODEL = os.environ.get("JUDGE_MODEL", "anthropic/claude-haiku-4-5")

# Phase 1: single paper, all chunked variants + baseline
PHASE1_VARIANTS = [
    "rag_local",
    "rag_chunked",
    "rag_chunked_w5",
    "rag_chunked_defs",
    "rag_chunked_2pass",
    "rag_chunked_full",
]

# Phase 2: best variants (updated after Phase 1 analysis)
PHASE2_VARIANTS = [
    "rag_local",
    "rag_chunked",
    "rag_chunked_full",
]

PHASE1_PAPER = "inference-molecular"


def load_papers() -> list[dict]:
    papers = []
    with open(BENCHMARK_FILE) as f:
        for line in f:
            papers.append(json.loads(line))
    return papers


def load_completed(output_file: Path) -> set[tuple[str, str]]:
    """Load (slug, variant) pairs already completed."""
    completed = set()
    if output_file.exists():
        with open(output_file) as f:
            for line in f:
                try:
                    record = json.loads(line)
                    completed.add((record["paper_slug"], record["method"]))
                except (json.JSONDecodeError, KeyError):
                    pass
    return completed


def run_experiment(
    paper: dict,
    variant: str,
    large_model: str,
    small_model: str,
    judge_model: str,
    output_file: Path,
) -> dict | None:
    """Run a single experiment and return metrics."""
    slug = paper["slug"]
    doc = paper["document_content"]
    ground_truth = paper["comments"]

    print(f"\n{'─'*60}")
    print(f"Variant: {variant} | Paper: {slug}")
    print(f"GT comments: {len(ground_truth)}")
    print(f"{'─'*60}")

    try:
        if variant == "zero_shot":
            result = review_zero_shot(
                slug, doc,
                model=large_model,
            )
            full_result = None
        elif variant in PROGRESSIVE_VARIANTS:
            result, full_result = review_progressive(
                slug, doc,
                model=large_model,
                small_model=small_model,
                variant=variant,
            )
        else:
            result = review_rag(
                slug, doc,
                small_model=small_model,
                large_model=large_model,
                variant=variant,
            )
            full_result = None
        print(f"  Found {result.num_comments} comments")

        metrics = evaluate(
            result, ground_truth,
            use_llm_judge=True,
            judge_model=judge_model,
        )

        cost = metrics["cost_usd"]
        print(f"  sim_recall={metrics['recall']:.2f}  "
              f"loc_recall={metrics['location_recall']:.2f}  "
              f"loc_recall_5={metrics['location_recall_5']:.2f}  "
              f"llm_recall={metrics.get('recall_llm', 0):.2f}  "
              f"llm_recall_wide={metrics.get('recall_llm_wide', 0):.2f}")
        print(f"  precision_llm={metrics.get('precision_llm', 0):.2f}  "
              f"precision_llm_wide={metrics.get('precision_llm_wide', 0):.2f}")
        print(f"  cost=${cost:.4f}")

        record = {
            "method": variant,
            "paper_slug": slug,
            "paper_title": paper["title"],
            "metrics": metrics,
            "result": result.to_dict(),
        }
        with open(output_file, "a") as f:
            f.write(json.dumps(record) + "\n")

        # Save full (pre-consolidation) result for progressive variants
        if full_result:
            full_metrics = evaluate(
                full_result, ground_truth,
                use_llm_judge=True,
                judge_model=judge_model,
            )
            print(f"  Full (pre-consolidation): {full_result.num_comments} comments, "
                  f"llm_recall={full_metrics.get('recall_llm', 0):.2f}")
            full_record = {
                "method": full_result.method,
                "paper_slug": slug,
                "paper_title": paper["title"],
                "metrics": full_metrics,
                "result": full_result.to_dict(),
            }
            with open(output_file, "a") as f:
                f.write(json.dumps(full_record) + "\n")

        return metrics

    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


def print_comparison_table(all_results: list[tuple[str, str, dict]]) -> None:
    """Print a compact comparison table."""
    print(f"\n{'='*100}")
    print("COMPARISON TABLE")
    print(f"{'='*100}")
    header = (
        f"{'Variant':<22} {'Paper':<22} "
        f"{'Pred':>4} {'GT':>3} "
        f"{'LocR':>5} {'LocR5':>5} {'LocR10':>6} "
        f"{'LLM_R':>5} {'LLM_P':>5} "
        f"{'WideR':>5} {'WideP':>5} "
        f"{'Cost':>7}"
    )
    print(header)
    print("─" * 100)

    for variant, slug, m in all_results:
        row = (
            f"{variant:<22} {slug:<22} "
            f"{m['num_predicted']:>4} {m['num_ground_truth']:>3} "
            f"{m.get('location_recall', 0):>5.2f} "
            f"{m.get('location_recall_5', 0):>5.2f} "
            f"{m.get('location_recall_10', 0):>6.2f} "
            f"{m.get('recall_llm', 0):>5.2f} "
            f"{m.get('precision_llm', 0):>5.2f} "
            f"{m.get('recall_llm_wide', 0):>5.2f} "
            f"{m.get('precision_llm_wide', 0):>5.2f} "
            f"${m['cost_usd']:>6.2f}"
        )
        print(row)

    # Aggregate by variant
    print(f"\n{'─'*100}")
    print("AGGREGATE BY VARIANT:")
    variants_seen: dict[str, list[dict]] = {}
    for v, s, m in all_results:
        variants_seen.setdefault(v, []).append(m)
    for v, metrics_list in variants_seen.items():
        n = len(metrics_list)
        avg_loc = sum(m.get("location_recall", 0) for m in metrics_list) / n
        avg_llm = sum(m.get("recall_llm", 0) for m in metrics_list) / n
        avg_ung = sum(m.get("recall_llm_wide", 0) for m in metrics_list) / n
        avg_cost = sum(m["cost_usd"] for m in metrics_list) / n
        total_cost = sum(m["cost_usd"] for m in metrics_list)
        print(
            f"  {v:<22} (n={n}) "
            f"avg_loc_recall={avg_loc:.2f}  "
            f"avg_llm_recall={avg_llm:.2f}  "
            f"avg_wide_recall={avg_ung:.2f}  "
            f"avg_cost=${avg_cost:.2f}  total_cost=${total_cost:.2f}"
        )

    total_cost = sum(m["cost_usd"] for _, _, m in all_results)
    print(f"\nTotal experiment cost: ${total_cost:.2f}")
    print(f"{'='*100}")


def main():
    parser = argparse.ArgumentParser(description="Run RAG improvement experiments")
    parser.add_argument(
        "--phase", type=int, default=1, choices=[1, 2],
        help="Phase 1: single paper; Phase 2: all papers with best variants",
    )
    parser.add_argument(
        "--variants", nargs="+", default=None,
        help="Override variant list (default: phase-specific)",
    )
    parser.add_argument(
        "--papers", nargs="+", default=None,
        help="Override paper slugs (default: phase-specific)",
    )
    parser.add_argument(
        "--large-model", default=DEFAULT_LARGE_MODEL,
    )
    parser.add_argument(
        "--small-model", default=DEFAULT_SMALL_MODEL,
    )
    parser.add_argument(
        "--judge-model", default=DEFAULT_JUDGE_MODEL,
    )
    parser.add_argument(
        "--output", default=None,
        help="Output JSONL file (default: results/experiments_<timestamp>.jsonl)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print experiment config without running API calls",
    )
    args = parser.parse_args()

    # Determine variants and papers
    if args.variants:
        variants = args.variants
    elif args.phase == 1:
        variants = PHASE1_VARIANTS
    else:
        variants = PHASE2_VARIANTS

    # Validate variants
    for v in variants:
        if v not in ALL_VARIANTS:
            print(f"ERROR: Unknown variant '{v}'. Available: {list(ALL_VARIANTS.keys())}")
            sys.exit(1)

    all_papers = load_papers()
    if args.papers:
        papers = [p for p in all_papers if p["slug"] in args.papers]
    elif args.phase == 1:
        papers = [p for p in all_papers if p["slug"] == PHASE1_PAPER]
    else:
        papers = all_papers

    if not papers:
        print("No papers found. Check slug names or run scripts/parse_examples.py first.")
        sys.exit(1)

    # Output file
    RESULTS_DIR.mkdir(exist_ok=True)
    if args.output:
        output_file = Path(args.output)
    else:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = RESULTS_DIR / f"experiments_{ts}.jsonl"

    # Dry run
    if args.dry_run:
        print("DRY RUN — Experiment configuration:")
        print(f"  Phase: {args.phase}")
        print(f"  Large model: {args.large_model}")
        print(f"  Small model: {args.small_model}")
        print(f"  Judge model: {args.judge_model}")
        print(f"  Output: {output_file}")
        print(f"\n  Variants ({len(variants)}):")
        for v in variants:
            if v in PROGRESSIVE_VARIANTS:
                cfg = PROGRESSIVE_VARIANTS[v]
                print(f"    {v}: {cfg}")
            else:
                cfg = RAG_VARIANTS[v]
                print(f"    {v}: {cfg}")
        print(f"\n  Papers ({len(papers)}):")
        for p in papers:
            print(f"    {p['slug']}: {p['title'][:60]} ({len(p['comments'])} GT comments)")
        total_runs = len(variants) * len(papers)
        print(f"\n  Total runs: {total_runs}")
        return

    # Check for completed runs (crash resilience)
    completed = load_completed(output_file)
    if completed:
        print(f"Resuming: {len(completed)} runs already completed in {output_file}")

    print(f"Phase {args.phase}: {len(variants)} variants x {len(papers)} papers")
    print(f"Models: {args.large_model} + {args.small_model}")
    print(f"Judge: {args.judge_model}")
    print(f"Output: {output_file}\n")

    all_results: list[tuple[str, str, dict]] = []
    running_cost = 0.0

    for variant in variants:
        for paper in papers:
            slug = paper["slug"]
            if (slug, variant) in completed:
                print(f"  SKIP (already done): {variant} / {slug}")
                continue

            metrics = run_experiment(
                paper, variant,
                large_model=args.large_model,
                small_model=args.small_model,
                judge_model=args.judge_model,
                output_file=output_file,
            )
            if metrics:
                all_results.append((variant, slug, metrics))
                running_cost += metrics["cost_usd"]
                print(f"  Running total cost: ${running_cost:.2f}")

    # Also load previously completed results for the table
    if completed:
        with open(output_file) as f:
            for line in f:
                try:
                    record = json.loads(line)
                    key = (record["paper_slug"], record["method"])
                    if key in completed:
                        all_results.append(
                            (record["method"], record["paper_slug"], record["metrics"])
                        )
                except (json.JSONDecodeError, KeyError):
                    pass

    if all_results:
        print_comparison_table(all_results)
        print_report(all_results)

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
