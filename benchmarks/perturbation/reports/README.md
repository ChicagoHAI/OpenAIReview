# Perturbation benchmark reports

Rendered markdown reports. Raw JSON summaries live next to the run artifacts
under `benchmarks/perturbation/results/<length>/...`.

## Current experiments

| Experiment | Latest | Key finding |
|---|---|---|
| Context-mode comparison | [`context_mode_comparison_2026-04-22.md`](context_mode_comparison_2026-04-22.md) | `related` > `window` > `none`. `window` is the practical sweet spot (3× baseline cost, 82.5% end-to-end acceptance). |
| Substantive-guidance A/B | [`substantive_guidance_comparison_2026-04-24.md`](substantive_guidance_comparison_2026-04-24.md) | Guidance-on wins +14.8 pts end-to-end (57.4% → 72.2%) under sonnet-4-6 @ reasoning=none with the tuned prompt. Keep as default. Earlier run at `reasoning=medium`: [`..._sonnet_medium.md`](substantive_guidance_comparison_2026-04-24_sonnet_medium.md) (+10 pts). |

## Coarse-model benchmark

| Report | Notes |
|---|---|
| [`combined.md`](combined.md) | Gemini-flash / glm-4.6 / qwen3-235b on short + medium papers |
| [`surface_3models_short_medium.md`](surface_3models_short_medium.md) | Earlier 3-model surface-error run; largely superseded by `combined.md` |

## Session notes

- [`revision_session_notes_2026-04-22.md`](revision_session_notes_2026-04-22.md) — design decisions from the verifier-tuning session

## Logs

`logs/` holds run stdout/stderr; gitignored.
