# Can LLMs Review Academic Papers? Benchmarking Review Approaches

*March 2026*

Academic peer review is slow, expensive, and inconsistent. A single paper can wait months for feedback from a handful of reviewers, each bringing different expertise and attention. Meanwhile, LLMs can read a 50,000-token paper in seconds and have absorbed more scientific literature than any individual human. So the natural question is: how well can they actually catch mistakes?

This post documents a benchmarking experiment: building an AI paper reviewer and iterating on approaches to maximize recall against Refine comments as ground truth.

---

## The Benchmark

We used four papers from [refine.ink](https://www.refine.ink/examples), each with comments from Refine identifying specific errors. Every comment includes a verbatim quote, a detailed explanation, a confidence score, and a `paragraph_index` that anchors it to a specific location in the document.

| Paper | Field | Comments |
|---|---|---|
| Inference in Molecular Population Genetics | Statistical Genetics | 15 |
| Coset Codes --- Part I | Information Theory | 19 |
| Targeting Interventions in Networks | Economic Theory | 6 |
| Chaotic Balanced State in Cortical Circuits | Neuroscience | 12 |

**52 ground-truth comments total** (43 technical, 9 logical). The papers range from 24K to 50K tokens.

---

## Evaluation Metrics

We use three complementary recall metrics:

1. **Similarity recall** --- fuzzy string matching (threshold 0.35) between predicted and ground-truth quotes. Strict; penalizes paraphrasing. Largely useless for LaTeX-heavy text.
2. **Location recall** --- a ground-truth comment is "recalled" if any prediction falls within a paragraph window (we report +-3 and +-5). Measures whether the model is looking at the right part of the paper.
3. **LLM-judge recall** --- a Haiku judge determines if a predicted and ground-truth comment (within a location window) refer to the same issue. The primary metric. We report both gated (+-3) and wide-gated (+-10) versions.

---

## Methods

All methods use Claude Opus 4.5 as the large model and Claude Haiku 4.5 as the small model, via OpenRouter. All share the same deep-check prompt with 8 issue categories, Refine-style writing instructions, and leniency for introductory/overview sections.

### Zero-shot

Sends the entire paper in a single prompt with instructions to find technical and logical mistakes. Cheapest method but limited by single-pass attention.

### RAG Local

Splits the paper into paragraphs (~140 tokens each), uses Haiku to filter candidates (~40 of ~300), then deep-checks each with +-3 paragraph window context (asymmetric: 5 before, 2 after).

### Progressive

Processes the paper sequentially through ~27 merged passages (~8000 chars each), maintaining a running summary of definitions, equations, theorems, and key claims. For each passage:
1. **Deep-check** (Opus): running summary + window context + passage → find errors
2. **Summary update** (Opus): current summary + passage → updated summary
3. **Post-hoc consolidation**: one final Opus call to deduplicate and merge related issues

The running summary is capped at ~2000 tokens and provides the model with notation context from the entire paper seen so far, without requiring the full text.

We report two versions:
- **Progressive**: after consolidation (fewer, higher-quality comments)
- **Progressive (Full)**: pre-consolidation (all comments found, higher recall but lower precision)

---

## Results

### All methods on all 4 papers

| Method | Comments | Loc Recall | Loc Recall +-5 | LLM Recall | Precision | Cost |
|---|---|---|---|---|---|---|
| Zero-shot | 23 | 17.3% | 23.1% | 0.0% | 0.0% | $1.35 |
| RAG Local | 211 | 48.1% | 50.0% | 15.4% | 4.5% | $3.63 |
| **Progressive** | **68** | **53.8%** | **69.2%** | **25.0%** | **19.1%** | **$16.73** |
| Progressive (Full) | 247 | 82.7% | 86.5% | 44.2% | 9.3% | $15.81 |

### Per-paper breakdown (LLM recall)

| Paper | GT | Zero-shot | RAG Local | Progressive | Progressive (Full) |
|---|---|---|---|---|---|
| inference-molecular | 15 | 0% | 13% | 33% | **67%** |
| coset-codes | 19 | 0% | 16% | 16% | 16% |
| targeting-interventions | 6 | 0% | 17% | 33% | **50%** |
| chaotic-balanced-state | 12 | 0% | 17% | 25% | **58%** |

### Per-paper breakdown (location recall)

| Paper | GT | Zero-shot | RAG Local | Progressive | Progressive (Full) |
|---|---|---|---|---|---|
| inference-molecular | 15 | 7% | 20% | 53% | **93%** |
| coset-codes | 19 | 16% | 63% | 42% | **74%** |
| targeting-interventions | 6 | 17% | 33% | 33% | **50%** |
| chaotic-balanced-state | 12 | 33% | 67% | 83% | **100%** |

---

## Key Findings

### 1. Progressive summaries dramatically improve recall

The progressive method achieves 25% LLM recall (44% pre-consolidation) compared to 15% for RAG Local and 0% for zero-shot. The running summary gives the model access to notation and definitions from the entire paper seen so far, enabling it to catch inconsistencies that span many pages.

### 2. Consolidation trades recall for precision

Post-hoc consolidation reduces comments from 247 to 68 (72% reduction) while only dropping LLM recall from 44% to 25%. Precision improves from 9.3% to 19.1%. The consolidation prompt deduplicates and merges related issues, removing comments that flag standard conventions or the same underlying problem.

### 3. Location recall reveals the true ceiling

The progressive (full) method achieves 83% location recall, meaning the model finds *something* at nearly every ground-truth error location. The gap between 83% location recall and 44% LLM recall is the deep-check quality problem: the model finds issues at the right place but not always the *same* issue as the expert reviewer.

### 4. Zero-shot fails with the uniform prompt

Zero-shot found only 23 comments with 0% LLM recall across all papers. The leniency instructions (designed for the progressive method's per-passage checking) may be too gentle for a single-pass review where the model sees the full paper and has full context.

### 5. Cost scales with depth

| Method | Cost/paper | Comments/paper | Cost/LLM-recalled |
|---|---|---|---|
| Zero-shot | $0.34 | 6 | N/A |
| RAG Local | $0.91 | 53 | $0.45 |
| Progressive | $4.18 | 17 | $1.29 |
| Progressive (Full) | $3.95 | 62 | $0.69 |

The progressive method costs ~4.6x more than RAG Local per paper but finds 1.6x more ground-truth issues (consolidated) or 2.9x more (full). The bulk of the cost is the Opus deep-check calls (27 passages x ~8000 tokens each), plus 27 summary update calls.

### 6. Coset-codes remains difficult

All methods struggle with coset-codes (16% LLM recall even for progressive full). This paper has dense information-theoretic notation and geometric arguments that may require deeper domain expertise than the model can provide from general training.

---

## Evolution of the Approach

### Phase 1: RAG filter experiments

The original RAG pipeline used Haiku to pre-filter paragraphs, selecting ~17% for deep-checking. Analysis showed this was the primary bottleneck: the filter missed many ground-truth error locations. Removing the filter improved coverage but increased cost.

### Phase 2: Definitions prefix

Adding a definitions prefix (keywords: "definition", "denote", "let", "theorem", "assume", plus equation patterns) improved recall on notation-heavy papers. The biggest gain was on targeting-interventions (0% -> 50%) and chaotic-balanced-state (17% -> 42%).

### Phase 3: Progressive approach

Instead of dumping raw definition paragraphs as context, the progressive method maintains a structured running summary updated after each passage. This provides:
- **Structured context**: notation, equations, theorems, assumptions, and claims organized by category
- **Sequential awareness**: the summary reflects only what has been seen so far, matching how a reader encounters the paper
- **Bounded cost**: the summary is capped at ~2000 tokens regardless of paper length

The progressive approach significantly outperforms all RAG variants on recall while producing fewer, higher-quality comments after consolidation.

---

## Recommendations

1. **Use Progressive for maximum recall.** 44% LLM recall (full) or 25% (consolidated) at ~$4/paper, with 83% location coverage.

2. **Use RAG Local for budget-constrained runs.** 15% LLM recall at $0.91/paper --- 4.6x cheaper.

3. **Always report location recall.** It reveals that models engage with the right parts of papers far more often than LLM-judge recall suggests. The gap between location and LLM recall is the key metric for measuring deep-check quality.

4. **Post-consolidation is a precision/recall tradeoff.** If precision matters, use consolidated results (19% precision). If recall matters, use full results (44% LLM recall).

5. **The zero-shot prompt needs separate tuning.** The leniency instructions designed for per-passage checking hurt single-pass review performance.

---

## Seeded-Perturbation Benchmark

The Refine benchmark above measures recall against expert-written comments, but those comments are subjective and the matching heuristic is noisy. As a complementary evaluation, we built a **seeded-perturbation benchmark** with known ground truth: take a clean paper, inject specific errors, and measure exactly what the reviewer catches.

### Setup

**Paper:** Nakamura & Steinsson (2018), "High-Frequency Identification of Monetary Non-Neutrality: The Information Effect," QJE. 48 pages, extracted via Mistral OCR (113K chars of clean markdown with LaTeX math).

**12 injected errors** across 5 categories:

| Category | Count | Examples |
|---|---|---|
| `sign_flip` | 3 | Flipped minus to plus in Euler equation; removed leading negative in habits equation; changed kappa\*omega to kappa/omega in Phillips curve |
| `parameter` | 5 | beta: 0.99->0.95; sigma: 0.5->5; b: 0.9->0.09; phi_pi: 0.01->1.5; labor share: 2/3->1/3 |
| `definition` | 2 | Output gap y_t->c_t; information fraction 1-psi->1+psi |
| `subscript_swap` | 1 | lambda_t^n -> lambda_s^n in marginal utility gap |
| `claim` | 1 | "large and persistent" -> "permanent" effects |

Each error is a targeted text replacement with known ground truth. See `benchmarks/seed_errors.py` for the full specification and `benchmarks/results/error_manifest.json` for the manifest.

### Results: Zero-Shot (Claude Opus 4.6)

| Metric | Value |
|---|---|
| Injected errors | 12 |
| **Detected** | **11 (92%)** |
| Missed | 1 |
| Total comments | 10 |
| False positives | 5 (50%) |
| Prompt tokens | 29,831 |
| Completion tokens | 3,354 |

**By category:**

| Category | Detected / Injected | Recall |
|---|---|---|
| Sign flips | 3/3 | **100%** |
| Parameter errors | 5/5 | **100%** |
| Definition errors | 2/2 | **100%** |
| Subscript swaps | 1/1 | **100%** |
| Overstated claims | 0/1 | 0% |

**Key observations:**

1. **92% recall on injected errors.** The reviewer caught every mathematical and parameter error. It correctly identified sign flips in equations, inconsistent calibration values, and definition mismatches.

2. **The explanations are substantive.** For each detected error, the reviewer didn't just flag the inconsistency but explained *why* it was wrong. For example, on `b=0.09`: "The habit parameter b=0.09 is extremely low compared to values commonly used in the New Keynesian literature. Christiano, Eichenbaum, and Evans (2005) estimate values around 0.65."

3. **The only miss was the claim overstatement** ("persistent" -> "permanent"). This is the hardest category: it requires economic judgment about what constitutes an overstatement, not mathematical consistency checking.

4. **False positives are not all hallucinations.** Of 5 unmatched comments, several flag real issues in the original paper (a standard error discrepancy between text and table, weak stock price evidence). The 50% false positive rate overstates the problem.

5. **Zero-shot works much better here than on Refine.** The Refine benchmark showed 0% LLM recall for zero-shot. The difference: (a) seeded errors are more blatant than Refine's subtle expert comments, and (b) the Mistral OCR output preserves LaTeX math that zero-shot can actually check.

### Running the Benchmark

```bash
# Dry run: inject errors and inspect the perturbed paper
uv run python benchmarks/seed_errors.py --input path/to/clean_paper.md

# Full run with scoring
uv run python benchmarks/seed_errors.py --input path/to/clean_paper.md --review --method zero_shot

# Progressive method
uv run python benchmarks/seed_errors.py --input path/to/clean_paper.md --review --method progressive
```

Output is saved to `benchmarks/results/`:
- `perturbed_paper.md` -- the paper with injected errors
- `error_manifest.json` -- ground truth
- `review_<method>.json` -- raw reviewer output with all comments
- `scores_<method>.json` -- detection scores with per-category breakdown

### Extending to Other Papers

The `ERRORS` list in `seed_errors.py` is paper-specific. To benchmark on a different paper:
1. Extract the paper to clean markdown (e.g., `openaireview extract paper.pdf`)
2. Define new `SeededError` entries targeting that paper's equations and calibration
3. Run the benchmark

Reusable perturbation patterns (sign flips, parameter scaling, subscript swaps) could be automated in future work.

### Limitations

- Single paper: results may not generalize across fields
- Errors are hand-crafted and vary in difficulty (a subtle sign flip vs. an obviously wrong parameter)
- The matching heuristic uses keyword overlap; manual inspection of `review_<method>.json` is recommended

---

## Next Steps

- Tune zero-shot prompt separately (less leniency, since full paper context is available)
- Improve consolidation to preserve more true positives while still deduplicating
- Investigate why coset-codes recall is low across all methods
- Test on a larger set of papers beyond 4 benchmark examples
- Evaluate with different large models (GPT-4o, Gemini) for cost comparison
- Automate reusable perturbation patterns (sign flips, parameter scaling) across papers
- Compare progressive vs. zero-shot on seeded benchmark to measure consolidation loss
