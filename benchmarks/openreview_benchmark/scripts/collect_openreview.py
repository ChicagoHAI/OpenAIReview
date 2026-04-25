"""Collect paper forums (reviews, rebuttals, decisions) from the OpenReview API.

Usage:
    python benchmarks/openreview_benchmark/scripts/collect_openreview.py --venue ICLR.cc/2025/Conference --limit 10
    python benchmarks/openreview_benchmark/scripts/collect_openreview.py --forum-ids PwxYoMvmvy,HX5ujdsSon
"""

import argparse
import json
import sys
import time
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_TRACK_ROOT = _SCRIPT_DIR.parent
_DATA_DIR = _TRACK_ROOT / "data"
OUTPUT_DIR = _DATA_DIR / "openreview_raw"

if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from openreview_http import API_BASE_URL, create_openreview_session


def fetch_forum(session, forum_id: str) -> dict | None:
    """Fetch all notes for a single paper forum."""
    resp = session.get(
        f"{API_BASE_URL}/notes",
        params={"forum": forum_id},
        timeout=30,
    )
    if resp.status_code != 200:
        print(f"  ERROR {resp.status_code} for forum {forum_id}: {resp.text[:200]}")
        return None
    return resp.json()


def fetch_accepted_paper_ids(session, venue_id: str, limit: int) -> list[str]:
    """Fetch forum IDs of accepted papers for a venue."""
    paper_ids = []
    offset = 0
    batch_size = min(limit, 50)

    while len(paper_ids) < limit:
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
            print(f"  ERROR {resp.status_code} fetching paper list: {resp.text[:200]}")
            break

        data = resp.json()
        notes = data.get("notes", [])
        if not notes:
            break

        for note in notes:
            paper_ids.append(note["id"])
            if len(paper_ids) >= limit:
                break

        offset += batch_size
        time.sleep(0.5)

    return paper_ids


def save_forum(forum_data: dict, forum_id: str, output_dir: Path) -> Path:
    """Save raw forum JSON to disk."""
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{forum_id}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(forum_data, f, indent=2, ensure_ascii=False)
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Collect OpenReview paper forums.")
    parser.add_argument(
        "--venue",
        type=str,
        help="Venue ID, e.g. ICLR.cc/2025/Conference",
    )
    parser.add_argument(
        "--forum-ids",
        type=str,
        help="Comma-separated forum IDs to fetch directly",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Max number of papers to fetch when using --venue (default: 10)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(OUTPUT_DIR),
        help=f"Output directory for raw JSON files (default: {OUTPUT_DIR})",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Seconds to wait between API requests (default: 1.0)",
    )
    args = parser.parse_args()

    if not args.venue and not args.forum_ids:
        parser.error("Provide either --venue or --forum-ids")

    output_dir = Path(args.output_dir)
    session = create_openreview_session(mode="api", warmup_timeout=15.0)
    print("Session established.")

    if args.forum_ids:
        forum_ids = [fid.strip() for fid in args.forum_ids.split(",")]
    else:
        print(f"Fetching up to {args.limit} accepted paper IDs from {args.venue}...")
        forum_ids = fetch_accepted_paper_ids(session, args.venue, args.limit)
        print(f"Found {len(forum_ids)} paper IDs.")

    print(f"Collecting {len(forum_ids)} forums...\n")
    collected = 0
    for i, fid in enumerate(forum_ids):
        print(f"[{i + 1}/{len(forum_ids)}] Fetching {fid}...")
        data = fetch_forum(session, fid)
        if data and data.get("notes"):
            path = save_forum(data, fid, output_dir)
            n_notes = len(data["notes"])
            print(f"  Saved {n_notes} notes to {path}")
            collected += 1
        else:
            print(f"  Skipped (no data)")
        if i < len(forum_ids) - 1:
            time.sleep(args.delay)

    print(f"\nDone. Collected {collected}/{len(forum_ids)} forums in {output_dir}")


if __name__ == "__main__":
    main()
