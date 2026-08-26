"""Prompt schema tests."""

from reviewer import prompts


def test_all_review_prompts_request_suggestions():
    review_prompts = [
        prompts.DEEP_CHECK_PROMPT,
        prompts.DEEP_CHECK_PROGRESSIVE_PROMPT,
        prompts.ZERO_SHOT_PROMPT,
        prompts.LARGE_PAPER_CHUNK_PROMPT,
    ]

    for prompt in review_prompts:
        assert '"suggestion"' in prompt
        assert "concrete, actionable revision" in prompt
        assert "Avoid generic advice" in prompt
