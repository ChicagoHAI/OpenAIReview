"""Shared utilities for competitor adapters: paragraph assignment + result-JSON merge."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from reviewer.utils import locate_comment_in_document

from .base import NormalizedReview


def model_short(model: str) -> str:
    """Strip provider prefix. Matches openaireview cli.py's _model_short_name."""
    return model.split("/")[-1] if "/" in model else model


def build_method_data(
    review: NormalizedReview,
    method_key: str,
    method_label: str,
    paragraphs: list[str],
) -> dict[str, Any]:
    """Build the per-method JSON block matching openaireview's _build_paper_json.

    Assigns ``paragraph_index`` to each comment by fuzzy-matching its quote
    against the openaireview-parsed paragraphs — guaranteeing granularity
    matches ``progressive__*`` entries in the same result file.
    """
    comments_out = []
    for i, c in enumerate(review.comments):
        paragraph_index = locate_comment_in_document(c.quote, paragraphs)
        entry = {
            "id": f"{method_key}_{i}",
            "title": c.title,
            "quote": c.quote,
            "explanation": c.explanation,
            "comment_type": c.comment_type,
            "paragraph_index": paragraph_index,
        }
        # Adapter-specific fields (severity, confidence, etc.) pass through
        # as top-level keys. Existing consumers ignore unknown keys.
        entry.update(c.extra)
        comments_out.append(entry)

    method_data: dict[str, Any] = {
        "label": method_label,
        "model": review.model,
        "overall_feedback": review.overall_feedback,
        "comments": comments_out,
        "cost_usd": round(review.cost_usd, 4) if review.cost_usd is not None else None,
        "cost_method": review.cost_method,
        "prompt_tokens": review.prompt_tokens,
        "completion_tokens": review.completion_tokens,
    }
    return method_data


def merge_into_paper_json(
    out_file: Path,
    slug: str,
    title: str,
    paragraphs: list[str],
    method_key: str,
    method_data: dict[str, Any],
) -> None:
    """Read-modify-write a paper's result JSON, inserting/overwriting one method.

    Preserves ``paragraphs`` already on disk when available (so we keep the
    exact text that ``progressive__*`` methods were scored against). Falls
    back to our freshly-parsed paragraphs if the file doesn't exist yet.
    """
    if out_file.exists():
        try:
            paper_data = json.loads(out_file.read_text())
        except json.JSONDecodeError:
            paper_data = None
    else:
        paper_data = None

    if paper_data is None:
        para_list = [{"index": i, "text": p} for i, p in enumerate(paragraphs)]
        paper_data = {
            "slug": slug,
            "title": title,
            "paragraphs": para_list,
            "methods": {},
        }
    else:
        paper_data.setdefault("methods", {})

    paper_data["methods"][method_key] = method_data
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(paper_data, indent=2))
