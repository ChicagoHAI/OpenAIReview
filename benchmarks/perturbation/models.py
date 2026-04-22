"""Data models for the perturbation benchmark."""

from dataclasses import dataclass, field
from enum import Enum


class SpanType(str, Enum):
    """What kind of content a span contains."""
    EQUATION_DISPLAY = "equation_display"   # $$...$$ or \[...\]
    EQUATION_INLINE = "equation_inline"     # $...$ or \(...\)
    EQUATION_NAMED = "equation_named"       # align, equation, gather, multline, cases

    DEFINITION = "definition"
    THEOREM = "theorem"
    PROOF = "proof"


class Error(str, Enum):
    """Edit-centric error taxonomy (from Codex)."""
    # surface
    NUMERIC_PARAMETER = "numeric_parameter"
    OPERATOR_OR_SIGN = "operator_or_sign"
    SYMBOL_BINDING = "symbol_binding"
    INDEX_OR_SUBSCRIPT = "index_or_subscript"

    # formal
    DEF_WRONG = "def_wrong"
    THM_WRONG_CONDITION = "thm_wrong_condition"
    THM_WRONG_CONCLUSION = "thm_wrong_conclusion"
    THM_WRONG_SCOPE = "thm_wrong_scope"
    PROOF_WRONG_DIRECTION = "proof_wrong_direction"
    PROOF_MISSING_CASE = "proof_missing_case"
    PROOF_WRONG_ASSUMPTION = "proof_wrong_assumption"
    PROOF_MISMATCH = "proof_mismatch"


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


@dataclass
class PerturbationResult:
    """Result of scoring a reviewer against injected perturbations."""
    n_injected: int
    n_detected: int
    recall: float
    n_total_comments: int
    detected: list[str]                # perturbation_ids where step 1 + step 2 passed
    missed: list[str]                  # perturbation_ids where detection failed
