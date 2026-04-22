"""Inject perturbations into a clean paper to create a corrupted version.

Each perturbation replaces one span at its recorded offset. Replacements
are applied from right to left (highest offset first) so earlier offsets
stay valid.
"""

from .models import Perturbation

def inject_perturbations(
    paper_text: str,
    perturbations: list[Perturbation],
) -> tuple[str, list[Perturbation]]:
    """Apply perturbations to produce a corrupted paper.

    Returns (corrupted_text, applied) where applied lists the perturbations
    in document order.
    """
    # Sort by offset descending so replacements don't shift earlier positions
    ordered = sorted(perturbations, key=lambda p: p.offset, reverse=True)

    corrupted = paper_text
    applied: list[Perturbation] = []

    for p in ordered:
        end = p.offset + len(p.original)
        corrupted = corrupted[:p.offset] + p.perturbed + corrupted[end:]
        applied.append(p)

    # Return in document order (ascending offset)
    applied.reverse()
    return corrupted, applied
