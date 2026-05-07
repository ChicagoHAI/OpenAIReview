# Perturbation Benchmark Report

## Configuration

| Setting | Value |
|---------|-------|
| Papers | ? |
| Length | ? |
| Error type | ? |
| Perturb model | ? |
| Score method | ? |
| Score model | ? |
| Review models |  |
| Review methods |  |

## Ground Truth Summary

**6 papers**, 105 perturbations total:
  - causal_reversed: 29
  - misinterp: 45
  - p_hacking: 31

## Overall recall — per method (aggregated over models, papers, lengths)

| method | n_injected | n_detected | recall |
|--------|-----------:|-----------:|-------:|
| progressive | 105 | 5 | 4.8% |

## Recall — per model × method

| model | progressive |
|-------|------|
| claude-opus-4-6 | 4.8% (5/105) |

## Recall — per error type × method (aggregated across models and lengths)

| method | causal_reversed | misinterp | p_hacking | overall |
|--------|--------|--------|--------|---------|
| progressive | 1/29 (3.4%) | 3/45 (6.7%) | 1/31 (3.2%) | 5/105 (4.8%) |

## Recall by Error Type — per (model, method)

| model | method | causal_reversed | misinterp | p_hacking | overall |
|-------|--------|--------|--------|--------|---------|
| claude-opus-4-6 | progressive | 1/29 (3.4%) | 3/45 (6.7%) | 1/31 (3.2%) | 5/105 (4.8%) |

## Token Usage and Cost

| model | cells | prompt tokens | completion tokens | cost (USD) |
|-------|-------|---------------|-------------------|------------|
| claude-opus-4-6 | 6 | 0 | 0 | $0.0000 |
| **total** | **6** | **0** | **0** | **$0.0000** |

