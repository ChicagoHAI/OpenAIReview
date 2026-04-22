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
import sys
from pathlib import Path


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

    config = load_config()
    review, _markdown, paper_text = review_paper(
        pdf_path=pdf_path,
        model=model,
        skip_cost_gate=opts.get("skip_cost_gate", True),
        config=config,
    )

    # Post-hoc cost estimate using coarse's own estimator. LLMClient is built
    # inside review_paper() and not exposed — estimation keeps the number
    # internally consistent with coarse's own cost gate.
    cost_usd: float | None
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
        "cost_method": "estimated",
    }

    out_path.write_text(json.dumps(payload))


if __name__ == "__main__":
    main()
