#!/usr/bin/env python
"""Load SNOR v1 paper metadata.

SNOR v1 (Zenodo 15866613, CC-BY 4.0) links OpenReview submissions from
ICLR 2017-2025 and NeurIPS 2021-2025 to Semantic Scholar, with citation
counts, venue, decisions, and reviewer scores. We use only the
`normalized_papers.jsonl` file (448 MB); the comments file (1.3 GB) is
not needed for paper selection.

Each record has:
    id                     OpenReview forum id (str)
    semantic_scholar_id    S2 paper id (str or None)
    raw_decision           e.g. "ICLR 2017 Oral", "ICLR 2022 Reject"
    normalized_decision    e.g. "Oral", "Spotlight", "Poster", "Reject"
    title                  (str)
    accepted               (bool)
    publication_venue      S2 venue name, may be "" for unpublished
    citation_count         (int)
    authors                list[str]
    conference_year        (str, e.g. "2022")
    conference_name        (str, e.g. "iclr", "neurips")
    conf_id                (str, e.g. "iclr2022")
    review_scores          list[float]
    review_score_avg       (float)
    review_confidences     list[float]
    review_confidence_avg  (float)

Embeddings and abstracts are dropped on load to keep memory reasonable.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Iterator

HERE = Path(__file__).resolve().parent
CACHE_DIR = HERE / ".cache" / "snor"
PAPERS_FILE = CACHE_DIR / "normalized_papers.jsonl"
SNOR_URL = (
    "https://zenodo.org/records/15866613/files/normalized_papers.jsonl"
    "?download=1"
)

# Fields we keep on load. Drops `embedding` (768 floats per row) and
# `abstract`/`keywords` (not needed for selection).
KEEP_FIELDS = {
    "id", "semantic_scholar_id", "raw_decision", "normalized_decision",
    "title", "accepted", "publication_venue", "publication_venue_id",
    "citation_count", "authors", "conference_year", "conference_name",
    "conf_id", "review_scores", "review_score_avg",
    "review_confidences", "review_confidence_avg",
}


def ensure_download(force: bool = False) -> Path:
    """Download normalized_papers.jsonl to CACHE_DIR if not present.

    Uses curl with resume (-C -) so interrupted downloads pick up where
    they left off.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if PAPERS_FILE.exists() and not force:
        size_mb = PAPERS_FILE.stat().st_size / 1e6
        print(f"SNOR cached: {PAPERS_FILE} ({size_mb:.1f} MB)")
        return PAPERS_FILE

    print(f"Downloading SNOR v1 from Zenodo (~448 MB)...")
    cmd = ["curl", "-L", "-C", "-", "-#", "-o", str(PAPERS_FILE), SNOR_URL]
    r = subprocess.run(cmd)
    if r.returncode != 0:
        raise RuntimeError(f"curl failed with exit code {r.returncode}")
    return PAPERS_FILE


def iter_records(
    path: Path | None = None,
    venues: Iterable[str] | None = None,
    years: Iterable[int] | None = None,
) -> Iterator[dict]:
    """Stream SNOR records, optionally filtered by venue/year.

    venues: lowercase conference names, e.g. {"iclr", "neurips"}.
    years: int years, e.g. {2021, 2022}.
    Yields dicts with only KEEP_FIELDS.
    """
    if path is None:
        path = ensure_download()
    venue_set = {v.lower() for v in venues} if venues else None
    year_set = {str(y) for y in years} if years else None

    with path.open("r") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if venue_set and r.get("conference_name", "").lower() not in venue_set:
                continue
            if year_set and str(r.get("conference_year", "")) not in year_set:
                continue
            yield {k: r[k] for k in KEEP_FIELDS if k in r}


def load_cohort(venues: Iterable[str], years: Iterable[int]) -> list[dict]:
    """Load all SNOR records for the given venue/year cohort into memory."""
    records = list(iter_records(venues=venues, years=years))
    print(f"Loaded {len(records)} SNOR records for "
          f"venues={sorted(venues)} years={sorted(years)}")
    return records


def summarize(records: list[dict]) -> None:
    """Print a breakdown of decisions, citation stats, never-published count."""
    from collections import Counter
    by_conf = Counter(r.get("conf_id") for r in records)
    by_decision = Counter(r.get("normalized_decision") for r in records)
    accepted = sum(1 for r in records if r.get("accepted"))
    rejected = len(records) - accepted
    have_s2 = sum(1 for r in records if r.get("semantic_scholar_id"))
    no_venue = sum(
        1 for r in records
        if not r.get("accepted")
        and not (r.get("publication_venue") or "").strip()
    )

    print(f"\n  Conferences: {dict(by_conf)}")
    print(f"  Normalized decisions: {dict(by_decision)}")
    print(f"  Accepted: {accepted}    Rejected: {rejected}")
    print(f"  With S2 id: {have_s2}   Rejected & no publication_venue: {no_venue}")

    cites = [r.get("citation_count") or 0 for r in records]
    if cites:
        cites.sort()
        n = len(cites)
        print(f"  Citation count  min={cites[0]}  "
              f"p50={cites[n // 2]}  p90={cites[int(n * 0.9)]}  "
              f"p99={cites[int(n * 0.99)]}  max={cites[-1]}")


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--download-only", action="store_true",
                    help="Download the file and exit.")
    ap.add_argument("--venues", nargs="+", default=["iclr", "neurips"])
    ap.add_argument("--years", nargs="+", type=int, default=[2021, 2022])
    args = ap.parse_args()

    if args.download_only:
        ensure_download()
        return

    records = load_cohort(args.venues, args.years)
    summarize(records)


if __name__ == "__main__":
    main()
