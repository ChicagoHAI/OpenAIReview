# OpenReview benchmark track (pilot)

This track complements the Refine-based benchmark in `benchmarks/data/benchmark.jsonl`. It uses **public OpenReview** threads (reviews, author replies, meta-review, decision) from ML venues. It is **not** paragraph-anchored like Refine; evaluation should use **semantic overlap** (e.g. LLM-as-judge) between model comments and human review text, not paragraph-location metrics.

All OpenReview-specific assets live under **`benchmarks/openreview_benchmark/`** (data, scripts, this doc).

## Pilot scope (ICLR 2025)

The pilot includes **10 papers** from **ICLR 2025**, chosen from a random sample of accepted papers by **longest average** review length (sum of `summary`, `strengths`, `weaknesses`, and `questions` per official review, averaged across reviewers). Papers also had to have **at least three official reviews** and **at least one author reply** in the thread.

| Forum ID | Title |
|----------|--------|
| `jj7b3p5kLY` | The AdEMAMix Optimizer: Better, Faster, Older |
| `kOJf7Dklyv` | Air Quality Prediction with Physics-Guided Dual Neural ODEs in Open Systems |
| `ajxAJ8GUX4` | Learning Geometric Reasoning Networks For Robot Task And Motion Planning |
| `XMOaOigOQo` | ContraDiff: Planning Towards High Return States via Contrastive Learning |
| `SFNqrHQTEP` | NExUME: Adaptive Training and Inference for DNNs under Intermittent Power Environments |
| `BC4lIvfSzv` | Generative Representational Instruction Tuning |
| `M992mjgKzI` | OGBench: Benchmarking Offline Goal-Conditioned RL |
| `BM9qfolt6p` | LucidPPN: Unambiguous Prototypical Parts Network for User-centric Interpretable Computer Vision |
| `7b2JrzdLhA` | Graph Neural Ricci Flow: Evolving Feature from a Curvature Perspective |
| `d4qMoUSMLT` | Efficient Training of Neural Stochastic Differential Equations by Matching Finite Dimensional Distributions |

## Data files

| Path | Description |
|------|-------------|
| `benchmarks/openreview_benchmark/data/openreview_raw/<forum_id>.json` | Raw API response: all notes in the forum (`GET /notes?forum=<id>`). **Gitignored**; produce with `collect_openreview.py` if you need to re-run `normalize_openreview.py`. Not required to run eval (committed JSONL is enough). |
| `benchmarks/openreview_benchmark/data/openreview_benchmark.jsonl` | One JSON object per line: normalized paper metadata, reviews, discussions, meta-review, decision. **Committed**; this is what the eval script reads. |

Optional: `filter_candidates.py` can write a ranked list (e.g. `candidate_papers.json`) while discovering the pilot; that file is **not** required to use the benchmark once `openreview_benchmark.jsonl` exists.

### Locked evaluation artifacts (committed)

| Path | Description |
|------|-------------|
| `benchmarks/openreview_benchmark/reports/` | Frozen full-eval JSON copies for git (`eval_<UTC>.json`); use **repo-relative** `benchmark` / `results_dir` paths inside each file. |
| `benchmarks/openreview_benchmark/REPORT.md` | Human-readable pilot report (tables, caveats, how to reproduce). |

## Scripts

Shared HTTP helpers (Cloudflare session) live in **`benchmarks/openreview_benchmark/scripts/openreview_http.py`** and are imported by the fetch/download scripts below.

| Script | Purpose |
|--------|---------|
| `benchmarks/openreview_benchmark/scripts/collect_openreview.py` | Fetch forums by venue or explicit `--forum-ids`; writes `data/openreview_raw/`. Uses a browser session (visit `openreview.net` first) so API requests are not blocked. |
| `benchmarks/openreview_benchmark/scripts/normalize_openreview.py` | Convert raw forum JSON to `data/openreview_benchmark.jsonl`. |
| `benchmarks/openreview_benchmark/scripts/filter_candidates.py` | List accepted papers for ICLR 2025 + NeurIPS 2025, random sample, rank by review text length; optional pilot discovery. |
| `benchmarks/openreview_benchmark/scripts/validate_openreview_benchmark.py` | Check JSONL schema; optional `--parse-one` downloads the first paper’s PDF and runs `parse_document` (no LLM). Use before a full review run. |
| `benchmarks/openreview_benchmark/scripts/evaluate_openreview_benchmark.py` | LLM-judge **precision / recall / F1**; optional `--save-full-report` / `--output`; appends to `eval_history.jsonl` unless `--no-eval-history`. |
| `benchmarks/openreview_benchmark/scripts/download_openreview_pdfs.py` | Download PDFs for papers in `openreview_benchmark.jsonl` into `data/openreview_pdfs/` (gitignored) for `openaireview review <file.pdf>`. |

## Schema (normalized JSONL)

Each line is one paper. Main fields:

- **Paper:** `paper_id`, `forum_url`, `venue`, `year`, `title`, `authors`, `abstract`, `keywords`, `primary_area`, `pdf_url`, `decision`
- **Reviews:** `reviews[]` — each item has `review_id`, `reviewer`, `rating`, `confidence`, `soundness`, `presentation`, `contribution`, `summary`, `strengths`, `weaknesses`, `questions`
- **Discussion:** `discussions[]` — `comment_id`, `replyto`, `author_type`, `comment` (and optional `reviewer` for reviewer comments)
- **Meta-review:** `meta_review` (object or null)

## Evaluation (implemented)

Module: `src/reviewer/evaluate_openreview.py`. CLI: `benchmarks/openreview_benchmark/scripts/evaluate_openreview_benchmark.py`.

OpenAIReview outputs **discrete comments** (title, quote, explanation). Human ground truth is **official reviews** with separate fields. Scores are **LLM-as-judge** (configurable model, default `gpt-4o-mini` via `OPENREVIEW_JUDGE_MODEL`).

**Precision** (per paper): among model comments, the fraction for which the judge answers **YES** to: “Does this comment overlap **any** substantive critique or question in the **pooled** human review text (all reviewers combined)?”

**Recall** (per paper): for each official review with non-empty text, the judge answers **YES** if **at least one** model comment addresses a substantive issue in **that** review. **Recall** = (number of YES) / (number of non-empty official reviews). Macro-averaged over papers in the CLI summary.

**F1** = harmonic mean of precision and recall per paper; the script prints per-paper and **mean** P/R/F1.

**API keys:** use the same stack as the rest of the package (e.g. `OPENAI_API_KEY` and `REVIEW_PROVIDER=openai` for the judge). Review runs and judge calls can share the provider.

**Get PDFs locally** (the CLI does not fetch OpenReview PDF URLs like arXiv):

```bash
python benchmarks/openreview_benchmark/scripts/download_openreview_pdfs.py
# Writes benchmarks/openreview_benchmark/data/openreview_pdfs/<paper_id>.pdf (gitignored)
```

**Run a review** (keep outputs under this track; `results/` is gitignored except you can commit summaries separately):

```bash
openaireview review benchmarks/openreview_benchmark/data/openreview_pdfs/jj7b3p5kLY.pdf \
  --name jj7b3p5kLY --method zero_shot \
  --output-dir benchmarks/openreview_benchmark/results/reviews
```

**Run evaluation** — `--results-dir` must match where review JSON lives:

```bash
python benchmarks/openreview_benchmark/scripts/evaluate_openreview_benchmark.py \
  --results-dir benchmarks/openreview_benchmark/results/reviews \
  --save-full-report
```

That writes a **timestamped** full report under `benchmarks/openreview_benchmark/results/eval_<UTC>.json` and **appends one line** to **`benchmarks/openreview_benchmark/eval_history.jsonl`** (mean P/R/F1, judge model, paper ids, optional pointer to the full report). Commit `eval_history.jsonl` when you want a paper-trail for a written report; use `--no-eval-history` to skip the append. Use `--output <path.json>` instead of `--save-full-report` if you want a fixed report path.

For a **PR-ready snapshot**, copy that JSON into **`reports/`**, normalize paths to repo-relative strings, and extend **`REPORT.md`** (see the existing locked run there).

Do **not** use paragraph-index metrics from `evaluate.py` as the primary signal for this track unless human spans are aligned to the paper in a future version.

**Next steps (optional):** atomic human bullets; rebuttal–point linkage; cheaper embedding baselines.

## Local-only files (gitignored: `results/`, `data/openreview_pdfs/`, `data/openreview_raw/`)

| Path | Needed for git / PR? | When you can delete |
|------|----------------------|----------------------|
| `data/openreview_raw/<forum_id>.json` | No | Only for **regenerating** `openreview_benchmark.jsonl` via `normalize_openreview.py`. Eval and the committed pilot do **not** need these files on disk. |
| `results/reviews/<paper_id>.json` | No (local LLM outputs) | Never required for the **committed** scorecard; keep if you want to **re-run eval** without paying for reviews again. |
| `results/eval_<UTC>.json` | No | **Redundant** after you copy metrics into `reports/` (same numbers; `reports/` is the committed snapshot). |
| `data/openreview_pdfs/*.pdf` | No | Safe to remove to save disk if you no longer run `openaireview review` locally; download again with `download_openreview_pdfs.py` if needed. |

## Limitations

- OpenReview is **ML/AI-heavy**; diversity is mostly via topic area within venues.
- API access may require the same session pattern as in `collect_openreview.py` (Cloudflare).
- Review quality and length vary by reviewer; the pilot biased toward **longer** average reviews for denser supervision.
