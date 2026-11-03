from __future__ import annotations

from .inputs import VerifierInput

PROMPT_VERSION = "pis-v1.0"
SCALAR_PROMPT_VERSION = "scalar-v1.0"
BINARY_PROMPT_VERSION = "binary-v1.0"


def _fmt_block(s) -> str:
    return s if (s and str(s).strip()) else "(not provided)"


def _inputs_block(vin: VerifierInput) -> str:
    lines = [
        "INPUTS:",
        f"- Reported perturbation category: {vin.error_type if vin.error_type else '(not provided)'}",
        "- Original span:",
        _fmt_block(vin.original),
        "- Perturbed span:",
        _fmt_block(vin.perturbed),
        "- Evidence quote from the paper (verbatim):",
        vin.contradicts_quote.strip() if vin.quote_available else "(no quote available)",
    ]
    if vin.quote_source:
        lines.append(f"- Provenance of the evidence quote: {vin.quote_source}")
    lines += ["- Surrounding context:", _fmt_block(vin.surrounding_context)]
    if vin.related_passages:
        lines.append("- Related passages from the paper:")
        for i, p in enumerate(vin.related_passages, 1):
            lines.append(f"  [{i}] {p}")
    return "\n".join(lines)


def build_pis_prompt(vin: VerifierInput) -> str:
    return "\n".join([
        "You are auditing a perturbed span from a scientific paper.",
        "",
        'HYPOTHESIS H: "Replacing the original span with the perturbed span makes the text',
        'semantically inconsistent with the paper (a substantive error), as opposed to a',
        'harmless typographical or cosmetic change."',
        "",
        _inputs_block(vin),
        "",
        "TASK: Enumerate the evidence that bears on H, then rate your confidence.",
        "",
        "Each evidence item is an independent witness with:",
        '- "source_type": one of "quote", "context", "span_comparison", "error_type_meta",',
        '  "related_passage", "background_knowledge", "missing_evidence".',
        '- "description": one short sentence describing the evidence.',
        '- "polarity": "supports_H" (evidence that the perturbation IS a substantive',
        '  inconsistency), "against_H" (evidence that it is benign/typo-shaped), or',
        '  "unresolved" (cannot be committed either way).',
        '- "strength": number in [0,1]: how much this item contributes toward its polarity',
        "  if accepted.",
        '- "reliability": number in [0,1]: how much this item can be trusted as a witness',
        "  (a verbatim quote: high; a guess or a documented absence of evidence: low).",
        '- "justification": one short sentence.',
        "",
        "RULES:",
        "- List one item per DISTINCT piece of evidence; do not duplicate the same evidence.",
        "- Do NOT cancel conflicting evidence: if some items support H and others oppose it,",
        "  list them all. Conflict increases uncertainty; it is never resolved by averaging.",
        "- If the evidence quote is absent or empty, record one item with source_type",
        '  "missing_evidence" and polarity "unresolved".',
        "- Be honest with strength and reliability: use low values when unsure.",
        "- After the evidence items, give your overall self-rated confidence that H is true,",
        "  in [0,1].",
        "",
        "Respond with ONLY a JSON object in exactly this schema (no extra keys, no markdown):",
        "{",
        '  "hypothesis_restated": "<one sentence>",',
        '  "evidence_items": [',
        '    {"source_type": "...", "description": "...", "polarity": "...", "strength": 0.0, "reliability": 0.0, "justification": "..."}',
        "  ],",
        '  "self_reported_confidence_h": 0.0',
        "}",
    ])


def build_scalar_confidence_prompt(vin: VerifierInput) -> str:
    return "\n".join([
        "You are auditing a perturbed span from a scientific paper.",
        "",
        _inputs_block(vin),
        "",
        "Question: does the perturbed span introduce a substantive error (as opposed to a",
        "typo/cosmetic change)?",
        "",
        'Respond with ONLY a JSON object: {"p_substantive": <number in [0,1]>}',
    ])


def build_binary_prompt(vin: VerifierInput) -> str:
    return "\n".join([
        "You are auditing a perturbed span from a scientific paper.",
        "",
        _inputs_block(vin),
        "",
        "Question: does the perturbed span introduce a substantive error (as opposed to a",
        "typo/cosmetic change)? Answer with exactly one word: Yes or No.",
    ])