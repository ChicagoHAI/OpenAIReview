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


def cmd_perturb(args: argparse.Namespace) -> None:
    """Generate seeded perturbations for a paper."""
    from .parsers import is_url, parse_document
    from .perturbation import (
        add_line_numbers,
        extract_candidates,
        generate_freeform,
        generate_from_candidates,
        inject_perturbations,
        validate_perturbations,
    )

    source = args.file
    if is_url(source):
        print(f"Fetching and parsing URL...")
        title, content = parse_document(source)
        slug = source.rstrip("/").split("/")[-1]
    else:
        file_path = Path(source)
        if not file_path.exists():
            print(f"Error: file not found: {file_path}", file=sys.stderr)
            sys.exit(1)
        print(f"Parsing {file_path.name}...")
        title, content = parse_document(file_path)
        slug = slugify(file_path.stem)

    print(f"  Title: {title}")
    print(f"  Length: {len(content):,} chars")

    # Stage 0: Extract candidates
    print("\nStage 0: Extracting candidate spans...")
    candidates = extract_candidates(content)
    print(f"  {len(candidates)} candidates found")

    from collections import Counter
    type_counts = Counter(c.span_type.value for c in candidates)
    for t, n in type_counts.most_common():
        print(f"    {t}: {n}")

    reasoning = getattr(args, "reasoning_effort", None)

    # Stage 1: LLM picks from candidates
    print("\nStage 1: Generating perturbations from candidates...")
    perturbations = generate_from_candidates(
        candidates,
        model=args.model,
        n_per_category=args.n_per_category,
        reasoning_effort=reasoning,
    )

    # Stage 2: Free-form proposals
    if not args.skip_stage2:
        print("\nStage 2: Free-form proposals...")
        numbered = add_line_numbers(content)
        covered = list({p.category.value for p in perturbations})
        freeform = generate_freeform(
            content, numbered, covered,
            model=args.model,
            n_errors=args.n_freeform,
            reasoning_effort=reasoning,
        )
        perturbations.extend(freeform)

    # Validate
    print(f"\nValidating {len(perturbations)} perturbations...")
    valid, rejected = validate_perturbations(perturbations, content, candidates)
    print(f"  Valid: {len(valid)}, Rejected: {len(rejected)}")
    for p, reason in rejected:
        print(f"    REJECTED {p.perturbation_id}: {reason[:80]}")

    # Inject
    corrupted, applied = inject_perturbations(content, valid)
    print(f"\nInjected {len(applied)} perturbations")

    # Save outputs
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save perturbation manifest
    manifest = {
        "paper_title": title,
        "paper_slug": slug,
        "n_candidates": len(candidates),
        "n_generated": len(perturbations),
        "n_valid": len(valid),
        "n_injected": len(applied),
        "model": args.model,
        "perturbations": [
            {
                "perturbation_id": p.perturbation_id,
                "span_id": p.span_id,
                "category": p.category.value,
                "original": p.original,
                "perturbed": p.perturbed,
                "why_wrong": p.why_wrong,
                "difficulty": p.difficulty.value,
                "support_span_ids": p.support_span_ids,
            }
            for p in applied
        ],
    }

    manifest_path = output_dir / f"{slug}_perturbations.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"\nManifest saved to: {manifest_path}")

    # Save corrupted paper
    corrupted_path = output_dir / f"{slug}_corrupted.md"
    corrupted_path.write_text(corrupted)
    print(f"Corrupted paper saved to: {corrupted_path}")

    # Save clean paper for reference
    clean_path = output_dir / f"{slug}_clean.md"
    clean_path.write_text(content)
    print(f"Clean paper saved to: {clean_path}")

    print(f"\nDone. Run a review on the corrupted paper, then score with:")
    print(f"  openaireview score {manifest_path} <review_results.json>")


def cmd_score(args: argparse.Namespace) -> None:
    """Score a review against injected perturbations."""
    from .perturbation.models import ErrorCategory, Perturbation, Difficulty
    from .perturbation.score import score_review

    manifest_path = Path(args.manifest)
    review_path = Path(args.review)

    if not manifest_path.exists():
        print(f"Error: manifest not found: {manifest_path}", file=sys.stderr)
        sys.exit(1)
    if not review_path.exists():
        print(f"Error: review not found: {review_path}", file=sys.stderr)
        sys.exit(1)

    manifest = json.loads(manifest_path.read_text())
    review_data = json.loads(review_path.read_text())

    # Reconstruct Perturbation objects
    perturbations = []
    for p in manifest["perturbations"]:
        perturbations.append(Perturbation(
            perturbation_id=p["perturbation_id"],
            span_id=p["span_id"],
            category=ErrorCategory(p["category"]),
            original=p["original"],
            perturbed=p["perturbed"],
            why_wrong=p["why_wrong"],
            difficulty=Difficulty(p.get("difficulty", "local")),
            support_span_ids=p.get("support_span_ids", []),
        ))

    # Extract comments from review JSON (handles viz format)
    comments = []
    if "methods" in review_data:
        for method_data in review_data["methods"].values():
            comments.extend(method_data.get("comments", []))
    elif isinstance(review_data, list):
        comments = review_data
    else:
        comments = review_data.get("comments", [])

    print(f"Scoring {len(comments)} comments against {len(perturbations)} perturbations...")

    # Load clean paper for fuzzy matching if available
    clean_path = manifest_path.parent / manifest_path.name.replace("_perturbations.json", "_clean.md")
    paper_text = clean_path.read_text() if clean_path.exists() else ""

    result = score_review(
        perturbations, comments, paper_text,
        model=args.model,
        use_llm=not args.no_llm,
    )

    print(f"\n{'='*50}")
    print(f"PERTURBATION BENCHMARK RESULTS")
    print(f"{'='*50}")
    print(f"Paper: {manifest.get('paper_title', 'unknown')}")
    print(f"Perturbations injected: {result.n_injected}")
    print(f"Perturbations detected: {result.n_detected}")
    print(f"Recall: {result.recall:.1%}")
    print(f"Total comments: {result.n_total_comments}")
    print(f"False positives: {result.n_false_positives}")
    print(f"False positive rate: {result.false_positive_rate:.1%}")

    if result.by_category:
        print(f"\nBy category:")
        for cat, stats in result.by_category.items():
            print(f"  {cat}: {stats['detected']}/{stats['injected']} "
                  f"(recall={stats['recall']:.0%})")

    if result.missed:
        print(f"\nMissed perturbations:")
        pid_lookup = {p.perturbation_id: p for p in perturbations}
        for pid in result.missed:
            p = pid_lookup[pid]
            print(f"  [{p.category.value}] {pid}: {p.original[:60]}... -> {p.perturbed[:60]}...")

    # Save results
    output_path = manifest_path.parent / manifest_path.name.replace(
        "_perturbations.json", "_score.json"
    )
    score_data = {
        "n_injected": result.n_injected,
        "n_detected": result.n_detected,
        "recall": result.recall,
        "n_total_comments": result.n_total_comments,
        "n_false_positives": result.n_false_positives,
        "false_positive_rate": result.false_positive_rate,
        "detected": result.detected,
        "missed": result.missed,
        "by_category": result.by_category,
    }
    output_path.write_text(json.dumps(score_data, indent=2))
    print(f"\nResults saved to: {output_path}")


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

    # perturb subcommand
    perturb_parser = subparsers.add_parser(
        "perturb", help="Generate seeded perturbations for a paper"
    )
    perturb_parser.add_argument(
        "file", help="Path to paper file or arXiv URL"
    )
    perturb_parser.add_argument(
        "--model", default=DEFAULT_MODEL,
        help="Model for perturbation generation (default: anthropic/claude-opus-4-6)",
    )
    perturb_parser.add_argument(
        "--n-per-category", type=int, default=2,
        help="Target perturbations per error category (default: 2)",
    )
    perturb_parser.add_argument(
        "--n-freeform", type=int, default=4,
        help="Number of free-form proposals in stage 2 (default: 4)",
    )
    perturb_parser.add_argument(
        "--output-dir", default="./perturbation_results",
        help="Directory for output files (default: ./perturbation_results)",
    )
    perturb_parser.add_argument(
        "--reasoning-effort",
        choices=["none", "low", "medium", "high"],
        default=None,
        help="Reasoning effort level",
    )
    perturb_parser.add_argument(
        "--skip-stage2", action="store_true",
        help="Skip free-form stage 2 (only use extracted candidates)",
    )

    # score subcommand
    score_parser = subparsers.add_parser(
        "score", help="Score a review against injected perturbations"
    )
    score_parser.add_argument(
        "manifest", help="Path to perturbation manifest JSON"
    )
    score_parser.add_argument(
        "review", help="Path to review results JSON"
    )
    score_parser.add_argument(
        "--model", default="anthropic/claude-sonnet-4-20250514",
        help="Model for LLM-based matching (default: claude-sonnet)",
    )
    score_parser.add_argument(
        "--no-llm", action="store_true",
        help="Use fuzzy matching only (no LLM calls)",
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
    elif args.command == "serve":
        cmd_serve(args)
    elif args.command == "perturb":
        cmd_perturb(args)
    elif args.command == "score":
        cmd_score(args)
    elif args.command == "install-skill":
        cmd_install_skill(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
