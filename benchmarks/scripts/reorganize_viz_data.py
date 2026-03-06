"""
Reorganize viz/data.json into per-paper JSON files under viz/data/,
and merge in Phase 2 experiment results from results/experiments_phase2.jsonl.
"""

import json
import os
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))
from reviewer.utils import split_into_paragraphs, locate_comment_in_document

ROOT = Path(__file__).resolve().parent.parent
VIZ_DATA_DIR = ROOT / "viz" / "data"
OLD_DATA_JSON = ROOT / "viz" / "data.json"
PHASE2_RESULTS = ROOT / "results" / "experiments_phase2.jsonl"
DEFS_RERUN_RESULTS = ROOT / "results" / "experiments_defs_rerun.jsonl"
RERUN_INFERENCE = ROOT / "results" / "rerun_inference.jsonl"
RERUN_INFERENCE_RAG = ROOT / "results" / "rerun_inference_rag.jsonl"
PROGRESSIVE_RESULTS = ROOT / "results" / "incremental_inference.jsonl"
PROGRESSIVE_V2_RESULTS = ROOT / "results" / "incremental_v2.jsonl"
PROGRESSIVE_V3_RESULTS = ROOT / "results" / "incremental_v3.jsonl"
PROGRESSIVE_V4_RESULTS = ROOT / "results" / "incremental_v4.jsonl"
BENCHMARK_JSONL = ROOT / "data" / "benchmark.jsonl"

METHOD_LABELS = {
    "ground_truth": "Refine",
    "zero_shot": "Zero Shot",
    "few_shot": "Few Shot",
    "rag_local": "RAG Local",
    "rag_retrieved": "RAG Retrieved",
    "rag_retrieved_cot": "RAG Retrieved CoT",
    "rag_top_k_filter": "RAG Top-K Filter",
    "rag_nofilter_defs": "RAG No-Filter + Defs",
    "progressive": "Progressive",
    "progressive_full": "Progressive (Full)",
}

METHOD_ORDER = [
    "ground_truth",
    "zero_shot",
    "rag_local",
    "progressive",
    "progressive_full",
]


def load_phase2_results():
    """Load Phase 2 results, keyed by (method, paper_slug).

    Defs rerun results override the original phase2 results for defs methods.
    """
    results = {}
    with open(PHASE2_RESULTS) as f:
        for line in f:
            rec = json.loads(line)
            key = (rec["method"], rec["paper_slug"])
            results[key] = rec
    # Override with newer results (later files take precedence)
    for path in [DEFS_RERUN_RESULTS, RERUN_INFERENCE, RERUN_INFERENCE_RAG, PROGRESSIVE_RESULTS, PROGRESSIVE_V2_RESULTS, PROGRESSIVE_V3_RESULTS, PROGRESSIVE_V4_RESULTS]:
        if path.exists():
            with open(path) as f:
                for line in f:
                    rec = json.loads(line)
                    key = (rec["method"], rec["paper_slug"])
                    results[key] = rec
    return results


def build_method_entry(method_key, result_rec, paragraphs):
    """Build a method dict from a phase2 result record.

    Re-locates paragraph indices against current paragraph split.
    """
    label = METHOD_LABELS.get(method_key, method_key)
    res = result_rec["result"]
    comments = []
    for i, c in enumerate(res.get("comments", [])):
        quote = c.get("quote", "")
        para_idx = locate_comment_in_document(quote, paragraphs) if quote else None
        comments.append({
            "id": f"pred_{i}",
            "title": c.get("title", ""),
            "quote": quote,
            "explanation": c.get("explanation", ""),
            "comment_type": c.get("comment_type", ""),
            "paragraph_index": para_idx,
        })
    return {
        "label": label,
        "metrics": result_rec.get("metrics", {}),
        "overall_feedback": res.get("overall_feedback", ""),
        "comments": comments,
    }


def load_ground_truth():
    """Load GT comments from benchmark.jsonl, keyed by slug."""
    gt_by_slug = {}
    with open(BENCHMARK_JSONL) as f:
        for line in f:
            paper = json.loads(line)
            slug = paper["slug"]
            comments = []
            for i, c in enumerate(paper.get("comments", [])):
                comments.append({
                    "id": c.get("id", f"gt_{i}"),
                    "title": c.get("title", ""),
                    "paragraph": c.get("paragraph", ""),
                    "quote": c.get("quote", ""),
                    "message": c.get("message", ""),
                    "score": c.get("score"),
                    "comment_type": c.get("comment_type", ""),
                    "paragraph_index": c.get("paragraph_index"),
                })
            gt_by_slug[slug] = comments
    return gt_by_slug


def main():
    # Load existing data.json
    with open(OLD_DATA_JSON) as f:
        old_data = json.load(f)

    # Load phase2 results
    phase2 = load_phase2_results()

    # Load ground truth
    gt_by_slug = load_ground_truth()

    # Create output directory
    VIZ_DATA_DIR.mkdir(parents=True, exist_ok=True)

    index_papers = []

    for paper in old_data["papers"]:
        slug = paper["slug"]

        # Start with only methods we want to show
        methods = {}

        # Update ground_truth from benchmark.jsonl
        if slug in gt_by_slug:
            gt_comments = gt_by_slug[slug]
            methods["ground_truth"] = {
                "label": "Refine",
                "comments": gt_comments,
            }

        # Get paragraphs for re-locating comments
        paras = [p["text"] for p in paper["paragraphs"]]

        # Add/update phase2 methods
        for method_key in ["zero_shot", "rag_local", "progressive", "progressive_full"]:
            key = (method_key, slug)
            if key in phase2:
                methods[method_key] = build_method_entry(method_key, phase2[key], paras)

        # Build per-paper JSON
        paper_data = {
            "slug": slug,
            "title": paper["title"],
            "authors": paper["authors"],
            "field": paper["field"],
            "paragraphs": paper["paragraphs"],
            "methods": methods,
        }

        # Write per-paper file
        paper_file = VIZ_DATA_DIR / f"{slug}.json"
        with open(paper_file, "w") as f:
            json.dump(paper_data, f, indent=2)
        print(f"Wrote {paper_file} ({len(methods)} methods, {len(paper['paragraphs'])} paragraphs)")

        # Build index entry
        num_gt = len(gt_by_slug.get(slug, methods.get("ground_truth", {}).get("comments", [])))
        index_papers.append({
            "slug": slug,
            "title": paper["title"],
            "field": paper["field"],
            "num_gt_comments": num_gt,
        })

    # Write index.json
    index_data = {
        "papers": index_papers,
        "method_order": METHOD_ORDER,
    }
    index_file = VIZ_DATA_DIR / "index.json"
    with open(index_file, "w") as f:
        json.dump(index_data, f, indent=2)
    print(f"\nWrote {index_file}")
    print(f"  Papers: {len(index_papers)}")
    print(f"  Method order: {METHOD_ORDER}")


if __name__ == "__main__":
    main()
