"""Evaluation for the OpenReview benchmark track (pooled human text + LLM judge).

Unlike ``evaluate.py`` (Refine), ground truth is not paragraph-anchored. We define:

- **Precision:** fraction of model comments that the judge says overlap with *any*
  substantive issue in the **pooled** human review text (all reviewers).
- **Recall:** for each **official review** separately, fraction of reviews for which
  the judge says *at least one* model comment addresses a substantive critique or
  question in that review; then average across reviewers (macro recall).

**F1:** harmonic mean of precision and recall on [0, 1].

Requires API access for ``reviewer.client.chat`` (e.g. ``OPENAI_API_KEY`` + judge model).
"""

from __future__ import annotations

import os
from typing import Any

from .client import chat
from .models import Comment

DEFAULT_OPENREVIEW_JUDGE_MODEL = os.environ.get(
    "OPENREVIEW_JUDGE_MODEL", "gpt-4o-mini"
)

# Keep prompts within context limits
MAX_POOLED_CHARS = 28_000
MAX_SINGLE_REVIEW_CHARS = 12_000
MAX_PRED_LIST_CHARS = 24_000

# Bedrock-backed judges sometimes return 400 "Operation not allowed" transiently; extra retries help.
_JUDGE_CHAT_RETRIES = 8


def format_official_review_text(review: dict[str, Any]) -> str:
    """Build one string from OpenReview-style review fields."""
    parts: list[str] = []
    for key in ("summary", "strengths", "weaknesses", "questions"):
        val = review.get(key)
        if val and str(val).strip():
            parts.append(f"## {key.replace('_', ' ').title()}\n{val.strip()}")
    return "\n\n".join(parts)


def pool_human_reviews(paper: dict[str, Any]) -> str:
    """Concatenate all official reviews with separators."""
    reviews = paper.get("reviews") or []
    blocks = [format_official_review_text(r) for r in reviews if format_official_review_text(r)]
    return "\n\n==========\n\n".join(blocks)


def _truncate(s: str, max_len: int) -> str:
    if len(s) <= max_len:
        return s
    return s[: max_len - 20] + "\n...[truncated]"


def _yes_no_from_response(text: str) -> bool:
    t = text.strip().upper()
    return t.startswith("YES")


def llm_precision_vs_pooled(
    pred: Comment,
    pooled_human_text: str,
    model: str,
    provider: str | None = None,
) -> bool:
    """True if the judge says this prediction overlaps any substantive human issue."""
    pooled = _truncate(pooled_human_text, MAX_POOLED_CHARS)
    prompt = f"""You compare one model-generated review comment to the combined text of human peer reviews (multiple reviewers; sections may include summary, strengths, weaknesses, questions).

Human reviews (combined):
{pooled}

Predicted comment:
Title: {pred.title}
Quote from paper: {pred.quote[:1200]}
Explanation: {pred.explanation[:2000]}

Does this predicted comment identify or substantially overlap with ANY substantive critique, limitation, or question raised in the human reviews? (Agreement with strengths-only praise alone does not count as YES.)

Reply with exactly one word: YES or NO."""
    response, _ = chat(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        temperature=0.0,
        max_tokens=8,
        provider=provider,
        retries=_JUDGE_CHAT_RETRIES,
    )
    return _yes_no_from_response(response)


def llm_recall_one_review(
    review_text: str,
    preds: list[Comment],
    model: str,
    provider: str | None = None,
) -> bool:
    """True if the judge says at least one prediction addresses an issue in this review."""
    if not review_text.strip():
        return False
    rev = _truncate(review_text, MAX_SINGLE_REVIEW_CHARS)
    lines: list[str] = []
    for i, p in enumerate(preds, 1):
        lines.append(
            f"{i}. Title: {p.title}\n   Quote: {p.quote[:600]}\n   Explanation: {p.explanation[:1200]}"
        )
    pred_block = _truncate("\n\n".join(lines), MAX_PRED_LIST_CHARS)

    prompt = f"""Human review from ONE reviewer (sections may include summary, strengths, weaknesses, questions):

{rev}

Predicted comments from a model (numbered):
{pred_block}

Does at least ONE predicted comment address the same substantive issue as ANY criticism, limitation, or question in this human review? (Focus on weaknesses and questions; matching only generic strengths without addressing a concern does not count.)

Reply with exactly one word: YES or NO."""
    response, _ = chat(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        temperature=0.0,
        max_tokens=8,
        provider=provider,
        retries=_JUDGE_CHAT_RETRIES,
    )
    return _yes_no_from_response(response)


def evaluate_openreview_pooled(
    predictions: list[Comment],
    paper: dict[str, Any],
    judge_model: str | None = None,
    judge_provider: str | None = None,
) -> dict[str, Any]:
    """Compute precision, recall, F1 for one paper.

    ``paper`` is one line from ``openreview_benchmark.jsonl`` (dict).
    """
    model = judge_model or DEFAULT_OPENREVIEW_JUDGE_MODEL
    reviews = paper.get("reviews") or []
    pooled = pool_human_reviews(paper)

    if not predictions:
        return {
            "precision": 0.0,
            "recall": 0.0,
            "f1": 0.0,
            "num_predictions": 0,
            "num_human_reviews": len(reviews),
            "num_predictions_matched": 0,
            "num_reviews_covered": 0,
            "judge_model": model,
        }

    matched_preds = 0
    for pred in predictions:
        if llm_precision_vs_pooled(pred, pooled, model, provider=judge_provider):
            matched_preds += 1

    precision = matched_preds / len(predictions)

    covered = 0
    for r in reviews:
        text = format_official_review_text(r)
        if not text.strip():
            continue
        if llm_recall_one_review(text, predictions, model, provider=judge_provider):
            covered += 1

    nonempty = sum(1 for r in reviews if format_official_review_text(r).strip())
    recall = (covered / nonempty) if nonempty else 0.0

    if precision + recall > 0:
        f1 = 2 * precision * recall / (precision + recall)
    else:
        f1 = 0.0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "num_predictions": len(predictions),
        "num_human_reviews": len(reviews),
        "num_predictions_matched": matched_preds,
        "num_reviews_covered": covered,
        "num_nonempty_reviews": nonempty,
        "judge_model": model,
    }


def comments_from_results_json(data: dict[str, Any], method_key: str | None = None) -> list[Comment]:
    """Load Comment list from a ``review_results`` JSON file (viz format)."""
    methods = data.get("methods") or {}
    if not methods:
        return []
    if method_key is not None:
        key = method_key
        if key not in methods:
            raise KeyError(f"method key not found: {key!r}. Available: {list(methods)}")
    else:
        key = next(iter(methods))
    block = methods[key]
    out: list[Comment] = []
    for c in block.get("comments") or []:
        out.append(
            Comment(
                title=c.get("title", ""),
                quote=c.get("quote", ""),
                explanation=c.get("explanation", ""),
                comment_type=c.get("comment_type", "technical"),
                paragraph_index=c.get("paragraph_index"),
            )
        )
    return out
