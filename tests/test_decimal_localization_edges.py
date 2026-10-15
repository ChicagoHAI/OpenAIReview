"""Offline boundaries for literal fixed-decimal quote localization."""

import pytest

from reviewer.models import Comment
from reviewer.utils import (
    assign_paragraph_indices,
    locate_comment_in_document,
    locate_comments_in_window,
)


@pytest.mark.parametrize("quote, source", [
    ("The estimate is 0.95.", "The estimate is 10.95."),
    ("The estimate is 4.70.", "The estimate is 4.7."),
    ("The estimate is 4.7.", "The estimate is 4.70."),
    ("The estimate is -4.7.", "The estimate is 4.7."),
    ("The estimate is 4.7.", "The estimate is -4.7."),
    ("The estimate is +4.7.", "The estimate is 4.7."),
])
def test_rejects_different_complete_decimal_spellings(quote, source):
    assert locate_comment_in_document(quote, [source]) is None


def test_keeps_matching_signed_decimal():
    source = "The estimate is -4.7."
    assert locate_comment_in_document(source, [source]) == 0


def test_repeated_value_checks_presence_not_occurrence_count():
    source = "The reported score is 4.7 in this experiment."
    quote = "The reported score is 4.7; this score is 4.7."
    assert locate_comment_in_document(quote, [source]) == 0


def test_source_can_contain_additional_decimals():
    source = "The reported score is 4.7, while another score is 2.2."
    assert locate_comment_in_document("The reported score is 4.7", [source]) == 0


def test_selects_later_compatible_paragraph():
    quote = "The reported score is 4.7."
    paragraphs = [quote.replace("4.7", "4.8"), quote]
    assert locate_comment_in_document(quote, paragraphs) == 1


def test_decimal_presence_does_not_replace_text_matching():
    quote = "The carefully measured kinetic velocity of the experiment is 4.7."
    assert locate_comment_in_document(quote, ["zzzzzzzz 4.7 qqqqqqqq"]) is None


def test_checks_decimals_beyond_the_matching_prefix():
    prefix = "An unchanged sentence about the experiment. " * 30
    assert len(prefix) > 1000
    source = prefix + "The reported score is 4.7."
    quote = prefix + "The reported score is 4.70."
    assert locate_comment_in_document(quote, [source]) is None


@pytest.mark.parametrize("quote, paragraphs", [("", ["Text."]), ("Text.", [])])
def test_preserves_empty_input_fallback(quote, paragraphs):
    assert locate_comment_in_document(quote, paragraphs) is None


@pytest.mark.parametrize("quote, source", [
    ("The model_v4.7 output is described here.", "The model_v4.8 output is described here."),
    ("The build4.7beta output is described here.", "The build4.8beta output is described here."),
    ("The scale is 4.7e2 in this experiment.", "The scale is 4.8e2 in this experiment."),
])
def test_unsupported_numeric_spellings_keep_legacy_matching(quote, source):
    # Identifiers and scientific notation are not fixed-decimal evidence checks.
    assert locate_comment_in_document(quote, [source]) == 0


@pytest.mark.parametrize("windowed", [False, True])
def test_attribution_keeps_payload_and_safe_unlocated_value(windowed):
    quote = "The reported score is 4.7."
    source = quote + " Details of the experiment are described in the following discussion." * 2
    paragraphs = [source.replace("4.7", "4.8"), source]
    comments = [
        Comment("Score", quote, "Check the explanation.", "technical"),
        Comment("Unlocated", quote.replace("4.7", "4.70"), "Retain this comment.", "technical", 0),
    ]
    payloads = [{k: v for k, v in c.to_dict().items() if k != "paragraph_index"} for c in comments]
    if windowed:
        chunks = [([i], paragraph) for i, paragraph in enumerate(paragraphs)]
        locate_comments_in_window(comments, 0, chunks, paragraphs)
    else:
        assign_paragraph_indices(comments, "\n\n".join(paragraphs))

    assert comments[0].paragraph_index == 1
    assert comments[1].paragraph_index is None
    assert [{k: v for k, v in c.to_dict().items() if k != "paragraph_index"} for c in comments] == payloads
