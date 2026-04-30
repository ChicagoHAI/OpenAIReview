"""Per-perturbation substantive-error verifier (validation test #5).

Runs AFTER validate_perturbations has applied its 4 structural checks. For each
surviving perturbation, a strong-model verifier is asked a narrow question:

  Given (original → perturbed), does the cited contradicts_quote — together with
  the perturbation's related passages — establish that this is a substantive,
  detectable error by a careful reader with access to the paper alone?

Three verdicts:
  - "substantive"   → keep
  - "typo-shaped"   → reject (surface slip, fixed in the reader's head)
  - "not-an-error"  → reject (no real contradiction)

The generator sees ALL candidates together and picks a subset. Each verifier
sees ONE perturbation at a time, with only that perturbation's own related
passages — so its verdicts are independent of any cross-candidate reasoning
the generator did.

Verifiers are fanned out via ThreadPoolExecutor. chat() is thread-safe
(stateless underneath) and already handles retries and reasoning-token budget.
"""

import hashlib
import json
import random
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

from reviewer.client import chat

from .models import CandidateSpan, Error, Perturbation


DEFAULT_VERIFIER_MODEL = "anthropic/claude-sonnet-4-6"
DEFAULT_VERIFIER_REASONING = "none"
DEFAULT_MAX_WORKERS = 8

_VALID_VERDICTS = ("substantive", "typo-shaped", "not-an-error")


# Legacy prompt kept so we can run apples-to-apples before/after evals. Do not
# use in the main pipeline — use VERIFIER_PROMPT below.
VERIFIER_PROMPT_LEGACY = r"""
You are verifying whether a seeded error in an academic math paper is SUBSTANTIVE or TYPO-SHAPED.

- A SUBSTANTIVE error changes a claim, theorem, definition, or computation. Its
  contradiction is visible to a careful reader who connects the perturbed span to a specific passage in the paper.
- A TYPO-SHAPED error is a surface slip the reader fixes in their head (e.g., one sign flip in a standalone equation, a symbol swap with no downstream use).
- NOT AN ERROR means the "perturbation" is actually consistent with the paper, or the cited quote does not contradict it.

You are given ONE perturbation to judge, and ONE quote from elsewhere in the paper
({quote_source}). Judge only whether the shown quote and the perturbed span establish a
substantive contradiction. Do NOT speculate about what else the paper might say.

INPUTS:

Error type: {error_type}

Original span (from the paper):
<<<
{original}
>>>

Perturbed span (the seeded error):
<<<
{perturbed}
>>>

Quote from elsewhere in the paper ({quote_source}):
<<<
{quote}
>>>

Generator's why_wrong explanation (may be absent if generator had no context):
<<<
{why_wrong}
>>>

TASK:
Decide whether the perturbation is substantive, typo-shaped, or not-an-error.

Return ONLY a single JSON object (no commentary):
{{"verdict": "substantive" | "typo-shaped" | "not-an-error", "reason": "<one sentence>"}}
"""


VERIFIER_PROMPT = r"""
You are verifying whether a seeded error in an academic math paper is SUBSTANTIVE or TYPO-SHAPED.

A SUBSTANTIVE error changes a claim, theorem, definition, or computation in a way a careful
reader would recognize as a real disagreement with another part of the paper. A TYPO-SHAPED
error is a surface slip the reader mentally repairs on the spot — malformed math, a bare
symbol swap to an undefined letter, a local index shift never referenced again.

Tie-breaking rules when you are unsure:
  - If the perturbed span is MALFORMED in isolation (or obviously local and never referenced),
    choose typo-shaped.
  - If NO QUOTE is available and the perturbation is a bare symbol swap (one identifier
    replaced with another) or a local index shift, choose typo-shaped — even without
    corroborating evidence, bare symbol swaps to undefined/differently-bound letters and
    purely-local index shifts are structurally typo-shaped.
  - If the perturbed span is well-formed and you simply cannot verify a contradiction from
    the shown quote (because the quote is too vague, or describes the variable abstractly),
    choose not-an-error — not typo-shaped. "Not-an-error" means "I cannot conclude this is
    wrong from what I was given", and is the correct verdict whenever Step 2 fails below
    AND the perturbed span is not itself structurally typo-shaped.
  - Between substantive and typo-shaped, choose typo-shaped.

INPUTS:

Error type: {error_type}

Original span (from the paper):
<<<
{original}
>>>

Perturbed span (the seeded error):
<<<
{perturbed}
>>>

Quote from elsewhere in the paper ({quote_source}):
<<<
{quote}
>>>

JUDGMENT PROCEDURE (work through these in order; any NO → typo-shaped or not-an-error):

Step 1 — Self-coherence check (on the PERTURBED span alone).
  Is the perturbed span internally well-formed when read in isolation?
  Examples of FAILURE (→ typo-shaped):
    - Mixed-direction inequality chain like "0 < w > L/2" or "a \le b \ge c".
    - Broken sandwich like "a \ge b \le c".
    - Type/unit mismatches obvious without context (e.g. "T = N_T / \Delta_t" where T is a time
      but the product N_T \Delta_t has time units and the quotient does not).
    - Operator salad (two binary operators back to back with no operand).
    - A symbol replaced with a letter not bound anywhere in the quote or original span.

Step 2 — Quote specificity.
  Does the quote literally state the original value/symbol/operator (or an obviously
  equivalent form)? A quote that only mentions the same variable or the same topic is NOT
  enough. If the quote does not concretely state the original → not-an-error.

Step 3 — Downstream dependence.
  Would the perturbation propagate through the paper's downstream math?
  For numeric_parameter: is the specific value reused (in derivations, proofs, numerical
    results)? If the value is stated once and never used again → typo-shaped.
  For index_or_subscript on a summation or interval: is the boundary term plausibly NONZERO,
    AND is the sum/interval referenced or reused? A pure re-indexing that doesn't change the
    sum's value (or where the sum is never reused) → typo-shaped.
  For operator_or_sign: does the flipped operator actually change a statement the paper
    elsewhere relies on? A lone sign in a standalone equation that is never reused →
    typo-shaped.
  For symbol_binding: almost always typo-shaped. The only exception is when the replacement
    symbol is independently defined in the paper with an incompatible type/role, and the
    swap creates a well-formed but false statement. Bare letter swaps (alpha → gamma, A_i →
    X_i, \beta → \phi) are typo-shaped.

NEGATIVE EXAMPLES (both should be classified typo-shaped):

  (a) Perturbed: "$0 < w > L/2$". Quote mentions "w < L/2". Verdict: typo-shaped — the
      perturbed chain is malformed (mixed direction); Step 1 fails.

  (b) Original: "$\beta_k$". Perturbed: "$\phi_k$". Quote: "... their own weight $\beta_k$".
      Verdict: typo-shaped — bare symbol swap to an undefined letter; Step 3 fails for
      symbol_binding (no independent binding of $\phi_k$).

POSITIVE EXAMPLE (should be classified substantive):

  Original: "$10^{{-6}}$". Perturbed: "$10^{{-3}}$". Quote: "number of Newton iterations
  before the desired accuracy of $10^{{-6}}$ is reached". Verdict: substantive — quote states
  the original value verbatim (Step 2), and the accuracy threshold governs the numerical
  experiment (Step 3).

Return ONLY a single JSON object (no commentary):
{{"verdict": "substantive" | "typo-shaped" | "not-an-error", "reason": "<one sentence citing which step failed or passed>"}}
"""


# Checklist variants: replace the prose 3-step procedure with 4 yes/no items
# whose answer pattern deterministically maps to a verdict. One checklist per
# error-type family. Same INPUT placeholders as VERIFIER_PROMPT.

# VERDICT (applied in code from the answers):
#   if C1 == N or C4 == Y          → "typo-shaped"
#   elif C2 == N                   → "not-an-error"
#   elif C3 == N                   → "not-an-error"
#   else                           → "substantive"
VERIFIER_PROMPT_CHECKLIST_SURFACE = r"""
You are checking a seeded error in an academic math paper against a checklist.

INPUTS:

Error type: {error_type}

Original span:
<<<
{original}
>>>

Perturbed span:
<<<
{perturbed}
>>>

Quote from elsewhere in the paper ({quote_source}):
<<<
{quote}
>>>

Answer each item with Y or N. Be literal — do not infer beyond what is shown.

C1. Is the perturbed span well-formed when read in isolation?
    Answer N if it has any of but not limited to: mixed-direction inequality chain (e.g.
    "0 < w > L/2"), broken sandwich (e.g. "a >= b <= c"), operator salad
    (two binary operators with no operand), obvious type/unit mismatch,
    or contains a symbol/letter not bound anywhere in the original or quote.
    Otherwise Y.

C2. Does the quote literally state the ORIGINAL value/symbol/operator
    (or an obviously equivalent form)?
    Mentioning the same variable name or topic abstractly does NOT count.
    The quote must concretely state the original. Otherwise N.

C3. Does the perturbation alter something the quote (or its directly
    implied downstream math) relies on?
    Answer N for: a numeric value the quote shows is stated only once and
    never reused; a sign/operator flip in a standalone equation never
    referenced by the quote.
    Otherwise Y.

C4. (structural) Is the perturbed form structurally typo-shaped
    regardless of evidence — one of:
    (a) a bare symbol swap whose replacement letter is not bound
        anywhere in the paper; or
    (b) a re-indexing that leaves the expression algebraically
        unchanged (dummy-variable rename like \sum_i \to \sum_j, or
        simultaneous bound + index shift like \sum_{{i=0}}^n a_i \to
        \sum_{{i=1}}^{{n+1}} a_{{i-1}})?
    Y if yes; N otherwise.

Return ONLY a single JSON object (no commentary). The verdict will be
computed downstream from your answers — do not output a verdict yourself.
{{"c1": "Y" | "N",
  "c2": "Y" | "N",
  "c3": "Y" | "N",
  "c4": "Y" | "N",
  "reason": "<one sentence justifying the most decisive item>"}}
"""


# VERDICT (applied in code from the answers):
#   if L1 == N or L4 == Y          → "typo-shaped"
#   elif L2 == N                   → "not-an-error"
#   elif L3 == N                   → "not-an-error"
#   else                           → "substantive"
VERIFIER_PROMPT_CHECKLIST_LOGIC = r"""
You are checking a seeded error in the PROOF of an academic math paper against
a checklist.

INPUTS:

Error type: {error_type}    (one of: missing_case, induction, circular_reasoning, invalid_implication)

Original step / proof excerpt:
<<<
{original}
>>>

Perturbed version:
<<<
{perturbed}
>>>

Quote from elsewhere in the paper ({quote_source}):
<<<
{quote}
>>>

Answer each item with Y or N. Be literal — judge from inputs only.

L1. Is the perturbed step coherent as a logical argument when read in
    isolation? Y if it parses as a step / case / inductive argument.
    N for nonsense like "by induction on the empty set", a step that names
    variables not bound anywhere, or a syntactically broken inference.

L2. Does the quote establish what the proof is meant to conclude — the
    theorem statement, lemma being applied, or inductive hypothesis?
    Mentioning the topic in the abstract is NOT enough; the quote must
    pin down the claim the perturbed step bears on. Otherwise N.

L3. Does the perturbation break the chain of inference?
    - missing_case: the deleted case is non-trivial (its conclusion is not
      forced by the remaining cases).
    - induction: the base case is now wrong, or the inductive step no
      longer reduces n+1 to n.
    - circular_reasoning: a step now invokes the very claim being proved.
    - invalid_implication: a reversed/dropped arrow now allows conclusions
      the quote rules out (or blocks ones it requires).
    Y if a careful reader could point at the broken link given the quote;
    N if the modification leaves the proof still valid (or its breakage
    is invisible from the inputs).

L4. Is the change cosmetic? Y for: rewording, swapping an equivalent
    step, permuting a case ordering, dropping a manifestly redundant case.

Return ONLY a single JSON object (no commentary). The verdict will be
computed downstream from your answers — do not output a verdict yourself.
{{"l1": "Y" | "N",
  "l2": "Y" | "N",
  "l3": "Y" | "N",
  "l4": "Y" | "N",
  "reason": "<one sentence justifying the most decisive item>"}}
"""


# VERDICT (applied in code from the answers):
#   if D1 == N or D4 == Y          → "typo-shaped"
#   elif D2 == N                   → "not-an-error"
#   elif D3 == N                   → "not-an-error"
#   else                           → "substantive"
VERIFIER_PROMPT_CHECKLIST_CLAIM = r"""
You are checking a seeded error in a DEFINITION or THEOREM statement of an
academic math paper against a checklist.

INPUTS:

Error type: {error_type}    (incorrect_claim_theoretical)

Original statement:
<<<
{original}
>>>

Perturbed statement:
<<<
{perturbed}
>>>

Quote from elsewhere in the paper ({quote_source}):
<<<
{quote}
>>>

Answer each item with Y or N. Be literal.

D1. Is the perturbed statement well-formed as a definition/theorem when
    read in isolation? N for: undefined symbols, missing quantifiers that
    the syntax requires, mismatched arity, or any malformation that
    wouldn't compile in the paper.

D2. Does the quote actually invoke, apply, or reference the original
    definition/theorem in a way that depends on its specific wording?
    Just naming "Theorem 2.1" or using a related concept does NOT count.
    The quote must use a hypothesis or conclusion that the perturbation
    touches. Otherwise N.

D3. Does the perturbation change the meaning so that the quoted
    application is no longer valid? Look for: weakened/strengthened
    quantifiers (∀ ↔ ∃) the application relies on, a hypothesis the
    application uses now dropped/reversed, a conclusion the application
    cites now strengthened beyond what the proof supports.
    Y if the application stops going through; N if it still holds with
    the perturbed wording.

D4. Is the change a cosmetic reformulation? Y for: renaming bound
    variables, reordering equivalent clauses, restating with a synonym.

Return ONLY a single JSON object (no commentary). The verdict will be
computed downstream from your answers — do not output a verdict yourself.
{{"d1": "Y" | "N",
  "d2": "Y" | "N",
  "d3": "Y" | "N",
  "d4": "Y" | "N",
  "reason": "<one sentence justifying the most decisive item>"}}
"""


# VERDICT (applied in code from the answers):
#   if E1 == N or E4 == Y          → "typo-shaped"
#   elif E2 == N                   → "not-an-error"
#   elif E3 == N                   → "not-an-error"
#   else                           → "substantive"
VERIFIER_PROMPT_CHECKLIST_EMPIRICAL = r"""
You are checking a seeded error in EMPIRICAL prose of an academic paper
against a checklist.

INPUTS:

Error type: {error_type}    (incorrect_statement_empirical, misinterp, causal_reversed, p_hacking)

Original passage:
<<<
{original}
>>>

Perturbed passage:
<<<
{perturbed}
>>>

Quote from elsewhere in the paper ({quote_source}):
<<<
{quote}
>>>

Answer each item with Y or N. Be literal.

E1. Is the perturbed passage coherent prose? N for: garbled grammar
    introduced by the perturbation, undefined terms, or sentences that
    parse but become meaningless.

E2. Does the quote pin down the specific empirical content the passage
    is about — a named result, dataset, comparison, p-value, effect
    direction, method choice? Mentioning the same topic abstractly is
    NOT enough. Otherwise N.

E3. Does the perturbation produce a claim that disagrees with the
    quoted content?
    - incorrect_statement_empirical: the claim now contradicts a number,
      dataset, or methodological detail the quote states.
    - misinterp: the claim now misreads what the quoted result means
      (e.g. p-value treated as Pr[null|data], correlation read as
      causation where the paper explicitly disclaims it).
    - causal_reversed: the claim's causal direction now opposes what the
      quote establishes.
    - p_hacking: the claim now adds a methodological flaw absent from
      the quote, or removes a correction the quote describes.
    Y if a careful reader comparing prose to quote sees the
    disagreement; N otherwise.

E4. Is the change a stylistic rephrasing that preserves the empirical
    claim? Y for: synonym swaps, hedging tweaks like "few" ↔ "some" that
    don't flip the conclusion, reordering the claim's clauses.

Return ONLY a single JSON object (no commentary). The verdict will be
computed downstream from your answers — do not output a verdict yourself.
{{"e1": "Y" | "N",
  "e2": "Y" | "N",
  "e3": "Y" | "N",
  "e4": "Y" | "N",
  "reason": "<one sentence justifying the most decisive item>"}}
"""


# Batched, unified-prompt variant. One call evaluates ALL perturbations from a
# single (paper, error_type) run. Each perturbation carries its own evidence
# (surrounding_context + related_passages), so the prompt is independent of any
# single sampled quote. The model dispatches I3 on each perturbation's
# error_type field.
#
# VERDICT (applied in code from the answers, per perturbation):
#   if I1 == N or I4 == Y          → "typo-shaped"
#   elif I2 == N                   → "not-an-error"
#   elif I3 == N                   → "not-an-error"
#   else                           → "substantive"
VERIFIER_PROMPT_BATCHED = r"""
You are checking a batch of seeded errors in an academic paper against a checklist.

Paper: {paper_title}

You will receive a JSON array of perturbations. Each perturbation has:
- perturbation_id: unique key — use this verbatim in your output
- error_type: one of the seeded error categories
- original: the original text span from the paper
- perturbed: the modified version with the seeded error
- surrounding_context: ~200 characters of paper text around the span (verbatim, NOT perturbed)
- related_passages: list of snippets from elsewhere in the paper that mention the same symbols/named refs (verbatim, NOT perturbed)

Judge each perturbation INDEPENDENTLY. Do not let the assessment of one perturbation influence another. Treat surrounding_context and related_passages as ground truth from the original paper, even if they overlap with the location of another perturbation in the batch.

PERTURBATIONS:
{perturbations_json}

For EACH perturbation, answer four items with Y or N. Be literal — judge from the inputs above only.

I1. (well-formed) Is the perturbed span well-formed when read in isolation?
    Answer N for any of: a mixed-direction inequality chain (e.g. "0 < w > L/2"),
    a broken sandwich (e.g. "a >= b <= c"), operator salad (two binary operators
    with no operand), obvious type/unit mismatch, garbled grammar, a sentence
    that parses but is meaningless, "by induction on the empty set"-style
    nonsense, a step that names variables not bound anywhere, a definition with
    undefined symbols / mismatched arity / missing required quantifiers, or a
    symbol/letter not bound in the original, surrounding_context, or
    related_passages. Otherwise Y.

I2. (evidence available) Do the surrounding_context or related_passages contain
    something CONCRETE that the original span establishes or relates to —
    a stated value, a definition, an applied theorem, a methodological detail,
    a named result, a stated fact, or a downstream use of the same
    symbol/quantity/concept? Mentioning the topic abstractly does NOT count;
    the evidence must be a concrete claim about the same object the original
    span is about. Otherwise N.

I3. (contradiction confirmed) Does the perturbation contradict that evidence,
    given the perturbation's error_type?
    - Surface (numeric_parameter, operator_or_sign, index_or_subscript,
      computation, symbol_binding): does the perturbed value/symbol/operator
      now disagree with how the same quantity appears in surrounding_context
      or related_passages?
    - incorrect_claim_theoretical: does the perturbation alter the statement
      so that an application of it visible in surrounding_context or
      related_passages no longer goes through?
    - Logic (missing_case, induction, circular_reasoning, invalid_implication):
      does the perturbed step now break the chain of inference toward what
      the proof is trying to establish? (missing_case: the deleted case is
      non-trivial; induction: base case wrong, or step no longer reduces n+1
      to n; circular_reasoning: a step now invokes the very claim being
      proved; invalid_implication: a reversed/dropped arrow now allows
      conclusions ruled out by context.)
    - Empirical (incorrect_statement_empirical, misinterp, causal_reversed,
      p_hacking): does the perturbed claim now disagree with a fact
      established in surrounding_context or related_passages, OR introduce a
      methodological flaw the original explicitly avoided (post-hoc
      selection, removed correction, reversed causal direction)?
    Y if a careful reader could point at the contradiction; N if the
    modification leaves the perturbation unrefuted by the available evidence.

I4. (typo-shaped / cosmetic) Is the perturbed form structurally typo-shaped or
    cosmetically equivalent regardless of evidence — one of: a bare symbol
    swap whose replacement letter is not bound anywhere; a re-indexing that
    leaves the expression algebraically unchanged (dummy-variable rename like
    \sum_i \to \sum_j; simultaneous bound + index shift); a synonym swap; a
    reordering of equivalent clauses; renaming bound variables; permuting a
    case ordering; dropping a manifestly redundant case; a hedging tweak
    ("few" ↔ "some") that does not flip the conclusion?
    Y if yes; N otherwise.

Return ONLY a single JSON array (no commentary). One object per input
perturbation, keyed by perturbation_id (NOT by list order — the consumer binds
on perturbation_id). Include every perturbation_id from the input. The verdict
will be computed downstream from your answers — do not output a verdict yourself.

[{{"perturbation_id": "<id>",
   "i1": "Y" | "N",
   "i2": "Y" | "N",
   "i3": "Y" | "N",
   "i4": "Y" | "N",
   "reason": "<one sentence justifying the most decisive item>"}},
  ...]
"""


# Dispatcher: maps Error.value → checklist template. Used when prompt_template
# is the special sentinel "checklist" — _verify_one resolves the right template
# per perturbation.
CHECKLIST_BY_ERROR: dict[str, str] = {
    # surface
    "numeric_parameter":              VERIFIER_PROMPT_CHECKLIST_SURFACE,
    "operator_or_sign":               VERIFIER_PROMPT_CHECKLIST_SURFACE,
    "index_or_subscript":             VERIFIER_PROMPT_CHECKLIST_SURFACE,
    "computation":                    VERIFIER_PROMPT_CHECKLIST_SURFACE,
    "symbol_binding":                 VERIFIER_PROMPT_CHECKLIST_SURFACE,
    # claim theoretical
    "incorrect_claim_theoretical":    VERIFIER_PROMPT_CHECKLIST_CLAIM,
    # logic
    "missing_case":                   VERIFIER_PROMPT_CHECKLIST_LOGIC,
    "induction":                      VERIFIER_PROMPT_CHECKLIST_LOGIC,
    "circular_reasoning":             VERIFIER_PROMPT_CHECKLIST_LOGIC,
    "invalid_implication":            VERIFIER_PROMPT_CHECKLIST_LOGIC,
    # statement empirical
    "incorrect_statement_empirical":  VERIFIER_PROMPT_CHECKLIST_EMPIRICAL,
    # experimental
    "misinterp":                      VERIFIER_PROMPT_CHECKLIST_EMPIRICAL,
    "causal_reversed":                VERIFIER_PROMPT_CHECKLIST_EMPIRICAL,
    "p_hacking":                      VERIFIER_PROMPT_CHECKLIST_EMPIRICAL,
}


def _resolve_prompt_template(prompt_template, error: Error) -> str:
    """Allow prompt_template to be either a string template or a dict
    keyed by Error.value. The sentinel string "checklist" routes through
    CHECKLIST_BY_ERROR (the per-error checklist family)."""
    if prompt_template == "checklist":
        return CHECKLIST_BY_ERROR[error.value]
    if isinstance(prompt_template, dict):
        return prompt_template[error.value]
    return prompt_template


_MIXED_INEQ_RE = re.compile(r"(<|\\le(?:q)?\b|\\leq\b).*?(>|\\ge(?:q)?\b|\\geq\b)", re.DOTALL)
_MIXED_INEQ_RE_REV = re.compile(r"(>|\\ge(?:q)?\b|\\geq\b).*?(<|\\le(?:q)?\b|\\leq\b)", re.DOTALL)
_OPERATOR_SALAD_RE = re.compile(r"(?:<\s*>|>\s*<|\\le\s*\\ge|\\ge\s*\\le|\\leq\s*\\geq|\\geq\s*\\leq)")


def structural_precheck(p: Perturbation) -> tuple[str, str]:
    """Fast, deterministic pre-check. Returns (status, reason).

    status is one of:
      - "keep"         → pass to LLM verifier
      - "reject-typo"  → surface-typo caught by a structural rule; skip LLM call

    Rules (any match → reject-typo):
      1. Runaway perturbed span (likely span-extraction bug).
      2. Literal escape artifacts in perturbed that aren't in original.
      3. Mixed-direction inequality chain in perturbed (e.g. "0 < w > L/2").
      4. Operator salad (two consecutive binary inequality operators with no operand).

    The checks are conservative; they fire only on patterns that are bugs or obvious
    malformation. The LLM verifier handles everything else.
    """
    orig, pert = p.original or "", p.perturbed or ""

    # Rule 1: runaway span.
    if len(pert) > 2 * len(orig) + 50:
        return ("reject-typo",
                f"perturbed is {len(pert)} chars vs {len(orig)} original — runaway span (structural bug)")

    # Rule 2: literal escape artifacts introduced by the perturbation.
    # e.g. paper_005 had "$$\n   ...\n  $$" where \n appears as literal backslash-n
    # (2-char sequence) instead of a real newline. These are pipeline bugs.
    # Guard against false positives: \neq, \nabla, \tau, \times, \top, \rightarrow, \rm
    # all start with \n / \t / \r followed by a letter — those are legitimate LaTeX
    # macros and should NOT be flagged. Only flag the escape char followed by a
    # non-letter (whitespace, punctuation, end of string).
    escape_re = re.compile(r"\\[ntr](?![a-zA-Z])")
    if escape_re.search(pert) and not escape_re.search(orig):
        return ("reject-typo",
                "perturbed contains a literal escape artifact (\\n / \\t / \\r not followed by a letter) absent from original")

    # Rule 3: mixed-direction inequality chain inside the perturbed span.
    # Only consider math content (between $ delimiters or \begin{align}/\end{align} blocks).
    # Skip when the original already mixes directions (legit coexistence of \le and \ge).
    orig_blobs = _extract_math_blobs(orig)
    orig_mixed = any(
        _MIXED_INEQ_RE.search(b) and _MIXED_INEQ_RE_REV.search(b) for b in orig_blobs
    )
    if not orig_mixed:
        for blob in _extract_math_blobs(pert):
            lt_count = len(re.findall(r"<|\\le(?:q)?\b|\\leq\b", blob))
            gt_count = len(re.findall(r">|\\ge(?:q)?\b|\\geq\b", blob))
            if lt_count > 0 and gt_count > 0:
                return ("reject-typo",
                        "perturbed math contains a mixed-direction inequality chain (Step 1 malformation)")

    # Rule 4: operator salad.
    if _OPERATOR_SALAD_RE.search(pert) and not _OPERATOR_SALAD_RE.search(orig):
        return ("reject-typo",
                "perturbed contains two consecutive inequality operators (operator salad)")

    return ("keep", "")


def _extract_math_blobs(text: str) -> list[str]:
    """Return a list of math-mode substrings: content between $...$ pairs and between
    \\begin{...} ... \\end{...} blocks. Best-effort, not a full LaTeX parser."""
    blobs = []
    # $$...$$ first (greedy-safe via non-greedy)
    for m in re.finditer(r"\$\$(.+?)\$\$", text, re.DOTALL):
        blobs.append(m.group(1))
    # $...$ (skip $$ which we already stripped by re-matching text minus $$ pairs is messy;
    # the earlier pattern is a superset so dup hits are harmless for our detector)
    for m in re.finditer(r"(?<!\$)\$([^$]+)\$(?!\$)", text):
        blobs.append(m.group(1))
    # \begin{env} ... \end{env}
    for m in re.finditer(r"\\begin\{[^}]+\}(.+?)\\end\{[^}]+\}", text, re.DOTALL):
        blobs.append(m.group(1))
    # \[ ... \]
    for m in re.finditer(r"\\\[(.+?)\\\]", text, re.DOTALL):
        blobs.append(m.group(1))
    if not blobs:
        blobs = [text]
    return blobs


@dataclass
class VerifierVerdict:
    perturbation_id: str
    verdict: str            # one of _VALID_VERDICTS, or "parse-error"
    reason: str
    quote_source: str = ""  # "generator" | "random-sampled" | "none-available"


def _deterministic_rng(key: str) -> random.Random:
    """Return a random.Random seeded reproducibly from a string key (e.g. perturbation_id)."""
    seed = int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16) % (2**32)
    return random.Random(seed)


def _pick_quote(
    p: Perturbation,
    span: CandidateSpan | None,
) -> tuple[str, str]:
    """Return (quote, quote_source) for the verifier prompt.

    Preference:
      1. p.contradicts_quote if non-empty → ("<quote>", "generator")
      2. random snippet from span.verifier_related_passages → ("<snippet>", "random-sampled")
      3. ("(no quote available)", "none-available")

    Note on self-quotes: a small fraction (~7-12%) of generator-produced quotes are
    substrings of the original span — providing no independent evidence. We do not
    filter these here because some gold-label judgments depend on the quote. The
    prompt's Step 2 is the place to steer the verifier away from circular evidence.
    """
    if p.contradicts_quote:
        return p.contradicts_quote, "generator"
    if span and span.verifier_related_passages:
        rng = _deterministic_rng(p.perturbation_id)
        rp = rng.choice(span.verifier_related_passages)
        return rp.get("snippet", ""), "random-sampled"
    return "(no quote available)", "none-available"


def _strip_code_fences(s: str) -> str:
    """Remove a leading ```json / ``` fence and trailing ``` fence if present."""
    s = s.strip()
    # Leading fence
    for prefix in ("```json", "```JSON", "```"):
        if s.startswith(prefix):
            s = s[len(prefix):].lstrip("\n").lstrip()
            break
    # Trailing fence
    if s.endswith("```"):
        s = s[: -3].rstrip()
    return s


_CHECKLIST_PREFIXES = ("c", "l", "d", "e", "i")


def _compute_verdict_from_checklist(obj: dict) -> tuple[str, str] | None:
    """If obj is a checklist response (keys <p>1..<p>4 with Y/N values for some
    prefix in {c,l,d,e}), apply the deterministic rule and return (verdict, items_repr).
    Returns None if obj is not a checklist response. Returns ("parse-error", reason)
    if items are present but malformed.

    Rule (identical across all four families):
      if i1 == N or i4 == Y          → "typo-shaped"
      elif i2 == N or i3 == N        → "not-an-error"
      else                           → "substantive"
    """
    for prefix in _CHECKLIST_PREFIXES:
        keys = tuple(f"{prefix}{i}" for i in (1, 2, 3, 4))
        if not all(k in obj for k in keys):
            continue
        vals = [str(obj[k]).strip().upper() for k in keys]
        if any(v not in ("Y", "N") for v in vals):
            return ("parse-error", f"checklist items must be Y/N, got {dict(zip(keys, vals))}")
        i1, i2, i3, i4 = vals
        if i1 == "N" or i4 == "Y":
            return ("typo-shaped", f"{keys[0]}={i1} {keys[3]}={i4}")
        if i2 == "N" or i3 == "N":
            return ("not-an-error", f"{keys[1]}={i2} {keys[2]}={i3}")
        return ("substantive", f"{keys[0]}=Y {keys[1]}=Y {keys[2]}=Y {keys[3]}=N")
    return None


def _try_verdict_dict(obj) -> tuple[str, str] | None:
    """Return (verdict, reason) if obj is a valid verdict dict, else None.

    Two response shapes are accepted:
      1. Checklist: keys c1..c4 / l1..l4 / d1..d4 / e1..e4 with Y/N values.
         Verdict is computed deterministically in code.
      2. Legacy: a "verdict" key with one of _VALID_VERDICTS.
    """
    if not isinstance(obj, dict):
        return None
    model_reason = str(obj.get("reason", "")).strip()

    checklist = _compute_verdict_from_checklist(obj)
    if checklist is not None:
        verdict, items_repr = checklist
        if verdict == "parse-error":
            return checklist
        reason = f"[{items_repr}] {model_reason}".strip() if model_reason else f"[{items_repr}]"
        return (verdict, reason)

    if "verdict" not in obj:
        return None
    verdict = str(obj.get("verdict", "")).strip().lower()
    if verdict not in _VALID_VERDICTS:
        return ("parse-error", f"unknown verdict {verdict!r}")
    return (verdict, model_reason)


def _parse_verdict(response: str) -> tuple[str, str]:
    """Pull a valid verdict JSON object out of the response. Tries several
    strategies:
      1. Strip code fences, then `json.loads` the whole thing.
      2. Walk the response looking for `{...}` substrings that decode into a
         dict with a "verdict" key.

    Falls back to ('parse-error', <diagnostic with raw>) on failure.
    """
    stripped = _strip_code_fences(response)

    # Strategy 1: whole-response JSON parse.
    try:
        obj = json.loads(stripped)
        result = _try_verdict_dict(obj)
        if result is not None:
            return result
    except (json.JSONDecodeError, TypeError):
        pass

    # Strategy 2: walk for any embedded JSON object with a verdict key.
    decoder = json.JSONDecoder()
    for source in (stripped, response):
        i = 0
        while i < len(source):
            if source[i] == "{":
                try:
                    obj, end = decoder.raw_decode(source, i)
                    result = _try_verdict_dict(obj)
                    if result is not None:
                        return result
                    i = end
                except json.JSONDecodeError:
                    i += 1
            else:
                i += 1

    # Strategy 3: salvage from a truncated response. If the model's output was cut off
    # mid-JSON (e.g. the reason string overflowed max_tokens), we can still recover the
    # verdict token via regex — the verdict is always one of a fixed set and appears
    # early in the output.
    salvage_re = re.compile(r'"verdict"\s*:\s*"(substantive|typo-shaped|not-an-error)"')
    m = salvage_re.search(response)
    if m:
        return m.group(1), f"salvaged from truncated response; raw_head={response[:120]!r}"

    return "parse-error", f"no JSON object with 'verdict' found; raw={response[:300]!r}"


def _verify_one(
    p: Perturbation,
    span: CandidateSpan | None,
    model: str,
    reasoning_effort: str | None,
    prompt_template=VERIFIER_PROMPT,
    use_structural_precheck: bool = True,
) -> VerifierVerdict:
    quote, quote_source = _pick_quote(p, span)

    if use_structural_precheck:
        status, reason = structural_precheck(p)
        if status == "reject-typo":
            return VerifierVerdict(
                p.perturbation_id, "typo-shaped",
                f"structural precheck: {reason}",
                quote_source=quote_source,
            )

    resolved_template = _resolve_prompt_template(prompt_template, p.error)

    format_kwargs = dict(
        error_type=p.error.value,
        original=p.original,
        perturbed=p.perturbed,
        quote=quote,
        quote_source=(
            "provided by the generator" if quote_source == "generator"
            else "randomly sampled from the paper" if quote_source == "random-sampled"
            else "no quote was available"
        ),
    )
    # Legacy prompt expects why_wrong; new prompt does not. Supply both so either works.
    if "{why_wrong}" in resolved_template:
        format_kwargs["why_wrong"] = p.why_wrong or "(generator did not provide one)"
    prompt = resolved_template.format(**format_kwargs)

    # Note: we used to short-circuit "none-available" to not-an-error here without calling
    # the LLM. That missed bare-symbol-swap / local-index-shift typos where the perturbed
    # span itself is evidence. Now we let the LLM judge even without a quote — the revised
    # prompt handles the no-quote case explicitly.
    try:
        response, _usage = chat(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            max_tokens=4096,
            reasoning_effort=reasoning_effort,
        )
    except Exception as e:
        return VerifierVerdict(p.perturbation_id, "parse-error", f"chat failed: {e}", quote_source=quote_source)

    verdict, reason = _parse_verdict(response)
    return VerifierVerdict(p.perturbation_id, verdict, reason, quote_source=quote_source)


def verify_perturbations(
    perturbations: list[Perturbation],
    candidates: list[CandidateSpan],
    model: str = DEFAULT_VERIFIER_MODEL,
    reasoning_effort: str | None = DEFAULT_VERIFIER_REASONING,
    max_workers: int = DEFAULT_MAX_WORKERS,
    prompt_template: str = VERIFIER_PROMPT,
    use_structural_precheck: bool = True,
) -> tuple[list[Perturbation], list[tuple[Perturbation, VerifierVerdict]], dict]:
    """Run the per-perturbation verifier in parallel.

    Returns (accepted, rejected, stats) where:
      - accepted: perturbations the verifier judged "substantive"
      - rejected: list of (perturbation, verdict) for everything else (typo-shaped,
        not-an-error, or parse-error)
      - stats: dict with bucket counts

    Parse errors are treated as REJECTED — we'd rather drop a genuine perturbation
    than inject a bogus one into the benchmark.
    """
    span_lookup = {c.span_id: c for c in candidates}

    if not perturbations:
        return [], [], {
            "n_input": 0,
            "substantive": 0,
            "typo-shaped": 0,
            "not-an-error": 0,
            "parse-error": 0,
        }

    print(f"\nVerifier: fanning out {len(perturbations)} perturbations "
          f"across {max_workers} workers (model={model}, reasoning={reasoning_effort})...")

    verdicts: dict[str, VerifierVerdict] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {
            ex.submit(
                _verify_one,
                p,
                span_lookup.get(p.span_id),
                model,
                reasoning_effort,
                prompt_template,
                use_structural_precheck,
            ): p
            for p in perturbations
        }
        for fut in as_completed(futures):
            v = fut.result()
            verdicts[v.perturbation_id] = v

    accepted: list[Perturbation] = []
    rejected: list[tuple[Perturbation, VerifierVerdict]] = []
    for p in perturbations:
        v = verdicts[p.perturbation_id]
        if v.verdict == "substantive":
            accepted.append(p)
        else:
            rejected.append((p, v))

    stats = {
        "n_input": len(perturbations),
        "substantive": sum(1 for v in verdicts.values() if v.verdict == "substantive"),
        "typo-shaped": sum(1 for v in verdicts.values() if v.verdict == "typo-shaped"),
        "not-an-error": sum(1 for v in verdicts.values() if v.verdict == "not-an-error"),
        "parse-error": sum(1 for v in verdicts.values() if v.verdict == "parse-error"),
        "structural-typo": sum(
            1 for v in verdicts.values()
            if v.verdict == "typo-shaped" and v.reason.startswith("structural precheck:")
        ),
        "quote_source": {
            "generator": sum(1 for v in verdicts.values() if v.quote_source == "generator"),
            "random-sampled": sum(1 for v in verdicts.values() if v.quote_source == "random-sampled"),
            "none-available": sum(1 for v in verdicts.values() if v.quote_source == "none-available"),
        },
    }
    print(f"  Verifier verdicts: {stats}")
    return accepted, rejected, stats


# ---------------------------------------------------------------------------
# Batched verifier (one LLM call per (paper, error_type) run)
# ---------------------------------------------------------------------------


def _parse_batched_response(
    response: str,
    expected_ids: set[str],
) -> dict[str, tuple[str, str]]:
    """Pull a JSON array of per-perturbation answers out of the response.

    Returns dict keyed by perturbation_id → (verdict, reason). Missing IDs
    from `expected_ids` are NOT inserted here — the caller decides how to
    handle them (typically: assign 'parse-error').

    Strategies, in order:
      1. Strip code fences, parse the whole response as a JSON list.
      2. Walk for the first embedded `[...]` that decodes into a list.
      3. Walk for individual `{...}` objects carrying `perturbation_id`
         (handles a model that returned concatenated objects without array
         wrapping).
    """
    out: dict[str, tuple[str, str]] = {}

    def _ingest(arr: list) -> None:
        for obj in arr:
            if not isinstance(obj, dict):
                continue
            pid = str(obj.get("perturbation_id", "")).strip()
            if not pid or pid not in expected_ids:
                continue
            result = _compute_verdict_from_checklist(obj)
            if result is None:
                out[pid] = ("parse-error", "no checklist items in response object")
                continue
            verdict, items_repr = result
            if verdict == "parse-error":
                out[pid] = result
                continue
            model_reason = str(obj.get("reason", "")).strip()
            reason = f"[{items_repr}] {model_reason}".strip() if model_reason else f"[{items_repr}]"
            out[pid] = (verdict, reason)

    stripped = _strip_code_fences(response)

    # Strategy 1: whole-response JSON array.
    try:
        obj = json.loads(stripped)
        if isinstance(obj, list):
            _ingest(obj)
            if out:
                return out
    except (json.JSONDecodeError, TypeError):
        pass

    # Strategy 2: walk for an embedded `[...]` that decodes to a list.
    decoder = json.JSONDecoder()
    for source in (stripped, response):
        i = 0
        while i < len(source):
            if source[i] == "[":
                try:
                    obj, end = decoder.raw_decode(source, i)
                    if isinstance(obj, list):
                        _ingest(obj)
                        if out:
                            return out
                    i = end
                except json.JSONDecodeError:
                    i += 1
            else:
                i += 1

    # Strategy 3: walk for individual objects carrying `perturbation_id`.
    for source in (stripped, response):
        i = 0
        while i < len(source):
            if source[i] == "{":
                try:
                    obj, end = decoder.raw_decode(source, i)
                    if isinstance(obj, dict):
                        _ingest([obj])
                    i = end
                except json.JSONDecodeError:
                    i += 1
            else:
                i += 1

    return out


def verify_perturbations_batched(
    perturbations: list[Perturbation],
    candidates: list[CandidateSpan],
    paper_title: str = "",
    model: str = DEFAULT_VERIFIER_MODEL,
    reasoning_effort: str | None = DEFAULT_VERIFIER_REASONING,
    use_structural_precheck: bool = True,
) -> tuple[list[Perturbation], list[tuple[Perturbation, VerifierVerdict]], dict]:
    """Verify all perturbations in a single batched LLM call.

    One call evaluates the whole list. Each perturbation carries its own
    surrounding_context (±200 chars from `CandidateSpan.context`) and the
    full `verifier_related_passages` list — no single-quote dependency.

    The structural precheck still runs upfront and short-circuits caught
    perturbations to "typo-shaped" without an LLM call.

    Returns (accepted, rejected, stats) — same shape as
    `verify_perturbations` so callers can swap the function name.
    """
    span_lookup = {c.span_id: c for c in candidates}

    if not perturbations:
        return [], [], {
            "n_input": 0,
            "substantive": 0,
            "typo-shaped": 0,
            "not-an-error": 0,
            "parse-error": 0,
        }

    verdicts: dict[str, VerifierVerdict] = {}
    survivors: list[Perturbation] = []

    # Stage 1: structural precheck (deterministic, no LLM).
    if use_structural_precheck:
        for p in perturbations:
            status, reason = structural_precheck(p)
            if status == "reject-typo":
                verdicts[p.perturbation_id] = VerifierVerdict(
                    p.perturbation_id, "typo-shaped",
                    f"structural precheck: {reason}",
                )
            else:
                survivors.append(p)
    else:
        survivors = list(perturbations)

    # Stage 2: batched LLM call for the survivors.
    print(f"\nVerifier (batched): {len(survivors)} perturbations "
          f"({len(perturbations) - len(survivors)} caught by structural precheck) "
          f"in 1 call (model={model}, reasoning={reasoning_effort})...")

    if survivors:
        payload = []
        for p in survivors:
            span = span_lookup.get(p.span_id)
            payload.append({
                "perturbation_id": p.perturbation_id,
                "error_type": p.error.value,
                "original": p.original,
                "perturbed": p.perturbed,
                "surrounding_context": span.context if span else "",
                "related_passages": [
                    rp.get("snippet", "")
                    for rp in (span.verifier_related_passages if span else [])
                ],
            })

        prompt = VERIFIER_PROMPT_BATCHED.format(
            paper_title=paper_title or "(untitled)",
            perturbations_json=json.dumps(payload, indent=2),
        )

        try:
            response, _usage = chat(
                messages=[{"role": "user", "content": prompt}],
                model=model,
                max_tokens=16384,
                reasoning_effort=reasoning_effort,
            )
        except Exception as e:
            err = f"batched chat failed: {e}"
            for p in survivors:
                verdicts[p.perturbation_id] = VerifierVerdict(
                    p.perturbation_id, "parse-error", err,
                )
        else:
            expected_ids = {p.perturbation_id for p in survivors}
            parsed = _parse_batched_response(response, expected_ids)
            for p in survivors:
                if p.perturbation_id in parsed:
                    verdict, reason = parsed[p.perturbation_id]
                    verdicts[p.perturbation_id] = VerifierVerdict(
                        p.perturbation_id, verdict, reason,
                    )
                else:
                    verdicts[p.perturbation_id] = VerifierVerdict(
                        p.perturbation_id, "parse-error",
                        f"missing from batched response; raw_head={response[:200]!r}",
                    )

    # Bucket into accepted / rejected.
    accepted: list[Perturbation] = []
    rejected: list[tuple[Perturbation, VerifierVerdict]] = []
    for p in perturbations:
        v = verdicts[p.perturbation_id]
        if v.verdict == "substantive":
            accepted.append(p)
        else:
            rejected.append((p, v))

    stats = {
        "n_input": len(perturbations),
        "substantive": sum(1 for v in verdicts.values() if v.verdict == "substantive"),
        "typo-shaped": sum(1 for v in verdicts.values() if v.verdict == "typo-shaped"),
        "not-an-error": sum(1 for v in verdicts.values() if v.verdict == "not-an-error"),
        "parse-error": sum(1 for v in verdicts.values() if v.verdict == "parse-error"),
        "structural-typo": sum(
            1 for v in verdicts.values()
            if v.verdict == "typo-shaped" and v.reason.startswith("structural precheck:")
        ),
    }
    print(f"  Verifier verdicts: {stats}")
    return accepted, rejected, stats
