# Quality-Proxy Study

Do AI review systems comment more on weaker papers than on stronger ones?
This study tests whether comment volume tracks paper quality on real
ICLR/NeurIPS papers. Paper quality has no gold-standard label, so we split
papers into high- and low-quality groups using four noisy **quality proxies**
built from citation, award, and review-score signals, and check whether each
system produces more comments on the low-quality group.

The paper has the full method, metric, and results
([arXiv:2606.19749](https://arxiv.org/abs/2606.19749), Section "AI Review
Systems Correlate with Human Quality Signals"). This README covers how to
reproduce the runs.

## The four quality proxies

Each proxy splits papers into a high-quality and a low-quality group of 30,
drawn from ICLR/NeurIPS 2021-2022 papers with at least three reviews and a
non-null average score:

- **Community-level**: top 30 by citations-per-year vs 30 rejected papers never published elsewhere.
- **Conference-level**: 30 papers highlighted by the venue (Outstanding, Best, Oral, Spotlight) vs 30 rejected papers.
- **Reviewer-level**: top 30 by mean review score vs bottom 30.
- **Composite**: top 30 awarded papers by combined citation-and-score rank vs bottom 30 rejected, never-published papers by review score.

That gives 60 papers per proxy and 240 in total (197 unique, since some papers
satisfy more than one criterion). Frontier models too expensive to run on the
full set use a **frontier subset** of 74 unique papers, which the paper mainly
reports on.

Citations, awards, and review scores are noisy proxies of quality. We pick the
top and bottom groups as a tractable approximation, not as ground-truth quality.

## Reproducing the paper set

Selection draws from SNOR ([Zenodo 15866613](https://zenodo.org/records/15866613)),
which links OpenReview submissions to Semantic Scholar citation counts,
decisions, and reviewer scores.

**Full set (197 papers)** regenerates from code:

```bash
cd conference_study
python select_papers.py        # downloads SNOR (~448 MB, cached), writes manifests/canonical/
```

Selection is deterministic (fixed seed, forum-id tiebreak), so this reproduces
the exact 197-paper set used in the paper.

**Frontier subset (74 papers)** is a fixed subsample of the full set with no
regeneration script, so it is not shipped here. The pipeline runs end to end on
the full set with the repo code; to reproduce the paper's frontier-subset
numbers, contact the authors for `manifests/canonical/frontier.json`.

## Run flow

```bash
cd conference_study
export OPENROUTER_API_KEY=...      # all model calls route through OpenRouter

# 1. Build the full paper manifest.
python select_papers.py

# 2. Download the PDFs listed in a manifest. Add --limit 5 for a cheap end-to-end smoke test first.
python download_papers.py --source snor --manifest manifests/canonical/full.json

# 3. Preview the API cost before the full run. estimate_cost.py prints a per-model
#    breakdown; the full efficient set costs ~$25-50.
python estimate_cost.py --config configs/baseline.yaml

# 4. Run the systems on the same paper x model grid.
python run_study.py       --config configs/baseline.yaml      # our system, efficient models, full set
python run_competitors.py --config configs/coarse.yaml        # coarse, in its own venv (see "Running coarse")

# 5. Build the paper's tables (pairwise accuracy + 95% CIs) from the results.
#    Pass several configs to compare systems in one set of tables.
python analyses/generate_report.py --config configs/baseline.yaml configs/coarse.yaml
```

Start with the `--limit 5` smoke run in step 2 plus one model to confirm the
pipeline end to end for a few cents before launching the full set. Both runners
are idempotent: rerunning skips (paper, model) combos already complete.

To reproduce the paper's frontier-subset numbers (all six models, including the
two frontier ones), obtain `manifests/canonical/frontier.json` from the authors,
then run steps 4 and 5 with `configs/frontier.yaml` in place of `baseline.yaml`.

## Running coarse

`coarse` (PyPI `coarse-ink`) has a large, version-sensitive dependency set, so
it runs in its own virtual environment and the adapter subprocess-calls into it.
Set it up once:

```bash
uv venv /path/to/coarse-venv
uv pip install --python /path/to/coarse-venv coarse-ink
export COARSE_VENV_PYTHON=/path/to/coarse-venv/bin/python
```

`run_competitors.py --config configs/coarse.yaml` finds the venv through
`COARSE_VENV_PYTHON` (or a `venv_python:` field in the config). coarse runs on
the same paper x model grid, and its output merges into the same result schema
as the other systems.

## Metric

For each (system, model, proxy) we compare mean comments on the high- and
low-quality groups and report **pairwise accuracy**: the fraction of (low,
high) paper pairs where the low-quality paper received more comments (ties
count 0.5). A value of 0.5 means no separation, and above 0.5 means the system
tracks the proxy direction. Confidence intervals come from a cluster bootstrap
over papers (`analyses/ci_auc.py`); see the paper's appendix for the
construction.

## Config schema

```yaml
name: baseline                                 # results -> results/<name>/
manifest: manifests/canonical/full.json    # paper set to run on
models:                                        # backbone models (falls back to the manifest's list if omitted)
  - deepseek/deepseek-v4-flash
  - qwen/qwen3.6-35b-a3b
max_pages: 20                                   # passed to the openaireview CLI
max_tokens: 20000                               # passed to the openaireview CLI
timeout_sec: 3600                               # per-subprocess timeout
max_per_model: 2                                # concurrent runs per model
```

## Directory layout

```
configs/            # run configs (baseline = full set, frontier = 74-subset, coarse = external system)
manifests/          # paper set (canonical/full.json regenerates via select_papers.py)
papers/             # downloaded PDFs (gitignored; regenerate via download_papers.py)
results/            # output JSONs + run_log.jsonl (gitignored)
competitors/        # adapters for external review systems
analyses/           # report + AUC + confidence-interval scripts
select_papers.py    # build the canonical manifest from SNOR
download_papers.py  # fetch PDFs listed in a manifest
run_study.py        # batch runner for our system
run_competitors.py  # batch runner for external review systems
```

## Output structure

Each run config writes to its own results directory:

```
results/<name>/
  <paper-slug>.json     # one file per paper, with every model and system merged in
  run_log.jsonl         # one line per (paper, model) run: timing, exit code, output tails
```

Each `<paper-slug>.json` holds the paper identity (`slug`, `title`), the parsed
`paragraphs` the systems reviewed, and a `methods` dict keyed by
`<system>__<model_short>`:

```
methods:
  progressive__<model>           # OpenAIReview comments after consolidation
  progressive_original__<model>  # OpenAIReview comments before consolidation
  coarse__<model>                # one key per external system run
```

Each method entry has `label`, `model`, `overall_feedback`, `cost_usd`,  
`prompt_tokens`, `completion_tokens`, and a `comments` list. Each comment has a  
`title`, `quote`, `explanation`, `paragraph_index`, and `severity`.