"""Post-OCR consistency check: detect and fix likely OCR errors in math notation."""

import re
from collections import Counter


def fix_ocr_notation(text: str) -> tuple[str, list[dict]]:
    """Detect and fix likely OCR errors in LaTeX math notation.

    Finds math symbols that appear only once and have a high-frequency
    near-neighbor (same LaTeX command, different letter), then replaces
    the singleton with the frequent variant.

    Returns (fixed_text, list of corrections applied).
    """
    corrections = []

    # LaTeX accent commands that take a single-letter argument
    _ACCENT_CMDS = r'hat|tilde|bar|dot|ddot|vec|check'

    # Match \hat{x}, \hat {x}, \hat { x }, \hat x (no braces) patterns
    accent_pattern = re.compile(
        rf'(\\(?:{_ACCENT_CMDS}))\s*'
        rf'(?:\{{\s*(\w)\s*\}}|(\w))'
    )

    # Count occurrences of each (command, letter) pair
    cmd_letter_counts: Counter[tuple[str, str]] = Counter()
    for match in accent_pattern.finditer(text):
        cmd = match.group(1)
        letter = match.group(2) or match.group(3)
        cmd_letter_counts[(cmd, letter)] += 1

    # Find rare symbols that have a more-frequent visually-similar neighbor.
    # Heuristic: if symbol A appears ≤1 time and symbol B appears ≥2x more
    # with the same accent command, and they're visually confusable, fix A→B.
    for (cmd, letter), count in list(cmd_letter_counts.items()):
        if count > 1:
            continue
        for (other_cmd, other_letter), other_count in cmd_letter_counts.items():
            if other_cmd != cmd or other_letter == letter:
                continue
            if other_count < 2 * count:
                continue
            if not _visually_similar(letter, other_letter):
                continue

            # Build all whitespace variants the OCR might have produced
            old_variants = [
                f'{cmd}{{{letter}}}',          # \hat{t}
                f'{cmd} {{{letter}}}',          # \hat {t}
                f'{cmd} {{ {letter} }}',        # \hat { t }
                f'{cmd}{{{letter} }}',          # \hat{t }
                f'{cmd}{{ {letter}}}',          # \hat{ t}
            ]
            canonical = f'{cmd}{{{other_letter}}}'
            for old in old_variants:
                if old in text:
                    text = text.replace(old, canonical)
                    corrections.append({
                        'old': old,
                        'new': canonical,
                        'reason': f'{cmd}{{{letter}}} appears {count}x '
                                  f'but {cmd}{{{other_letter}}} appears {other_count}x '
                                  f'— likely OCR misread',
                    })
                    break

    return text, corrections


# Pairs of characters commonly confused by OCR engines
_CONFUSABLE_PAIRS = {
    frozenset({'i', 't'}),  # î vs t̂
    frozenset({'i', 'l'}),  # i vs l
    frozenset({'l', '1'}),  # l vs 1
    frozenset({'0', 'O'}),  # zero vs O
    frozenset({'0', 'o'}),
    frozenset({'I', 'l'}),
    frozenset({'I', '1'}),
    frozenset({'c', 'e'}),
    frozenset({'n', 'u'}),
    frozenset({'rn', 'm'}),
}


def _visually_similar(a: str, b: str) -> bool:
    """Check if two characters are commonly confused by OCR."""
    return frozenset({a, b}) in _CONFUSABLE_PAIRS
