# Benchmarks

Reproducibility code for the two studies in the paper:

- **Outcomes study** ([`conference_study/`](conference_study/)) — Does the proposed reviewer produce more (or qualitatively different) comments on rejected vs. accepted conference submissions? Papers are sampled via a 4-pair signal matrix (top-cited vs. never-published, awarded vs. rejected, top vs. bottom review scores, and a composed pair).
- **Perturbation benchmark** ([`perturbation/`](perturbation/)) — Can the proposed reviewer detect *seeded* errors injected into clean papers? Errors span four categories: surface math edits, false claims, faulty reasoning, and experimental-design flaws. Recall is reported per (model, method) cell.

Both share a common setup. Throughout this document, the **system under evaluation** is the proposed reviewer (referred to as a "system" or "method" below); **competitor systems** are external review tools we compare against.

## Setup

```bash
uv pip install -e ".[benchmarks]"
export OPENROUTER_API_KEY=...      # all model calls route through OpenRouter
```

Run scripts from inside each benchmark's directory.

## Outcomes study

Configs that produced the main-text tables: `conference_study/configs/scaleup_progressive.yaml` (proposed system) and `conference_study/configs/coarse_v2.yaml` (competitor). End-to-end:

```bash
cd conference_study

# 1. Build manifests (manifests/v1/{pair_1..4,combined}.json)
python select_papers.py --venues iclr neurips --years 2021 2022

# 2. Download PDFs flat under papers/scaleup/, write pages back into the manifest
python download_papers.py --source snor

# 3. Optional cost preview (estimate = pages × tokens_per_page × method-specific multipliers)
python estimate_cost.py --config configs/scaleup_progressive.yaml

# 4. Run the proposed system and/or competitor systems on the same paper × model grid
python run_study.py       --config configs/scaleup_progressive.yaml
python run_competitors.py --config configs/coarse_v2.yaml

# 5. Aggregate into the tables reported in the paper
python analyses/report_scaleup.py results/scaleup_progressive
```

Both runners are idempotent — rerunning skips (paper × model) combos already complete. Per-paper locks let multiple models share the same result JSON. See [`conference_study/README.md`](conference_study/README.md) for the config schema, concurrency model, and result format.

## Perturbation benchmark

Pipeline: `extract → generate → validate → verify → inject → review → score`. The first five stages produce a *corrupted paper* and a ground-truth manifest of injected errors; the last two stages run the reviewer and score its output. `run_benchmark.py` drives all stages from a single YAML.

```bash
cd perturbation

# One-shot: prepare papers, run reviews, score against the perturbation manifest
python run_benchmark.py configs/default.yaml

# Or run a subset of stages (useful when iterating on scoring or rerunning a single model)
python run_benchmark.py configs/default.yaml --stages prepare,review
python run_benchmark.py configs/default.yaml --stages score

# Multi-config sweep with parallel workers reused across configs
python run_benchmark.py --configs configs/full_*.yaml \
    --parallel-openaireview 2 --parallel-coarse 8

# Aggregate the recall-by-{model,method,error-type,domain} tables in the paper
python generate_report.py results/
```

The `system:` field in each config selects the reviewer under test. Scoring uses a two-stage filter: (1) a fuzzy substring match on the perturbed text against each review comment's quote (after whitespace + math-delimiter normalization, with a 0.75 coverage threshold), then (2) an LLM judge rating (≥3/5) on whether the comment's explanation identifies the same error described in the perturbation's `why_wrong` field. See [`perturbation/README.md`](perturbation/README.md) for the error-type taxonomy, results layout, and known limitations.

## Repository map

```
benchmarks/
├── conference_study/              # outcomes study (§ above)
│   ├── select_papers.py           # build the 4-pair signal-matrix manifest
│   ├── download_papers.py         # fetch PDFs from OpenReview
│   ├── run_study.py               # batch runner, proposed system
│   ├── run_competitors.py         # batch runner, external systems
│   ├── analyses/                  # report-generation scripts
│   └── configs/                   # per-experiment YAMLs
└── perturbation/                  # perturbation benchmark (§ above)
    ├── run_benchmark.py           # single-entry pipeline driver
    ├── extract.py / generate.py / validate.py / verify.py / inject.py
    ├── score.py / generate_report.py
    ├── systems/                   # adapters for the proposed system + competitors
    └── configs/                   # per-experiment YAMLs
```

The reviewer code itself is at the repository root (`src/`), exposed as a Python package and a CLI; both benchmarks invoke it through their adapter layers rather than calling its internals directly.
