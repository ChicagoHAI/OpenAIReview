"""Adapter for Reviewer 3 (closed-source HTTP API).

Submission flow is the same as the perturbation benchmark — POST a PDF to
`/api/internal/review`, poll the session until the `status` enum is terminal,
then map each comment via `_normalize_comment`. We reuse those helpers from
the perturbation adapter (`benchmarks/perturbation/systems/reviewer3_adapter.py`)
rather than duplicating the HTTP code; the only difference here is that
conference inputs arrive as PDFs already, so the LaTeX-as-md → PDF compile
step (`_ensure_pdf`) is unnecessary.

Reviewer 3 has no model selector, so `method_key(...)` always returns
`"reviewer3__reviewer3"` regardless of the manifest `model` value. The
conference YAML should pin `models: [reviewer3]` to avoid duplicate
submissions across a phantom model loop.

Required env:
    REVIEWER3_API_KEY    sk_... (sent as `x-api-key` header)
    REVIEWER3_USER_ID    UUID from the vendor's web UI session JSON (not an email)
"""
from __future__ import annotations

import sys
from pathlib import Path

from .base import CompetitorAdapter, NormalizedComment, NormalizedReview

# Reuse the perturbation adapter's HTTP + normalization helpers.
_PERT = Path(__file__).resolve().parents[2] / "perturbation" / "systems"
sys.path.insert(0, str(_PERT))
import reviewer3_adapter as _r3  # noqa: E402


_METHOD_KEY = f"{_r3.REVIEWER3_SLUG}__{_r3.REVIEWER3_SLUG}"


class Reviewer3Adapter(CompetitorAdapter):
    name = "reviewer3"
    required_env = ("REVIEWER3_API_KEY", "REVIEWER3_USER_ID")

    def method_key(self, model: str) -> str:
        # R3 has no model selector — fixed key regardless of `model`.
        return _METHOD_KEY

    def review(self, pdf: Path, model: str, cfg: dict) -> NormalizedReview:
        opts = cfg.get("reviewer3_options", {}) or {}
        rcfg = _r3.config_from_env()
        for k in ("review_mode", "poll_interval_s", "poll_timeout_s",
                  "request_timeout_s", "base_url"):
            if k in opts and opts[k] is not None:
                setattr(rcfg, k, opts[k])

        session_id = _r3._submit(rcfg, pdf, title=pdf.stem)
        body = _r3._poll_until_done(rcfg, session_id, tag=f"reviewer3/{pdf.stem}")

        comments: list[NormalizedComment] = []
        for i, raw in enumerate(body.get("comments") or []):
            if not isinstance(raw, dict):
                raw = {"comment": str(raw)}
            norm = _r3._normalize_comment(raw, i)
            comments.append(NormalizedComment(
                title=norm.get("title", ""),
                quote=norm.get("quote", ""),
                explanation=norm.get("explanation", ""),
                comment_type=norm.get("comment_type", "technical"),
                extra={
                    "severity": norm.get("severity"),
                    "reviewerId": raw.get("reviewerId"),
                    "rank": raw.get("rank"),
                    "session_id": session_id,
                },
            ))

        # R3 doesn't publish pricing and doesn't return overall_feedback or
        # token counts in its response, so we leave those empty/None.
        return NormalizedReview(
            comments=comments,
            overall_feedback="",
            cost_usd=None,
            cost_method="estimated",
            prompt_tokens=None,
            completion_tokens=None,
            model=_r3.REVIEWER3_SLUG,
        )
