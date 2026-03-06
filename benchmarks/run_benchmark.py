"""Run the benchmark: evaluate all three review methods on all four papers."""

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path(__file__).parent / "data"
RESULTS_DIR = Path(__file__).parent / "results"
BENCHMARK_FILE = DATA_DIR / "benchmark.jsonl"

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from reviewer.evaluate import evaluate, load_benchmark, print_report
from reviewer.method_progressive import review_progressive
from reviewer.method_local import review_local
from reviewer.method_zero_shot import review_zero_shot

DEFAULT_MODEL = os.environ.get("MODEL", "anthropic/claude-opus-4-5")

METHODS = {
    "zero_shot": lambda slug, doc, args: review_zero_shot(
        slug, doc, model=args.model
    ),
    "local": lambda slug, doc, args: review_local(
        slug, doc, model=args.model,
    ),
    "progressive": lambda slug, doc, args: review_progressive(
        slug, doc, model=args.model
    ),
}


def main():
    parser = argparse.ArgumentParser(description="Run the paper review benchmark")
    parser.add_argument(
        "--methods",
        nargs="+",
        choices=list(METHODS.keys()),
        default=list(METHODS.keys()),
        help="Methods to run",
    )
    parser.add_argument(
        "--papers",
        nargs="+",
        default=None,
        help="Paper slugs to evaluate (default: all)",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="Model to use for review",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output JSONL file for raw results (default: results/<timestamp>.jsonl)",
    )
    parser.add_argument(
        "--llm-judge",
        action="store_true",
        help="Use LLM-as-a-judge for recall evaluation in addition to string similarity",
    )
    parser.add_argument(
        "--judge-model",
        default=os.environ.get("JUDGE_MODEL", "anthropic/claude-haiku-4-5"),
        help="Model to use as the LLM judge",
    )
    args = parser.parse_args()

    papers = load_benchmark(BENCHMARK_FILE)
    if args.papers:
        papers = [p for p in papers if p["slug"] in args.papers]

    if not papers:
        print("No papers found. Run scripts/parse_examples.py first.")
        sys.exit(1)

    RESULTS_DIR.mkdir(exist_ok=True)
    if args.output:
        output_file = Path(args.output)
    else:
        import datetime
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = RESULTS_DIR / f"results_{ts}.jsonl"

    all_results = []

    for method_name in args.methods:
        method_fn = METHODS[method_name]
        print(f"\n{'='*60}")
        print(f"Running method: {method_name.upper()}")
        print(f"{'='*60}")

        for paper in papers:
            slug = paper["slug"]
            doc = paper["document_content"]
            ground_truth = paper["comments"]

            print(f"\n  Paper: {paper['title'][:60]}")
            print(f"  GT comments: {len(ground_truth)}")

            try:
                result = method_fn(slug, doc, args)
                print(f"  Found {result.num_comments} comments")

                metrics = evaluate(
                    result, ground_truth,
                    use_llm_judge=args.llm_judge,
                    judge_model=args.judge_model,
                )
                print(
                    f"  Recall: {metrics['recall']:.2f}  "
                    f"Cost: ${metrics['cost_usd']:.4f}"
                )

                record = {
                    "method": method_name,
                    "paper_slug": slug,
                    "paper_title": paper["title"],
                    "metrics": metrics,
                    "result": result.to_dict(),
                }
                all_results.append((method_name, slug, metrics))

                # Save incrementally
                with open(output_file, "a") as f:
                    f.write(json.dumps(record) + "\n")

            except Exception as e:
                print(f"  ERROR: {e}")
                import traceback
                traceback.print_exc()

    print_report(all_results)
    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
