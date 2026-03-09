"""Integration test: review a deliberately bad paragraph and check comments are generated.

Requires OPENROUTER_API_KEY to be set. Skipped automatically if not available.
"""

import os

import pytest

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

_has_api_key = any(
    os.environ.get(k)
    for k in ("OPENROUTER_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY")
)

pytestmark = pytest.mark.skipif(
    not _has_api_key,
    reason="No API key set (OPENROUTER/OPENAI/ANTHROPIC/GEMINI)",
)

BAD_PAPER = """\
# A Study of Widget Performance

## Abstract

We study the performance of widgets under various conditions.

## 1. Introduction

Let x denote the number of widgets produced per hour. We define the production rate as
r = x / t, where t is the total time in hours.

## 2. Analysis

From Section 1, we know that r = x / t. Therefore the total output is x = r * t.
However, we also claim that x = r + t, which follows directly from the definition.
Note that the variance of x is Var(x) = E[x]^2 - E[x^2], which is always positive.
Furthermore, since r > 0 and t > 0, we conclude that x < 0 in all cases.
By Theorem 7 (see Section 9), this contradicts our earlier assumption, but we ignore this.
The sample size is N=10000 in Table 1 but N=500 in the methods section.

## 3. Conclusion

We have conclusively proven that widgets are optimal in all possible scenarios,
surpassing all existing and future methods.
"""


def test_zero_shot_finds_issues():
    from reviewer.method_zero_shot import review_zero_shot

    result = review_zero_shot(
        paper_slug="test-bad-paper",
        document_content=BAD_PAPER,
        model="anthropic/claude-sonnet-4-6",
    )
    print(f"zero_shot found {result.num_comments} comments")
    for c in result.comments:
        print(f"  - [{c.comment_type}] {c.title}")
    assert result.num_comments >= 2, f"Expected at least 2 issues, got {result.num_comments}"


def test_progressive_finds_issues():
    from reviewer.method_progressive import review_progressive

    consolidated, full = review_progressive(
        paper_slug="test-bad-paper",
        document_content=BAD_PAPER,
        model="anthropic/claude-sonnet-4-6",
    )
    print(f"progressive found {consolidated.num_comments} comments (full: {full.num_comments})")
    for c in consolidated.comments:
        print(f"  - [{c.comment_type}] {c.title}")
    assert full.num_comments >= 2, f"Expected at least 2 issues in full, got {full.num_comments}"
    assert consolidated.num_comments >= 1, f"Expected at least 1 issue after consolidation"
    # Consolidation should not increase the count
    assert consolidated.num_comments <= full.num_comments
