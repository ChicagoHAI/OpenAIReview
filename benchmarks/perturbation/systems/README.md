# System reviewers on the perturbation benchmark

Runs third-party review systems through the same `perturb → review → score`
pipeline as the native `openaireview` benchmark, so results are directly
comparable on identical perturbed corpora.

Each system implements the `System` protocol (`_base.py`); the runner buckets
review jobs by `(model, method)` cell and dispatches via the configured system.

Currently supports:

- **openaireview** (`openaireview.py`) — the native runner; subprocess `openaireview review`.
- **coarse** (`coarse.py`, wraps `coarse_adapter.py` + `coarse_driver.py`) — third-party.
- **reviewer3** (`reviewer3.py`, wraps `reviewer3_adapter.py`) — third-party HTTP API.

Select the system per config via the YAML field `system: openaireview | coarse | reviewer3`.

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
# 1. Estimate cost before launching (no LLM calls; coarse only today)
python benchmarks/perturbation/run_benchmark.py \
    benchmarks/perturbation/configs/coarse_short.yaml --estimate-cost

# 2. Run the full pipeline (prepare → review → score → report)
#    --parallel-coarse N runs N (paper, model) pairs concurrently
python benchmarks/perturbation/run_benchmark.py \
    benchmarks/perturbation/configs/coarse_short.yaml --parallel-coarse 3

# 3. Regenerate the report standalone (single or combined)
python benchmarks/perturbation/generate_report.py \
    benchmarks/perturbation/results_short

python benchmarks/perturbation/generate_report.py \
    benchmarks/perturbation/results_short \
    benchmarks/perturbation/results_medium \
    --out benchmarks/perturbation/reports/combined.md

# Optional: split progressive into consolidated vs pre-consolidation columns
#   (rescores each review JSON twice — costs a handful of LLM-judge calls).
python benchmarks/perturbation/systems/split_rescore_progressive.py \
    --results-dir benchmarks/perturbation/results_short \
    --results-dir benchmarks/perturbation/results_medium
```

### Stages

`--stages` takes any comma-separated subset of `prepare,review,score,report`.
Common patterns:

- `--stages review,score,report` — skip prepare when staging is already done.
- `--stages prepare` — just stage the corrupted papers (fast, no LLM).

### Parallelism

`--parallel-coarse N` runs N (paper, model) pairs concurrently for coarse;
analogous flags exist for the other systems (`--parallel-openaireview`,
`--parallel-reviewer3`). Each coarse process already parallelizes across
paper sections internally, so the outer pool multiplies throughput against
OpenRouter. Guidance:

- N=1 — serial; easy to read logs; slowest.
- N=3 — 3× speedup, reasonable load on OpenRouter.
- N=6+ — may trip rate limits depending on your OpenRouter plan.

Log lines are prefixed with `[<domain>/<paper>/<error>/<model>]` so interleaved
output stays greppable.

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
