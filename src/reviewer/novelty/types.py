"""Data types shared across the novelty pipeline."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class Chunk:
    """A retrievable unit of text.

    ``text`` is what gets indexed (BM25) and embedded. It already carries a
    short contextual header (paper title + section) so that a chunk that says
    "our method" is still retrievable on its own.
    """

    chunk_id: str
    doc_id: str
    text: str
    section: str = ""
    kind: str = "passage"  # "passage" | "abstract" | "claim"
    position: int = 0      # order within the source document

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CandidatePaper:
    """A prior paper found on the web."""

    paper_id: str          # canonical id, e.g. "arxiv:2310.06825", "doi:10.1/x", "s2:abc"
    title: str
    abstract: str = ""
    year: int | None = None
    published: str = ""    # ISO date when known
    url: str = ""
    authors: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)  # which search backends returned it
    arxiv_id: str = ""
    doi: str = ""
    full_text: str = ""    # filled only when --full-text fetches it

    def to_dict(self, include_text: bool = False) -> dict:
        d = asdict(self)
        if not include_text:
            d.pop("full_text", None)
        return d


@dataclass
class Hit:
    """One retrieved chunk for a claim, with per-retriever diagnostics."""

    chunk: Chunk
    fused_score: float
    dense_score: float | None = None   # cosine similarity (vectors are L2-normalised)
    bm25_score: float | None = None
    dense_rank: int | None = None
    bm25_rank: int | None = None

    def to_dict(self) -> dict:
        return {
            "chunk_id": self.chunk.chunk_id,
            "paper_id": self.chunk.doc_id,
            "section": self.chunk.section,
            "text": self.chunk.text,
            "fused_score": round(self.fused_score, 6),
            "dense_score": None if self.dense_score is None else round(self.dense_score, 4),
            "bm25_score": None if self.bm25_score is None else round(self.bm25_score, 4),
            "dense_rank": self.dense_rank,
            "bm25_rank": self.bm25_rank,
        }


@dataclass
class ClaimAssessment:
    """Retrieval evidence (and optional LLM verdict) for one claim."""

    claim: Chunk
    hits: list[Hit] = field(default_factory=list)
    max_similarity: float | None = None
    similarity_z: float | None = None   # how far the top hit stands out from the pool
    verdict: str | None = None          # "anticipated" | "partial" | "novel" (LLM judge)
    explanation: str = ""
    key_difference: str = ""
    evidence_chunk_id: str | None = None

    def to_dict(self) -> dict:
        return {
            "claim": self.claim.text,
            "claim_section": self.claim.section,
            "max_similarity": None if self.max_similarity is None else round(self.max_similarity, 4),
            "similarity_z": None if self.similarity_z is None else round(self.similarity_z, 3),
            "verdict": self.verdict,
            "explanation": self.explanation,
            "key_difference": self.key_difference,
            "evidence_chunk_id": self.evidence_chunk_id,
            "hits": [h.to_dict() for h in self.hits],
        }


@dataclass
class NoveltyReport:
    paper_slug: str
    title: str
    queries: list[str] = field(default_factory=list)
    candidates: list[CandidatePaper] = field(default_factory=list)
    claims: list[ClaimAssessment] = field(default_factory=list)
    related_papers: list[dict] = field(default_factory=list)
    novelty_score: float | None = None
    score_basis: str = ""
    config: dict = field(default_factory=dict)
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0

    def to_dict(self) -> dict:
        return {
            "paper_slug": self.paper_slug,
            "title": self.title,
            "novelty_score": None if self.novelty_score is None else round(self.novelty_score, 3),
            "score_basis": self.score_basis,
            "queries": self.queries,
            "related_papers": self.related_papers,
            "claims": [c.to_dict() for c in self.claims],
            "candidates": [c.to_dict() for c in self.candidates],
            "config": self.config,
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
        }
