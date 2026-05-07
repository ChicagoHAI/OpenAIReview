#!/usr/bin/env python3
"""Score experimental reviews and generate report.

Quote matching mirrors score.py _substring_match exactly (uses
reviewer.utils._normalize_for_match and _quote_coverage).
Explanation matching uses LLM-as-judge (score.py _explanation_match_llm,
threshold >= 3) with google/gemini-3-flash-preview by default.

Usage:
    python report_experimental.py
    python report_experimental.py --reviews ./experimental_comments/zero_shot \
                                   --results ./results/zero_shot \
                                   --score-model google/gemini-3-flash-preview
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

BENCH_DIR = Path(__file__).resolve().parents[1] / "perturbation"
sys.path.insert(0, str(BENCH_DIR.parent))

from perturbation.generate_report import generate_report
from perturbation.score import _explanation_match_llm
from reviewer.utils import _normalize_for_match, _quote_coverage


# ── Scoring (mirrors score.py exactly) ───────────────────────────────────────

_FUZZY_QUOTE_THRESHOLD = 0.75


def _quote_match(comment_quote: str, perturbed: str) -> bool:
    """Same logic as score.py _substring_match."""
    if not comment_quote or not perturbed:
        return False
    q = _normalize_for_match(comment_quote)
    p = _normalize_for_match(perturbed)
    if not p:
        return False
    if p in q:
        return True
    return _quote_coverage(p, q) >= _FUZZY_QUOTE_THRESHOLD


def score_paper(perturbations: list[dict], comments: list[dict], score_model: str) -> dict:
    detected = []
    missed = []
    for p in perturbations:
        found = False
        for c in comments:
            if _quote_match(c.get("quote", ""), p["perturbed"]):
                if _explanation_match_llm(c.get("explanation", ""), p["why_wrong"], score_model):
                    found = True
                    break
        pid = p["perturbation_id"]
        if found:
            detected.append(pid)
        else:
            missed.append(pid)
    n = len(perturbations)
    return {
        "n_injected": n,
        "n_detected": len(detected),
        "recall": len(detected) / n if n else 0.0,
        "n_total_comments": len(comments),
        "detected": detected,
        "missed": missed,
    }


# ── Data loading ──────────────────────────────────────────────────────────────

def find_manifest(perturbation_results: Path, paper_id: str) -> Path | None:
    for m in perturbation_results.rglob(f"*/{paper_id}/experimental/*_kept_perturbations.json"):
        return m
    return None


# ── Main pipeline ─────────────────────────────────────────────────────────────

def _score_one_method(method: str, method_dir: Path, perturbation_results: Path,
                      results_dir: Path, score_model: str) -> None:
    for review_path in sorted(method_dir.glob("*.json")):
        paper_id = review_path.stem
        review = json.loads(review_path.read_text())
        model_slug = review.get("model", "unknown").split("/")[-1]
        comments = review.get("comments", [])

        manifest_path = find_manifest(perturbation_results, paper_id)
        if not manifest_path:
            print(f"  WARNING: no manifest for {paper_id}, skipping.", file=sys.stderr)
            continue

        perturbations = json.loads(manifest_path.read_text()).get("perturbations", [])
        if not perturbations:
            print(f"  WARNING: empty manifest for {paper_id}, skipping.", file=sys.stderr)
            continue

        print(f"  Scoring {paper_id} ({method})...", file=sys.stderr)
        score_data = score_paper(perturbations, comments, score_model)

        paper_label = f"paper_{paper_id}"

        # Manifest → perturb dir (ground truth for generate_report)
        perturb_dir = results_dir / "perturb" / "experimental" / paper_label
        perturb_dir.mkdir(parents=True, exist_ok=True)
        dest = perturb_dir / manifest_path.name
        if not dest.exists():
            shutil.copy2(manifest_path, dest)

        # Score JSON → directory structure generate_report.py reads:
        # <model_slug>/<error_type>/<method>/paper_*/score/<score_method>/*.json
        score_dir = results_dir / model_slug / "experimental" / method / paper_label / "score" / "llm"
        score_dir.mkdir(parents=True, exist_ok=True)
        score_filename = manifest_path.name.replace("_kept_perturbations.json", "_score.json")
        (score_dir / score_filename).write_text(json.dumps(score_data, indent=2))


def run_scoring(reviews_root: Path, perturbation_results: Path,
                results_dir: Path, score_model: str) -> None:
    results_dir.mkdir(parents=True, exist_ok=True)

    if any(reviews_root.glob("*.json")):
        _score_one_method(reviews_root.name, reviews_root, perturbation_results,
                          results_dir, score_model)
    else:
        for method_dir in sorted(reviews_root.iterdir()):
            if not method_dir.is_dir() or method_dir.name.startswith("."):
                continue
            _score_one_method(method_dir.name, method_dir, perturbation_results,
                               results_dir, score_model)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reviews", type=Path, default=Path("./experimental_comments"),
                        help="Root reviews dir with method subdirs (or single method dir)")
    parser.add_argument("--perturbations", type=Path, default=Path("./perturbation_results"),
                        help="Root perturbation_results directory")
    parser.add_argument("--results", type=Path, default=Path("./results"),
                        help="Output directory for scores + report")
    parser.add_argument("--score-model", default="google/gemini-3-flash-preview",
                        help="Model for LLM-as-judge explanation scoring (default: gemini-3-flash-preview)")
    args = parser.parse_args()

    print("Scoring...", file=sys.stderr)
    run_scoring(args.reviews, args.perturbations, args.results, args.score_model)

    print("Generating report...", file=sys.stderr)
    md = generate_report([args.results])
    report_path = args.results / "report.md"
    report_path.write_text(md)
    print(f"Report saved to {report_path}", file=sys.stderr)
    print(md)
