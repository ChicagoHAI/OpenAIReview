"""Unit tests for perturbation benchmark scoring metrics."""

import sys
import types
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
_SRC = _REPO / "src"
_BENCHMARKS = _REPO / "benchmarks"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
if str(_BENCHMARKS) not in sys.path:
    sys.path.insert(0, str(_BENCHMARKS))

if "tiktoken" not in sys.modules:
    sys.modules["tiktoken"] = types.SimpleNamespace(
        get_encoding=lambda _name: types.SimpleNamespace(
            encode=lambda text: text.split(),
            decode=lambda tokens: " ".join(tokens),
        )
    )
if "rapidfuzz" not in sys.modules:
    sys.modules["rapidfuzz"] = types.SimpleNamespace(
        fuzz=types.SimpleNamespace(
            token_set_ratio=lambda a, b: 100 if set(a.split()) == set(b.split()) else 0
        )
    )
if "sentence_transformers" not in sys.modules:
    sys.modules["sentence_transformers"] = types.SimpleNamespace(
        SentenceTransformer=lambda _name: None,
        util=types.SimpleNamespace(cos_sim=lambda _a, _b: 0.0),
    )

from perturbation.models import Error, Perturbation
from perturbation.score import score_review


def _perturbation(pid: str, perturbed: str) -> Perturbation:
    return Perturbation(
        perturbation_id=pid,
        span_id=f"S_{pid}",
        error=Error.OPERATOR_OR_SIGN,
        original="x + y",
        offset=0,
        perturbed=perturbed,
        why_wrong="same explanation",
    )


def _comment(quote: str, explanation: str = "same explanation") -> dict:
    return {
        "title": "issue",
        "quote": quote,
        "explanation": explanation,
        "comment_type": "technical",
    }


def test_comment_efficiency_metrics_count_detection_at_comment_zero_for_all_cutoffs():
    result = score_review(
        [_perturbation("P0", "x - y")],
        [_comment("The paper states x - y.")],
        model="unused",
        method="fuzzy",
    )

    assert result.first_matching_comment_index == {"P0": 0}
    assert result.n_detected_at_1 == 1
    assert result.n_detected_at_3 == 1
    assert result.n_detected_at_5 == 1
    assert result.n_detected_at_10 == 1
    assert result.recall_at_1 == 1.0
    assert result.recall_at_3 == 1.0
    assert result.recall_at_5 == 1.0
    assert result.recall_at_10 == 1.0


def test_comment_efficiency_metrics_count_detection_at_comment_four_for_larger_cutoffs_only():
    comments = [
        _comment("unrelated 0"),
        _comment("unrelated 1"),
        _comment("unrelated 2"),
        _comment("unrelated 3"),
        _comment("The paper states a >= b."),
    ]

    result = score_review(
        [_perturbation("P0", "a >= b")],
        comments,
        model="unused",
        method="fuzzy",
    )

    assert result.first_matching_comment_index == {"P0": 4}
    assert result.n_detected_at_1 == 0
    assert result.n_detected_at_3 == 0
    assert result.n_detected_at_5 == 1
    assert result.n_detected_at_10 == 1
    assert result.recall_at_1 == 0.0
    assert result.recall_at_3 == 0.0
    assert result.recall_at_5 == 1.0
    assert result.recall_at_10 == 1.0


def test_comment_efficiency_metrics_handle_no_detections_safely():
    result = score_review(
        [_perturbation("P0", "x - y")],
        [_comment("unrelated"), _comment("also unrelated")],
        model="unused",
        method="fuzzy",
    )

    assert result.n_detected == 0
    assert result.n_detected_at_1 == 0
    assert result.recall_at_10 == 0.0
    assert result.comments_per_detected_error is None
    assert result.detected_per_comment == 0.0
