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

# Run the default config (2 short papers, 1 model, all methods)
python benchmarks/perturbation2/run_pipeline.py benchmarks/perturbation2/configs/default.yaml

# Run only specific stages
python benchmarks/perturbation2/run_pipeline.py configs/default.yaml --stages perturb,review
python benchmarks/perturbation2/run_pipeline.py configs/default.yaml --stages score
```

## Configuration

Configs are YAML files in `configs/`. Copy `default.yaml` and edit to create experiment variants. Committed configs serve as the experiment log.

```yaml
max_papers: 5
length: short              # short (2k-7k words) | medium (7k-17k) | long (>17k)
error_type: surface         # surface | formal | all
score_method: llm           # llm | fuzzy | semantic

perturb_model: google/gemini-3-flash-preview
score_model:   google/gemini-3-flash-preview

review_models:
  - google/gemini-3-flash-preview
  - z-ai/glm-4.6

review_methods:
  - zero_shot
  - progressive

results_dir: benchmarks/perturbation2/results
```

Papers are streamed from the [proof-pile](https://huggingface.co/datasets/hoskinson-center/proof-pile) dataset and binned by word count.

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

## Scoring

The scorer uses a two-stage filter:
1. **Fuzzy substring match** — checks if the perturbed text appears (approximately) in the review comment's quote, using normalized text coverage with a 0.75 threshold.
2. **LLM-as-judge** — asks a model to rate whether the reviewer's explanation identifies the same error described in the perturbation's `why_wrong` field (score >= 3/5 = match).

## Known Limitations

- The perturb stage targets `n_per_error=2` perturbations per error type (8 total per paper), but the LLM often reuses the same candidate span for both, causing the validator to reject the duplicate. Typical yield is ~4-5 per paper.
- Fuzzy substring matching can miss catches where the reviewer heavily paraphrases the quoted text.
- `cost_usd` from OpenRouter metadata is unreliable for some models (notably qwen).
