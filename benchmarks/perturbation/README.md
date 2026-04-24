# Perturbation Benchmark (v2)

Benchmark for evaluating how well LLM reviewers detect **seeded errors** in mathematical papers. The pipeline takes real arxiv papers, injects controlled perturbations, runs automated reviews, and measures recall.

## Pipeline

```
extract → generate → validate → verify → inject → review → score
```

1. **Extract** (`extract.py`): Identify candidate math spans (equations, symbols). Each span carries `verifier_related_passages` — passages elsewhere in the paper referencing the same symbols (used downstream by the verifier). Optionally also `related_passages` shown to the generator (`context_mode=related`).
2. **Generate** (`generate.py`): An LLM produces perturbations + a verbatim `contradicts_quote` from the paper that the perturbation contradicts. The prompt teaches the typo-shaped vs substantive-error distinction (`substantive_guidance=on`).
3. **Validate** (`validate.py`): Structural tests 1–4 — original exists, perturbed differs, no span overlap, no garbled output.
4. **Verify** (`verify.py`): Test #5 — a strong-model judge drops `typo-shaped` and `not-an-error` perturbations, keeping only `substantive` ones. See [Verifier](#verifier).
5. **Inject** (`inject.py`): Apply surviving perturbations to produce a corrupted paper.
6. **Review**: Run `openaireview review` on the corrupted paper with each (model, method) combination.
7. **Score** (`score.py`): Compare review comments against the perturbation manifest using fuzzy substring matching + LLM-as-judge.

## Error Types

### Surface errors

Minimal single-token edits to math expressions:

- `operator_or_sign` — flip `+`/`-`, `≤`/`≥`, `∪`/`∩`
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
python benchmarks/perturbation/run_pipeline.py benchmarks/perturbation/configs/default.yaml

# Run only specific stages
python benchmarks/perturbation/run_pipeline.py configs/default.yaml --stages perturb,review
python benchmarks/perturbation/run_pipeline.py configs/default.yaml --stages score
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

# Generator context-provision strategy:
context_mode: window        # none | window | related
context_window: 200
related_passages_max: 5

# Substantive-error verifier (test #5):
verifier_model: anthropic/claude-sonnet-4-6
verifier_reasoning: none    # none | low | medium | high
verifier_max_workers: 8
skip_verifier: false

review_models:
  - google/gemini-3-flash-preview
  - z-ai/glm-4.6

review_methods:
  - zero_shot
  - progressive

results_dir: benchmarks/perturbation/results/short
```

Papers are streamed from the [proof-pile](https://huggingface.co/datasets/hoskinson-center/proof-pile) dataset and binned by word count.

## Verifier

The verifier (`verify.py`, test #5) judges each surviving perturbation as `substantive` / `typo-shaped` / `not-an-error` and drops everything that isn't substantive. Two layers:

1. **Structural pre-check** (deterministic, no LLM): rejects mixed-direction inequality chains, operator salad, runaway spans, literal `\n`/`\t` escape artifacts.
2. **LLM judge**: 3-step prompt (self-coherence / quote specificity / downstream dependence) with explicit tie-breaking rules.

Production setup is `anthropic/claude-sonnet-4-6 @ reasoning=none` — selected after gold-set eval showed `medium` reasoning over-thinks the "almost-always-typo-shaped" rules and underperforms `none` (~3-4 pts on training, ~3.7 pts on held-out). Override per-run via `verifier_model` / `verifier_reasoning` in the config, or with `--skip-verifier` to run only the structural tests 1–4.

### Validating the verifier itself

A hand-labeled gold set (89 training + 83 held-out perturbations) lives at `analyses/verifier_eval/`. Each example carries a verdict (`substantive` / `typo-shaped` / `not-an-error`) and a rationale. Re-run the eval with:

```bash
# Training set (production prompt + structural pre-check)
python -m benchmarks.perturbation.analyses.verifier_eval.run_eval --variant after

# Held-out set
python -m benchmarks.perturbation.analyses.verifier_eval.run_eval --variant after \
    --gold benchmarks/perturbation/analyses/verifier_eval/gold_set_heldout.json \
    --tag heldout

# Compare to legacy prompt (no pre-check, why_wrong included)
python -m benchmarks.perturbation.analyses.verifier_eval.run_eval --variant before
```

Each run writes `analyses/verifier_eval/results/{split}_{variant}.json` with per-example predictions, accuracy, per-class F1, and per-error-type accuracy. Canonical accuracy tables across model/reasoning combinations live in `analyses/verifier_eval/README.md`.

## Analyses

`analyses/` holds A/B comparison scripts that exercise the perturb pipeline under different settings on the same paper set. Each emits raw JSON next to the run artifacts under `<results_dir>/` and a rendered markdown report under `reports/`.

- `compare_context_modes.py` — sweep `none` / `window` / `related` generator context modes. `--modes` flag for subset runs.
- `compare_substantive_guidance.py` — A/B between `substantive_guidance=on` vs `off` in the generator prompt.

```bash
python benchmarks/perturbation/analyses/compare_substantive_guidance.py \
    benchmarks/perturbation/configs/compare_substantive_guidance_10papers.yaml

python benchmarks/perturbation/analyses/compare_context_modes.py \
    benchmarks/perturbation/configs/compare_10papers.yaml --modes window,related
```

`reports/README.md` indexes completed analyses with their key findings.

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
python benchmarks/perturbation/generate_report.py benchmarks/perturbation/results/short
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

- Surface generation now targets 3 error types × 2 per type = 6 perturbations per paper (down from 8 — `symbol_binding` was dropped because bare symbol swaps are structurally typo-shaped). After verifier filtering, typical yield is ~4 substantive perturbations per short paper.
- Fuzzy substring matching can miss catches where the reviewer heavily paraphrases the quoted text.
- `cost_usd` from OpenRouter metadata is unreliable for some models (notably qwen).

