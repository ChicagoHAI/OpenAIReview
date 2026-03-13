# OpenAIReview

[![PyPI version](https://img.shields.io/pypi/v/openaireview.svg)](https://pypi.org/project/openaireview/)

Our goal is provide thorough and detailed reviews to help researchers conduct the best research. See more examples [here](https://openaireview.github.io/).

![Example](assets/example.png)

## Installation

```bash
uv venv && uv pip install openaireview
# or: pip install openaireview
```

For development:
```bash
git clone https://github.com/ChicagoHAI/OpenAIReview.git
cd OpenAIReview
uv venv && uv pip install -e .
# or: pip install -e .
```

For optional LightOn OCR support:
```bash
pip install "openaireview[lighton]"
```

For the official Python Transformers runtime:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install "openaireview[lighton-transformers]"
```

To download the public ONNX Runtime LightOn OCR checkpoint:
```bash
openaireview download-lighton plain --output-dir ./models/lighton-oc2-plain
```

### PDF math support (optional)

For math-heavy PDFs, install [Marker](https://github.com/VikParuchuri/marker) separately to get accurate LaTeX extraction. Without Marker, PDFs are processed with PyMuPDF which cannot extract math symbols correctly.

```bash
# Install Marker CLI in an isolated environment (avoids dependency conflicts)
uv tool install marker-pdf --with psutil
```

Marker is used automatically when available on PATH. It is most useful for math-heavy PDFs, but runs very slowly without a GPU. For papers with math, we recommend using `.tex` source, `.md`, or arXiv HTML URLs instead of PDF when possible — these always produce correct output without needing Marker.

### LightOn ONNX PDF parsing (optional)

You can also plug in a locally exported LightOn ONNX vision model for PDF extraction. The repo does not vendor model weights; it only provides the integration hook.

```bash
pip install "openaireview[lighton]"
export OPENAIREVIEW_PDF_BACKEND=lighton_onnx
export OPENAIREVIEW_LIGHTON_MODEL_DIR=/path/to/lighton-oc2-2.1b-onnx
openaireview review examples/2602.18458v1.pdf
```

If you want LightOn to be attempted automatically after Marker and before the PyMuPDF fallback, keep `OPENAIREVIEW_PDF_BACKEND=auto` and set only `OPENAIREVIEW_LIGHTON_MODEL_DIR`.

Benchmark CPU throughput:

```bash
openaireview benchmark-ocr examples/2602.18458v1.pdf \
  --model-dir /path/to/lighton-oc2-2.1b-onnx \
  --provider cpu \
  --max-pages 5
```

Extract figure crops with a bbox-capable checkpoint such as `LightOnOCR-2-1B-bbox` or `LightOnOCR-2-1B-bbox-soup`:

```bash
openaireview extract-figures examples/2602.18458v1.pdf \
  --model-dir /path/to/lighton-oc2-2.1b-bbox-soup-onnx \
  --provider cpu \
  --output-dir ./figure_results
```

This writes cropped figures plus a `figures_manifest.json` file containing page text, normalized boxes, and pixel coordinates for downstream pipelines.

Compare plain OCR vs bbox vs bbox-soup on the same rendered pages:

```bash
openaireview benchmark-ocr-compare examples/2602.18458v1.pdf \
  --provider cpu \
  --model plain=/models/lighton-oc2-2.1b \
  --model bbox=/models/lighton-oc2-2.1b-bbox \
  --model soup=/models/lighton-oc2-2.1b-bbox-soup \
  --reference-arxiv-html
```

The comparison benchmark renders the PDF once, runs each model on the same page images, reports per-model throughput, counts image markers, and, when reference text is available, scores OCR text with lightweight similarity metrics.

Compare the existing parser against ONNX OCR using arXiv HTML as the reference:

```bash
openaireview benchmark-ocr-compare examples/2602.18458v1.pdf \
  --provider cpu \
  --model plain=./models/lighton-oc2-plain \
  --reference-arxiv-html \
  --include-pymupdf-baseline
```

Today, the public ONNX path is straightforward for the plain OCR checkpoint. Public ONNX releases for `bbox` and `bbox-soup` were not available when this was written, so those require a custom export path or a different runtime.

### LightOn Transformers OCR benchmarking (recommended first step)

To benchmark OCR quality against arXiv HTML using the official Python runtime:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install "openaireview[lighton-transformers]"

openaireview benchmark-transformers-ocr examples/2602.18458v1.pdf \
  --device cpu \
  --batch-size 1 \
  --model plain=lightonai/LightOnOCR-2-1B \
  --reference-arxiv-html
```

This follows the official LightOn Python route and compares the OCR text against the arXiv HTML parse while also reporting the built-in `pymupdf` baseline.

## Quick Start

First, set an API key for any supported provider:

```bash
export OPENROUTER_API_KEY=your_key_here   # OpenRouter (supports all models)
# or
export OPENAI_API_KEY=your_key_here       # OpenAI native
# or
export ANTHROPIC_API_KEY=your_key_here    # Anthropic native
# or
export GEMINI_API_KEY=your_key_here       # Google Gemini native
```

Or create a `.env` file in your working directory (see `.env.example`).

Then review a paper and visualize results:

```bash
# Review a local file
openaireview review paper.pdf

# Or review directly from an arXiv URL
openaireview review https://arxiv.org/html/2602.18458v1

# Visualize results
openaireview serve
# Open http://localhost:8080
```

## CLI Reference

### `openaireview review <file_or_url>`

Review an academic paper for technical and logical issues. Accepts a local file path or an arXiv URL.

| Option | Default | Description |
|---|---|---|
| `--method` | `progressive` | Review method: `zero_shot`, `local`, `progressive`, `progressive_full` |
| `--model` | `anthropic/claude-opus-4-6` | Model to use |
| `--output-dir` | `./review_results` | Directory for output JSON files |
| `--name` | (from filename) | Paper slug name |

### `openaireview serve`

Start a local visualization server to browse review results.

| Option | Default | Description |
|---|---|---|
| `--results-dir` | `./review_results` | Directory containing result JSON files |
| `--port` | `8080` | Server port |

### `openaireview benchmark-ocr <pdf>`

Benchmark optional LightOn OCR on a local PDF and print JSON metrics including model load time, render time, inference time, and pages/sec.

### `openaireview benchmark-ocr-compare <pdf>`

Benchmark multiple LightOn OCR checkpoints on the same rendered pages. This is the intended command for comparing `plain` vs `bbox` vs `bbox-soup` on CPU before deciding whether the one-pass soup model is good enough.

### `openaireview benchmark-transformers-ocr <pdf>`

Benchmark one or more official LightOn Transformers checkpoints on a local PDF. This is the preferred first benchmark path for quality-vs-reference experiments because it follows the runtime shown in the public LightOn demo. Use `--batch-size` to batch multiple rendered pages into one generation call when testing GPU throughput.

### `openaireview download-lighton <alias_or_repo_id>`

Download a LightOn ONNX model snapshot from Hugging Face. Built-in aliases currently cover the public ONNX plain OCR checkpoint.

### `openaireview extract-figures <pdf>`

Run a bbox-capable LightOn OCR checkpoint on a local PDF, save cropped figures, and emit a manifest JSON for downstream multimodal pipelines.

## Supported Input Formats

- **PDF** (`.pdf`) — uses [Marker](https://github.com/VikParuchuri/marker) for high-quality extraction with LaTeX math; falls back to PyMuPDF if Marker is not installed
- **DOCX** (`.docx`) — via python-docx
- **LaTeX** (`.tex`) — plain text with title extraction from `\title{}`
- **Text/Markdown** (`.txt`, `.md`) — plain text
- **arXiv HTML** — fetch and parse directly from `https://arxiv.org/html/<id>` or `https://arxiv.org/abs/<id>`

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OPENROUTER_API_KEY` | | OpenRouter API key (supports all models) |
| `OPENAI_API_KEY` | | OpenAI native API key |
| `ANTHROPIC_API_KEY` | | Anthropic native API key |
| `GEMINI_API_KEY` | | Google Gemini native API key |
| `MODEL` | `anthropic/claude-opus-4-6` | Default model |
| `OPENAIREVIEW_PDF_BACKEND` | `auto` | PDF parser backend: `auto`, `marker`, `lighton_onnx`, or `pymupdf` |
| `OPENAIREVIEW_PDF_PREFER_ARXIV_HTML` | `1` | For local arXiv PDFs, try `arxiv.org/html/<id>` before PDF OCR/text extraction |
| `OPENAIREVIEW_LIGHTON_MODEL_DIR` | | Path to a local LightOn ONNX model export |
| `OPENAIREVIEW_LIGHTON_PROMPT` | built-in OCR prompt | Custom prompt used for the LightOn ONNX page extraction |
| `OPENAIREVIEW_LIGHTON_PROVIDER` | `auto` | Provider for optional LightOn OCR inside the parser: `auto`, `cpu`, or `cuda` |
| `OPENAIREVIEW_LIGHTON_LONGEST_DIM` | `1540` | Render size used before optional LightOn OCR |
| `OPENAIREVIEW_LIGHTON_MAX_LENGTH` | `4096` | Maximum generated token length per page for optional LightOn OCR |

Set one API key. The provider is auto-detected from whichever key is set. See `.env.example` for a template.

## Supported Models & Pricing

All models available on [OpenRouter](https://openrouter.ai) are supported — use any model ID via `--model`. The following models have built-in pricing for accurate cost tracking in the visualization:

| Model | Input ($/1M tokens) | Output ($/1M tokens) |
|---|---|---|
| `anthropic/claude-opus-4-6` | $5.00 | $25.00 |
| `anthropic/claude-opus-4-5` | $5.00 | $25.00 |
| `openai/gpt-5.2-pro` | $21.00 | $168.00 |
| `google/gemini-3.1-pro-preview` | $2.00 | $12.00 |

For models not listed above, a default rate of $5.00/$25.00 per 1M tokens is used.

## Review Methods

- **zero_shot** — single prompt asking the model to find all issues
- **local** — deep-checks each chunk with surrounding window context (no filtering)
- **progressive** — sequential processing with running summary, then consolidation
- **progressive_full** — same as progressive but returns all comments before consolidation

## Claude Code Skill

A deep-review skill is bundled with the package. It runs a multi-agent pipeline — one sub-agent per paper section plus cross-cutting agents — and produces severity-tiered findings (major / moderate / minor).

Install once:

```bash
pip install openaireview
openaireview install-skill
```

Then in any Claude Code project:

```
/openaireview paper.pdf
/openaireview https://arxiv.org/abs/2602.18458
```

Finally, run `openaireview serve` to see results.

## Development

Install with dev dependencies (includes pytest):

```bash
uv pip install -e ".[dev]"
```

Run tests:

```bash
pytest tests/
```

Integration tests that call the API require `OPENROUTER_API_KEY` and are skipped automatically when it's not set.

## Benchmarks

Benchmark data and experiment scripts are in `benchmarks/`. See `benchmarks/REPORT.md` for results.

## Related Resources

- [AI-research-feedback](https://github.com/claesbackman/AI-research-feedback)
- [OpenEvalProject](https://github.com/OpenEvalProject)

## License

[MIT](LICENSE)
