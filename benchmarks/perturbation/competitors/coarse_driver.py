#!/usr/bin/env python
"""Driver script run inside the coarse venv.

Invokes `coarse.review_paper` on a single paper + model and writes a JSON
file matching the perturbation benchmark schema (methods dict with quote /
explanation comments, consumable by `openaireview score`).

Usage (called by coarse_adapter.py):
    /path/to/coarse/.venv/bin/python coarse_driver.py \\
        --paper <corrupted.md> --model <provider/model> --out <review.json>

This script imports from `coarse` and must therefore run inside the coarse
venv; it has no dependency on the openaireview codebase.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from pathlib import Path

from coarse import review_paper


def build_pipeline_json(paper_path: Path, model: str) -> dict:
    """Run review and shape the result into the pipeline review schema."""
    start = time.time()
    review, _markdown, _paper_text = review_paper(
        pdf_path=paper_path,
        model=model,
        skip_cost_gate=True,
    )
    elapsed = time.time() - start

    model_slug = model.split("/")[-1]
    method_key = f"coarse__{model_slug}"

    overall_parts: list[str] = []
    if review.overall_feedback.summary:
        overall_parts.append(review.overall_feedback.summary)
    if review.overall_feedback.assessment:
        overall_parts.append(review.overall_feedback.assessment)
    for issue in review.overall_feedback.issues:
        overall_parts.append(f"**{issue.title}**\n\n{issue.body}")
    if review.overall_feedback.recommendation:
        overall_parts.append(f"**Recommendation**: {review.overall_feedback.recommendation}")
    overall_feedback = "\n\n".join(p for p in overall_parts if p)

    comments = []
    for dc in review.detailed_comments:
        comments.append({
            "id": f"coarse_{dc.number}",
            "title": dc.title,
            "quote": dc.quote,
            "explanation": dc.feedback,
            "comment_type": "technical",
            "paragraph_index": None,
        })

    return {
        "slug": paper_path.stem,
        "title": review.title or paper_path.stem,
        "paragraphs": [],
        "methods": {
            method_key: {
                "label": f"coarse ({model_slug})",
                "model": model,
                "overall_feedback": overall_feedback,
                "comments": comments,
                "cost_usd": 0.0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "elapsed_s": elapsed,
            }
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--paper", required=True, type=Path)
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    try:
        data = build_pipeline_json(args.paper, args.model)
    except Exception:
        traceback.print_exc()
        err = {
            "slug": args.paper.stem,
            "error": traceback.format_exc(),
            "methods": {},
        }
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(err, indent=2))
        return 1

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, indent=2))
    print(f"[coarse_driver] wrote {args.out} ({len(data['methods'][next(iter(data['methods']))]['comments'])} comments)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
