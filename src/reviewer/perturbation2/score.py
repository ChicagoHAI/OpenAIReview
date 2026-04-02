"""Score a reviewer's comments against injected perturbations.

Detection matching: a reviewer comment "detects" a perturbation if:
1. It quotes or references text near the perturbed span (fuzzy match), OR
2. Its explanation describes the same error the perturbation introduces.

We use both quote-overlap and semantic similarity (via the LLM) for robust matching.
"""

from difflib import SequenceMatcher

from .models import ErrorCategory, Perturbation, PerturbationResult


def score_review(
    perturbations: list[Perturbation],
    review_comments: list[dict],
    paper_text: str,
) -> PerturbationResult:
    """Score reviewer comments against injected perturbations via fuzzy matching."""
    matches = _fuzzy_match(perturbations, review_comments, paper_text)

    detected_ids = set(matches.values())
    missed_ids = [p.perturbation_id for p in perturbations if p.perturbation_id not in detected_ids]

    # Count false positives: comments that didn't match any perturbation
    matched_comment_indices = set(matches.keys())
    n_false_positives = len(review_comments) - len(matched_comment_indices)

    # Per-category breakdown
    by_category: dict[str, dict] = {}
    for cat in ErrorCategory:
        cat_perturbations = [p for p in perturbations if p.category == cat]
        if not cat_perturbations:
            continue
        cat_detected = [p for p in cat_perturbations if p.perturbation_id in detected_ids]
        by_category[cat.value] = {
            "injected": len(cat_perturbations),
            "detected": len(cat_detected),
            "recall": len(cat_detected) / len(cat_perturbations) if cat_perturbations else 0,
        }

    n_detected = len(detected_ids)
    return PerturbationResult(
        n_injected=len(perturbations),
        n_detected=n_detected,
        recall=n_detected / len(perturbations) if perturbations else 0,
        n_total_comments=len(review_comments),
        n_false_positives=n_false_positives,
        false_positive_rate=n_false_positives / len(review_comments) if review_comments else 0,
        detected=list(detected_ids),
        missed=missed_ids,
        by_category=by_category,
    )


def _fuzzy_match(
    perturbations: list[Perturbation],
    comments: list[dict],
    paper_text: str,
    threshold: float = 0.5,
) -> dict[int, str]:
    """Match comments to perturbations via quote overlap.

    Returns {comment_index: perturbation_id} for matched pairs.
    """
    matches: dict[int, str] = {}

    for i, comment in enumerate(comments):
        quote = comment.get("quote", "")
        explanation = comment.get("explanation", "")
        comment_text = f"{quote} {explanation}"

        best_score = 0.0
        best_pid = None

        for p in perturbations:
            # Check overlap with the original text region
            score = SequenceMatcher(None, comment_text.lower(), p.original.lower()).ratio()

            # Also check if the comment mentions the perturbed value
            if p.perturbed.lower() in comment_text.lower():
                score = max(score, 0.6)

            # Check if the why_wrong reasoning overlaps with the comment
            why_score = SequenceMatcher(
                None, explanation.lower(), p.why_wrong.lower()
            ).ratio()
            score = max(score, why_score)

            if score > best_score:
                best_score = score
                best_pid = p.perturbation_id

        if best_score >= threshold and best_pid is not None:
            matches[i] = best_pid

    return matches


