# OpenReview pilot benchmark — locked evaluation report

**Run:** `generated_at` = `2026-04-23T10:43:02.136255+00:00` (UTC)  
**Committed scorecard:** [`reports/eval_20260423T104302Z.json`](reports/eval_20260423T104302Z.json)  
**History line:** [`eval_history.jsonl`](eval_history.jsonl) (same run; `full_report` points at the committed JSON under `reports/`)

This report summarizes one completed **LLM-as-judge** pass over all **10** ICLR 2025 pilot papers. It is meant to be cited before a PR; raw review outputs stay under `results/` (gitignored).

---

## What was evaluated

| Role | Model | Notes |
|------|--------|--------|
| **Paper review** (predictions) | `claude-opus-4-6` | `openaireview review … --method zero_shot`; method key `zero_shot__claude-opus-4-6` in each `<paper_id>.json`. |
| **Judge** (precision / recall) | `claude-sonnet-4-6` | Same API stack as reviews (`REVIEW_PROVIDER=openai` + gateway). Judge calls use `temperature=0.0`, `max_tokens=8`, YES/NO prompts per `src/reviewer/evaluate_openreview.py`. |

Metrics are **not** comparable to the Refine benchmark in `benchmarks/REPORT.md` (different ground truth: paragraph-anchored Refine comments vs OpenReview review text overlap).

---

## Metric definitions (short)

See **`OPENREVIEW.md`** and **`src/reviewer/evaluate_openreview.py`** for the exact prompts.

- **Precision:** fraction of model comments the judge says overlap **any** substantive critique or question in **pooled** official review text (all reviewers).
- **Recall:** for each official review with non-empty formatted text, the judge says whether **at least one** model comment addresses a substantive issue in **that** review; recall = YES count / number of such reviews.
- **F1:** harmonic mean of precision and recall **per paper**; the table below matches the committed JSON. **Means** in the JSON are unweighted averages across the 10 papers.

---

## Aggregate results (n = 10)

| Mean precision | Mean recall | Mean F1 |
|----------------|-------------|---------|
| 0.377 | 0.745 | 0.464 |

---

## Per-paper results

| `paper_id` | Precision | Recall | F1 | Predictions | Reviews covered / non-empty |
|------------|-----------|--------|-----|-------------|----------------------------|
| 7b2JrzdLhA | 0.500 | 0.750 | 0.600 | 12 | 3 / 4 |
| ajxAJ8GUX4 | 0.250 | 1.000 | 0.400 | 8 | 4 / 4 |
| BC4lIvfSzv | 0.300 | 1.000 | 0.462 | 10 | 4 / 4 |
| BM9qfolt6p | 0.111 | 0.750 | 0.194 | 9 | 3 / 4 |
| d4qMoUSMLT | 0.500 | 0.750 | 0.600 | 8 | 3 / 4 |
| jj7b3p5kLY | 0.500 | 0.600 | 0.545 | 8 | 3 / 5 |
| kOJf7Dklyv | 0.750 | 0.600 | 0.667 | 8 | 3 / 5 |
| M992mjgKzI | 0.000 | 0.000 | 0.000 | 8 | 0 / 4 |
| SFNqrHQTEP | 0.556 | 1.000 | 0.714 | 9 | 4 / 4 |
| XMOaOigOQo | 0.300 | 1.000 | 0.462 | 10 | 3 / 3 |

---

## Interpretation and caveats

1. **LLM judge variance:** A second run with the same inputs can change YES/NO edges; treat means as **point estimates**, not ground truth.
2. **Strict overlap:** The judge is asked for overlap with **substantive** human critiques. Model comments that are mostly notation or internal consistency may score **no** overlap when humans emphasized contribution, novelty, or positioning (see **`M992mjgKzI`**: all NO in this run despite substantive model comments).
3. **Review vs judge model mismatch:** Reviews used **Opus**, judge **Sonnet**; both are valid for an end-to-end pipeline but should be stated in any write-up.
4. **Infrastructure:** Gateway retries (including higher retry count on judge calls in `evaluate_openreview.py` during this workstream) absorbed intermittent 503 / Bedrock errors; long runs are still sensitive to outages.

---

## Reproducing (after PDFs and review JSON exist)

```bash
python benchmarks/openreview_benchmark/scripts/evaluate_openreview_benchmark.py \
  --results-dir benchmarks/openreview_benchmark/results/reviews \
  --save-full-report
```

Copy the new `eval_<UTC>.json` into `reports/` with **repo-relative** `benchmark` and `results_dir` fields if you want another locked row for git. You can then delete the duplicate under `results/` to save space; the committed snapshot lives only in `reports/`.
