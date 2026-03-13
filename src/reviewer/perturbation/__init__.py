"""Automated seeded-perturbation benchmark for academic paper reviews.

Pipeline: extract candidates → generate perturbations → validate → inject → score.
"""

from .extract import add_line_numbers, extract_candidates
from .generate import generate_freeform, generate_from_candidates
from .inject import inject_perturbations
from .models import (
    CandidateSpan,
    Difficulty,
    ErrorCategory,
    Perturbation,
    PerturbationResult,
    SpanType,
)
from .score import score_review
from .validate import validate_perturbations

__all__ = [
    "extract_candidates",
    "add_line_numbers",
    "generate_from_candidates",
    "generate_freeform",
    "validate_perturbations",
    "inject_perturbations",
    "score_review",
    "CandidateSpan",
    "Perturbation",
    "PerturbationResult",
    "SpanType",
    "ErrorCategory",
    "Difficulty",
]
