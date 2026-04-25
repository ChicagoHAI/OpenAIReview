# Substantive-guidance comparison — 2026-04-24

- error_type: `surface` · length: `short` · max_papers: `10`
- context_mode: `window`
- generator: `google/gemini-3-flash-preview`
- verifier: `anthropic/claude-sonnet-4-6` (reasoning=medium)

## Summary

| Guidance | Papers | Cands | Gen | Gen yield | Valid (1-4) | Accepted (1-5) | Verif accept | End-to-end | Tokens/cand | Multiplier |
|----------|-------:|------:|----:|----------:|------------:|---------------:|-------------:|-----------:|------------:|-----------:|
| off | 10 | 2790 | 60 | 2.2% | 60 | 32 | 53.3% | 53.3% | 285 | 1.00× |
| on | 10 | 2790 | 60 | 2.2% | 60 | 38 | 63.3% | 63.3% | 287 | 1.01× |

## Verifier verdicts (test #5)

| Guidance | Substantive | Typo-shaped | Not-an-error | Parse-error |
|----------|------------:|------------:|-------------:|------------:|
| off | 32 | 9 | 19 | 0 |
| on | 38 | 9 | 13 | 0 |

## Verifier quote source

| Guidance | Generator-picked | Random-sampled | None available |
|----------|-----------------:|---------------:|---------------:|
| off | 48 | 11 | 1 |
| on | 54 | 6 | 0 |

## Metric definitions

- **off** removes the explicit typo-shaped vs substantive-error framing but keeps the same context mode, quote policy, and verifier.
- **on** includes the typo-shaped vs substantive-error framing.
- **Gen yield** = n_generated / n_candidates.
- **Verif accept** = n_accepted / n_valid_structural.
- **End-to-end** = n_accepted / n_generated.
- **Tokens/cand** = mean prompt tokens per candidate, averaged across paper×error_type calls.
- **Multiplier** is relative to guidance `off`.
