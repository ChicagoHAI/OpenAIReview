"""LLM-based error generation from candidate spans.

Type 1: Surface 
Type 2: Formal 
"""

import json

from reviewer.client import chat
from .models import (
    CandidateSpan,
    Error,
    Perturbation,
)

surface_errors = [
    Error.OPERATOR_OR_SIGN,
    Error.SYMBOL_BINDING,
    Error.INDEX_OR_SUBSCRIPT,
    Error.NUMERIC_PARAMETER,
]

formal_errors = [
    Error.DEF_WRONG,
    Error.THM_WRONG_CONDITION,
    Error.THM_WRONG_CONCLUSION,
    Error.THM_WRONG_SCOPE,
    Error.PROOF_WRONG_DIRECTION,
    Error.PROOF_MISSING_CASE,
    Error.PROOF_WRONG_ASSUMPTION,
    Error.PROOF_MISMATCH
]

"""Given candidate spans from a paper, select spans and introduce a single minimal error
per span. Errors should be subtle enough that a careful reviewer could catch them,
but not so obvious they are immediately apparent."""

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

SURFACE_PROMPT = r"""
You are creating seeded errors in academic math papers to benchmark LLM reviewers.

Generate {n_per_error} perturbations for each of the following (if possible):
- operator_or_sign: flip an operator or sign (e.g. + becomes -, \leq becomes \geq, \cup becomes \cap)
- symbol_binding: replace a symbol with a similar but wrong one (e.g. \alpha becomes \beta, \mu becomes \sigma)
- index_or_subscript: change a subscript or superscript (e.g. x_i becomes x_{{i+1}}, A^n becomes A^{{n-1}})
- numeric_parameter: change a numeric value (e.g. 0.5 becomes 0.25, n=100 becomes n=200)

RULES:
- Make exactly one change per perturbation (minimal edit)
- The perturbed text must be valid LaTeX
- The error must be detectable from the paper text alone (no external knowledge needed)

CANDIDATES:
{candidates_json}

For each perturbation, return:
- span_id: which candidate to perturb
- error: one of {errors}
- perturbed: the replacement text (must differ from original)
- why_wrong: how a reader can verify this is wrong using only the paper

Return ONLY a JSON array of perturbation objects. No commentary.
"""

FORMAL_PROMPT = r"""
You are creating seeded errors in academic math papers to benchmark LLM reviewers.

Generate {n_per_error} perturbations for each of the following (if possible):
- def_wrong: corrupt a definition so it no longer captures the intended object (e.g. wrong condition, wrong formula, wrong bound)
- thm_wrong_condition: weaken, strengthen, or change a condition so the theorem no longer holds as stated
- thm_wrong_conclusion: alter the conclusion so it is stronger than what the proof supports
- thm_wrong_scope: change a quantifier or domain so the theorem applies in the wrong scope (e.g. "for all" becomes "there exists", or the domain changes)
- proof_wrong_direction: reverse an implication in a key step (e.g. prove A becomes B instead B becomes A as needed)
- proof_missing_case: drop one case from a case analysis or induction step, making the proof incomplete
- proof_wrong_assumption: introduce or substitute a wrong assumption in the proof (e.g. use a stronger property than what was proven)
- proof_mismatch: make a step prove a statement that is subtly different from the theorem being claimed

RULES:
- Make exactly one change per perturbation (minimal edit)
- The perturbed text must be valid LaTeX
- The error must be detectable from the paper text alone — cite the specific line or equation in why_wrong

CANDIDATES:
{candidates_json}

For each perturbation, return:
- span_id: which candidate to perturb
- error: one of {errors}
- perturbed: the replacement text (must differ from original, valid LaTeX)
- why_wrong: how a reader can verify this is wrong using only the paper (reference the specific inconsistency)

Return ONLY a JSON array of perturbation objects. No commentary.
"""

# ---------------------------------------------------------------------------
# Generate perturbations by error type:
# ---------------------------------------------------------------------------

def generate_perturbations_by_type(error_type: str, 
                                   candidates: list[CandidateSpan],
                                   model: str = "anthropic/claude-opus-4-6",
                                   n_per_error: int = 2,
                                   reasoning_effort: str | None = None) -> list[Perturbation]:
    # get prompt
    if error_type == "surface":
        errors = surface_errors
        prompt = SURFACE_PROMPT
    elif error_type == "formal":
        errors = formal_errors
        prompt = FORMAL_PROMPT
    else:
        pass 

    # Build candidate JSON for the prompt
    candidates_json = json.dumps([
        {
            "span_id": c.span_id,
            "type": c.span_type.value,
            "text": c.text,
            "context": c.context,
            "error_type": c.error_type,
            "compatible_errors": [error.value for error in c.compatible_errors],
        }
        for c in candidates
    ], indent=2)

    formatted_prompt = prompt.format(
        n_per_error=n_per_error,
        candidates_json=candidates_json,
        errors=", ".join(c.value for c in errors),
    )

    print(f"  {error_type}: {len(candidates)} candidates...")

    response, usage = chat(
        messages=[{"role": "user", "content": formatted_prompt}],
        model=model,
        max_tokens=8192,
        reasoning_effort=reasoning_effort,
    )

    perturbations = _parse_response(response, candidates)
    print(f"    -> {len(perturbations)} perturbations")

    return perturbations

# ---------------------------------------------------------------------------
# Generate all perturbations:
# ---------------------------------------------------------------------------

def generate_perturbations(candidates: list[CandidateSpan],
                                model: str = "anthropic/claude-opus-4-6",
                                n_per_error: int = 2,
                                reasoning_effort: str | None = None,
                                error_type: str = "surface"):
    candidates_surface = [candidate for candidate in candidates if candidate.error_type == "surface"]
    candidates_formal = [candidate for candidate in candidates if candidate.error_type == "formal"]

    perturbations = []
    if error_type == "surface" or error_type == "all":
        surface = generate_perturbations_by_type("surface", candidates_surface, model, n_per_error, reasoning_effort)
        perturbations.extend(surface)
    if error_type == "formal" or error_type == "all":
        formal = generate_perturbations_by_type("formal", candidates_formal, model, n_per_error, reasoning_effort)
        perturbations.extend(formal)

    return perturbations

# ---------------------------------------------------------------------------
# Helpers:
# ---------------------------------------------------------------------------

def _parse_response(response: str,
                    candidates: list[CandidateSpan]) -> list[Perturbation]:
    span_lookup = {c.span_id: c for c in candidates}

    # Find all valid JSON arrays in the response using the JSON decoder directly.
    # This handles nested brackets, LaTeX, and self-corrections correctly.
    # We take the last non-empty list found (model may self-correct mid-response).
    decoder = json.JSONDecoder()
    found = []
    i = 0
    while i < len(response):
        if response[i] == "[":
            try:
                obj, end = decoder.raw_decode(response, i)
                if isinstance(obj, list) and obj:
                    found.append(obj)
                i = end
            except json.JSONDecodeError:
                i += 1
        else:
            i += 1

    if not found:
        return []
    items = found[-1]

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
            error = Error(item.get("error", ""))
        except ValueError:
            continue

        perturbations.append(Perturbation(
            perturbation_id=f"P{i:03d}_{span_id}",
            span_id=span_id,
            error=error,
            original=span.text,  # from OUR store, not the model's
            perturbed=perturbed,
            why_wrong=item.get("why_wrong", ""),
        ))

    return perturbations