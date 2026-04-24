# Verifier evaluation harness

Measures the substantive-error verifier's agreement with hand-labeled gold verdicts.

## Run

Training set:
```
python -m benchmarks.perturbation.analyses.verifier_eval.run_eval --variant before
python -m benchmarks.perturbation.analyses.verifier_eval.run_eval --variant after
```

Held-out set:
```
python -m benchmarks.perturbation.analyses.verifier_eval.run_eval --variant before \
    --gold benchmarks/perturbation/analyses/verifier_eval/gold_set_heldout.json --tag heldout
python -m benchmarks.perturbation.analyses.verifier_eval.run_eval --variant after \
    --gold benchmarks/perturbation/analyses/verifier_eval/gold_set_heldout.json --tag heldout
```

### Variants

**`before` — legacy prompt, no structural precheck.** The starting baseline; everything goes to the LLM.

- Prompt includes the generator's `why_wrong` rationale alongside the (original, perturbed, quote) triple. The model can lean on the generator's stated reason for the contradiction.
- No-quote short-circuit: if the perturbation has no `contradicts_quote`, the verifier returns `not-an-error` without an LLM call.
- No structural precheck: every perturbation goes to the LLM regardless of how malformed it looks.

**`after` — tuned prompt, structural precheck enabled.** The production setup.

- `why_wrong` removed from the prompt — generators were too easily fabricating plausible-sounding rationales that bluffed past the verifier (notably, this drove `symbol_binding` from 24% → 100% accuracy on training).
- 3-step judgment procedure with explicit tie-breaking:
  1. **Self-coherence** on the perturbed span alone — flag malformations like mixed-direction inequality chains, type/unit mismatches, operator salad, or symbols replaced with letters never bound in the quote/original.
  2. **Quote specificity** — the cited quote must literally state the original value/symbol/operator (or an obvious equivalent). A quote that only mentions the same variable or topic is not enough.
  3. **Downstream dependence** — does the perturbation actually break a statement the paper relies on elsewhere? If the value/symbol is stated once and never reused → typo-shaped.
- Tie-breakers: when ambiguous between substantive and typo-shaped, choose typo-shaped. When no quote available and the perturbed span is a bare symbol swap or local index shift, also typo-shaped.
- No-quote short-circuit removed: even without a quote, the LLM judges the perturbed span on its own merits (catches bare-symbol-swap typos that the legacy short-circuit miscategorized as not-an-error).
- Structural precheck before the LLM call: deterministic regex rules reject obvious malformations without spending a token. Rules:
  - Runaway perturbed span (>2× original length + 50 chars) — probably a span-extraction bug.
  - Literal escape artifacts (`\n` / `\t` / `\r` not followed by a letter, when not in original) — pipeline bug, not a real perturbation.
  - Mixed-direction inequality chain inside math content (`<` and `>` both present in a single math blob) — malformed by construction.
  - Operator salad (two consecutive binary inequality operators).
- JSON salvage: when the LLM output is truncated mid-JSON (reasoning ate the budget), regex-recovers the verdict token from the partial response so a single bad call doesn't drop a perturbation.

Each run writes to a canonical path under `results/` (rerun overwrites in place):

| file | contents |
|---|---|
| `results/training_before.json` | legacy verifier on training gold set |
| `results/training_after.json` | new verifier on training gold set |
| `results/heldout_before.json` | legacy verifier on held-out gold set |
| `results/heldout_after.json` | new verifier on held-out gold set |

Each file's `rows` array has per-example predictions: `perturbation_id`, `original`, `perturbed`, `gold_label`, `pred_label`, `pred_reason`, `rationale`, `correct`. The top level has aggregate stats: `accuracy`, `per_class`, `confusion_matrix`, `per_error_type`, `wall_time_sec`.

## `gold_set.json` schema

Each row in `examples`:

| field | meaning |
|---|---|
| `idx` | row index in the source aggregation |
| `paper` | source paper directory |
| `perturbation_id` | unique id from the original manifest |
| `span_id` | candidate span id |
| `error` | one of `numeric_parameter`, `operator_or_sign`, `index_or_subscript`, `symbol_binding` |
| `original`, `perturbed` | the spans |
| `why_wrong` | generator's stated reason (legacy prompt uses this) |
| `contradicts_quote` | quote attached by the generator |
| `quote_source` | `generator` \| `none-available` |
| `gold_label` | `substantive` \| `typo-shaped` \| `not-an-error` |
| `rationale` | human-written justification for the label |

## Labeling rubric

- **substantive**: perturbed span is well-formed in isolation, quote states the original concretely, and the change propagates downstream.
- **typo-shaped**: malformed on its face (mixed inequality chains, operator salad, escape artifacts, runaway spans), bare symbol swap to an undefined letter, or a purely local change never referenced elsewhere.
- **not-an-error**: the attached quote does not actually contradict the perturbation.

## Results — training set (89 examples, 47 substantive / 30 typo-shaped / 12 not-an-error)

Production verifier: **Claude Sonnet 4.6 @ reasoning=none** with the tuned (`after`) prompt.
Opus 4.7 and Sonnet @ medium are reported for reference; neither is the default.

| model                  | variant | accuracy  | substantive F1 | typo-shaped F1 | not-an-error F1 |
|---|---|---|---|---|---|
| Opus 4.7 medium        | before  | 61.8%     | 0.81 | 0.11 | 0.46 |
| Opus 4.7 medium        | after   | **89.9%** | 0.96 | 0.86 | 0.74 |
| Sonnet 4.6 medium      | after   | 83.1%     | 0.85 | 0.85 | 0.75 |
| Sonnet 4.6 none (prod) | after   | **86.5%** | 0.88 | 0.88 | 0.80 |

Per-error-type accuracy (`after`):

| error type         | Opus 4.7 | Sonnet medium | Sonnet none |
|---|---|---|---|
| numeric_parameter  | 100%  | 100%  | 100% |
| symbol_binding     | 100%  | 81.0% | 95.2% |
| operator_or_sign   | 88.0% | 76.0% | 76.0% |
| index_or_subscript | 70.0% | 75.0% | 75.0% |

Sonnet @ `reasoning=none` outperforms Sonnet @ `medium` on every metric, despite (or because of) emitting no thinking budget. The biggest gain is `symbol_binding` (+14pt): the prompt explicitly says "almost always typo-shaped"; medium reasoning was talking itself out of the rule. Cheaper AND more accurate.

## Results — held-out set (83 examples, 47 substantive / 24 typo-shaped / 12 not-an-error)

Built from `substantive_guidance_compare` runs not seen during prompt iteration, plus 12 fresh synthetic not-an-error cases. Tests generalization. See `gold_set_heldout.json`.

| model                  | variant | accuracy  | substantive F1 | typo-shaped F1 | not-an-error F1 |
|---|---|---|---|---|---|
| Opus 4.7 medium        | before  | 63.9%     | 0.79 | 0.07 | 0.59 |
| Opus 4.7 medium        | after   | **85.5%** | 0.92 | 0.80 | 0.67 |
| Sonnet 4.6 medium      | after   | 84.3%     | 0.89 | 0.81 | 0.75 |
| Sonnet 4.6 none (prod) | after   | **88.0%** | 0.93 | 0.82 | 0.82 |

Per-error-type accuracy on held-out (`after`):

| error type         | Opus 4.7 | Sonnet medium | Sonnet none |
|---|---|---|---|
| numeric_parameter  | 96.2% | 88.5% | 92.3% |
| symbol_binding     | 91.7% | 87.5% | 91.7% |
| operator_or_sign   | 85.0% | 85.0% | 90.0% |
| index_or_subscript | 53.8% | 69.2% | 69.2% |

Sonnet @ none beats Opus @ medium on held-out (88.0% vs 85.5%) and the training-to-held-out gap is −1.5 pts (i.e. held-out *exceeds* training — a sign the prompt isn't overfit). Production setting: **Sonnet 4.6 @ reasoning=none with the tuned (`after`) prompt.**

## Interpretation

Structural precheck alone catches ~5 typo-shaped examples per set (mixed-direction inequality chains, broken sandwiches, runaway spans, literal `\n`/`\t`/`\r` escape artifacts) with zero false positives. Removing the no-quote short-circuit (so bare symbol swaps with no quote can be judged typo-shaped instead of not-an-error) drives most of the `symbol_binding` accuracy jump. The prompt's self-coherence + quote-specificity + downstream-dependence steps with the explicit "typo vs not-an-error" tie-breaking rule handle the rest.

Residual hard cases cluster in `index_or_subscript` — summation-index shifts where whether the boundary term is load-bearing requires more paper context than a single quote provides.
