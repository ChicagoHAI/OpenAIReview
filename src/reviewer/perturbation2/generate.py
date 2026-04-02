"""LLM-based error generation from candidate spans.

Stage 1: LLM picks from pre-extracted candidates and creates perturbations.
Stage 2: LLM proposes free-form errors the extraction missed (validated by fuzzy match).
"""

import json
import re

from ..client import chat
from .models import (
    CandidateSpan,
    ErrorCategory,
    Perturbation,
)

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

STAGE1_PROMPT = """\
You are generating seeded perturbations for an academic paper review benchmark.

Below are candidate spans extracted from the paper. Each has a span_id, type, \
the exact text, and surrounding context.

IMPORTANT RULES:
- Choose spans where a minimal edit creates an internally inconsistent paper
- The error must be verifiable from the paper text alone, not external knowledge
- Do NOT perturb spans that look OCR-corrupted or ambiguous
- Each perturbation must target a DIFFERENT fact or equation
- Aim for {n_per_category} perturbations per category when possible

CANDIDATES:
{candidates_json}

For each perturbation, return:
- span_id: which candidate to perturb
- category: one of {categories}
- perturbed: the replacement text (must differ from original)
- why_wrong: how a reader can verify this is wrong using only the paper
- support_span_ids: list of other span_ids that prove it's wrong (if crossref)

Return ONLY a JSON array of perturbation objects. No commentary."""

# ---------------------------------------------------------------------------
# Stage 1: Pick from candidates
# ---------------------------------------------------------------------------

def generate_from_candidates(
    candidates: list[CandidateSpan],
    model: str = "anthropic/claude-opus-4-6",
    n_per_category: int = 2,
    reasoning_effort: str | None = None,
) -> list[Perturbation]:
    """Ask the LLM to create perturbations from pre-extracted candidates.

    Runs one call per category group (technical vs prose) to prevent
    the model from drifting toward easy overclaims.
    """
    technical_cats = [
        ErrorCategory.OPERATOR_OR_SIGN,
        ErrorCategory.SYMBOL_BINDING,
        ErrorCategory.INDEX_OR_SUBSCRIPT,
        ErrorCategory.NUMERIC_PARAMETER,
    ]

    all_perturbations: list[Perturbation] = []

    for cat_group, label in [(technical_cats, "technical")]:
        # Filter candidates compatible with this category groups
        filtered = [
            c for c in candidates
            if any(cat in c.compatible_categories for cat in cat_group)
        ]
        if not filtered:
            continue

        # Build candidate JSON for the prompt
        candidates_json = json.dumps([
            {
                "span_id": c.span_id,
                "type": c.span_type.value,
                "text": c.text,
                "context": c.context[:300],
                "compatible_categories": [cat.value for cat in c.compatible_categories
                                          if cat in cat_group],
            }
            for c in filtered
        ], indent=2)

        prompt = STAGE1_PROMPT.format(
            n_per_category=n_per_category,
            candidates_json=candidates_json,
            categories=", ".join(c.value for c in cat_group),
        )

        print(f"  Stage 1 ({label}): {len(filtered)} candidates...")
        response, usage = chat(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            max_tokens=8192,
            reasoning_effort=reasoning_effort,
        )

        perturbations = _parse_stage1_response(response, candidates)
        all_perturbations.extend(perturbations)
        print(f"    -> {len(perturbations)} perturbations")

    return all_perturbations


def _parse_stage1_response(
    response: str,
    candidates: list[CandidateSpan],
) -> list[Perturbation]:
    """Parse Stage 1 LLM response into Perturbation objects."""
    span_lookup = {c.span_id: c for c in candidates}

    arr_match = re.search(r"\[.*\]", response, re.DOTALL)
    if not arr_match:
        return []

    try:
        items = json.loads(arr_match.group(0))
    except json.JSONDecodeError:
        return []

    perturbations = []
    for i, item in enumerate(items):
        span_id = item.get("span_id", "")
        if span_id not in span_lookup:
            continue

        span = span_lookup[span_id]
        perturbed = item.get("perturbed", "")
        if not perturbed or perturbed == span.text:
            continue

        try:
            category = ErrorCategory(item.get("category", ""))
        except ValueError:
            continue

        perturbations.append(Perturbation(
            perturbation_id=f"P{i:03d}_{span_id}",
            span_id=span_id,
            category=category,
            original=span.text,  # from OUR store, not the model's
            perturbed=perturbed,
            why_wrong=item.get("why_wrong", ""),
            support_span_ids=item.get("support_span_ids", []),
        ))

    return perturbations