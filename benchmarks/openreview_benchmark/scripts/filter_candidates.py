"""Find good benchmark candidate papers by sampling and ranking review quality.

Steps:
1. Fetch all accepted paper IDs from given venues (lightweight metadata only)
2. Randomly sample N papers from the full set
3. Fetch full forums for the sampled papers
4. Rank by average review text length across structured fields
5. Print a ranked table for manual curation

Usage:
    python benchmarks/openreview_benchmark/scripts/filter_candidates.py
    python benchmarks/openreview_benchmark/scripts/filter_candidates.py --sample-size 30 --seed 42
"""

import argparse
import json
import random
import sys
import time
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_TRACK_ROOT = _SCRIPT_DIR.parent
_DATA_DIR = _TRACK_ROOT / "data"

if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from openreview_http import API_BASE_URL, create_openreview_session, rewarm_session

VENUES = [
    "ICLR.cc/2025/Conference",
    "NeurIPS.cc/2025/Conference",
]

REVIEW_FIELDS = ["summary", "strengths", "weaknesses", "questions"]


def fetch_all_paper_ids(session, venue_id: str) -> list[dict]:
    """Fetch all accepted paper IDs and basic metadata for a venue."""
    papers = []
    offset = 0
    batch_size = 200

    while True:
        resp = session.get(
            f"{API_BASE_URL}/notes",
            params={
                "content.venueid": venue_id,
                "limit": batch_size,
                "offset": offset,
            },
            timeout=30,
        )
        if resp.status_code != 200:
            print(f"  ERROR {resp.status_code} at offset {offset}")
            break

        data = resp.json()
        notes = data.get("notes", [])
        if not notes:
            break

        for note in notes:
            content = note.get("content", {})
            title_field = content.get("title", {})
            area_field = content.get("primary_area", {})
            papers.append({
                "paper_id": note["id"],
                "venue": venue_id,
                "title": title_field.get("value", "") if isinstance(title_field, dict) else str(title_field),
                "primary_area": area_field.get("value", "") if isinstance(area_field, dict) else str(area_field),
            })

        offset += batch_size
        print(f"  Fetched {len(papers)} IDs so far (offset={offset})...")
        time.sleep(0.5)

    return papers


def fetch_forum_notes(session, forum_id: str) -> list[dict] | None:
    """Fetch all notes for a forum, retrying once with rewarm on 403."""
    for attempt in range(2):
        resp = session.get(
            f"{API_BASE_URL}/notes",
            params={"forum": forum_id},
            timeout=30,
        )
        if resp.status_code == 200:
            return resp.json().get("notes", [])
        if resp.status_code == 403 and attempt == 0:
            rewarm_session(session, timeout=15.0)
            time.sleep(1)
            continue
        break
    return None


def score_paper(notes: list[dict]) -> dict:
    """Compute review quality metrics from forum notes."""
    reviews = []
    has_author_response = False

    for note in notes:
        invitations = " ".join(note.get("invitations", []))
        if "Official_Review" in invitations:
            reviews.append(note)
        elif "Official_Comment" in invitations:
            sigs = " ".join(note.get("signatures", []))
            if "Authors" in sigs:
                has_author_response = True

    if not reviews:
        return {"num_reviews": 0, "avg_review_length": 0, "has_author_response": False}

    review_lengths = []
    for review in reviews:
        content = review.get("content", {})
        total = 0
        for field in REVIEW_FIELDS:
            val = content.get(field, {})
            text = val.get("value", "") if isinstance(val, dict) else str(val or "")
            total += len(text)
        review_lengths.append(total)

    return {
        "num_reviews": len(reviews),
        "avg_review_length": sum(review_lengths) // len(review_lengths),
        "min_review_length": min(review_lengths),
        "max_review_length": max(review_lengths),
        "has_author_response": has_author_response,
    }


def main():
    parser = argparse.ArgumentParser(description="Find benchmark candidate papers.")
    parser.add_argument(
        "--sample-size",
        type=int,
        default=50,
        help="Number of papers to sample per venue (default: 50)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Seconds between forum fetches (default: 1.0)",
    )
    args = parser.parse_args()

    random.seed(args.seed)
    session = create_openreview_session(mode="api", warmup_timeout=15.0)
    print("Session established.\n")

    # Step 1: Fetch all paper IDs from each venue
    all_papers = []
    for venue in VENUES:
        print(f"Fetching paper IDs from {venue}...")
        papers = fetch_all_paper_ids(session, venue)
        print(f"  Total: {len(papers)} papers\n")
        all_papers.extend(papers)

    print(f"Total papers across all venues: {len(all_papers)}\n")

    # Step 2: Random sample
    sample_size = min(args.sample_size * len(VENUES), len(all_papers))
    sampled = random.sample(all_papers, sample_size)
    print(f"Randomly sampled {len(sampled)} papers.\n")

    # Step 3: Fetch forums and score
    print("Fetching forums and scoring review quality...\n")
    candidates = []
    for i, paper in enumerate(sampled):
        pid = paper["paper_id"]
        print(f"  [{i + 1}/{len(sampled)}] {pid}: {paper['title'][:50]}...")
        notes = fetch_forum_notes(session, pid)
        if notes is None:
            print(f"    SKIPPED (fetch failed)")
            continue
        scores = score_paper(notes)
        paper.update(scores)
        candidates.append(paper)
        if i < len(sampled) - 1:
            time.sleep(args.delay)

    # Step 4: Filter and rank
    # Require: at least 1 author response, at least 3 reviews
    filtered = [
        c for c in candidates
        if c["has_author_response"] and c["num_reviews"] >= 3
    ]
    filtered.sort(key=lambda x: x["avg_review_length"], reverse=True)

    # Step 5: Print results
    print(f"\n{'=' * 120}")
    print(f"TOP CANDIDATES (filtered: {len(filtered)} of {len(candidates)} sampled)")
    print(f"{'=' * 120}")
    print(
        f"{'Rank':<5} {'Venue':<15} {'Reviews':<8} {'AvgLen':<8} {'MinLen':<8} "
        f"{'Primary Area':<35} {'Title'}"
    )
    print("-" * 120)

    for i, c in enumerate(filtered[:30]):
        venue_short = c["venue"].split("/")[0]
        area = (c["primary_area"] or "")[:33]
        title = c["title"][:55]
        print(
            f"{i + 1:<5} {venue_short:<15} {c['num_reviews']:<8} "
            f"{c['avg_review_length']:<8} {c['min_review_length']:<8} "
            f"{area:<35} {title}"
        )

    # Save full results for reference
    out_path = _DATA_DIR / "candidate_papers.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(filtered, f, indent=2, ensure_ascii=False)
    print(f"\nFull results saved to {out_path}")


if __name__ == "__main__":
    main()
