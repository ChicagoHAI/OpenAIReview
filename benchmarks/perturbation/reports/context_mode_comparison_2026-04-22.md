# Context-mode comparison — 2026-04-22

- error_type: `surface` · length: `short` · max_papers: `10`
- generator: `google/gemini-3-flash-preview`
- verifier: `google/gemini-3-flash-preview` (reasoning=none)

## Summary


| Mode    | Papers | Cands | Gen | Gen yield | Valid (1-4) | Accepted (1-5) | Verif accept | End-to-end | Tokens/cand | Multiplier |
| ------- | ------ | ----- | --- | --------- | ----------- | -------------- | ------------ | ---------- | ----------- | ---------- |
| none    | 10     | 2790  | 64  | 2.3%      | 63          | 28             | 44.4%        | 43.8%      | 99          | 1.00×      |
| window  | 10     | 2790  | 80  | 2.9%      | 76          | 66             | 86.8%        | 82.5%      | 285         | 2.89×      |
| related | 10     | 2790  | 72  | 2.6%      | 72          | 63             | 87.5%        | 87.5%      | 885         | 8.98×      |


## Summary (compact)


| Mode    | Papers | Cands | Gen | Gen yield | Accepted | End-to-end |
| ------- | ------ | ----- | --- | --------- | -------- | ---------- |
| none    | 10     | 2790  | 64  | 2.3%      | 28       | 43.8%      |
| window  | 10     | 2790  | 80  | 2.9%      | 66       | 82.5%      |
| related | 10     | 2790  | 72  | 2.6%      | 63       | 87.5%      |


## Verifier verdicts (test #5)


| Mode    | Substantive | Typo-shaped | Not-an-error | Parse-error |
| ------- | ----------- | ----------- | ------------ | ----------- |
| none    | 28          | 17          | 15           | 3           |
| window  | 66          | 4           | 0            | 6           |
| related | 63          | 1           | 3            | 5           |


## Verifier quote source

How the verifier's contradicts-quote was sourced. In `none` mode the generator produces no quote, so the verifier draws a random related passage from the paper; in `window` / `related` modes the generator picks one.


| Mode    | Generator-picked | Random-sampled | None available |
| ------- | ---------------- | -------------- | -------------- |
| none    | 12               | 42             | 9              |
| window  | 73               | 3              | 0              |
| related | 72               | 0              | 0              |


## Metric definitions

- **Gen yield** = n_generated / n_candidates — how liberally the generator produces perturbations given its available context. Higher is not better by itself.
- **Verif accept** = n_accepted / n_valid_structural — of perturbations that passed structural tests 1–4, the fraction the verifier rated substantive.
- **End-to-end** = n_accepted / n_generated — the product of structural validity and verifier acceptance.
- **Tokens/cand** = mean prompt tokens per candidate, averaged across paper×error_type calls.
- **Multiplier** is relative to the `none` mode (the cheapest baseline).

