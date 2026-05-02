"""Adapters for running system review systems on the perturbation benchmark.

The unified `run_benchmark.py` runner selects a system by `system:`
key in its YAML config and dispatches review work through the `System`
protocol below.
"""

from ._base import CellKey, System, CostReport, ReviewJob, ReviewResult
from .coarse import CoarseSystem
from .openaireview import OpenAIReviewSystem
from .reviewer3 import Reviewer3System


SYSTEMS: dict[str, System] = {
    "openaireview": OpenAIReviewSystem(),
    "coarse": CoarseSystem(),
    "reviewer3": Reviewer3System(),
}


def get_system(name: str) -> System:
    try:
        return SYSTEMS[name]
    except KeyError:
        raise ValueError(
            f"unknown system {name!r}; valid: {sorted(SYSTEMS)}"
        ) from None


__all__ = [
    "CellKey", "System", "CostReport", "ReviewJob", "ReviewResult",
    "SYSTEMS", "get_system",
    "CoarseSystem", "OpenAIReviewSystem", "Reviewer3System",
]
