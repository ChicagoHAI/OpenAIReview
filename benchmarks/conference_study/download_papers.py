#!/usr/bin/env python
"""Download papers for the accepted-vs-rejected study.

Two data sources:
  --source papercopilot  (default) ICLR only, has explicit accept/reject decisions.
  --source hf            AlgorithmicResearchGroup/openreview-papers-with-reviews
                         on HuggingFace. Multi-venue (ICLR, NeurIPS, CoRL, etc.),
                         uses review score thresholds instead of decisions.

Three modes:

1. **manifest.json exists** (normal case): downloads PDFs for the papers
   listed in the manifest, skipping any already on disk. Manifest is not
   modified.

2. **--add** (with existing manifest): selects N more papers per group,
   downloads their PDFs, and appends them to the manifest.

3. **No manifest.json** (bootstrapping): selects N papers per group,
   downloads their PDFs, and writes a new manifest.json.

Usage:
    python download_papers.py                                    # download from manifest
    python download_papers.py --add -n 5                         # add 5 more (papercopilot)
    python download_papers.py --source hf --venue ICLR --year 2023 -n 10
    python download_papers.py --source hf --venue NeurIPS --year 2022 -n 10
    python download_papers.py --source hf --add -n 5 --group rejected

Score thresholds:
    Accepted: avg rating >= --accepted-threshold (default 7.0).
              Papercopilot uses Oral/Spotlight status instead of threshold.
    Rejected: avg rating <= --rejected-threshold (default 4.0).
              Both sources use this threshold.
    Papers in between are skipped (gray zone).
    HF source requires >= --min-reviews reviews per paper (default 2).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

PAPERCOPILOT_URL = (
    "https://raw.githubusercontent.com/Papercopilot/paperlists/main"
    "/iclr/iclr{year}.json"
)


def fetch_dataset(year: int, cache_dir: Path) -> list[dict]:
    """Download (or load cached) papercopilot ICLR dataset."""
    cache = cache_dir / f"iclr{year}.json"
    if cache.exists():
        print(f"Using cached dataset: {cache}")
        return json.loads(cache.read_text())

    url = PAPERCOPILOT_URL.format(year=year)
    print(f"Downloading {url} ...")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache.write_bytes(data)
    return json.loads(data)


def avg_field(paper: dict, key: str) -> float | None:
    """Extract average from papercopilot's [mean, std] lists."""
    v = paper.get(key)
    if isinstance(v, list) and v:
        return v[0]
    return None


def select_accepted(dataset: list[dict], n: int) -> list[dict]:
    """Pick N accepted papers (Oral/Spotlight, highest-rated first)."""
    candidates = []
    for p in dataset:
        if p["status"] not in ("Oral", "Spotlight"):
            continue
        r = avg_field(p, "rating_avg")
        if r is None:
            continue
        candidates.append((r, p))
    candidates.sort(key=lambda x: -x[0])  # highest rating first
    if len(candidates) < n:
        print(f"  Warning: only {len(candidates)} Oral/Spotlight papers available, "
              f"requested {n}")
    return [p for _, p in candidates[:n]]


def select_rejected(dataset: list[dict], n: int,
                    threshold: float = 4.0) -> list[dict]:
    """Pick N rejected papers with substantive reviews.

    Filters: status=Reject, rating_avg <= threshold, >= 3 reviewers,
    avg review word-count > 400.
    """
    candidates = []
    for p in dataset:
        if p["status"] != "Reject":
            continue
        r = avg_field(p, "rating_avg")
        wc = avg_field(p, "wc_review_avg")
        n_rev = len(p.get("rating", "").split(";")) if p.get("rating") else 0
        if r is None or wc is None:
            continue
        if r > threshold or wc < 400 or n_rev < 3:
            continue
        pdf_kb = (p.get("pdf_size") or 0) / 1024
        candidates.append((pdf_kb, r, p))
    # Sort by PDF size descending (proxy for longer papers)
    candidates.sort(key=lambda x: -x[0])
    if len(candidates) < n:
        print(f"  Warning: only {len(candidates)} eligible rejected papers, "
              f"requested {n}")
    return [p for _, _, p in candidates[:n]]


# ---------------------------------------------------------------------------
# HuggingFace data source
# ---------------------------------------------------------------------------

HF_DATASET = "AlgorithmicResearchGroup/openreview-papers-with-reviews"

# Map short venue names to patterns in the HF dataset's venue field.
VENUE_PATTERNS = {
    "iclr": "ICLR",
    "neurips": "NeurIPS",
    "corl": "CoRL",
    "uai": "UAI",
    "midl": "MIDL",
}


def fetch_hf_dataset(venue: str, year: int, cache_dir: Path,
                     min_reviews: int = 2) -> list[dict]:
    """Load the HF dataset, filter by venue/year, aggregate per paper.

    Returns a list of dicts with keys:
        paper_id, title, pdf_url, rating_avg, ratings, num_reviews,
        confidence_avg, venue, year.
    Cached as JSON after first aggregation.
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache = cache_dir / f"hf_{venue}_{year}.json"
    if cache.exists():
        print(f"Using cached HF data: {cache}")
        return json.loads(cache.read_text())

    from collections import defaultdict
    from datasets import load_dataset

    pattern = VENUE_PATTERNS.get(venue.lower(), venue)
    year_str = str(year)

    print(f"Loading HF dataset (filtering {pattern} {year})...")
    ds = load_dataset(HF_DATASET, split="train", streaming=True)

    papers: dict[str, dict] = defaultdict(lambda: {
        "ratings": [], "confidences": [], "title": "", "pdf_url": "", "venue": "",
    })

    for row in ds:
        v = row.get("venue", "")
        y = row.get("year", "")
        if pattern not in v or y != year_str:
            continue
        # Skip workshops/tiny papers.
        v_lower = v.lower()
        if "workshop" in v_lower or "tiny" in v_lower:
            continue

        pid = row["paper_id"]
        sr = row.get("structured_review") or {}
        rating = sr.get("review_rating_integer")
        confidence = sr.get("review_confidence_integer")

        papers[pid]["title"] = row["paper_title"]
        papers[pid]["pdf_url"] = row.get("pdf_url", "")
        papers[pid]["venue"] = v
        if rating is not None:
            papers[pid]["ratings"].append(rating)
        if confidence is not None:
            papers[pid]["confidences"].append(confidence)

    # Aggregate and filter.
    result = []
    for pid, p in papers.items():
        if len(p["ratings"]) < min_reviews:
            continue
        avg_r = sum(p["ratings"]) / len(p["ratings"])
        avg_c = (sum(p["confidences"]) / len(p["confidences"])
                 if p["confidences"] else None)
        result.append({
            "paper_id": pid,
            "title": p["title"],
            "pdf_url": p["pdf_url"],
            "rating_avg": round(avg_r, 2),
            "ratings": p["ratings"],
            "num_reviews": len(p["ratings"]),
            "confidence_avg": round(avg_c, 2) if avg_c else None,
            "venue": p["venue"],
            "year": year,
        })

    print(f"  {len(result)} papers with >= {min_reviews} reviews")
    cache.write_text(json.dumps(result, indent=2) + "\n")
    return result


def select_and_download_hf(
    papers: list[dict],
    n: int,
    venue: str,
    year: int,
    min_pages: int,
    accepted_threshold: float,
    rejected_threshold: float,
    out_dir: Path,
    exclude_ids: set[str],
    groups: list[str] | None = None,
) -> list[dict]:
    """Select papers by score threshold, download PDFs, return manifest entries."""
    if groups is None:
        groups = ["accepted", "rejected"]

    # Build candidate pools.
    acc_pool = sorted(
        [p for p in papers if p["rating_avg"] >= accepted_threshold
         and p["paper_id"] not in exclude_ids],
        key=lambda x: -x["rating_avg"],
    )
    rej_pool = sorted(
        [p for p in papers if p["rating_avg"] <= rejected_threshold
         and p["paper_id"] not in exclude_ids],
        key=lambda x: x["rating_avg"],  # lowest first
    )

    pools = {}
    if "accepted" in groups:
        pools["accepted"] = acc_pool
        print(f"  Accepted candidates (rating >= {accepted_threshold}): {len(acc_pool)}")
    if "rejected" in groups:
        pools["rejected"] = rej_pool
        print(f"  Rejected candidates (rating <= {rejected_threshold}): {len(rej_pool)}")

    # Venue slug prefix: "iclr23", "neurips22", etc.
    venue_slug = venue.lower().replace(" ", "")
    prefix_map = {
        "accepted": f"{venue_slug}{year % 100}-acc",
        "rejected": f"{venue_slug}{year % 100}-rej",
    }

    new_entries = []
    for group in groups:
        pool = pools.get(group, [])
        dest_dir = out_dir / "papers" / group
        dest_dir.mkdir(parents=True, exist_ok=True)
        prefix = prefix_map[group]

        print(f"\nDownloading {group} papers (target: {n})...")
        picked = 0
        for p in pool:
            if picked >= n:
                break

            slug = slugify(p["title"], prefix)
            pdf_path = dest_dir / f"{slug}.pdf"

            ok = download_pdf(p["paper_id"], pdf_path)
            if not ok:
                print(f"  FAIL  {slug}  (download error)")
                continue

            pages = get_page_count(pdf_path)
            if pages < min_pages:
                print(f"  SKIP  {slug}  ({pages} pages < {min_pages} min)")
                pdf_path.unlink(missing_ok=True)
                continue

            picked += 1
            print(f"  [{picked}/{n}] {slug}  (avg={p['rating_avg']:.1f}, "
                  f"{p['num_reviews']} reviews, {pages} pages)")

            entry = {
                "slug": slug,
                "group": group,
                "forum_id": p["paper_id"],
                "title": p["title"],
                "rating_avg": p["rating_avg"],
            }
            new_entries.append(entry)
            exclude_ids.add(p["paper_id"])

            time.sleep(0.5)

        if picked < n:
            print(f"  Warning: only got {picked}/{n} {group} papers")

    return new_entries


# ---------------------------------------------------------------------------
# Shared utilities
# ---------------------------------------------------------------------------

def download_pdf(forum_id: str, dest: Path) -> bool:
    """Download a PDF from OpenReview. Returns True on success."""
    if dest.exists() and dest.stat().st_size > 10_000:
        return True
    url = f"https://openreview.net/pdf?id={forum_id}"
    result = subprocess.run(
        ["curl", "-sL", "-A", UA, "-o", str(dest), "-w", "%{http_code}", url],
        capture_output=True, text=True,
    )
    code = result.stdout.strip()
    size = dest.stat().st_size if dest.exists() else 0
    return code == "200" and size > 10_000


def get_page_count(pdf_path: Path) -> int:
    """Return page count of a PDF using pymupdf."""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        n = len(doc)
        doc.close()
        return n
    except Exception:
        return 0


def slugify(title: str, prefix: str) -> str:
    """Create a slug from a paper title."""
    import re
    s = title.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")[:60]
    return f"{prefix}-{s}"


def download_from_manifest(manifest: dict, out_dir: Path) -> None:
    """Download PDFs for papers already listed in manifest.json.

    Skips papers whose PDFs already exist on disk.
    """
    papers = manifest["papers"]
    total = len(papers)
    skipped = 0
    downloaded = 0
    failed = 0

    for p in papers:
        dest_dir = out_dir / "papers" / p["group"]
        dest_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = dest_dir / f"{p['slug']}.pdf"

        if pdf_path.exists() and pdf_path.stat().st_size > 10_000:
            skipped += 1
            print(f"  SKIP  {p['slug']}  (already exists)")
            continue

        ok = download_pdf(p["forum_id"], pdf_path)
        if ok:
            downloaded += 1
            size_kb = pdf_path.stat().st_size // 1024
            print(f"  OK    {p['slug']}  ({size_kb}kb)")
        else:
            failed += 1
            print(f"  FAIL  {p['slug']}  (download error)")

        time.sleep(0.5)

    print(f"\nDone: {downloaded} downloaded, {skipped} skipped, {failed} failed "
          f"(out of {total})")


def select_and_download(
    dataset: list[dict],
    n: int,
    year: int,
    min_pages: int,
    rejected_threshold: float,
    out_dir: Path,
    exclude_ids: set[str],
    groups: list[str] | None = None,
) -> list[dict]:
    """Select papers from papercopilot, download PDFs, return manifest entries.

    Args:
        dataset: Full papercopilot dataset.
        n: Target number of papers per group.
        year: ICLR year (for slug prefix).
        min_pages: Minimum page count filter.
        rejected_threshold: Max avg rating for rejected papers.
        out_dir: Base output directory.
        exclude_ids: Forum IDs already in the manifest (skip these).
        groups: Which groups to select for, e.g. ["accepted"], ["rejected"],
                or None for both.
    """
    if groups is None:
        groups = ["accepted", "rejected"]

    # Over-fetch candidates to account for page-count filtering + exclusions.
    extra = max(n * 3, n + 20)
    all_candidates = {}
    if "accepted" in groups:
        all_candidates["accepted"] = select_accepted(dataset, extra)
    if "rejected" in groups:
        all_candidates["rejected"] = select_rejected(dataset, extra,
                                                     threshold=rejected_threshold)

    new_entries = []
    for group in groups:
        candidates = all_candidates.get(group, [])
        dest_dir = out_dir / "papers" / group
        dest_dir.mkdir(parents=True, exist_ok=True)
        prefix = f"iclr{year % 100}-{'acc' if group == 'accepted' else 'rej'}"

        print(f"\nDownloading {group} papers (target: {n})...")
        picked = 0
        for p in candidates:
            if picked >= n:
                break
            if p["id"] in exclude_ids:
                continue

            slug = slugify(p["title"], prefix)
            pdf_path = dest_dir / f"{slug}.pdf"

            ok = download_pdf(p["id"], pdf_path)
            if not ok:
                print(f"  FAIL  {slug}  (download error)")
                continue

            pages = get_page_count(pdf_path)
            if pages < min_pages:
                print(f"  SKIP  {slug}  ({pages} pages < {min_pages} min)")
                pdf_path.unlink(missing_ok=True)
                continue

            picked += 1
            print(f"  [{picked}/{n}] {slug}  ({pages} pages, "
                  f"{pdf_path.stat().st_size // 1024}kb)")

            entry = {
                "slug": slug,
                "group": group,
                "forum_id": p["id"],
                "title": p["title"],
                "pages": pages,
                "rating": p.get("rating", ""),
                "rating_avg": avg_field(p, "rating_avg"),
                "soundness": p.get("soundness", ""),
                "soundness_avg": avg_field(p, "soundness_avg"),
                "confidence": p.get("confidence", ""),
                "confidence_avg": avg_field(p, "confidence_avg"),
                "contribution": p.get("contribution", ""),
                "contribution_avg": avg_field(p, "contribution_avg"),
                "presentation": p.get("presentation", ""),
                "presentation_avg": avg_field(p, "presentation_avg"),
            }
            if group == "accepted":
                entry["award"] = p["status"]  # Oral or Spotlight
            new_entries.append(entry)
            exclude_ids.add(p["id"])

            time.sleep(0.5)

        if picked < n:
            print(f"  Warning: only got {picked}/{n} {group} papers")

    return new_entries


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    # General flags.
    ap.add_argument("-n", "--num", type=int, default=5,
                    help="Number of papers per group (default: 5)")
    ap.add_argument("--add", action="store_true",
                    help="Add N more papers per group to an existing manifest.")
    ap.add_argument("--group", choices=["accepted", "rejected"],
                    help="With --add: only add papers to this group.")
    ap.add_argument("--source", choices=["papercopilot", "hf"], default="papercopilot",
                    help="Data source (default: papercopilot).")
    ap.add_argument("--year", type=int, default=2024,
                    help="Conference year (default: 2024)")
    ap.add_argument("--min-pages", type=int, default=15,
                    help="Minimum page count to keep a paper (default: 15)")
    ap.add_argument("--accepted-threshold", type=float, default=7.0,
                    help="Min avg rating for 'accepted' group (default: 7.0). "
                         "Papercopilot uses Oral/Spotlight status instead.")
    ap.add_argument("--rejected-threshold", type=float, default=4.0,
                    help="Max avg rating for 'rejected' group (default: 4.0)")
    # HF-specific.
    ap.add_argument("--venue", type=str, default="ICLR",
                    help="[hf] Venue name (default: ICLR). "
                         "Options: ICLR, NeurIPS, CoRL, UAI, MIDL.")
    ap.add_argument("--min-reviews", type=int, default=2,
                    help="[hf] Min reviews per paper (default: 2)")
    args = ap.parse_args()

    out_dir = HERE
    manifest_path = out_dir / "manifest.json"
    cache_dir = out_dir / ".cache"

    # Mode 1: manifest exists, no --add → just download what's listed.
    if manifest_path.exists() and not args.add:
        manifest = json.loads(manifest_path.read_text())
        n_papers = len(manifest.get("papers", []))
        print(f"Manifest exists: {manifest_path} ({n_papers} papers)")
        print(f"Downloading missing PDFs...\n")
        download_from_manifest(manifest, out_dir)
        return

    # For --add and bootstrap modes, dispatch by source.
    existing_ids: set[str] = set()
    n_before = 0
    manifest = None

    if manifest_path.exists() and args.add:
        manifest = json.loads(manifest_path.read_text())
        existing_ids = {p["forum_id"] for p in manifest["papers"]}
        n_before = len(manifest["papers"])
        print(f"Manifest exists: {manifest_path} ({n_before} papers)")
        print(f"Adding {args.num} more per group (excluding "
              f"{len(existing_ids)} already selected)...\n")
    else:
        print(f"No manifest found. Bootstrapping from {args.source}...\n")

    groups = [args.group] if args.group else None

    if args.source == "hf":
        papers = fetch_hf_dataset(args.venue, args.year, cache_dir,
                                  min_reviews=args.min_reviews)
        new_entries = select_and_download_hf(
            papers, args.num, args.venue, args.year, args.min_pages,
            args.accepted_threshold, args.rejected_threshold,
            out_dir, existing_ids, groups=groups,
        )
        venue_label = f"{args.venue} {args.year}"
    else:
        dataset = fetch_dataset(args.year, cache_dir)
        print(f"Dataset: {len(dataset)} ICLR {args.year} submissions")
        new_entries = select_and_download(
            dataset, args.num, args.year, args.min_pages,
            args.rejected_threshold, out_dir, existing_ids, groups=groups,
        )
        venue_label = f"ICLR {args.year}"

    # Write / update manifest.
    if manifest is not None:
        # --add mode.
        manifest["papers"].extend(new_entries)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
        print(f"\nManifest updated: {n_before} → {len(manifest['papers'])} papers")
    else:
        # Bootstrap mode.
        manifest = {
            "description": (f"{venue_label} papers for OpenAIReview "
                            f"accepted-vs-rejected comparison study."),
            "venue": venue_label,
            "papers": new_entries,
            "models": [
                "google/gemini-3-flash-preview",
                "z-ai/glm-4.6",
                "qwen/qwen3-235b-a22b-2507",
            ],
            "review_caps": {
                "max_pages": 20,
                "max_tokens": 20_000,
            },
        }
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
        print(f"\nManifest written: {manifest_path}")
        print(f"  {sum(1 for p in new_entries if p['group'] == 'accepted')} accepted, "
              f"{sum(1 for p in new_entries if p['group'] == 'rejected')} rejected")


if __name__ == "__main__":
    main()
