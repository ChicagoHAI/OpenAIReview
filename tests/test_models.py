"""Unit tests for data models."""

from reviewer.models import Comment, ReviewResult


def test_comment_to_dict():
    c = Comment(title="Bug", quote="x=1", explanation="wrong", comment_type="technical", paragraph_index=3)
    d = c.to_dict()
    assert d["title"] == "Bug"
    assert d["paragraph_index"] == 3


def test_comment_to_dict_no_paragraph():
    c = Comment(title="Bug", quote="x", explanation="y", comment_type="logical")
    d = c.to_dict()
    assert "paragraph_index" not in d
    assert "suggestion" not in d


def test_comment_to_dict_with_suggestion():
    c = Comment(
        title="Bug",
        quote="x",
        explanation="y",
        comment_type="logical",
        suggestion="Clarify the claim and add a supporting citation.",
    )
    d = c.to_dict()
    assert d["suggestion"] == "Clarify the claim and add a supporting citation."


def test_review_result_num_comments():
    r = ReviewResult(method="test", paper_slug="slug")
    assert r.num_comments == 0
    r.comments.append(Comment(title="A", quote="q", explanation="e", comment_type="technical"))
    assert r.num_comments == 1


def test_review_result_to_dict():
    r = ReviewResult(method="progressive", paper_slug="paper1", model="test-model")
    r.comments.append(Comment(title="Issue", quote="q", explanation="e", comment_type="logical"))
    d = r.to_dict()
    assert d["method"] == "progressive"
    assert d["num_comments"] == 1
    assert len(d["comments"]) == 1
