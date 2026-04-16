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
OCR_DISCLAIMER = "This document was extracted by OCR engine and could contain mistakes."

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
    ocr = getattr(args, "ocr", None)
    max_pages = getattr(args, "max_pages", None)
    if max_pages and not (not is_url(source) and Path(source).suffix.lower() == ".pdf"):
        print("  Warning: --max-pages only applies to local PDF files, ignoring")
        max_pages = None
    if is_url(source):
        print(f"Fetching and parsing URL...")
        title, content, was_ocr = parse_document(source, ocr=ocr, max_pages=max_pages)
        # Derive slug from URL: use the arxiv ID or last path segment
        default_slug = source.rstrip("/").split("/")[-1]
    else:
        file_path = Path(source)
        if not file_path.exists():
            print(f"Error: file not found: {file_path}", file=sys.stderr)
            sys.exit(1)
        print(f"Parsing {file_path.name}...")
        title, content, was_ocr = parse_document(file_path, ocr=ocr, max_pages=max_pages)
        fmt = file_path.suffix.lstrip(".").lower()
        default_slug = f"{file_path.stem}-{fmt}" if fmt else file_path.stem
        if fmt:
            title = f"{title} [{fmt.upper()}]"

    print(f"  Title: {title}")

    # Truncate to max_tokens if specified
    max_tokens = getattr(args, "max_tokens", None)
    if max_tokens:
        from .utils import count_tokens, truncate_text
        token_count = count_tokens(content)
        if token_count > max_tokens:
            content = truncate_text(content, max_tokens)
            print(f"  Truncated from {token_count} to {max_tokens} tokens")

    slug = args.name or slugify(default_slug)
    paragraphs = split_into_paragraphs(content)
    print(f"  {len(paragraphs)} paragraphs")

    if was_ocr:
        print("  Source: OCR (notation auto-correction applied)")

    method = args.method
    print(f"Running method: {method}...")

    if args.skip_nonsubstantial == "true":
        skip = True
    else:
        skip = False

    reasoning = getattr(args, "reasoning_effort", None)

    if method == "zero_shot":
        result = review_zero_shot(slug, content, model=args.model,
                                  reasoning_effort=reasoning, ocr=was_ocr)
    elif method == "local":
        result = review_local(
            slug, content,
            model=args.model,
            reasoning_effort=reasoning,
            ocr=was_ocr,
        )
    elif method in ("progressive", "progressive_full"):
        consolidated, full = review_progressive(
            slug, content,
            model=args.model,
            reasoning_effort=reasoning,
            skip_nonsubstantial=skip,
            ocr=was_ocr,
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
        slug, title, paragraphs, method, key, result, was_ocr
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
    paragraphs: list[str],
    method: str,
    key: str,
    result,
    was_ocr: bool,
) -> dict:
    """Build viz-compatible JSON structure for a paper."""
    if was_ocr:
        paragraphs = paragraphs + [OCR_DISCLAIMER]
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


def cmd_extract(args: argparse.Namespace) -> None:
    """Run OCR extraction on a document and save as markdown with metadata."""
    from datetime import date
    from .parsers import parse_document
    from .ocr_postprocess import fix_ocr_notation

    source = Path(args.file)
    if not source.exists():
        print(f"Error: file not found: {source}", file=sys.stderr)
        sys.exit(1)

    ocr = getattr(args, "ocr", None)
    print(f"Extracting {source.name}...")
    title, content, was_ocr = parse_document(source, ocr=ocr)
    print(f"  Title: {title}")

    # Build YAML frontmatter
    output_path = Path(args.output) if args.output else source.with_suffix(".md")
    frontmatter_lines = [
        "---",
        f"title: \"{title}\"",
        f"source: \"{source.name}\"",
        f"extract_date: \"{date.today().isoformat()}\"",
    ]
    if was_ocr:
        engine = getattr(parse_document, "_last_ocr_engine", ocr or "auto")
        frontmatter_lines.append(f"ocr_engine: \"{engine}\"")
    frontmatter_lines.append("---")

    output_text = "\n".join(frontmatter_lines) + "\n\n" + content
    output_path.write_text(output_text)
    print(f"  Saved to {output_path} ({len(content)} chars)")


def cmd_serve(args: argparse.Namespace) -> None:
    """Start the visualization server."""
    from .serve import run_server
    run_server(results_dir=args.results_dir, port=args.port)


def main() -> None:
    from . import __version__
    parser = argparse.ArgumentParser(
        prog="openaireview",
        description="AI-powered academic paper reviewer",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
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
    review_parser.add_argument(
        "--skip-nonsubstantial",
        choices=["true", "false"],
        default="false",
        help="Skip non-substantial passages (default: false)",
    )
    review_parser.add_argument(
        "--ocr",
        choices=["mistral", "deepseek", "marker", "pymupdf"],
        default=None,
        help="PDF OCR engine (default: auto -- tries mistral, deepseek, marker, pymupdf)",
    )
    review_parser.add_argument(
        "--max-pages", type=int, default=None,
        help="Only process the first N pages of a PDF (saves OCR cost)",
    )
    review_parser.add_argument(
        "--max-tokens", type=int, default=None,
        help="Truncate input text to first N tokens before review",
    )

    # extract subcommand
    extract_parser = subparsers.add_parser(
        "extract", help="Extract text from a document (OCR stage only)"
    )
    extract_parser.add_argument(
        "file", help="Path to paper file (PDF, DOCX, TEX, etc.)"
    )
    extract_parser.add_argument(
        "-o", "--output", default=None,
        help="Output markdown path (default: same name with .md extension)",
    )
    extract_parser.add_argument(
        "--ocr",
        choices=["mistral", "deepseek", "marker", "pymupdf"],
        default=None,
        help="PDF OCR engine (default: auto)",
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

    args = parser.parse_args()
    if args.command == "review":
        cmd_review(args)
    elif args.command == "extract":
        cmd_extract(args)
    elif args.command == "serve":
        cmd_serve(args)
    elif args.command == "install-skill":
        cmd_install_skill(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
