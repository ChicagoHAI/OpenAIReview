# Conference Paper Study: Coarse on Accepted vs Rejected

**Question:** Does [coarse](https://pypi.org/project/coarse-ink/) produce more
comments on rejected papers than on accepted ones, and how does it compare to
openaireview's `progressive` method on the same papers?

Companion to `[baseline.md](baseline.md)`, which runs the same 10 papers and 3
models through openaireview's progressive method.

## Setup

- **Venue:** ICLR 2024 (same 10 papers as baseline.md)
- **Accepted (5):** Outstanding Paper Award winners
- **Rejected (5):** Clear rejections (rating avg 2.5–3.5, ≥3 reviewers, substantive reviews)
- **Models (3, via OpenRouter):** `z-ai/glm-4.6`, `google/gemini-3-flash-preview`, `qwen/qwen3-235b-a22b-2507`
- **System:** [coarse](https://github.com/isitcredible/coarse) (`coarse-ink`), invoked via `coarse.pipeline.review_paper(...)` in its own venv
- **Date:** April 2026

coarse runs a multi-stage pipeline (extraction QA → domain calibration → literature
search → per-section agents → editorial filtering → quote verification). Unlike
progressive, coarse has no separate "raw vs consolidated" pass — its editorial
filter runs in-line and produces a single set of comments. So the tables below
have no shrink column.

## Runs completed

30 combinations planned (10 papers × 3 models); **27 completed successfully, 3 timed
out at the 30-minute ceiling** (all during the full batch run):

- `iclr24-acc-data-selection-theory × qwen3-235b-a22b-2507`
- `iclr24-rej-calibrated-sim-offline-rl × glm-4.6`
- `iclr24-rej-single-source-dg × glm-4.6`

The 3 missing cells skew sample sizes on glm-rejected (n=3 instead of 5) and
qwen-accepted (n=4 instead of 5). Re-running with a 60-minute ceiling should
fill them.

## Results

### Overall: accepted vs rejected


| Group        | N runs | Comments (total) | Comments (avg) |
| ------------ | ------ | ---------------- | -------------- |
| **Accepted** | 14     | 186              | 13.3           |
| **Rejected** | 13     | 169              | 13.0           |


**Finding: coarse produces essentially the same number of comments on accepted
and rejected papers (−2.2% on rejected).** This is in contrast to progressive,
which showed +14% more raw comments and +19% more consolidated comments on
rejected (see [baseline.md](baseline.md)).

### Per-model breakdown


| Group    | Model                  | N   | Comments (total) | Comments (avg) |
| -------- | ---------------------- | --- | ---------------- | -------------- |
| accepted | gemini-3-flash-preview | 5   | 39               | 7.8            |
| accepted | glm-4.6                | 5   | 73               | 14.6           |
| accepted | qwen3-235b-a22b-2507   | 4   | 74               | 18.5           |
| rejected | gemini-3-flash-preview | 5   | 42               | 8.4            |
| rejected | glm-4.6                | 3   | 55               | 18.3           |
| rejected | qwen3-235b-a22b-2507   | 5   | 72               | 14.4           |


**Model-level observations:**

- **gemini-3-flash-preview** is the most conservative (~8 comments per paper)
and shows a weak +7.7% rejected signal (42 vs 39). Progressive flips sign on
gemini (−11.7% raw, −5.6% consolidated) — both systems agree gemini has no
meaningful acc-vs-rej signal, just disagree on which direction the tiny
residual points.
- **glm-4.6** shows the same "rejected > accepted" direction as under
progressive. coarse: +25.3% by avg. Progressive: +57.3% raw, +66.7%
consolidated. The two glm-rejected timeouts make the coarse number the most
uncertain in the table — if those two come in at the rejected median, the
gap widens.
- **qwen3-235b-a22b-2507** reverses direction under coarse (−22.2%). Progressive
is near-flat on qwen (+3.7% raw, −5.7% consolidated). Both systems agree qwen
produces roughly the same count either way; coarse's larger negative may be
sampling noise amplified by the one qwen-accepted timeout.

### Comparison to progressive (all models)


| System                   | Accepted   | Rejected   | Δ   | Δ%     |
| ------------------------ | ---------- | ---------- | --- | ------ |
| progressive raw          | 356 (n=15) | 405 (n=15) | +49 | +13.8% |
| progressive consolidated | 186 (n=15) | 221 (n=15) | +35 | +18.8% |
| coarse                   | 186 (n=14) | 169 (n=13) | −17 | −2.2%  |


Progressive's rejected-skew is in the same direction before and after
consolidation (+14% raw → +19% cons.), so consolidation amplifies the signal
rather than masking it. coarse flips direction — rejected gets fewer total
comments, driven by qwen3 (see per-model table below) and the missing
glm-rejected cells.

### Comparison to progressive (total comments per model)


| Model                  | System            | Accepted  | Rejected  | Δ   |
| ---------------------- | ----------------- | --------- | --------- | --- |
| gemini-3-flash-preview | progressive cons. | 36 (n=5)  | 34 (n=5)  | −2  |
| gemini-3-flash-preview | coarse            | 39 (n=5)  | 42 (n=5)  | +3  |
| glm-4.6                | progressive cons. | 63 (n=5)  | 105 (n=5) | +42 |
| glm-4.6                | coarse            | 73 (n=5)  | 55 (n=3)  | −18 |
| qwen3-235b-a22b-2507   | progressive cons. | 87 (n=5)  | 82 (n=5)  | −5  |
| qwen3-235b-a22b-2507   | coarse            | 74 (n=4)  | 72 (n=5)  | −2  |


- **coarse is in the same ballpark as progressive-consolidated in raw volume**
(~7–18 comments per paper), not the much-higher progressive-raw volume
(15–45). coarse's editorial filter lands it near progressive's
post-consolidation number.
- **Only glm-4.6 under progressive shows a real acc-vs-rej comment-count
signal.** coarse does not reproduce it, and the other two models show no
signal under either system.

### Severity distribution

Coarse tags each comment as critical / major / minor. Distribution is similar
between groups, with a slight shift toward "critical" + "major" on rejected:


| Group    | Critical | Major     | Minor    |
| -------- | -------- | --------- | -------- |
| Accepted | 15 (8%)  | 139 (75%) | 32 (17%) |
| Rejected | 17 (10%) | 130 (77%) | 22 (13%) |


Critical + major combined: 83% (accepted) vs 87% (rejected). Small shift, but
the *direction* is what you'd expect if rejected papers have more severe issues.

Confidence distribution also leans higher on rejected (95% high vs 86% high) —
coarse expresses more certainty about its rejected-paper comments.

### Quote localization

Coarse emits verbatim quotes which openaireview's `locate_comment_in_document`
then maps to paragraph indices. Location success rate:


| Group    | Located       |
| -------- | ------------- |
| Accepted | 180/186 (97%) |
| Rejected | 137/169 (81%) |


Rejected papers have a notably lower localization rate (81% vs 97%).
Hypothesis: rejected papers in this set contain denser math and custom
notation that survive coarse's extraction less cleanly than the well-typeset
accepted papers, so fuzzy-matching the quote back to the paper's paragraphs
fails more often. Worth investigating if location-recall becomes a metric
of interest.

### Cost


| Model     | Accepted   | Rejected   | Total      |
| --------- | ---------- | ---------- | ---------- |
| Gemini    | $7.97      | $7.30      | $15.27     |
| Glm       | $5.51      | $2.99      | $8.50      |
| Qwen3     | $1.26      | $1.66      | $2.92      |
| **Total** | **$14.74** | **$11.95** | **$26.69** |


Cost is an **estimate from coarse's own pre-flight estimator** (`coarse.cost.build_cost_estimate`),
not measured API spend. coarse creates its `LLMClient` internally and doesn't
expose per-call cost after the fact. The coarse batch was ~8.5× more expensive
per run than progressive ($26.69 / 27 runs ≈ $0.99 vs $3.12 / 30 runs ≈ $0.10).
Most of that gap is coarse's multi-agent pipeline (per-section agents, proof
verify, literature search via Perplexity, extraction QA via Gemini vision).

### Runtime


| Model  | Avg per run | Range        |
| ------ | ----------- | ------------ |
| Gemini | 3.3 min     | 1.6–7.1 min  |
| Qwen3  | 10.7 min    | 5.2–17.4 min |
| Glm    | 19.2 min    | 9.8–29.0 min |


Runtimes are in the same order of magnitude as progressive (gemini: 2.8 min,
qwen: 23 min, glm: 27 min). Coarse is slightly faster on glm/qwen and slightly
slower on gemini. The three timeouts were all glm/qwen runs that brushed the
30-minute ceiling.

## Conclusions

1. **coarse does not distinguish accepted from rejected papers by comment
  count.** 13.3 vs 13.0 per paper is flat noise. This contrasts with progressive,
   which showed +14% raw / +19% consolidated on rejected (mostly driven by
   glm-4.6).
2. **glm-4.6's acc-vs-rej signal is model-intrinsic, not system-specific.**
  glm produces more comments on rejected papers under both progressive and
   coarse. gemini and qwen don't — so you'd need a model ensemble, not glm
   alone, to claim the signal is robust.
3. **coarse's editorial filter behaves similarly to progressive's consolidation.**
  Post-filtering comment counts (7–19 per paper) are close to
   progressive-consolidated (7–17 per paper), not progressive-raw (15–45).
4. **Severity distribution leans the right direction** (more critical/major on
  rejected), but the magnitude is small. Severity could be a useful signal
   even when raw count is flat — worth exploring as a separate metric.
5. **coarse is significantly more expensive** (~$1 per paper estimated, vs
  ~$0.10 per paper for progressive). Most of that gap is coarse's additional
   pipeline stages (literature search, extraction QA, per-section agents with
   proof verify).

### Limitations

- **3 timeouts** leave n=3 on glm-rejected and n=4 on qwen-accepted. Retrying with
a 60-minute ceiling is straightforward and would cost ~$2–3.
- **Cost numbers are estimated**, not measured. coarse's LLMClient isn't exposed
by `review_paper`, so actual OpenRouter spend could differ (likely in the
same order of magnitude — the estimator is coarse's own tool for its cost gate).
- **N=5 per group** is too small for statistical significance, same as baseline.
- **Single venue** (ICLR 2024 only) and a specific rejection band (rating 2.5–3.5).
- **coarse was told to route through OpenRouter** for all three models; native
provider routing (e.g. direct Anthropic for Claude) might give slightly
different numbers.

## Reproducibility

```bash
# One-time setup: install coarse-ink in its own venv
python -m venv /data/dangnguyen/openaireview_project/coarse/.venv
/data/dangnguyen/openaireview_project/coarse/.venv/bin/pip install coarse-ink

# Run (reads from same manifest.json + papers/ as baseline)
export OPENROUTER_API_KEY=...
python benchmarks/conference_study/run_competitors.py --config configs/coarse.yaml

# Report
python benchmarks/conference_study/generate_report.py --config configs/coarse.yaml

# Visualize alongside progressive results
openaireview serve --results-dir benchmarks/conference_study/results/coarse
```

Adapter: `[competitors/coarse_adapter.py](../competitors/coarse_adapter.py)`.
Config: `[configs/coarse.yaml](../configs/coarse.yaml)`.
Results: `results/coarse/<slug>.json` (10 files).
Run log: `results/coarse/run_log.jsonl`.