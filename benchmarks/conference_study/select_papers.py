#!/usr/bin/env python
"""Select papers for the 4-pair signal matrix from SNOR v1.

Writes per-pair manifests to manifests/pair_{1,2,3,4}.json plus a
combined manifest (manifests/combined.json) with deduped papers and
pair-membership metadata — that combined manifest is what the downloader
and runner consume.

Pairs:
    1  top-cited (high)         vs  never-published (low)     community-wide
    2  award (high)             vs  rejected (low)            conference-level
    3  top scores (high)        vs  bottom scores (low)       reviewer-level
    4  award & top-cited & top-scored (high)
       vs  rejected & never-published & bottom-scored (low)   composed

Definitions:
    * top-cited: highest citations-per-year within the cohort (deterministic).
    * never-published: rejected AND publication_venue empty / only arXiv-like,
      AND at least 2 years elapsed since conference_year. Random sample.
    * top / bottom scores: highest / lowest review_score_avg in the cohort.
    * awards: raw_decision contains Outstanding / Best / Oral / Spotlight.
      Random sample (was: highest-cited awarded paper).
    * rejected: not accepted, has substantive reviews. Random sample.
    * composed high: awarded papers ranked by sum of citation-rank and
      score-rank within the awarded pool (best on both axes).
    * composed low: rejected & never-published, sorted by lowest score.

Random samples use a fixed seed (RANDOM_SEED) for reproducibility; ties
in deterministic tails are broken by forum_id.
"""
from __future__ import annotations

import argparse
import json
import random
import re
from collections import defaultdict
from pathlib import Path

from snor_loader import load_cohort

HERE = Path(__file__).resolve().parent
MANIFESTS_DIR = HERE / "manifests" / "v1"

CURRENT_YEAR = 2026

AWARD_KEYWORDS = ("outstanding", "best paper", "best", "oral", "spotlight")
# raw_decision tokens for award detection are case-insensitive substring.

DEFAULT_VENUES = ("iclr", "neurips")
DEFAULT_YEARS = (2021, 2022)
N_PER_TAIL = 30
MIN_REVIEWS = 3
MIN_YEARS_FOR_NEVER_PUBLISHED = 2
RANDOM_SEED = 42


def slugify(title: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s[:60] or "untitled"


def short_forum_id(forum_id: str) -> str:
    return forum_id[:8]


def cites_per_year(r: dict) -> float:
    cc = r.get("citation_count") or 0
    try:
        y = int(r.get("conference_year") or CURRENT_YEAR)
    except (TypeError, ValueError):
        y = CURRENT_YEAR
    years = max(1, CURRENT_YEAR - y)
    return cc / years


def is_preprint_venue(v: str | None) -> bool:
    """Empty venue or arXiv-only counts as 'not formally published'."""
    if not v:
        return True
    return "arxiv" in v.lower()


def is_awarded(r: dict) -> bool:
    raw = (r.get("raw_decision") or "").lower()
    # "Reject" sometimes contains substrings like "best of reject" — be careful.
    # Use the normalized_decision field as the cleaner signal, falling back
    # to raw only when normalized is missing.
    norm = (r.get("normalized_decision") or "").lower()
    if norm in {"reject", "poster"}:
        return False
    return any(k in raw or k in norm for k in AWARD_KEYWORDS)


def is_rejected(r: dict) -> bool:
    if r.get("accepted"):
        return False
    # Require substantive reviews to avoid withdrawn-before-review papers.
    scores = r.get("review_scores") or []
    return len(scores) >= MIN_REVIEWS


def is_never_published(r: dict) -> bool:
    if r.get("accepted"):
        return False
    # Must be ≥2 years since conference_year.
    try:
        y = int(r.get("conference_year") or CURRENT_YEAR)
    except (TypeError, ValueError):
        return False
    if CURRENT_YEAR - y < MIN_YEARS_FOR_NEVER_PUBLISHED:
        return False
    return is_preprint_venue(r.get("publication_venue"))


def has_reviews(r: dict) -> bool:
    scores = r.get("review_scores") or []
    return len(scores) >= MIN_REVIEWS and r.get("review_score_avg") is not None


def dedup_key(r: dict) -> str:
    """Key for deduplicating papers that were submitted to multiple
    venues/years. Prefers the S2 id (same across OpenReview resubmissions
    of the same work), falls back to normalized title."""
    s2 = r.get("semantic_scholar_id")
    if s2:
        return f"s2:{s2}"
    t = (r.get("title") or "").strip().lower()
    return f"title:{re.sub(r'[^a-z0-9]+', ' ', t).strip()}"


def top_n_dedup(pool: list[dict], n: int, key) -> list[dict]:
    """Sort `pool` by `key`, take first-occurrence of each dedup_key,
    return up to n entries."""
    pool = sorted(pool, key=key)
    seen: set[str] = set()
    out: list[dict] = []
    for r in pool:
        k = dedup_key(r)
        if k in seen:
            continue
        seen.add(k)
        out.append(r)
        if len(out) >= n:
            break
    return out


def random_sample_dedup(pool: list[dict], n: int,
                        seed: int = RANDOM_SEED) -> list[dict]:
    """Random sample of `pool` with dedup_key collapse, deterministic via seed."""
    pool = sorted(pool, key=lambda r: r.get("id", ""))
    rng = random.Random(seed)
    shuffled = pool[:]
    rng.shuffle(shuffled)
    seen: set[str] = set()
    out: list[dict] = []
    for r in shuffled:
        k = dedup_key(r)
        if k in seen:
            continue
        seen.add(k)
        out.append(r)
        if len(out) >= n:
            break
    return out


# ---------------------------------------------------------------------------
# Per-pair selectors
# ---------------------------------------------------------------------------

def select_top_cited(cohort: list[dict], n: int) -> list[dict]:
    """Highest citations-per-year across the cohort."""
    return top_n_dedup(
        cohort, n,
        key=lambda r: (-cites_per_year(r), r.get("id", "")),
    )


def select_never_published(cohort: list[dict], n: int) -> list[dict]:
    """Rejected + no publication venue, with at least MIN_REVIEWS reviews.

    Random sample within the pool (was: lowest score). Random sampling
    avoids systematic overlap with the bottom-scores tail (pair 3 low).
    """
    pool = [r for r in cohort if is_never_published(r) and has_reviews(r)]
    return random_sample_dedup(pool, n)


def select_award(cohort: list[dict], n: int) -> list[dict]:
    """Random sample of awarded papers (was: highest-cited award).

    Random sampling avoids systematic overlap with the top-cited tail
    (pair 1 high) and the top-scores tail (pair 3 high).
    """
    pool = [r for r in cohort if is_awarded(r)]
    return random_sample_dedup(pool, n)


def select_rejected(cohort: list[dict], n: int) -> list[dict]:
    """Random sample of rejected papers with reviews (was: lowest score).

    Random sampling avoids systematic overlap with the bottom-scores
    tail (pair 3 low) and the never-published tail (pair 1 low).
    """
    pool = [r for r in cohort if is_rejected(r) and has_reviews(r)]
    return random_sample_dedup(pool, n)


def select_top_scores(cohort: list[dict], n: int) -> list[dict]:
    """Top-scoring papers across venue-year cohorts."""
    pool = [r for r in cohort if has_reviews(r)]
    return top_n_dedup(
        pool, n,
        key=lambda r: (-(r.get("review_score_avg") or 0), r.get("id", "")),
    )


def select_bottom_scores(cohort: list[dict], n: int) -> list[dict]:
    pool = [r for r in cohort if has_reviews(r)]
    return top_n_dedup(
        pool, n,
        key=lambda r: (r.get("review_score_avg") or 99, r.get("id", "")),
    )


def select_composed_high(cohort: list[dict], n: int) -> list[dict]:
    """Awarded papers ranked by both citations and review scores.

    Computes citation-rank and score-rank within the awarded pool with
    reviews, then sorts by sum of ranks (lower = better on both axes).
    Papers missing one signal fall to the back.
    """
    pool = [r for r in cohort if is_awarded(r) and has_reviews(r)]
    if not pool:
        return []
    by_cites = sorted(pool, key=lambda r: -cites_per_year(r))
    cite_rank = {r["id"]: i for i, r in enumerate(by_cites)}
    by_score = sorted(pool, key=lambda r: -(r.get("review_score_avg") or 0))
    score_rank = {r["id"]: i for i, r in enumerate(by_score)}
    return top_n_dedup(
        pool, n,
        key=lambda r: (cite_rank[r["id"]] + score_rank[r["id"]],
                       r.get("id", "")),
    )


def select_composed_low(cohort: list[dict], n: int) -> list[dict]:
    """Rejected & bottom-5% & never-published: rank by lowest review score."""
    pool = [
        r for r in cohort
        if is_rejected(r) and is_never_published(r) and has_reviews(r)
    ]
    return top_n_dedup(
        pool, n,
        key=lambda r: (r.get("review_score_avg") or 99, r.get("id", "")),
    )


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

PAIRS = [
    {
        "id": 1,
        "label": "community",
        "high": ("cited", select_top_cited),
        "low": ("nopub", select_never_published),
    },
    {
        "id": 2,
        "label": "conference",
        "high": ("award", select_award),
        "low": ("rej", select_rejected),
    },
    {
        "id": 3,
        "label": "reviewer",
        "high": ("top5", select_top_scores),
        "low": ("bot5", select_bottom_scores),
    },
    {
        "id": 4,
        "label": "composed",
        "high": ("comp-hi", select_composed_high),
        "low": ("comp-lo", select_composed_low),
    },
]


def entry_from_record(r: dict) -> dict:
    """Project a SNOR record into a manifest-safe entry (no embeddings)."""
    return {
        "forum_id": r["id"],
        "title": r["title"],
        "conf_id": r.get("conf_id"),
        "venue": r.get("conference_name"),
        "year": r.get("conference_year"),
        "accepted": r.get("accepted"),
        "raw_decision": r.get("raw_decision"),
        "normalized_decision": r.get("normalized_decision"),
        "publication_venue": r.get("publication_venue"),
        "citation_count": r.get("citation_count") or 0,
        "cites_per_year": round(cites_per_year(r), 3),
        "review_score_avg": r.get("review_score_avg"),
        "review_confidence_avg": r.get("review_confidence_avg"),
        "num_reviews": len(r.get("review_scores") or []),
        "authors": r.get("authors") or [],
        "semantic_scholar_id": r.get("semantic_scholar_id"),
    }


def make_slug(r: dict) -> str:
    conf = r.get("conf_id") or "unk"
    return f"{conf}-{short_forum_id(r['id'])}-{slugify(r['title'])}"


def collapse_resubmissions(cohort: list[dict]) -> list[dict]:
    """Collapse SNOR records that share a semantic_scholar_id.

    A paper submitted to multiple venues/years (e.g. rejected at ICLR 2021
    then accepted at ICLR 2022 Spotlight) has one row per submission but
    all rows point at the same S2 record. Treating them as separate
    papers would let the same paper appear in both the awarded tail and
    the rejected tail and be reviewed twice with opposite labels.

    Rule: for each s2_id, keep the record from the latest conference_year.
    Ties within a year fall back to the most-positive decision (awarded
    > posters > rejected) so the paper's final status dominates.
    """
    by_s2: dict[str, dict] = {}
    rank = {"Oral": 4, "Spotlight": 3, "Accepted": 2, "Poster": 2,
            "Reject": 0, "Withdrawn": -1}

    def sort_key(r: dict) -> tuple:
        try:
            y = int(r.get("conference_year") or 0)
        except (TypeError, ValueError):
            y = 0
        d_rank = rank.get(r.get("normalized_decision"), 0)
        return (y, d_rank)

    for r in cohort:
        s2 = r.get("semantic_scholar_id")
        if not s2:
            # No s2_id: key by normalized title so at least same-title
            # resubmissions collapse.
            t = re.sub(r'[^a-z0-9]+', ' ', (r.get("title") or "").lower()).strip()
            s2 = f"title:{t}"
        if s2 not in by_s2 or sort_key(r) > sort_key(by_s2[s2]):
            by_s2[s2] = r
    collapsed = list(by_s2.values())
    print(f"Collapsed cohort: {len(cohort)} -> {len(collapsed)} "
          f"(removed {len(cohort) - len(collapsed)} resubmission rows)")
    return collapsed


def build_manifests(
    venues: list[str],
    years: list[int],
    n_per_tail: int,
    out_dir: Path,
) -> None:
    cohort = load_cohort(venues=venues, years=years)
    cohort = collapse_resubmissions(cohort)

    # Per-pair files + accumulating index of pair memberships.
    memberships: dict[str, list[dict]] = defaultdict(list)  # forum_id -> [{pair,tail},...]
    records_by_forum: dict[str, dict] = {}

    out_dir.mkdir(parents=True, exist_ok=True)

    for pair in PAIRS:
        pid = pair["id"]
        label = pair["label"]
        hi_code, hi_fn = pair["high"]
        lo_code, lo_fn = pair["low"]
        hi = hi_fn(cohort, n_per_tail)
        lo = lo_fn(cohort, n_per_tail)
        print(f"\nPair {pid} ({label}): high={hi_code} n={len(hi)}  "
              f"low={lo_code} n={len(lo)}")

        pair_manifest = {
            "pair_id": pid,
            "label": label,
            "high_tail": hi_code,
            "low_tail": lo_code,
            "venues": venues,
            "years": years,
            "high": [entry_from_record(r) for r in hi],
            "low": [entry_from_record(r) for r in lo],
        }
        (out_dir / f"pair_{pid}.json").write_text(
            json.dumps(pair_manifest, indent=2) + "\n"
        )

        # Update combined index.
        for r in hi:
            records_by_forum[r["id"]] = r
            memberships[r["id"]].append({"pair": pid, "tail": hi_code, "side": "high"})
        for r in lo:
            records_by_forum[r["id"]] = r
            memberships[r["id"]].append({"pair": pid, "tail": lo_code, "side": "low"})

    # Combined manifest — one entry per unique forum_id.
    combined_papers = []
    for fid, r in records_by_forum.items():
        entry = entry_from_record(r)
        entry["slug"] = make_slug(r)
        entry["pair_memberships"] = memberships[fid]
        combined_papers.append(entry)

    combined = {
        "description": (
            f"Scale-up 4-pair signal matrix across venues={venues} "
            f"years={years}, n={n_per_tail}/tail. Built from SNOR v1."
        ),
        "venues": venues,
        "years": years,
        "n_per_tail": n_per_tail,
        "papers": combined_papers,
        "models": [
            "google/gemini-3-flash-preview",
            "z-ai/glm-4.6",
            "qwen/qwen3-235b-a22b-2507",
        ],
        "review_caps": {"max_pages": 20, "max_tokens": 20_000},
    }
    (out_dir / "combined.json").write_text(
        json.dumps(combined, indent=2) + "\n"
    )
    print(f"\nCombined manifest: {len(combined_papers)} unique papers "
          f"-> {out_dir / 'combined.json'}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--venues", nargs="+", default=list(DEFAULT_VENUES))
    ap.add_argument("--years", nargs="+", type=int, default=list(DEFAULT_YEARS))
    ap.add_argument("-n", "--n-per-tail", type=int, default=N_PER_TAIL)
    ap.add_argument("--out-dir", type=Path, default=MANIFESTS_DIR)
    args = ap.parse_args()

    build_manifests(args.venues, args.years, args.n_per_tail, args.out_dir)


if __name__ == "__main__":
    main()
