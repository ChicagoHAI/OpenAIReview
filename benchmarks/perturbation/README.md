# Perturbation Benchmark

Do AI review systems catch errors deliberately injected into otherwise-good
papers? This benchmark takes real arXiv papers, injects controlled errors, runs
automated reviews, and measures recall (the fraction of injected errors a system
detects).

The paper has the full method and results
([arXiv:2606.19749](https://arxiv.org/abs/2606.19749)). This README covers how to
reproduce a run.

## Pipeline

```
extract → generate → validate → verify → inject → review → score
```

- **extract → generate → validate → verify → inject** (the `openaireview perturb`
  CLI, driven by `perturb_automated.py`): find candidate spans in a paper,
  generate candidate errors, validate and verify them, and inject the kept ones
  to produce a corrupted paper plus a ground-truth manifest.
- **review** (`run_benchmark.py`): run each (model, method) over the corrupted paper.
- **score** (`run_benchmark.py`): match each review comment against the manifest
  and compute recall.

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
cd benchmarks/perturbation
```

Run the pipeline one stage at a time:

```bash
# 1. Sample papers from arXiv and generate perturbations (extract→...→inject).
#    Writes corrupted papers + manifests under results/perturbations/<category>/<error_type>/.
python perturb_automated.py --arxiv-category "math.*" --category theoretical \
    --error-type all --target 10 --min-year 2015

# Point the config's input_dir at step 1's output, then run the benchmark stages:
python run_benchmark.py configs/default.yaml --stages prepare   # 2. stage corrupted papers
python run_benchmark.py configs/default.yaml --stages review    # 3. run the reviews
python run_benchmark.py configs/default.yaml --stages score     # 4. score against the manifests
python run_benchmark.py configs/default.yaml --stages report    # 5. aggregate the recall tables
```

Run several stages at once with `--stages prepare,review,score,report`, or sweep
many configs with `--configs configs/*.yaml`. `run_benchmark.py` selects the
review system per config via the `system:` field (`openaireview` | `coarse` |
`reviewer3`). See `systems/README.md` for setting up the external systems.

## Config schema

```yaml
system: openaireview                        # openaireview | coarse | reviewer3
input_dir: results/perturbations/math_all   # corrupted papers from perturb_automated.py
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

Configs in `configs/` are local except the committed `default.yaml`. Copy it to
define experiment variants.

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

## Known limitations

- The generator often reuses the same candidate span for multiple errors, and the
  validator rejects the duplicates, so typical yield is ~4-5 perturbations per paper.
- The substring match can miss detections where the reviewer heavily paraphrases
  the quoted text.
- `cost_usd` from OpenRouter metadata is unreliable for some models.
