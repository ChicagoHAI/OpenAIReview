"""Pydantic models + dataclasses that cross the LangGraph checkpoint boundary.

Kept in a separate module (not the `python -m` entry script) so that their
__module__ is `review_rounds.models` rather than `__main__` — which stops
the "Deserializing unregistered type" msgpack warning the SqliteSaver
otherwise emits when rehydrating state from an earlier process.

Pydantic BaseModel subclasses double as structured-output schemas passed
to `ChatOpenAI.with_structured_output(...)`.
"""

from typing import Literal

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Section splitting
# ---------------------------------------------------------------------------


class Section(BaseModel):
    idx: int
    heading: str
    text: str
    chars: int


# ---------------------------------------------------------------------------
# Orchestrator output
# ---------------------------------------------------------------------------


class PlanOutput(BaseModel):
    """Produced by plan_assignments. Personas list is the set of reviewer
    personas; assignments maps each persona_idx (0, 1, 2) to the section
    indices that persona is responsible for reviewing.

    Constraint communicated in the prompt (not enforceable in the schema):
    every section must be covered by at least one persona, and each persona
    should get roughly equal load."""

    personas: list[str] = Field(description="One-sentence reviewer personas")
    # List-of-lists instead of dict: outer index = persona index, inner list =
    # section indices for that persona. Avoids the JSON-schema "no int dict
    # keys" issue and the "persona_1 vs 0 vs 1" naming ambiguity that cost
    # an afternoon — see NOTES.md.
    assignments: list[list[int]] = Field(
        description="assignments[i] = section indices assigned to personas[i]"
    )


# ---------------------------------------------------------------------------
# Per-section comment output
# ---------------------------------------------------------------------------


CommentType = Literal["methodology", "claim_accuracy", "presentation", "missing_information"]
Confidence = Literal["high", "medium", "low"]


class Comment(BaseModel):
    """One issue flagged by a persona while reviewing one section.

    `source_section_idx` and `persona_idx` are stamped after the structured
    output returns; the LLM doesn't need to fill them (the caller already
    knows which section/persona it's running on). Kept on the model so the
    downstream viz + consolidation nodes have everything inline."""

    title: str = Field(description="Short headline for the issue")
    quote: str = Field(description="Exact verbatim text from the paper")
    explanation: str = Field(description="Why this is a problem and what would fix it")
    comment_type: CommentType
    confidence: Confidence
    source_section_idx: int = -1   # stamped post-hoc
    persona_idx: int = -1          # stamped post-hoc


class CommentList(BaseModel):
    """Structured output schema for one (persona, section) review call."""

    comments: list[Comment]


# ---------------------------------------------------------------------------
# Self-critique output (end of persona's internal section loop)
# ---------------------------------------------------------------------------


class CriticVerdict(BaseModel):
    """Output of the per-persona self_critique step. kept_indices are
    indices into the persona's section_comments list — the LLM decides
    which of its own findings survive."""

    kept_indices: list[int] = Field(
        description="Indices of comments to keep (drop low-confidence or off-target ones)"
    )
    reason: str = Field(description="One sentence explaining the pruning decisions")


# ---------------------------------------------------------------------------
# Consolidation output (severity tiering)
# ---------------------------------------------------------------------------


Severity = Literal["major", "moderate", "minor"]


class ConsolidatedIssue(BaseModel):
    """A final issue after dedup + severity tiering. Same fields as Comment
    plus severity and the provenance list. merged_from lists the indices of
    the raw comments that got folded in — useful for auditing."""

    title: str
    quote: str
    explanation: str
    comment_type: CommentType
    severity: Severity
    source_section_idx: int = -1
    merged_from: list[int] = Field(default_factory=list)


class ConsolidationOutput(BaseModel):
    issues: list[ConsolidatedIssue]
    overall_feedback: str = Field(
        description="2-4 sentence paper-level recommendation, for the viz overall_feedback slot"
    )
