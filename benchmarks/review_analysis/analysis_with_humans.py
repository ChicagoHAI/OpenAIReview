"""Overlap between human reviewers (OpenReview) and the union of 3 AI systems.

Per paper:
  H = set of paragraph_index touched by any human reviewer
  A = set of paragraph_index touched by any of (coarse / openaireview / reviewer3)
Reports per-paper and averaged |H∩A|, |H\\A|, |A\\H|, Jaccard; saves a venn2 PNG.

Human comments are extracted from raw OpenReview review text in two LLM passes:
  1. verbatim atomic-concern extraction (no paraphrasing)
  2. top-5 paragraph retrieval (SentenceTransformer) + LLM picks best paragraph_index

Caches everything under .cache/ in the working directory so re-runs cost nothing.

Capped at ~70 papers (intersection of scaleup ∩ AI runs ∩ openreview-available);
see the printed count at startup.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import matplotlib.pyplot as plt

# Local repo imports
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
from reviewer import client as llm_client  # noqa: E402

from utils import COLOR_BLUE, COLOR_RED, load, para_set, stems, regions_2, draw_venn2, save_fig  # noqa: E402


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DEFAULT_RESULTS_DIR = Path("../conference_study/results")
DEFAULT_MANIFEST    = Path("../conference_study/manifests/v2_frontier/combined.json")
DEFAULT_CACHE_DIR   = Path(".cache")

SYSTEMS = {
    "coarse / DeepSeek":        ("coarse_v2",                  "coarse__deepseek-v4-flash"),
    "OpenAIReview / GPT-5.5":   ("frontier_subset_progressive","progressive__gpt-5.5"),
    "Reviewer 3":               ("reviewer3_v2",               "reviewer3__reviewer3"),
}

# Where to write per-paper human results in the same format as the AI systems.
HUMAN_RESULTS_SUBDIR = "human_v1"
HUMAN_METHOD_KEY     = "human__openreview"
HUMAN_METHOD_LABEL   = "Human (OpenReview)"

# Review-body fields likely to contain concerns/criticisms.
# Bare summaries (`summary`, `summary_of_the_paper`) are excluded.
CRITIQUE_FIELDS = (
    "review",
    "main_review",
    "strengths_and_weaknesses",
    "strength_and_weaknesses",
    "weaknesses",
    "questions",
    "limitations",
    "limitations_and_societal_impact",
    "summary_of_the_review",
)


# ---------------------------------------------------------------------------
# AI side
# ---------------------------------------------------------------------------

def load_ai_union(results_dir: Path, slug: str) -> tuple[set[int], list[dict]]:
    """Return (union of paragraph_index across 3 systems, canonical paragraphs list)."""
    union: set[int] = set()
    paragraphs = None
    for _, (subdir, mk) in SYSTEMS.items():
        p = results_dir / subdir / f"{slug}.json"
        d = load(p)
        union |= para_set(d, mk)
        if paragraphs is None:
            paragraphs = d.get("paragraphs", [])
    return union, (paragraphs or [])


def ai_stems(results_dir: Path) -> set[str]:
    return set.intersection(*(stems(results_dir / subdir) for _, (subdir, _) in SYSTEMS.items()))


# ---------------------------------------------------------------------------
# Manifest → slug↔forum_id
# ---------------------------------------------------------------------------

def load_manifest(manifest_path: Path) -> dict[str, str]:
    """Return {slug: forum_id}."""
    m = json.loads(manifest_path.read_text())
    papers = m["papers"] if isinstance(m, dict) and "papers" in m else m
    return {p["slug"]: p["forum_id"] for p in papers if p.get("slug") and p.get("forum_id")}


# ---------------------------------------------------------------------------
# OpenReview fetcher
# ---------------------------------------------------------------------------

_OPENREVIEW_CLIENT = None

def _or_client():
    global _OPENREVIEW_CLIENT
    if _OPENREVIEW_CLIENT is None:
        import openreview
        _OPENREVIEW_CLIENT = openreview.Client(baseurl="https://api.openreview.net")
    return _OPENREVIEW_CLIENT


def fetch_reviews(forum_id: str, cache_dir: Path) -> list[dict]:
    """Return list of {reviewer_id, text} for Official_Review notes. Cached."""
    cache_file = cache_dir / "openreview_reviews" / f"{forum_id}.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text())

    cache_file.parent.mkdir(parents=True, exist_ok=True)
    client = _or_client()
    notes = client.get_notes(forum=forum_id)
    reviews = []
    for n in notes:
        inv = getattr(n, "invitation", "") or ""
        if "Official_Review" not in inv:
            continue
        # Reviewer id from signatures, e.g. ".../AnonReviewer3"
        sigs = getattr(n, "signatures", []) or []
        reviewer_id = sigs[0].split("/")[-1] if sigs else f"reviewer_{len(reviews)}"
        content = getattr(n, "content", {}) or {}
        parts = []
        for k in CRITIQUE_FIELDS:
            v = content.get(k)
            if isinstance(v, str) and v.strip():
                parts.append(f"## {k}\n{v.strip()}")
        if not parts:
            continue
        reviews.append({
            "reviewer_id": reviewer_id,
            "rating": content.get("rating") or content.get("recommendation"),
            "confidence": content.get("confidence"),
            "text": "\n\n".join(parts),
        })

    cache_file.write_text(json.dumps(reviews, indent=2))
    time.sleep(1.0)  # be polite
    return reviews


# ---------------------------------------------------------------------------
# LLM pass 1: verbatim atomic extraction
# ---------------------------------------------------------------------------

_EXTRACT_PROMPT = """You are given one peer review of a research paper. Split it into atomic concerns — each one a distinct criticism, question, or weakness the reviewer raises.

For each concern, copy the reviewer's own sentence(s) verbatim. DO NOT paraphrase, summarize, or rewrite. If a sentence packs multiple concerns, emit multiple items that each quote the same span. If no quote exists for the concern, skip it. Skip pure praise, generic summary statements, and procedural remarks.

Return a JSON array (and ONLY a JSON array) of objects with exactly these fields:
  - "title": a short (≤10 word) label you write
  - "verbatim": the reviewer's exact words for this concern (one or more contiguous sentences, copied without changes)
  - "comment_type": "technical" if it concerns math/formulas/experiments/methodology, else "logical"

REVIEW:
\"\"\"
{review_text}
\"\"\""""


def _strip_code_fence(s: str) -> str:
    s = s.strip()
    if s.startswith("```"):
        s = re.sub(r"^```(?:json)?\s*", "", s)
        s = re.sub(r"\s*```$", "", s)
    return s.strip()


def llm_extract(review_text: str, model: str) -> tuple[list[dict], dict]:
    """Return (list of {title, verbatim, comment_type}, usage)."""
    messages = [{"role": "user", "content": _EXTRACT_PROMPT.format(review_text=review_text)}]
    raw, usage = llm_client.chat(messages=messages, model=model, temperature=0.0, max_tokens=4096)
    raw = _strip_code_fence(raw)
    try:
        items = json.loads(raw)
    except json.JSONDecodeError:
        # Try to find a JSON array inside
        m = re.search(r"\[.*\]", raw, re.DOTALL)
        if not m:
            print(f"  WARN: extraction returned non-JSON; got {raw[:200]!r}", file=sys.stderr)
            return [], usage
        try:
            items = json.loads(m.group(0))
        except json.JSONDecodeError:
            print(f"  WARN: still not parseable: {raw[:200]!r}", file=sys.stderr)
            return [], usage
    cleaned = []
    for it in items:
        if not isinstance(it, dict):
            continue
        verbatim = (it.get("verbatim") or "").strip()
        if not verbatim:
            continue
        cleaned.append({
            "title": (it.get("title") or "").strip()[:120],
            "verbatim": verbatim,
            "comment_type": it.get("comment_type", "logical"),
        })
    return cleaned, usage


def extract_for_forum(reviews: list[dict], forum_id: str, model: str,
                       cache_dir: Path) -> tuple[list[dict], dict]:
    """Return (list of comments with reviewer_id attached, accumulated usage)."""
    out_dir = cache_dir / "human_comments"
    out_dir.mkdir(parents=True, exist_ok=True)
    all_comments = []
    total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "cost_usd": 0.0}
    for r in reviews:
        rid = r["reviewer_id"]
        cache_file = out_dir / f"{forum_id}__{rid}.json"
        if cache_file.exists():
            entries = json.loads(cache_file.read_text())
        else:
            entries, usage = llm_extract(r["text"], model)
            cache_file.write_text(json.dumps(entries, indent=2))
            for k in ("prompt_tokens", "completion_tokens"):
                total_usage[k] += usage.get(k, 0)
            total_usage["cost_usd"] += usage.get("cost_usd") or 0.0
        for e in entries:
            all_comments.append({**e, "reviewer_id": rid})
    return all_comments, total_usage


# ---------------------------------------------------------------------------
# Embeddings + LLM pass 2 grounding
# ---------------------------------------------------------------------------

_EMBED_MODEL = None

def _embedder():
    global _EMBED_MODEL
    if _EMBED_MODEL is None:
        from sentence_transformers import SentenceTransformer
        _EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _EMBED_MODEL


def paragraph_embeddings(slug: str, paragraphs: list[dict], cache_dir: Path) -> np.ndarray:
    cache_file = cache_dir / "paragraph_embeddings" / f"{slug}.npy"
    if cache_file.exists():
        arr = np.load(cache_file)
        if arr.shape[0] == len(paragraphs):
            return arr
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    texts = [p.get("text", "") for p in paragraphs]
    emb = _embedder().encode(texts, show_progress_bar=False, normalize_embeddings=True)
    np.save(cache_file, emb)
    return emb


_GROUND_PROMPT = """You will be given a concern from a peer reviewer and 5 candidate paragraphs from the paper. Pick the single paragraph that the concern is most directly about.

Output ONLY the integer index of the best paragraph, or the literal word "none" if no candidate is a reasonable match.

REVIEWER CONCERN:
\"\"\"
{concern}
\"\"\"

CANDIDATE PARAGRAPHS:
{candidates}

Your answer (a single integer index from the candidates, or "none"):"""


def llm_ground(concern: str, candidates: list[tuple[int, str]], model: str) -> tuple[int | None, dict]:
    cand_text = "\n\n".join(
        f"[index {idx}]\n{text[:1200]}" for idx, text in candidates
    )
    prompt = _GROUND_PROMPT.format(concern=concern, candidates=cand_text)
    raw, usage = llm_client.chat(
        messages=[{"role": "user", "content": prompt}],
        model=model, temperature=0.0, max_tokens=64,
    )
    s = raw.strip().lower()
    if s.startswith("none") or "none" in s and not re.search(r"\d", s):
        return None, usage
    m = re.search(r"-?\d+", s)
    if not m:
        return None, usage
    chosen = int(m.group(0))
    # Validate it's one of the candidates
    if chosen not in {idx for idx, _ in candidates}:
        return None, usage
    return chosen, usage


def ground_comments(slug: str, comments: list[dict], paragraphs: list[dict],
                    model: str, cache_dir: Path, top_k: int = 5) -> tuple[set[int], int, dict, list[dict]]:
    """Return (set of grounded paragraph_index, ungrounded_count, usage, per-comment grounding info).

    The per-comment list contains the input comment dict augmented with `paragraph_index`
    (int or None). Ordering matches `comments`.
    """
    if not comments or not paragraphs:
        return set(), len(comments), {"prompt_tokens": 0, "completion_tokens": 0, "cost_usd": 0.0}, [
            {**c, "paragraph_index": None} for c in comments
        ]

    cache_file = cache_dir / "grounding" / f"{slug}.json"
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache: dict[str, Any] = json.loads(cache_file.read_text()) if cache_file.exists() else {}

    emb = paragraph_embeddings(slug, paragraphs, cache_dir)
    embedder = _embedder()

    grounded = set()
    ungrounded = 0
    total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "cost_usd": 0.0}
    per_comment: list[dict] = []

    for c in comments:
        key = f"{c['reviewer_id']}::{c['verbatim'][:200]}"
        if key in cache:
            choice = cache[key]
        else:
            q = embedder.encode([c["verbatim"]], normalize_embeddings=True)[0]
            sims = emb @ q
            top_idx = np.argsort(-sims)[:top_k].tolist()
            candidates = [(int(i), paragraphs[i].get("text", "")) for i in top_idx]
            chosen, usage = llm_ground(c["verbatim"], candidates, model)
            for k in ("prompt_tokens", "completion_tokens"):
                total_usage[k] += usage.get(k, 0)
            total_usage["cost_usd"] += usage.get("cost_usd") or 0.0
            choice = chosen
            cache[key] = choice
            cache_file.write_text(json.dumps(cache, indent=2))

        per_comment.append({**c, "paragraph_index": (int(choice) if choice is not None else None)})
        if choice is None:
            ungrounded += 1
        else:
            grounded.add(int(choice))

    return grounded, ungrounded, total_usage, per_comment


# ---------------------------------------------------------------------------
# Save human comments in the same format as AI results
# ---------------------------------------------------------------------------

def save_human_results(results_dir: Path, slug: str, title: str,
                       paragraphs: list[dict], grounded_comments: list[dict],
                       reviews: list[dict]) -> Path:
    """Write a per-paper JSON under results/human_v1/ in the AI-style schema.

    The "quote" field gets the paper paragraph text (mirroring AI semantics where
    quote = passage being critiqued); the "explanation" field gets the reviewer's
    verbatim words. Reviewer attribution lives in the `reviewer_id` extra field.
    """
    out_dir = results_dir / HUMAN_RESULTS_SUBDIR
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{slug}.json"

    comments_out = []
    for i, c in enumerate(grounded_comments):
        if c.get("paragraph_index") is None:
            continue  # only emit grounded comments — they're the ones that count for overlap
        pi = c["paragraph_index"]
        para_text = paragraphs[pi].get("text", "") if 0 <= pi < len(paragraphs) else ""
        comments_out.append({
            "id": f"{HUMAN_METHOD_KEY}_{i}",
            "title": c.get("title", ""),
            "quote": para_text,
            "explanation": c["verbatim"],
            "comment_type": c.get("comment_type", "logical"),
            "paragraph_index": pi,
            "reviewer_id": c.get("reviewer_id", ""),
        })

    # Build the standard top-level shell, with paragraphs reused for visualization.
    doc = {
        "slug": slug,
        "title": title,
        "paragraphs": paragraphs,
        "methods": {
            HUMAN_METHOD_KEY: {
                "label": HUMAN_METHOD_LABEL,
                "model": "openreview-human-reviewers",
                "overall_feedback": "\n\n".join(
                    f"### {r['reviewer_id']} (rating={r.get('rating')}, confidence={r.get('confidence')})\n{r['text']}"
                    for r in reviews
                ),
                "comments": comments_out,
                "cost_usd": 0.0,
                "cost_method": "n/a",
                "prompt_tokens": None,
                "completion_tokens": None,
                "n_reviewers": len(reviews),
                "n_comments_total": len(grounded_comments),
                "n_comments_grounded": len(comments_out),
            }
        },
    }
    out_file.write_text(json.dumps(doc, indent=2))
    return out_file


# ---------------------------------------------------------------------------
# Overlap + plot
# ---------------------------------------------------------------------------

def compute_overlap(papers: list[str], results_dir: Path, slug_to_forum: dict[str, str],
                    model: str, cache_dir: Path, limit: int) -> dict:
    if limit > 0:
        papers = papers[:limit]
    totals = defaultdict(int)
    jaccard_sum = 0.0
    jaccard_n = 0
    skipped_no_reviews = 0
    total_ungrounded = 0
    total_human = 0
    cumulative_cost = 0.0
    per_paper_rows = []

    for slug in papers:
        forum = slug_to_forum.get(slug)
        if not forum:
            print(f"  SKIP {slug}: no forum_id in manifest")
            continue
        try:
            ai_set, paragraphs = load_ai_union(results_dir, slug)
        except FileNotFoundError as e:
            print(f"  SKIP {slug}: missing AI JSON ({e})")
            continue

        try:
            reviews = fetch_reviews(forum, cache_dir)
        except Exception as e:
            print(f"  SKIP {slug}: OpenReview fetch failed: {e}")
            skipped_no_reviews += 1
            continue
        if not reviews:
            print(f"  SKIP {slug}: no Official_Review notes for forum {forum}")
            skipped_no_reviews += 1
            continue

        h_comments, u1 = extract_for_forum(reviews, forum, model, cache_dir)
        h_set, ungrounded, u2, h_grounded = ground_comments(slug, h_comments, paragraphs, model, cache_dir)
        cumulative_cost += (u1.get("cost_usd") or 0.0) + (u2.get("cost_usd") or 0.0)

        # Save in AI-style per-paper JSON so the human side is browsable next to AI results.
        title = ""
        try:
            title = load(results_dir / SYSTEMS["coarse / DeepSeek"][0] / f"{slug}.json").get("title", "")
        except Exception:
            pass
        save_human_results(results_dir, slug, title, paragraphs, h_grounded, reviews)

        r = regions_2(h_set, ai_set)
        totals["h_only"] += r["only_a"]
        totals["a_only"] += r["only_b"]
        totals["both"]   += r["both"]
        total_ungrounded += ungrounded
        total_human += len(h_comments)
        if r["total"]:
            jaccard_sum += r["jaccard"]
            jaccard_n += 1

        per_paper_rows.append({
            "slug": slug, "forum": forum, "n_reviews": len(reviews),
            "h_comments": len(h_comments), "ungrounded": ungrounded,
            "|H|": len(h_set), "|A|": len(ai_set),
            "H_only": r["only_a"], "A_only": r["only_b"], "both": r["both"], "jaccard": r["jaccard"],
        })
        print(f"  {slug[:60]:60s}  H={len(h_set):3d}  A={len(ai_set):3d}  ∩={r['both']:3d}  J={r['jaccard']:.3f}")

    n = len(per_paper_rows)
    avg = {k: v / max(n, 1) for k, v in totals.items()}
    jac_avg = jaccard_sum / max(jaccard_n, 1)
    return {
        "n_papers": n,
        "totals": dict(totals),
        "avg": avg,
        "jaccard_avg": jac_avg,
        "rows": per_paper_rows,
        "skipped_no_reviews": skipped_no_reviews,
        "total_ungrounded": total_ungrounded,
        "total_human_comments": total_human,
        "cumulative_cost_usd": cumulative_cost,
    }


def plot_venn(avg: dict, jaccard_avg: float, n_papers: int, base_name: str) -> None:
    sizes = (round(avg["h_only"], 2), round(avg["a_only"], 2), round(avg["both"], 2))
    fig, ax = plt.subplots(figsize=(7, 6), dpi=300)
    draw_venn2(
        ax, sizes,
        set_labels=("Human", "AI"),
        colors=(COLOR_RED, COLOR_BLUE),
        alpha=0.15, region_fontsize=32, set_fontsize=30,
    )
    plt.tight_layout()
    paths = save_fig(base_name, dpi=300)
    print(f"\nWrote {', '.join(str(p) for p in paths)}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS_DIR)
    ap.add_argument("--manifest",    type=Path, default=DEFAULT_MANIFEST)
    ap.add_argument("--cache-dir",   type=Path, default=DEFAULT_CACHE_DIR)
    ap.add_argument("--model",       type=str,  default="google/gemini-3-flash-preview")
    ap.add_argument("--limit",       type=int,  default=0, help="0 = all")
    ap.add_argument("--out",         type=str,  default="venn_human_vs_ai",
                    help="Base name (no extension) for the venn figure under plots/")
    ap.add_argument("--rows-out",    type=Path, default=Path("per_paper_human_vs_ai.json"))
    args = ap.parse_args()

    slug_to_forum = load_manifest(args.manifest)
    ai_intersection = ai_stems(args.results_dir)
    candidates = sorted(set(slug_to_forum) & ai_intersection)
    print(f"Manifest papers: {len(slug_to_forum)}")
    print(f"AI 3-way intersection: {len(ai_intersection)}")
    print(f"Candidates (manifest ∩ AI): {len(candidates)}")
    if args.limit > 0:
        print(f"--limit {args.limit} → using first {min(args.limit, len(candidates))} candidates")
    print(f"Note: scaleup has ~209 PDFs but the bottleneck is frontier_subset_progressive (74).\n")

    summary = compute_overlap(candidates, args.results_dir, slug_to_forum,
                              args.model, args.cache_dir, args.limit)

    n = summary["n_papers"]
    a = summary["avg"]
    print(f"\n{'='*60}")
    print(f"Papers analyzed:           {n}")
    print(f"Skipped (no reviews):      {summary['skipped_no_reviews']}")
    print(f"Total human comments:      {summary['total_human_comments']}")
    print(f"  ungrounded (dropped):    {summary['total_ungrounded']} "
          f"({summary['total_ungrounded']/max(summary['total_human_comments'],1):.1%})")
    print(f"LLM cost this run:         ${summary['cumulative_cost_usd']:.4f}")
    print()
    print(f"{'Region':<32} {'Avg/paper':>10}")
    print("-" * 44)
    print(f"{'Human only (H \\ A)':<32} {a['h_only']:>10.2f}")
    print(f"{'AI only    (A \\ H)':<32} {a['a_only']:>10.2f}")
    print(f"{'Both       (H ∩ A)':<32} {a['both']:>10.2f}")
    print(f"{'Jaccard (avg)':<32} {summary['jaccard_avg']:>10.3f}")

    args.rows_out.write_text(json.dumps(summary, indent=2))
    print(f"\nPer-paper rows → {args.rows_out}")

    plot_venn(a, summary["jaccard_avg"], n, args.out)


if __name__ == "__main__":
    main()
