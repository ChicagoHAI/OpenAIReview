# Conference Study: Accepted vs Rejected

**Research question:** Does OpenAIReview's progressive method produce more (or
different) comments on rejected papers than on accepted ones?

**Venue:** ICLR 2024. The only major ML venue where rejected submissions are
publicly available on OpenReview. NeurIPS, ICML, CVPR etc. hide rejected
papers, so this study can't easily port to them.

## Directory layout

```
configs/           # YAML run configs (one per experiment)
reports/           # Markdown write-ups (one per experiment)
results/           # Output JSONs + run_log.jsonl (gitignored)
papers/            # Downloaded PDFs (gitignored; regenerate via download_papers.py)
  accepted/        # 5 ICLR 2024 Outstanding Paper Award winners
  rejected/        # 5 substantive rejections (ratings 2.5–3.5, ≥3 reviewers)
download_papers.py  # Fetches PDFs + writes manifest.json
estimate_cost.py    # Pre-run USD cost estimate (progressive method)
run_study.py        # Batch runner (multi-model, multi-paper)
generate_report.py  # Computes summary tables from result JSONs
manifest.json       # Curated paper list (forum IDs, titles, groups)
```

One experiment = `configs/<name>.yaml` + `reports/<name>.md` +
`results/<name>/`. The triad shares a name.

## Workflow

### 1. Download papers (one-time)

PDFs are gitignored. Download them before the first run:

```bash
python download_papers.py
```

If `manifest.json` exists, the script downloads the exact papers listed
there, skipping any already on disk. The manifest is never modified.

**Adding more papers** to an existing manifest:

```bash
python download_papers.py --add -n 5                         # 5 more per group (papercopilot)
python download_papers.py --add -n 3 --group rejected        # 3 more rejected only
```

**Bootstrapping a new study** (no manifest yet):

```bash
python download_papers.py -n 10                              # papercopilot, ICLR 2024
python download_papers.py --source hf --venue ICLR --year 2023 -n 10   # HuggingFace
python download_papers.py --source hf --venue NeurIPS --year 2022 -n 10
```

Two data sources via `--source`:

- **papercopilot** (default): ICLR only, uses explicit accept/reject decisions.
- **hf**: [AlgorithmicResearchGroup/openreview-papers-with-reviews](https://huggingface.co/datasets/AlgorithmicResearchGroup/openreview-papers-with-reviews)
  on HuggingFace. Multi-venue (ICLR, NeurIPS, CoRL, UAI, MIDL), selects
  by review score thresholds (`--accepted-threshold`, `--rejected-threshold`)
  since the dataset has no explicit decisions.

### 2. Estimate cost before a run

```bash
python estimate_cost.py
```

Uses observed progressive-method token multipliers (~6× input for the chain
of running-summary + window replay, ~0.15× output). Sanity-check before
burning API credits.

### 3. Run an experiment

```bash
export OPENROUTER_API_KEY=...
python run_study.py --config configs/baseline.yaml
```

Writes results to `results/<name>/<paper-slug>.json` and a run log to
`results/<name>/run_log.jsonl`. Idempotent — rerunning skips paper/model
combos already complete.

**Useful flags:**

- `--dry-run` — print the commands without calling the API.
- `--paper <slug>` / `--model <name>` — restrict to one paper or model.
- `--force` — re-run even if already complete.
- `--max-pages` / `--max-tokens` / `--timeout-sec` / `--max-per-model` — ad-hoc
overrides of any YAML value.

### 4. Generate report tables

```bash
python generate_report.py --config configs/baseline.yaml
python generate_report.py --config configs/baseline.yaml --papers  # include papers table (parses PDFs, slow)
```

Prints markdown tables (overall, per-model, consolidation, cost, runtime)
to stdout. Pipe to a file or paste into `reports/<name>.md`.

### 5. Add a new experiment

```bash
cp configs/baseline.yaml configs/my_experiment.yaml
# edit name, caps, parallelism as needed
python run_study.py --config configs/my_experiment.yaml
python generate_report.py --config configs/my_experiment.yaml
# write up findings in reports/my_experiment.md
```

## Config schema

```yaml
name: baseline         # Results -> results/<name>/
max_pages: 20          # Passed to openaireview CLI
max_tokens: 20000      # Passed to openaireview CLI
timeout_sec: 3600      # Per-subprocess timeout
max_per_model: 2       # Concurrent runs per model
```

Precedence: **CLI flag > YAML value > built-in default**. CLI flag names
mirror YAML keys (hyphens for underscores).

## Concurrency model

Each model gets its own queue + `max_per_model` worker threads — keeps
OpenRouter per-model rate limits isolated. Per-paper locks prevent two
models from clobbering the same result JSON during the CLI's
read-modify-write merge. Total in-flight = `max_per_model × num_models`
(default 6 for 3 models).

## Results format

Each `results/<name>/<slug>.json` contains:

- `progressive__<model_short>` — comments after the consolidation pass.
- `progressive_original__<model_short>` — raw comments before consolidation.

Both are written in a single CLI invocation. `run_study.py` considers a
(paper, model) combo "done" only when both keys exist.