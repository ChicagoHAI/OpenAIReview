"""Validate perturbations before injection.

Checks:
1. Perturbed text differs from original
2. No two perturbations target overlapping text spans
3. Replacement won't create garbled text at boundaries
"""

from .models import Perturbation

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
) -> tuple[list[Perturbation], list[tuple[Perturbation, str]]]:
    """Validate perturbations against the paper text.

    Returns (valid, rejected) where rejected is a list of (perturbation, reason).
    """
    valid: list[Perturbation] = []
    rejected: list[tuple[Perturbation, str]] = []
    # Track occupied character ranges to prevent overlaps
    occupied: list[tuple[int, int]] = []

    for p in perturbations:
        idx = p.offset

        # Check 1: perturbed differs from original
        if p.original == p.perturbed:
            rejected.append((p, "perturbed text is identical to original"))
            continue

        # Check 2: no overlapping spans
        span_end = idx + len(p.original)
        overlap = False
        for occ_start, occ_end in occupied:
            if idx < occ_end and span_end > occ_start:
                overlap = True
                break
        if overlap:
            rejected.append((p, f"overlaps with an already-selected perturbation at [{idx}:{span_end}]"))
            continue

        # Check 3: replacement won't create garbled text
        if _replacement_creates_garbage(paper_text, idx, p.original, p.perturbed):
            rejected.append((p, "replacement would create garbled text at boundaries"))
            continue

        occupied.append((idx, span_end))
        valid.append(p)

    return valid, rejected