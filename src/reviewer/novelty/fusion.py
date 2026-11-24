"""Rank fusion for hybrid (sparse + dense) retrieval."""

from __future__ import annotations

from collections import defaultdict


def reciprocal_rank_fusion(
    rankings: list[list[int]],
    k: int = 60,
    weights: list[float] | None = None,
) -> list[tuple[int, float]]:
    """Reciprocal Rank Fusion (Cormack, Clarke & Buettcher, SIGIR 2009).

    ``score(d) = sum_r w_r / (k + rank_r(d))`` with 1-based ranks.

    RRF only uses ranks, so it needs no score calibration between BM25 (an
    unbounded sum) and cosine similarity (bounded, model-dependent). ``k=60``
    is the value from the original paper and is robust in practice.
    """
    weights = weights or [1.0] * len(rankings)
    if len(weights) != len(rankings):
        raise ValueError("weights must match rankings")
    fused: dict[int, float] = defaultdict(float)
    for ranking, w in zip(rankings, weights):
        for rank, doc in enumerate(ranking, start=1):
            fused[doc] += w / (k + rank)
    return sorted(fused.items(), key=lambda kv: (-kv[1], kv[0]))
