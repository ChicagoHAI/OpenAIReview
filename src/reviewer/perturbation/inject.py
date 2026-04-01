"""Inject perturbations into a clean paper to create a corrupted version.

Each perturbation replaces one exact substring. Replacements are applied
from right to left (highest offset first) so earlier offsets stay valid.
"""

from .models import Perturbation


def inject_perturbations(
    paper_text: str,
    perturbations: list[Perturbation],
) -> tuple[str, list[Perturbation]]:
    """Apply perturbations to produce a corrupted paper.

    Returns (corrupted_text, applied) where applied lists the perturbations
    that were successfully injected. Perturbations whose original text
    isn't found are silently skipped.
    """
    # Locate each perturbation's offset
    located: list[tuple[int, Perturbation]] = []
    for p in perturbations:
        idx = paper_text.find(p.original)
        if idx == -1:
            continue
        located.append((idx, p))

    # Sort by offset descending so replacements don't shift earlier positions
    located.sort(key=lambda x: x[0], reverse=True)

    corrupted = paper_text
    applied: list[Perturbation] = []

    for idx, p in located:
        end = idx + len(p.original)
        corrupted = corrupted[:idx] + p.perturbed + corrupted[end:]
        applied.append(p)

    # Return in document order (ascending offset)
    applied.reverse()
    return corrupted, applied
