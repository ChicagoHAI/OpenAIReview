"""Normalize raw OpenReview forum JSON into benchmark JSONL format.

Reads raw forum JSON files (from collect_openreview.py) and produces a single
JSONL file with one paper per line, following a schema designed for the
OpenReview benchmark track.

Usage:
    python benchmarks/openreview_benchmark/scripts/normalize_openreview.py
    python benchmarks/openreview_benchmark/scripts/normalize_openreview.py --raw-dir benchmarks/openreview_benchmark/data/openreview_raw --output benchmarks/openreview_benchmark/data/openreview_benchmark.jsonl
"""

import argparse
import json
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_TRACK_ROOT = _SCRIPT_DIR.parent
_DATA_DIR = _TRACK_ROOT / "data"
RAW_DIR = _DATA_DIR / "openreview_raw"
OUTPUT_PATH = _DATA_DIR / "openreview_benchmark.jsonl"


def classify_note(note: dict) -> str:
    """Classify a note by its invitation type."""
    if note.get("replyto") is None:
        return "submission"
    invitations = " ".join(note.get("invitations", []))
    if "Official_Review" in invitations:
        return "review"
    if "Meta_Review" in invitations:
        return "meta_review"
    if "Decision" in invitations:
        return "decision"
    if "Official_Comment" in invitations:
        return "comment"
    if "Rebuttal" in invitations:
        return "rebuttal"
    return "other"


def extract_value(field) -> str | list | None:
    """Extract the 'value' from an OpenReview content field."""
    if isinstance(field, dict):
        return field.get("value")
    return field


def extract_reviewer_id(note: dict) -> str:
    """Extract anonymous reviewer ID from signatures."""
    sigs = note.get("signatures", [])
    if sigs:
        return sigs[0].split("/")[-1]
    return "Unknown"


def extract_author_type(note: dict) -> str:
    """Determine whether a comment is from authors, a reviewer, or an AC."""
    sigs = " ".join(note.get("signatures", []))
    if "Authors" in sigs:
        return "authors"
    if "Area_Chair" in sigs:
        return "area_chair"
    if "Reviewer" in sigs:
        return "reviewer"
    return "other"


def normalize_review(note: dict) -> dict:
    """Convert a raw review note into the benchmark review schema."""
    content = note.get("content", {})
    return {
        "review_id": note["id"],
        "reviewer": extract_reviewer_id(note),
        "rating": extract_value(content.get("rating", {})),
        "confidence": extract_value(content.get("confidence", {})),
        "soundness": extract_value(content.get("soundness", {})),
        "presentation": extract_value(content.get("presentation", {})),
        "contribution": extract_value(content.get("contribution", {})),
        "summary": extract_value(content.get("summary", {})),
        "strengths": extract_value(content.get("strengths", {})),
        "weaknesses": extract_value(content.get("weaknesses", {})),
        "questions": extract_value(content.get("questions", {})),
    }


def normalize_comment(note: dict) -> dict:
    """Convert a raw comment/rebuttal note into the benchmark discussion schema."""
    content = note.get("content", {})
    text = extract_value(content.get("comment", {})) or extract_value(
        content.get("rebuttal", {})
    )
    return {
        "comment_id": note["id"],
        "replyto": note.get("replyto"),
        "author_type": extract_author_type(note),
        "reviewer": extract_reviewer_id(note) if "Reviewer" in " ".join(note.get("signatures", [])) else None,
        "comment": text or "",
    }


def normalize_forum(raw_data: dict) -> dict | None:
    """Convert a full raw forum into the benchmark paper schema."""
    notes = raw_data.get("notes", [])
    if not notes:
        return None

    submission = None
    reviews = []
    discussions = []
    meta_review = None
    decision = None

    for note in notes:
        note_type = classify_note(note)
        if note_type == "submission":
            submission = note
        elif note_type == "review":
            reviews.append(normalize_review(note))
        elif note_type in ("comment", "rebuttal"):
            discussions.append(normalize_comment(note))
        elif note_type == "meta_review":
            content = note.get("content", {})
            meta_review = {
                "metareview": extract_value(content.get("metareview", {})),
                "justification_for_why_not_higher_score": extract_value(
                    content.get("justification_for_why_not_higher_score", {})
                ),
                "justification_for_why_not_lower_score": extract_value(
                    content.get("justification_for_why_not_lower_score", {})
                ),
            }
        elif note_type == "decision":
            content = note.get("content", {})
            decision = extract_value(content.get("decision", {}))

    if submission is None:
        return None

    content = submission.get("content", {})
    venue_id = extract_value(content.get("venueid", {})) or ""

    # Derive venue and year from venue_id (e.g. "ICLR.cc/2025/Conference")
    parts = venue_id.split("/")
    year = None
    for part in parts:
        if part.isdigit() and len(part) == 4:
            year = int(part)
            break

    paper = {
        "paper_id": submission["id"],
        "forum_url": f"https://openreview.net/forum?id={submission['id']}",
        "venue": venue_id,
        "year": year,
        "title": extract_value(content.get("title", {})),
        "authors": extract_value(content.get("authors", {})),
        "abstract": extract_value(content.get("abstract", {})),
        "keywords": extract_value(content.get("keywords", {})),
        "primary_area": extract_value(content.get("primary_area", {})),
        "pdf_url": f"https://openreview.net/pdf?id={submission['id']}",
        "decision": decision,
        "num_reviews": len(reviews),
        "num_discussions": len(discussions),
        "reviews": reviews,
        "discussions": discussions,
        "meta_review": meta_review,
    }

    return paper


def main():
    parser = argparse.ArgumentParser(
        description="Normalize raw OpenReview forums into benchmark JSONL."
    )
    parser.add_argument(
        "--raw-dir",
        type=str,
        default=str(RAW_DIR),
        help=f"Directory with raw forum JSON files (default: {RAW_DIR})",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(OUTPUT_PATH),
        help=f"Output JSONL path (default: {OUTPUT_PATH})",
    )
    args = parser.parse_args()

    raw_dir = Path(args.raw_dir)
    output_path = Path(args.output)

    raw_files = sorted(raw_dir.glob("*.json"))
    if not raw_files:
        print(f"No JSON files found in {raw_dir}")
        return

    print(f"Normalizing {len(raw_files)} forums from {raw_dir}...")
    papers = []
    for raw_file in raw_files:
        with open(raw_file, encoding="utf-8") as f:
            raw_data = json.load(f)
        paper = normalize_forum(raw_data)
        if paper:
            papers.append(paper)
            n_rev = paper["num_reviews"]
            n_disc = paper["num_discussions"]
            title = paper["title"] or "(no title)"
            print(f"  {raw_file.name}: {title[:60]}... ({n_rev} reviews, {n_disc} discussions)")
        else:
            print(f"  {raw_file.name}: SKIPPED (no submission note found)")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for paper in papers:
            f.write(json.dumps(paper, ensure_ascii=False) + "\n")

    print(f"\nWrote {len(papers)} papers to {output_path}")


if __name__ == "__main__":
    main()
