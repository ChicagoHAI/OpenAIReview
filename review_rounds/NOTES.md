# review-rounds — post-mortem

Interview fuel, not OSS docs. Surprises from the actual build on
`examples/2602.18458v1.pdf` against `minimax/minimax-m2.7` via OpenRouter.

---

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
