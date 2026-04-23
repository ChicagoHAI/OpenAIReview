"""A stateful review-round graph over OpenAIReview outputs.

Exercises the LangGraph primitives I hadn't touched in production:
  - StateGraph with a typed TypedDict state
  - Annotated[list, add] reducer for parallel fan-in (the silent-bug case)
  - Parallel fan-out via Send
  - Subgraph composition (review_as_persona is its own compiled graph)
  - SqliteSaver checkpointer for durability across process restarts
  - interrupt() + Command(resume=...) for human-in-the-loop
  - get_state_history() + update_state() for time-travel fork-and-replay
  - Conditional edges (declarative routing, not LLM-chosen)

The per-persona subgraph uses an adversarial self-critique step (challenge +
verdict) whose prompts are adapted from the progressive_debate method in
OpenAIReview PR #37. Point of that cross-pollination: the typed StateGraph
makes it impossible to forget to thread the source passage to the verdict
node, which is the root cause of the claim_persistent miss reported in
PR #37's benchmark.

CLI:
    python -m review_rounds.review_rounds run <paper> [--thread-id ID]
    python -m review_rounds.review_rounds resume <thread-id> <decision>
    python -m review_rounds.review_rounds history <thread-id>
    python -m review_rounds.review_rounds fork <thread-id> <checkpoint> --persona N --draft TEXT
    python -m review_rounds.review_rounds topology
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import uuid
from operator import add
from pathlib import Path
from typing import Annotated, TypedDict

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, Send, interrupt

from reviewer.client import chat
from reviewer.parsers import parse_document
from reviewer.utils import count_tokens

from review_rounds.models import Draft


CHECKPOINT_DB = Path(__file__).parent / ".checkpoints.db"
OUTPUTS_DIR = Path(__file__).parent / "outputs"

MODEL = "minimax/minimax-m2.7"
PROVIDER = "openrouter"
OCR_ENGINE = "mistral"

PAPER_MAX_TOKENS = 20_000        # Budget for paper text threaded into prompts.
PERSONA_MAX_TOKENS = 8_096       # Output cap for draft / challenge / revise / aggregate.
VERDICT_MAX_TOKENS = 512         # JSON-only; no need to burn tokens.


# ---------------------------------------------------------------------------
# State shapes
# ---------------------------------------------------------------------------


def _merge_edits(left: dict[str, str], right: dict[str, str]) -> dict[str, str]:
    """Reducer for the edits channel: right wins on key collision.

    Lives here as a named function so the state definition reads cleanly and
    the reducer behavior is greppable — the plan calls out reducer semantics
    as a silent-bug case."""
    return {**left, **right}


class ReviewState(TypedDict, total=False):
    paper_path: str
    paper_title: str
    paper_text: str
    personas: list[str]
    # Parallel fan-in: three subgraphs append one Draft each.
    drafts: Annotated[list[Draft], add]
    aggregate: str
    decision: str  # "approve" | "redo:<idx>" | "edit"
    edits: Annotated[dict[str, str], _merge_edits]


class PersonaState(TypedDict, total=False):
    """Subgraph-local state. Carries everything the per-persona pipeline
    needs internally. Only fields declared on PersonaOutput cross back to
    the parent — otherwise `paper_text`, `persona`, etc. would fan-in with
    three concurrent writes against a non-reducer channel."""

    persona: str
    persona_idx: int
    paper_text: str
    initial: str
    challenge: str
    verdict: str
    verdict_reason: str
    final: str
    drafts: Annotated[list[Draft], add]


class PersonaOutput(TypedDict, total=False):
    """Subgraph → parent boundary. Only `drafts` leaks out; everything else
    stays private to the persona pipeline. Matches the parent's reducer on
    `drafts` so the three subgraph results fan in cleanly."""

    drafts: Annotated[list[Draft], add]


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

PLAN_REVIEWERS_PROMPT = """\
You are assigning three reviewers to an academic paper. Return a JSON list of \
exactly three short persona descriptions (one sentence each), each written as \
"A {{adjective}} {{role}} who focuses on {{concern}}". Cover complementary \
angles (e.g., methodology, clarity, prior-art). Return ONLY the JSON list.

Paper title: {title}

First 4000 chars of paper:
{excerpt}
"""

DRAFT_PROMPT = """\
You are the following reviewer: {persona}

Write a short, focused review of the paper below. 4-8 sentences. Be concrete \
about the single most important issue you see through your lens. Quote one \
specific passage you are reacting to.

Paper title: {title}

Paper text (truncated):
{paper_text}
"""

# Adapted from OpenAIReview PR #37 (method_debate.py). The kata uses this as
# the subgraph's self-critique step — a persona's own draft is the "comment",
# the challenge attacks it, and the verdict decides keep vs revise.
CHALLENGE_PROMPT = """\
You are a devil's advocate. Argue that the review below is WRONG — that the \
issue it flags is not actually a problem.

Consider:
- Is the reviewer misreading the paper or applying the wrong framework?
- Is this a standard convention the reviewer is unfamiliar with?
- Does surrounding context resolve the apparent issue?
- Is this a trivial formatting or style issue dressed up as substance?

If the review is genuinely correct, say so explicitly: "No strong \
counterargument; the issue stands."

2-4 sentences.

REVIEW UNDER CHALLENGE (from {persona}):
{draft}

PAPER CONTEXT (truncated):
{paper_text}
"""

VERDICT_PROMPT = """\
You are an editor adjudicating a dispute. Weigh the review against the \
challenge. Return ONLY a JSON object:

{{
  "verdict": "keep" or "revise",
  "reason": "one sentence"
}}

"keep" means the review stands as written. "revise" means the challenge has \
merit and the review should be rewritten to address it.

REVIEW (from {persona}):
{draft}

CHALLENGE:
{challenge}
"""

REVISE_PROMPT = """\
Rewrite the review below to address the challenge. Keep your persona:
{persona}

Original review:
{draft}

Challenge to address:
{challenge}

Editor's note: {reason}

Return the revised review only — 4-8 sentences.
"""

AGGREGATE_PROMPT = """\
Synthesize the three reviews below into one coherent meta-review. Preserve \
each reviewer's single most important point; do not average them into mush. \
End with one "overall recommendation" line: accept / revise / reject.

{drafts_block}
"""


# ---------------------------------------------------------------------------
# Nodes (parent graph)
# ---------------------------------------------------------------------------


def extract_pdf(state: ReviewState) -> dict:
    """Reuse OpenAIReview's extractor; the kata's only imported domain logic.

    Forces Mistral OCR (better math/table rendering) and truncates to
    PAPER_MAX_TOKENS via tiktoken so the persona subgraphs get a predictable
    budget rather than a character-count proxy."""
    title, text, _ = parse_document(state["paper_path"], ocr=OCR_ENGINE)
    text = _truncate_to_tokens(text, PAPER_MAX_TOKENS)
    return {"paper_title": title, "paper_text": text}


def _truncate_to_tokens(text: str, max_tokens: int) -> str:
    if count_tokens(text) <= max_tokens:
        return text
    # Binary search on char offset — count_tokens uses tiktoken, so tokenizing
    # the full text once and slicing tokens is faster, but char-based is
    # simpler for the kata and the one-time cost is negligible.
    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if count_tokens(text[:mid]) <= max_tokens:
            lo = mid
        else:
            hi = mid - 1
    return text[:lo]


def plan_reviewers(state: ReviewState) -> dict:
    prompt = PLAN_REVIEWERS_PROMPT.format(
        title=state["paper_title"],
        excerpt=state["paper_text"][:4000],
    )
    response, _ = chat(
        messages=[{"role": "user", "content": prompt}],
        model=MODEL,
        provider=PROVIDER,
        max_tokens=1024,
    )
    personas = _parse_json_list(response) or [
        "A methodology-focused reviewer who focuses on experimental validity",
        "A clarity-focused reviewer who focuses on exposition and notation",
        "A prior-art reviewer who focuses on novelty and citations",
    ]
    return {"personas": personas[:3]}


def fan_out_personas(state: ReviewState) -> list[Send]:
    """Conditional edge that dispatches one Send per persona to the subgraph.

    The Send pattern is the LangGraph idiom for dynamic map-reduce — one
    branch per element, each reducing back via the shared `drafts` channel."""
    return [
        Send(
            "review_as_persona",
            {
                "persona": p,
                "persona_idx": i,
                "paper_text": state["paper_text"],
            },
        )
        for i, p in enumerate(state["personas"])
    ]


def critic_aggregate(state: ReviewState) -> dict:
    # The `drafts` channel uses an `add` reducer, so update_state and redo:N
    # both APPEND rather than replace. Dedupe here by taking the latest entry
    # per persona_idx — that gives "most recent wins" semantics, which is
    # what fork-and-replay and redo:N both conceptually want. See NOTES.md
    # for the trap this unearths.
    latest: dict[int, Draft] = {}
    for d in state["drafts"]:
        latest[d.persona_idx] = d
    drafts = [latest[i] for i in sorted(latest)]

    # edits (if any) from a prior human gate override a persona's final text.
    edits = state.get("edits", {}) or {}
    blocks = []
    for d in drafts:
        final_text = edits.get(str(d.persona_idx), d.final)
        blocks.append(f"### Reviewer {d.persona_idx + 1}: {d.persona}\n{final_text}")
    drafts_block = "\n\n".join(blocks)

    response, _ = chat(
        messages=[{"role": "user", "content": AGGREGATE_PROMPT.format(drafts_block=drafts_block)}],
        model=MODEL,
        provider=PROVIDER,
        max_tokens=PERSONA_MAX_TOKENS,
    )
    return {"aggregate": response}


def human_gate(state: ReviewState) -> dict:
    """Durable HITL pause. The payload is what the human sees on resume."""
    decision = interrupt(
        {
            "aggregate": state["aggregate"],
            "personas": state["personas"],
            "prompt": (
                "Reply with one of:\n"
                "  approve                      — publish as-is\n"
                "  redo:<idx>                   — re-run persona <idx>'s subgraph\n"
                "  edit:<idx>:<new draft text>  — override persona <idx>'s final draft"
            ),
        }
    )
    # `decision` is whatever was passed to Command(resume=...).
    if isinstance(decision, str) and decision.startswith("edit:"):
        _, idx, text = decision.split(":", 2)
        return {"decision": "edit", "edits": {idx: text}}
    return {"decision": decision if isinstance(decision, str) else "approve"}


def publish(state: ReviewState, config: RunnableConfig) -> dict:
    """Terminal node. Writes the final review to outputs/<thread_id>.md.

    The second arg makes LangGraph pass RunnableConfig so we can pull the
    thread_id. Saving here (rather than in _cmd_run) means the file is
    produced regardless of which process invokes approve — run, resume,
    or a fork that got approved."""
    thread_id = config.get("configurable", {}).get("thread_id", "unknown")
    path = _write_output(thread_id, state)
    print(f"[saved] {path}")
    return {}


def _write_output(thread_id: str, state: ReviewState) -> Path:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUTS_DIR / f"{thread_id}.md"

    # Dedupe drafts by persona_idx the same way critic_aggregate does — the
    # append-only `add` reducer means the raw list may contain stale entries
    # from redo:N or fork-override cycles.
    latest: dict[int, Draft] = {}
    for d in state.get("drafts", []) or []:
        latest[d.persona_idx] = d
    drafts = [latest[i] for i in sorted(latest)]
    edits = state.get("edits") or {}

    lines = [
        f"# Review — {state.get('paper_title', '')}",
        "",
        f"- **Thread:** `{thread_id}`",
        f"- **Paper:** `{state.get('paper_path', '')}`",
        f"- **Decision:** `{state.get('decision') or 'n/a'}`",
        "",
        "## Aggregate",
        "",
        state.get("aggregate", "_no aggregate produced_"),
        "",
        "## Individual drafts",
        "",
    ]
    for d in drafts:
        final_text = edits.get(str(d.persona_idx), d.final)
        lines.extend([
            f"### Reviewer {d.persona_idx + 1}: {d.persona}",
            f"*verdict: {d.verdict} — {d.verdict_reason}*",
            "",
            "**Initial draft**",
            "",
            d.initial,
            "",
            "**Challenge**",
            "",
            d.challenge,
            "",
            "**Final**",
            "",
            final_text,
            "",
            "---",
            "",
        ])
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def route_from_gate(state: ReviewState):
    """Conditional edge out of human_gate.

    Returns either a node name (publish / critic_aggregate) or a Send that
    dispatches a single persona back through the subgraph — symmetric with the
    initial fan-out. Returning Send from a conditional edge keeps the redo
    path static and visible in draw_mermaid()."""
    decision = state.get("decision", "approve")
    if decision == "approve":
        return "publish"
    if decision == "edit":
        # Re-aggregate with the edits map applied; no persona re-run needed.
        return "critic_aggregate"
    if decision.startswith("redo:"):
        idx = int(decision.split(":", 1)[1])
        return Send(
            "review_as_persona",
            {
                "persona": state["personas"][idx],
                "persona_idx": idx,
                "paper_text": state["paper_text"],
            },
        )
    return "publish"


# ---------------------------------------------------------------------------
# Subgraph: review_as_persona (draft → challenge → verdict → revise)
# ---------------------------------------------------------------------------


def _draft(state: PersonaState) -> dict:
    prompt = DRAFT_PROMPT.format(
        persona=state["persona"],
        title="",  # not threaded through — kata keeps state minimal
        paper_text=state["paper_text"],
    )
    response, _ = chat(
        messages=[{"role": "user", "content": prompt}],
        model=MODEL,
        provider=PROVIDER,
        max_tokens=PERSONA_MAX_TOKENS,
    )
    return {"initial": response}


def _challenge(state: PersonaState) -> dict:
    prompt = CHALLENGE_PROMPT.format(
        persona=state["persona"],
        draft=state["initial"],
        paper_text=state["paper_text"],
    )
    response, _ = chat(
        messages=[{"role": "user", "content": prompt}],
        model=MODEL,
        provider=PROVIDER,
        max_tokens=PERSONA_MAX_TOKENS,
    )
    return {"challenge": response}


def _verdict(state: PersonaState) -> dict:
    prompt = VERDICT_PROMPT.format(
        persona=state["persona"],
        draft=state["initial"],
        challenge=state["challenge"],
    )
    response, _ = chat(
        messages=[{"role": "user", "content": prompt}],
        model=MODEL,
        provider=PROVIDER,
        max_tokens=VERDICT_MAX_TOKENS,
    )
    parsed = _parse_json_object(response) or {"verdict": "keep", "reason": "parse failed"}
    verdict = parsed.get("verdict", "keep")
    if verdict not in ("keep", "revise"):
        verdict = "keep"
    return {"verdict": verdict, "verdict_reason": parsed.get("reason", "")}


def _route_after_verdict(state: PersonaState) -> str:
    return "revise" if state["verdict"] == "revise" else "finalize"


def _revise(state: PersonaState) -> dict:
    prompt = REVISE_PROMPT.format(
        persona=state["persona"],
        draft=state["initial"],
        challenge=state["challenge"],
        reason=state["verdict_reason"],
    )
    response, _ = chat(
        messages=[{"role": "user", "content": prompt}],
        model=MODEL,
        provider=PROVIDER,
        max_tokens=PERSONA_MAX_TOKENS,
    )
    return {"final": response}


def _finalize(state: PersonaState) -> dict:
    """Emit the Draft into the shared `drafts` channel. Reducer handles merge."""
    final_text = state.get("final") or state["initial"]
    draft = Draft(
        persona=state["persona"],
        persona_idx=state["persona_idx"],
        initial=state["initial"],
        challenge=state["challenge"],
        verdict=state["verdict"],
        verdict_reason=state["verdict_reason"],
        final=final_text,
    )
    return {"drafts": [draft]}


def build_persona_subgraph():
    sg = StateGraph(PersonaState, output_schema=PersonaOutput)
    sg.add_node("draft", _draft)
    sg.add_node("challenge", _challenge)
    sg.add_node("verdict", _verdict)
    sg.add_node("revise", _revise)
    sg.add_node("finalize", _finalize)

    sg.add_edge(START, "draft")
    sg.add_edge("draft", "challenge")
    sg.add_edge("challenge", "verdict")
    sg.add_conditional_edges("verdict", _route_after_verdict, {"revise": "revise", "finalize": "finalize"})
    sg.add_edge("revise", "finalize")
    sg.add_edge("finalize", END)
    return sg.compile()


# ---------------------------------------------------------------------------
# Parent graph
# ---------------------------------------------------------------------------


def build_graph(checkpointer=None):
    g = StateGraph(ReviewState)
    g.add_node("extract_pdf", extract_pdf)
    g.add_node("plan_reviewers", plan_reviewers)
    g.add_node("review_as_persona", build_persona_subgraph())
    g.add_node("critic_aggregate", critic_aggregate)
    g.add_node("human_gate", human_gate)
    g.add_node("publish", publish)

    g.add_edge(START, "extract_pdf")
    g.add_edge("extract_pdf", "plan_reviewers")
    g.add_conditional_edges("plan_reviewers", fan_out_personas, ["review_as_persona"])
    g.add_edge("review_as_persona", "critic_aggregate")
    g.add_edge("critic_aggregate", "human_gate")
    g.add_conditional_edges(
        "human_gate",
        route_from_gate,
        ["publish", "critic_aggregate", "review_as_persona"],
    )
    g.add_edge("publish", END)
    return g.compile(checkpointer=checkpointer)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _open_checkpointer() -> SqliteSaver:
    """Construct a SqliteSaver that survives across CLI invocations.

    The context-manager form (`with SqliteSaver.from_conn_string(...) as s`)
    is awkward here — each CLI subcommand is a fresh process, so we pass the
    connection directly. check_same_thread=False for LangGraph's worker."""
    conn = sqlite3.connect(str(CHECKPOINT_DB), check_same_thread=False)
    return SqliteSaver(conn)


def _cmd_run(args) -> int:
    thread_id = args.thread_id or uuid.uuid4().hex[:8]
    config = {"configurable": {"thread_id": thread_id}}
    graph = build_graph(_open_checkpointer())

    print(f"[thread_id] {thread_id}")
    print(f"[paper]     {args.paper}")
    result = graph.invoke({"paper_path": args.paper}, config=config)

    interrupts = _collect_interrupts(result)
    if interrupts:
        payload = interrupts[0]
        print("\n--- paused at human_gate ---")
        print(f"\nAggregate review:\n{payload.get('aggregate', '')}\n")
        print(payload.get("prompt", ""))
        print(f"\nResume with: python -m review_rounds.review_rounds resume {thread_id} <decision>")
        return 0

    print("\n--- final aggregate ---")
    print(result.get("aggregate", "<no aggregate>"))
    return 0


def _cmd_resume(args) -> int:
    config = {"configurable": {"thread_id": args.thread_id}}
    graph = build_graph(_open_checkpointer())
    result = graph.invoke(Command(resume=args.decision), config=config)

    interrupts = _collect_interrupts(result)
    if interrupts:
        payload = interrupts[0]
        print("\n--- paused again at human_gate ---")
        print(f"\nAggregate review:\n{payload.get('aggregate', '')}\n")
        print(payload.get("prompt", ""))
        return 0

    print("\n--- final aggregate ---")
    print(result.get("aggregate", "<no aggregate>"))
    return 0


def _cmd_history(args) -> int:
    config = {"configurable": {"thread_id": args.thread_id}}
    graph = build_graph(_open_checkpointer())
    for i, snap in enumerate(graph.get_state_history(config)):
        next_nodes = list(snap.next) if snap.next else []
        n_drafts = len(snap.values.get("drafts", []))
        checkpoint_id = snap.config["configurable"].get("checkpoint_id", "?")
        print(f"[{i:>2}] next={next_nodes} drafts={n_drafts} checkpoint={checkpoint_id}")
    return 0


def _cmd_fork(args) -> int:
    """Time-travel demo: rewrite one persona's draft at a past checkpoint,
    then re-run from there. critic_aggregate re-runs with the edited draft;
    the other two drafts are untouched."""
    # checkpoint_ns="" pins the fork to the parent graph's namespace
    # (subgraph checkpoints live in their own ns). Without it, SqliteSaver's
    # put_writes fails with KeyError at config["configurable"]["checkpoint_ns"].
    config = {
        "configurable": {
            "thread_id": args.thread_id,
            "checkpoint_id": args.checkpoint_id,
            "checkpoint_ns": "",
        }
    }
    graph = build_graph(_open_checkpointer())

    snap = graph.get_state(config)
    drafts = list(snap.values.get("drafts", []))
    # Deserialize if the checkpointer returned dicts.
    drafts = [Draft(**d) if isinstance(d, dict) else d for d in drafts]

    found = False
    for d in drafts:
        if d.persona_idx == args.persona:
            d.final = args.draft
            found = True
            break
    if not found:
        print(f"No draft with persona_idx={args.persona} at this checkpoint.")
        return 1

    # update_state with as_node="review_as_persona" — we're asserting "this is
    # what the subgraph would have produced". The `add` reducer on `drafts`
    # would otherwise append; passing the full sorted list replaces via
    # langgraph's snapshot semantics (full write for the field).
    new_config = graph.update_state(
        config,
        {"drafts": drafts},
        as_node="review_as_persona",
    )
    print(f"[forked] new checkpoint: {new_config['configurable']['checkpoint_id']}")

    # Re-invoke from the forked checkpoint with no input — resumes graph flow.
    result = graph.invoke(None, config=new_config)
    interrupts = _collect_interrupts(result)
    if interrupts:
        payload = interrupts[0]
        print("\n--- paused at human_gate (fork) ---")
        print(f"\nAggregate review:\n{payload.get('aggregate', '')}\n")
        return 0
    print("\n--- final aggregate (fork) ---")
    print(result.get("aggregate", ""))
    return 0


def _cmd_dump(args) -> int:
    """Save the current state of a thread to outputs/<thread_id>.md without
    advancing the graph. Useful when paused at human_gate."""
    config = {"configurable": {"thread_id": args.thread_id}}
    graph = build_graph(_open_checkpointer())
    snap = graph.get_state(config)
    if not snap.values:
        print(f"No state found for thread {args.thread_id}")
        return 1
    path = _write_output(args.thread_id, snap.values)
    print(f"[saved] {path}")
    return 0


def _cmd_topology(_args) -> int:
    graph = build_graph()
    try:
        print(graph.get_graph(xray=True).draw_ascii())
    except Exception:
        print(graph.get_graph(xray=True).draw_mermaid())
    return 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_json_list(text: str) -> list | None:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        return None
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None


def _parse_json_object(text: str) -> dict | None:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None


def _collect_interrupts(result) -> list:
    # LangGraph surfaces interrupts via the special "__interrupt__" key on the
    # returned state when the graph pauses.
    if isinstance(result, dict):
        raw = result.get("__interrupt__") or []
        return [i.value if hasattr(i, "value") else i for i in raw]
    return []


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="review_rounds")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="start a new review thread")
    p_run.add_argument("paper", help="path/URL of paper (PDF, md, arXiv)")
    p_run.add_argument("--thread-id", default=None)
    p_run.set_defaults(func=_cmd_run)

    p_res = sub.add_parser("resume", help="resume from human_gate")
    p_res.add_argument("thread_id")
    p_res.add_argument("decision", help='approve | redo:<idx> | edit:<idx>:<text>')
    p_res.set_defaults(func=_cmd_resume)

    p_hist = sub.add_parser("history", help="list checkpoints for a thread")
    p_hist.add_argument("thread_id")
    p_hist.set_defaults(func=_cmd_history)

    p_fork = sub.add_parser("fork", help="time-travel: rewrite a draft at a checkpoint")
    p_fork.add_argument("thread_id")
    p_fork.add_argument("checkpoint_id")
    p_fork.add_argument("--persona", type=int, required=True)
    p_fork.add_argument("--draft", required=True)
    p_fork.set_defaults(func=_cmd_fork)

    p_dump = sub.add_parser("dump", help="save current thread state to outputs/<thread_id>.md")
    p_dump.add_argument("thread_id")
    p_dump.set_defaults(func=_cmd_dump)

    p_top = sub.add_parser("topology", help="print the graph topology")
    p_top.set_defaults(func=_cmd_topology)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
