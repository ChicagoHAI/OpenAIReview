# Competitor reviewers on the perturbation benchmark

Runs third-party review systems through the same `perturb → review → score`
pipeline as the native `openaireview` benchmark, so results are directly
comparable on identical perturbed corpora.

Currently supports:

- **coarse** — adapter at `coarse_adapter.py`, driver at `coarse_driver.py`.

## Setup (one-time)

```bash
# 1. Clone and build the coarse repo somewhere on disk.
git clone <coarse-repo-url> /path/to/coarse
cd /path/to/coarse
uv sync

# 2. Tell the adapter where to find coarse's venv. Either:
export COARSE_PATH=/path/to/coarse        # adapter uses $COARSE_PATH/.venv/bin/python
# or, for an explicit binary path:
export COARSE_PYTHON=/path/to/coarse/.venv/bin/python

# 3. Set OPENROUTER_API_KEY (coarse uses OpenRouter):
export OPENROUTER_API_KEY=sk-or-v1-...
# or put it in /path/to/coarse/.env
```

The adapter invokes coarse's venv python directly, so no further install
into the openaireview env is required.

## Running

```bash
# 1. Estimate cost before launching (no LLM calls made)
python benchmarks/perturbation/run_competitor_benchmark.py \
    benchmarks/perturbation/configs/coarse_short.yaml --estimate-cost
python benchmarks/perturbation/run_competitor_benchmark.py \
    benchmarks/perturbation/configs/coarse_medium.yaml --estimate-cost

# 2. Run the full pipeline (perturb → review → score → report)
#    --parallel N runs N (paper, model) pairs concurrently
python benchmarks/perturbation/run_competitor_benchmark.py \
    benchmarks/perturbation/configs/coarse_short.yaml --parallel 3
python benchmarks/perturbation/run_competitor_benchmark.py \
    benchmarks/perturbation/configs/coarse_medium.yaml --parallel 3

# 3. Regenerate the report standalone (single or combined)
python benchmarks/perturbation/generate_report.py \
    benchmarks/perturbation/results/short

python benchmarks/perturbation/generate_report.py \
    benchmarks/perturbation/results/short \
    benchmarks/perturbation/results/medium \
    --out benchmarks/perturbation/reports/combined.md

# Optional: split progressive into consolidated vs pre-consolidation columns
#   (rescores each review JSON twice — costs a handful of LLM-judge calls).
python benchmarks/perturbation/competitors/split_rescore_progressive.py \
    --results-dir benchmarks/perturbation/results/short \
    --results-dir benchmarks/perturbation/results/medium
```

### Stages

`--stages` takes any comma-separated subset of `perturb,review,score,report`.
Common patterns:

- `--stages review,score,report` — skip perturb when artifacts already exist.
- `--stages perturb` — just materialize the corrupted papers (fast, cheap).

### Parallelism

`--parallel N` flattens all (paper × model) pairs and dispatches up to N
concurrently. Each coarse process already parallelizes across paper sections
internally, so the outer pool multiplies throughput against OpenRouter.
Guidance:

- N=1 — serial; easy to read logs; slowest.
- N=3 — 3× speedup, reasonable load on OpenRouter.
- N=6+ — may trip rate limits depending on your OpenRouter plan.

Log lines are prefixed with `[coarse/<model_slug>/paper_NNN]` so interleaved
output stays greppable. A heartbeat prints every 30 s per job.

## Output layout

Both coarse and openaireview results can coexist in the same `results_dir`:

```
results_short/
  perturb/surface/paper_00N/paper_00N{,_corrupted}.md, *_perturbations.json
  gemini-3-flash-preview/surface/
    coarse/paper_00N/review/*.json        # coarse
    coarse/paper_00N/score/llm/*.json
    zero_shot/paper_00N/...               # openaireview (existing)
    progressive/paper_00N/...
  qwen3-235b-a22b-2507/surface/coarse/paper_00N/...
  glm-4.6/surface/coarse/paper_00N/...
reports/coarse_competitor_results_short_<timestamp>.md    # auto-generated
```

Reports live one level up from `results_*` so accidental cleanup of a results
dir doesn't wipe the summary.

## Cost estimate

`--estimate-cost` calls `coarse.cost.build_cost_estimate` (same function
coarse uses for its interactive pre-flight gate) on each (paper, model) pair
with no LLM calls. Output:

```
Cost estimate — configs/coarse_short.yaml
paper            words                gemini-3-flash    qwen3-235b   glm-4.6
paper_001        4,823                $0.18             $0.09        $0.31
...
TOTAL                                 $0.95             $0.47        $1.58
Config total: $3.00   (1.3× buffer: $3.90)
```

Also persisted to `<results_dir>/coarse_cost_estimate_<config>.json`.

## Notes

- Actual per-review cost isn't currently captured in output JSON (coarse's
  `LLMClient.cost_usd` lives inside `review_paper()` and isn't exposed on
  the return). The report relies on the pre-flight estimate for cost
  columns. If you need exact costs, pipe coarse's own logs separately.
- `score_method: llm` is the only option that uses LLM-as-judge; it costs
  extra per run. Use `fuzzy` or `semantic` if you want a pure-local score.
- coarse is slow (~3–10 min/paper). Use `--parallel` liberally.
