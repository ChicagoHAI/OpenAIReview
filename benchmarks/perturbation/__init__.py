"""Automated seeded-perturbation benchmark for academic paper reviews.

Pipeline: extract candidates → generate perturbations → validate → inject → score.
"""

from .extract import extract_abstract, extract_candidates
from .generate import generate_perturbations
from .inject import inject_perturbations
from .models import (
    CandidateSpan,
    Error,
    Perturbation,
    PerturbationResult,
    SpanType,
)
from .score import score_review
from .validate import validate_perturbations

__all__ = [
    "extract_abstract",
    "extract_candidates",
    "generate_perturbations",
    "validate_perturbations",

    "inject_perturbations",
    "score_review",
    "CandidateSpan",
    "Perturbation",
    "PerturbationResult",
    "SpanType",
    "Error",
]
