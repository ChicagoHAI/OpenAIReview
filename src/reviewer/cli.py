"""CLI entry point for openaireview."""

import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


DEFAULT_MODEL = os.environ.get("MODEL", "anthropic/claude-opus-4-6")


def slugify(name: str) -> str:
    """Convert a name to a URL-friendly slug."""
    s = name.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")[:80]


def _model_short_name(model: str) -> str:
    """Extract short model name from provider/model string."""
    # "anthropic/claude-opus-4-6" -> "claude-opus-4-6"
    return model.split("/")[-1] if "/" in model else model


def _method_key(method: str, model: str) -> str:
    """Build a unique key for a method+model combination."""
    return f"{method}__{_model_short_name(model)}"


def cmd_review(args: argparse.Namespace) -> None:
    """Run a review on a document."""
    from .method_progressive import review_progressive
    from .method_local import review_local
    from .method_zero_shot import review_zero_shot
    from .parsers import is_url, parse_document
    from .utils import split_into_paragraphs

    # Set provider env var early so client.get_client() picks it up
    provider = getattr(args, "provider", None)
    if provider:
        os.environ["REVIEW_PROVIDER"] = provider

    source = args.file
    if is_url(source):
        print(f"Fetching and parsing URL...")
        title, content = parse_document(source)
        # Derive slug from URL: use the arxiv ID or last path segment
        default_slug = source.rstrip("/").split("/")[-1]
    else:
        file_path = Path(source)
        if not file_path.exists():
            print(f"Error: file not found: {file_path}", file=sys.stderr)
            sys.exit(1)
        print(f"Parsing {file_path.name}...")
        title, content = parse_document(file_path)
        fmt = file_path.suffix.lstrip(".").lower()
        default_slug = f"{file_path.stem}-{fmt}" if fmt else file_path.stem
        if fmt:
            title = f"{title} [{fmt.upper()}]"

    print(f"  Title: {title}")

    slug = args.name or slugify(default_slug)
    paragraphs = split_into_paragraphs(content)
    print(f"  {len(paragraphs)} paragraphs")

    method = args.method
    print(f"Running method: {method}...")

    reasoning = getattr(args, "reasoning_effort", None)

    if method == "zero_shot":
        result = review_zero_shot(slug, content, model=args.model,
                                  reasoning_effort=reasoning)
    elif method == "local":
        result = review_local(
            slug, content,
            model=args.model,
            reasoning_effort=reasoning,
        )
    elif method in ("progressive", "progressive_full"):
        consolidated, full = review_progressive(
            slug, content,
            model=args.model,
            reasoning_effort=reasoning,
        )
        result = full if method == "progressive_full" else consolidated
    else:
        print(f"Error: unknown method: {method}", file=sys.stderr)
        sys.exit(1)

    print(f"  Found {result.num_comments} comments")

    # Build output JSON
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{slug}.json"

    # Build viz-compatible data
    key = _method_key(method, args.model)
    paper_data = _build_paper_json(
        slug, title, content, paragraphs, method, key, result
    )

    # Merge with existing file if present
    if output_file.exists():
        try:
            existing = json.loads(output_file.read_text())
            existing["methods"][key] = paper_data["methods"][key]
            paper_data = existing
        except (json.JSONDecodeError, KeyError):
            pass

    output_file.write_text(json.dumps(paper_data, indent=2))
    print(f"Results saved to: {output_file}")


def _build_paper_json(
    slug: str,
    title: str,
    content: str,
    paragraphs: list[str],
    method: str,
    key: str,
    result,
) -> dict:
    """Build viz-compatible JSON structure for a paper."""
    para_list = [{"index": i, "text": p} for i, p in enumerate(paragraphs)]

    comments = []
    for i, c in enumerate(result.comments):
        comments.append({
            "id": f"{key}_{i}",
            "title": c.title,
            "quote": c.quote,
            "explanation": c.explanation,
            "comment_type": c.comment_type,
            "paragraph_index": c.paragraph_index,
        })

    model_short = _model_short_name(result.model) if result.model else ""
    label = method.replace("_", " ").title()
    if model_short:
        label = f"{label} ({model_short})"

    # Compute cost
    from .evaluate import compute_cost
    cost_usd = compute_cost(result)

    method_data = {
        "label": label,
        "model": result.model,
        "overall_feedback": result.overall_feedback,
        "comments": comments,
        "cost_usd": round(cost_usd, 4),
        "prompt_tokens": result.total_prompt_tokens,
        "completion_tokens": result.total_completion_tokens,
    }

    return {
        "slug": slug,
        "title": title,
        "paragraphs": para_list,
        "methods": {key: method_data},
    }


def cmd_install_skill(args: argparse.Namespace) -> None:
    """Install the /openaireview Claude Code skill to ~/.claude/commands/."""
    import shutil

    skill_src = Path(__file__).parent / "skill"
    dest = Path.home() / ".claude" / "commands" / "openaireview"

    if dest.exists() and not args.force:
        print(f"Skill already installed at {dest}")
        print("Run with --force to overwrite.")
        return

    dest.mkdir(parents=True, exist_ok=True)
    for item in skill_src.rglob("*"):
        if item.name == "__init__.py":
            continue
        rel = item.relative_to(skill_src)
        target = dest / rel
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            shutil.copy2(item, target)

    print(f"Skill installed to {dest}")
    print("You can now use /openaireview in any Claude Code project.")


def _resolve_lighton_model_dir(cli_value: str | None) -> str:
    """Resolve the LightOn model directory from CLI or environment."""
    model_dir = cli_value or os.environ.get("OPENAIREVIEW_LIGHTON_MODEL_DIR")
    if not model_dir:
        print(
            "Error: set --model-dir or OPENAIREVIEW_LIGHTON_MODEL_DIR for LightOn OCR.",
            file=sys.stderr,
        )
        sys.exit(1)
    return model_dir


def _resolve_lighton_prompt(cli_value: str | None) -> str:
    """Resolve the OCR prompt from CLI or environment."""
    from .lighton import DEFAULT_LIGHTON_PROMPT

    return cli_value or os.environ.get("OPENAIREVIEW_LIGHTON_PROMPT", DEFAULT_LIGHTON_PROMPT)


def _parse_model_spec(spec: str) -> tuple[str, str]:
    """Parse LABEL=PATH into a benchmark model spec."""
    if "=" not in spec:
        raise ValueError(f"Invalid model spec {spec!r}. Expected LABEL=PATH.")
    label, path = spec.split("=", 1)
    label = label.strip()
    path = path.strip()
    if not label or not path:
        raise ValueError(f"Invalid model spec {spec!r}. Expected LABEL=PATH.")
    return label, path


def _resolve_reference_text(args: argparse.Namespace) -> str | None:
    """Resolve optional reference text for OCR quality scoring."""
    if getattr(args, "reference_file", None):
        return Path(args.reference_file).read_text(encoding="utf-8", errors="replace")

    reference_url = getattr(args, "reference_url", None)
    if reference_url:
        from .parsers import parse_document

        _, text = parse_document(reference_url)
        return text

    if getattr(args, "reference_arxiv_html", False):
        from .parsers import _extract_arxiv_id_from_pdf, parse_arxiv_html

        arxiv_id = _extract_arxiv_id_from_pdf(Path(args.file))
        if not arxiv_id:
            print(
                "Warning: could not detect an arXiv ID from the PDF, skipping reference scoring.",
                file=sys.stderr,
            )
            return None
        html_url = f"https://arxiv.org/html/{arxiv_id}"
        try:
            _, text = parse_arxiv_html(html_url)
        except Exception as e:
            print(
                f"Warning: failed to fetch arXiv HTML reference from {html_url}: {e}",
                file=sys.stderr,
            )
            return None
        return text

    return None


def cmd_benchmark_ocr(args: argparse.Namespace) -> None:
    """Benchmark LightOn OCR on a local PDF."""
    from .lighton import benchmark_lighton_ocr

    pdf_path = Path(args.file)
    if not pdf_path.exists():
        print(f"Error: file not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    result = benchmark_lighton_ocr(
        pdf_path,
        model_dir=_resolve_lighton_model_dir(args.model_dir),
        provider=args.provider,
        max_pages=args.max_pages,
        longest_dim=args.longest_dim,
        prompt=_resolve_lighton_prompt(args.prompt),
        max_length=args.max_length,
        warmup_pages=args.warmup_pages,
    )
    print(json.dumps(result, indent=2))


def cmd_benchmark_ocr_compare(args: argparse.Namespace) -> None:
    """Benchmark multiple LightOn OCR models on the same rendered pages."""
    from .lighton import benchmark_lighton_ocr_models

    pdf_path = Path(args.file)
    if not pdf_path.exists():
        print(f"Error: file not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    try:
        model_specs = [_parse_model_spec(spec) for spec in args.model]
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    result = benchmark_lighton_ocr_models(
        pdf_path,
        models=model_specs,
        provider=args.provider,
        max_pages=args.max_pages,
        longest_dim=args.longest_dim,
        prompt=_resolve_lighton_prompt(args.prompt),
        max_length=args.max_length,
        warmup_pages=args.warmup_pages,
        reference_text=_resolve_reference_text(args),
        include_pymupdf_baseline=args.include_pymupdf_baseline,
    )
    print(json.dumps(result, indent=2))


def cmd_benchmark_transformers_ocr(args: argparse.Namespace) -> None:
    """Benchmark official LightOn Transformers OCR models on the same PDF."""
    from .lighton_transformers import benchmark_lighton_transformers_models

    pdf_path = Path(args.file)
    if not pdf_path.exists():
        print(f"Error: file not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    try:
        raw_specs = args.model or ["plain=lightonai/LightOnOCR-2-1B"]
        model_specs = [_parse_model_spec(spec) for spec in raw_specs]
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    result = benchmark_lighton_transformers_models(
        pdf_path,
        models=model_specs,
        device=args.device,
        dtype=args.dtype,
        max_pages=args.max_pages,
        longest_dim=args.longest_dim,
        max_new_tokens=args.max_new_tokens,
        warmup_pages=args.warmup_pages,
        batch_size=args.batch_size,
        reference_text=_resolve_reference_text(args),
        include_pymupdf_baseline=args.include_pymupdf_baseline,
        torch_num_threads=args.torch_num_threads,
    )
    print(json.dumps(result, indent=2))


def cmd_download_lighton(args: argparse.Namespace) -> None:
    """Download a LightOn model snapshot from Hugging Face."""
    if args.runtime == "transformers":
        from .lighton_transformers import download_lighton_transformers_model

        downloader = download_lighton_transformers_model
    else:
        from .lighton import download_lighton_onnx_model

        downloader = download_lighton_onnx_model
    try:
        path = downloader(
            args.model,
            output_dir=args.output_dir,
            revision=args.revision,
        )
    except Exception as e:
        print(f"Error: failed to download model: {e}", file=sys.stderr)
        sys.exit(1)

    print(path)


def cmd_extract_figures(args: argparse.Namespace) -> None:
    """Extract figure crops using a bbox-capable LightOn OCR model."""
    from .lighton import extract_figures_from_pdf

    pdf_path = Path(args.file)
    if not pdf_path.exists():
        print(f"Error: file not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    model_dir = _resolve_lighton_model_dir(args.model_dir)

    figures, pages = extract_figures_from_pdf(
        pdf_path,
        model_dir=model_dir,
        output_dir=output_dir,
        provider=args.provider,
        max_pages=args.max_pages,
        longest_dim=args.longest_dim,
        prompt=_resolve_lighton_prompt(args.prompt),
        max_length=args.max_length,
    )

    manifest = {
        "pdf_path": str(pdf_path),
        "model_dir": model_dir,
        "provider": args.provider,
        "page_count": len(pages),
        "figure_count": len(figures),
        "pages": [
            {
                "page_index": page.page_index,
                "width": page.width,
                "height": page.height,
                "generated_tokens": page.generated_tokens,
                "text": page.text,
            }
            for page in pages
        ],
        "figures": [
            {
                "page_index": figure.page_index,
                "figure_index": figure.figure_index,
                "bbox_norm": list(figure.bbox_norm),
                "bbox_pixels": list(figure.bbox_pixels),
                "crop_path": str(figure.crop_path),
            }
            for figure in figures
        ],
    }
    manifest_path = output_dir / "figures_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))

    print(f"Extracted {len(figures)} figures to {output_dir}")
    print(f"Manifest saved to: {manifest_path}")


def cmd_serve(args: argparse.Namespace) -> None:
    """Start the visualization server."""
    from .serve import run_server
    run_server(results_dir=args.results_dir, port=args.port)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="openaireview",
        description="AI-powered academic paper reviewer",
    )
    subparsers = parser.add_subparsers(dest="command")

    # review subcommand
    review_parser = subparsers.add_parser(
        "review", help="Review an academic paper"
    )
    review_parser.add_argument(
        "file", help="Path to paper file or arXiv URL (e.g. https://arxiv.org/html/2310.06825)"
    )
    review_parser.add_argument(
        "--method",
        choices=["zero_shot", "local", "progressive", "progressive_full"],
        default="progressive",
        help="Review method (default: progressive)",
    )
    review_parser.add_argument(
        "--model", default=DEFAULT_MODEL,
        help="Model to use (default: anthropic/claude-opus-4-6)",
    )
    review_parser.add_argument(
        "--provider",
        choices=["openrouter", "openai", "anthropic", "gemini", "mistral"],
        default=None,
        help="LLM provider (default: auto-detect from API keys, or REVIEW_PROVIDER env var)",
    )
    review_parser.add_argument(
        "--output-dir", default="./review_results",
        help="Directory for output JSON files (default: ./review_results)",
    )
    review_parser.add_argument(
        "--name", default=None,
        help="Paper slug name (default: derived from filename)",
    )
    review_parser.add_argument(
        "--reasoning-effort",
        choices=["none", "low", "medium", "high"],
        default=None,
        help="Reasoning effort level (default: adaptive/auto)",
    )

    # serve subcommand
    serve_parser = subparsers.add_parser(
        "serve", help="Start visualization server"
    )
    serve_parser.add_argument(
        "--results-dir", default="./review_results",
        help="Directory containing result JSON files (default: ./review_results)",
    )
    serve_parser.add_argument(
        "--port", type=int, default=8080,
        help="Server port (default: 8080)",
    )

    # install-skill subcommand
    install_parser = subparsers.add_parser(
        "install-skill", help="Install the /openaireview Claude Code skill"
    )
    install_parser.add_argument(
        "--force", action="store_true",
        help="Overwrite existing installation",
    )

    benchmark_parser = subparsers.add_parser(
        "benchmark-ocr",
        help="Benchmark optional LightOn OCR on a local PDF",
    )
    benchmark_parser.add_argument("file", help="Path to a local PDF file")
    benchmark_parser.add_argument(
        "--model-dir",
        default=None,
        help="Path to the LightOn ONNX model export (default: OPENAIREVIEW_LIGHTON_MODEL_DIR)",
    )
    benchmark_parser.add_argument(
        "--provider",
        choices=["auto", "cpu", "cuda"],
        default="cpu",
        help="ONNX Runtime provider to use (default: cpu)",
    )
    benchmark_parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Limit the benchmark to the first N pages",
    )
    benchmark_parser.add_argument(
        "--longest-dim",
        type=int,
        default=1540,
        help="Render pages so the longest dimension is this many pixels (default: 1540)",
    )
    benchmark_parser.add_argument(
        "--max-length",
        type=int,
        default=4096,
        help="Maximum generated token length per page (default: 4096)",
    )
    benchmark_parser.add_argument(
        "--warmup-pages",
        type=int,
        default=1,
        help="Warm up the first N rendered pages before timing (default: 1)",
    )
    benchmark_parser.add_argument(
        "--prompt",
        default=None,
        help="Override the OCR prompt (default: OPENAIREVIEW_LIGHTON_PROMPT or built-in prompt)",
    )

    compare_parser = subparsers.add_parser(
        "benchmark-ocr-compare",
        help="Benchmark multiple LightOn OCR models on the same PDF",
    )
    compare_parser.add_argument("file", help="Path to a local PDF file")
    compare_parser.add_argument(
        "--model",
        action="append",
        required=True,
        help="Benchmark spec in the form LABEL=PATH. Repeat for each model.",
    )
    compare_parser.add_argument(
        "--provider",
        choices=["auto", "cpu", "cuda"],
        default="cpu",
        help="ONNX Runtime provider to use (default: cpu)",
    )
    compare_parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Limit the benchmark to the first N pages",
    )
    compare_parser.add_argument(
        "--longest-dim",
        type=int,
        default=1540,
        help="Render pages so the longest dimension is this many pixels (default: 1540)",
    )
    compare_parser.add_argument(
        "--max-length",
        type=int,
        default=4096,
        help="Maximum generated token length per page (default: 4096)",
    )
    compare_parser.add_argument(
        "--warmup-pages",
        type=int,
        default=1,
        help="Warm up the first N rendered pages before timing (default: 1)",
    )
    compare_parser.add_argument(
        "--prompt",
        default=None,
        help="Override the OCR prompt (default: OPENAIREVIEW_LIGHTON_PROMPT or built-in prompt)",
    )
    compare_parser.add_argument(
        "--reference-file",
        default=None,
        help="Optional reference text file for OCR quality scoring",
    )
    compare_parser.add_argument(
        "--reference-url",
        default=None,
        help="Optional reference URL for OCR quality scoring",
    )
    compare_parser.add_argument(
        "--reference-arxiv-html",
        action="store_true",
        help="If the PDF is an arXiv paper, fetch arXiv HTML and use it as reference text",
    )
    compare_parser.add_argument(
        "--include-pymupdf-baseline",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Include the built-in PyMuPDF parser baseline in the comparison (default: true)",
    )

    transformers_parser = subparsers.add_parser(
        "benchmark-transformers-ocr",
        help="Benchmark official LightOn Transformers OCR models on the same PDF",
    )
    transformers_parser.add_argument("file", help="Path to a local PDF file")
    transformers_parser.add_argument(
        "--model",
        action="append",
        default=None,
        help=(
            "Benchmark spec in the form LABEL=MODEL_ID. "
            "Repeat for each model. Default: plain=lightonai/LightOnOCR-2-1B"
        ),
    )
    transformers_parser.add_argument(
        "--device",
        choices=["auto", "cpu", "cuda", "mps"],
        default="auto",
        help="Torch device to use (default: auto)",
    )
    transformers_parser.add_argument(
        "--dtype",
        choices=["auto", "float32", "float16", "bfloat16"],
        default="auto",
        help="Torch dtype to use (default: auto)",
    )
    transformers_parser.add_argument(
        "--torch-num-threads",
        type=int,
        default=None,
        help="Optional torch CPU thread count override",
    )
    transformers_parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Limit the benchmark to the first N pages",
    )
    transformers_parser.add_argument(
        "--longest-dim",
        type=int,
        default=1540,
        help="Render pages to this maximum longest dimension (default: 1540)",
    )
    transformers_parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=4096,
        help="Maximum generated tokens per page (default: 4096)",
    )
    transformers_parser.add_argument(
        "--warmup-pages",
        type=int,
        default=1,
        help="Warm up the first N rendered pages before timing (default: 1)",
    )
    transformers_parser.add_argument(
        "--batch-size",
        type=int,
        default=1,
        help="Number of rendered pages to decode per generation batch (default: 1)",
    )
    transformers_parser.add_argument(
        "--reference-file",
        default=None,
        help="Optional reference text file for OCR quality scoring",
    )
    transformers_parser.add_argument(
        "--reference-url",
        default=None,
        help="Optional reference URL for OCR quality scoring",
    )
    transformers_parser.add_argument(
        "--reference-arxiv-html",
        action="store_true",
        help="If the PDF is an arXiv paper, fetch arXiv HTML and use it as reference text",
    )
    transformers_parser.add_argument(
        "--include-pymupdf-baseline",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Include the built-in PyMuPDF parser baseline in the comparison (default: true)",
    )

    extract_figures_parser = subparsers.add_parser(
        "extract-figures",
        help="Extract figure crops with a bbox-capable LightOn OCR model",
    )
    extract_figures_parser.add_argument("file", help="Path to a local PDF file")
    extract_figures_parser.add_argument(
        "--model-dir",
        default=None,
        help="Path to the LightOn ONNX model export (default: OPENAIREVIEW_LIGHTON_MODEL_DIR)",
    )
    extract_figures_parser.add_argument(
        "--provider",
        choices=["auto", "cpu", "cuda"],
        default="cpu",
        help="ONNX Runtime provider to use (default: cpu)",
    )
    extract_figures_parser.add_argument(
        "--output-dir",
        default="./figure_results",
        help="Directory for extracted figure crops and manifest (default: ./figure_results)",
    )
    extract_figures_parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Limit extraction to the first N pages",
    )
    extract_figures_parser.add_argument(
        "--longest-dim",
        type=int,
        default=1540,
        help="Render pages so the longest dimension is this many pixels (default: 1540)",
    )
    extract_figures_parser.add_argument(
        "--max-length",
        type=int,
        default=4096,
        help="Maximum generated token length per page (default: 4096)",
    )
    extract_figures_parser.add_argument(
        "--prompt",
        default=None,
        help="Override the OCR prompt (default: OPENAIREVIEW_LIGHTON_PROMPT or built-in prompt)",
    )

    download_parser = subparsers.add_parser(
        "download-lighton",
        help="Download a LightOn model snapshot from Hugging Face",
    )
    download_parser.add_argument(
        "model",
        help=(
            "Model alias or Hugging Face repo id. "
            "Built-in aliases currently include: plain, plain-onnx, bbox, bbox-soup"
        ),
    )
    download_parser.add_argument(
        "--runtime",
        choices=["onnx", "transformers"],
        default="onnx",
        help="Model runtime packaging to download (default: onnx)",
    )
    download_parser.add_argument(
        "--output-dir",
        default=None,
        help="Optional local directory for the downloaded snapshot",
    )
    download_parser.add_argument(
        "--revision",
        default=None,
        help="Optional Hugging Face revision",
    )

    args = parser.parse_args()
    if args.command == "review":
        cmd_review(args)
    elif args.command == "serve":
        cmd_serve(args)
    elif args.command == "install-skill":
        cmd_install_skill(args)
    elif args.command == "benchmark-ocr":
        cmd_benchmark_ocr(args)
    elif args.command == "benchmark-ocr-compare":
        cmd_benchmark_ocr_compare(args)
    elif args.command == "benchmark-transformers-ocr":
        cmd_benchmark_transformers_ocr(args)
    elif args.command == "extract-figures":
        cmd_extract_figures(args)
    elif args.command == "download-lighton":
        cmd_download_lighton(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
