"""Competitor review systems benchmarked against openaireview.

Each competitor lives behind a `CompetitorAdapter` (see base.py). The
orchestrator (run_competitors.py) is adapter-agnostic — it handles the
paper loop, per-model queues, idempotency, paragraph-index assignment,
and result-JSON merging. Adding a new competitor = drop a new adapter
class + register it in registry.py + add a configs/<name>.yaml.
"""
from .base import CompetitorAdapter, NormalizedComment, NormalizedReview
from .registry import get_adapter, list_adapters

__all__ = [
    "CompetitorAdapter",
    "NormalizedComment",
    "NormalizedReview",
    "get_adapter",
    "list_adapters",
]
