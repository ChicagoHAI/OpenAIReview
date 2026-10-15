"""Unit tests for progressive method helpers (no API calls)."""

from reviewer.method_progressive import merge_into_passages, split_into_paragraphs


def test_split_and_merge_roundtrip():
    """Paragraphs fed into merge should cover all text."""
    text = "\n\n".join(f"Paragraph {i} with enough text to pass the minimum character threshold easily." for i in range(20))
    paragraphs = split_into_paragraphs(text, min_chars=50)
    passages = merge_into_passages(paragraphs, target_chars=500)
    # Every paragraph index should appear in exactly one passage
    all_indices = []
    for indices, _ in passages:
        all_indices.extend(indices)
    assert sorted(all_indices) == list(range(len(paragraphs)))


def test_merge_respects_target():
    paragraphs = ["x" * 200 for _ in range(10)]
    passages = merge_into_passages(paragraphs, target_chars=500)
    # Should produce multiple passages
    assert len(passages) > 1
    # No passage text (excluding separators) should massively exceed target
    for _, text in passages:
        assert len(text) < 1000


def test_consolidate_restores_suggested_fix_by_quote(monkeypatch):
    """A fix the consolidation model moved onto another issue is replaced by that issue's own fix."""
    import json

    from reviewer import method_progressive
    from reviewer.models import Comment, ReviewResult

    comments = [
        Comment(title="A", quote="x = -y", explanation="sign", comment_type="technical",
                paragraph_index=3, suggested_fix="Use x = y."),
        Comment(title="B", quote="for all n", explanation="cond", comment_type="logical",
                paragraph_index=5),
    ]
    merged = [{"title": "A", "quote": "x = -y", "explanation": "sign", "type": "technical",
               "suggested_fix": "Assume n > 0."}]
    monkeypatch.setattr(method_progressive, "chat",
                        lambda **kw: (json.dumps(merged), {"prompt_tokens": 0, "completion_tokens": 0}))
    out = method_progressive.consolidate_comments(comments, "m", ReviewResult(method="t", paper_slug="s"))
    assert out[0].suggested_fix == "Use x = y."
    assert out[0].paragraph_index == 3
