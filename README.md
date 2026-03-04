# OpenAIReview

AI-powered academic paper reviewer that detects technical and logical errors using LLMs.

## Installation

```bash
pip install .
# or for development:
pip install -e .
```

## Quick Start

First, set your OpenRouter API key (get one at [openrouter.ai/keys](https://openrouter.ai/keys)):

```bash
export OPENROUTER_API_KEY=your_key_here
```

Or create a `.env` file in your working directory:

```
OPENROUTER_API_KEY=your_key_here
```

Then review a paper and visualize results:

```bash
# Review a local file
openaireview review paper.pdf

# Or review directly from an arXiv URL
openaireview review https://arxiv.org/html/2310.06825

# Visualize results
openaireview serve
# Open http://localhost:8080
```

## CLI Reference

### `openaireview review <file_or_url>`

Review an academic paper for technical and logical issues. Accepts a local file path or an arXiv URL.

| Option | Default | Description |
|---|---|---|
| `--method` | `incremental` | Review method: `zero_shot`, `local`, `incremental`, `incremental_full` |
| `--model` | `anthropic/claude-opus-4-5` | Model to use |
| `--output-dir` | `./review_results` | Directory for output JSON files |
| `--name` | (from filename) | Paper slug name |

### `openaireview serve`

Start a local visualization server to browse review results.

| Option | Default | Description |
|---|---|---|
| `--results-dir` | `./review_results` | Directory containing result JSON files |
| `--port` | `8080` | Server port |

## Supported Input Formats

- **PDF** (`.pdf`) — text extraction via PyMuPDF
- **DOCX** (`.docx`) — via python-docx
- **LaTeX** (`.tex`) — plain text with title extraction from `\title{}`
- **Text/Markdown** (`.txt`, `.md`) — plain text
- **arXiv HTML** — fetch and parse directly from `https://arxiv.org/html/<id>` or `https://arxiv.org/abs/<id>`

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OPENROUTER_API_KEY` | (required) | Your OpenRouter API key |
| `MODEL` | `anthropic/claude-opus-4-5` | Default model |

These can be set as environment variables or in a `.env` file. See `.env.example` for a template.

## Supported Models & Pricing

All models available on [OpenRouter](https://openrouter.ai) are supported — use any model ID via `--model`. The following models have built-in pricing for accurate cost tracking in the visualization (prices fetched from OpenRouter on 2026-03-04):

| Model | Input ($/1M tokens) | Output ($/1M tokens) |
|---|---|---|
| `anthropic/claude-opus-4-6` | $5.00 | $25.00 |
| `anthropic/claude-opus-4-5` | $5.00 | $25.00 |
| `anthropic/claude-haiku-4-5` | $1.00 | $5.00 |
| `openai/gpt-5.2-pro` | $21.00 | $168.00 |
| `openai/gpt-4o` | $2.50 | $10.00 |
| `openai/gpt-4o-mini` | $0.15 | $0.60 |
| `google/gemini-2.0-flash-001` | $0.10 | $0.40 |
| `z-ai/glm-5` | $0.80 | $2.56 |
| `moonshotai/kimi-k2.5` | $0.45 | $2.20 |

For models not listed above, a default rate of $5.00/$25.00 per 1M tokens is used.

## Review Methods

- **zero_shot** — single prompt asking the model to find all issues
- **local** — deep-checks each chunk with surrounding window context (no filtering)
- **incremental** — sequential processing with running summary, then consolidation
- **incremental_full** — same as incremental but returns all comments before consolidation

## Benchmarks

Benchmark data and experiment scripts are in `benchmarks/`. See `benchmarks/REPORT.md` for results.
