# Perturbation Benchmark Report

## Sources

- `benchmarks/perturbation/results_short` (length=short, models=['google/gemini-3-flash-preview', 'z-ai/glm-4.6', 'qwen/qwen3-235b-a22b-2507'])
- `benchmarks/perturbation/results_medium` (length=medium, models=['google/gemini-3-flash-preview', 'z-ai/glm-4.6', 'qwen/qwen3-235b-a22b-2507'])

## Ground Truth Summary

**10 papers**, 79 perturbations total:

- index_or_subscript: 20
- numeric_parameter: 20
- operator_or_sign: 19
- symbol_binding: 20

## Overall recall — per method (aggregated over models, papers, lengths)


| method                   | n_injected | n_detected | recall |
| ------------------------ | ---------- | ---------- | ------ |
| coarse                   | 237        | 27         | 11.4%  |
| zero_shot                | 237        | 27         | 11.4%  |
| progressive              | 229        | 94         | 41.0%  |
| progressive_consolidated | 229        | 81         | 35.4%  |
| progressive_preconsol    | 229        | 93         | 40.6%  |


## Recall — per length × method


| length | coarse         | zero_shot      | progressive    | progressive_consolidated | progressive_preconsol |
| ------ | -------------- | -------------- | -------------- | ------------------------ | --------------------- |
| medium | 8.5% (10/117)  | 8.5% (10/117)  | 44.0% (48/109) | 38.5% (42/109)           | 43.1% (47/109)        |
| short  | 14.2% (17/120) | 14.2% (17/120) | 38.3% (46/120) | 32.5% (39/120)           | 38.3% (46/120)        |


## Recall — per model × method


| model                  | coarse        | zero_shot     | progressive   | progressive_consolidated | progressive_preconsol |
| ---------------------- | ------------- | ------------- | ------------- | ------------------------ | --------------------- |
| gemini-3-flash-preview | 8.9% (7/79)   | 12.7% (10/79) | 25.3% (20/79) | 22.8% (18/79)            | 26.6% (21/79)         |
| glm-4.6                | 15.2% (12/79) | 12.7% (10/79) | 40.8% (29/71) | 35.2% (25/71)            | 39.4% (28/71)         |
| qwen3-235b-a22b-2507   | 10.1% (8/79)  | 8.9% (7/79)   | 57.0% (45/79) | 48.1% (38/79)            | 55.7% (44/79)         |


## Recall — per length × model × method


| length | model                  | coarse       | zero_shot    | progressive   | progressive_consolidated | progressive_preconsol |
| ------ | ---------------------- | ------------ | ------------ | ------------- | ------------------------ | --------------------- |
| medium | gemini-3-flash-preview | 12.8% (5/39) | 7.7% (3/39)  | 28.2% (11/39) | 25.6% (10/39)            | 30.8% (12/39)         |
| medium | glm-4.6                | 10.3% (4/39) | 15.4% (6/39) | 54.8% (17/31) | 48.4% (15/31)            | 51.6% (16/31)         |
| medium | qwen3-235b-a22b-2507   | 2.6% (1/39)  | 2.6% (1/39)  | 51.3% (20/39) | 43.6% (17/39)            | 48.7% (19/39)         |
| short  | gemini-3-flash-preview | 5.0% (2/40)  | 17.5% (7/40) | 22.5% (9/40)  | 20.0% (8/40)             | 22.5% (9/40)          |
| short  | glm-4.6                | 20.0% (8/40) | 10.0% (4/40) | 30.0% (12/40) | 25.0% (10/40)            | 30.0% (12/40)         |
| short  | qwen3-235b-a22b-2507   | 17.5% (7/40) | 15.0% (6/40) | 62.5% (25/40) | 52.5% (21/40)            | 62.5% (25/40)         |


## Recall — per error type × method (aggregated across models and lengths)


| method                   | index_or_subscript | numeric_parameter | operator_or_sign | symbol_binding | overall        |
| ------------------------ | ------------------ | ----------------- | ---------------- | -------------- | -------------- |
| coarse                   | 6/60 (10.0%)       | 6/60 (10.0%)      | 11/57 (19.3%)    | 4/60 (6.7%)    | 27/237 (11.4%) |
| zero_shot                | 10/60 (16.7%)      | 6/60 (10.0%)      | 5/57 (8.8%)      | 6/60 (10.0%)   | 27/237 (11.4%) |
| progressive              | 21/58 (36.2%)      | 24/58 (41.4%)     | 28/55 (50.9%)    | 21/58 (36.2%)  | 94/229 (41.0%) |
| progressive_consolidated | 17/58 (29.3%)      | 20/58 (34.5%)     | 26/55 (47.3%)    | 18/58 (31.0%)  | 81/229 (35.4%) |
| progressive_preconsol    | 20/58 (34.5%)      | 24/58 (41.4%)     | 28/55 (50.9%)    | 21/58 (36.2%)  | 93/229 (40.6%) |


## Recall by Error Type — per (model, method)


| model                  | method                   | index_or_subscript | numeric_parameter | operator_or_sign | symbol_binding | overall       |
| ---------------------- | ------------------------ | ------------------ | ----------------- | ---------------- | -------------- | ------------- |
| gemini-3-flash-preview | coarse                   | 2/20 (10.0%)       | 1/20 (5.0%)       | 3/19 (15.8%)     | 1/20 (5.0%)    | 7/79 (8.9%)   |
| gemini-3-flash-preview | progressive              | 3/20 (15.0%)       | 4/20 (20.0%)      | 7/19 (36.8%)     | 6/20 (30.0%)   | 20/79 (25.3%) |
| gemini-3-flash-preview | progressive_consolidated | 3/20 (15.0%)       | 3/20 (15.0%)      | 6/19 (31.6%)     | 6/20 (30.0%)   | 18/79 (22.8%) |
| gemini-3-flash-preview | progressive_preconsol    | 3/20 (15.0%)       | 5/20 (25.0%)      | 7/19 (36.8%)     | 6/20 (30.0%)   | 21/79 (26.6%) |
| gemini-3-flash-preview | zero_shot                | 3/20 (15.0%)       | 3/20 (15.0%)      | 2/19 (10.5%)     | 2/20 (10.0%)   | 10/79 (12.7%) |
| glm-4.6                | coarse                   | 3/20 (15.0%)       | 2/20 (10.0%)      | 4/19 (21.1%)     | 3/20 (15.0%)   | 12/79 (15.2%) |
| glm-4.6                | progressive              | 7/18 (38.9%)       | 7/18 (38.9%)      | 10/17 (58.8%)    | 5/18 (27.8%)   | 29/71 (40.8%) |
| glm-4.6                | progressive_consolidated | 5/18 (27.8%)       | 6/18 (33.3%)      | 10/17 (58.8%)    | 4/18 (22.2%)   | 25/71 (35.2%) |
| glm-4.6                | progressive_preconsol    | 6/18 (33.3%)       | 7/18 (38.9%)      | 10/17 (58.8%)    | 5/18 (27.8%)   | 28/71 (39.4%) |
| glm-4.6                | zero_shot                | 5/20 (25.0%)       | 1/20 (5.0%)       | 2/19 (10.5%)     | 2/20 (10.0%)   | 10/79 (12.7%) |
| qwen3-235b-a22b-2507   | coarse                   | 1/20 (5.0%)        | 3/20 (15.0%)      | 4/19 (21.1%)     | 0/20 (0.0%)    | 8/79 (10.1%)  |
| qwen3-235b-a22b-2507   | progressive              | 11/20 (55.0%)      | 13/20 (65.0%)     | 11/19 (57.9%)    | 10/20 (50.0%)  | 45/79 (57.0%) |
| qwen3-235b-a22b-2507   | progressive_consolidated | 9/20 (45.0%)       | 11/20 (55.0%)     | 10/19 (52.6%)    | 8/20 (40.0%)   | 38/79 (48.1%) |
| qwen3-235b-a22b-2507   | progressive_preconsol    | 11/20 (55.0%)      | 12/20 (60.0%)     | 11/19 (57.9%)    | 10/20 (50.0%)  | 44/79 (55.7%) |
| qwen3-235b-a22b-2507   | zero_shot                | 2/20 (10.0%)       | 2/20 (10.0%)      | 1/19 (5.3%)      | 2/20 (10.0%)   | 7/79 (8.9%)   |


## Token Usage and Cost


| model                  | cells   | prompt tokens  | completion tokens | cost (USD)   |
| ---------------------- | ------- | -------------- | ----------------- | ------------ |
| gemini-3-flash-preview | 50      | 4,441,423      | 775,795           | $4.5483      |
| glm-4.6                | 47      | 4,385,578      | 2,971,152         | $7.3550      |
| qwen3-235b-a22b-2507   | 50      | 4,983,944      | 1,257,172         | $0.4796      |
| **total**              | **147** | **13,810,945** | **5,004,119**     | **$12.3829** |


