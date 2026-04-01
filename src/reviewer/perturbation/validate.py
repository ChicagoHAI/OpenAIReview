"""Validate perturbations before injection.

Checks:
1. Original text actually exists in the paper (exact match)
2. Perturbed text differs from original
3. No two perturbations target overlapping text spans
4. Each perturbation's category is compatible with its span type
5. Original text isn't truncated mid-expression (unbalanced delimiters)
6. Replacement won't create garbled text at boundaries
"""

from .models import CandidateSpan, Perturbation


def _is_truncated(text: str) -> bool:
    """Check if text appears to be truncated mid-expression."""
    stripped = text.rstrip()
    # Ends with = (mid-equation)
    if stripped.endswith("="):
        return True
    # Unbalanced $ (LaTeX math)
    if stripped.count("$") % 2 != 0:
        return True
    # Unbalanced LaTeX delimiters
    if stripped.count("\\(") != stripped.count("\\)"):
        return True
    if stripped.count("\\[") != stripped.count("\\]"):
        return True
    return False


def _replacement_creates_garbage(
    paper_text: str, idx: int, original: str, perturbed: str,
) -> bool:
    """Check if the replacement would create garbled text at boundaries.

    Catches cases where the perturbed text extends beyond the original
    and collides with the text that follows.
    """
    after = paper_text[idx + len(original):idx + len(original) + 20]
    # If perturbed ends with a closing delimiter but the original didn't,
    # and the next text starts with a continuation, it's garbled
    if perturbed.endswith("$") and not original.endswith("$"):
        # Check if what follows also has $ — would create $$
        if after.lstrip().startswith("$") or after.lstrip().startswith("\\"):
            return True
    return False


def validate_perturbations(
    perturbations: list[Perturbation],
    paper_text: str,
    candidates: list[CandidateSpan] | None = None,
) -> tuple[list[Perturbation], list[tuple[Perturbation, str]]]:
    """Validate perturbations against the paper text.

    Returns (valid, rejected) where rejected is a list of (perturbation, reason).
    """
    span_lookup = {c.span_id: c for c in candidates} if candidates else {}
    valid: list[Perturbation] = []
    rejected: list[tuple[Perturbation, str]] = []
    # Track occupied character ranges to prevent overlaps
    occupied: list[tuple[int, int]] = []

    for p in perturbations:
        # Check 1: original exists in paper
        idx = paper_text.find(p.original)
        if idx == -1:
            rejected.append((p, f"original text not found in paper: {p.original[:80]}..."))
            continue

        # Check 2: perturbed differs from original
        if p.original == p.perturbed:
            rejected.append((p, "perturbed text is identical to original"))
            continue

        # Check 3: no overlapping spans
        span_end = idx + len(p.original)
        overlap = False
        for occ_start, occ_end in occupied:
            if idx < occ_end and span_end > occ_start:
                overlap = True
                break
        if overlap:
            rejected.append((p, f"overlaps with an already-selected perturbation at [{idx}:{span_end}]"))
            continue

        # Check 4: category compatible with span type (if we have candidate info)
        if p.span_id in span_lookup:
            span = span_lookup[p.span_id]
            if p.category not in span.compatible_categories:
                rejected.append((
                    p,
                    f"category {p.category.value} not compatible with span type {span.span_type.value}",
                ))
                continue

        # Check 5: original isn't truncated mid-expression
        if _is_truncated(p.original):
            rejected.append((p, f"original appears truncated: ...{p.original[-40:]}"))
            continue

        # Check 6: replacement won't create garbled text
        if _replacement_creates_garbage(paper_text, idx, p.original, p.perturbed):
            rejected.append((p, "replacement would create garbled text at boundaries"))
            continue

        occupied.append((idx, span_end))
        valid.append(p)

    return valid, rejected
