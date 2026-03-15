"""Seeded-perturbation benchmark for the reviewer.

Takes a clean OCR'd paper and injects known errors of different types.
Then runs the reviewer and measures recall (caught / injected) and
false positive rate (hallucinated issues / total comments).

Usage:
    uv run python benchmarks/seed_errors.py [--review]
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SeededError:
    """A known error injected into the paper."""
    id: str
    category: str  # sign_flip, subscript_swap, parameter, claim, definition
    original: str
    perturbed: str
    location_hint: str  # human-readable description
    line_approx: int | None = None  # approximate line number after injection


# ── Error definitions (Nakamura & Steinsson 2018) ──────────────────────────

ERRORS: list[SeededError] = [
    # 1. Sign flip in Euler equation (eq 2)
    SeededError(
        id="sign_euler",
        category="sign_flip",
        original=r"(\hat{i} _ {t} - E _ {t} \hat {\pi} _ {t + 1} - \hat {r} _ {t} ^ {n})",
        perturbed=r"(\hat{i} _ {t} + E _ {t} \hat {\pi} _ {t + 1} - \hat {r} _ {t} ^ {n})",
        location_hint="Euler equation (2): minus before E_t pi should not be plus",
    ),
    # 2. Subscript swap in marginal utility gap definition
    SeededError(
        id="subscript_gap",
        category="subscript_swap",
        original=r"$\hat{\lambda}_{xt} = \hat{\lambda}_t - \hat{\lambda}_t^n$",
        perturbed=r"$\hat{\lambda}_{xt} = \hat{\lambda}_t - \hat{\lambda}_s^n$",
        location_hint="Definition of marginal utility gap: lambda_t^n changed to lambda_s^n",
    ),
    # 3. Wrong parameter value: beta = 0.99 changed to 0.95
    SeededError(
        id="param_beta",
        category="parameter",
        original=r"$\beta = 0.99$",
        perturbed=r"$\beta = 0.95$",
        location_hint="Calibration: discount factor changed from 0.99 to 0.95",
    ),
    # 4. Wrong parameter value: sigma = 0.5 changed to 5
    SeededError(
        id="param_sigma",
        category="parameter",
        original=r"$\sigma = 0.5$",
        perturbed=r"$\sigma = 5$",
        location_hint="Calibration: IES changed from 0.5 to 5 (huge difference)",
    ),
    # 5. Wrong parameter: habit b = 0.9 changed to 0.09
    SeededError(
        id="param_habit",
        category="parameter",
        original=r"$b = 0.9$",
        perturbed=r"$b = 0.09$",
        location_hint="Calibration: habit parameter changed from 0.9 to 0.09",
    ),
    # 6. Sign flip in habits equation (eq 4): minus on leading term
    SeededError(
        id="sign_habits",
        category="sign_flip",
        original=r"-(1 + b^2 \beta) \sigma_c \hat{x}_t",
        perturbed=r"(1 + b^2 \beta) \sigma_c \hat{x}_t",
        location_hint="Equation (4): leading minus sign removed",
    ),
    # 7. Overstated claim: "large and persistent" -> "permanent"
    SeededError(
        id="claim_persistent",
        category="claim",
        original="large and persistent effects on real interest rates",
        perturbed="permanent effects on real interest rates",
        location_hint="Section III summary: 'persistent' overstated to 'permanent'",
    ),
    # 8. Definition inconsistency: output gap uses wrong variable
    SeededError(
        id="def_output_gap",
        category="definition",
        original=r"$\hat{x} = \hat{y}_t - \hat{y}_t^n$",
        perturbed=r"$\hat{x} = \hat{c}_t - \hat{y}_t^n$",
        location_hint="Output gap definition: y_t changed to c_t (consumption, not output)",
    ),
    # 9. Wrong fraction in information effect
    SeededError(
        id="info_fraction",
        category="definition",
        original=r"A fraction $\psi$ of the shock shows up as an information effect, while a fraction $1 - \psi$",
        perturbed=r"A fraction $\psi$ of the shock shows up as an information effect, while a fraction $1 + \psi$",
        location_hint="Information effect: 1-psi changed to 1+psi (fractions don't sum to 1)",
    ),
    # 10. Wrong labor share: 2/3 -> 1/3
    SeededError(
        id="param_labor_share",
        category="parameter",
        original=r"a labor share of $\frac{2}{3}$",
        perturbed=r"a labor share of $\frac{1}{3}$",
        location_hint="Calibration: labor share changed from 2/3 to 1/3",
    ),
    # 11. Phillips curve coefficient: kappa*omega -> kappa/omega
    SeededError(
        id="coeff_phillips",
        category="sign_flip",
        original=r"\kappa \omega \hat {\zeta} \hat {x} _ {t}",
        perturbed=r"\frac{\kappa}{\omega} \hat {\zeta} \hat {x} _ {t}",
        location_hint="Phillips curve (3): kappa*omega changed to kappa/omega",
    ),
    # 12. Taylor rule coefficient: phi_pi = 0.01 -> 1.5
    SeededError(
        id="param_taylor",
        category="parameter",
        original=r"$\phi_{\pi} = 0.01$",
        perturbed=r"$\phi_{\pi} = 1.5$",
        location_hint="Taylor rule: phi_pi changed from 0.01 to 1.5 (very different policy stance)",
    ),
]


def inject_errors(clean_text: str, errors: list[SeededError] | None = None) -> tuple[str, list[SeededError]]:
    """Inject seeded errors into the text. Returns (perturbed_text, injected_errors)."""
    if errors is None:
        errors = ERRORS

    text = clean_text
    injected = []
    for err in errors:
        if err.original in text:
            text = text.replace(err.original, err.perturbed, 1)
            injected.append(err)
        else:
            print(f"  WARNING: could not find target for {err.id}: {err.original[:60]}...")

    return text, injected


def check_detections(
    injected: list[SeededError],
    comments: list[dict],
    verbose: bool = True,
) -> dict:
    """Match reviewer comments against injected errors.

    A comment is considered a "hit" if its quote or explanation contains
    text that overlaps with the perturbed region.
    """
    hits = set()
    matched_comments = set()

    for err in injected:
        # Build search terms from both the perturbed text and key identifiers
        search_terms = [
            err.perturbed[:50],
            err.id.replace("_", " "),
        ]
        # Also add specific keywords from the location hint
        for kw in re.findall(r'\b\w{4,}\b', err.location_hint):
            search_terms.append(kw.lower())

        for ci, comment in enumerate(comments):
            quote = comment.get("quote", "").lower()
            explanation = comment.get("explanation", "").lower()
            combined = f"{quote} {explanation}"

            # Check if the comment references the perturbed region
            score = 0
            for term in search_terms:
                if term.lower() in combined:
                    score += 1
            if score >= 2:  # need at least 2 matching terms
                hits.add(err.id)
                matched_comments.add(ci)
                break

    n_injected = len(injected)
    n_detected = len(hits)
    n_total_comments = len(comments)
    n_false_positives = n_total_comments - len(matched_comments)

    result = {
        "n_injected": n_injected,
        "n_detected": n_detected,
        "recall": n_detected / n_injected if n_injected else 0,
        "n_total_comments": n_total_comments,
        "n_false_positives": n_false_positives,
        "false_positive_rate": n_false_positives / n_total_comments if n_total_comments else 0,
        "detected": sorted(hits),
        "missed": sorted(set(e.id for e in injected) - hits),
        "by_category": {},
    }

    # Breakdown by category
    for cat in set(e.category for e in injected):
        cat_errors = [e for e in injected if e.category == cat]
        cat_hits = [e for e in cat_errors if e.id in hits]
        result["by_category"][cat] = {
            "injected": len(cat_errors),
            "detected": len(cat_hits),
            "recall": len(cat_hits) / len(cat_errors) if cat_errors else 0,
        }

    if verbose:
        print(f"\n{'='*60}")
        print(f"BENCHMARK RESULTS")
        print(f"{'='*60}")
        print(f"Injected errors:   {n_injected}")
        print(f"Detected:          {n_detected} ({result['recall']:.0%})")
        print(f"Missed:            {n_injected - n_detected}")
        print(f"Total comments:    {n_total_comments}")
        print(f"False positives:   {n_false_positives} ({result['false_positive_rate']:.0%})")
        print(f"\nBy category:")
        for cat, stats in sorted(result["by_category"].items()):
            print(f"  {cat:20s}: {stats['detected']}/{stats['injected']} ({stats['recall']:.0%})")
        print(f"\nDetected: {', '.join(result['detected']) or 'none'}")
        print(f"Missed:   {', '.join(result['missed']) or 'none'}")
        print(f"{'='*60}")

    return result


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Seeded-perturbation benchmark")
    parser.add_argument(
        "--input",
        default="examples/nakamura_extracted_v2/nakamura_steinsson_2018.md",
        help="Clean markdown file to perturb",
    )
    parser.add_argument("--review", action="store_true", help="Actually run the reviewer")
    parser.add_argument("--method", default="zero_shot", help="Review method")
    parser.add_argument("--model", default=None, help="Model to use")
    parser.add_argument("--output", default="benchmarks/results", help="Output directory")
    args = parser.parse_args()

    clean_path = Path(args.input)
    if not clean_path.exists():
        print(f"Error: {clean_path} not found")
        return

    clean_text = clean_path.read_text()

    # Strip frontmatter if present
    if clean_text.startswith("---\n"):
        end = clean_text.find("\n---\n", 4)
        if end != -1:
            clean_text = clean_text[end + 5:]

    print(f"Loaded {clean_path.name} ({len(clean_text)} chars)")

    # Inject errors
    perturbed_text, injected = inject_errors(clean_text)
    print(f"Injected {len(injected)}/{len(ERRORS)} errors")

    # Save perturbed version
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    perturbed_path = out_dir / "perturbed_paper.md"
    perturbed_path.write_text(perturbed_text)
    print(f"Saved perturbed paper to {perturbed_path}")

    # Save error manifest
    manifest = [
        {"id": e.id, "category": e.category, "original": e.original,
         "perturbed": e.perturbed, "hint": e.location_hint}
        for e in injected
    ]
    manifest_path = out_dir / "error_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"Saved manifest to {manifest_path}")

    if not args.review:
        print("\nDry run complete. Use --review to run the reviewer on the perturbed paper.")
        print(f"You can also run manually:")
        print(f"  uv run openaireview review {perturbed_path} --method {args.method}")
        return

    # Run the reviewer
    from reviewer.method_zero_shot import review_zero_shot
    from reviewer.method_progressive import review_progressive

    model = args.model or "anthropic/claude-opus-4-6"
    slug = "benchmark-nakamura-perturbed"

    print(f"\nRunning reviewer ({args.method}, {model})...")
    if args.method == "zero_shot":
        result = review_zero_shot(slug, perturbed_text, model=model)
    elif args.method in ("progressive", "progressive_full"):
        consolidated, full = review_progressive(slug, perturbed_text, model=model)
        result = full if args.method == "progressive_full" else consolidated
    else:
        print(f"Unknown method: {args.method}")
        return

    # Extract comments as dicts
    comments = [
        {"title": c.title, "quote": c.quote, "explanation": c.explanation,
         "comment_type": c.comment_type}
        for c in result.comments
    ]

    # Save review output
    review_path = out_dir / f"review_{args.method}.json"
    review_path.write_text(json.dumps({
        "method": args.method,
        "model": model,
        "n_comments": len(comments),
        "comments": comments,
        "prompt_tokens": result.total_prompt_tokens,
        "completion_tokens": result.total_completion_tokens,
    }, indent=2))

    # Score
    scores = check_detections(injected, comments)
    scores_path = out_dir / f"scores_{args.method}.json"
    scores_path.write_text(json.dumps(scores, indent=2))


if __name__ == "__main__":
    main()
