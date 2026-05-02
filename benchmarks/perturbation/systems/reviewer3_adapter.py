"""Adapter that runs Reviewer 3 (closed-source HTTP API) on the perturbation benchmark.

Submits each staged corrupted paper to `POST /api/internal/review`, polls
`GET /api/internal/review/{sessionId}` until the review is ready, then writes
a JSON file in the schema `openaireview score` consumes.

Environment:
  REVIEWER3_API_KEY   API key (sk_...). Sent as `x-api-key` header.
  REVIEWER3_USER_ID   User account ID required by the submit endpoint.
  REVIEWER3_BASE_URL  Optional override (default: https://reviewer3.com).

Notes on the upstream API (OpenAPI v0):
  * The documented surface lives under `/api/internal/*`. Confirm with the
    vendor that this is the right surface for external partners — naming
    suggests staff tooling.
  * Submit is async: returns `sessionId`. Reviews are fetched via the GET
    endpoint with a `status` enum and `comments: array`. The shape of an
    individual comment is not specified in the spec; this adapter does
    defensive field mapping and dumps the raw API response next to the
    converted pipeline JSON so the mapping can be tightened after a real run.
"""

from __future__ import annotations

import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError as e:
    raise ImportError(
        "reviewer3_adapter requires `requests`. Install via: pip install requests"
    ) from e


REVIEWER3_SLUG = "reviewer3"

DEFAULT_BASE_URL = "https://reviewer3.com"
DEFAULT_POLL_INTERVAL_S = 5.0
DEFAULT_POLL_TIMEOUT_S = 20 * 60  # 20 minutes per paper
DEFAULT_REQUEST_TIMEOUT_S = 60.0

_TERMINAL_OK = {"complete", "completed", "done", "ready", "success", "succeeded", "finished"}
_TERMINAL_FAIL = {"failed", "error", "errored", "rejected", "cancelled", "canceled"}


def model_slug(_model: str | None = None) -> str:
    """Reviewer 3 does not expose a model selector; slug is fixed."""
    return REVIEWER3_SLUG


# ---------------------------------------------------------------------------
# Config / env
# ---------------------------------------------------------------------------

@dataclass
class Reviewer3Config:
    api_key: str
    user_id: str
    base_url: str = DEFAULT_BASE_URL
    review_mode: str = "author"  # author|journal per OpenAPI enum
    poll_interval_s: float = DEFAULT_POLL_INTERVAL_S
    poll_timeout_s: float = DEFAULT_POLL_TIMEOUT_S
    request_timeout_s: float = DEFAULT_REQUEST_TIMEOUT_S


def config_from_env() -> Reviewer3Config:
    api_key = os.environ.get("REVIEWER3_API_KEY")
    user_id = os.environ.get("REVIEWER3_USER_ID")
    missing = [n for n, v in [("REVIEWER3_API_KEY", api_key),
                              ("REVIEWER3_USER_ID", user_id)] if not v]
    if missing:
        raise RuntimeError(
            f"Reviewer 3 adapter needs {', '.join(missing)} in the environment. "
            "Add them to your .env file (REVIEWER3_API_KEY=sk_..., REVIEWER3_USER_ID=...)."
        )
    base_url = os.environ.get("REVIEWER3_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    return Reviewer3Config(api_key=api_key, user_id=user_id, base_url=base_url)


# ---------------------------------------------------------------------------
# Job types
# ---------------------------------------------------------------------------

@dataclass
class Reviewer3Job:
    paper: Path           # path to *_corrupted.md
    out_json: Path        # where to write the pipeline-shaped JSON
    paper_label: str      # e.g. "<error_type>/<paper_label>"
    title: str | None = None


@dataclass
class Reviewer3Result:
    job: Reviewer3Job
    ok: bool
    elapsed_s: float
    session_id: str = ""
    error: str = ""
    raw_response: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# HTTP wrappers
# ---------------------------------------------------------------------------

def _headers(cfg: Reviewer3Config) -> dict[str, str]:
    return {"x-api-key": cfg.api_key}


def _submit(cfg: Reviewer3Config, paper: Path, *, title: str | None) -> str:
    """POST /api/internal/review (multipart). Returns sessionId."""
    url = f"{cfg.base_url}/api/internal/review"
    data: dict[str, str] = {
        "userId": cfg.user_id,
        "reviewMode": cfg.review_mode,
        "filename": paper.name,
    }
    if title:
        data["title"] = title
    with paper.open("rb") as fh:
        files = {"file": (paper.name, fh, "text/markdown")}
        resp = requests.post(url, headers=_headers(cfg), data=data, files=files,
                             timeout=cfg.request_timeout_s)
    if resp.status_code >= 400:
        raise RuntimeError(f"submit failed (HTTP {resp.status_code}): {resp.text[:500]}")
    body = resp.json()
    sid = body.get("sessionId") or body.get("session_id")
    if not sid:
        raise RuntimeError(f"submit response missing sessionId: {body}")
    return sid


def _fetch(cfg: Reviewer3Config, session_id: str) -> dict:
    url = f"{cfg.base_url}/api/internal/review/{session_id}"
    resp = requests.get(url, headers=_headers(cfg), timeout=cfg.request_timeout_s)
    if resp.status_code >= 400:
        raise RuntimeError(f"fetch failed (HTTP {resp.status_code}): {resp.text[:500]}")
    return resp.json()


def _poll_until_done(cfg: Reviewer3Config, session_id: str, *, tag: str) -> dict:
    """Poll GET /review/{sessionId} until status is terminal or we time out."""
    deadline = time.time() + cfg.poll_timeout_s
    last_status = None
    while True:
        body = _fetch(cfg, session_id)
        status = str(body.get("status", "")).lower()
        if status != last_status:
            print(f"[{tag}] status={status or '<none>'}", file=sys.stderr, flush=True)
            last_status = status
        if status in _TERMINAL_OK:
            return body
        if status in _TERMINAL_FAIL:
            raise RuntimeError(f"review {session_id} ended with status={status}: {body}")
        if time.time() >= deadline:
            raise TimeoutError(
                f"review {session_id} not complete after {cfg.poll_timeout_s:.0f}s "
                f"(last status={status!r})"
            )
        time.sleep(cfg.poll_interval_s)


# ---------------------------------------------------------------------------
# Response → pipeline JSON
# ---------------------------------------------------------------------------

def _pick(d: dict, *keys: str, default: str = "") -> str:
    """Return the first non-empty string value from d for any of `keys`."""
    for k in keys:
        v = d.get(k)
        if isinstance(v, str) and v.strip():
            return v
    return default


def _normalize_comment(raw: dict, idx: int) -> dict:
    """Best-effort mapping from Reviewer 3 comment shape to pipeline schema.

    The OpenAPI spec doesn't pin field names. We try common synonyms; anything
    we don't recognize is preserved on the side as `_raw` for later inspection.
    """
    cid = _pick(raw, "id", "commentId", "uuid") or f"reviewer3_{idx}"
    title = _pick(raw, "title", "subject", "heading", "summary")
    quote = _pick(raw, "quote", "snippet", "excerpt", "passage", "text", "highlight")
    explanation = _pick(raw, "explanation", "comment", "feedback", "body", "rationale", "message")
    if not explanation:
        # last resort: serialize whatever we have so the comment isn't empty
        explanation = json.dumps({k: v for k, v in raw.items()
                                  if k not in ("id", "commentId", "uuid", "title", "subject",
                                               "heading", "summary", "quote", "snippet",
                                               "excerpt", "passage", "text", "highlight")},
                                 ensure_ascii=False)
    return {
        "id": cid,
        "title": title,
        "quote": quote,
        "explanation": explanation,
        "comment_type": "technical",
        "paragraph_index": None,
        "_raw": raw,
    }


def build_pipeline_json(paper: Path, body: dict, *, elapsed_s: float) -> dict:
    session = body.get("session") or {}
    title = session.get("title") or paper.stem
    comments_raw = body.get("comments") or []
    comments = [_normalize_comment(c if isinstance(c, dict) else {"text": str(c)}, i)
                for i, c in enumerate(comments_raw)]
    method_key = f"{REVIEWER3_SLUG}__{REVIEWER3_SLUG}"
    overall = _pick(body, "summary", "overall", "overallFeedback", "feedback")
    return {
        "slug": paper.stem,
        "title": title,
        "paragraphs": [],
        "methods": {
            method_key: {
                "label": "Reviewer 3",
                "model": REVIEWER3_SLUG,
                "overall_feedback": overall,
                "comments": comments,
                "cost_usd": 0.0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "elapsed_s": elapsed_s,
            }
        },
    }


# ---------------------------------------------------------------------------
# Job execution
# ---------------------------------------------------------------------------

def _run_one(job: Reviewer3Job, cfg: Reviewer3Config) -> Reviewer3Result:
    job.out_json.parent.mkdir(parents=True, exist_ok=True)
    raw_path = job.out_json.with_suffix(".raw.json")
    tag = f"reviewer3/{job.paper_label}"
    print(f"[{tag}] starting: {job.paper.name}", file=sys.stderr, flush=True)
    start = time.time()
    sid = ""
    try:
        sid = _submit(cfg, job.paper, title=job.title)
        print(f"[{tag}] submitted, sessionId={sid}", file=sys.stderr, flush=True)
        body = _poll_until_done(cfg, sid, tag=tag)
        elapsed = time.time() - start
        raw_path.write_text(json.dumps(body, indent=2, ensure_ascii=False))
        pipeline = build_pipeline_json(job.paper, body, elapsed_s=elapsed)
        job.out_json.write_text(json.dumps(pipeline, indent=2, ensure_ascii=False))
        n = len(pipeline["methods"][next(iter(pipeline["methods"]))]["comments"])
        print(f"[{tag}] done in {elapsed:.0f}s ({n} comments)", file=sys.stderr, flush=True)
        return Reviewer3Result(job=job, ok=True, elapsed_s=elapsed,
                               session_id=sid, raw_response=body)
    except Exception as e:
        elapsed = time.time() - start
        msg = f"{type(e).__name__}: {e}"
        print(f"[{tag}] FAILED in {elapsed:.0f}s: {msg}", file=sys.stderr, flush=True)
        return Reviewer3Result(job=job, ok=False, elapsed_s=elapsed,
                               session_id=sid, error=msg)


def run_reviewer3_review(
    jobs: list[Reviewer3Job],
    *,
    parallel: int = 1,
    cfg: Reviewer3Config | None = None,
) -> list[Reviewer3Result]:
    """Submit each paper, poll until ready, write pipeline JSON. One result per job."""
    cfg = cfg or config_from_env()
    if parallel <= 1 or len(jobs) <= 1:
        return [_run_one(j, cfg) for j in jobs]
    results: list[Reviewer3Result] = []
    with ThreadPoolExecutor(max_workers=parallel) as pool:
        futures = {pool.submit(_run_one, j, cfg): j for j in jobs}
        for fut in as_completed(futures):
            results.append(fut.result())
    order = {id(j): i for i, j in enumerate(jobs)}
    results.sort(key=lambda r: order[id(r.job)])
    return results


# ---------------------------------------------------------------------------
# Cleanup helper (uses review:delete scope)
# ---------------------------------------------------------------------------

def delete_review(session_id: str, *, cfg: Reviewer3Config | None = None) -> bool:
    cfg = cfg or config_from_env()
    url = f"{cfg.base_url}/api/internal/review/{session_id}"
    resp = requests.delete(url, headers=_headers(cfg), timeout=cfg.request_timeout_s)
    return resp.status_code < 400
