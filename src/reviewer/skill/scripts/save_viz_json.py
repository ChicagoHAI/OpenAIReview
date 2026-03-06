#!/usr/bin/env python3
"""Build viz-compatible JSON from review findings and save to review_results/.

Usage:
    python3 ~/.claude/commands/openaireview/scripts/save_viz_json.py /tmp/<slug>_review [--output-dir ./review_results]

Expects these files in the review workspace:
    metadata.json          -- {"title": "...", "slug": "..."}
    full_text.md           -- complete paper text
    final_issues.json      -- array of {title, quote, explanation, comment_type, severity}
    overall_assessment.txt -- overall assessment paragraph (optional)

Merges with existing review_results/<slug>.json if present, preserving other methods.
"""

import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Save viz-compatible review JSON")
    parser.add_argument("review_dir", help="Path to the review workspace")
    parser.add_argument("--output-dir", default="./review_results", help="Output directory")
    parser.add_argument("--method-key", default="openaireview__claude")
    parser.add_argument("--method-label", default="OpenAIReview (claude)")
    args = parser.parse_args()

    review_dir = Path(args.review_dir)

    # Load workspace files
    metadata = json.loads((review_dir / "metadata.json").read_text())
    slug = metadata["slug"]
    title = metadata["title"]
    text = (review_dir / "full_text.md").read_text()

    issues_path = review_dir / "final_issues.json"
    if not issues_path.exists():
        print("ERROR: final_issues.json not found in workspace", file=sys.stderr)
        sys.exit(1)
    issues = json.loads(issues_path.read_text())

    overall_path = review_dir / "overall_assessment.txt"
    overall = overall_path.read_text().strip() if overall_path.exists() else ""

    # Split into paragraphs and locate quotes
    from reviewer.utils import split_into_paragraphs, locate_comment_in_document

    paragraphs = split_into_paragraphs(text)
    indexed = [{"index": i, "text": p} for i, p in enumerate(paragraphs)]

    comments = []
    for i, issue in enumerate(issues):
        quote = issue.get("quote", "")
        para_idx = locate_comment_in_document(quote, paragraphs)
        if para_idx is None:
            para_idx = 0
        comments.append({
            "id": f"{args.method_key}_{i}",
            "title": issue.get("title", "Untitled"),
            "quote": quote,
            "explanation": issue.get("explanation", ""),
            "comment_type": issue.get("comment_type", "technical"),
            "severity": issue.get("severity", "moderate"),
            "paragraph_index": para_idx,
        })

    method_data = {
        "label": args.method_label,
        "model": "claude",
        "overall_feedback": overall,
        "comments": comments,
        "cost_usd": 0,
        "prompt_tokens": 0,
        "completion_tokens": 0,
    }

    # Merge with existing file or create new
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{slug}.json"

    if output_path.exists():
        data = json.loads(output_path.read_text())
        data["methods"][args.method_key] = method_data
    else:
        data = {
            "slug": slug,
            "title": title,
            "paragraphs": indexed,
            "methods": {args.method_key: method_data},
        }

    output_path.write_text(json.dumps(data, indent=2))
    print(f"Results saved to {output_path} \u2014 run `openaireview serve` to visualize.")


if __name__ == "__main__":
    main()
