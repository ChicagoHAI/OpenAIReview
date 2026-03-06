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

    args = parser.parse_args()
    if args.command == "review":
        cmd_review(args)
    elif args.command == "serve":
        cmd_serve(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
