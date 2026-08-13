#!/usr/bin/env python3
"""Pull down completed Reviewer 3 sessions whose local poll loop gave up.

Reviewer 3 is async: a session keeps processing on their server even after
our adapter has timed out / been killed. The adapter persists the sessionId
to a `.sid` file next to each cell's output JSON; this script walks those
`.sid` files, fetches each session, and writes results to disk for the ones
that completed in the meantime.

Walks both result trees:
  * Perturbation:  <results>/full_<domain>_reviewer3/.../review/*.sid
  * Conference:    <conference_study>/results/reviewer3_v2/.sids/*.sid

Skips cells whose `out_json` already has comments. Safe to re-run.

Usage:
  python rescue_sessions.py                  # rescue both, write results
  python rescue_sessions.py --dry-run        # just report what's recoverable
  python rescue_sessions.py --kind perturbation
  python rescue_sessions.py --kind conference

Required env: REVIEWER3_API_KEY (used for the `review:read` GET).

Exit code: 0 always (no errors are fatal — script is meant to be safe to
re-run; failures are just logged).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import requests  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from systems.reviewer3_adapter import build_pipeline_json  # noqa: E402

# Repo root + conference_study root
REPO = HERE.parent.parent
CONFERENCE = REPO / "benchmarks" / "conference_study"
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(CONFERENCE))


REVIEWER3_BASE_URL = os.environ.get("REVIEWER3_BASE_URL", "https://reviewer3.com").rstrip("/")


@dataclass
class Orphan:
    """A `.sid` file pointing at a session we never wrote out_json for."""
    kind: str               # "pert" or "conf"
    sid_file: Path
    out_json: Path          # where we'd write the result if status == completed
    extra: dict             # kind-specific (e.g. conference slug)


def _has_content(out_json: Path, method_key: str | None = None) -> bool:
    """`out_json` exists AND already has a comment-bearing method entry."""
    if not out_json.exists():
        return False
    try:
        d = json.loads(out_json.read_text())
    except Exception:
        return False
    methods = d.get("methods") or {}
    if method_key is not None:
        m = methods.get(method_key)
        return bool(m and m.get("comments"))
    return bool(methods) and any(m.get("comments") for m in methods.values())


def find_orphans(kind: str = "both") -> list[Orphan]:
    """Walk .sid files; return ones whose result JSON is missing or empty."""
    out: list[Orphan] = []

    if kind in ("both", "perturbation"):
        # Result paths are resolved via Config.results_dir, which the runner
        # resolves to absolute via REPO/<results_dir>. The most robust thing
        # is to walk every `.sid` under any `full_*_reviewer3` results dir
        # that the runner might write to. We check both the local results
        # tree (under this worktree) and any sibling worktrees the user may
        # have symlinked in.
        pert_roots = [REPO / "benchmarks" / "perturbation" / "results"]
        # Follow the symlink target too in case results/ is a symlink (we use
        # this pattern when running from a different worktree than the data).
        resolved = (REPO / "benchmarks" / "perturbation" / "results").resolve()
        if resolved not in pert_roots:
            pert_roots.append(resolved)
        seen = set()
        for root in pert_roots:
            if not root.exists():
                continue
            for sid_file in root.rglob("*.sid"):
                if sid_file in seen:
                    continue
                seen.add(sid_file)
                out_json = sid_file.with_suffix(".json")
                if _has_content(out_json):
                    continue
                out.append(Orphan(kind="pert", sid_file=sid_file,
                                  out_json=out_json, extra={}))

    if kind in ("both", "conference"):
        conf_root = CONFERENCE / "results" / "reviewer3_v2"
        sids_dir = conf_root / ".sids"
        if sids_dir.exists():
            for sid_file in sids_dir.glob("*.sid"):
                # filename: <slug>.<method_key>.sid
                stem_parts = sid_file.stem.split(".")
                slug = stem_parts[0]
                method_key = ".".join(stem_parts[1:]) or "reviewer3__reviewer3"
                out_json = conf_root / f"{slug}.json"
                if _has_content(out_json, method_key=method_key):
                    continue
                out.append(Orphan(kind="conf", sid_file=sid_file,
                                  out_json=out_json,
                                  extra={"slug": slug, "method_key": method_key}))

    return out


def fetch_session(sid: str, *, headers: dict, timeout: float = 30.0) -> dict | None:
    """Return the full session body if status==completed, else None."""
    url = f"{REVIEWER3_BASE_URL}/api/internal/review/{sid}"
    try:
        r = requests.get(url, headers=headers, timeout=timeout)
    except Exception as e:
        print(f"  fetch error for {sid}: {type(e).__name__}: {e}",
              file=sys.stderr, flush=True)
        return None
    if r.status_code != 200:
        print(f"  {sid}: HTTP {r.status_code}", file=sys.stderr, flush=True)
        return None
    body = r.json()
    if body.get("status") != "completed":
        return None
    return body


def write_perturbation(orphan: Orphan, body: dict) -> None:
    """Write pipeline JSON + raw.json next to the .sid."""
    raw_path = orphan.sid_file.with_suffix(".raw.json")
    raw_path.write_text(json.dumps(body, indent=2, ensure_ascii=False))
    # Synthesize a paper path from the sid_file stem (e.g. paper_001_corrupted.md)
    pj = build_pipeline_json(Path(orphan.sid_file.stem + ".md"),
                             body, elapsed_s=0.0)
    orphan.out_json.write_text(json.dumps(pj, indent=2, ensure_ascii=False))


def write_conference(orphan: Orphan, body: dict, *, _cache: dict = {}) -> None:
    """Build the merged paper JSON for the conference cohort."""
    # Lazy imports to keep --kind perturbation fast (avoids parse_document deps).
    if "loaded" not in _cache:
        from competitors import get_adapter  # noqa: F401
        from competitors.helpers import build_method_data, merge_into_paper_json
        from competitors.base import NormalizedComment, NormalizedReview
        from reviewer.parsers import parse_document
        from reviewer.utils import split_into_paragraphs
        import systems.reviewer3_adapter as r3a
        manifest = json.loads((CONFERENCE / "manifests/v2/combined.json").read_text())
        _cache.update(
            build_method_data=build_method_data,
            merge_into_paper_json=merge_into_paper_json,
            NormalizedComment=NormalizedComment,
            NormalizedReview=NormalizedReview,
            parse_document=parse_document,
            split_into_paragraphs=split_into_paragraphs,
            r3a=r3a,
            slug2paper={p["slug"]: p for p in manifest["papers"]},
            loaded=True,
        )
    slug = orphan.extra["slug"]
    method_key = orphan.extra["method_key"]
    paper = _cache["slug2paper"].get(slug)
    if not paper:
        print(f"  {slug}: no manifest entry, skipping", file=sys.stderr)
        return
    pdf = CONFERENCE / paper["pdf_path"]
    title, content, _ = _cache["parse_document"](pdf, max_pages=20)
    paragraphs = _cache["split_into_paragraphs"](content)
    comments = []
    for i, c in enumerate(body.get("comments") or []):
        if not isinstance(c, dict):
            c = {"comment": str(c)}
        n = _cache["r3a"]._normalize_comment(c, i)
        comments.append(_cache["NormalizedComment"](
            title=n.get("title", ""), quote=n.get("quote", ""),
            explanation=n.get("explanation", ""),
            comment_type=n.get("comment_type", "technical"),
            extra={"severity": n.get("severity"),
                   "reviewerId": c.get("reviewerId"),
                   "rank": c.get("rank"),
                   "session_id": (body.get("session") or {}).get("id")},
        ))
    review = _cache["NormalizedReview"](
        comments=comments, overall_feedback="", cost_usd=None,
        cost_method="estimated", model="reviewer3",
    )
    md = _cache["build_method_data"](
        review=review, method_key=method_key,
        method_label="Reviewer3 (reviewer3)", paragraphs=paragraphs,
    )
    _cache["merge_into_paper_json"](
        out_file=orphan.out_json, slug=slug,
        title=paper.get("title") or title, paragraphs=paragraphs,
        method_key=method_key, method_data=md,
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--kind", choices=["both", "perturbation", "conference"],
                    default="both")
    ap.add_argument("--dry-run", action="store_true",
                    help="Just report what's recoverable; don't write anything.")
    ap.add_argument("--parallel", type=int, default=10,
                    help="Concurrent API fetches (default 10).")
    args = ap.parse_args()

    api_key = os.environ.get("REVIEWER3_API_KEY")
    if not api_key:
        print("REVIEWER3_API_KEY not set (check .env)", file=sys.stderr)
        return 1
    headers = {"x-api-key": api_key}

    orphans = find_orphans(args.kind)
    print(f"found {len(orphans)} orphan .sid file(s) "
          f"(no result on disk for these cells yet)")
    if not orphans:
        return 0

    # Fetch every sid in parallel; bucket by status.
    def _fetch(orphan: Orphan):
        sid = orphan.sid_file.read_text().strip()
        if not sid:
            return orphan, sid, None
        return orphan, sid, fetch_session(sid, headers=headers)

    completed: list[tuple[Orphan, str, dict]] = []
    incomplete = 0
    with ThreadPoolExecutor(max_workers=args.parallel) as pool:
        for orphan, sid, body in pool.map(_fetch, orphans):
            if body is None:
                incomplete += 1
                continue
            completed.append((orphan, sid, body))

    print(f"  {len(completed)} completed on R3 (recoverable)")
    print(f"  {incomplete} still in-progress / failed / unreachable")

    if args.dry_run or not completed:
        for orphan, sid, _ in completed:
            print(f"  would write: {orphan.out_json}  (sid={sid})")
        return 0

    n_pert = n_conf = 0
    for orphan, sid, body in completed:
        try:
            if orphan.kind == "pert":
                write_perturbation(orphan, body)
                n_pert += 1
            else:
                write_conference(orphan, body)
                n_conf += 1
        except Exception as e:
            print(f"  write failed for {sid} ({orphan.out_json}): "
                  f"{type(e).__name__}: {e}", file=sys.stderr)

    print(f"\nrescued: perturbation={n_pert}  conference={n_conf}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
