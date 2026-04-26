"""Section-level stateful review pipeline over OpenAIReview outputs.

A LangGraph StateGraph that mirrors the OpenAIReview Claude Code skill's
section-level review flow:

    extract_pdf → split_sections → summarize_paper → plan_assignments
                                                          │
                                              (Send × 3)  ▼
                                          review_as_persona (subgraph, loops assigned sections)
                                                          │  (reducer: comments)
                                                          ▼
                                                     consolidate  (dedup + severity tiering)
                                                          │
                                                          ▼
                                                     human_gate   (interrupt)
                                                          ├─→ publish (md + viz JSON)
                                                          ├─→ consolidate  (edit path)
                                                          └─→ review_as_persona  (redo)

LLM calls use `langchain_openai.ChatOpenAI.with_structured_output(method="json_schema", schema=PydanticModel)`
so every node gets a validated Pydantic instance instead of raw JSON strings.

Stateful CLI:
    python -m review_rounds.review_rounds run <paper> [--thread-id ID]
    python -m review_rounds.review_rounds resume <thread-id> <decision>
    python -m review_rounds.review_rounds history <thread-id>
    python -m review_rounds.review_rounds fork <thread-id> <checkpoint> --persona N
    python -m review_rounds.review_rounds dump <thread-id>
    python -m review_rounds.review_rounds topology

Main-CLI shim entry:
    from review_rounds.review_rounds import run_oneshot
    run_oneshot(paper_path=..., output_dir=Path("./review_results"))
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys
import tempfile
import uuid
from operator import add
from pathlib import Path
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, Send, interrupt

from reviewer.parsers import parse_document
from reviewer.skill.scripts.prepare_workspace import split_sections as _skill_split_sections
from reviewer.utils import count_tokens, truncate_text

from review_rounds.models import (
    Comment,
    CommentList,
    ConsolidatedIssue,
    ConsolidationOutput,
    CriticVerdict,
    PlanOutput,
    Section,
)
from review_rounds.viz import write_viz_json


load_dotenv()  # pulls OPENROUTER_API_KEY + MISTRAL_API_KEY from .env

CHECKPOINT_DB = Path(__file__).parent / ".checkpoints.db"
OUTPUTS_DIR = Path(__file__).parent / "outputs"
DEFAULT_VIZ_DIR = Path("review_results")

MODEL = os.environ.get("REVIEW_ROUNDS_MODEL", "moonshotai/kimi-k2.6")
OCR_ENGINE = "mistral"
PAPER_MAX_TOKENS = 20_000
PER_CALL_MAX_TOKENS = 8_096


# ---------------------------------------------------------------------------
# Usage tracking (OpenRouter reports cost per response; accumulate across nodes)
# ---------------------------------------------------------------------------


class _UsageCollector(BaseCallbackHandler):
    """LangChain callback that accumulates token + cost usage across every
    LLM call in the graph.

    OpenRouter returns the upstream dollar cost in
    `completion.usage.cost`; LangChain exposes it via
    response.llm_output['token_usage']['cost']. Reasoning tokens land in
    `completion_tokens_details.reasoning_tokens`.

    Uses a module-level singleton; each LLM-calling node emits
    `USAGE.snapshot()` into the `usage` state channel (element-wise-max
    reducer) so totals survive process restarts at the human_gate interrupt."""

    def __init__(self) -> None:
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.reasoning_tokens = 0
        self.cost_usd = 0.0
        self.calls = 0

    def on_llm_end(self, response, **kwargs):  # type: ignore[override]
        self.calls += 1
        usage: dict = {}
        if response.llm_output and "token_usage" in response.llm_output:
            usage = response.llm_output["token_usage"] or {}
        else:
            # with_structured_output chains sometimes bury usage in the
            # per-generation metadata instead of llm_output. Fall back.
            for gens in response.generations:
                for gen in gens:
                    meta = getattr(gen, "generation_info", None) or {}
                    usage = meta.get("token_usage") or meta.get("usage_metadata") or usage
        self.prompt_tokens += int(usage.get("prompt_tokens", 0) or 0)
        self.completion_tokens += int(usage.get("completion_tokens", 0) or 0)
        self.cost_usd += float(usage.get("cost", 0) or 0)
        details = usage.get("completion_tokens_details") or {}
        if isinstance(details, dict):
            self.reasoning_tokens += int(details.get("reasoning_tokens", 0) or 0)

    def snapshot(self) -> dict:
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "reasoning_tokens": self.reasoning_tokens,
            "cost_usd": round(self.cost_usd, 6),
            "calls": self.calls,
        }


USAGE = _UsageCollector()


# ---------------------------------------------------------------------------
# LLM client (structured output via LangChain)
# ---------------------------------------------------------------------------


def _make_llm(max_tokens: int = PER_CALL_MAX_TOKENS, reasoning_max: int = 1024) -> ChatOpenAI:
    """Construct a ChatOpenAI pointed at OpenRouter.

    kimi-k2.6 is a reasoning model — left unconstrained it can spend 3000+
    reasoning tokens per call, which starves the visible-output budget and
    throws LengthFinishReasonError before the JSON schema completes. Cap
    reasoning explicitly via OpenRouter's extra_body.reasoning.max_tokens.
    Passed as a top-level ChatOpenAI kwarg (not model_kwargs) — LangChain
    warns on the latter form in 1.x."""
    return ChatOpenAI(
        model=MODEL,
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_API_KEY"],
        max_tokens=max_tokens,
        # timeout covers each attempt; max_retries bounds total time per node.
        # Reasoning models on OpenRouter can legitimately take 2-3 min on
        # complex structured-output calls (kimi-k2.6 spending 4k reasoning
        # tokens + 16k visible). A 90s cutoff would abort real calls
        # mid-flight and waste retries. 300s + 2 retries bounds total to
        # ~15 min/node and avoids killing legit slow generations.
        timeout=300,
        max_retries=2,
        extra_body={"reasoning": {"max_tokens": reasoning_max}},
        callbacks=[USAGE],
    )


# ---------------------------------------------------------------------------
# State shapes
# ---------------------------------------------------------------------------


def _merge_edits(left: dict[str, str], right: dict[str, str]) -> dict[str, str]:
    """Reducer for the edits channel: right wins on key collision."""
    return {**left, **right}


def _merge_dropped(left: list[int] | None, right: list[int] | None) -> list[int]:
    """Set-union reducer for dropped_personas.

    `comments` uses `operator.add` (append), so you can't "undrop" via
    replacement. The fork command instead writes persona indices here;
    `consolidate` filters `comments` by this set before running. Stored
    as a list (not set) because the sqlite checkpointer msgpack encoder
    doesn't round-trip sets."""
    return sorted(set(left or []) | set(right or []))


def _merge_usage(left: dict | None, right: dict | None) -> dict:
    """Reducer for the usage channel: element-wise max.

    USAGE is module-level and monotonically increasing within a process, so
    every write is a cumulative snapshot. Max across concurrent writes
    (three parallel persona subgraphs) keeps the largest/latest total
    without double-counting."""
    left = left or {}
    right = right or {}
    out = dict(left)
    for k, v in right.items():
        if isinstance(v, (int, float)) and isinstance(out.get(k), (int, float)):
            out[k] = max(out[k], v)
        else:
            out[k] = v
    return out


class ReviewState(TypedDict, total=False):
    paper_path: str
    paper_title: str
    paper_text: str
    sections: list[Section]
    summary: str
    personas: list[str]
    assignments: dict[int, list[int]]              # persona_idx -> section_idx list
    comments: Annotated[list[Comment], add]        # parallel fan-in from personas
    final_issues: list[ConsolidatedIssue]
    overall_feedback: str
    decision: str                                   # "approve" | "redo:<idx>" | "edit"
    edits: Annotated[dict[str, str], _merge_edits]
    # Fork channel: persona indices whose comments `consolidate` should
    # ignore. Union-reducer so concurrent writes survive; `_cmd_fork`
    # writes here instead of trying to replace the add-reducer comments
    # channel (which would just append).
    dropped_personas: Annotated[list[int], _merge_dropped]
    # Usage/cost tracking. Persisted in state so it survives across process
    # boundaries (run process pauses at human_gate; resume process runs
    # publish with a fresh USAGE module-level collector, so we read from
    # here instead).
    usage: Annotated[dict, _merge_usage]


class PersonaState(TypedDict, total=False):
    """Subgraph-local. The section loop accumulates raw comments into
    `section_comments` via the reducer; self_critique filters; emit writes
    to `comments` which is the boundary channel."""

    persona: str
    persona_idx: int
    summary: str
    sections: list[Section]                         # assigned slice only
    section_cursor: int
    section_comments: Annotated[list[Comment], add] # internal fan-in across sections
    comments: Annotated[list[Comment], add]         # boundary-emitted


class PersonaOutput(TypedDict, total=False):
    """Only `comments` leaves the subgraph — everything else (persona,
    section_cursor, section_comments) stays private. Without this schema,
    concurrent subgraphs would fight over non-reducer fields at fan-in."""

    comments: Annotated[list[Comment], add]
    usage: Annotated[dict, _merge_usage]


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------


SUMMARY_PROMPT = """You are an orchestrator preparing a deep review of an academic paper. \
Read the paper and write a concise 200-400 word summary covering: the research \
question, core hypothesis or contribution, key definitions, main claims, and \
how the paper is organized (a brief section map). Future reviewers will use \
this summary as context; be specific about what each section does.

Paper title: {title}

Section list:
{section_list}

Paper text (truncated):
{paper_text}
"""


PLAN_PROMPT = """You are the orchestrator for a 3-reviewer deep review of an academic \
paper. Choose three complementary reviewer personas and assign each one a \
subset of sections to review.

Rules:
- Return exactly 3 personas. Each persona: one sentence, format "A {{adjective}} {{role}} who focuses on {{concern}}".
- Every section must be covered by at least one persona.
- Roughly balance load — no persona should carry more than ⌈N/2⌉+1 sections.
- Assign sections where the persona's expertise matters; prefer disjoint assignments but allow overlap on pivotal sections.
- Use the persona indices 0, 1, 2 in the assignments map; section indices match the section list below.

Paper title: {title}

Paper summary:
{summary}

Sections (index: heading):
{section_list}
"""


REVIEW_SECTION_PROMPT = """You are reviewing ONE section of an academic paper, acting as \
this reviewer persona:

{persona}

Paper-level summary (for context):
{summary}

SECTION {section_idx}: {section_heading}
---
{section_text}
---

Flag genuine issues through your persona's lens. Each issue must:
- Quote a SHORT, EXACT, VERBATIM passage from the section above (≤200 chars).
- Explain why it is a problem and what would fix it.
- Classify comment_type as one of: methodology, claim_accuracy, presentation, missing_information.
- Assign confidence: high | medium | low.

Return 0-5 comments. Return an empty list if you find nothing substantive — \
this is not a checklist exercise. Do not invent quotes.
"""


CRITIC_PROMPT = """You are reviewing your own findings to prune weak ones before they \
go to the consolidation step. Below are the comments you (persona: {persona}) \
made across the sections you reviewed. Return the indices of the comments \
you want to KEEP.

Drop comments that are:
- Low-confidence without a strong quote.
- Repetitive of another comment in this list.
- Off-target for your persona.
- Pedantic or stylistic beyond substantive issue.

Keep comments that:
- Identify a substantive problem with a clear quote and explanation.
- Are the strongest comment on their particular issue.

Your comments (JSON, one per index):
{comments_json}
"""


CONSOLIDATION_PROMPT = """You are consolidating comments from three reviewers into a final \
severity-tiered issue list. Below are all comments the reviewers kept, with an \
index so you can cite provenance.

Your job:
1. Merge comments that flag the same underlying issue (same quote or same root cause). Keep the clearer explanation; list the merged indices in `merged_from`.
2. Assign severity to each final issue:
   - major: threatens a paper-level conclusion or core claim's validity
   - moderate: localized, fixable error that doesn't cascade
   - minor: framing, ambiguity, or mild overclaim
3. Reclassify comment_type to one of: methodology, claim_accuracy, presentation, missing_information.
4. Preserve the exact quote — do not paraphrase.
5. Also produce a 2-4 sentence `overall_feedback` suitable for a review summary.

Paper title: {title}
Paper summary: {summary}

Raw comments (JSON, indexed):
{comments_json}
"""


# ---------------------------------------------------------------------------
# Parent nodes
# ---------------------------------------------------------------------------


def extract_pdf(state: ReviewState) -> dict:
    """Parse the paper with OpenAIReview's extractor; truncate to PAPER_MAX_TOKENS."""
    title, text, _ = parse_document(state["paper_path"], ocr=OCR_ENGINE)
    if count_tokens(text) > PAPER_MAX_TOKENS:
        text = truncate_text(text, PAPER_MAX_TOKENS)
    return {"paper_title": title, "paper_text": text}


def split_sections_node(state: ReviewState) -> dict:
    """Adapter around skill/scripts/prepare_workspace.py:split_sections.

    That function writes files to disk as a side effect — we call it with
    a tmpdir, read each section file back, and build Pydantic Section
    instances. Keeps the regex + heading/8K-chunk split logic in one place
    (the skill script) rather than duplicating it here."""
    with tempfile.TemporaryDirectory() as td:
        sections_dir = Path(td)
        meta = _skill_split_sections(state["paper_text"], sections_dir)
        sections: list[Section] = []
        for i, m in enumerate(meta):
            text = (sections_dir / m["file"]).read_text(encoding="utf-8")
            sections.append(Section(idx=i, heading=m["heading"], text=text, chars=m["chars"]))
    return {"sections": sections}


def summarize_paper(state: ReviewState) -> dict:
    """Orchestrator summary — equivalent to the skill's summary.md."""
    section_list = "\n".join(f"  {s.idx}: {s.heading} ({s.chars} chars)" for s in state["sections"])
    prompt = SUMMARY_PROMPT.format(
        title=state["paper_title"],
        section_list=section_list,
        paper_text=state["paper_text"],
    )
    llm = _make_llm(max_tokens=4096)
    # Free-form summary, no Pydantic schema — not every node needs structured output.
    msg = llm.invoke(prompt)
    return {"summary": msg.content, "usage": USAGE.snapshot()}


def plan_assignments(state: ReviewState) -> dict:
    """LLM decides three personas and assigns each a section subset.

    This is the node that makes Option B (orchestrator-assigned) interesting:
    its structured output directly shapes the fan-out topology."""
    section_list = "\n".join(f"  {s.idx}: {s.heading}" for s in state["sections"])
    prompt = PLAN_PROMPT.format(
        title=state["paper_title"],
        summary=state["summary"],
        section_list=section_list,
    )
    def _fallback(reason: str) -> dict:
        print(f"  [warn] plan_assignments {reason}; using fallback personas")
        fallback_personas = [
            "A methodology-focused reviewer who focuses on experimental rigor and reproducibility",
            "A clarity-focused reviewer who focuses on exposition and logical flow",
            "A prior-art reviewer who focuses on novelty and literature positioning",
        ]
        n_sections = len(state["sections"])
        fallback_assignments = {i: [] for i in range(3)}
        for idx in range(n_sections):
            fallback_assignments[idx % 3].append(idx)
        return {
            "personas": fallback_personas,
            "assignments": fallback_assignments,
            "usage": USAGE.snapshot(),
        }

    structured = _make_llm(max_tokens=8192, reasoning_max=2048).with_structured_output(method="json_schema", schema=PlanOutput)
    try:
        plan: PlanOutput = structured.invoke(prompt)  # type: ignore[assignment]
    except Exception as e:
        # Kimi-k2.6 occasionally returns empty content after burning its
        # reasoning budget — LangChain then raises ValueError. Fall back to
        # generic personas + round-robin section assignment so the graph
        # can still proceed.
        return _fallback(f"failed: {type(e).__name__}: {str(e)[:200]}")

    # An empty `personas` list would silently ship a no-reviewer review; treat
    # it the same as a raise. Keeps the graph's downstream fan-out sane.
    if not plan.personas:
        return _fallback("returned empty personas list")

    # list[list[int]] on the wire → dict[int, list[int]] in state. Normalize
    # to exactly 3 personas + 3 assignments, padding with empty lists if the
    # LLM returned fewer.
    personas = plan.personas[:3]
    raw = list(plan.assignments[:3])
    while len(raw) < len(personas):
        raw.append([])
    assignments: dict[int, list[int]] = {i: list(raw[i]) for i in range(len(personas))}

    # Guard: every section must be covered. Leftovers go round-robin.
    covered = {idx for idxs in assignments.values() for idx in idxs}
    leftovers = [s.idx for s in state["sections"] if s.idx not in covered]
    for i, idx in enumerate(leftovers):
        assignments[i % len(personas)].append(idx)

    return {"personas": personas, "assignments": assignments, "usage": USAGE.snapshot()}


def fan_out_personas(state: ReviewState) -> list[Send]:
    """Dispatch one Send per persona, each carrying ONLY its assigned sections.

    The subgraph sees a pre-filtered `sections` list + `section_cursor=0`;
    it doesn't know about the parent's full section list."""
    assignments = state["assignments"]
    all_sections = {s.idx: s for s in state["sections"]}
    sends: list[Send] = []
    for i, persona in enumerate(state["personas"]):
        assigned_idxs = assignments.get(i, [])
        assigned = [all_sections[idx] for idx in assigned_idxs if idx in all_sections]
        sends.append(
            Send(
                "review_as_persona",
                {
                    "persona": persona,
                    "persona_idx": i,
                    "summary": state["summary"],
                    "sections": assigned,
                    "section_cursor": 0,
                },
            )
        )
    return sends


def consolidate(state: ReviewState) -> dict:
    """Dedup + severity tier all personas' comments into final_issues.

    Respects `dropped_personas` — fork writes there to exclude a persona's
    comments without mutating the add-reducer `comments` channel."""
    comments = state.get("comments", []) or []
    dropped = set(state.get("dropped_personas") or [])
    if dropped:
        before = len(comments)
        comments = [c for c in comments if c.persona_idx not in dropped]
        print(f"  [fork] consolidate: dropped {before - len(comments)} comments from personas {sorted(dropped)}")
    if not comments:
        return {"final_issues": [], "overall_feedback": "No issues flagged."}

    # Dump comments to the prompt with an index so the LLM can reference provenance.
    indexed = [
        {"index": i, **c.model_dump()} for i, c in enumerate(comments)
    ]
    import json as _json
    prompt = CONSOLIDATION_PROMPT.format(
        title=state["paper_title"],
        summary=state["summary"],
        comments_json=_json.dumps(indexed, indent=2),
    )
    # 64k visible output budget — reasoning models chew through a big chunk of
    # max_tokens invisibly, and ConsolidationOutput with 50+ nested issues
    # easily needs 15k+ tokens of visible JSON. 16k was getting truncated
    # mid-object on kimi-k2.6; 64k gives generous headroom. See NOTES R11.
    structured = _make_llm(max_tokens=65536, reasoning_max=4096).with_structured_output(method="json_schema", schema=ConsolidationOutput)
    try:
        out: ConsolidationOutput = structured.invoke(prompt)  # type: ignore[assignment]
    except Exception as e:
        # Consolidate is the last LLM call — if it fails, synthesize a
        # minimal fallback from raw comments so publish still produces a
        # viz JSON (lower quality but non-empty).
        print(f"  [warn] consolidate failed: {type(e).__name__}: {str(e)[:200]}; using raw comments as issues")
        fallback = [
            ConsolidatedIssue(
                title=c.title, quote=c.quote, explanation=c.explanation,
                comment_type=c.comment_type, severity="moderate",
                source_section_idx=c.source_section_idx, merged_from=[i],
            )
            for i, c in enumerate(comments)
        ]
        return {
            "final_issues": fallback,
            "overall_feedback": "Consolidation step failed; raw per-persona comments listed without dedup or severity tiering.",
            "usage": USAGE.snapshot(),
        }
    return {
        "final_issues": list(out.issues),
        "overall_feedback": out.overall_feedback,
        "usage": USAGE.snapshot(),
    }


def human_gate(state: ReviewState) -> dict:
    """Durable HITL pause. Payload summarizes severity tiers + issue titles."""
    issues = state.get("final_issues", []) or []
    tier_counts: dict[str, int] = {"major": 0, "moderate": 0, "minor": 0}
    for i in issues:
        tier_counts[i.severity] = tier_counts.get(i.severity, 0) + 1

    decision = interrupt(
        {
            "tier_counts": tier_counts,
            "n_issues": len(issues),
            "titles": [f"[{i.severity}] {i.title}" for i in issues],
            "overall_feedback": state.get("overall_feedback", ""),
            "prompt": (
                "Reply with one of:\n"
                "  approve                — publish as-is\n"
                "  redo:<persona_idx>     — re-run persona <idx>'s subgraph\n"
                "  edit:<key>:<value>     — stash an edit in the edits map (for consolidation hint)"
            ),
        }
    )
    if isinstance(decision, str) and decision.startswith("edit:"):
        _, k, v = decision.split(":", 2)
        return {"decision": "edit", "edits": {k: v}}
    return {"decision": decision if isinstance(decision, str) else "approve"}


def publish(state: ReviewState, config: RunnableConfig) -> dict:
    """Terminal node. Writes markdown dump + viz JSON.

    Usage is sourced from state["usage"] because publish often runs in a
    different Python process than the LLM-calling nodes (after a human_gate
    interrupt + resume), where the module-level USAGE collector is fresh.

    Output-dir routing:
      - viz JSON: `config.configurable.output_dir` if set, else
        module-level DEFAULT_VIZ_DIR (the `python -m` stateful CLI).
      - markdown: same override → alongside the viz JSON when invoked via
        the main CLI shim; OUTPUTS_DIR otherwise."""
    configurable = config.get("configurable", {}) or {}
    thread_id = configurable.get("thread_id", "unknown")
    override = configurable.get("output_dir")
    viz_dir = Path(override) if override else DEFAULT_VIZ_DIR
    md_dir = Path(override) if override else OUTPUTS_DIR
    usage = _merge_usage(state.get("usage") or {}, USAGE.snapshot())
    md_path = _write_markdown(thread_id, state, usage=usage, outputs_dir=md_dir)
    viz_path = write_viz_json(
        paper_path=state.get("paper_path", ""),
        paper_title=state.get("paper_title", ""),
        paper_text=state.get("paper_text", ""),
        issues=state.get("final_issues", []) or [],
        overall_feedback=state.get("overall_feedback", ""),
        model=MODEL,
        output_dir=viz_dir,
        usage=usage,
    )
    print(f"[saved] {md_path}")
    print(f"[saved] {viz_path}")
    print(
        f"[usage] calls={usage.get('calls', 0)} "
        f"prompt={usage.get('prompt_tokens', 0)} "
        f"completion={usage.get('completion_tokens', 0)} "
        f"reasoning={usage.get('reasoning_tokens', 0)} "
        f"cost=${usage.get('cost_usd', 0):.4f}"
    )
    return {}


def route_from_gate(state: ReviewState):
    decision = state.get("decision", "approve")
    if decision == "approve":
        return "publish"
    if decision == "edit":
        return "consolidate"
    if decision.startswith("redo:"):
        personas = state.get("personas") or []
        try:
            idx = int(decision.split(":", 1)[1])
        except ValueError:
            print(f"  [warn] redo: non-integer persona index in decision {decision!r}; publishing")
            return "publish"
        if not (0 <= idx < len(personas)):
            print(f"  [warn] redo:{idx} out of range (0..{len(personas)-1}); publishing")
            return "publish"
        all_sections = {s.idx: s for s in state["sections"]}
        assigned_idxs = state["assignments"].get(idx, [])
        assigned = [all_sections[i] for i in assigned_idxs if i in all_sections]
        return Send(
            "review_as_persona",
            {
                "persona": personas[idx],
                "persona_idx": idx,
                "summary": state["summary"],
                "sections": assigned,
                "section_cursor": 0,
            },
        )
    return "publish"


# ---------------------------------------------------------------------------
# Persona subgraph (nested internal section loop)
# ---------------------------------------------------------------------------


def _review_section(state: PersonaState) -> dict:
    """Review the current cursor's section; append comments to section_comments.

    Defensive: catches ValidationError / API errors from the structured-
    output call. OpenRouter + some models don't strictly enforce JSON
    schema — we've seen kimi return comments missing required fields
    (e.g. `title` absent). Rather than crash the whole run on one bad
    section, log and emit an empty list for that section so the loop
    keeps advancing and sibling personas stay unaffected."""
    cursor = state["section_cursor"]
    section = state["sections"][cursor]
    prompt = REVIEW_SECTION_PROMPT.format(
        persona=state["persona"],
        summary=state["summary"],
        section_idx=section.idx,
        section_heading=section.heading,
        section_text=section.text,
    )
    structured = _make_llm(max_tokens=16384, reasoning_max=4096).with_structured_output(method="json_schema", schema=CommentList)
    try:
        out: CommentList = structured.invoke(prompt)  # type: ignore[assignment]
    except Exception as e:
        print(
            f"  [warn] review_section failed for persona {state['persona_idx']} "
            f"section {section.idx}: {type(e).__name__}: {str(e)[:200]}"
        )
        return {"section_comments": [], "section_cursor": cursor + 1, "usage": USAGE.snapshot()}

    # Stamp provenance on every comment (LLM doesn't fill these).
    stamped: list[Comment] = []
    for c in out.comments:
        c.source_section_idx = section.idx
        c.persona_idx = state["persona_idx"]
        stamped.append(c)

    return {
        "section_comments": stamped,    # reducer appends
        "section_cursor": cursor + 1,    # plain write; single sequential edge
        "usage": USAGE.snapshot(),
    }


def _more_sections(state: PersonaState) -> str:
    return "review_section" if state["section_cursor"] < len(state["sections"]) else "self_critique"


def _self_critique(state: PersonaState) -> dict:
    """Prune weak comments; the returned kept_indices filter section_comments."""
    all_comments = state.get("section_comments", []) or []
    if not all_comments:
        return {"comments": []}

    import json as _json
    indexed = [{"index": i, **c.model_dump()} for i, c in enumerate(all_comments)]
    prompt = CRITIC_PROMPT.format(
        persona=state["persona"],
        comments_json=_json.dumps(indexed, indent=2),
    )
    structured = _make_llm(max_tokens=8192, reasoning_max=2048).with_structured_output(method="json_schema", schema=CriticVerdict)
    try:
        verdict: CriticVerdict = structured.invoke(prompt)  # type: ignore[assignment]
    except Exception as e:
        # Fall back to keep-everything if the critic fails — better to over-
        # emit than to drop all of this persona's work. Consolidation will
        # still dedupe/prune downstream.
        print(
            f"  [warn] self_critique failed for persona {state['persona_idx']}: "
            f"{type(e).__name__}: {str(e)[:200]}; keeping all comments"
        )
        return {"comments": all_comments, "usage": USAGE.snapshot()}

    kept = [all_comments[i] for i in verdict.kept_indices if 0 <= i < len(all_comments)]
    # Emit to the boundary `comments` channel (shared reducer with parent).
    # Also emit cumulative usage snapshot — fan-in max-reducer keeps the
    # largest across the three parallel personas (all seeing the same
    # module-level USAGE counter).
    return {"comments": kept, "usage": USAGE.snapshot()}


def build_persona_subgraph():
    # ───────────────────────────────────────────────────────────────────
    # NOTE — the section loop is INTENTIONALLY sequential per persona.
    #
    # Each persona reviews its assigned sections one at a time, driven by
    # `section_cursor` + a conditional back-edge to `review_section`. The
    # "obvious" faster version is to fan out one Send per section inside
    # the subgraph so all assigned sections are reviewed in parallel.
    # Reasons to keep it sequential:
    #
    # 1. Linear checkpoint history → clean fork-at-step semantics.
    #    `get_state_history` on a persona's namespace shows a readable
    #    progression (cursor 0, 1, 2, …, self_critique). You can fork at
    #    any cursor value and replay from there. Parallel Sends inside the
    #    subgraph would produce a checkpoint tree with concurrent pending
    #    tasks, and "rewind to just before section 5" stops being a
    #    well-defined checkpoint.
    #
    # 2. Hang blast radius is bounded. OpenRouter occasionally hangs a
    #    single request. Sequential-per-persona means max concurrent
    #    requests = 3 (one per persona); parallel-inside is sum(
    #    assignments), 15–25 on real papers. Self_critique still has to
    #    wait for ALL sibling section reviews either way — parallelizing
    #    doesn't rescue a hung call, it only multiplies the surface area.
    #
    # Wall-clock trade-off: on a ~22-section paper, sequential runs ~5 min
    # per persona (bottlenecked by the longest assignment); parallel
    # Sends would run ~30 s/persona. If you need throughput, copy this
    # file and flatten the fan-out.
    # ───────────────────────────────────────────────────────────────────
    sg = StateGraph(PersonaState, output_schema=PersonaOutput)
    sg.add_node("review_section", _review_section)
    sg.add_node("self_critique", _self_critique)

    sg.add_edge(START, "review_section")
    sg.add_conditional_edges(
        "review_section",
        _more_sections,
        {"review_section": "review_section", "self_critique": "self_critique"},
    )
    sg.add_edge("self_critique", END)
    return sg.compile()


# ---------------------------------------------------------------------------
# Parent graph
# ---------------------------------------------------------------------------


def build_graph(checkpointer=None):
    g = StateGraph(ReviewState)
    g.add_node("extract_pdf", extract_pdf)
    g.add_node("split_sections", split_sections_node)
    g.add_node("summarize_paper", summarize_paper)
    g.add_node("plan_assignments", plan_assignments)
    g.add_node("review_as_persona", build_persona_subgraph())
    g.add_node("consolidate", consolidate)
    g.add_node("human_gate", human_gate)
    g.add_node("publish", publish)

    g.add_edge(START, "extract_pdf")
    g.add_edge("extract_pdf", "split_sections")
    g.add_edge("split_sections", "summarize_paper")
    g.add_edge("summarize_paper", "plan_assignments")
    g.add_conditional_edges("plan_assignments", fan_out_personas, ["review_as_persona"])
    g.add_edge("review_as_persona", "consolidate")
    g.add_edge("consolidate", "human_gate")
    g.add_conditional_edges(
        "human_gate",
        route_from_gate,
        ["publish", "consolidate", "review_as_persona"],
    )
    g.add_edge("publish", END)
    return g.compile(checkpointer=checkpointer)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _collect_interrupts(result) -> list:
    if isinstance(result, dict):
        raw = result.get("__interrupt__") or []
        return [i.value if hasattr(i, "value") else i for i in raw]
    return []


def _write_markdown(
    thread_id: str,
    state: ReviewState,
    usage: dict | None = None,
    outputs_dir: Path | None = None,
) -> Path:
    target = Path(outputs_dir) if outputs_dir is not None else OUTPUTS_DIR
    target.mkdir(parents=True, exist_ok=True)
    path = target / f"{thread_id}.md"
    if usage is None:
        usage = _merge_usage(state.get("usage") or {}, USAGE.snapshot())

    issues = state.get("final_issues", []) or []
    sections = state.get("sections", []) or []
    personas = state.get("personas", []) or []
    assignments = state.get("assignments", {}) or {}
    raw_comments = state.get("comments", []) or []

    lines = [
        f"# Review — {state.get('paper_title', '')}",
        "",
        f"- **Thread:** `{thread_id}`",
        f"- **Paper:** `{state.get('paper_path', '')}`",
        f"- **Decision:** `{state.get('decision') or 'n/a'}`",
        f"- **Sections:** {len(sections)}",
        f"- **Personas:** {len(personas)}",
        f"- **Raw comments:** {len(raw_comments)}",
        f"- **Final issues:** {len(issues)}",
        f"- **Usage:** {usage}",
        "",
        "## Overall feedback",
        "",
        state.get("overall_feedback", "_none_"),
        "",
        "## Assignments",
        "",
    ]
    for i, p in enumerate(personas):
        lines.append(f"- **Reviewer {i}** ({p}): sections {assignments.get(i, [])}")
    lines.extend(["", "## Final issues (severity-tiered)", ""])
    for issue in issues:
        lines.extend([
            f"### [{issue.severity}] {issue.title}",
            f"*type: {issue.comment_type}; section: {issue.source_section_idx}; merged_from: {issue.merged_from}*",
            "",
            f"> {issue.quote}",
            "",
            issue.explanation,
            "",
            "---",
            "",
        ])
    lines.extend(["", "## Raw persona comments (pre-consolidation)", ""])
    for c in raw_comments:
        lines.extend([
            f"- **[reviewer {c.persona_idx}, section {c.source_section_idx}, {c.confidence}]** {c.title}",
            f"  > {c.quote}",
            f"  {c.explanation}",
            "",
        ])
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Main-CLI shim entry point
# ---------------------------------------------------------------------------


def run_oneshot(
    *,
    paper_path: str,
    output_dir: Path = DEFAULT_VIZ_DIR,
    thread_id: str | None = None,
) -> dict:
    """One-shot entry for `openaireview review <paper> --method review_rounds`.

    Runs the graph to completion with no checkpointer (no HITL pause — the
    human_gate auto-approves via a synthetic Command(resume=...)). Writes
    markdown + viz JSON and returns the final state dict.

    The main CLI should import this; the stateful commands (run/resume/fork)
    remain on the python -m review_rounds.review_rounds entry."""
    graph = build_graph()  # no checkpointer
    tid = thread_id or uuid.uuid4().hex[:8]
    config = {"configurable": {"thread_id": tid, "output_dir": str(output_dir)}}
    result = graph.invoke({"paper_path": paper_path}, config=config)

    # If the graph paused at human_gate, auto-approve and continue.
    if _collect_interrupts(result):
        result = graph.invoke(Command(resume="approve"), config=config)
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _open_checkpointer() -> SqliteSaver:
    conn = sqlite3.connect(str(CHECKPOINT_DB), check_same_thread=False)
    return SqliteSaver(conn)


def _print_gate_payload(payload: dict) -> None:
    print("\n--- paused at human_gate ---")
    print(f"tiers:  {payload.get('tier_counts', {})}")
    print(f"issues: {payload.get('n_issues', 0)}")
    for t in payload.get("titles", []):
        print(f"  - {t}")
    print(f"\noverall: {payload.get('overall_feedback', '')}\n")
    print(payload.get("prompt", ""))


def _cmd_run(args) -> int:
    thread_id = args.thread_id or uuid.uuid4().hex[:8]
    config = {"configurable": {"thread_id": thread_id}}
    graph = build_graph(_open_checkpointer())

    print(f"[thread_id] {thread_id}")
    print(f"[paper]     {args.paper}")
    result = graph.invoke({"paper_path": args.paper}, config=config)

    interrupts = _collect_interrupts(result)
    if interrupts:
        _print_gate_payload(interrupts[0])
        print(f"\nResume: python -m review_rounds.review_rounds resume {thread_id} <decision>")
    return 0


def _cmd_resume(args) -> int:
    config = {"configurable": {"thread_id": args.thread_id}}
    graph = build_graph(_open_checkpointer())
    result = graph.invoke(Command(resume=args.decision), config=config)
    interrupts = _collect_interrupts(result)
    if interrupts:
        _print_gate_payload(interrupts[0])
    return 0


def _cmd_history(args) -> int:
    config = {"configurable": {"thread_id": args.thread_id}}
    graph = build_graph(_open_checkpointer())
    for i, snap in enumerate(graph.get_state_history(config)):
        next_nodes = list(snap.next) if snap.next else []
        n_sec = len(snap.values.get("sections", []) or [])
        n_comments = len(snap.values.get("comments", []) or [])
        n_issues = len(snap.values.get("final_issues", []) or [])
        cp = snap.config["configurable"].get("checkpoint_id", "?")
        print(f"[{i:>2}] next={next_nodes} sections={n_sec} comments={n_comments} issues={n_issues} cp={cp}")
    return 0


def _cmd_fork(args) -> int:
    """Time-travel: drop one persona's comments from consolidation at a past
    checkpoint, then continue. Writes to the `dropped_personas` channel
    instead of rewriting `comments` — the latter's `add` reducer would
    append the replacement list to the existing one, leaving the target
    persona's comments in state and duplicating the survivors."""
    config = {
        "configurable": {
            "thread_id": args.thread_id,
            "checkpoint_id": args.checkpoint_id,
            "checkpoint_ns": "",
        }
    }
    graph = build_graph(_open_checkpointer())
    snap = graph.get_state(config)

    raw = list(snap.values.get("comments", []) or [])
    comments = [Comment(**c) if isinstance(c, dict) else c for c in raw]
    n_target = sum(1 for c in comments if c.persona_idx == args.persona)
    print(f"[fork] persona {args.persona}: {n_target} comments will be excluded from consolidation")

    new_config = graph.update_state(
        config,
        {"dropped_personas": [args.persona]},
        as_node="review_as_persona",
    )
    print(f"[forked] new checkpoint: {new_config['configurable']['checkpoint_id']}")

    result = graph.invoke(None, config=new_config)
    interrupts = _collect_interrupts(result)
    if interrupts:
        _print_gate_payload(interrupts[0])
    return 0


def _cmd_dump(args) -> int:
    config = {"configurable": {"thread_id": args.thread_id}}
    graph = build_graph(_open_checkpointer())
    snap = graph.get_state(config)
    if not snap.values:
        print(f"No state found for thread {args.thread_id}")
        return 1
    path = _write_markdown(args.thread_id, snap.values)
    print(f"[saved] {path}")
    return 0


def _cmd_topology(_args) -> int:
    graph = build_graph()
    try:
        print(graph.get_graph(xray=True).draw_ascii())
    except Exception:
        print(graph.get_graph(xray=True).draw_mermaid())
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="review_rounds")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="start a new review thread")
    p_run.add_argument("paper")
    p_run.add_argument("--thread-id", default=None)
    p_run.set_defaults(func=_cmd_run)

    p_res = sub.add_parser("resume", help="resume from human_gate")
    p_res.add_argument("thread_id")
    p_res.add_argument("decision", help="approve | redo:<idx> | edit:<k>:<v>")
    p_res.set_defaults(func=_cmd_resume)

    p_hist = sub.add_parser("history", help="list checkpoints")
    p_hist.add_argument("thread_id")
    p_hist.set_defaults(func=_cmd_history)

    p_fork = sub.add_parser("fork", help="time-travel: drop one persona's comments")
    p_fork.add_argument("thread_id")
    p_fork.add_argument("checkpoint_id")
    p_fork.add_argument("--persona", type=int, required=True)
    p_fork.set_defaults(func=_cmd_fork)

    p_dump = sub.add_parser("dump", help="save current state to outputs/<thread>.md")
    p_dump.add_argument("thread_id")
    p_dump.set_defaults(func=_cmd_dump)

    p_top = sub.add_parser("topology", help="print the graph topology")
    p_top.set_defaults(func=_cmd_topology)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
