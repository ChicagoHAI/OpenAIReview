"""Evaluate OpenAIReview outputs against openreview_benchmark.jsonl using LLM judge.

Metrics (per paper): precision, recall, F1 — see ``reviewer.evaluate_openreview``.

Usage:
    # After running reviews with matching slugs (use --name <paper_id>):
    #   openaireview review paper.pdf --name jj7b3p5kLY --method zero_shot

    python benchmarks/openreview_benchmark/scripts/evaluate_openreview_benchmark.py \\
        --benchmark benchmarks/openreview_benchmark/data/openreview_benchmark.jsonl \\
        --results-dir ./review_results

    # Full JSON under the track (gitignored) + append a line to eval_history.jsonl:
    python benchmarks/openreview_benchmark/scripts/evaluate_openreview_benchmark.py \\
        --results-dir benchmarks/openreview_benchmark/results/reviews \\
        --save-full-report

    # Or set an explicit report path (--save-full-report not needed):
    python benchmarks/openreview_benchmark/scripts/evaluate_openreview_benchmark.py \\
        --results-dir ./review_results \\
        --output benchmarks/openreview_benchmark/results/my_run.json

Environment:
    OPENAI_API_KEY          Native OpenAI (set REVIEW_PROVIDER=openai if multiple keys)
    REVIEW_PROVIDER         e.g. openai
    OPENREVIEW_JUDGE_MODEL  Judge model (default: gpt-4o-mini)
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

_SCRIPT_DIR = Path(__file__).resolve().parent
_TRACK_ROOT = _SCRIPT_DIR.parent
_DATA_DIR = _TRACK_ROOT / "data"
_REPO_ROOT = _SCRIPT_DIR.parents[3]
_EVAL_HISTORY = _TRACK_ROOT / "eval_history.jsonl"
sys.path.insert(0, str(_REPO_ROOT / "src"))

from reviewer.evaluate_openreview import (  # noqa: E402
    comments_from_results_json,
    evaluate_openreview_pooled,
)


def _append_eval_history(
    *,
    benchmark: Path,
    results_dir: Path,
    judge_model: str,
    judge_provider: str | None,
    method_key: str | None,
    paper_ids: list[str],
    mean_p: float,
    mean_r: float,
    mean_f: float,
    full_report_rel: str | None,
) -> None:
    """One JSON line per run for REPORT-style tables (file lives under the track root)."""
    row = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "benchmark": str(benchmark.resolve()),
        "results_dir": str(results_dir.resolve()),
        "judge_model": judge_model,
        "judge_provider": judge_provider,
        "method_key": method_key,
        "paper_ids_evaluated": paper_ids,
        "num_papers": len(paper_ids),
        "mean": {
            "precision": round(mean_p, 6),
            "recall": round(mean_r, 6),
            "f1": round(mean_f, 6),
        },
        "full_report": full_report_rel,
    }
    with open(_EVAL_HISTORY, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description="LLM-judge evaluation for OpenReview track")
    parser.add_argument(
        "--benchmark",
        type=Path,
        default=_DATA_DIR / "openreview_benchmark.jsonl",
        help="Path to openreview_benchmark.jsonl",
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=Path("./review_results"),
        help="Directory with <paper_id>.json from openaireview review",
    )
    parser.add_argument(
        "--method-key",
        default=None,
        help="Key under methods in result JSON (default: first method)",
    )
    parser.add_argument(
        "--judge-model",
        default=os.environ.get("OPENREVIEW_JUDGE_MODEL", "gpt-4o-mini"),
        help="Model for LLM judge",
    )
    parser.add_argument(
        "--provider",
        default=os.environ.get("REVIEW_PROVIDER"),
        help="Provider for judge API (e.g. openai)",
    )
    parser.add_argument(
        "--papers",
        nargs="*",
        default=None,
        help="Optional paper_ids to evaluate (default: all in benchmark with results)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write full eval report JSON (per-paper metrics + means + run metadata)",
    )
    parser.add_argument(
        "--save-full-report",
        action="store_true",
        help=f"Write full report to {_TRACK_ROOT / 'results' / 'eval_<timestamp>.json'} (implies --results-dir is usually under results/reviews/)",
    )
    parser.add_argument(
        "--no-eval-history",
        action="store_true",
        help="Do not append a summary line to benchmarks/openreview_benchmark/eval_history.jsonl",
    )
    args = parser.parse_args()

    papers = []
    with open(args.benchmark, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                papers.append(json.loads(line))

    if args.papers:
        want = set(args.papers)
        papers = [p for p in papers if p["paper_id"] in want]

    rows = []
    for paper in papers:
        pid = paper["paper_id"]
        result_path = args.results_dir / f"{pid}.json"
        if not result_path.exists():
            print(f"  SKIP {pid}: no {result_path}")
            continue
        data = json.loads(result_path.read_text(encoding="utf-8"))
        try:
            preds = comments_from_results_json(data, method_key=args.method_key)
        except KeyError as e:
            print(f"  ERROR {pid}: {e}")
            continue

        m = evaluate_openreview_pooled(
            preds,
            paper,
            judge_model=args.judge_model,
            judge_provider=args.provider,
        )
        m["paper_id"] = pid
        m["title"] = (paper.get("title") or "")[:60]
        rows.append(m)
        print(
            f"  {pid}: P={m['precision']:.2f} R={m['recall']:.2f} F1={m['f1']:.2f} "
            f"(preds={m['num_predictions']}, covered_reviews={m['num_reviews_covered']}/{m['num_nonempty_reviews']})"
        )

    if not rows:
        print("No papers evaluated. Place review JSON files as <paper_id>.json in results-dir.")
        sys.exit(1)

    avg_p = sum(r["precision"] for r in rows) / len(rows)
    avg_r = sum(r["recall"] for r in rows) / len(rows)
    avg_f = sum(r["f1"] for r in rows) / len(rows)
    print(f"\nMean over {len(rows)} papers: precision={avg_p:.3f} recall={avg_r:.3f} f1={avg_f:.3f}")

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "benchmark": str(args.benchmark.resolve()),
        "results_dir": str(args.results_dir.resolve()),
        "judge_model": args.judge_model,
        "judge_provider": args.provider,
        "method_key": args.method_key,
        "num_papers": len(rows),
        "mean": {
            "precision": round(avg_p, 6),
            "recall": round(avg_r, 6),
            "f1": round(avg_f, 6),
        },
        "per_paper": rows,
    }

    full_report_path: Path | None = None
    if args.output is not None:
        full_report_path = args.output
    elif args.save_full_report:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        full_report_path = _TRACK_ROOT / "results" / f"eval_{ts}.json"

    full_report_rel: str | None = None
    if full_report_path is not None:
        full_report_path.parent.mkdir(parents=True, exist_ok=True)
        full_report_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        try:
            full_report_rel = str(full_report_path.resolve().relative_to(_TRACK_ROOT.resolve()))
        except ValueError:
            full_report_rel = str(full_report_path.resolve())
        print(f"\nWrote full report to {full_report_path}")

    if not args.no_eval_history:
        _append_eval_history(
            benchmark=args.benchmark,
            results_dir=args.results_dir,
            judge_model=args.judge_model,
            judge_provider=args.provider,
            method_key=args.method_key,
            paper_ids=[r["paper_id"] for r in rows],
            mean_p=avg_p,
            mean_r=avg_r,
            mean_f=avg_f,
            full_report_rel=full_report_rel,
        )
        print(f"Appended summary to {_EVAL_HISTORY}")


if __name__ == "__main__":
    main()
