"""Unit tests for the perturbation scorer (benchmarks/perturbation/score.py).

Covers the substring gate, the LLM-judge threshold, and the score_review
bookkeeping without any network calls: the gate and the fuzzy matcher are
deterministic, and the LLM path is exercised with a stubbed `chat`.
"""

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import benchmarks.perturbation.score as score  # noqa: E402
from benchmarks.perturbation.models import Error, Perturbation  # noqa: E402


def _perturbation(pid, perturbed, why_wrong):
    return Perturbation(
        perturbation_id=pid,
        span_id="s",
        error=Error.NUMERIC_PARAMETER,
        original="orig",
        offset=0,
        perturbed=perturbed,
        why_wrong=why_wrong,
    )


def _comment(quote, explanation):
    return {"quote": quote, "explanation": explanation}


# ---- _llm_substring_gate: does the quote overlap the perturbed text? ----

def test_gate_false_on_empty_inputs():
    assert score._llm_substring_gate("", "the coefficient is 0.95") is False
    assert score._llm_substring_gate("coefficient", "") is False


def test_gate_true_when_quote_contained_in_perturbed():
    # Normalized quote is a substring of the perturbed text.
    assert score._llm_substring_gate("the error", "we found the error in eq 3") is True


def test_gate_true_on_high_coverage_without_containment():
    # Not a substring, but ~all of the quote's characters are matched.
    assert score._llm_substring_gate("abcdefghij", "abcdefghXYij") is True


def test_gate_false_on_low_coverage():
    assert score._llm_substring_gate("abcdefghij", "abXXXXXXXX") is False


# ---- explanation matchers ----

def test_explanation_match_fuzzy():
    assert score._explanation_match_fuzzy("X is wrong", "X is wrong") is True
    assert score._explanation_match_fuzzy("completely unrelated text here", "X is wrong") is False


@pytest.mark.parametrize("response, threshold, expected", [
    ("4", 3, True),    # rating clears the cutoff
    ("3", 3, True),    # rating equals the cutoff
    ("2", 3, False),   # rating below the cutoff
    ("4", 5, False),   # same rating, stricter cutoff
    ("not-an-int", 3, False),  # unparseable judge reply is treated as no match
])
def test_explanation_match_llm_threshold(monkeypatch, response, threshold, expected):
    monkeypatch.setattr(score, "chat", lambda **kwargs: (response, {}))
    got = score._explanation_match_llm("expl", "why", model="m", threshold=threshold)
    assert got is expected


# ---- score_review bookkeeping ----

def test_default_does_not_gate(monkeypatch):
    # Regression guard for the opt-in fix: with substring_gate off (default), a
    # comment whose quote does not overlap the perturbed text is still scored,
    # so an explanation match counts even when the quote is unrelated.
    perts = [_perturbation("p1", "the coefficient is 0.95", "p1 reason"),
             _perturbation("p2", "the exponent is 3", "p2 reason")]
    comments = [_comment("zzzzz qqqqq", "p1 reason"),
                _comment("zzzzz qqqqq", "p2 reason")]
    r = score.score_review(perts, comments, model="m", method="fuzzy")
    assert r.n_detected == 2 and r.recall == 1.0
    assert sorted(r.detected) == ["p1", "p2"] and r.missed == []


def test_gate_on_filters_non_overlapping_quotes():
    perts = [_perturbation("p1", "the coefficient is 0.95", "p1 reason")]
    # Explanation would match, but the quote does not overlap the perturbed text.
    comments = [_comment("zzzzz qqqqq", "p1 reason")]
    r = score.score_review(perts, comments, model="m", method="fuzzy", substring_gate=True)
    assert r.n_detected == 0 and r.recall == 0.0 and r.missed == ["p1"]


def test_gate_on_keeps_overlapping_quotes():
    perts = [_perturbation("p1", "the coefficient is 0.95", "p1 reason")]
    comments = [_comment("coefficient is 0.95", "p1 reason")]  # quote overlaps perturbed
    r = score.score_review(perts, comments, model="m", method="fuzzy", substring_gate=True)
    assert r.n_detected == 1 and r.detected == ["p1"]


def test_each_perturbation_counted_once():
    # Two comments match the same perturbation; it should count once (break).
    perts = [_perturbation("p1", "the coefficient is 0.95", "p1 reason")]
    comments = [_comment("q", "p1 reason"), _comment("q", "p1 reason")]
    r = score.score_review(perts, comments, model="m", method="fuzzy")
    assert r.n_detected == 1 and r.n_total_comments == 2


def test_missed_when_no_comment_matches():
    perts = [_perturbation("p1", "the coefficient is 0.95", "p1 reason")]
    comments = [_comment("q", "an entirely different observation")]
    r = score.score_review(perts, comments, model="m", method="fuzzy")
    assert r.n_detected == 0 and r.missed == ["p1"]


def test_empty_perturbations_recall_zero():
    r = score.score_review([], [_comment("q", "e")], model="m", method="fuzzy")
    assert r.n_injected == 0 and r.recall == 0.0 and r.detected == [] and r.missed == []


def test_llm_method_threshold_flows_through(monkeypatch):
    # The score_review threshold reaches the judge: a rating of 3 detects at
    # threshold 3 but not at threshold 4.
    monkeypatch.setattr(score, "chat", lambda **kwargs: ("3", {}))
    perts = [_perturbation("p1", "the coefficient is 0.95", "p1 reason")]
    comments = [_comment("q", "p1 reason")]
    assert score.score_review(perts, comments, model="m", threshold=3).n_detected == 1
    assert score.score_review(perts, comments, model="m", threshold=4).n_detected == 0
