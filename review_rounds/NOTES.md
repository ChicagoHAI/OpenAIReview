# review-rounds — post-mortem

Ten lines max. Interview fuel, not OSS docs. Fill in after Day 2.

---

1. **Biggest surprise:**
2. **Reducer gotcha I actually hit:**
3. **Checkpointer feature I underestimated:**
4. **`interrupt` vs. Strands HITL — concrete difference:**
5. **`update_state` as_node semantics:**
6. **Subgraph composition — what crossed the boundary cleanly, what didn't:**
7. **Conditional edges vs. LLM-chosen routing — where I'd use which:**
8. **Thing I'd redesign if I started over:**
9. **Primitive I'd *not* reach for on a production system:**
10. **Where I'd pick LangGraph over Strands now, and where I still wouldn't:**

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
