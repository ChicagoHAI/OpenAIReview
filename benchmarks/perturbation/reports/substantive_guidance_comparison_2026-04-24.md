# Substantive-guidance comparison — 2026-04-24

- error_type: `surface` · length: `short` · max_papers: `10`
- context_mode: `window`
- generator: `google/gemini-3-flash-preview`
- verifier: `anthropic/claude-sonnet-4-6` (reasoning=none)

## Summary

| Guidance | Papers | Cands | Gen | Gen yield | Valid (1-4) | Accepted (1-5) | Verif accept | End-to-end | Tokens/cand | Multiplier |
|----------|-------:|------:|----:|----------:|------------:|---------------:|-------------:|-----------:|------------:|-----------:|
| off | 10 | 2790 | 54 | 1.9% | 54 | 31 | 57.4% | 57.4% | 285 | 1.00× |
| on | 10 | 2790 | 54 | 1.9% | 54 | 39 | 72.2% | 72.2% | 287 | 1.01× |

## Verifier verdicts (test #5)

| Guidance | Substantive | Typo-shaped | Not-an-error | Parse-error |
|----------|------------:|------------:|-------------:|------------:|
| off | 31 | 10 | 13 | 0 |
| on | 39 | 10 | 5 | 0 |

## Verifier quote source

| Guidance | Generator-picked | Random-sampled | None available |
|----------|-----------------:|---------------:|---------------:|
| off | 40 | 12 | 2 |
| on | 54 | 0 | 0 |

## Metric definitions

- **off** removes the explicit typo-shaped vs substantive-error framing but keeps the same context mode, quote policy, and verifier.
- **on** includes the typo-shaped vs substantive-error framing.
- **Gen yield** = n_generated / n_candidates.
- **Verif accept** = n_accepted / n_valid_structural.
- **End-to-end** = n_accepted / n_generated.
- **Tokens/cand** = mean prompt tokens per candidate, averaged across paper×error_type calls.
- **Multiplier** is relative to guidance `off`.
