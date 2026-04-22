"""Adapter interface for competitor review systems.

An adapter wraps a third-party review system and returns a `NormalizedReview`
— the orchestrator handles paragraph assignment and JSON merging so adapters
only have to translate their system's output into our schema.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class NormalizedComment:
    """One review comment in the openaireview-compatible shape.

    ``extra`` holds adapter-specific fields (e.g. severity, confidence) that
    get emitted as top-level keys on the comment dict in the result JSON.
    Consumers that don't know about a key ignore it — the schema is additive.
    """

    title: str
    quote: str
    explanation: str
    comment_type: str = "technical"
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class NormalizedReview:
    comments: list[NormalizedComment]
    overall_feedback: str = ""
    cost_usd: float | None = None
    # "measured" if pulled from the competitor's own usage tracking;
    # "estimated" if derived from a token-count × price calculation.
    cost_method: str = "estimated"
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    model: str = ""


class CompetitorAdapter(ABC):
    """Base class for competitor review systems."""

    #: Short name used in configs and the registry (e.g. "coarse").
    name: str = ""

    #: Env vars that must be set for this adapter to run.
    required_env: tuple[str, ...] = ()

    @abstractmethod
    def method_key(self, model: str) -> str:
        """Return the method-key written into result JSON (e.g. 'coarse__glm-4.6').

        Convention: ``<competitor>__<short_model>``, matching the openaireview
        ``progressive__<short_model>`` pattern so all methods for a paper
        live under one ``methods`` dict.
        """

    @abstractmethod
    def review(self, pdf: Path, model: str, cfg: dict) -> NormalizedReview:
        """Run the competitor on a PDF and return normalized output.

        Args:
            pdf: Absolute path to the paper PDF.
            model: Model ID from manifest.json (e.g. 'z-ai/glm-4.6').
            cfg: Adapter-specific options from the YAML config.
        """
