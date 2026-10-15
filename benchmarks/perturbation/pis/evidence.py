from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, List, Mapping, Sequence, Tuple

from .interval import PISInterval

POLARITY_SUPPORTS = "supports_H"
POLARITY_AGAINST = "against_H"
POLARITY_UNRESOLVED = "unresolved"
POLARITIES = (POLARITY_SUPPORTS, POLARITY_AGAINST, POLARITY_UNRESOLVED)

SOURCE_TYPES = (
    "quote", "context", "span_comparison", "error_type_meta",
    "related_passage", "background_knowledge", "missing_evidence",
)


def _strict01(name: str, v: Any) -> float:
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise ValueError(f"{name} must be a number, got {type(v).__name__}")
    v = float(v)
    if not math.isfinite(v):
        raise ValueError(f"{name} must be finite, got {v}")
    if v < 0.0 or v > 1.0:
        raise ValueError(f"{name} must be in [0,1], got {v}")
    return v


@dataclass(frozen=True)
class EvidenceItem:
    """One independent evidential witness bearing on H."""

    source_type: str
    description: str
    polarity: str
    strength: float      # contribution toward its polarity if accepted, in [0,1]
    reliability: float   # trustworthiness as a witness, in [0,1]
    justification: str = ""

    def __post_init__(self) -> None:
        if self.source_type not in SOURCE_TYPES:
            raise ValueError(f"unknown source_type: {self.source_type!r}")
        if self.polarity not in POLARITIES:
            raise ValueError(f"unknown polarity: {self.polarity!r}")
        if not (isinstance(self.description, str) and self.description.strip()):
            raise ValueError("description must be a non-empty string")
        if not isinstance(self.justification, str):
            raise ValueError("justification must be a string")
        object.__setattr__(self, "strength", _strict01("strength", self.strength))
        object.__setattr__(self, "reliability", _strict01("reliability", self.reliability))

    @property
    def commitment(self) -> float:
        """Effective per-witness detection probability."""
        return min(1.0, self.strength * self.reliability)

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> Tuple["EvidenceItem", List[str]]:
        """Build an item from model output. Out-of-range numbers are clamped and
        EVERY clamp is reported as a repair (never silent). Unknown enums or
        missing keys are hard failures (trigger retry), never imputed."""
        repairs: List[str] = []
        for key in ("source_type", "description", "polarity", "strength", "reliability"):
            if key not in payload:
                raise ValueError(f"missing key {key!r}")
        source_type = payload["source_type"]
        if source_type not in SOURCE_TYPES:
            raise ValueError(f"unknown source_type: {source_type!r}")
        polarity = payload["polarity"]
        if polarity not in POLARITIES:
            raise ValueError(f"unknown polarity: {polarity!r}")
        description = payload["description"]
        if not (isinstance(description, str) and description.strip()):
            raise ValueError("description must be a non-empty string")

        def _num(key: str) -> float:
            v = payload[key]
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
                raise ValueError(f"{key} must be a finite number, got {v!r}")
            v = float(v)
            if v < 0.0 or v > 1.0:
                clamped = min(1.0, max(0.0, v))
                repairs.append(f"{key} clamped {v} -> {clamped}")
                return clamped
            return v

        justification = payload.get("justification", "")
        if not isinstance(justification, str):
            justification = str(justification)
        item = cls(source_type=source_type, description=description.strip(),
                   polarity=polarity, strength=_num("strength"),
                   reliability=_num("reliability"), justification=justification)
        return item, repairs


def aggregate_evidence(items: Sequence[EvidenceItem]) -> PISInterval:
    """Combine evidence items into a PIS interval (witness model).

    Each committed item i is an independent noisy witness for its polarity with
    detection probability c_i = strength_i * reliability_i. Define

        A_plus  = prod_{i: supports_H} (1 - c_i)   # P(no supporting witness fires)
        A_minus = prod_{i: against_H}  (1 - c_i)   # P(no opposing witness fires)

    Under independence the unit mass splits as:

        m(H)     = (1 - A_plus)  * A_minus                    # only + fires
        m(not-H) = A_plus * (1 - A_minus)                     # only - fires
        m(Theta) = A_plus*A_minus + (1-A_plus)*(1-A_minus)    # none or BOTH fire

    This is exactly the Dubois-Prade disjunctive combination of simple support
    functions m_i({sigma_i}) = c_i, m_i(Theta) = 1 - c_i: conflicting mass is
    committed to Theta (unresolved), never cancelled, never normalized away.
    The four terms sum to 1 because they factor as
    ((1-A_plus)+A_plus) * (A_minus+(1-A_minus)) = 1.

    'unresolved'-polarity items are descriptive only: they never change the
    committed masses (absence of committed witnesses already implies vacuity).

    Determinism: items are processed in canonical order (descending
    commitment, then source_type, description), so the result is bitwise
    order-independent for a fixed multiset of items.
    """
    ordered = sorted(items, key=lambda it: (-it.commitment, it.source_type, it.description))
    a_plus = 1.0
    a_minus = 1.0
    for it in ordered:
        c = it.commitment
        if c <= 0.0:
            continue
        if it.polarity == POLARITY_SUPPORTS:
            a_plus *= 1.0 - c
        elif it.polarity == POLARITY_AGAINST:
            a_minus *= 1.0 - c
    m_support = (1.0 - a_plus) * a_minus
    m_against = a_plus * (1.0 - a_minus)
    # Algebraically equals a_plus*a_minus + (1-a_plus)*(1-a_minus); computed by
    # subtraction so the three masses sum to 1 exactly in floating point.
    m_unresolved = max(0.0, 1.0 - m_support - m_against)
    return PISInterval(m_support=m_support, m_against=m_against, m_unresolved=m_unresolved)