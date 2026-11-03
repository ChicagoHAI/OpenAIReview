# PIS: Probabilistic Inconsistency Signal for verifier-reliability analysis

**Experimental contribution for Issue #23 (Evaluation / Improve comment quality).**

**Research question:** can a PIS-style evidential uncertainty interval identify cases where the perturbation verifier is unreliable?

**Headline result (frozen scope): an honest null, plus a diagnosis.**
The pre-registered primary signal (interval width W = U − L from a Qwen2.5-7B evidence elicitation) does **NOT** predict verifier errors (AUROC 0.502, 95% CI [0.377, 0.634], n = 89, 22 errors). Selective verification on W provides no calibrated benefit (permutation p = 0.145). Gold-blind audits show the elicitation itself — not the interval algebra — is the weak link: two assessors produce structurally different evidence decompositions with near-zero width-rank correlation (ρ ≈ 0.05), and the stronger assessor self-collapses the interval into a point classifier. Full report: `docs/RESULTS.md`.

---

## What this module is

* A self-contained evaluator producing, per perturbation, a Dempster–Shafer interval [L, U] over the inconsistency hypothesis from itemized evidence (support / against / unresolved), aggregated by the disjunctive (Dubois–Prade) rule: conflict → vacuity, corroboration → narrowing, never cancellation. It is NOT a renamed scalar confidence: the interval is derived from the evidence decomposition, and the model's self-reported confidence is kept only as a baseline.
* Failure-prediction, selective-verification, controls/ablation and diagnostics analyses over verifier predictions.
* A strict leakage architecture: allowlist-only input builder, data-only deny-list (AST-guarded), gold joins only at the evaluation stage, sentinel/source-scan/import-isolation tests.
* Zero modifications to production verifier code. The surrogate verifier path (`scripts/run_surrogate_verifier.py`) reuses production logic verbatim with a local model, for when no production API credentials are available.

---

## Quick start

```bash
python -m pytest benchmarks/perturbation/pis/tests -q
# see docs/RESULTS.md §12 and the commands below for the full pipeline
python -m benchmarks.perturbation.pis.runner --gold-set data/gold_set.json \
  --task pis --model Qwen/Qwen2.5-7B-Instruct --quantization nf4 \
  --out-dir artifacts/pis_qwen7b
```

---

## Commands (frozen configuration used for the reported results)

* **Evaluator + baselines:** `runner --task {pis,scalar_confidence,binary_logit}`
* **Verifier predictions:** `scripts/make_uid_gold_set.py` (collision-free copy) → repo `run_eval.py --variant after` (production credentials) or `scripts/run_surrogate_verifier.py` (local fallback) → `scripts/convert_predictions.py`
* **Analyses:** `analysis/failure_prediction`, `analysis/selective` (permutation+bootstrap calibration built in), `analysis/controls`, `analysis/diagnostics {audit,forensics}`
* **Cache/resume:** reruns skip completed examples whose cache key (model + resolved revision + quantization + dtype + chat template + prompt version + feature set + input hash) matches.

---

## Known limitations

See `docs/RESULTS.md` §10: small n (22 errors), surrogate verifier scope, LLM-assessed masses, label noise in the gold set, assessor-family confound, heavy width ties.

---

## 4. Proposed PR

**Title:**

[perturbation] Add experimental PIS evidential-uncertainty evaluator and verifier-reliability analysis (Issue #23) — negative result with diagnosis

**Description:**

````markdown
## Summary

Adds a self-contained experimental module under `benchmarks/perturbation/pis/`
that tests, for the perturbation benchmark (Issue #23 — Evaluation / Improve
comment quality), whether a **probabilistic inconsistency interval** can
flag cases where the verifier is unreliable. **No existing file is
modified**; production verifier behavior is untouched.

The research question was pre-registered before any gold-error analysis:
does higher evidential uncertainty (interval width W = U − L) predict
verifier prediction errors? **The answer on the current gold set is no**
— and the contribution reports that honestly, together with a diagnosis
of why, and two verifier/benchmark findings useful to maintainers.

## What is added

- **PIS evaluator** (`pis/`): per perturbation, an evidential interval
  [L, U] ⊆ [0, 1] over the "substantive inconsistency" hypothesis, built
  from an explicit support/against/unresolved evidence decomposition and
  aggregated by the disjunctive (Dubois–Prade) rule — conflict becomes
  vacuity, never cancellation. Distinct from a scalar confidence score by
  construction (the self-reported confidence is kept only as a baseline).
- **Leakage architecture**: allowlist-only input builder; data-only
  gold-field deny-list (AST-guarded); gold labels join predictions only
  inside the evaluation-stage analysis; sentinel + source-scan +
  import-isolation tests. 69 unit/integration tests, all CPU-only.
- **Analyses**: failure prediction (E1), selective verification with
  permutation/bootstrap calibration (E2), controls (confounds,
  leave-one-evidence-source-out, cross-assessor), gold-blind evidence
  audit and post-hoc forensics.
- **Verifier-side tooling**: a collision-free gold-set rewrite script and
  a predictions converter; a local surrogate runner that reuses
  `structural_precheck` / `VERIFIER_PROMPT` / `_parse_verdict` verbatim
  for environments without production API credentials.

## Results (gold set: 89 examples, 22 verifier errors; full report in
`pis/docs/RESULTS.md`)

- **Primary (pre-registered): null.** AUROC(W → verifier error) = 0.502
  (95% CI [0.377, 0.634]; MWU p = 0.98). The whole family of elicited
  uncertainty signals (self-confidence, token probability, ambiguity) is
  at chance. Selective verification on W: no calibrated benefit
  (permutation p = 0.145).
- **Diagnosis (evidence gathered gold-blind, before any error analysis):**
  the elicitation, not the interval algebra, is the weak link. Two
  assessor models produce structurally different evidence decompositions
  (59/89 vs 4/89 mixed-polarity examples; 0% vs 47% saturated items) with
  near-zero width-rank correlation (ρ ≈ 0.05); the stronger assessor
  self-collapses the interval into a point classifier. A useful PIS-style
  signal for this benchmark likely needs grounded mass sources (e.g., the
  repo's own deterministic `structural_precheck` rules, verbatim
  quote-match tests), with LLM elicitation at most for the residual.
- Scope: verifier conclusions are scoped to **production logic with a
  local surrogate model** (no production API credentials were available
  in the compute environment).

## Findings for maintainers (independent of PIS)

1. **`run_eval.py` joins on `perturbation_id` alone, which is not unique
   across papers.** In the current gold set, 4 ids collide, affecting
   10/89 examples (`P000_S0000` ×4 across paper_003/004/009/010;
   `P002_S0025`, `P003_S0049`, `P004_S0001` ×2 each). Colliding examples
   receive a single completion-order-dependent verdict and are scored
   against a single gold label; output rows lack a `paper` field, so the
   conflation cannot be repaired post hoc. Repro:
   `python -c "import json,collections; ex=json.load(open('benchmarks/perturbation/analyses/verifier_eval/gold_set.json'))['examples']; print({k:v for k,v in collections.Counter(e['perturbation_id'] for e in ex).items() if v>1})"`.
   This PR does not change `run_eval.py` (minimal-integration principle);
   `pis/scripts/make_uid_gold_set.py` provides a zero-modification
   workaround, and we'd be happy to send the one-line composite-key fix
   as a separate PR.
2. **LLM JSON outputs with LaTeX spans systematically contain invalid
   backslash escapes** (38% of 7B / 19% of 14B generations in our runs).
   The tracked repair in `pis/parsing.py` (identity on valid JSON,
   unit-tested) recovered 100%.
3. On the surrogate run, the verifier predicted `not-an-error` only 1/89
   times and missed 11/12 gold `not-an-error` examples — worth checking
   the production model's recall on that class.

## Reproduction

`pis/README_PIS.md` (commands) and `pis/docs/RESULTS.md` (§12). Compute:
fits in a Kaggle 2×T4 budget; the PIS side requires no API calls. All
configs, model revisions, gold-set hash, library versions and timings are
recorded in per-run manifests.

## Not claimed

- No superiority claim for PIS over anything: the primary hypothesis
  failed and is reported as such.
- The cross-assessor AUROC of 0.66 for the 14B evaluator is an
  exact-same-checkpoint observation (it shares model+revision with the
  surrogate verifier) and is reported as confounded, not as replication.
- No conclusions about the production Claude verifier's model (only its
  logic was exercised).
````