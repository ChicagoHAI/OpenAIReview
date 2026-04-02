"""Data models for the perturbation benchmark."""

from dataclasses import dataclass, field
from enum import Enum


class SpanType(str, Enum):
    """What kind of content a span contains."""
    EQUATION_DISPLAY = "equation_display"   # $$...$$ or \[...\]
    EQUATION_INLINE = "equation_inline"     # $...$ or \(...\)
    EQUATION_NAMED = "equation_named"       # align, equation, gather, multline, cases
    NUMERIC = "numeric"                     # "0.67 hours", "p < 0.05", "N = 631,389"


class ErrorCategory(str, Enum):
    """Edit-centric error taxonomy (from Codex)."""
    NUMERIC_PARAMETER = "numeric_parameter"
    OPERATOR_OR_SIGN = "operator_or_sign"
    SYMBOL_BINDING = "symbol_binding"
    INDEX_OR_SUBSCRIPT = "index_or_subscript"


@dataclass
class CandidateSpan:
    """A span of text identified as a perturbation candidate."""
    span_id: str
    span_type: SpanType
    text: str                          # exact verbatim text from the paper
    paragraph_index: int               # which paragraph (0-based)
    char_offset: int                   # character offset within the full document
    context: str = ""                  # surrounding text for the LLM
    compatible_categories: list[ErrorCategory] = field(default_factory=list)


@dataclass
class Perturbation:
    """A single error to inject."""
    perturbation_id: str
    span_id: str                       # references a CandidateSpan
    category: ErrorCategory
    original: str                      # exact text to find (from span store)
    perturbed: str                     # replacement text
    why_wrong: str                     # explanation of why this breaks internal consistency
    support_span_ids: list[str] = field(default_factory=list)  # other spans that prove it's wrong


@dataclass
class PerturbationResult:
    """Result of scoring a reviewer against injected perturbations."""
    n_injected: int
    n_detected: int
    recall: float
    n_total_comments: int
    n_false_positives: int
    false_positive_rate: float
    detected: list[str]                # perturbation_ids
    missed: list[str]                  # perturbation_ids
    by_category: dict[str, dict]       # category -> {injected, detected, recall}
