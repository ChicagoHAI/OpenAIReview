# Perturbation Benchmark

Do AI review systems catch errors deliberately injected into otherwise-good
papers? This benchmark takes real arXiv papers, injects controlled errors, runs
automated reviews, and measures recall (the fraction of injected errors a system
detects).

See the paper for full method and results ([arXiv:2606.19749](https://arxiv.org/abs/2606.19749)). This README covers how to
reproduce a run.

## Pipeline

```
extract → generate → validate → verify → inject → review → score
```

- **extract → generate → validate** (`perturb_automated.py`, the `openaireview perturb` CLI): find candidate spans in a paper, generate candidate errors, and
apply the structural checks, writing a ground-truth manifest per paper.
- **verify** (`analyses/verify_existing.py`): rate each surviving error and drop
the ones that read as typos or do not constitute a real error.
- **inject** (`reinject_existing.py`): apply the kept errors to the clean source,
writing a corrupted paper (`*_recorrupted.md`) plus its filtered manifest
(`*_kept_perturbations.json`). These files are the input to the review stage.
- **review** (`run_benchmark.py`): run each (model, method) over the corrupted paper.
- **score** (`run_benchmark.py`): match each review comment against the manifest
and compute recall.

## Dataset

The recommended way to reproduce the paper is to use the released perturbed
papers, so most users can skip generation entirely. The exact set is published as
a zip archive on
[Google Drive](https://drive.google.com/file/d/10tI0prXCDtyBFv_gdHFlU0i7SWN3zMr3/view?usp=sharing)
(download with `gdown 10tI0prXCDtyBFv_gdHFlU0i7SWN3zMr3`). Each paper
ships as a corrupted markdown file (`*_recorrupted.md`) and a ground-truth
manifest (`*_kept_perturbations.json`), laid out as
`<domain>/all/<paper_id>/<error_type>/`. Unzip it inside `benchmarks/perturbation/`
so it lands at `data/perturbations_filtered/`, then run every domain at once with
the committed per-domain configs (each `full_*.yaml` already points `input_dir` at
its split):

```bash
cd benchmarks/perturbation
# unzip the released archive here first (creates data/perturbations_filtered/)
python run_benchmark.py --configs configs/full_*.yaml --stages prepare,review,score,report
```

For a single domain, pass one config instead, for example
`run_benchmark.py configs/full_math_all.yaml --stages ...`.

The released set was filtered with an LLM verifier (the verify stage below) and
spot-checked by a manual audit (82.5% of a 40-perturbation sample judged valid
errors, see the paper). To build a fresh set of your own instead, follow the
Quick start below. Error generation is model-driven, so a fresh run produces
different papers and errors from the released set.

## Error types

Injected errors span four categories (the underlying error type is in parentheses):

- **Surface** (`surface`): minimal single-token math edits (flip an operator or sign, change a number, alter a subscript).
- **Claim** (`statement_empirical`, `claim_theoretical`): a stated empirical or theoretical claim is made wrong.
- **Reasoning** (`logic`): a logical or derivation step is broken.
- **Experimental** (`experimental`): an experimental-design or setup detail is corrupted.

## Quick start

Install the benchmark dependencies and set an API key:

```bash
uv pip install -e ".[benchmarks]"
export OPENROUTER_API_KEY=...
```

This rebuilds the perturbed papers from scratch. Most users do not need it: the
released set (see Dataset above) is the recommended input. Regenerate only to
make a fresh set. Steps 1-3 build the perturbed papers (the generation pipeline),
steps 4-7 run the benchmark over them. Step 2, verify, is an LLM filter that drops
non-substantive perturbations; it is how the released set was built, and inject
keeps only the perturbations it marks substantive. The verify and inject steps are
package modules, so they run from the repo root (the `(cd ../.. && ...)` subshells
below); the others run from this directory.

```bash
cd benchmarks/perturbation

# 1. extract → generate → validate: sample papers and write a clean copy plus a
#    candidate manifest (_clean.md + _perturbations.json) per paper. Generation
#    is model-driven, so this produces a fresh set each run.
python perturb_automated.py --arxiv-category "math.*" --category theoretical \
    --error-type all --target 10 --min-year 2015 \
    --output-dir data/perturbations/math_all

# 2. verify: rate each candidate error and record verdicts under
#    results/error_verification/.
(cd ../.. && python -m benchmarks.perturbation.analyses.verify_existing)

# 3. inject: apply the kept (substantive) errors to the clean source, writing the
#    corrupted papers (_recorrupted.md) and filtered manifests
#    (_kept_perturbations.json). This is the benchmark input.
(cd ../.. && python -m benchmarks.perturbation.reinject_existing \
    --output-root benchmarks/perturbation/data/perturbations_filtered)

# 4-7. the config's input_dir already points at the injected set
#      (data/perturbations_filtered/math_all/all); run the benchmark stages.
python run_benchmark.py configs/default.yaml --stages prepare   # 4. stage corrupted papers
python run_benchmark.py configs/default.yaml --stages review    # 5. run the reviews
python run_benchmark.py configs/default.yaml --stages score     # 6. score against the manifests
python run_benchmark.py configs/default.yaml --stages report    # 7. aggregate the recall tables
```

Run several stages at once with `--stages prepare,review,score,report`, or sweep
many configs with `--configs configs/*.yaml`. `run_benchmark.py` selects the
review system per config via the `system:` field (`openaireview` | `coarse` |
`reviewer3`). See `systems/README.md` for setting up the external systems. To skip
generation entirely, download the released set (see Dataset above) and point
`input_dir` at it.

## Config schema

```yaml
system: openaireview                        # openaireview | coarse | reviewer3
input_dir: benchmarks/perturbation/data/perturbations_filtered/math_all/all   # injected papers from reinject_existing.py (or the released set)
results_dir: results/default                # staged papers, reviews, scores

models:                                     # backbone models to review with
  - openai/gpt-5.5
  - deepseek/deepseek-v4-flash
methods:                                    # zero_shot | local | progressive
  - zero_shot
  - progressive

score_method: llm                           # llm | fuzzy | semantic
score_model: google/gemini-3-flash-preview  # the llm judge
```

Configs in `configs/` are local except the committed `default.yaml` and the
per-domain `full_*.yaml` set (one per paper domain), which reproduce the paper via
`--configs configs/full_*.yaml`. Copy any of them to define experiment variants.

## Scoring

A comment counts as detecting an injected error when it passes two stages:

1. **Substring match** — the perturbed text approximately covers the comment's
  quote (normalized, 0.75 coverage), so the judge only sees comments pointing at
   the right span.
2. **LLM judge** — Gemini-3 Flash Preview rates whether the comment's explanation
  identifies the same error as the manifest's `why_wrong`, on a 1-5 scale, and a
   rating >= 3 counts as detected.

Recall is the fraction of injected errors detected, reported per (model, method)
and per error category by the `report` stage.

## Results layout

```
<results_dir>/
  perturb/<error_type>/paper_NNN/
    paper_NNN_corrupted.md              # injected paper
    paper_NNN_perturbations.json        # ground-truth manifest
  <model>/<error_type>/<method>/paper_NNN/
    review/*.json                       # review output
    score/<score_method>/*_score.json   # recall scores
```

