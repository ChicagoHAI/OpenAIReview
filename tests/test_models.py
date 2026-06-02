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


def test_comment_to_dict_omits_empty_suggested_fix():
    c = Comment(title="Bug", quote="x", explanation="y", comment_type="logical")
    d = c.to_dict()
    assert "suggested_fix" not in d


def test_comment_to_dict_includes_suggested_fix():
    c = Comment(
        title="Bug", quote="x", explanation="y", comment_type="technical",
        suggested_fix="Use x = y instead.",
    )
    d = c.to_dict()
    assert d["suggested_fix"] == "Use x = y instead."


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
