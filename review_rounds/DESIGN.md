# review-rounds — Design and Data Flow

A LangGraph kata that simulates the OpenAIReview Claude Code skill's
section-level review pipeline. Three reviewer personas read orchestrator-
assigned sections in parallel, self-critique their own findings, and a
consolidate step dedupes and tiers everything by severity. Ships both as a
stateful CLI with human-in-the-loop / time-travel / fork, and a one-shot
`--method review_rounds` shim on the main `openaireview` CLI.

**Purpose:** exercise the five LangGraph primitives I hadn't used in
production (typed StateGraph + reducer, SqliteSaver, interrupt/Command,
get_state_history/update_state, subgraph composition) on a domain I already
have substrate for. See NOTES.md for the write-up of what surprised me.

---

## Topology

### Parent graph

```
 START
   │
   ▼
┌───────────────┐
│  extract_pdf  │  reviewer.parsers.parse_document (Mistral OCR)
└───────┬───────┘  → paper_title, paper_text (truncated to PAPER_MAX_TOKENS)
        ▼
┌──────────────────┐
│  split_sections  │  skill/scripts/prepare_workspace.split_sections via tmpdir
└────────┬─────────┘  → sections: list[Section]
         ▼
┌──────────────────┐
│  summarize_paper │  free-form ChatOpenAI call
└────────┬─────────┘  → summary: str  (orchestrator's notes)
         ▼
┌────────────────────┐
│  plan_assignments  │  structured: PlanOutput
└────────┬───────────┘  → personas: list[str]
         │               → assignments: dict[int, list[int]]
         │ (Send × 3)
    ┌────┼────┐
    ▼    ▼    ▼
┌──────────────────────┐
│  review_as_persona   │  SUBGRAPH (see below) — one per persona,
│  (compiled subgraph) │  each with its assigned section subset
└──────────┬───────────┘
   │    │     │
   └────┼─────┘ (reducer: Annotated[list[Comment], add])
        ▼
┌──────────────────┐
│   consolidate    │  structured: ConsolidationOutput
└────────┬─────────┘  → final_issues: list[ConsolidatedIssue]
         │            → overall_feedback: str
         ▼
┌──────────────────┐
│   human_gate     │  interrupt(payload) — durable HITL pause
└────────┬─────────┘  resume via Command(resume="approve|redo:N|edit:k:v")
         │
         │     Conditional edge (route_from_gate):
         ├──── "approve"   ──▶  publish  ──▶  END
         ├──── "edit"      ──▶  consolidate (loop)
         └──── "redo:N"    ──▶  review_as_persona  (Send, specific persona)
```

### Persona subgraph (nested internal section loop)

```
   [subgraph START]
         │
         ▼
 ┌────────────────┐    ←───────────┐
 │ review_section │                │
 └───────┬────────┘                │
         │                         │
         ▼                         │
  more_sections?  ──"loop"─────────┘
         │
         │ "done"
         ▼
 ┌───────────────┐
 │ self_critique │    structured: CriticVerdict
 └───────┬───────┘    (filters raw comments to kept_indices)
         │
         ▼
   [subgraph END]
         │
         ▼ (PersonaOutput: only `comments` + `usage` cross the boundary)
   parent state
```

Loop driver: `section_cursor: int`. Each `review_section` call writes
`section_comments` (internal reducer) and increments cursor.
`more_sections` is a conditional edge that returns `"review_section"`
while `cursor < len(sections)`, else `"self_critique"`.

---

## State shapes

Two TypedDict schemas — one for the parent, one for the subgraph. The
`output_schema` on the subgraph constrains what crosses the fan-in.

### Parent: `ReviewState`

```python
class ReviewState(TypedDict, total=False):
    # Input + derived paper context
    paper_path:      str
    paper_title:     str
    paper_text:      str                              # truncated to PAPER_MAX_TOKENS
    sections:        list[Section]                    # from split_sections
    summary:         str                              # orchestrator's note

    # Orchestrator-shaped control flow
    personas:        list[str]                        # 3 reviewer descriptions
    assignments:     dict[int, list[int]]             # persona_idx → section_idx list

    # Fan-in results (reducer: operator.add)
    comments:        Annotated[list[Comment], add]    # all kept comments, stamped

    # Consolidation output
    final_issues:    list[ConsolidatedIssue]          # severity-tiered
    overall_feedback: str

    # HITL + fork affordances
    decision:        str                              # approve | redo:N | edit
    edits:           Annotated[dict[str, str], _merge_edits]

    # Cost/usage (reducer: _merge_usage element-wise max)
    usage:           Annotated[dict, _merge_usage]
```

### Subgraph-internal: `PersonaState`

```python
class PersonaState(TypedDict, total=False):
    persona:          str                              # one-sentence persona
    persona_idx:      int                              # 0, 1, 2
    summary:          str                              # inherited context
    sections:         list[Section]                    # ASSIGNED subset only
    section_cursor:   int                              # loop counter
    section_comments: Annotated[list[Comment], add]    # internal fan-in
    comments:         Annotated[list[Comment], add]    # boundary-emitted (PersonaOutput)
```

### Subgraph boundary: `PersonaOutput`

```python
class PersonaOutput(TypedDict, total=False):
    comments: Annotated[list[Comment], add]
    usage:    Annotated[dict, _merge_usage]
```

Without `output_schema=PersonaOutput`, every `PersonaState` field would
fan in to the parent. `paper_text`-style non-reducer fields hit with 3
concurrent writes → `InvalidUpdateError`.

---

## Pydantic models (structured-output schemas)

Living in `review_rounds/models.py`. Doubles as the schemas passed to
`ChatOpenAI.with_structured_output(method="json_schema", schema=...)`.

| Model | Used by | Fields |
|---|---|---|
| `Section` | `split_sections_node` | `idx`, `heading`, `text`, `chars` |
| `PlanOutput` | `plan_assignments` | `personas: list[str]`, `assignments: list[list[int]]` |
| `CommentList` | `_review_section` | `comments: list[Comment]` |
| `Comment` | per-section review + boundary | `title`, `quote`, `explanation`, `comment_type`, `confidence`, `source_section_idx`, `persona_idx` |
| `CriticVerdict` | `_self_critique` | `kept_indices: list[int]`, `reason: str` |
| `ConsolidatedIssue` | `consolidate` | Comment fields + `severity: major/moderate/minor` + `merged_from: list[int]` |
| `ConsolidationOutput` | `consolidate` | `issues: list[ConsolidatedIssue]`, `overall_feedback: str` |

**Note on assignments shape:** originally `dict[int, list[int]]`. Switched
to `list[list[int]]` after JSON schema round-tripping dropped integer
keys and kimi returned `"persona_1"`, `"persona_2"`, `"persona_3"`.
Outer-index-as-persona-id is cleaner — see NOTES.md §R2.

---

## Reducers

### `operator.add` on `list[Comment]`

Standard list concatenation. Fires when three subgraphs emit `comments`
in parallel at the fan-in. Also fires when a persona's internal section
loop appends to `section_comments`.

```
Persona 0: emit {"comments": [c0, c1, c2]}
Persona 1: emit {"comments": [c3, c4]}
Persona 2: emit {"comments": [c5, c6, c7]}
                    ⇓
Parent state.comments = [c0, c1, c2, c3, c4, c5, c6, c7]
```

### `_merge_edits` on `dict[str, str]`

Right-wins merge for the `edits` override map. Lets `human_gate` stash
an override keyed by persona_idx (as a string).

### `_merge_usage` on `dict`

Element-wise max. The module-level `USAGE` collector is cumulative
within a Python process, so three parallel persona subgraphs see the
same running total. Max of their boundary snapshots keeps the latest
value without double-counting.

```
Persona 0 emits: {"cost_usd": 0.08, "calls": 5}
Persona 1 emits: {"cost_usd": 0.09, "calls": 6}
Persona 2 emits: {"cost_usd": 0.11, "calls": 7}
                    ⇓
Parent usage = {"cost_usd": 0.11, "calls": 7}
```

---

## Cost and usage tracking

Two-layer design — a callback collects per-call usage; the graph state
persists the total across process boundaries.

```
┌───────────────────────────────────────────┐
│  _UsageCollector (BaseCallbackHandler)    │  module-level singleton
│  ─────────────────────────────────────    │  (USAGE)
│  on_llm_end(response):                    │
│    prompt_tokens     += usage.prompt_*    │
│    completion_tokens += usage.completion_*│
│    reasoning_tokens  += usage.reasoning_* │
│    cost_usd          += usage.cost        │
│    calls             += 1                 │
└────────────────────┬──────────────────────┘
                     │  attached to every ChatOpenAI(callbacks=[USAGE])
                     ▼
       every LLM call contributes to USAGE
                     │
                     │  each LLM-calling node returns
                     │  {"usage": USAGE.snapshot()} alongside its payload
                     ▼
┌───────────────────────────────────────────┐
│  state["usage"]  (Annotated reducer: max) │  persisted in SqliteSaver
└────────────────────┬──────────────────────┘
                     │
                     │  publish() reads state["usage"] ∪ USAGE.snapshot()
                     │  (resume process has fresh USAGE but non-empty state)
                     ▼
          review_rounds/outputs/<thread>.md
          review_results/<slug>.json methods[<key>] cost_usd
```

---

## Data flow per node

Compact reference. All nodes exist in `review_rounds/review_rounds.py`.

| Node | Reads from state | Writes to state | LLM? |
|---|---|---|---|
| `extract_pdf` | `paper_path` | `paper_title`, `paper_text` | no (OCR service) |
| `split_sections_node` | `paper_text` | `sections` | no |
| `summarize_paper` | `paper_title`, `paper_text`, `sections` | `summary`, `usage` | free-form |
| `plan_assignments` | `paper_title`, `summary`, `sections` | `personas`, `assignments`, `usage` | structured (`PlanOutput`) |
| `fan_out_personas` (conditional edge) | `assignments`, `personas`, `sections` | — (emits Sends) | no |
| `_review_section` (subgraph) | `persona`, `summary`, `sections[cursor]` | `section_comments` (reducer), `section_cursor` | structured (`CommentList`) |
| `_self_critique` (subgraph) | `persona`, `section_comments` | `comments` (boundary), `usage` | structured (`CriticVerdict`) |
| `consolidate` | `paper_title`, `summary`, `comments` | `final_issues`, `overall_feedback`, `usage` | structured (`ConsolidationOutput`) |
| `human_gate` | `final_issues`, `overall_feedback` | `decision`, `edits` | no (interrupts) |
| `route_from_gate` (conditional edge) | `decision`, `assignments`, `personas`, `sections` | — (returns node name or Send) | no |
| `publish` | all of the above | — (writes files) | no |

---

## Interrupt / resume / fork mechanics

### Interrupt-resume

```
Run process                 │    SqliteSaver              │   Resume process
─────────────                │    ──────────               │   ──────────────
graph.invoke({...})          │                             │
  ...nodes run to human_gate │                             │
  human_gate:                │                             │
    interrupt(payload)       │                             │
        │                    │                             │
        ▼                    │                             │
    raises GraphInterrupt    │                             │
    checkpoint is written ───┼──▶ [thread_id=T, next=      │
  returns with payload       │     human_gate, values=…]   │
process exits                │                             │
                             │                             │
                             │                             │ graph.invoke(
                             │                             │   Command(resume="approve"),
                             │                             │   config={"configurable":
                             │                             │             {"thread_id": T}})
                             │                             │   loads checkpoint ◀───┐
                             │                             │   re-enters human_gate │
                             │                             │   interrupt returns "approve"
                             │                             │   node continues
                             │                             │   conditional edge → publish
                             │                             │   writes viz JSON + md
```

### Fork / time-travel

`graph.update_state(config, values, as_node=X)` writes `values` into the
state at the given checkpoint as if node X had just produced them. The
next `graph.invoke(None, config=forked_config)` resumes from there with
whatever was statically next.

Demo use case (`python -m review_rounds.review_rounds fork`):
rewrite one persona's comment list at a post-review pre-consolidate
checkpoint → consolidate re-runs with the override, the other personas'
comments untouched.

---

## Main-CLI shim (guarded)

```
                   openaireview CLI (src/reviewer/cli.py)
                   ────────────────────────────────────────
           openaireview review <paper> --method <X>
                               │
    ┌──────────┬────────────┬──┴──────────┬────────────────┐
    │          │            │             │                │
zero_shot  progressive    local       debate         review_rounds
    │          │            │             │              (GUARDED IMPORT)
    │          │            │             │                │
    ▼          ▼            ▼             ▼                ▼
method_zero  method_prog  method_local  method_debate  review_rounds.run_oneshot
...they all produce review_results/<slug>.json method-merged
```

`run_oneshot` runs the graph with no checkpointer, auto-approves at the
HITL interrupt via `Command(resume="approve")`, and writes both outputs.
Import-guarded: if langgraph / langchain-openai aren't installed, the
main CLI raises with an install hint (`pip install -e .[kata]`).

---

## Reuse map (what imports from where)

```
┌────────────────────────────── src/reviewer/ ──────────────────────────────┐
│                                                                           │
│  parsers.parse_document(path, ocr="mistral")                              │
│                            ▲                                              │
│  utils.split_into_paragraphs(text)                                        │
│  utils.locate_comment_in_document(quote, paragraphs)                      │
│                            ▲                                              │
│  skill.scripts.prepare_workspace.split_sections(text, dir)                │
│                            ▲                                              │
│                            │                                              │
└────────────────────────────┼──────────────────────────────────────────────┘
                             │  (one-directional: src/reviewer never imports
                             │   from review_rounds/)
┌────────────────────────────┼──────────────── review_rounds/ ──────────────┐
│                            │                                              │
│  review_rounds.py          │                                              │
│    ↳ imports parse_document, split_sections                               │
│    ↳ uses LangChain: ChatOpenAI, RunnableConfig, BaseCallbackHandler      │
│    ↳ uses LangGraph: StateGraph, Send, interrupt, Command, SqliteSaver    │
│                                                                           │
│  viz.py                                                                   │
│    ↳ imports split_into_paragraphs, locate_comment_in_document            │
│                                                                           │
│  models.py  (Pydantic)                                                    │
└───────────────────────────────────────────────────────────────────────────┘
```

The kata is one-directionally coupled to the main package. Deleting
`review_rounds/` requires only dropping one argparse branch in `cli.py`.

---

## Output files

On publish (or `dump` subcommand):

- **`review_rounds/outputs/<thread_id>.md`** — human-readable per-thread dump: paper metadata, assignments, final issues with severity + provenance, raw per-persona comments, usage totals. Gitignored.
- **`review_results/<slug>.json`** — viz-compatible payload, merged with any existing `<slug>.json` under method key `review_rounds__<model_short>`. Read by `openaireview serve` — renders alongside other methods on the same paper. Unchanged format from what `save_viz_json.py` produces.

---

## Key design decisions

1. **Orchestrator-assigned sections, not Cartesian.** `plan_assignments` LLM output shapes the fan-out — a genuinely new primitive demo versus "send everyone to everyone." Also ~3× cheaper.
2. **Nested internal section loop, not flat fan-out of (persona, section) pairs.** Exercises subgraph-internal state; the parent graph sees 3 clean sends, not 20+.
3. **`method="json_schema"` on `with_structured_output`.** Default picks a path that doesn't propagate `extra_body.reasoning.max_tokens` — kimi burned 3000+ reasoning tokens and returned empty. Explicit `json_schema` honors the cap. See NOTES §R1.
4. **Subgraph `output_schema=PersonaOutput`.** Only `comments` + `usage` cross the boundary. Without this, every `PersonaState` field would fan in with 3 concurrent writes against non-reducer channels.
5. **Usage in state (not just module-level).** Publish runs in the resume process after human_gate; module-level USAGE is fresh there. State-persisted usage survives via the checkpointer.
6. **Viz JSON merge, not replace.** Matches `src/reviewer/cli.py` convention so `review_rounds__<model>` shows up as a method alongside other methods on the same paper, not a separate paper entry.
7. **Main CLI shim as thin guarded import.** Keeps the kata deletable (removing `review_rounds/` costs one argparse branch), keeps langgraph out of the minimal install's dep closure.

Full write-up of surprises and the reasoning behind trade-offs: **NOTES.md**.
