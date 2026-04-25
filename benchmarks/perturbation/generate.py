"""LLM-based error generation from candidate spans.

Type 1: Surface
Type 2: Formal
"""

import json

from reviewer.client import chat
from reviewer.utils import count_tokens
from .models import (
    CandidateSpan,
    Error,
    Perturbation,
)

surface_errors = [
    Error.OPERATOR_OR_SIGN,
    Error.INDEX_OR_SUBSCRIPT,
    Error.NUMERIC_PARAMETER,
    # Error.SYMBOL_BINDING intentionally omitted: bare symbol swaps are structurally
    # typo-shaped — readers auto-correct them. See verifier_eval notes.
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

PROMPT_ROLE = r"""
You are creating SUBSTANTIVE, DETECTABLE errors in academic math papers to benchmark LLM reviewers.
"""

NEUTRAL_PROMPT_ROLE = r"""
You are creating seeded errors in academic math papers to benchmark LLM reviewers.
"""

PROMPT_FOOTER = r"""

No commentary.

CANDIDATES:
{candidates_json}
"""

SURFACE_SUBSTANTIVE_GUIDANCE = r"""

# What counts as substantive (vs. typo-shaped)

A TYPO-SHAPED error is a surface slip a reader fixes in their head on the next line — e.g.,
one isolated sign flip, a lone symbol swap in an equation that's never referenced again, a
numeric value stated once and never used. Do NOT produce these.

A SUBSTANTIVE error is a semantic swap whose contradiction lives in a DOWNSTREAM REFERENCE
elsewhere in the paper: the perturbed text still parses cleanly, but it disagrees with a
later definition, claim, theorem application, or plug-in of numeric values. Catching it
requires the reader to connect two parts of the paper, not just to notice a glitch.

GOOD examples:
- operator_or_sign: flip a theorem's inequality direction (≤ → ≥) or quantifier (∀ → ∃)
  when a later corollary or proof step quoted elsewhere relies on the original direction.
- index_or_subscript: shift a time/layer/batch index in a recurrence (e.g., h_t = f(W h_{{t-1}} + U x_t)
  → h_t = f(W h_{{t-1}} + U x_{{t-1}})) where another passage explicitly describes the model
  as consuming the CURRENT input x_t.
- numeric_parameter: change a load-bearing constant in a bound or assumption (e.g., a
  sample-complexity bound n ≥ 4d/ε² → n ≥ 4d/ε) where a later passage plugs in specific
  values whose scaling then contradicts the stated regime.

BAD (typo-shaped) examples to AVOID:
- Flipping a sign in a standalone equation with no downstream reference.
- Renaming x_i → x_j in an expression where the index plays no role elsewhere.
- Changing 0.5 → 0.25 in a parameter stated once and never plugged into a claim.
- Bare symbol swaps (α → γ, β_k → φ_k) — readers auto-correct these; they are
  structurally typo-shaped regardless of context.
"""

SURFACE_INPUTS = r"""

# Inputs

You will see a list of candidate spans. Each candidate has:
- span_id
- text (the span)
- context (local text around the span)
- related_passages (passages from ELSEWHERE in the paper that mention the same symbols/names
  as the span; may be empty)
- compatible_errors (which of the four error types can apply to this span)
"""

SURFACE_STRATEGY_REQUIRED_QUOTE = r"""

# Strategy

1. PREFER candidates whose related_passages contain a concrete downstream use of the
   perturbed quantity/symbol. If related_passages is empty for a candidate, it is much
   harder to produce a substantive perturbation — skip it unless the context alone clearly
   encodes the contradiction.
2. Pick exactly one error type per candidate from its compatible_errors.
3. Write the perturbed text (valid LaTeX, minimal single edit).
4. Copy the EXACT VERBATIM quote from related_passages (or context) that your perturbation
   contradicts into `contradicts_quote`. No paraphrasing, no ellipses.
5. In `why_wrong`, name the contradiction in one sentence, referring to the quote.
"""

SURFACE_CONTEXT_OPTIONAL_QUOTE = r"""

You may or may not have surrounding context for each span. Do your best with what's given:
- If a candidate has NO `context` and NO `related_passages`, just produce a plausible
  minimal edit that looks like a substantive semantic error rather than a typo-shaped slip.
- If a candidate has a `context` field (a local slice of the paper), use it to choose a
  more meaningful edit with a locally visible contradiction if possible.
- If a candidate has `related_passages`, prefer candidates whose passages hint at a
  downstream reference to the perturbed quantity/symbol.
"""

SURFACE_CONTEXT_OPTIONAL_QUOTE_NEUTRAL = r"""

You may or may not have surrounding context for each span. Do your best with what's given:
- If a candidate has NO `context` and NO `related_passages`, just produce a plausible
  minimal edit that looks like an error.
- If a candidate has a `context` field (a local slice of the paper), use it to choose a
  more meaningful edit.
- If a candidate has `related_passages`, prefer candidates whose passages hint at a
  downstream reference to the perturbed quantity/symbol.
"""

SURFACE_TASK = r"""

# Task

Select a subset of candidates and generate EXACTLY {n_per_error} perturbations for EACH of
the following errors:
- operator_or_sign: flip an operator, sign, or quantifier (e.g. + ↔ -, ≤ ↔ ≥, ∀ ↔ ∃)
- index_or_subscript: shift an index (e.g. x_t ↔ x_{{t-1}})
- numeric_parameter: change a numeric value (e.g. 0.5 ↔ 0.25)

You should end up with exactly {n_total} perturbations total.
"""

SURFACE_STRICT_COMMON = r"""

# Strict requirements

- Do NOT generate more than ONE perturbation per candidate.
- The perturbed text must be valid LaTeX and differ from the original.
"""

SURFACE_STRICT_REQUIRED_QUOTE = r"""
- `contradicts_quote` must be a copy-paste substring of the paper (drawn from
  related_passages or context). If you cannot produce one, SKIP the candidate — emit fewer
  high-quality perturbations rather than fabricate.
- The contradiction must be verifiable from the paper alone (no external knowledge).
"""

SURFACE_STRICT_OPTIONAL_QUOTE = r"""
- Make a minimal, single edit per perturbation.
"""

SURFACE_OUTPUT_REQUIRED_QUOTE = r"""

# Output format

Return ONLY a JSON array of objects with fields:
- span_id: str (copy exactly from the candidate)
- error: one of {errors}
- perturbed: str (valid LaTeX, minimal edit)
- contradicts_quote: str (exact verbatim quote from elsewhere in the paper)
- why_wrong: str — ONE short sentence a non-expert reader could follow, in this exact
  three-part shape: "Original says <X>. Perturbed now says <Y>. This is wrong because
  <concrete reason citing the quote>." Use plain language; avoid jargon like "downstream
  reference", "semantic swap", "load-bearing". The point is for a human auditor to judge
  the perturbation without having to read the paper.
"""

SURFACE_OUTPUT_OPTIONAL_QUOTE = r"""

# Output format

Return ONLY a JSON array of objects with fields:
- span_id: str (copy exactly from the candidate)
- error: one of {errors}
- perturbed: str (valid LaTeX, minimal edit)
- why_wrong: str — ONE short sentence a non-expert reader could follow, in this exact
  three-part shape: "Original says <X>. Perturbed now says <Y>. This is wrong because
  <concrete reason; cite the quote if one is present>." Use plain language; avoid jargon
  like "downstream reference", "semantic swap", "load-bearing". The point is for a human
  auditor to judge the perturbation without having to read the paper.
- contradicts_quote: str — OPTIONAL. If the provided `context` or `related_passages`
  contains a verbatim sentence/clause that the perturbation contradicts, copy it exactly
  here. Otherwise, omit this field or set it to the empty string. Do NOT fabricate a
  quote that isn't literally present in the inputs.
"""

SURFACE_PROMPT = (
    PROMPT_ROLE
    + SURFACE_SUBSTANTIVE_GUIDANCE
    + SURFACE_INPUTS
    + SURFACE_STRATEGY_REQUIRED_QUOTE
    + SURFACE_TASK
    + SURFACE_STRICT_COMMON
    + SURFACE_STRICT_REQUIRED_QUOTE
    + SURFACE_OUTPUT_REQUIRED_QUOTE
    + PROMPT_FOOTER
)

SURFACE_PROMPT_OPTIONAL_QUOTE = (
    PROMPT_ROLE
    + SURFACE_SUBSTANTIVE_GUIDANCE
    + SURFACE_CONTEXT_OPTIONAL_QUOTE
    + SURFACE_TASK
    + SURFACE_STRICT_COMMON
    + SURFACE_STRICT_OPTIONAL_QUOTE
    + SURFACE_OUTPUT_OPTIONAL_QUOTE
    + PROMPT_FOOTER
)

SURFACE_PROMPT_NO_GUIDANCE = (
    NEUTRAL_PROMPT_ROLE
    + SURFACE_INPUTS
    + SURFACE_STRATEGY_REQUIRED_QUOTE
    + SURFACE_TASK
    + SURFACE_STRICT_COMMON
    + SURFACE_STRICT_REQUIRED_QUOTE
    + SURFACE_OUTPUT_REQUIRED_QUOTE
    + PROMPT_FOOTER
)

SURFACE_PROMPT_OPTIONAL_QUOTE_NO_GUIDANCE = (
    NEUTRAL_PROMPT_ROLE
    + SURFACE_CONTEXT_OPTIONAL_QUOTE_NEUTRAL
    + SURFACE_TASK
    + SURFACE_STRICT_COMMON
    + SURFACE_STRICT_OPTIONAL_QUOTE
    + SURFACE_OUTPUT_OPTIONAL_QUOTE
    + PROMPT_FOOTER
)

FORMAL_SUBSTANTIVE_GUIDANCE = r"""

# What counts as substantive (vs. typo-shaped)

A TYPO-SHAPED error is a local slip the reader fixes in their head. Do NOT produce these.

A SUBSTANTIVE error is a semantic change to a definition, theorem, or proof whose
contradiction lives in a DOWNSTREAM REFERENCE elsewhere in the paper — a later invocation
of the definition, an application of the theorem, or a proof step that would no longer go
through as written.

GOOD examples:
- def_wrong: weaken or rewrite a condition in a definition so that a later application of
  that definition (quoted elsewhere) no longer satisfies what is claimed there.
- thm_wrong_condition / thm_wrong_scope: change "for all" to "there exists", or weaken a
  condition, where a later corollary or application assumes the original form.
- thm_wrong_conclusion: strengthen the conclusion beyond what the proof actually supports,
  where the proof body (quoted elsewhere) only justifies the weaker claim.
- proof_wrong_direction / proof_wrong_assumption / proof_mismatch: change a direction of
  implication or substitute a wrong assumption whose contradiction is visible because the
  theorem statement (quoted elsewhere) requires the original direction/assumption.
- proof_missing_case: drop a case from a case analysis where the induction hypothesis or
  theorem condition (quoted elsewhere) explicitly requires all cases.
"""

FORMAL_INPUTS = r"""

# Inputs

You will see a list of candidate spans. Each candidate has:
- span_id
- text (the span)
- context (local text around the span)
- related_passages (passages from ELSEWHERE in the paper that mention the same symbols/names
  as the span; may be empty)
- compatible_errors (which formal error types apply to this span)
"""

FORMAL_STRATEGY_REQUIRED_QUOTE = r"""

# Strategy

1. PREFER candidates whose related_passages contain an invocation/application of the
   definition or theorem being perturbed. If related_passages is empty, skip unless the
   context alone contains the contradicting passage.
2. Pick exactly one error type per candidate from its compatible_errors.
3. Write the perturbed text (valid LaTeX, minimal single edit).
4. Copy the EXACT VERBATIM quote (from related_passages or context) that your perturbation
   contradicts into `contradicts_quote`. No paraphrasing.
5. In `why_wrong`, name the contradiction in one sentence, referring to the quote.
"""

FORMAL_CONTEXT_OPTIONAL_QUOTE = r"""

You may or may not have surrounding context. If a candidate has a `context` or
`related_passages`, use them to ground your edit. Otherwise, produce a plausible minimal
edit that changes the semantics rather than creating a typo-shaped slip.
"""

FORMAL_CONTEXT_OPTIONAL_QUOTE_NEUTRAL = r"""

You may or may not have surrounding context. If a candidate has a `context` or
`related_passages`, use them to ground your edit. Otherwise, produce a plausible minimal
edit.
"""

FORMAL_TASK_REQUIRED_QUOTE = r"""

# Task

Generate {n_per_error} perturbations for each of the following (if possible):
- def_wrong: corrupt a definition so it no longer captures the intended object
- thm_wrong_condition: weaken / strengthen / change a condition so the theorem no longer holds
- thm_wrong_conclusion: alter the conclusion so it is stronger than what the proof supports
- thm_wrong_scope: change a quantifier or domain so the theorem applies in the wrong scope
- proof_wrong_direction: reverse an implication in a key step
- proof_missing_case: drop one case from a case analysis or induction
- proof_wrong_assumption: introduce or substitute a wrong assumption in the proof
- proof_mismatch: make a step prove a statement subtly different from the theorem
"""

FORMAL_TASK_OPTIONAL_QUOTE = r"""

# Task

Generate {n_per_error} perturbations for each of the following (if possible):
- def_wrong, thm_wrong_condition, thm_wrong_conclusion, thm_wrong_scope,
  proof_wrong_direction, proof_missing_case, proof_wrong_assumption, proof_mismatch
"""

FORMAL_STRICT_COMMON = r"""

# Strict requirements

- Exactly one change per perturbation (minimal edit).
- The perturbed text must be valid LaTeX.
"""

FORMAL_STRICT_REQUIRED_QUOTE = r"""
- `contradicts_quote` must be a copy-paste substring of the paper. If you cannot produce
  one, skip the candidate.
- The contradiction must be detectable from the paper alone.
"""

FORMAL_OUTPUT_REQUIRED_QUOTE = r"""

# Output format

Return ONLY a JSON array of objects with fields:
- span_id: str (copy exactly from the candidate)
- error: one of {errors}
- perturbed: str (valid LaTeX, minimal edit)
- contradicts_quote: str (exact verbatim quote from elsewhere in the paper)
- why_wrong: str (one-sentence explanation referencing the quote)
"""

FORMAL_OUTPUT_OPTIONAL_QUOTE = r"""

# Output format

Return ONLY a JSON array of objects with fields:
- span_id: str
- error: one of {errors}
- perturbed: str (valid LaTeX, minimal edit)
- why_wrong: str (short explanation)
- contradicts_quote: str — OPTIONAL. Verbatim copy from `context` or `related_passages`
  if one contradicts the perturbation; otherwise omit or leave empty. Do NOT fabricate.
"""

FORMAL_PROMPT_OPTIONAL_QUOTE = (
    PROMPT_ROLE
    + FORMAL_SUBSTANTIVE_GUIDANCE
    + FORMAL_CONTEXT_OPTIONAL_QUOTE
    + FORMAL_TASK_OPTIONAL_QUOTE
    + FORMAL_STRICT_COMMON
    + FORMAL_OUTPUT_OPTIONAL_QUOTE
    + PROMPT_FOOTER
)

FORMAL_PROMPT = (
    PROMPT_ROLE
    + FORMAL_SUBSTANTIVE_GUIDANCE
    + FORMAL_INPUTS
    + FORMAL_STRATEGY_REQUIRED_QUOTE
    + FORMAL_TASK_REQUIRED_QUOTE
    + FORMAL_STRICT_COMMON
    + FORMAL_STRICT_REQUIRED_QUOTE
    + FORMAL_OUTPUT_REQUIRED_QUOTE
    + PROMPT_FOOTER
)

FORMAL_PROMPT_NO_GUIDANCE = (
    NEUTRAL_PROMPT_ROLE
    + FORMAL_INPUTS
    + FORMAL_STRATEGY_REQUIRED_QUOTE
    + FORMAL_TASK_REQUIRED_QUOTE
    + FORMAL_STRICT_COMMON
    + FORMAL_STRICT_REQUIRED_QUOTE
    + FORMAL_OUTPUT_REQUIRED_QUOTE
    + PROMPT_FOOTER
)

FORMAL_PROMPT_OPTIONAL_QUOTE_NO_GUIDANCE = (
    NEUTRAL_PROMPT_ROLE
    + FORMAL_CONTEXT_OPTIONAL_QUOTE_NEUTRAL
    + FORMAL_TASK_OPTIONAL_QUOTE
    + FORMAL_STRICT_COMMON
    + FORMAL_OUTPUT_OPTIONAL_QUOTE
    + PROMPT_FOOTER
)

# ---------------------------------------------------------------------------
# Generate perturbations by error type:
# ---------------------------------------------------------------------------

def _candidate_to_payload(c: CandidateSpan, context_mode: str) -> dict:
    """Serialize a CandidateSpan into the JSON payload sent to the generator.

    context_mode controls which fields are included:
      "none"    — span_id + text + type + compatible_errors. No context, no passages.
      "window"  — adds the local ±context_window slice.
      "related" — adds the local slice AND related_passages.
    """
    payload = {
        "span_id": c.span_id,
        "type": c.span_type.value,
        "text": c.text,
        "error_type": c.error_type,
        "compatible_errors": [error.value for error in c.compatible_errors],
    }
    if context_mode != "none":
        payload["context"] = c.context
    if context_mode == "related" and c.related_passages:
        payload["related_passages"] = [
            {"offset": rp["offset"], "snippet": rp["snippet"]}
            for rp in c.related_passages
        ]
    return payload


def _prompt_for(
    error_type: str,
    context_mode: str,
    substantive_guidance: bool = True,
) -> tuple[str, list[Error]]:
    """Pick the generator prompt template based on error_type and context_mode.

    Quote is REQUIRED only in `related` mode (where the generator has the full
    downstream passage set to pick from). In `none` and `window` modes, the
    quote is optional — the verifier will sample one from the paper if the
    generator didn't produce one, so all three modes face the same verifier
    input format.

    substantive_guidance toggles whether the prompt explicitly teaches the
    generator the typo-shaped vs substantive-error distinction.
    """
    if context_mode == "related":
        if error_type == "surface":
            return (
                SURFACE_PROMPT if substantive_guidance else SURFACE_PROMPT_NO_GUIDANCE,
                surface_errors,
            )
        if error_type == "formal":
            return (
                FORMAL_PROMPT if substantive_guidance else FORMAL_PROMPT_NO_GUIDANCE,
                formal_errors,
            )
    else:  # "none" or "window" — quote optional
        if error_type == "surface":
            return (
                SURFACE_PROMPT_OPTIONAL_QUOTE
                if substantive_guidance
                else SURFACE_PROMPT_OPTIONAL_QUOTE_NO_GUIDANCE,
                surface_errors,
            )
        if error_type == "formal":
            return (
                FORMAL_PROMPT_OPTIONAL_QUOTE
                if substantive_guidance
                else FORMAL_PROMPT_OPTIONAL_QUOTE_NO_GUIDANCE,
                formal_errors,
            )
    raise ValueError(f"error_type must be 'surface' or 'formal', got {error_type!r}")


def generate_perturbations_by_type(error_type: str,
                                   candidates: list[CandidateSpan],
                                   model: str = "anthropic/claude-opus-4-6",
                                   n_per_error: int = 2,
                                   reasoning_effort: str | None = None,
                                   context_mode: str = "window",
                                   substantive_guidance: bool = True) -> tuple[list[Perturbation], dict]:
    """Generate perturbations for one error_type.

    Returns a tuple (perturbations, stats) where stats carries:
      - prompt_tokens: int (token count of the formatted prompt)
      - n_candidates: int
      - n_candidates_with_related: int (candidates whose related_passages is non-empty,
        i.e., visible to the generator — only relevant in related mode)
    """
    prompt, errors = _prompt_for(error_type, context_mode, substantive_guidance=substantive_guidance)

    # Build candidate JSON for the prompt
    candidates_json = json.dumps(
        [_candidate_to_payload(c, context_mode) for c in candidates],
        indent=2,
    )

    formatted_prompt = prompt.format(
        n_per_error=n_per_error,
        n_total=n_per_error * len(errors),
        candidates_json=candidates_json,
        errors=", ".join(c.value for c in errors),
    )

    prompt_tokens = count_tokens(formatted_prompt)
    n_with_related = sum(1 for c in candidates if c.related_passages)

    print(f"  {error_type}[{context_mode}, guidance={'on' if substantive_guidance else 'off'}]: {len(candidates)} candidates "
          f"({n_with_related} with generator-visible related_passages); "
          f"prompt={prompt_tokens} tokens")

    response, usage = chat(
        messages=[{"role": "user", "content": formatted_prompt}],
        model=model,
        max_tokens=8192,
        reasoning_effort=reasoning_effort,
    )

    perturbations = _parse_response(response, candidates)
    print(f"    -> {len(perturbations)} perturbations")

    stats = {
        "prompt_tokens": prompt_tokens,
        "n_candidates": len(candidates),
        "n_candidates_with_related": n_with_related,
    }
    return perturbations, stats

# ---------------------------------------------------------------------------
# Generate all perturbations:
# ---------------------------------------------------------------------------

def generate_perturbations(candidates: list[CandidateSpan],
                                model: str = "anthropic/claude-opus-4-6",
                                n_per_error: int = 2,
                                reasoning_effort: str | None = None,
                                error_type: str = "surface",
                                return_stats: bool = False,
                                context_mode: str = "window",
                                substantive_guidance: bool = True):
    """Generate perturbations for `candidates`.

    If return_stats is True, returns (perturbations, stats_by_type) where
    stats_by_type is a dict {"surface": {...}, "formal": {...}} populated only
    for the error types actually run.
    """
    by_type: dict[str, list[CandidateSpan]] = {"surface": [], "formal": []}
    for c in candidates:
        if c.error_type in by_type:
            by_type[c.error_type].append(c)

    types_to_run = list(by_type) if error_type == "all" else [error_type]

    perturbations: list[Perturbation] = []
    stats_by_type: dict[str, dict] = {}
    for t in types_to_run:
        perts, stats = generate_perturbations_by_type(
            t, by_type[t], model, n_per_error, reasoning_effort,
            context_mode=context_mode,
            substantive_guidance=substantive_guidance,
        )
        perturbations.extend(perts)
        stats_by_type[t] = stats

    if return_stats:
        return perturbations, stats_by_type
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
            contradicts_quote=item.get("contradicts_quote", ""),
        ))

    return perturbations
