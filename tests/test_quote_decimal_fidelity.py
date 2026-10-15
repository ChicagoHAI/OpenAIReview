"""Quote-fidelity regressions using recorded source text; no API calls.

The rejection cases intentionally fail until numeric localization is fixed.
They test source attribution, not scientific correctness or numeric equivalence.
"""

import json
from pathlib import Path

import pytest

from reviewer.utils import locate_comment_in_document


@pytest.fixture(scope="module")
def recorded_sources():
    artifact = Path(__file__).resolve().parents[1] / "examples/review_results/260218458v1.json"
    data = json.loads(artifact.read_text(encoding="utf-8"))
    paragraphs = {p["index"]: p["text"] for p in data["paragraphs"]}
    score_sentence = next(
        line.strip() for line in paragraphs[37].splitlines() if "4.7 out of 5" in line
    )
    return {37: score_sentence, 98: paragraphs[98]}


@pytest.mark.parametrize("variant", ["exact", "whitespace", "punctuation", "no_decimal"])
def test_locator_keeps_supported_recorded_quotes(recorded_sources, variant):
    source = recorded_sources[37]
    quotes = {
        "exact": source,
        "whitespace": source.replace(" is high, with ", " is  high,\nwith "),
        "punctuation": source.replace("high, with", "high; with"),
        "no_decimal": "rated quality of the evaluation outputs by MechEvalAgent is high",
    }

    assert locate_comment_in_document(quotes[variant], [source]) == 0


def test_locator_keeps_recorded_quote_with_multiple_decimals(recorded_sources):
    source = recorded_sources[98]

    assert locate_comment_in_document(source, [source]) == 0


@pytest.mark.parametrize(
    "paragraph_index, original, substituted",
    [(37, "4.7", "9.876543210"), (98, "1.57", "1.58")],
    ids=["single_absent_decimal", "one_of_multiple_decimals_altered"],
)
def test_locator_rejects_quote_with_absent_decimal(
    recorded_sources, paragraph_index, original, substituted
):
    source = recorded_sources[paragraph_index]
    assert original in source
    assert substituted not in source
    quote = source.replace(original, substituted, 1)
    located = locate_comment_in_document(quote, [source])

    assert located is None, (
        f"Changed decimal {original} -> {substituted} is absent from source "
        f"paragraph {paragraph_index}, but locator accepted candidate {located}"
    )
