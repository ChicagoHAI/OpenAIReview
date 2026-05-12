"""Data models for the reviewer."""

from dataclasses import dataclass, field


@dataclass
class Comment:
    """A comment (issue) found by the reviewer."""
    title: str
    quote: str          # the flagged text from the paper
    explanation: str    # reviewer's explanation
    comment_type: str   # "technical" or "logical"
    paragraph_index: int | None = None  # 0-based index in split paragraphs

    def to_dict(self) -> dict:
        d = {
            "title": self.title,
            "quote": self.quote,
            "explanation": self.explanation,
            "comment_type": self.comment_type,
        }
        if self.paragraph_index is not None:
            d["paragraph_index"] = self.paragraph_index
        return d


@dataclass
class ReviewResult:
    """Output of a review method."""
    method: str
    paper_slug: str
    comments: list[Comment] = field(default_factory=list)
    overall_feedback: str = ""
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_cost_usd: float = 0.0      # actual cost summed from API responses (OpenRouter only)
    cost_source: str | None = None   # "openrouter" if total_cost_usd is real; else None
    model: str = ""
    reasoning_effort: str | None = None
    raw_responses: list[str] = field(default_factory=list)

    @property
    def num_comments(self) -> int:
        return len(self.comments)

    def add_usage(self, usage: dict) -> None:
        """Accumulate one chat() usage dict into this result."""
        self.total_prompt_tokens += usage.get("prompt_tokens", 0)
        self.total_completion_tokens += usage.get("completion_tokens", 0)
        cost = usage.get("cost_usd")
        if cost:
            self.total_cost_usd += float(cost)
        src = usage.get("cost_source")
        if src and self.cost_source is None:
            self.cost_source = src

    def to_dict(self) -> dict:
        return {
            "method": self.method,
            "paper_slug": self.paper_slug,
            "overall_feedback": self.overall_feedback,
            "comments": [c.to_dict() for c in self.comments],
            "num_comments": self.num_comments,
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "model": self.model,
        }
