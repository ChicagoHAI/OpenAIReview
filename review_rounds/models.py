"""Dataclasses that cross the LangGraph checkpoint boundary.

Kept in a separate module (not the `python -m` entry script) so their
__module__ is `review_rounds.models` rather than `__main__` — which stops
the "Deserializing unregistered type" msgpack warning the SqliteSaver
otherwise emits when rehydrating state from an earlier process.
"""

from dataclasses import dataclass


@dataclass
class Draft:
    """One persona's finished draft. Carries enough state that the time-travel
    demo (update_state on a completed run) can rewrite a single entry without
    re-running the other personas' subgraphs."""

    persona: str
    persona_idx: int
    initial: str
    challenge: str
    verdict: str  # "keep" | "revise"
    verdict_reason: str
    final: str
