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
_BENCHMARKS_DIR = Path(__file__).parent.parent.parent / "benchmarks"
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

    # Build viz-compatible data. For `progressive`, also save the
    # pre-consolidation comments under a separate `progressive_original__*`
    # method key so we can compare raw vs consolidated counts later.
    method_blocks: list[tuple[str, str, object]] = []
    key = _method_key(method, args.model)
    method_blocks.append((method, key, result))

    if method == "progressive":
        full.method = "progressive_original"
        orig_key = _method_key("progressive_original", args.model)
        print(f"  Pre-consolidation: {full.num_comments} comments "
              f"(saved as {orig_key})")
        method_blocks.append(("progressive_original", orig_key, full))

    # Build first block as the base paper_data, then attach extras.
    base_method, base_key, base_result = method_blocks[0]
    paper_data = _build_paper_json(
        slug, title, paragraphs, base_method, base_key, base_result, was_ocr
    )
    for extra_method, extra_key, extra_result in method_blocks[1:]:
        extra_data = _build_paper_json(
            slug, title, paragraphs, extra_method, extra_key, extra_result, was_ocr
        )
        paper_data["methods"][extra_key] = extra_data["methods"][extra_key]

    # Merge with existing file if present
    if output_file.exists():
        try:
            existing = json.loads(output_file.read_text())
            for _m, k, _r in method_blocks:
                existing["methods"][k] = paper_data["methods"][k]
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


def cmd_perturb(args: argparse.Namespace) -> None:
    """Generate seeded perturbations for a paper."""
    from .parsers import is_url, parse_document
    if str(_BENCHMARKS_DIR) not in sys.path:
        sys.path.insert(0, str(_BENCHMARKS_DIR))
    from perturbation import (
        extract_candidates,
        generate_perturbations,
        inject_perturbations,
        validate_perturbations,
        verify_perturbations,
    )

    source = args.file
    if is_url(source):
        print(f"Fetching and parsing URL...")
        title, content, _ = parse_document(source)
        slug = source.rstrip("/").split("/")[-1]
    else:
        file_path = Path(source)
        if not file_path.exists():
            print(f"Error: file not found: {file_path}", file=sys.stderr)
            sys.exit(1)
        print(f"Parsing {file_path.name}...")
        title, content, _ = parse_document(file_path)
        slug = slugify(file_path.stem)

    print(f"  Title: {title}")
    print(f"  Length: {len(content):,} chars")
    print(f"  Context mode: {args.context_mode} (window={args.context_window}, "
          f"related_passages_max={args.related_passages_max})")
    print(f"  Substantive guidance: {'on' if args.substantive_guidance else 'off'}")

    # Stage 0: Extract candidates
    print("\nStage 0: Extracting candidate spans...")
    candidates = extract_candidates(
        content,
        args.error_type,
        context_mode=args.context_mode,
        context_window=args.context_window,
        related_passages_max=args.related_passages_max,
    )
    print(f"  {len(candidates)} candidates found")

    from collections import Counter
    type_counts = Counter(c.span_type.value for c in candidates)
    for t, n in type_counts.most_common():
        print(f"    {t}: {n}")

    if args.context_mode == "related":
        n_with_related = sum(1 for c in candidates if c.related_passages)
        print(f"  Candidates with related_passages: {n_with_related}/{len(candidates)}")

    reasoning = getattr(args, "reasoning_effort", None)

    # Stage 1: Generate perturbations
    print(f"\nGenerating perturbations...")
    perturbations, gen_stats = generate_perturbations(
        candidates,
        model=args.model,
        n_per_error=args.n_per_error,
        reasoning_effort=reasoning,
        error_type=args.error_type,
        return_stats=True,
        context_mode=args.context_mode,
        substantive_guidance=args.substantive_guidance,
    )

    # Stage 2: Structural validation (tests 1–4)
    print(f"\nValidating {len(perturbations)} perturbations (tests 1–4)...")
    valid, rejected = validate_perturbations(perturbations, content)
    print(f"  Valid: {len(valid)}, Rejected: {len(rejected)}")

    # Tally per-test rejection reasons (best-effort, via substring match).
    rejected_by_test = {
        "test1_original_not_found": 0,
        "test2_unchanged": 0,
        "test3_overlap": 0,
        "test4_garbled": 0,
    }
    for p, reason in rejected:
        if "original text not found" in reason:
            rejected_by_test["test1_original_not_found"] += 1
        elif "identical to original" in reason:
            rejected_by_test["test2_unchanged"] += 1
        elif "overlaps" in reason:
            rejected_by_test["test3_overlap"] += 1
        elif "garbled" in reason:
            rejected_by_test["test4_garbled"] += 1
        print(f"    REJECTED {p.perturbation_id}: {reason[:80]}")

    # Stage 3: Verifier validation (test 5) — only if enabled
    verifier_stats = {
        "n_input": 0, "substantive": 0, "typo-shaped": 0,
        "not-an-error": 0, "parse-error": 0,
    }
    verifier_rejected: list[tuple] = []
    if args.skip_verifier:
        print(f"\nVerifier: SKIPPED (--skip-verifier)")
        accepted = valid
    else:
        accepted, verifier_rejected, verifier_stats = verify_perturbations(
            valid,
            candidates,
            model=args.verifier_model,
            reasoning_effort=args.verifier_reasoning,
            max_workers=args.verifier_max_workers,
        )
        for p, v in verifier_rejected:
            print(f"    VERIFIER REJECTED {p.perturbation_id} [{v.verdict}]: {v.reason[:100]}")

    # Inject
    corrupted, applied = inject_perturbations(content, accepted)
    print(f"\nInjected {len(applied)} perturbations")

    # Save outputs
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    n_generated = len(perturbations)
    n_candidates = len(candidates)
    generation_yield = (n_generated / n_candidates) if n_candidates else 0.0
    if not valid:
        verifier_acceptance_rate = 0.0
    elif args.skip_verifier:
        verifier_acceptance_rate = 1.0
    else:
        verifier_acceptance_rate = len(applied) / len(valid)
    acceptance_rate = (len(applied) / n_generated) if n_generated else 0.0

    # Save perturbation manifest
    manifest = {
        "paper_title": title,
        "paper_slug": slug,
        "n_candidates": n_candidates,
        "n_generated": n_generated,
        "n_valid_structural": len(valid),
        "n_accepted_by_verifier": len(applied) if not args.skip_verifier else None,
        "n_injected": len(applied),
        "generation_yield": generation_yield,
        "verifier_acceptance_rate": verifier_acceptance_rate,
        "acceptance_rate": acceptance_rate,  # n_injected / n_generated (end-to-end)
        "model": args.model,
        "context_mode": args.context_mode,
        "substantive_guidance": args.substantive_guidance,
        "context_window": args.context_window,
        "related_passages_max": args.related_passages_max,
        "generator_stats": gen_stats,
        "rejection_counts": {
            **rejected_by_test,
            "test5_verifier_typo_shaped": verifier_stats.get("typo-shaped", 0),
            "test5_verifier_not_an_error": verifier_stats.get("not-an-error", 0),
            "test5_verifier_parse_error": verifier_stats.get("parse-error", 0),
        },
        "verifier": {
            "enabled": not args.skip_verifier,
            "model": args.verifier_model,
            "reasoning_effort": args.verifier_reasoning,
            **verifier_stats,
        },
        "perturbations": [
            {
                "perturbation_id": p.perturbation_id,
                "span_id": p.span_id,
                "error": p.error.value,
                "original": p.original,
                "perturbed": p.perturbed,
                "why_wrong": p.why_wrong,
                "contradicts_quote": p.contradicts_quote,
            }
            for p in applied
        ],
    }

    manifest_path = output_dir / f"{slug}_perturbations.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"\nManifest saved to: {manifest_path}")

    # Summary table
    print("\n" + "=" * 60)
    print(f"ACCEPTANCE SUMMARY ({args.context_mode} mode)")
    print("=" * 60)
    print(f"  Candidates:                        {n_candidates}")
    print(f"  Generated:                         {n_generated}  "
          f"(generation yield: {generation_yield:.1%} of candidates)")
    print(f"  Rejected (test 1 not-found):       {rejected_by_test['test1_original_not_found']}")
    print(f"  Rejected (test 2 unchanged):       {rejected_by_test['test2_unchanged']}")
    print(f"  Rejected (test 3 overlap):         {rejected_by_test['test3_overlap']}")
    print(f"  Rejected (test 4 garbled):         {rejected_by_test['test4_garbled']}")
    if not args.skip_verifier:
        print(f"  Rejected (test 5 typo-shaped):     {verifier_stats['typo-shaped']}")
        print(f"  Rejected (test 5 not-an-error):    {verifier_stats['not-an-error']}")
        print(f"  Rejected (test 5 parse-error):     {verifier_stats['parse-error']}")
        qs = verifier_stats.get('quote_source', {}) or {}
        print(f"  Quote source: generator={qs.get('generator', 0)}  "
              f"random-sampled={qs.get('random-sampled', 0)}  "
              f"none-available={qs.get('none-available', 0)}")
    print(f"  Accepted (injected):               {len(applied)}")
    print(f"  End-to-end acceptance rate:        {acceptance_rate:.1%}  "
          f"(verifier acceptance: {verifier_acceptance_rate:.1%})")

    # Save corrupted paper
    corrupted_path = output_dir / f"{slug}_corrupted.md"
    corrupted_path.write_text(corrupted)
    print(f"\nCorrupted paper saved to: {corrupted_path}")

    # Save clean paper for reference
    clean_path = output_dir / f"{slug}_clean.md"
    clean_path.write_text(content)
    print(f"Clean paper saved to: {clean_path}")

    print(f"\nDone. Run a review on the corrupted paper, then score with:")
    print(f"  openaireview score {manifest_path} <review_results.json>")


def cmd_score(args: argparse.Namespace) -> None:
    """Score a review against injected perturbations."""
    if str(_BENCHMARKS_DIR) not in sys.path:
        sys.path.insert(0, str(_BENCHMARKS_DIR))
    from perturbation.models import Error, Perturbation
    from perturbation.score import score_review

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

    # Reconstruct Perturbation objects (contradicts_quote is optional for
    # backwards compatibility with pre-verifier manifests).
    perturbations = []
    for p in manifest["perturbations"]:
        perturbations.append(Perturbation(
            perturbation_id=p["perturbation_id"],
            span_id=p["span_id"],
            error=Error(p["error"]),
            original=p["original"],
            perturbed=p["perturbed"],
            why_wrong=p["why_wrong"],
            contradicts_quote=p.get("contradicts_quote", ""),
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

    result = score_review(perturbations, comments, model=args.model, method=args.method)

    print(f"\n{'='*50}")
    print(f"PERTURBATION BENCHMARK RESULTS")
    print(f"{'='*50}")
    print(f"Paper: {manifest.get('paper_title', 'unknown')}")
    print(f"Perturbations injected: {result.n_injected}")
    print(f"Perturbations detected: {result.n_detected}")
    print(f"Recall: {result.recall:.1%}")
    print(f"Total comments: {result.n_total_comments}")

    if result.missed:
        print(f"\nMissed perturbations:")
        pid_lookup = {p.perturbation_id: p for p in perturbations}
        for pid in result.missed:
            p = pid_lookup[pid]
            print(f"  [{p.error.value}] {pid}: {p.original[:60]}... -> {p.perturbed[:60]}...")

    # Save results
    score_filename = manifest_path.name.replace("_perturbations.json", "_score.json")
    output_dir = Path(args.output_dir) if args.output_dir else manifest_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / score_filename
    score_data = {
        "n_injected": result.n_injected,
        "n_detected": result.n_detected,
        "recall": result.recall,
        "n_total_comments": result.n_total_comments,
        "detected": result.detected,
        "missed": result.missed,
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
        "--n-per-error", type=int, default=2,
        help="Target perturbations per error category (default: 2)",
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
        "--error_type", default="all",
        help="Error type (default: all)",
    )
    perturb_parser.add_argument(
        "--context-mode",
        choices=["none", "window", "related"],
        default="window",
        help="How to supply context to the generator: 'none' (no context), "
             "'window' (current ±200-char behavior), 'related' (window + "
             "whole-paper related passages). Default: window.",
    )
    perturb_parser.add_argument(
        "--context-window", type=int, default=200,
        help="Width of the ±context window in characters (default: 200). "
             "Used when --context-mode is 'window' or 'related'.",
    )
    substantive_guidance_group = perturb_parser.add_mutually_exclusive_group()
    substantive_guidance_group.add_argument(
        "--substantive-guidance",
        dest="substantive_guidance",
        action="store_true",
        help="Explicitly teach the generator the typo-shaped vs substantive-error distinction "
             "(default: enabled).",
    )
    substantive_guidance_group.add_argument(
        "--no-substantive-guidance",
        dest="substantive_guidance",
        action="store_false",
        help="Disable the explicit typo-shaped vs substantive-error guidance and use a neutral prompt.",
    )
    perturb_parser.set_defaults(substantive_guidance=True)
    perturb_parser.add_argument(
        "--related-passages-max", type=int, default=5,
        help="Maximum number of related passages attached per candidate when "
            "--context-mode is 'related' (default: 5).",
    )
    perturb_parser.add_argument(
        "--verifier-model", default="anthropic/claude-sonnet-4-6",
        help="Model used by the substantive-error verifier (test #5). "
             "Default: anthropic/claude-sonnet-4-6.",
    )
    perturb_parser.add_argument(
        "--verifier-reasoning",
        choices=["none", "low", "medium", "high"],
        default="none",
        help="Reasoning effort for the verifier (default: none).",
    )
    perturb_parser.add_argument(
        "--verifier-max-workers", type=int, default=8,
        help="Parallel worker count for verifier fan-out (default: 8).",
    )
    perturb_parser.add_argument(
        "--skip-verifier", action="store_true",
        help="Skip the substantive-error verifier (test #5). Structural tests "
             "1–4 still run.",
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
        "--model", default=DEFAULT_MODEL,
        help="Model for explanation matching (default: anthropic/claude-opus-4-6)",
    )
    score_parser.add_argument(
        "--output-dir", default=None,
        help="Directory to save score JSON (default: same directory as manifest)",
    )
    score_parser.add_argument(
        "--method", choices=["llm", "fuzzy", "semantic"], default="llm",
        help="Score method (default: llm)",
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
