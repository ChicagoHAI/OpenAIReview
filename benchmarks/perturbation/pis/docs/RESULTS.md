# PIS Evidential Uncertainty Evaluator — Experimental Report

**Status:** experimental contribution, frozen scope. Primary hypothesis and signal were pre-registered before any gold-error analysis. No metric, threshold, prompt, model, or subset was changed after observing gold-set errors. Implementation changes with potential scientific bearing are listed in §9 with timestamps relative to the analysis.

---

## 1. Research question and pre-registered design

**RQ (Issue #23, Evaluation / Improve comment quality):** Can a PIS-style probabilistic inconsistency signal identify cases where the OpenAIReview perturbation verifier is unreliable?

**Primary hypothesis (fixed in advance):** examples with higher evidential uncertainty — PIS interval width W = U − L, where L = Bel(H) = m(H), U = Pl(H) = 1 − m(¬H), and H = "the perturbed span is a substantive inconsistency" — have a higher probability of verifier prediction error.

**Declared secondary/exploratory at design time (never promoted):** ambiguity min(U, 1−L); self-reported confidence; first-token probability; lexical distance; |length diff|; the 14B evaluator; evidence-source ablations; all stratum breakdowns; the 14B×surrogate pairing.

The PIS interval is a Dempster–Shafer mass assignment over {H, ¬H} aggregated from itemized evidence by the disjunctive (Dubois–Prade) rule: committed witnesses with detection probability c_i = strength_i · reliability_i combine as m(H) = (1−A₊)A₋, m(¬H) = A₊(1−A₋), m(Θ) = A₊A₋ + (1−A₊)(1−A₋), with A± = ∏(1−c_i) per side. Conflict mass goes to Θ (vacuity), never cancels; corroboration narrows the interval multiplicatively; unresolved-polarity items provably cannot change the masses (validated empirically: LOSO on "missing_evidence" reproduces the primary AUROC exactly).

---

## 2. Systems under study and provenance

| Component | Configuration |
|---|---|
| Verifier | production logic, variant "after" (structural_precheck + VERIFIER_PROMPT + _parse_verdict, span=None), executed with a **local surrogate model**: Qwen2.5-14B-Instruct, rev `cf98f3b3`, NF4, fp16, greedy — Path B fallback; no production API credentials were available |
| PIS primary evaluator | Qwen2.5-7B-Instruct, rev `a09a3545`, NF4, fp16, SDPA, chat template, greedy, prompt `pis-v1.0`, features `default-v1` |
| PIS secondary | Qwen2.5-14B-Instruct, rev `cf98f3b3` — **same checkpoint as the surrogate verifier** (see §5.3) |
| Gold set | 89 examples: 47 substantive / 30 typo-shaped / 12 not-an-error; error types 20/23/25/21; 5 no-quote; 12 synthetic not-an-error; sha256 `713ea9ad…` |
| Environment | Python 3.13.15, torch 2.11.0+cu128, transformers 4.46.3, bitsandbytes 0.50.2, numpy 2.1.3, huggingface_hub 0.36.2, Tesla T4 |

**Leakage architecture:** the evaluator accepts only a `VerifierInput` built by an allowlist-only builder (a data-only deny-list module is AST-guarded); gold labels meet predictions exclusively inside `analysis/common.build_rows` at the evaluation stage. Runtime sentinel tests, source scans and import-isolation are enforced by the test suite.

---

## 3. Experiment 1 — verifier failure prediction: NULL RESULT

n = 89 joined rows, 0 exclusions; 22 verifier errors (24.7%).

| Signal (→ error) | AUROC | 95% CI / note |
|---|---|---|
| **PIS width (primary, pre-registered)** | **0.5024** | bootstrap [0.3768, 0.6336]; Mann-Whitney p = 0.977 |
| ambiguity min(U,1−L) | 0.5112 | [0.3862, 0.6406] |
| self-reported confidence | 0.5000 | saturated: 83×1.0, 6×0.0 |
| first-token probability | 0.4182 | null |
| lexical distance | 0.5417 | null |
| abs length diff | 0.5210 | null |

Mean width: incorrect 0.513 vs correct 0.451 — direction consistent with the hypothesis but far below significance; strata disagree in sign (real papers: 0.466 vs 0.448; synthetic: 0.560 vs 0.685 — wrong direction). Binned error rates are non-monotone: [3/25, 8/14, 7/27, 4/23] errors = 12.0%, 57.1%, 25.9%, 17.4%; the middle bin has n = 14 (Wilson CI for its rate ≈ [0.33, 0.79]).

**Interpretation (constraints pre-stated):** with 22 errors, the minimal detectable AUROC at 80% power is ≈ 0.70 (Hanley–McNeil SE at A = 0.5 is 0.071). The supported claim is: *no evidence of signal; moderate signals (≤ 0.63) cannot be ruled out.* The planned interval-vs-scalar comparison is untestable on this data because both families sit at chance.

---

## 4. Experiment 2 — selective verification: no benefit (confirmatory completeness)

Run once, after the pre-registered gate failed, with interpretation rules committed before running: primary signal only; permutation + bootstrap calibration; no threshold selection; no claim-building from E2.

- Always-accept risk: 0.2472. Width-gated AURC: 0.1917. Raw gain: +0.0555.
- Permutation p (one-sided vs the tie-conditional null): 0.145.
- Bootstrap 95% CI for gain: [−0.0090, +0.1043] (crosses zero).
- Risk–coverage curve flat/noisy around the base rate (selective risk 0.244 at coverage 0.51; 0.278 at 0.81 — worse than always-accept).

**Methodological note:** the permutation null mean gain is +0.0098 rather than ≈ base/n ≈ +0.0028 because elicited widths are heavily tied and stable-sort tie-breaking preserves index order within tied groups; the test compares the observed gain against exactly this conditional null, which is the appropriate reference for tied scores.

---

## 5. Controls and ablations

### 5.1 Confounds

Width does not proxy trivial factors: Spearman(W, lexical distance) = 0.060; (W, |Δlen|) = 0.084; (W, n_items) = −0.289 (construction: more committed witnesses → narrower interval).

### 5.2 Evidence-source ablation (LOSO, recomputed from cached items)

context 0.510; error_type_meta 0.519; missing_evidence 0.502 (= primary exactly — unresolved items are semantics-preserving by construction); quote 0.473; span_comparison 0.601. All within noise; no removal creates signal.

### 5.3 Cross-model control — CONFOUNDED; reported as observation only

Spearman(W_7B, W_14B) = 0.057 on the final artifact state (An earlier pre-E1 audit computed 0.045; §9.7 resolves this: the two computations saw different states of one example, paper_001::P005_S0043, whose width differed between the interrupted-session recovery path and the monolithic path. Both values are ≈ 0.05, far inside the null band, SE ≈ 0.11.) The 14B width AUROC of 0.662 is an exact-same-checkpoint observation: the 14B PIS assessor and the surrogate verifier share model, revision, quantization and dtype. It is consistent with same-model self-knowledge, not an independent reliability signal. Moreover ≈ 15 failure-prediction-style comparisons were examined; under a global null, P(max ≥ 0.66) ≈ 0.10–0.16. This number is not evidence for PIS and is not treated as such.

---

## 6. Diagnostics `width_one` classification bug — the committed-evidence check
   was polarity-agnostic, so an example whose only non-zero-commitment items
   were `unresolved`-polarity could be labeled "maximal_conflict" instead of
   "no_committed_evidence" (unresolved items commit no mass by construction).
   Caught by its own unit test before any artifact was regenerated; fixed
   and upgraded to a self-checking three-way classification (vacuity /
   verified both-sides-saturated conflict / inconsistency tripwire). The
   W = 1 breakdown is not cited in any conclusion; canonical numbers are
   those of the regenerated audit artifact, which may differ from the
   earlier inline audit on this sub-count.


---

## 7. Failure forensics (exploratory, post-hoc; no claims built here)

- Failure mass is concentrated: the 12 synthetic not-an-error examples account for 11/22 errors (91.7% within stratum); real papers: 11/77 (14.3%).
- Class collapse: the surrogate predicted "not-an-error" exactly once (1/89) and misclassifies 11/12 gold not-an-error examples (8 → typo-shaped, 3 → substantive). Real-paper errors are mostly substantive→typo-shaped (9) vs typo→substantive (2), consistent with the prompt's tie-breaking rules.
- PIS width does not identify the synthetic hotspot (within-stratum widths: errors 0.560 vs correct 0.685 — wrong direction).
- No-quote stratum (n = 5): the highest widths (mean 0.555, incl. 1.0) and zero verifier errors. The verifier's structural tie-breaking rules make it reliable exactly where evidence is absent, so evidential uncertainty and verifier reliability decorrelate by construction in this stratum — one specific, checkable mechanism contributing to the null.

---

## 8. The diagnostic finding: elicitation, not interval algebra

Two gold-blind audits (run BEFORE any gold-error analysis; scripts shipped in `analysis/diagnostics.py audit`) show the two assessors produce structurally different evidence decompositions:

| Metric | 7B | 14B |
|---|---|---|
| mixed-polarity examples | 59/89 | 4/89 |
| items with strength = reliability = 1.0 | 0/222 | 100/212 |
| median width | 0.578 | 0.0 |
| examples with W = 0 | 0 | 54 (all supports_H) |
| self-confidence ≥ 0.9 | 0% | 53% |

Width rankings are essentially uncorrelated across assessors (ρ ≈ 0.05). The interval aggregation is faithful to what it is given (unit-tested invariants: conflict → vacuity, corroboration → narrowing, zero information → [0,1], full commitment → point). What it is given is assessor-idiosyncratic: under the 14B elicitation the model self-collapses PIS into a point classifier (W = 0 + committed side) — i.e., the "scalar confidence in disguise" failure mode occurs at the elicitation layer, not the interval layer.

**Conclusion (diagnostic):** LLM-elicited evidence masses do not currently provide a model-invariant uncertainty signal for this benchmark. A useful PIS-style signal here needs grounded, checkable mass sources — e.g., deterministic symbolic checks (the repo's own `structural_precheck` rules), verbatim quote-match tests, symbol-binding checks — with LLM elicitation at most for the residual.

---

## 9. Compute and runtime profile

Measured in the clean end-to-end reproduction run (git 5eee8b2, driver 580.178.04, 2× Tesla T4, monolithic execution):

| Run | Model | n | Wall time (s) |
|---|---|---|---|
| PIS primary | Qwen2.5-7B NF4 | 89 | 962.1 |
| scalar baseline | Qwen2.5-7B NF4 | 89 | 83.3 |
| binary logit | Qwen2.5-7B NF4 | 89 | 107.3 |
| PIS secondary | Qwen2.5-14B NF4 | 89 | 2275.1 |
| surrogate verifier | Qwen2.5-14B NF4 | 89 (83 LLM-judged) | 521.9 |

Total ≈ 66 GPU-minutes across the two T4s; ≈ 40 min wall with the parallel schedule (14B on GPU 1 overlapping the GPU-0 chain). Analyses are CPU-seconds. API cost: $0. Every reported number was regenerated bit-identically by this run (27/27 pre-registered checks, zero drift). The PIS side is fully local; Path B was chosen after the production credential check failed (production API path was estimated at ~$1–2, not incurred).

---

## 10. Audit trail of changes with scientific bearing

1. v0.1.1 JSON escape repair — before any gold-error analysis; validated gold-blind; identity-on-valid-JSON is unit-tested. 38% (7B) / 19% (14B) of generations contained invalid LaTeX backslash escapes in JSON; all were repaired with tracking; 0 final failures across the campaign.
2. Resume-semantics fix (re-attempt failed, drop stale) — no scientific effect at freeze (0 failed examples).
3. Step D Path B surrogate — pre-committed fallback after the credential check failed; stamped in every downstream artifact.
4. Same-checkpoint confound in the 14B cross-model arm — discovered post-hoc via revision check; the arm was downgraded to "observation only". A control-design miss on our side, documented here.
5. The 0.045 vs 0.057 Spearman discrepancy (§5.3) — flagged, final value pinned to the final artifact state.
7. Batch-composition nondeterminism — characterized, resolved, reproduced around. One example (paper_001::P005_S0043) generated different greedy evidence depending on batch composition: in-batch attempt-1 (3 items) gives W = 0.68456; a solo re-attempt on the interrupted-session recovery path (2 items) gave W = 0.578. This single difference explains three observations at once: (a) the audit-vs-controls Spearman discrepancy (0.045 vs 0.057); (b) the recovery manifest's width differing from the in-batch value; and (c) which state the reported analyses used — the reported bin sizes ([25, 14, 27, 23]) and real-paper stratum means (ok 0.448 / err 0.466) are arithmetically consistent only with the in-batch value. The clean monolithic reproduction run regenerates that value and every reported number exactly (27/27 checks, zero drift). Under the alternative value the primary AUROC would shift by ≤ 0.015 (worst-case bound 0.045), remaining inside the null band; no conclusion is affected. Practical note for future runs: greedy generation is deterministic given (versions, batch composition); interrupted sessions should resume with matching batch sizes or accept documented per-example variation.

---

## 11. Limitations

1. n = 89, 22 errors: powered only for strong signals (MDD ≈ 0.70 AUROC).
2. Surrogate verifier, not the production Claude model: conclusions are scoped to production logic, not production model.
3. LLM-assessed evidence masses; witness-independence assumption; no surrounding-context / related-passage features were available for this gold set (PIS and verifier ran on the same reduced information set — parity held by construction; the richer batched-verifier setting was not tested).
4. Gold-set label noise, including generator artifacts encoded in labels (runaway span, literal `\n` escapes).
5. Assessor-family confound: PIS primary (7B) and surrogate (14B) are both Qwen2.5 (different checkpoints; cross-assessor ρ ≈ 0.05 mitigates but does not eliminate the concern).
6. Width ties (discrete elicited strengths) make rank statistics coarse and condition the permutation null (§4).
7. Single run per configuration; greedy decoding is deterministic given versions, but a batch-composition-dependent difference was observed and fully characterized (§9.7); the clean monolithic reproduction confirms exact determinism (27/27 checks, zero drift); cache keys freeze completed results.

---

## 12. What would test the hypothesis properly next

*Not a claim — a direction implied by the negative result:*

1. grounded mass sources as in §7;
2. the production verifier once credentials exist;
3. a larger or error-enriched gold set (the current 22 errors bound power);
4. a pre-registered stratified analysis separating the synthetic not-an-error stratum from real papers.

---

## 13. Reproduction

```bash
python -m pytest benchmarks/perturbation/pis/tests -q
# evaluator + baselines (GPU) and surrogate verifier per README_PIS.md
python -m benchmarks.perturbation.pis.analysis.failure_prediction --pis … --predictions … --gold-set … --scalar … --logit … --out …
python -m benchmarks.perturbation.pis.analysis.selective --pis … --predictions … --gold-set … --out …
python -m benchmarks.perturbation.pis.analysis.controls --pis … --predictions … --gold-set … --pis-b … --out …
python -m benchmarks.perturbation.pis.analysis.diagnostics audit --pis 7B=… --pis 14B=… --out …
python -m benchmarks.perturbation.pis.analysis.diagnostics forensics --pis … --predictions … --gold-set … --scalar … --out …
```

A one-click Kaggle notebook (Save & Run All, ~40 min on 2×T4) regenerates the entire pipeline from a clean clone — tests, all runs, all analyses — and checks 27 pre-registered values against this report with zero drift (run provenance: git 5eee8b2, gold-set sha256 713ea9ad…, driver 580.178.04; see run_provenance.json attached to the PR).

All numbers in this report are MEASURED from the artifacts of the frozen runs, except where explicitly marked ESTIMATE.