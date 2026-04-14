# Surface Error Detection Benchmark Report

## Run Configuration


| Setting         | Value                                                                             |
| --------------- | --------------------------------------------------------------------------------- |
| Papers          | 5 short (2k-7k words) + 5 medium (7k-17k words)                                   |
| Error type      | Surface (operator_or_sign, symbol_binding, index_or_subscript, numeric_parameter) |
| n_per_error     | 2 (target; actual varies due to span overlap rejection)                           |
| Perturb model   | google/gemini-3-flash-preview                                                     |
| Score model     | google/gemini-3-flash-preview (LLM-as-judge)                                      |
| Substring match | Fuzzy (_quote_coverage >= 0.75)                                                   |
| Review models   | gemini-3-flash-preview, glm-4.6, qwen3-235b-a22b-2507                             |
| Review methods  | zero_shot, progressive                                                            |


## Ground Truth Summary

**short** papers: 20 total perturbations

- operator_or_sign: 7
- symbol_binding: 6
- index_or_subscript: 3
- numeric_parameter: 4

**medium** papers: 27 total perturbations

- operator_or_sign: 11
- symbol_binding: 3
- index_or_subscript: 7
- numeric_parameter: 6

## Recall by Model x Method


| model                  | method      | length | gt  | detected | recall |
| ---------------------- | ----------- | ------ | --- | -------- | ------ |
| gemini-3-flash-preview | zero_shot   | short  | 20  | 5        | 25.0%  |
| gemini-3-flash-preview | progressive | short  | 20  | 4        | 20.0%  |
| glm-4.6                | zero_shot   | short  | 20  | 3        | 15.0%  |
| glm-4.6                | progressive | short  | 20  | 10       | 50.0%  |
| qwen3-235b-a22b-2507   | zero_shot   | short  | 20  | 3        | 15.0%  |
| qwen3-235b-a22b-2507   | progressive | short  | 20  | 11       | 55.0%  |
| gemini-3-flash-preview | zero_shot   | medium | 27  | 2        | 7.4%   |
| gemini-3-flash-preview | progressive | medium | 27  | 11       | 40.7%  |
| glm-4.6                | zero_shot   | medium | 27  | 4        | 14.8%  |
| glm-4.6                | progressive | medium | 27  | 12       | 44.4%  |
| qwen3-235b-a22b-2507   | zero_shot   | medium | 27  | 4        | 14.8%  |
| qwen3-235b-a22b-2507   | progressive | medium | 27  | 11       | 40.7%  |


### Overall Recall (short + medium combined)


| model                  | method      | gt  | detected | recall |
| ---------------------- | ----------- | --- | -------- | ------ |
| gemini-3-flash-preview | zero_shot   | 47  | 7        | 14.9%  |
| gemini-3-flash-preview | progressive | 47  | 15       | 31.9%  |
| glm-4.6                | zero_shot   | 47  | 7        | 14.9%  |
| glm-4.6                | progressive | 47  | 22       | 46.8%  |
| qwen3-235b-a22b-2507   | zero_shot   | 47  | 7        | 14.9%  |
| qwen3-235b-a22b-2507   | progressive | 47  | 22       | 46.8%  |


## Recall by Error Type (all papers combined)


| model                  | method      | operator_or_sign | symbol_binding | index_or_subscript | numeric_parameter | overall     |
| ---------------------- | ----------- | ---------------- | -------------- | ------------------ | ----------------- | ----------- |
| gemini-3-flash-preview | zero_shot   | 0/18 (0%)        | 1/9 (11%)      | 2/10 (20%)         | 4/10 (40%)        | 7/47 (15%)  |
| gemini-3-flash-preview | progressive | 6/18 (33%)       | 2/9 (22%)      | 2/10 (20%)         | 5/10 (50%)        | 15/47 (32%) |
| glm-4.6                | zero_shot   | 2/18 (11%)       | 1/9 (11%)      | 2/10 (20%)         | 2/10 (20%)        | 7/47 (15%)  |
| glm-4.6                | progressive | 7/18 (39%)       | 5/9 (56%)      | 4/10 (40%)         | 6/10 (60%)        | 22/47 (47%) |
| qwen3-235b-a22b-2507   | zero_shot   | 1/18 (6%)        | 2/9 (22%)      | 1/10 (10%)         | 3/10 (30%)        | 7/47 (15%)  |
| qwen3-235b-a22b-2507   | progressive | 7/18 (39%)       | 5/9 (56%)      | 4/10 (40%)         | 6/10 (60%)        | 22/47 (47%) |


## Token Usage and Cost


| length    | model                  | cells  | prompt tokens | completion tokens | cost (USD)  |
| --------- | ---------------------- | ------ | ------------- | ----------------- | ----------- |
| short     | gemini-3-flash-preview | 10     | 413,901       | 64,833            | $0.4014     |
| short     | glm-4.6                | 10     | 568,607       | 511,241           | $1.1931     |
| short     | qwen3-235b-a22b-2507   | 10     | 464,451       | 111,520           | $0.0441     |
| medium    | gemini-3-flash-preview | 10     | 828,309       | 140,317           | $0.8350     |
| medium    | glm-4.6                | 10     | 1,031,211     | 687,402           | $1.7082     |
| medium    | qwen3-235b-a22b-2507   | 10     | 884,255       | 186,626           | $0.0814     |
| **total** |                        | **60** | **4,190,734** | **1,701,939**     | **$4.2632** |


## Consolidation Impact on Progressive Recall

The progressive method produces comments in multiple passes, then consolidates (deduplicates/merges) them. The tables above report **pooled** recall (consolidated + pre-consolidation comments fed together to the scorer). Below is the breakdown showing whether consolidation helps or hurts:

| model | consolidated | pre-consolidation | pooled | comments (consol / pre-consol) |
|---|---:|---:|---:|---|
| gemini-3-flash-preview | 14/47 (30%) | 15/47 (32%) | 15/47 (32%) | 78 / 103 |
| glm-4.6 | 22/47 (47%) | 21/47 (45%) | 22/47 (47%) | 141 / 151 |
| qwen3-235b-a22b-2507 | 18/47 (38%) | 20/47 (43%) | 22/47 (47%) | 112 / 263 |

**Findings:**
- **gemini**: consolidation drops 1 detection (30% vs 32% pre-consol). Minimal impact — comment counts are similar (78 vs 103).
- **glm-4.6**: consolidation is neutral or slightly helpful (+1 detection vs pre-consol alone). The consolidation step may produce more focused explanations that score better with the LLM judge.
- **qwen**: consolidation hurts the most — drops from 20 to 18 detections. qwen generates far more raw comments (263 pre-consolidation vs 112 after), so consolidation aggressively prunes. Pooling recovers the lost detections and adds 2 more.

Note: consolidation is **not** a strict subset of pre-consolidation — it merges and rewrites comments, creating new ones with different quotes and explanations. This is why `pooled > pre-consolidation` for qwen (22 > 20): the 2 extra detections came from newly synthesized consolidated comments that matched perturbations the raw pre-consolidation set missed.

Pooling (the current default in `cmd_score`) is the safest strategy since it captures catches from both dropped and newly created comments. The progressive recall numbers in the main tables above use pooled scoring.

## Caveats

1. **Ground truth is under-counted.** The perturb stage asks for `n_per_error=2` (target 8 perturbations per paper), but the LLM often picks the same candidate span for both perturbations within an error type. The validator correctly rejects the duplicate, yielding ~4-5 valid perturbations per paper on average instead of 8. One short paper (paper_002) produced 0 perturbations due to a flaky LLM response.
2. **Fuzzy substring matching.** The score uses `_quote_coverage >= 0.75` to match the perturbed string against comment quotes, followed by an LLM-as-judge on the explanation. This can miss valid catches where the reviewer heavily paraphrases the quoted text.
3. **Cost reporting.** The `cost_usd` field comes from OpenRouter response metadata. Values for qwen are suspiciously low relative to token volume and may undercount actual billing.

