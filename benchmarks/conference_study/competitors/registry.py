"""Registry mapping competitor name → adapter class.

Adding a new competitor:
    1. Write `competitors/<name>_adapter.py` with a `CompetitorAdapter` subclass.
    2. Register it in `_REGISTRY` below.
    3. Create `configs/<name>.yaml` with `competitor: <name>` and any options.
"""
from __future__ import annotations

from .base import CompetitorAdapter
from .coarse_adapter import CoarseAdapter

_REGISTRY: dict[str, type[CompetitorAdapter]] = {
    "coarse": CoarseAdapter,
}


def get_adapter(name: str) -> CompetitorAdapter:
    if name not in _REGISTRY:
        raise KeyError(
            f"unknown competitor: {name!r} "
            f"(registered: {sorted(_REGISTRY)})"
        )
    return _REGISTRY[name]()


def list_adapters() -> list[str]:
    return sorted(_REGISTRY)
