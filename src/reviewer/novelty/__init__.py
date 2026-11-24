"""Retrieval-augmented novelty assessment.

Compares a submission's contribution claims against prior work found on
arXiv / Semantic Scholar / OpenAlex using hybrid retrieval (BM25 + dense
embeddings with an ANN index, fused by Reciprocal Rank Fusion), then
optionally asks the review LLM to judge each claim against the evidence.

Requires the ``novelty`` extra: ``pip install "openaireview[novelty]"``.
"""

from .pipeline import NoveltyConfig, render_markdown, run_novelty
from .types import CandidatePaper, Chunk, ClaimAssessment, Hit, NoveltyReport

__all__ = [
    "NoveltyConfig", "run_novelty", "render_markdown",
    "CandidatePaper", "Chunk", "ClaimAssessment", "Hit", "NoveltyReport",
]
