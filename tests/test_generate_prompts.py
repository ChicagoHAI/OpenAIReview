"""Unit tests for perturbation generator prompt variants."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
_BENCHMARKS = _REPO / "benchmarks"
if str(_BENCHMARKS) not in sys.path:
    sys.path.insert(0, str(_BENCHMARKS))

from perturbation.generate import _prompt_for


def test_prompt_for_surface_window_toggles_substantive_guidance():
    prompt_on, _ = _prompt_for("surface", "window", substantive_guidance=True)
    prompt_off, _ = _prompt_for("surface", "window", substantive_guidance=False)

    assert "TYPO-SHAPED error" in prompt_on
    assert "TYPO-SHAPED error" not in prompt_off
    assert "SUBSTANTIVE, DETECTABLE errors" in prompt_on
    assert "seeded errors in academic math papers" in prompt_off

    # Quote policy should stay the same in window mode.
    assert "contradicts_quote: str — OPTIONAL" in prompt_on
    assert "contradicts_quote: str — OPTIONAL" in prompt_off


def test_prompt_for_formal_related_keeps_required_quote_when_guidance_off():
    prompt_on, _ = _prompt_for("formal", "related", substantive_guidance=True)
    prompt_off, _ = _prompt_for("formal", "related", substantive_guidance=False)

    assert "A TYPO-SHAPED error is a local slip" in prompt_on
    assert "A TYPO-SHAPED error is a local slip" not in prompt_off

    # Required-quote behavior should stay the same in related mode.
    required_quote_line = "`contradicts_quote` must be a copy-paste substring of the paper."
    assert required_quote_line in prompt_on
    assert required_quote_line in prompt_off
