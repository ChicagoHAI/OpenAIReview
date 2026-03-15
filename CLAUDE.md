## What has been built

### Environment
- Python 3.12. Install with `pip install -e .` (or `pip install .`).
- Dependencies: `openai`, `tiktoken`, `python-dotenv`, `pymupdf`, `pymupdf4llm`, `pymupdf-layout`, `python-docx`, `beautifulsoup4`, `lxml`, `mistralai` (for OCR).
- Dev dependencies (for benchmarks): `pytest`. Install with `pip install -e ".[dev]"`.
- API key and model overrides in `.env` (see `.env.example`).

### Package (`src/reviewer/`)
- `__init__.py` — `__version__ = "0.1.0"`.
- `cli.py` — CLI entry point (`openaireview review <file>`, `openaireview serve`).
- `parsers.py` — Document parsers (PDF, DOCX, TEX, TXT/MD) returning `(title, full_text)`.
- `serve.py` — Local HTTP server for review visualization.
- `models.py` — `Comment` (with `paragraph_index`) and `ReviewResult` dataclasses.
- `client.py` — Multi-provider LLM client (OpenRouter, OpenAI, Anthropic, Gemini, Mistral). Auto-detects from API keys or explicit `--provider` / `REVIEW_PROVIDER`.
- `utils.py` — `count_tokens`, `chunk_text`, `parse_comments_from_response`, `locate_comment_in_document`, `assign_paragraph_indices`.
- `method_zero_shot.py` — single-prompt review; chunks paper if > 100K tokens.
- `method_local.py` — deep-checks each chunk with surrounding window context.
- `method_progressive.py` — sequential processing with running summary + consolidation.
- `evaluate.py` — recall/precision/F1 via fuzzy quote similarity, location-based recall, cost estimation.
- `viz/index.html` — Visualization UI (served by `serve.py`).

### CLI Usage
```bash
openaireview review paper.pdf                              # default: progressive, auto-detect provider
openaireview review paper.pdf --provider gemini             # explicit provider
openaireview review paper.pdf --method zero_shot
openaireview serve --results-dir ./review_results --port 8080
```

### Provider routing (`client.py`)
Five providers supported, all via OpenAI-compatible endpoints (no extra SDKs needed for chat):

| Provider | Env var | Base URL | Model prefix stripped |
|----------|---------|----------|----------------------|
| OpenRouter | `OPENROUTER_API_KEY` | `openrouter.ai/api/v1` | (none — passes model as-is) |
| OpenAI | `OPENAI_API_KEY` | (default) | (none) |
| Anthropic | `ANTHROPIC_API_KEY` | `api.anthropic.com/v1/` | `anthropic/` |
| Gemini | `GEMINI_API_KEY` | `generativelanguage.googleapis.com/v1beta/openai/` | `google/` |
| Mistral | `MISTRAL_API_KEY` | `api.mistral.ai/v1` | `mistralai/` |

**Resolution order** (4 tiers):
1. `--provider` CLI flag (explicit)
2. `REVIEW_PROVIDER` env var (persistent config in `.env`)
3. Model-prefix match: `anthropic/claude-*` → Anthropic API if key available
4. Fallback: first available key in priority order (openrouter > openai > anthropic > gemini > mistral)

**Reasoning tokens** are provider-specific:
- OpenRouter: `extra_body.reasoning.max_tokens`
- Anthropic: `extra_body.thinking` (budget_tokens)
- OpenAI: `reasoning_effort` string
- Gemini: `extra_body.thinking` (budget_tokens)
- Mistral: not supported

**Empty response handling**: if reasoning consumes all output tokens, auto-retries up to 3x with doubled `max_tokens`.

**OCR** is separate: Mistral OCR uses `MISTRAL_API_KEY` via the `mistralai` SDK directly (not through `client.py`). Controlled by `--ocr` flag, not `--provider`.

### Claude Code Skill (`src/reviewer/skill/`)
- `SKILL.md` — Skill definition for `/openaireview` command in Claude Code. Runs a multi-agent pipeline with section-level sub-agents and cross-cutting agents, producing severity-tiered findings (major/moderate/minor).
- `scripts/prepare_workspace.py` — Parses paper, splits into sections, writes workspace files.
- `scripts/consolidate_comments.py` — Merges sub-agent comment JSONs, deduplicates, and assigns severity tiers.
- `scripts/save_viz_json.py` — Builds viz-compatible JSON for `openaireview serve`.
- `references/criteria.md` — Review criteria copied into workspace for sub-agents.
- `references/subagent_templates.md` — Prompt templates for sub-agents.
- Install with `openaireview install-skill`, then use `/openaireview <path-or-url>` in Claude Code.

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
