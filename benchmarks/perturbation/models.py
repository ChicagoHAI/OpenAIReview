"""Data models for the perturbation benchmark."""

from dataclasses import dataclass, field
from enum import Enum


class SpanType(str, Enum):
    """What kind of content a span contains."""
    # abstract 
    ABSTRACT = "abstract"

    # surface errors
    EQUATION_DISPLAY = "equation_display"   # $$...$$ or \[...\]
    EQUATION_INLINE = "equation_inline"     # $...$ or \(...\)
    EQUATION_NAMED = "equation_named"       # align, equation, gather, multline, cases

    # false claims
    DEFINITION = "definition"
    THEOREM = "theorem"

    # logic errors
    PROOF = "proof"

    # empirical errors
    EXPERIMENTAL = "experimental"
    PARAGRAPH = "paragraph"



class Error(str, Enum):
    """Edit-centric error taxonomy."""
    # surface
    NUMERIC_PARAMETER = "numeric_parameter"
    OPERATOR_OR_SIGN = "operator_or_sign"
    INDEX_OR_SUBSCRIPT = "index_or_subscript"
    COMPUTATION = "computation"
    SYMBOL_BINDING = "symbol_binding"  # deprecated for generation; kept for back-compat with old gold-set manifests


    # claim theoretical
    INCORRECT_CLAIM_THEORETICAL = "incorrect_claim_theoretical"

    # logic
    MISSING_CASE = "missing_case"
    INDUCTION = "induction"
    CIRCULAR_REASONING = "circular_reasoning"
    INVALID_IMPLICATION = "invalid_implication"


    # statement empirical 
    INCORRECT_STATEMENT_EMPIRICAL = "incorrect_statement_empirical"

    # experimental 
    MISINTERP = "misinterp"
    CAUSAL_REVERSED = "causal_reversed"
    P_HACKING = "p_hacking"


@dataclass
class CandidateSpan:
    """A span of text identified as a perturbation candidate."""
    span_id: str
    span_type: SpanType
    text: str                          # exact verbatim text from the paper
    offset: int                        # character offset into the paper text
    context: str                       # surrounding text for the LLM
    error_type: str
    compatible_errors: list[Error] = field(default_factory=list)
    related_passages: list[dict] = field(default_factory=list)
    verifier_related_passages: list[dict] = field(default_factory=list)


@dataclass
class Perturbation:
    """A single error to inject."""
    perturbation_id: str
    span_id: str                       # references a CandidateSpan
    error: Error
    original: str                      # exact text to find (from span store)
    offset: int                        # character offset into the original paper text
    perturbed: str                     # replacement text
    why_wrong: str                     # explanation of why this breaks internal consistency
    contradicts_quote: str = ""        # verbatim quote the perturbation contradicts; verifier samples one if empty


@dataclass
class PerturbationResult:
    """Result of scoring a reviewer against injected perturbations."""
    n_injected: int
    n_detected: int
    recall: float
    n_total_comments: int
    detected: list[str]                # perturbation_ids where step 1 + step 2 passed
    missed: list[str]                  # perturbation_ids where detection failed
