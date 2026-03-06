## What has been built

### Environment
- Python 3.12. Install with `pip install -e .` (or `pip install .`).
- Dependencies: `openai`, `tiktoken`, `python-dotenv`, `pymupdf`, `python-docx`.
- Dev dependencies (for benchmarks): `beautifulsoup4`, `lxml`. Install with `pip install -e ".[dev]"`.
- API key and model overrides in `.env` (see `.env.example`).

### Package (`src/reviewer/`)
- `__init__.py` — `__version__ = "0.1.0"`.
- `cli.py` — CLI entry point (`openaireview review <file>`, `openaireview serve`).
- `parsers.py` — Document parsers (PDF, DOCX, TEX, TXT/MD) returning `(title, full_text)`.
- `serve.py` — Local HTTP server for review visualization.
- `models.py` — `Comment` (with `paragraph_index`) and `ReviewResult` dataclasses.
- `client.py` — OpenRouter wrapper (loads `.env` automatically via `python-dotenv`).
- `utils.py` — `count_tokens`, `chunk_text`, `parse_comments_from_response`, `locate_comment_in_document`, `assign_paragraph_indices`.
- `method_zero_shot.py` — single-prompt review; chunks paper if > 100K tokens.
- `method_local.py` — deep-checks each chunk with surrounding window context.
- `method_progressive.py` — sequential processing with running summary + consolidation.
- `evaluate.py` — recall/precision/F1 via fuzzy quote similarity, location-based recall, cost estimation.
- `viz/index.html` — Visualization UI (served by `serve.py`).

### CLI Usage
```bash
openaireview review paper.pdf                    # default: progressive method
openaireview review paper.pdf --method zero_shot
openaireview serve --results-dir ./review_results --port 8080
```

### Benchmark data (`benchmarks/`)
- `benchmarks/data/` — Raw HTML pages from refine.ink + parsed `benchmark.jsonl`.
- `benchmarks/scripts/` — Parsing, experiment, and evaluation scripts.
- `benchmarks/run_benchmark.py` — Benchmark runner.
- `benchmarks/REPORT.md` — Experiment results.
- `benchmarks/viz_data/` — Pre-generated viz data for benchmark papers.
- 52 ground-truth comments across 4 papers (43 technical, 9 logical).

### Ground-truth issue taxonomy (from 52 Refine comments)
1. **Mathematical / formula errors** (9.6%): Wrong formulas, sign errors, missing factors, incorrect derivations.
2. **Notation inconsistencies** (11.5%): Symbols used differently than defined, undefined notation introduced without explanation.
3. **Logical / conceptual inconsistencies** (7.7%): Statements that contradict each other or the paper's own framework.
4. **Incorrect cross-references** (only when numbered references exist): E.g. theorem/equation number mismatches.
5. **Insufficient justification / missing proof steps** (15.4%): Compressed or hand-waved proof steps.
6. **Parameter / numerical inconsistencies** (9.6%): Stated values contradict what can be derived elsewhere.
7. **Inconsistency between text and formal definitions** (7.7%): Prose disagrees with math.
8. **Questionable claims / overclaiming** (9.6%): Misleadingly strong or imprecise statements.
9. **Ambiguity / unclear exposition** (7.7%): Could mislead a careful reader.
10. **Sign / direction errors** (5.8%): Wrong sign conventions or reversed inequality directions.
11. **Subscript / index errors** (3.8%): Wrong subscript in a specific term.

### Key findings from experiments
- Recall is low across all methods (4-6%) using similarity-based matching.
- The main issue is the matching metric: models find the correct passages but paraphrase them.
- RAG generates more comments but at lower precision; the filtering step is too permissive.
- Defs-scoped variants (rag_nofilter_defs): avg_loc_recall=0.58, avg_llm_recall=0.19, avg_wide_recall=0.37.
