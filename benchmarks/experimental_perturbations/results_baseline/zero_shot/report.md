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
| zero_shot | 105 | 13 | 12.4% |

## Recall — per model × method

| model | zero_shot |
|-------|------|
| claude-opus-4-6 | 12.4% (13/105) |

## Recall — per error type × method (aggregated across models and lengths)

| method | causal_reversed | misinterp | p_hacking | overall |
|--------|--------|--------|--------|---------|
| zero_shot | 2/29 (6.9%) | 9/45 (20.0%) | 2/31 (6.5%) | 13/105 (12.4%) |

## Recall by Error Type — per (model, method)

| model | method | causal_reversed | misinterp | p_hacking | overall |
|-------|--------|--------|--------|--------|---------|
| claude-opus-4-6 | zero_shot | 2/29 (6.9%) | 9/45 (20.0%) | 2/31 (6.5%) | 13/105 (12.4%) |

## Token Usage and Cost

| model | cells | prompt tokens | completion tokens | cost (USD) |
|-------|-------|---------------|-------------------|------------|
| claude-opus-4-6 | 6 | 0 | 0 | $0.0000 |
| **total** | **6** | **0** | **0** | **$0.0000** |

