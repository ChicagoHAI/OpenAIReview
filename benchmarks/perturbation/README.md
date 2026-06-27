# Perturbation Benchmark (v2)

Benchmark for evaluating how well LLM reviewers detect **seeded errors** in mathematical papers. The pipeline takes real arxiv papers, injects controlled perturbations, runs automated reviews, and measures recall.

## Pipeline

```
extract → generate → validate → inject → review → score
```

1. **Extract** (`extract.py`): Identify candidate math spans (equations, symbols) in the paper.
2. **Generate** (`generate.py`): Use an LLM to create perturbations for each candidate span.
3. **Validate** (`validate.py`): Check that perturbations are valid (original exists, no overlaps, no garbled text).
4. **Inject** (`inject.py`): Apply valid perturbations to produce a corrupted paper.
5. **Review**: Run `openaireview review` on the corrupted paper with each (model, method) combination.
6. **Score** (`score.py`): Compare review comments against the perturbation manifest using fuzzy substring matching + LLM-as-judge.

## Error Types

### Surface errors
Minimal single-token edits to math expressions:
- `operator_or_sign` — flip `+`/`-`, `≤`/`≥`, `∪`/`∩`
- `symbol_binding` — swap a symbol (`α`→`β`)
- `index_or_subscript` — change sub/superscript (`x_i`→`x_{i+1}`)
- `numeric_parameter` — change a number (`0.5`→`0.25`)

### Formal errors
Deeper structural corruptions to definitions, theorems, and proofs:
- `def_wrong`, `thm_wrong_condition`, `thm_wrong_conclusion`, `thm_wrong_scope`
- `proof_wrong_direction`, `proof_missing_case`, `proof_wrong_assumption`, `proof_mismatch`

## Quick Start

```bash
# Install benchmark dependencies
pip install -e ".[benchmarks]"

# Run a single config (prepare → review → score → report)
python benchmarks/perturbation/run_benchmark.py benchmarks/perturbation/configs/default.yaml

# Run only specific stages
python benchmarks/perturbation/run_benchmark.py configs/default.yaml --stages prepare,review
python benchmarks/perturbation/run_benchmark.py configs/default.yaml --stages score

# Run many domains in one process (workers stay busy across config boundaries)
python benchmarks/perturbation/run_benchmark.py --configs configs/full_*.yaml \
    --parallel-openaireview 2 --parallel-coarse 8
```

`run_benchmark.py` selects a review system per config via the `system:` field
(`openaireview` | `coarse` | `reviewer3`); see `systems/README.md` for setup
of the third-party systems.

## Configuration

`run_benchmark.py` now uses the unified runner schema below. It rejects unknown
keys at load time, so older experiment configs in `configs/` that contain
generation-era fields such as `max_papers`, `length`, `error_type`, and
`perturb_model` are retained as historical experiment logs and are not directly
loadable by the current unified runner.

```yaml
system: openaireview        # openaireview | coarse | reviewer3
input_dir: benchmarks/perturbation/results/perturbations
results_dir: benchmarks/perturbation/results
max_tokens: 13000
min_perturbations: 0
score_method: llm           # llm | fuzzy | semantic
score_model: google/gemini-3-flash-preview

models:
  - google/gemini-3-flash-preview
  - z-ai/glm-4.6

methods:                    # required for system: openaireview
  - zero_shot
  - progressive
```

For `--stages score,report`, the configured `input_dir` must already contain
prepared upstream perturbation artifacts named `*_recorrupted.md` and
`*_kept_perturbations.json`, and `results_dir` must already contain matching
review JSONs under the layout shown below. This repository does not currently
check in those prepared/reviewed artifacts, so score/report smoke tests require
local benchmark outputs from an earlier prepare/review run.

## Results Layout

```
<results_dir>/
  config.yaml                                    # resolved config
  perturb/<error_type>/paper_001/
    paper_001.md                                 # original paper
    paper-001_clean.md                           # clean copy
    paper-001_corrupted.md                       # with injected errors
    paper-001_perturbations.json                 # ground-truth manifest
  <model_slug>/<error_type>/<method>/paper_001/
    review/*.json                                # review results
    score/<score_method>/*_score.json             # recall scores
```

## Reports

Experiment reports are in `reports/`. See `reports/surface_3models_short_medium.md` for the first benchmark run (3 cheap models, 10 papers, surface errors).

### Generating report statistics

After a pipeline run completes, use `generate_report.py` to aggregate results across all papers, models, and methods:

```bash
python benchmarks/perturbation/generate_report.py benchmarks/perturbation/results_short
```

This prints markdown tables to stdout covering:
- Configuration summary
- Ground truth counts by length and error type
- Recall by model × method (split by paper length and overall)
- Recall by error type
- Token usage and cost

The output is meant to be reviewed and edited into a final report in `reports/`.

## Scoring

The scorer uses a two-stage filter:
1. **Fuzzy substring match** — checks if the perturbed text appears (approximately) in the review comment's quote, using normalized text coverage with a 0.75 threshold.
2. **LLM-as-judge** — asks a model to rate whether the reviewer's explanation identifies the same error described in the perturbation's `why_wrong` field (score >= 3/5 = match).

## Known Limitations

- The perturb stage targets `n_per_error=2` perturbations per error type (8 total per paper), but the LLM often reuses the same candidate span for both, causing the validator to reject the duplicate. Typical yield is ~4-5 per paper.
- Fuzzy substring matching can miss catches where the reviewer heavily paraphrases the quoted text.
- `cost_usd` from OpenRouter metadata is unreliable for some models (notably qwen).
