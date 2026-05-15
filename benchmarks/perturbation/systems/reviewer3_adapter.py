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
    paper: Path                 # path to *_corrupted.md (staged, possibly token-truncated)
    out_json: Path              # where to write the pipeline-shaped JSON
    paper_label: str            # e.g. "<error_type>/<paper_label>"
    title: str | None = None
    # Optional: full pre-truncation source. When provided, _ensure_pdf
    # compiles THIS instead of `paper` — the staged file is often invalid
    # LaTeX because token truncation can chop mid-environment.
    source: Path | None = None
    # Optional: trim the rendered PDF to its first N pages so R3 still sees
    # roughly the same window other systems do (coarse uses max_pages: 20).
    max_pages: int | None = None


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


def _ensure_pdf(paper: Path, *, source: Path | None = None,
                max_pages: int | None = None) -> Path:
    """Reviewer 3 only accepts PDF. Return a compiled+possibly-trimmed PDF.

    Resolution order for the source bytes:
      1. If `paper` is already a `.pdf`, return it as-is (page trim still applies).
      2. If `source` was provided, compile that — preferred for LaTeX-as-md
         since the staged `paper` is often invalid LaTeX (token truncation
         chops mid-environment).
      3. Else compile `paper` directly. If it lacks `\\end{document}`, append
         one as a best-effort close.

    When `max_pages` is set, the resulting PDF is trimmed to its first N
    pages via pymupdf. This matches what coarse does (max_pages: 20) so R3
    sees roughly the same window other systems see.
    """
    if paper.suffix.lower() == ".pdf":
        return _maybe_trim_pages(paper, max_pages)

    src_for_compile = source if (source is not None and source.exists()) else paper
    cached_suffix = ".trim.pdf" if max_pages else ".pdf"
    cached = src_for_compile.with_suffix(cached_suffix)
    src_mtime = src_for_compile.stat().st_mtime
    if cached.exists() and cached.stat().st_mtime > src_mtime:
        return cached

    head = src_for_compile.read_text(errors="replace")[:2000]
    if "\\documentclass" not in head:
        raise RuntimeError(
            f"don't know how to convert {src_for_compile.name} to PDF "
            "(no \\documentclass found; expected LaTeX-as-md or PDF)"
        )
    text = src_for_compile.read_text(errors="replace")
    if "\\end{document}" not in text:
        # `source` should always close cleanly; this only fires if we fell back
        # to compiling the token-truncated `paper`.
        text = text.rstrip() + "\n\n\\end{document}\n"
    # Strip orphan \input / \include — the perturbation corpus dumps each paper
    # into a single .md but a few preserve `\input{mypreamble.tex}`-style
    # directives that pdflatex can't resolve (fatal error, no PDF produced).
    text = _strip_orphan_includes(text, src_for_compile.parent)
    # Stripped-include papers (and some others) rely on author-defined shortcuts
    # like \bbC, \calA, \vvirg, \ootimes from the missing preamble. Inject
    # \providecommand fallbacks so the body compiles.
    text = _inject_rescue_preamble(text)

    import shutil, subprocess, tempfile
    with tempfile.TemporaryDirectory() as td:
        tex = Path(td) / "source.tex"
        tex.write_text(text)
        # Run twice to resolve cross-refs; ignore exit code, accept partial PDF.
        # Capture output as bytes — pdflatex's own log can contain non-UTF-8
        # accent bytes and we don't read this output anyway (the .log file is
        # the source of truth on failure).
        for _ in range(2):
            subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "source.tex"],
                cwd=td, capture_output=True, timeout=300,
            )
        out_pdf = Path(td) / "source.pdf"
        if not out_pdf.exists() or out_pdf.stat().st_size < 1000:
            log_path = Path(td) / "source.log"
            log = log_path.read_text(errors="replace") if log_path.exists() else ""
            raise RuntimeError(
                f"pdflatex produced no usable PDF for {src_for_compile}: {log[-1500:]}"
            )
        if max_pages:
            _trim_pages_to(out_pdf, max_pages)
        shutil.copy(out_pdf, cached)
    return cached


_INPUT_RE = __import__("re").compile(
    r"\\(?:input|include)\s*\{([^}]+)\}", flags=__import__("re").IGNORECASE,
)


def _strip_orphan_includes(text: str, base_dir: Path) -> str:
    """Comment out `\\input{path}` / `\\include{path}` whose target file isn't
    next to the source. pdflatex aborts hard on a missing \\input, which kills
    the compile even when the rest of the document is fine."""
    def _replace(m):
        target = m.group(1).strip()
        # Common LaTeX convention: optional .tex extension.
        for cand in (target, target + ".tex"):
            if (base_dir / cand).exists():
                return m.group(0)
        return "% [stripped missing include] " + m.group(0)
    return _INPUT_RE.sub(_replace, text)


# Defensive preamble injected after \documentclass to provide fallbacks for
# common custom-command patterns that authors typically define in private
# preamble files (e.g. mypreamble.tex). \providecommand is a no-op when the
# command is already defined, so this is safe to inject blindly.
_RESCUE_PREAMBLE = r"""
% --- injected by reviewer3_adapter: providecommand fallbacks ---
% blackboard / cal / bf shortcuts authors commonly define per-paper
\providecommand{\bb}[1]{\mathbb{#1}}
\providecommand{\cal}[1]{\mathcal{#1}}
\providecommand{\bff}[1]{\mathbf{#1}}
% common single-letter shortcuts (\bbR, \calA, \bfx, etc.)
\makeatletter
\@for\letter:={A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z}\do{%
  \expandafter\providecommand\csname bb\letter\endcsname{\ensuremath{\mathbb{\letter}}}%
  \expandafter\providecommand\csname cal\letter\endcsname{\ensuremath{\mathcal{\letter}}}%
}
\@for\letter:={a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z,A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z}\do{%
  \expandafter\providecommand\csname bf\letter\endcsname{\ensuremath{\mathbf{\letter}}}%
}
\makeatother
% other commonly-used shortcuts
\providecommand{\eps}{\epsilon}
\providecommand{\veps}{\varepsilon}
\providecommand{\vvirg}{,\,}
\providecommand{\ootimes}{\otimes}
\providecommand{\Bbbk}{\mathbb{k}}
% --- end injected preamble ---
"""


def _inject_rescue_preamble(text: str) -> str:
    """Insert _RESCUE_PREAMBLE right after the first \\documentclass{...} line.
    Idempotent: looks for our marker before injecting."""
    if "injected by reviewer3_adapter" in text:
        return text
    import re
    m = re.search(r"\\documentclass(\[[^\]]*\])?\{[^}]+\}", text)
    if not m:
        return text
    cut = m.end()
    return text[:cut] + "\n" + _RESCUE_PREAMBLE + text[cut:]


def _maybe_trim_pages(pdf: Path, max_pages: int | None) -> Path:
    """Return `pdf` (already a PDF). If `max_pages` is set and the PDF has more,
    return a trimmed sibling cached next to it."""
    if not max_pages:
        return pdf
    import fitz
    src = fitz.open(pdf)
    try:
        if src.page_count <= max_pages:
            return pdf
        trimmed = pdf.with_suffix(f".first{max_pages}p.pdf")
        if trimmed.exists() and trimmed.stat().st_mtime > pdf.stat().st_mtime:
            return trimmed
        dst = fitz.open()
        dst.insert_pdf(src, from_page=0, to_page=max_pages - 1)
        dst.save(trimmed)
        dst.close()
        return trimmed
    finally:
        src.close()


def _trim_pages_to(pdf: Path, max_pages: int) -> None:
    """In-place trim of `pdf` to its first `max_pages` pages."""
    import fitz
    src = fitz.open(pdf)
    try:
        if src.page_count <= max_pages:
            return
        dst = fitz.open()
        dst.insert_pdf(src, from_page=0, to_page=max_pages - 1)
        tmp = pdf.with_suffix(".pdf.tmp")
        dst.save(tmp)
        dst.close()
    finally:
        src.close()
    tmp.replace(pdf)


def _submit(cfg: Reviewer3Config, paper: Path, *, title: str | None,
            source: Path | None = None, max_pages: int | None = None) -> str:
    """POST /api/internal/review (multipart). Returns sessionId.

    `source` and `max_pages` are forwarded to `_ensure_pdf` so callers can opt
    into compiling the full pre-truncation source and trimming the rendered
    PDF — see _ensure_pdf docstring.
    """
    paper = _ensure_pdf(paper, source=source, max_pages=max_pages)
    url = f"{cfg.base_url}/api/internal/review"
    data: dict[str, str] = {
        "userId": cfg.user_id,
        "reviewMode": cfg.review_mode,
        "filename": paper.name,
    }
    if title:
        data["title"] = title
    with paper.open("rb") as fh:
        files = {"file": (paper.name, fh, "application/pdf")}
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


# Canonical severity mapping lives in benchmarks/perturbation/_severity.py
# so every system (coarse, reviewer3, openaireview) and the downstream
# conference-study analyses share one source of truth.
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent.parent))
from _severity import normalize_severity as _normalize_r3_severity  # noqa: E402


def _normalize_comment(raw: dict, idx: int) -> dict:
    """Map a Reviewer 3 comment to the pipeline schema.

    Reviewer 3 comments carry: reviewerId, comment, title, citedText, severity, rank.
    `citedText` is the verbatim excerpt from the paper — what our scorer uses as
    `quote` for fuzzy/semantic matching.
    """
    cid = _pick(raw, "id", "commentId", "uuid") or f"reviewer3_{idx}"
    title = _pick(raw, "title")
    quote = _pick(raw, "citedText", "quote", "snippet", "excerpt", "passage", "highlight")
    explanation = _pick(raw, "comment", "explanation", "feedback", "body", "rationale", "message")
    severity = _normalize_r3_severity("reviewer3", raw.get("severity"))
    if not explanation:
        explanation = json.dumps(raw, ensure_ascii=False)
    return {
        "id": cid,
        "title": title,
        "quote": quote,
        "explanation": explanation,
        "comment_type": "technical",
        "severity": severity,
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
        sid = _submit(cfg, job.paper, title=job.title,
                      source=job.source, max_pages=job.max_pages)
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
