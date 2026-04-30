"""LLM-based error generation from candidate spans.
"""

import json
import re

from reviewer.client import chat
from .models import (
    CandidateSpan,
    Error,
    Perturbation,
)

_BATCH_SIZE = 10

errors_theoretical = [
    Error.NUMERIC_PARAMETER,
    Error.OPERATOR_OR_SIGN,
    Error.INDEX_OR_SUBSCRIPT,
    Error.COMPUTATION,

    Error.INCORRECT_CLAIM_THEORETICAL,

    Error.MISSING_CASE,
    Error.INDUCTION,
    Error.CIRCULAR_REASONING,
    Error.INVALID_IMPLICATION
]

errors_empirical = [
    Error.NUMERIC_PARAMETER,
    Error.OPERATOR_OR_SIGN,
    Error.INDEX_OR_SUBSCRIPT,
    Error.COMPUTATION,

    Error.INCORRECT_STATEMENT_EMPIRICAL,

    Error.MISINTERP,
    Error.CAUSAL_REVERSED,
    Error.P_HACKING
]

errors_surface = [
    Error.NUMERIC_PARAMETER,
    Error.OPERATOR_OR_SIGN,
    Error.INDEX_OR_SUBSCRIPT,
    Error.COMPUTATION
]

errors_claim_theoretical = [
    Error.INCORRECT_CLAIM_THEORETICAL
]

errors_logic = [
    Error.MISSING_CASE,
    Error.INDUCTION,
    Error.CIRCULAR_REASONING,
    Error.INVALID_IMPLICATION
]

errors_statement_empirical = [
    Error.INCORRECT_STATEMENT_EMPIRICAL
] 

errors_experimental = [
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

DOMAIN_PROMPT = r"""
This is the abstract of an academic paper in {field}:
{abstract}

What are the 5 most realistic and detectable errors an author could make in this kind of paper?

Return a JSON array of 5 strings, each describing one error type concisely.

Example format:
["error type one", "error type two", "error type three", "error type four", "error type five"]

Return ONLY the JSON array. No markdown, no explanation.
"""

PROMPT = r"""
You are generating MEANINGFUL perturbations for an academic paper in the field of {field} to benchmark LLM reviewers.

While generating perturbations, consider the following possible errors:
{domain_specific}

Aim for {n_target} perturbations. 

Choose from the following perturbation CANDIDATES:
{candidates_json}

{valid_errors}

Before finalizing each perturbation, verify that the introduced error is meaningful. 

OUTPUT FORMAT:
For each perturbation, return:
- span_id: the candidate's span_id (copy exactly)
- error: the corresponding error type from {error_types}
- perturbed: modified LaTeX text (must differ from original)
- why_wrong: a short explanation of how the error can be detected using ONLY the paper
- contradicts_quote: OPTIONAL. If a verbatim sentence/clause from elsewhere in the paper directly contradicts the perturbation, copy it here. Otherwise omit or set to "". Do NOT fabricate quotes that aren't literally in the paper.

Return ONLY a JSON array of perturbation objects. No commentary.
Example: [{{"span_id": "...", "error": "...", "perturbed": "...", "why_wrong": "...", "contradicts_quote": "..."}}]

STRICT REQUIREMENTS:
- The perturbed text must be valid LaTeX
- The error must be verifiable from the paper text alone (no external knowledge)
"""

SURFACE_ERRORS = r"""
For each candidate, generate ONE compatible perturbation:
- numeric_parameter: change a numeric constant (e.g. 0.5 becomes 0.25, n=10 becomes n=100)
- operator_or_sign: flip an operator or sign (e.g. + becomes -, ≤ becomes ≥)                                               
- index_or_subscript: change a subscript/superscript (e.g. x_i becomes x_{{i+1}})                                           
- computation: introduce an arithmetic error in a derivation step
"""

CLAIM_THEORETICAL_ERRORS = r"""
For each candidate, generate ONE compatible perturbation:
- incorrect_claim_theoretical: introduce a SUBSTANTIAL error that corrupts the validity of the claim

AVOID surface-level errors.
"""

LOGIC_ERRORS = r"""
For each candidate, generate ONE compatible perturbation:
- missing_case: remove one case from case analysis
- induction: incorrect base case or inductive step                                                                      
- circular_reasoning: use the theorem being proved as a step in its own proof
- invalid_implication: reverse or invalidate a key logical implication
"""

STATEMENT_EMPIRICAL_ERRORS = r"""
For each candidate, generate ONE compatible perturbation:
- incorrect_statement_empirical: introduce a SUBSTANTIAL error that corrupts the validity of the statement

AVOID surface-level errors.
"""

EXPERIMENTAL_ERRORS = r"""
For each candidate, generate ONE compatible perturbation:
- misinterp: misinterpret a result (e.g. p-value or confidence interval)
- causal_reversed: flip a causal claim (X causes Y becomes Y causes X)                                                      
- p_hacking: introduce a methodological flaw that constitutes p-hacking (e.g. remove or negate a multiple testing correction, change the stopping rule, 
selectively report only the significant outcome from a set of tested hypotheses)
"""

THEORETICAL_ERRORS = r"""
For each candidate: 
If "error_type" is "surface", generate ONE compatible perturbation:
- numeric_parameter: change a numeric constant (e.g. 0.5 becomes 0.25, n=10 becomes n=100)
- operator_or_sign: flip an operator or sign (e.g. + becomes -, ≤ becomes ≥)                                               
- index_or_subscript: change a subscript/superscript (e.g. x_i becomes x_{{i+1}})                                           
- computation: introduce an arithmetic error in a derivation step

If "error_type" is "claim_theoretical", generate ONE compatible perturbation:
- incorrect_claim: corrupt the statement subtly (e.g. wrong condition, wrong quantifier, wrong bound, wrong constant, wrong sign, wrong index/subscript)

If "error_type" is "logic", generate ONE compatible perturbation (in order from most to least important):
- missing_case: remove one case from case analysis
- induction: incorrect base case or inductive step                                                                      
- circular_reasoning: use the theorem being proved as a step in its own proof
- invalid_implication: reverse or invalidate a key logical implication
"""

EMPIRICAL_ERRORS = r"""
For each candidate: 
If "error_type" is "surface", generate ONE compatible perturbation:
- numeric_parameter: change a numeric constant (e.g. 0.5 becomes 0.25, n=10 becomes n=100)
- operator_or_sign: flip an operator or sign (e.g. + becomes -, ≤ becomes ≥)                                               
- index_or_subscript: change a subscript/superscript (e.g. x_i becomes x_{{i+1}})                                           
- computation: introduce an arithmetic error in a derivation step

If "error_type" is "statement_empirical", generate ONE compatible perturbation:
- incorrect_claim: corrupt the statement so it is factually incorrect

If "error_type" is "experimental", generate ONE compatible perturbation (in order from most to least important):
- misinterp: misinterpret a result (e.g. p-value or confidence interval)
- causal_reversed: flip a causal claim (X causes Y becomes Y causes X)                                                      
- p_hacking: introduce a methodological flaw that constitutes p-hacking (e.g. remove or negate a multiple testing correction, change the stopping rule, 
selectively report only the significant outcome from a set of tested hypotheses)
"""
# ---------------------------------------------------------------------------
# Generate perturbations:
# ---------------------------------------------------------------------------

def identify_field(abstract, model: str = "anthropic/claude-opus-4-6", reasoning_effort: str | None = None):
    formatted_prompt = FIELD_PROMPT.format(
        abstract=abstract,
    )

    response, usage = chat(
        messages=[{"role": "user", "content": formatted_prompt}],
        model=model,
        max_tokens=8192,
        reasoning_effort=reasoning_effort,
    )
    
    return response.strip().lower()

def domain_specific_errors(field, abstract, model: str = "anthropic/claude-opus-4-6", reasoning_effort: str | None = None):
    formatted_prompt = DOMAIN_PROMPT.format(
        field=field,
        abstract=abstract,
    )

    response, usage = chat(
        messages=[{"role": "user", "content": formatted_prompt}],
        model=model,
        max_tokens=8192,
        reasoning_effort=reasoning_effort,
    )

    cleaned = re.sub(r"^```[a-z]*\n?|\n?```$", "", response.strip(), flags=re.MULTILINE)
    try:
        items = json.loads(cleaned)
    except json.JSONDecodeError:
        cleaned = re.sub(r'\\(?!["\\/bfnrtu])', '', cleaned)
        items = json.loads(cleaned)
    return ", ".join(str(x) for x in items)

def generate_perturbations(category,
                           error_type,
                           n_total, 
                           abstract,
                           candidates: list[CandidateSpan],
                           model: str = "anthropic/claude-opus-4-6",
                           reasoning_effort: str | None = None) -> list[Perturbation]:
    field = identify_field(abstract, model=model, reasoning_effort=reasoning_effort)
    domain_specific = domain_specific_errors(field, abstract, model=model, reasoning_effort=reasoning_effort)

    if category == "theoretical":
        if error_type == "all":
            valid_errors = THEORETICAL_ERRORS
            errors_str = ", ".join(c.value for c in errors_theoretical)
        elif error_type == "surface":
            valid_errors = SURFACE_ERRORS
            errors_str = ", ".join(c.value for c in errors_surface)
        elif error_type == "claim_theoretical":
            valid_errors = CLAIM_THEORETICAL_ERRORS
            errors_str = ", ".join(c.value for c in errors_claim_theoretical)
        elif error_type == "logic":
            valid_errors = LOGIC_ERRORS
            errors_str = ", ".join(c.value for c in errors_logic)
    elif category == "empirical":
        if error_type == "all":
            valid_errors = EMPIRICAL_ERRORS
            errors_str = ", ".join(c.value for c in errors_empirical)
        elif error_type == "surface":
            valid_errors = SURFACE_ERRORS
            errors_str = ", ".join(c.value for c in errors_surface)
        elif error_type == "statement_empirical":
            valid_errors = STATEMENT_EMPIRICAL_ERRORS
            errors_str = ", ".join(c.value for c in errors_statement_empirical)
        elif error_type == "experimental":
            valid_errors = EXPERIMENTAL_ERRORS
            errors_str = ", ".join(c.value for c in errors_experimental)

    batches = [candidates[i:i + _BATCH_SIZE] for i in range(0, len(candidates), _BATCH_SIZE)]
    print(f"  {len(candidates)} candidates in {len(batches)} batches of {_BATCH_SIZE}...")

    all_perturbations: list[Perturbation] = []
    for batch_idx, batch in enumerate(batches):
        candidates_json = json.dumps([
            {
                "span_id": c.span_id,
                "text": c.text,
                "context": c.context,
                "error_type": c.error_type,
                "compatible_errors": [error.value for error in c.compatible_errors],
            }
            for c in batch
        ], indent=2)

        formatted_prompt = PROMPT.format(
            field=field,
            domain_specific=domain_specific,
            n_target=2 * n_total // len(batches), # double to have generation buffer 
            candidates_json=candidates_json,
            valid_errors=valid_errors,
            error_types=errors_str,
        )

        response, usage = chat(
            messages=[{"role": "user", "content": formatted_prompt}],
            model=model,
            max_tokens=16384,
            reasoning_effort=reasoning_effort,
        )

        batch_result = _parse_response(response, batch)
        print(f"    batch {batch_idx + 1}/{len(batches)}: {len(batch_result)} perturbations")
        all_perturbations.extend(batch_result)

    print(f"  -> {len(all_perturbations)} total perturbations")
    return all_perturbations

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
        if not isinstance(item, dict):
            continue
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
            original=span.text,
            offset=span.offset,  # from OUR store, not the model's
            perturbed=perturbed,
            why_wrong=item.get("why_wrong", ""),
            contradicts_quote=item.get("contradicts_quote", "") or "",
        ))

    return perturbations
