"""Viz JSON writer for review-rounds outputs.

Produces a JSON file in the format `openaireview serve` expects (see
`src/reviewer/viz/index.html`). Reuses paragraph-splitting and fuzzy
quote-location from `reviewer.utils` so the output is byte-compatible
with other methods' output.

Output path convention: <output_dir>/<slug>_review_rounds.json, where
output_dir defaults to ./review_results so the standard
`openaireview serve --results-dir ./review_results` picks it up.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from reviewer.utils import locate_comment_in_document, split_into_paragraphs

from review_rounds.models import ConsolidatedIssue


def _short_model(model: str) -> str:
    """Trim a provider-prefixed model name to something viz-friendly.

    moonshotai/kimi-k2.6  -> kimi-k2.6
    anthropic/claude-opus -> claude-opus
    """
    return model.split("/", 1)[-1]


def _slugify(paper_path: str) -> str:
    """Match the slug convention `openaireview serve` uses for filenames."""
    stem = Path(paper_path).stem
    slug = re.sub(r"[^a-z0-9]+", "_", stem.lower()).strip("_")
    return slug or "paper"


def write_viz_json(
    *,
    paper_path: str,
    paper_title: str,
    paper_text: str,
    issues: list[ConsolidatedIssue],
    overall_feedback: str,
    model: str,
    output_dir: Path,
    usage: dict | None = None,
) -> Path:
    """Write a viz-compatible JSON, return its path.

    Mutation note: this function does not modify `issues`; paragraph
    indices are assigned to the emitted dicts, not back to the Pydantic
    models."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Paragraph-split the paper text. Reuse the main package's splitter
    #    so fuzzy matches index into the same space the UI expects.
    paragraphs = split_into_paragraphs(paper_text)

    # 2. Emit one viz-comment per issue, with paragraph_index via fuzzy match.
    method_short = _short_model(model)
    method_key = f"review_rounds__{method_short}"

    viz_comments: list[dict] = []
    for n, issue in enumerate(issues):
        para_idx = locate_comment_in_document(issue.quote, paragraphs)
        viz_comments.append({
            "id": f"{method_key}_{n}",
            "title": issue.title,
            "quote": issue.quote,
            "explanation": issue.explanation,
            "comment_type": issue.comment_type,
            "severity": issue.severity,
            "paragraph_index": para_idx,
        })

    slug = _slugify(paper_path)
    usage = usage or {}
    method_block = {
        "label": f"Review Rounds ({method_short})",
        "model": model,
        "overall_feedback": overall_feedback,
        "comments": viz_comments,
        # Populated by review_rounds._UsageCollector via LangChain callbacks.
        # OpenRouter returns cost per response; we sum across all graph nodes.
        "cost_usd": usage.get("cost_usd", 0),
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        # Extra fields (not required by viz UI but useful in raw JSON):
        "reasoning_tokens": usage.get("reasoning_tokens", 0),
        "llm_calls": usage.get("calls", 0),
    }

    # Merge convention: if <slug>.json already exists (another method wrote
    # it), drop our method block into its `methods` dict. Otherwise write a
    # fresh doc. Matches src/reviewer/cli.py and save_viz_json.py so the
    # main `openaireview serve` UI renders review_rounds as one method
    # alongside the others on the same paper.
    path = output_dir / f"{slug}.json"
    if path.exists():
        try:
            doc = json.loads(path.read_text())
            doc.setdefault("methods", {})[method_key] = method_block
            # Backfill paragraphs/title if the existing doc is missing them.
            doc.setdefault("slug", slug)
            doc.setdefault("title", paper_title)
            doc.setdefault("paragraphs", [{"index": i, "text": p} for i, p in enumerate(paragraphs)])
        except (json.JSONDecodeError, KeyError):
            doc = _fresh_doc(slug, paper_title, paragraphs, method_key, method_block)
    else:
        doc = _fresh_doc(slug, paper_title, paragraphs, method_key, method_block)

    path.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    return path


def _fresh_doc(slug: str, title: str, paragraphs: list[str], method_key: str, method_block: dict) -> dict:
    return {
        "slug": slug,
        "title": title,
        "paragraphs": [{"index": i, "text": p} for i, p in enumerate(paragraphs)],
        "methods": {method_key: method_block},
    }
