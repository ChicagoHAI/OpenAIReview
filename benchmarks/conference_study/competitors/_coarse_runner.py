#!/usr/bin/env python
"""Runs inside the coarse venv. Not called directly — invoked by coarse_adapter.py.

Usage (argv):
    _coarse_runner.py <pdf_path> <model> <opts_json> <output_json_path>

Writes a normalized review dict to <output_json_path> and exits 0 on success.
Stdout/stderr carry coarse's own progress logs — the adapter doesn't parse
them, it reads <output_json_path>.

Output JSON schema (keys stable for the adapter to consume):
    {
      "model": str,
      "comments": [{title, quote, feedback, severity, confidence, status, number}],
      "overall_feedback": {summary, assessment, issues: [{title, body}],
                           recommendation, revision_targets},
      "cost_usd": float | null,
      "cost_method": "estimated"
    }
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.request
from pathlib import Path


def _install_generation_id_capture() -> list[str]:
    """Monkey-patch litellm.completion to record every OpenRouter generation
    id. Returns a list that callers can read after the review finishes."""
    captured: list[str] = []
    import litellm
    orig = litellm.completion

    def wrapped(*args, **kwargs):
        eb = kwargs.get("extra_body") or {}
        eb.setdefault("usage", {"include": True})
        kwargs["extra_body"] = eb
        resp = orig(*args, **kwargs)
        gid = getattr(resp, "id", None)
        if gid:
            captured.append(gid)
        return resp

    litellm.completion = wrapped
    return captured


def _fetch_actual_cost(generation_ids: list[str]) -> float | None:
    """Sum the real OpenRouter cost across captured generation ids.

    Skips ids that fail to resolve (sometimes they need a few seconds for
    OpenRouter's billing pipeline to settle). Returns None if everything
    fails — caller falls back to coarse's local estimate.
    """
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key or not generation_ids:
        return None
    total = 0.0
    found = 0
    for gid in generation_ids:
        for attempt in range(3):
            req = urllib.request.Request(
                f"https://openrouter.ai/api/v1/generation?id={gid}",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            try:
                with urllib.request.urlopen(req, timeout=15) as r:
                    body = json.loads(r.read())
                cost = body.get("data", {}).get("total_cost")
                if cost is not None:
                    total += float(cost)
                    found += 1
                    break
            except Exception:
                pass
            time.sleep(2 ** attempt)
    return total if found else None


def main() -> None:
    if len(sys.argv) != 5:
        sys.stderr.write(f"usage: {sys.argv[0]} <pdf> <model> <opts_json> <out_json>\n")
        sys.exit(2)

    pdf_path = Path(sys.argv[1])
    model = sys.argv[2]
    opts = json.loads(sys.argv[3])
    out_path = Path(sys.argv[4])

    from coarse.config import load_config
    from coarse.pipeline import review_paper

    captured_ids = _install_generation_id_capture()

    # Optional override for the gemini models coarse uses internally
    # (extraction file-parser host + post-extraction vision QA). Cheaper
    # than the gemini-3-flash-preview default.
    gemini_override = opts.get("gemini_internal_model")
    if gemini_override:
        import coarse.models as _cm
        _cm.OPENROUTER_EXTRACTION_MODEL = gemini_override
        # extraction.py imports the constant lazily inside a function so the
        # rebind takes effect on the next call.

    config = load_config()
    if gemini_override:
        # vision_model is read off `config` at runtime in pipeline.py, so
        # mutating it here propagates without needing to reimport.
        config.vision_model = (
            gemini_override
            if gemini_override.startswith(("gemini/", "google/"))
            else f"gemini/{gemini_override.split('/')[-1]}"
        )
    review, _markdown, paper_text = review_paper(
        pdf_path=pdf_path,
        model=model,
        skip_cost_gate=opts.get("skip_cost_gate", True),
        config=config,
    )

    # Prefer actual OpenRouter cost (summed via /generation lookup over the
    # captured ids). Fall back to coarse's own estimator if the lookup fails
    # (e.g. non-OpenRouter calls or transient API issues).
    cost_usd: float | None = None
    cost_method = "estimated"
    actual = _fetch_actual_cost(captured_ids)
    if actual is not None:
        cost_usd = actual
        cost_method = "openrouter_actual"
    else:
        try:
            from coarse.cost import build_cost_estimate

            est = build_cost_estimate(paper_text, config, model=model)
            cost_usd = float(est.total_cost_usd)
        except Exception:
            cost_usd = None

    payload = {
        "model": model,
        "comments": [
            {
                "title": c.title,
                "quote": c.quote,
                "feedback": c.feedback,
                "severity": c.severity,
                "confidence": c.confidence,
                "status": c.status,
                "number": c.number,
            }
            for c in review.detailed_comments
        ],
        "overall_feedback": {
            "summary": review.overall_feedback.summary,
            "assessment": review.overall_feedback.assessment,
            "issues": [
                {"title": i.title, "body": i.body}
                for i in review.overall_feedback.issues
            ],
            "recommendation": review.overall_feedback.recommendation,
            "revision_targets": list(review.overall_feedback.revision_targets),
        },
        "cost_usd": cost_usd,
        "cost_method": cost_method,
        "n_llm_calls": len(captured_ids),
    }

    out_path.write_text(json.dumps(payload))


if __name__ == "__main__":
    main()
