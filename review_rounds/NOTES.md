# review-rounds — post-mortem

Interview fuel, not OSS docs. Two builds on `examples/2602.18458v1.pdf`:
first against `minimax/minimax-m2.7` (prose-aggregate shape), then a
reshape to mirror the OpenAIReview Claude Code skill's section-level
pipeline against `moonshotai/kimi-k2.6` with LangChain structured output.

---

## Surprises from the section-aware reshape

**R1. LengthFinishReasonError is the reasoning-model tax.** kimi-k2.6
spends ~3000 reasoning tokens per structured-output call, invisibly,
before emitting any visible content. First run: `max_tokens=1024` → all
burned on reasoning, zero output, `LengthFinishReasonError`. Second
run: `max_tokens=4096` → reasoning capped at 1024 via
`extra_body.reasoning.max_tokens`, visible-output finally finishes.
Third run: `max_tokens=16384, reasoning_max=4096` for headroom. Lesson:
with reasoning models, `max_tokens` must budget for *both* thinking and
the schema. Also — `model_kwargs={"extra_body": {...}}` in ChatOpenAI
emits a deprecation warning in langchain-openai 1.x; pass `extra_body`
as a top-level kwarg.

**R2. JSON schema doesn't have integer dict keys.** First shape of
`PlanOutput` had `assignments: dict[int, list[int]]`. Structured output
round-trips through JSON schema under the hood — integer keys become
strings, and on top of that kimi chose `"persona_1"`, `"persona_2"`,
`"persona_3"` over `"0"`/`"1"`/`"2"`. Two mistakes in one field. Fix:
`list[list[int]]` — outer index is the persona index, no dict keys at
all. Removing the ambiguity is cheaper than parsing around it.

**R3. Subgraph output_schema is still the gatekeeper.** The section-loop
variant of `PersonaState` carries `persona`, `persona_idx`, `summary`,
`sections`, `section_cursor`, `section_comments` — none of which should
reach the parent. Without `output_schema=PersonaOutput` (only
`comments`), three concurrent subgraphs would collide on every single
non-reducer field at fan-in. This is the same trap from the first
build, just with a wider shape.

**R4. Structured output eliminates `_parse_json_*` helpers.** The
original prose-aggregate kata had 30 LoC of JSON extraction + fallback
defaults (`_parse_json_list`, `_parse_json_object`). Swapping to
`ChatOpenAI.with_structured_output(PydanticModel)` deleted all of them
— validation failures trigger LangChain's auto-retry, malformed output
is impossible at the schema level. Trade-off: one more dependency
(`langchain-openai`) and a reasoning-model tax (R1).

**R5. The orchestrator-assigns-sections node is the interesting new
demo.** `plan_assignments` takes a PaperOutput (personas + assignments)
and the fan-out conditional edge consumes `assignments` to Send each
persona only its assigned sections. That is LLM output directly shaping
the graph's control flow — far more interesting than the prose-aggregate
fan-out which was just "send everyone to everyone." It's also the
natural fork demo: `update_state` on the `assignments` field at the
post-plan checkpoint reissues the whole fan-out with a new partition.

**R6. Skill-script reuse via tmpdir.** `prepare_workspace.split_sections`
writes files as a side effect. For the kata's in-memory flow I wrapped
it with a `tempfile.TemporaryDirectory` and read each file back into a
Pydantic `Section`. ~5 lines. Cheaper than reimplementing the regex +
8K-char chunk fallback, and if the skill's heuristic changes, the kata
follows for free.

**R7. Viz JSON compatibility is almost-free when you reuse the right
helpers.** The main `openaireview serve` UI expects
`{paragraphs, methods: {<key>: {comments: [{quote, paragraph_index, ...}]}}}`.
Reusing `reviewer.utils.split_into_paragraphs` +
`locate_comment_in_document` makes my kata output byte-compatible with
other methods' output under a `review_rounds__<model>` method key.

**R8. OpenRouter hangs without max_retries.** One persona subgraph got
stuck at cursor=0/7 for 15 minutes on a single kimi-k2.6 request that
never returned — timeout=180 alone didn't save us; LangChain needed
`max_retries=3` too. The other two parallel subgraphs kept going, but
the hung one blocked the join at `consolidate`. Set `timeout=90,
max_retries=3` on ChatOpenAI; expect tail-latency pain on reasoning
models via OpenRouter.

**R9. Cost tracking belongs in a callback, not the node body.**
LangChain's `BaseCallbackHandler.on_llm_end` receives the LLMResult
with `llm_output['token_usage']`, which on OpenRouter includes `cost`
(upstream dollar cost). One module-level collector, attached via
`ChatOpenAI(callbacks=[USAGE])`, accumulates across every node — 1-2
graph calls or 80, same API. Running the totals through the graph
state instead would cost a reducer + constant thread-safety worry.

**R10. Output file collisions are the UI's boundary.** Main
`openaireview` CLI writes `review_results/<slug>.json` and merges new
methods into the existing `methods` dict. I nearly wrote a separate
`<slug>_review_rounds.json` file, which `openaireview serve` would
index as a separate paper instead of another method on the same paper.
Matching the main CLI's merge convention was one extra `if
path.exists(): doc.setdefault("methods", {})[method_key] = block`.

**R11. Reasoning models + big structured-output schemas = systematic
failure.** Ran the same pipeline against `anthropic/claude-haiku-4-5`
and `moonshotai/kimi-k2.6` on the 25-page paper. Haiku cleared all
four structured-output nodes in one go (56 issues, 12 major / 30
moderate / 14 minor, $0.41). Kimi hit four different failures on the
same run: `plan_assignments` → `LengthFinishReasonError`,
`review_section` → `ValidationError` (missing `title` field),
`self_critique` × 2 → empty `parsed`, `consolidate` → truncated JSON.
Every single one was a case where kimi's reasoning step consumed
most of the 16384-token budget before visible output got emitted, so
the schema either didn't complete or never started. Graceful
fallbacks produced 60 "moderate" issues ($0.47) — functionally
usable but severity-untiered, because consolidate was the last
fallback-triggering call.

**The lesson isn't "kimi is bad"** — it's that reasoning models spend
tokens on a budget that's invisible to `max_tokens`, and big nested
Pydantic schemas (`ConsolidationOutput` with `list[ConsolidatedIssue]`)
are token-hungry on the output side. The two combine badly. For this
pipeline shape, a non-reasoning model is structurally a better fit.
If you need a reasoning model, either shrink the schema (emit
comments incrementally, not as a big list), drop `method="json_schema"`
back to `function_calling` (more forgiving parse path), or bump
`max_tokens` far past what looks reasonable.

**R12. Defensive fallbacks are a kata-appropriate pattern.** The
cleanest way to diagnose what kimi was doing wrong was to see *which
node* failed and *what* it returned. Five lines of `try: structured.
invoke(...) except: log + emit fallback` per node gave me four
separate `[warn]` lines in one run, each identifying the failing node
and truncated error. Without it, the first crash would have ended the
run at minute 3 and I'd have re-run to diagnose. With it, I got a
full graph execution with warnings surfaced in-line.

**Trade-off**: the graph now always completes, but silently produces
lower-quality output when a node fails. For a kata — valuable;
failures become visible artifacts. For production — dangerous;
you'd want an explicit "partial result" flag on state and a
downstream check that fails loudly before writing viz JSON.

---

## Surprises from the first build (prose-aggregate, minimax)

1. **Biggest surprise — subgraph outputs flood the parent state.** When 3
   persona subgraphs finalize concurrently, *every* field of their
   `PersonaState` gets written back to the parent. Without `output_schema`,
   `paper_text` (a non-reducer field) hit `InvalidUpdateError: Can receive
   only one value per step` at the fan-in. The fix is one line —
   `StateGraph(PersonaState, output_schema=PersonaOutput)` where
   `PersonaOutput` only contains `drafts` — but discovering it requires
   reading the error and internalizing that the subgraph boundary is a
   schema boundary, not an object boundary. This is not in Strands at all.

2. **Reducer gotcha I actually hit — `update_state` appends, doesn't
   replace.** First fork attempt wrote `{"drafts": [edited_d0, d1, d2]}`
   and expected replacement. Instead the `add` reducer ran and produced a
   6-element list. Critic_aggregate got 6 drafts, and the LLM silently
   dropped the absurd override as inconsistent — no error, wrong answer.
   Pragmatic fix: dedupe in `critic_aggregate` by keeping the latest entry
   per `persona_idx`. "Most recent wins" is what fork-and-replay and
   redo:N both conceptually want; the reducer was fighting that intent.

3. **Checkpointer feature I underestimated — cross-process resume is free.**
   Three separate CLI invocations (`run`, `resume`, `fork`) share state
   through `.checkpoints.db`; the graph doesn't know or care that the
   Python process restarted. Strands' session state is in-process and
   needs explicit serialization.

4. **`interrupt` vs. Strands HITL — concrete difference.** `interrupt(payload)`
   raises through the whole call stack and the checkpointer freezes the
   graph state at the interrupting node. Resume with `Command(resume=value)`
   re-invokes the same node and the `interrupt(...)` call returns `value`.
   No callback, no continuation — just a pause-and-return idiom. In
   Strands you'd wire an async callback or rebuild the prompt from a
   message store. LangGraph makes the pause *the* primitive.

5. **`update_state(as_node=...)` semantics — it asserts, it doesn't replay.**
   Passing `as_node="review_as_persona"` tells LangGraph "pretend this
   node just finished and wrote these values." The next invocation picks
   up from whatever was statically next (critic_aggregate). It does NOT
   re-run the subgraph; it lets you forge the subgraph's output. Powerful
   for debugging and what-ifs, but means the reducer runs against the
   forged values as if they came from a normal node write — hence #2.

6. **Subgraph composition clean points.** Parent keys and subgraph keys
   with matching names and reducers fan in cleanly; everything else needs
   `output_schema`. Viz (`draw_mermaid`) honors nesting, which helps
   reading; the `xray=True` flag controls whether subgraphs are expanded.

7. **Conditional edges vs. LLM-chosen routing — where I'd use which.**
   `route_from_gate` is three cases over a stringly-typed `decision` field;
   declarative conditional edges keep the state machine obvious in the
   topology printout. If the decision were "pick the best next subgraph
   based on content," I'd still let an LLM decide but have the LLM return
   the name of one of a fixed set of declared edges — Strands' wider
   LLM-driven routing wins when the set isn't fixed, which is rare in
   review-style workflows.

8. **Thing I'd redesign — use `edits` as the dedupe key, not `drafts`.**
   If `edits: dict[int, str]` were the channel that fork writes to, there'd
   be no `add`-reducer trap at all. `drafts` would stay append-only
   (audit log) and `edits` would be the authoritative override. Would
   also make the redo:N case symmetric — it's currently implicit.

9. **Primitive I'd *not* reach for on a production system — `update_state`
   as_node="X" for time-travel.** The forged-write semantics are useful
   for interactive debugging (Jupyter, a review UI), but shipping code
   that does `update_state` behind the user's back is a correctness
   nightmare — reducers run, nothing prevents you from writing values
   that violate invariants the rest of the graph assumed.

10. **Where I'd pick LangGraph over Strands now, and where I still
    wouldn't.** LangGraph for: durable HITL, auditable review-style
    workflows with fixed topology, anything where the checkpointer is the
    feature. Strands for: anything where the LLM is doing the routing,
    tool-heavy agents, or "one conversation loop" where a state machine
    would just be ceremony. The two are solving different problems despite
    looking similar on paper.

---

## Cross-pollination with PR #37

Ran on `examples/2602.18458v1.pdf` (MechEvalAgent paper, 25 pages via Mistral
OCR). The per-persona subgraph's `challenge → verdict` step uses prompts
adapted from `method_debate.py`. One observation worth citing in an
interview: the typed `PersonaState` carries `paper_text` through to the
verdict node for free — the state-threading bug PR #37 calls out as open
work (`claim_persistent` miss) is not expressible here because the state
schema guarantees the field is present.

## Running the verifications

- **Reducer proof:** `run`, confirm `state["drafts"]` has length 3.
- **Checkpoint proof:** `run`, kill process mid-way, re-run with same `--thread-id` — graph resumes.
- **Interrupt proof:** `run` pauses at `human_gate`; `resume <tid> approve` continues.
- **Time-travel proof:** `history <tid>`, pick a post-persona checkpoint, `fork` with a new draft.
- **Subgraph proof:** `topology` shows `review_as_persona` as a nested subgraph.

---

## Cross-pollination with PR #37

The per-persona subgraph's `challenge → verdict` step is lifted from
`method_debate.py` in PR #37 (`feat/progressive-debate`). PR #37's
`claim_persistent` miss — where the verdict node didn't have the source
passage in its context — was the concrete motivation: a typed `PersonaState`
makes that state-threading bug impossible. If the graph version catches
something the imperative version doesn't on the same paper, write it here
and cite it in interviews.

## Running the verifications

- **Reducer proof:** `run`, confirm `state["drafts"]` has length 3.
- **Checkpoint proof:** `run`, kill process mid-way, re-run with same `--thread-id` — graph resumes.
- **Interrupt proof:** `run` pauses at `human_gate`; `resume <tid> approve` continues.
- **Time-travel proof:** `history <tid>`, pick a post-persona checkpoint, `fork` with a new draft.
- **Subgraph proof:** `topology` shows `review_as_persona` as a nested subgraph.
