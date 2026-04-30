"""Unit tests for the substantive-error verifier (mocked chat())."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
_BENCHMARKS = _REPO / "benchmarks"
if str(_BENCHMARKS) not in sys.path:
    sys.path.insert(0, str(_BENCHMARKS))

import pytest

from perturbation.models import CandidateSpan, Error, Perturbation, SpanType
from perturbation import verify as verify_mod
from perturbation.verify import (
    _parse_verdict,
    _pick_quote,
    structural_precheck,
    verify_perturbations,
)


def _make_perturbation(pid: str, span_id: str, quote: str = "some quote") -> Perturbation:
    return Perturbation(
        perturbation_id=pid,
        span_id=span_id,
        error=Error.OPERATOR_OR_SIGN,
        original="original text",
        perturbed="perturbed text",
        why_wrong="it contradicts the quote",
        contradicts_quote=quote,
    )


def _make_span(
    span_id: str,
    related: list[dict] | None = None,
    verifier_related: list[dict] | None = None,
) -> CandidateSpan:
    return CandidateSpan(
        span_id=span_id,
        span_type=SpanType.EQUATION_INLINE,
        text="x",
        context="",
        error_type="surface",
        related_passages=related or [],
        verifier_related_passages=verifier_related or [],
    )


# ---------------------------------------------------------------------------
# _pick_quote — the random-sample fallback
# ---------------------------------------------------------------------------

def test_pick_quote_uses_generator_quote_if_present():
    p = _make_perturbation("P001_S0", "S0", quote="GEN_QUOTE")
    span = _make_span("S0", verifier_related=[{"offset": 10, "snippet": "RANDOM_A"}])
    q, src = _pick_quote(p, span)
    assert q == "GEN_QUOTE"
    assert src == "generator"


def test_pick_quote_samples_random_when_generator_empty():
    p = _make_perturbation("P001_S0", "S0", quote="")
    span = _make_span(
        "S0",
        verifier_related=[
            {"offset": 10, "snippet": "RANDOM_A"},
            {"offset": 50, "snippet": "RANDOM_B"},
            {"offset": 90, "snippet": "RANDOM_C"},
        ],
    )
    q, src = _pick_quote(p, span)
    assert src == "random-sampled"
    assert q in {"RANDOM_A", "RANDOM_B", "RANDOM_C"}


def test_pick_quote_deterministic_by_perturbation_id():
    # Same perturbation_id → same sampled quote. Different id → possibly different.
    span = _make_span(
        "S0",
        verifier_related=[
            {"offset": 10, "snippet": "RANDOM_A"},
            {"offset": 50, "snippet": "RANDOM_B"},
            {"offset": 90, "snippet": "RANDOM_C"},
        ],
    )
    p1 = _make_perturbation("P001_S0", "S0", quote="")
    q1a, _ = _pick_quote(p1, span)
    q1b, _ = _pick_quote(p1, span)
    assert q1a == q1b  # deterministic for same id


def test_pick_quote_none_available():
    p = _make_perturbation("P001_S0", "S0", quote="")
    span = _make_span("S0", verifier_related=[])
    q, src = _pick_quote(p, span)
    assert src == "none-available"


# ---------------------------------------------------------------------------
# _parse_verdict
# ---------------------------------------------------------------------------

def test_parse_verdict_valid_substantive():
    v, reason = _parse_verdict('{"verdict": "substantive", "reason": "contradicts Theorem 2"}')
    assert v == "substantive"
    assert "Theorem" in reason


def test_parse_verdict_valid_typo_shaped():
    v, _ = _parse_verdict('{"verdict": "typo-shaped", "reason": "surface slip"}')
    assert v == "typo-shaped"


def test_parse_verdict_not_an_error():
    v, _ = _parse_verdict('{"verdict": "not-an-error", "reason": "actually consistent"}')
    assert v == "not-an-error"


def test_parse_verdict_unknown_verdict():
    v, _ = _parse_verdict('{"verdict": "maybe", "reason": "idk"}')
    assert v == "parse-error"


def test_parse_verdict_no_json():
    v, _ = _parse_verdict("the verdict is substantive")
    assert v == "parse-error"


def test_parse_verdict_embedded_in_prose():
    # Model sometimes wraps the JSON in prose; we should still recover it.
    v, _ = _parse_verdict('Here is my answer: {"verdict": "substantive", "reason": "ok"} .')
    assert v == "substantive"


def test_parse_verdict_code_fenced():
    # Model sometimes wraps in ```json ... ```.
    resp = '```json\n{"verdict": "substantive", "reason": "ok"}\n```'
    v, _ = _parse_verdict(resp)
    assert v == "substantive"


def test_parse_verdict_reason_contains_apostrophe():
    # Reason string contains an apostrophe and nested chars that might trip a brittle parser.
    resp = '{"verdict": "substantive", "reason": "The system\'s dimension {L+1} differs."}'
    v, reason = _parse_verdict(resp)
    assert v == "substantive"
    assert "dimension" in reason


# ---------------------------------------------------------------------------
# verify_perturbations — full fan-out (mocked chat)
# ---------------------------------------------------------------------------

def test_verify_perturbations_buckets_verdicts(monkeypatch):
    # Canned responses keyed by perturbation_id, so we can verify each
    # perturbation ends up in the right bucket.
    canned = {
        "P001_S0": '{"verdict": "substantive", "reason": "good"}',
        "P002_S1": '{"verdict": "typo-shaped", "reason": "slip"}',
        "P003_S2": '{"verdict": "not-an-error", "reason": "fine"}',
        "P004_S3": 'not-json-at-all',
    }

    def fake_chat(messages, model, max_tokens, reasoning_effort):
        content = messages[0]["content"]
        # Each prompt includes the perturbation_id indirectly via original/perturbed —
        # fall back to scanning for any canned key present in the prompt.
        for pid, resp in canned.items():
            if pid in content:
                return resp, {"prompt_tokens": 1, "completion_tokens": 1, "model": model}
        # Default: use the fact that we embed .why_wrong which we can control.
        return canned["P004_S3"], {"prompt_tokens": 1, "completion_tokens": 1, "model": model}

    monkeypatch.setattr(verify_mod, "chat", fake_chat)

    # Put the perturbation_id in `original` so fake_chat can route correctly.
    # (The new VERIFIER_PROMPT does not include why_wrong, so we use original instead.)
    perturbations = [
        Perturbation("P001_S0", "S0", Error.OPERATOR_OR_SIGN, "P001_S0", "p", "", "q"),
        Perturbation("P002_S1", "S1", Error.OPERATOR_OR_SIGN, "P002_S1", "p", "", "q"),
        Perturbation("P003_S2", "S2", Error.OPERATOR_OR_SIGN, "P003_S2", "p", "", "q"),
        Perturbation("P004_S3", "S3", Error.OPERATOR_OR_SIGN, "P004_S3", "p", "", "q"),
    ]
    candidates = [_make_span("S0"), _make_span("S1"), _make_span("S2"), _make_span("S3")]

    accepted, rejected, stats = verify_perturbations(
        perturbations, candidates, model="fake", reasoning_effort=None, max_workers=4,
    )

    # Substantive → accepted.
    accepted_ids = {p.perturbation_id for p in accepted}
    assert accepted_ids == {"P001_S0"}

    rejected_ids = {p.perturbation_id for p, _ in rejected}
    assert rejected_ids == {"P002_S1", "P003_S2", "P004_S3"}

    assert stats["substantive"] == 1
    assert stats["typo-shaped"] == 1
    assert stats["not-an-error"] == 1
    assert stats["parse-error"] == 1
    assert stats["n_input"] == 4


def test_verify_perturbations_empty_input():
    accepted, rejected, stats = verify_perturbations([], [], model="fake")
    assert accepted == []
    assert rejected == []
    assert stats["n_input"] == 0
    assert stats["substantive"] == 0


def test_verify_perturbations_chat_exception_becomes_parse_error(monkeypatch):
    def raising_chat(**_kw):
        raise RuntimeError("provider down")

    # signature needs to match; wrap it
    def fake_chat(messages, model, max_tokens, reasoning_effort):
        raise RuntimeError("provider down")

    monkeypatch.setattr(verify_mod, "chat", fake_chat)

    perturbations = [_make_perturbation("P001_S0", "S0")]
    candidates = [_make_span("S0")]
    accepted, rejected, stats = verify_perturbations(
        perturbations, candidates, model="fake", reasoning_effort=None, max_workers=2,
    )
    assert accepted == []
    assert len(rejected) == 1
    assert rejected[0][1].verdict == "parse-error"
    assert stats["parse-error"] == 1


# ---------------------------------------------------------------------------
# structural_precheck
# ---------------------------------------------------------------------------


def _precheck_perturbation(orig: str, pert: str, err: Error = Error.OPERATOR_OR_SIGN) -> Perturbation:
    return Perturbation(
        perturbation_id="P",
        span_id="S",
        error=err,
        original=orig,
        perturbed=pert,
        why_wrong="",
        contradicts_quote="q",
    )


def test_structural_precheck_mixed_inequality_chain():
    p = _precheck_perturbation("$0 < w < L/2$", "$0 < w > L/2$")
    status, reason = structural_precheck(p)
    assert status == "reject-typo"
    assert "mixed-direction" in reason


def test_structural_precheck_broken_sandwich_ge_le():
    orig = r"\begin{align} a \le b \le c \end{align}"
    pert = r"\begin{align} a \ge b \le c \end{align}"
    status, reason = structural_precheck(_precheck_perturbation(orig, pert))
    assert status == "reject-typo"
    assert "mixed-direction" in reason


def test_structural_precheck_runaway_span():
    p = _precheck_perturbation("$\\Lambda_j$", "a" * 500)
    status, reason = structural_precheck(p)
    assert status == "reject-typo"
    assert "runaway" in reason


def test_structural_precheck_escape_artifact():
    # Perturbed has literal '\n' (2-char backslash-n) where original has real newlines.
    orig = "$$\n    K = ...\n$$"
    pert = "$$\\n    K = ...\\n$$"
    status, reason = structural_precheck(_precheck_perturbation(orig, pert, Error.INDEX_OR_SUBSCRIPT))
    assert status == "reject-typo"
    assert "escape artifact" in reason


def test_structural_precheck_does_not_flag_latex_macros_starting_with_n_t_r():
    # `\neq`, `\nabla`, `\tau`, `\rightarrow`, `\top`, `\rm` must NOT trigger the
    # escape-artifact rule even when they are newly introduced by the perturbation.
    for macro in (r"\neq", r"\nabla", r"\tau", r"\rightarrow", r"\top", r"\rm"):
        pert = f"$x = {macro}$"
        status, _ = structural_precheck(_precheck_perturbation("$x = y$", pert))
        assert status == "keep", f"false positive on macro {macro!r}"


def test_structural_precheck_keeps_clean_sign_flip():
    status, _ = structural_precheck(_precheck_perturbation("$d > w/2$", "$d < w/2$"))
    assert status == "keep"


def test_structural_precheck_keeps_clean_numeric_change():
    status, _ = structural_precheck(_precheck_perturbation("$10^{-6}$", "$10^{-3}$"))
    assert status == "keep"
