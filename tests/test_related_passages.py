"""Unit tests for related_passages — distinctive-token extraction and whole-paper search."""

import sys
from pathlib import Path

# Make the benchmarks/perturbation package importable as `perturbation`.
_REPO = Path(__file__).resolve().parents[1]
_BENCHMARKS = _REPO / "benchmarks"
if str(_BENCHMARKS) not in sys.path:
    sys.path.insert(0, str(_BENCHMARKS))

from perturbation.models import CandidateSpan, SpanType
from perturbation.related_passages import (
    _extract_distinctive_tokens,
    find_related_passages,
)


def _make_span(text: str, span_id: str = "S0000") -> CandidateSpan:
    return CandidateSpan(
        span_id=span_id,
        span_type=SpanType.EQUATION_INLINE,
        text=text,
        context="",
        error_type="surface",
    )


# ---------------------------------------------------------------------------
# Token extraction
# ---------------------------------------------------------------------------

def test_extract_distinctive_tokens_latex_cmds():
    # \alpha (>=2 letters) is kept; \a is rejected by the ≥2-letter rule.
    toks = _extract_distinctive_tokens(r"\alpha + \beta")
    assert r"\alpha" in toks
    assert r"\beta" in toks


def test_extract_distinctive_tokens_skips_short_latex_escapes():
    toks = _extract_distinctive_tokens(r"\a \b foo")
    # Single-letter escapes are rejected.
    assert r"\a" not in toks
    assert r"\b" not in toks


def test_extract_distinctive_tokens_scripted_identifiers():
    toks = _extract_distinctive_tokens(r"W_{ij} and x_{t+1}")
    assert any("W_{ij}" == t for t in toks)
    assert any("x_{t+1}" == t for t in toks)


def test_extract_distinctive_tokens_assignment():
    toks = _extract_distinctive_tokens("n = 100")
    # The full "n = 100" should be captured as an assignment token.
    assert any(t.startswith("n") and "100" in t for t in toks)


def test_extract_distinctive_tokens_bare_literal_not_assigned_is_rejected():
    # Bare "0.5" alone is not an assignment, not a LaTeX cmd, not a script.
    # It gets no match from any pattern, so no tokens.
    toks = _extract_distinctive_tokens("value is 0.5 somewhere")
    # No pattern should match just "0.5" — the output must not contain it.
    assert "0.5" not in toks


def test_extract_distinctive_tokens_named_refs():
    toks = _extract_distinctive_tokens("see Theorem 2 above")
    assert any("Theorem" in t and "2" in t for t in toks)


def test_extract_distinctive_tokens_latex_ref():
    toks = _extract_distinctive_tokens(r"\eqref{eq:loss}")
    assert any(r"\eqref" in t for t in toks)


def test_extract_distinctive_tokens_dedup():
    toks = _extract_distinctive_tokens(r"\alpha + \alpha")
    # Should appear once, not twice.
    assert toks.count(r"\alpha") == 1


# ---------------------------------------------------------------------------
# find_related_passages
# ---------------------------------------------------------------------------

def test_find_related_passages_hits_downstream_symbol():
    paper = (
        "In Section 2 we let $\\alpha = 0.5$ denote the learning rate.\n\n"
        "Later in Section 7, the update rule is $x_{t+1} = x_t - \\alpha g_t$, "
        "which converges for \\alpha sufficiently small."
    )
    span_text = r"$\alpha = 0.5$"
    span_offset = paper.find(span_text)
    assert span_offset != -1

    span = _make_span(span_text)
    passages = find_related_passages(span, paper, span_offset, max_passages=5)
    # At least one passage referencing \alpha downstream.
    assert len(passages) >= 1
    # The span's own offset should be excluded.
    for p in passages:
        assert not (span_offset <= p["offset"] < span_offset + len(span_text))
    # The snippet should contain \alpha.
    assert any("\\alpha" in p["snippet"] for p in passages)


def test_find_related_passages_empty_when_no_downstream_reference():
    paper = "A one-off equation: $x = 0.5$ that is never referenced again anywhere."
    span_text = "$x = 0.5$"
    span_offset = paper.find(span_text)
    span = _make_span(span_text)
    passages = find_related_passages(span, paper, span_offset)
    # With an assignment-token "x = 0.5", the span is excluded from matching itself,
    # so 0 passages.
    assert passages == []


def test_find_related_passages_caps_at_max():
    # Make a paper with many downstream references to \alpha.
    paper = "Define \\alpha here.\n\n" + ("use \\alpha again. " * 20)
    span_text = "\\alpha here"
    span_offset = paper.find(span_text)
    span = _make_span(span_text)
    passages = find_related_passages(span, paper, span_offset, max_passages=3)
    assert len(passages) <= 3


def test_find_related_passages_no_distinctive_tokens():
    # Span has no LaTeX/scripted/assignment/named-ref content — should be empty.
    span = _make_span("just some english prose here")
    paper = "just some english prose here and elsewhere"
    passages = find_related_passages(span, paper, 0)
    assert passages == []
