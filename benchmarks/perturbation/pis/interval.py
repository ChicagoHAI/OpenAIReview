from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import Any, Dict

_MASS_TOL = 1e-9
_SUM_TOL = 1e-6


@dataclass(frozen=True)
class PISInterval:
    """Credal/evidential interval over the inconsistency hypothesis H.

    Dempster-Shafer mass assignment on the binary frame {H, not-H}:
      m_support   : committed mass that H holds  (evidence FOR inconsistency)
      m_against   : committed mass that H fails  (evidence AGAINST inconsistency)
      m_unresolved: uncommitted mass (missing / ambiguous / CONFLICTING evidence)

    Derived:
      L     = Bel(H) = m_support
      U     = Pl(H)  = m_support + m_unresolved = 1 - m_against
      width = U - L  = m_unresolved            (evidential uncertainty)
    """

    m_support: float
    m_against: float
    m_unresolved: float
    source: str = "witness_product"

    def __post_init__(self) -> None:
        for name in ("m_support", "m_against", "m_unresolved"):
            v = getattr(self, name)
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
                raise ValueError(f"{name} must be a finite number, got {v!r}")
            if v < -_MASS_TOL or v > 1.0 + _MASS_TOL:
                raise ValueError(f"{name} out of [0,1]: {v}")
        total = self.m_support + self.m_against + self.m_unresolved
        if abs(total - 1.0) > _SUM_TOL:
            raise ValueError(
                f"masses must sum to 1, got {total!r}: "
                f"({self.m_support}, {self.m_against}, {self.m_unresolved})"
            )
        for name in ("m_support", "m_against", "m_unresolved"):
            object.__setattr__(self, name, min(1.0, max(0.0, getattr(self, name))))

    @property
    def L(self) -> float:            # Bel(H)
        return self.m_support

    @property
    def U(self) -> float:            # Pl(H) = 1 - m_against
        return self.m_support + self.m_unresolved

    @property
    def width(self) -> float:        # evidential uncertainty
        return self.m_unresolved

    @property
    def ambiguity(self) -> float:    # distance of [L,U] from the nearest pole {0,1}
        return min(self.U, 1.0 - self.L)

    @property
    def midpoint(self) -> float:
        return 0.5 * (self.L + self.U)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "m_support": self.m_support, "m_against": self.m_against,
            "m_unresolved": self.m_unresolved,
            "L": self.L, "U": self.U, "width": self.width,
            "ambiguity": self.ambiguity, "source": self.source,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "PISInterval":
        return cls(m_support=float(d["m_support"]), m_against=float(d["m_against"]),
                   m_unresolved=float(d["m_unresolved"]),
                   source=str(d.get("source", "deserialized")))

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)

    @classmethod
    def from_json(cls, s: str) -> "PISInterval":
        return cls.from_dict(json.loads(s))