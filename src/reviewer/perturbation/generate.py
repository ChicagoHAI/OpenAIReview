"""LLM-based error generation from candidate spans.

Stage 1: LLM picks from pre-extracted candidates and creates perturbations.
Stage 2: LLM proposes free-form errors the extraction missed (validated by fuzzy match).
"""

import json
import re
from difflib import SequenceMatcher

from ..client import chat
from .models import (
    CandidateSpan,
    Difficulty,
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
- difficulty: "local" (same paragraph) or "crossref" (needs another section)
- support_span_ids: list of other span_ids that prove it's wrong (if crossref)

Return ONLY a JSON array of perturbation objects. No commentary."""

STAGE2_PROMPT = """\
You are generating seeded perturbations for an academic paper review benchmark.

Below is the paper with line numbers [L001], [L002], etc. The following error \
categories have already been covered by extracted spans: {covered_categories}.

Find {n_errors} additional error opportunities that the automatic extraction \
MISSED. Focus on:
- Claim strengthening (subtle overclaims in results/conclusions)
- Condition changes (swapping treatment/control, necessary/sufficient)
- Cross-section inconsistencies (a statement in one section contradicts another)

IMPORTANT RULES:
- Quote the EXACT original text (verbatim, including any LaTeX)
- The error must be verifiable from the paper text alone
- Reference the line number [LNNN] where the text appears

PAPER:
{numbered_paper}

Return ONLY a JSON array:
[
  {{
    "line_number": NNN,
    "original": "exact verbatim text",
    "perturbed": "replacement text",
    "category": "claim_strengthening" or "condition_or_assumption",
    "why_wrong": "explanation",
    "difficulty": "local" or "crossref"
  }}
]"""


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
    prose_cats = [
        ErrorCategory.CLAIM_STRENGTHENING,
        ErrorCategory.CONDITION_OR_ASSUMPTION,
    ]

    all_perturbations: list[Perturbation] = []

    for cat_group, label in [(technical_cats, "technical"), (prose_cats, "prose")]:
        # Filter candidates compatible with this category group
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

        try:
            difficulty = Difficulty(item.get("difficulty", "local"))
        except ValueError:
            difficulty = Difficulty.LOCAL

        perturbations.append(Perturbation(
            perturbation_id=f"P{i:03d}_{span_id}",
            span_id=span_id,
            category=category,
            original=span.text,  # from OUR store, not the model's
            perturbed=perturbed,
            why_wrong=item.get("why_wrong", ""),
            difficulty=difficulty,
            support_span_ids=item.get("support_span_ids", []),
        ))

    return perturbations


# ---------------------------------------------------------------------------
# Stage 2: Free-form proposals
# ---------------------------------------------------------------------------

def generate_freeform(
    paper_text: str,
    numbered_text: str,
    covered_categories: list[str],
    model: str = "anthropic/claude-opus-4-6",
    n_errors: int = 4,
    reasoning_effort: str | None = None,
) -> list[Perturbation]:
    """Ask the LLM to find errors that automatic extraction missed.

    Uses line-number anchoring + fuzzy match for validation.
    """
    prompt = STAGE2_PROMPT.format(
        covered_categories=", ".join(covered_categories),
        n_errors=n_errors,
        numbered_paper=numbered_text[:80000],  # truncate for context window
    )

    print(f"  Stage 2 (free-form): requesting {n_errors} proposals...")
    response, usage = chat(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        max_tokens=8192,
        reasoning_effort=reasoning_effort,
    )

    return _parse_stage2_response(response, paper_text)


def _parse_stage2_response(
    response: str,
    paper_text: str,
) -> list[Perturbation]:
    """Parse Stage 2 response, validating via fuzzy match."""
    arr_match = re.search(r"\[.*\]", response, re.DOTALL)
    if not arr_match:
        return []

    try:
        items = json.loads(arr_match.group(0))
    except json.JSONDecodeError:
        return []

    perturbations = []
    for i, item in enumerate(items):
        original = item.get("original", "")
        perturbed = item.get("perturbed", "")
        if not original or not perturbed or original == perturbed:
            continue

        # Try exact match first
        if original in paper_text:
            matched_text = original
        else:
            # Fuzzy match: find the best match in the paper
            matched_text = _fuzzy_find(original, paper_text)
            if not matched_text:
                print(f"    Dropped (no match): {original[:60]}...")
                continue

        try:
            category = ErrorCategory(item.get("category", ""))
        except ValueError:
            continue

        try:
            difficulty = Difficulty(item.get("difficulty", "local"))
        except ValueError:
            difficulty = Difficulty.LOCAL

        perturbations.append(Perturbation(
            perturbation_id=f"F{i:03d}_free",
            span_id=f"FREE_{i:03d}",
            category=category,
            original=matched_text,  # the VALIDATED exact text
            perturbed=perturbed,
            why_wrong=item.get("why_wrong", ""),
            difficulty=difficulty,
        ))

    print(f"    -> {len(perturbations)} validated proposals")
    return perturbations


def _fuzzy_find(
    approximate: str,
    text: str,
    threshold: float = 0.85,
    window_factor: int = 2,
) -> str | None:
    """Find the best fuzzy match for approximate text within the document.

    Slides a window of similar length across the text and returns the
    best match above threshold, or None.
    """
    approx_len = len(approximate)
    if approx_len < 10:
        return None

    best_ratio = 0.0
    best_text = None
    window = approx_len * window_factor
    step = max(1, approx_len // 4)

    for start in range(0, len(text) - approx_len + 1, step):
        # Try windows of varying size around the approximate length
        for size_mult in [1.0, 0.8, 1.2]:
            size = int(approx_len * size_mult)
            end = min(start + size, len(text))
            candidate = text[start:end]

            ratio = SequenceMatcher(None, approximate, candidate).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_text = candidate

    if best_ratio >= threshold:
        return best_text
    return None
