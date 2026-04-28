"""LLM-based error generation from candidate spans.
"""

import json

from reviewer.client import chat
from .models import (
    CandidateSpan,
    Error,
    Perturbation,
)

errors = [
    Error.NUMERIC_PARAMETER,
    Error.OPERATOR_OR_SIGN,
    Error.INDEX_OR_SUBSCRIPT,
    Error.COMPUTATION,

    Error.INCORRECT_CLAIM,

    Error.MISSING_CASE,
    Error.INDUCTION,
    Error.CIRCULAR_REASONING,
    Error.INVALID_IMPLICATION,

    Error.MISINTERP,
    Error.CAUSAL_REVERSED,
    Error.P_HACKING
]

surface_errors = [
    Error.NUMERIC_PARAMETER,
    Error.OPERATOR_OR_SIGN,
    Error.INDEX_OR_SUBSCRIPT,
    Error.COMPUTATION
]

claim_errors = [
    Error.INCORRECT_CLAIM
]

logic_errors = [
    Error.MISSING_CASE,
    Error.INDUCTION,
    Error.CIRCULAR_REASONING,
    Error.INVALID_IMPLICATION
]

experimental_errors = [
    Error.MISINTERP,
    Error.CAUSAL_REVERSED,
    Error.P_HACKING
]

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

FIELD_PROMPT = r"""
This is the abstract of an academic paper: 
{abstract}

Identify its main field of study and return ONLY 1-5 words. 
"""

PROMPT = r"""
You are creating seeded errors for an academic paper in the field of {field} to benchmark LLM reviewers.

Choose from the following perturbation CANDIDATES:
{candidates_json}

If "error_type" is "surface", generate ONE compatible perturbation:
- numeric_parameter: change a numeric constant (e.g. 0.5 → 0.25, n=10 → n=100)
- operator_or_sign: flip an operator or sign (e.g. + → -, ≤ → ≥, ∪ → ∩)                                               
- index_or_subscript: change a subscript/superscript (e.g. x_i → x_{{i+1}})                                           
- computation: introduce an arithmetic error in a derivation step

If "error_type" is "claim", generate ONE compatible perturbation:
- incorrect_claim: corrupt the statement subtly (wrong condition, wrong quantifier, wrong bound

If "error_type" is "logic", generate ONE compatible perturbation:
- missing_case: remove one case from case analysis, or corrupt the base case in an induction
- induction: make the inductive step invalid                                                                          
- circular_reasoning: use the theorem being proved as a step in its own proof
- invalid_implication: reverse or invalidate a key logical implication

If "error_type" is "experimental", you may generate MULTIPLE perturbations as long as they are DISJOINT:
- misinterp: misinterpret a p-value or confidence interval
- causal_reversed: flip a causal claim (X causes Y → Y causes X)                                                      
- p_hacking: remove or negate a multiple testing correction (Bonferroni, FDR, etc.) 

OUTPUT FORMAT:
For each perturbation, return:
- span_id: the candidate's span_id (copy exactly)
- error: the corresponding error from {errors}
- perturbed: modified LaTeX text (must differ from original)
- why_wrong: a short explanation of how the error can be detected using ONLY the paper

Return ONLY a JSON array of perturbation objects. No commentary.

STRICT REQUIREMENTS:
- The perturbed text must be valid LaTeX
- The error must be verifiable from the paper text alone (no external knowledge)
"""

# ---------------------------------------------------------------------------
# Generate perturbations:
# ---------------------------------------------------------------------------

def identify_field(abstract, model: str = "anthropic/claude-opus-4-6", reasoning_effort: str | None = None):
    formatted_prompt = FIELD_PROMPT.format(
        abstract=abstract,
    )

    response, usage = chat(
        messages=[{"role": "user", "content": FIELD_PROMPT}],
        model=model,
        max_tokens=8192,
        reasoning_effort=reasoning_effort,
    )
    
    return response.strip().lower()

def generate_perturbations(abstract,
                           candidates: list[CandidateSpan],
                           model: str = "anthropic/claude-opus-4-6",
                           reasoning_effort: str | None = None) -> list[Perturbation]:
    # Build candidate JSON for the prompt
    candidates_json = json.dumps([
        {
            "span_id": c.span_id,
            "text": c.text,
            "context": c.context,
            "error_type": c.error_type,
            "compatible_errors": [error.value for error in c.compatible_errors],
        }
        for c in candidates
    ], indent=2)

    formatted_prompt = PROMPT.format(
        field=identify_field(abstract),
        candidates_json=candidates_json,
        errors=", ".join(c.value for c in errors),
    )

    print(f"  {len(candidates)} candidates...")

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
            offset=span.offset,  # from OUR store, not the model's
            perturbed=perturbed,
            why_wrong=item.get("why_wrong", ""),
        ))

    return perturbations