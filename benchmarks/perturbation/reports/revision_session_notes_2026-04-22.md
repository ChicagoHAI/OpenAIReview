# Benchmark design notes — 2026-04-22

Handoff doc for the next session. Focus: design decisions and open questions about the perturbation benchmark (and briefly, the conference study).

---

## 1. Perturbation generation: selection and verifiability

### "Undetectable-by-construction" — core concept

A perturbation is undetectable-by-construction if the paper itself provides no information to contradict it. A reader reading only the paper would have no way to flag it as wrong. Examples:

- Numeric parameter stated once, never referenced downstream (flip 0.5 → 0.25, no contradiction).
- Symbol binding swap into an undefined symbol in an isolated equation.
- Operator flip in a standalone expression with no linked result downstream.

These exist in the current benchmark because the generator's ±200-char window sometimes isn't enough for it to find downstream dependencies, and it generates "errors" that aren't actually detectable.

---

## 2. The ±200-char context window is arbitrary

In `extract.py`, each candidate gets a ±200-char context passed to the generator. This is probably a prompt-budget heuristic, not a principled choice.

### What it excludes

- **Long-range definitions.** `\alpha` defined in §2 ("let α denote the learning rate"), used in §7. Generator sees §7 only, can't build a `why_wrong` that cites the §2 definition.
- **Cross-reference chains.** Theorem 2 used in proof of Theorem 5, where the perturbation breaks the chain across sections.
- **Structural invariants.** A parameter appearing in three equations; changing it breaks all three. Only one appears in the 400-char window.

### Bias this creates

The benchmark is weighted toward errors whose contradiction is *visible in one paragraph*. Probably easier than the distribution of errors real human reviewers catch. Progressive especially might benefit from being the only method that can do long-range reasoning — widening the window would test that hypothesis.

### Fix options (and costs)

- **Downstream reference filter (§3 below)**: targeted, preserves narrow generator prompts, guarantees detectability. Recommended path.

---

## 3. Downstream reference filter (proposed — the key idea)

Instead of giving the generator more context, *pre-scan* the paper for each candidate span and include only the specific downstream references it'd need.

### Stage 1 — lexical pre-scan (free)

For each candidate span, extract **distinctive tokens** likely to appear as references elsewhere:

- LaTeX symbols (`\alpha`, `\lambda`, `\mathcal{L}`)
- Variable subscripts (`x_i`, `W_{ij}`)
- Numeric literals with variable assignments (`n = 100`, not standalone `0.5`)
- Named objects (`Theorem 2`, `Eq.~\ref{eq:loss}`)

Search the rest of the paper for other occurrences of these tokens. Keep the span only if ≥1 downstream hit.

**False-positive handling**: require tokens with ≥2 characters, or require the surrounding context to match a "definition/usage" pattern (token assigned a value, part of another equation, cited by number). Avoids matching every `n` or `x`.

Rejections:

- Equation with a one-off constant that never appears again
- Symbol used in a single isolated equation with no upstream definition
- Named definition only shown once with no references

### Stage 2 — targeted downstream snippets in the prompt

For surviving spans, add a `downstream_references` field to the candidates JSON:

```json
{
  "span_id": "S0042",
  "text": "...$\\alpha = 0.5$...",
  "context": "...±200 char window...",
  "downstream_references": [
    {"offset": 5820, "snippet": "Eq. 3.1: $\\nabla L = \\alpha \\cdot g$"},
    {"offset": 9103, "snippet": "Eq. 4.2: $x_{t+1} = x_t - \\alpha g_t$"}
  ]
}
```

The generator now has exactly the information to craft perturbations that break *known* downstream relationships. Its `why_wrong` can cite which specific reference it contradicts.

### Cost and coverage

- Current: ~$0.10/paper
- Filter + 2–3 downstream snippets per candidate: ~$0.15–0.25/paper
- Whole-paper context: ~$1–2/paper

Roughly 5–10× less than whole-paper while unlocking long-range perturbations.

### Limitations

- Surface errors (operator, symbol binding, index, numeric) work well — they all involve concrete tokens.
- Formal errors (missing proof case, wrong direction) are weaker fit — contradiction is structural, not lexical. Might need a separate filter for those (e.g., proof parse → check cited lemmas still hold). Surface errors are the bulk of our data anyway.

---

## 4. Perturbation validation: contradiction-pair verifier (proposed)

We want to guarantee that each retained perturbation is **a real, detectable error**. Prior idea (run reviewers on both clean and corrupted) is bad:

- Doubles cost (~$5 per extra run)
- Biases toward errors current reviewers can catch — precisely the wrong bias for a benchmark that should reward *stronger* reviewers at detecting subtle errors

Better: validate at **generation time** with a narrower question.

### The design

Modify the generator's output schema. Require two outputs alongside the perturbation:

1. The perturbed span (already have).
2. An **exact verbatim quote** from elsewhere in the paper that contradicts the perturbation — not prose explanation; a copy-paste quote.

Then run a **verifier LLM** (strong model, e.g., Opus with reasoning) on only those two short snippets:

> *Does quote A contradict statement B? yes/no, with a one-sentence explanation of the contradiction.*

Keep perturbations where the verifier says yes.

### Why this avoids both cost and catchability objections

- **Cost**: one verifier call per perturbation at generation time (~$0.50/benchmark for 79 perturbations on Opus). Amortized to zero over the benchmark's lifetime — not per reviewer run.
- **Catchability bias**: the verifier isn't doing open-ended paper review. It's local entailment reasoning on two short snippets. That's a much easier task than full-paper review. A strong model reliably solves it even for errors current reviewers miss in full-paper mode. So we can *retain* "subtle but catastrophic" errors that reviewers fail on — which is exactly what a discriminating benchmark should have.

The key insight: a valid perturbation is one where *a careful reader could detect it given the paper*. The verifier simulates "careful reader focused on the relevant passage," which is a strictly stronger oracle than any reviewer being evaluated.

### Native hook to §3

The `downstream_references` field from the lexical filter is exactly what the generator uses to pick its primary contradiction. The verifier then checks that specific pair. The two features compose cleanly.

### What it doesn't catch

Perturbations where contradiction is distributed across multiple places (changing a symbol breaks three unrelated equations, each of which only mildly conflicts on its own). For v1, require the generator to pick one primary citation (lossy but workable). V2 could support a "primary + supporting" list.

### Calibration

Small human eval on ~20 perturbations, rated on:

- Is this a real error? (yes/no)
- Is it detectable from the paper alone? (yes/no)

Compare to verifier labels. If agreement >90%, cite that number in the paper and treat the verifier as the operational filter going forward. Tiny cost, strong defense.

---

## 5. Conference study — matrix of signal pairs

Separately from the perturbation benchmark, Yanai flagged that using ICLR accept/reject as the quality signal is contentious (reviewers will argue ICLR reviews are noisy).

Plan: broaden the conference study to a **matrix of high-quality vs low-quality signal pairs**, so a consistent finding across independent noise sources is harder to dismiss than a single accept/reject contrast.

### Suggested pairs


| High-quality signal            | Low-quality signal                      | What it buys                                                                                                                                                    |
| ------------------------------ | --------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Top-cited n years later        | Never-published anywhere                | Completely sidesteps ICLR-is-noisy objection; uses community judgment over time on both ends. Largest separation. Main confound: topic popularity / author fame |
| Spotlight / Outstanding / Oral | Rejected (or bottom 5% scores)          | Same-venue same-era controlled contrast; topic confounds matched. Leans on reviewer judgment at submission time                                                 |
| Top 5% overall scores          | Bottom 5% overall scores                | Pure reviewer-signal contrast (no AC noise). Cleanly within-reviewer-pool                                                                                       |
| Accepted                       | Never-published-anywhere-within-n-years | Filters the "rejected but actually fine, got into NeurIPS next cycle" confound                                                                                  |


### Minimum viable version

Pick three pairs that span independent noise sources:

1. Spotlight vs reject (reviewer-at-time)
2. Top 5% scores vs bottom 5% scores (pure reviewer signal)
3. Top-cited vs never-published (community-over-time)

Headline number: if a review system ranks consistently across all three, neither "ICLR reviewers are garbage" nor "citations just track hype" can knock the finding down.

Top-cited vs never-published is probably the strongest single contrast — if we have to pick one, it's this. Citation-per-year-normalized version as a robustness check for the topic-popularity confound.

---

