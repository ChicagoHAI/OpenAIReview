"""Deterministic span extraction from academic papers.

Identifies candidate spans for perturbation: equations, numeric values,
definitions, assumptions, claims, cross-references, and conditions.
Each span is tagged with its type and compatible error categories.
"""

import re
from .models import CandidateSpan, ErrorCategory, SpanType


def extract_candidates(text: str) -> list[CandidateSpan]:
    """Extract all perturbation candidates from a paper's text.

    Returns spans sorted by position in the document.
    """
    paragraphs = _split_paragraphs(text)
    candidates: list[CandidateSpan] = []
    span_counter = 0

    for para_idx, (para_text, char_offset) in enumerate(paragraphs):
        # Skip very short paragraphs (headings, page numbers, etc.)
        if len(para_text.strip()) < 30:
            continue

        # Extract spans of each type
        for extractor in _EXTRACTORS:
            for span_type, match_text, match_offset in extractor(para_text):
                context = _get_context(para_text, match_offset, window=200)
                categories = _compatible_categories(span_type)

                candidates.append(CandidateSpan(
                    span_id=f"S{span_counter:04d}",
                    span_type=span_type,
                    text=match_text,
                    paragraph_index=para_idx,
                    char_offset=char_offset + match_offset,
                    context=context,
                    compatible_categories=categories,
                ))
                span_counter += 1

    return candidates


def add_line_numbers(text: str) -> str:
    """Add [L001] prefixes to each paragraph for LLM free-form proposals."""
    paragraphs = text.split("\n\n")
    numbered = []
    for i, para in enumerate(paragraphs):
        numbered.append(f"[L{i+1:03d}] {para}")
    return "\n\n".join(numbered)


def strip_line_numbers(text: str) -> str:
    """Remove [L001] prefixes."""
    return re.sub(r"\[L\d{3}\] ", "", text)


# ---------------------------------------------------------------------------
# Paragraph splitting
# ---------------------------------------------------------------------------

def _split_paragraphs(text: str) -> list[tuple[str, int]]:
    """Split text into (paragraph_text, char_offset) pairs."""
    paragraphs = []
    offset = 0
    for block in re.split(r"\n\n+", text):
        if block.strip():
            paragraphs.append((block, text.index(block, offset)))
            offset = text.index(block, offset) + len(block)
    return paragraphs


# ---------------------------------------------------------------------------
# Span extractors -- each yields (SpanType, matched_text, offset_in_paragraph)
# ---------------------------------------------------------------------------

def _extract_display_equations(para: str):
    """Find display math: $$...$$ and \\[...\\]."""
    for pattern in [
        r"\$\$(.+?)\$\$",
        r"\\\[(.+?)\\\]",
    ]:
        for m in re.finditer(pattern, para, re.DOTALL):
            yield SpanType.EQUATION_DISPLAY, m.group(0), m.start()


def _extract_inline_equations(para: str):
    """Find inline math: $...$ and \\(...\\).

    Filters out dollar amounts (e.g., $18,426) by requiring LaTeX commands
    or multi-character math content.
    """
    for pattern in [
        r"(?<!\$)\$(?!\$)(.+?)\$(?!\$)",
        r"\\\((.+?)\\\)",
    ]:
        for m in re.finditer(pattern, para):
            inner = m.group(1)
            # Skip dollar amounts and trivially short content
            if re.match(r"^[\d,.\s]+$", inner):
                continue
            if len(inner.strip()) < 2:
                continue
            yield SpanType.EQUATION_INLINE, m.group(0), m.start()


def _extract_numeric_values(para: str):
    """Find numeric claims: values with context.

    Matches patterns like "= 0.67", "N = 631,389", "p < 0.05", "2.4%",
    but captures the surrounding clause for context.
    """
    # Numeric with comparison operator
    for m in re.finditer(
        r"(?:\b\w+\s*)?[=<>≤≥≈]\s*-?[\d,]+\.?\d*%?\b", para
    ):
        text = m.group(0).strip()
        if len(text) > 3:  # skip trivially short matches
            yield SpanType.NUMERIC, text, m.start()

    # Standalone percentages and large numbers in context
    for m in re.finditer(r"\b\d+[\d,]*\.?\d*\s*%", para):
        yield SpanType.NUMERIC, m.group(0), m.start()


def _extract_definitions(para: str):
    """Find definitional sentences.

    Matches up to the next sentence boundary (period, semicolon, or comma
    followed by 'where'/'and') to avoid truncating mid-expression.
    """
    patterns = [
        r"(?i)(?:let|define|denote|where)\s+.{5,80}?(?:denote|be|is|represent|=).{1,150}?[.;,]",
        r"(?i)we\s+define\s+.{5,150}?[.;]",
        r"(?i)(?:is|are)\s+defined\s+(?:as|by)\s+.{5,150}?[.;]",
    ]
    for pat in patterns:
        for m in re.finditer(pat, para):
            yield SpanType.DEFINITION, m.group(0).strip(), m.start()


def _extract_assumptions(para: str):
    """Find assumption statements."""
    patterns = [
        r"(?i)(?:we\s+)?assum(?:e|ing)\s+(?:that\s+)?.{10,120}?[.;]",
        r"(?i)suppose\s+(?:that\s+)?.{10,120}?[.;]",
        r"(?i)under\s+the\s+(?:assumption|condition)\s+(?:that\s+)?.{10,100}?[.;]",
    ]
    for pat in patterns:
        for m in re.finditer(pat, para):
            yield SpanType.ASSUMPTION, m.group(0).strip(), m.start()


def _extract_claims(para: str):
    """Find result/claim sentences."""
    patterns = [
        r"(?i)(?:we|I)\s+find\s+(?:that\s+)?.{10,150}?[.]",
        r"(?i)(?:the\s+)?results?\s+(?:show|suggest|indicate|demonstrate|imply)\s+.{10,150}?[.]",
        r"(?i)this\s+(?:implies|suggests|shows|indicates|demonstrates)\s+.{10,150}?[.]",
        r"(?i)(?:we|I)\s+(?:show|demonstrate|establish|prove)\s+(?:that\s+)?.{10,150}?[.]",
        r"(?i)(?:there\s+is|we\s+observe)\s+(?:a\s+)?(?:significant|strong|positive|negative).{10,100}?[.]",
    ]
    for pat in patterns:
        for m in re.finditer(pat, para):
            yield SpanType.CLAIM, m.group(0).strip(), m.start()


def _extract_cross_references(para: str):
    """Find cross-references to tables, figures, equations."""
    patterns = [
        r"(?i)(?:as\s+)?(?:shown|reported|presented|given|seen)\s+in\s+"
        r"(?:Table|Figure|Fig\.|Equation|Eq\.|Section|Appendix)\s*\d+",
        r"(?i)(?:see|from|in)\s+(?:Table|Figure|Fig\.|Equation|Eq\.)\s*\d+",
        r"(?i)(?:Table|Figure|Fig\.|Equation|Eq\.)\s*\d+\s+(?:shows|reports|presents|displays)",
    ]
    for pat in patterns:
        for m in re.finditer(pat, para):
            yield SpanType.CROSS_REFERENCE, m.group(0).strip(), m.start()


def _extract_conditions(para: str):
    """Find conditional statements."""
    patterns = [
        r"(?i)if\s+and\s+only\s+if\s+.{5,80}",
        r"(?i)(?:necessary|sufficient)\s+(?:condition|for)\s+.{5,80}",
        r"(?i)(?:provided|given)\s+that\s+.{10,100}?[.;]",
    ]
    for pat in patterns:
        for m in re.finditer(pat, para):
            yield SpanType.CONDITION, m.group(0).strip(), m.start()


_EXTRACTORS = [
    _extract_display_equations,
    _extract_inline_equations,
    _extract_numeric_values,
    _extract_definitions,
    _extract_assumptions,
    _extract_claims,
    _extract_cross_references,
    _extract_conditions,
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_context(para: str, offset: int, window: int = 200) -> str:
    """Get surrounding context for a match within a paragraph."""
    start = max(0, offset - window)
    end = min(len(para), offset + window)
    return para[start:end]


def _compatible_categories(span_type: SpanType) -> list[ErrorCategory]:
    """Which error categories can be applied to a given span type."""
    mapping = {
        SpanType.EQUATION_DISPLAY: [
            ErrorCategory.OPERATOR_OR_SIGN,
            ErrorCategory.SYMBOL_BINDING,
            ErrorCategory.INDEX_OR_SUBSCRIPT,
        ],
        SpanType.EQUATION_INLINE: [
            ErrorCategory.OPERATOR_OR_SIGN,
            ErrorCategory.SYMBOL_BINDING,
            ErrorCategory.INDEX_OR_SUBSCRIPT,
            ErrorCategory.NUMERIC_PARAMETER,
        ],
        SpanType.NUMERIC: [
            ErrorCategory.NUMERIC_PARAMETER,
        ],
        SpanType.DEFINITION: [
            ErrorCategory.SYMBOL_BINDING,
            ErrorCategory.CONDITION_OR_ASSUMPTION,
        ],
        SpanType.ASSUMPTION: [
            ErrorCategory.CONDITION_OR_ASSUMPTION,
        ],
        SpanType.CLAIM: [
            ErrorCategory.CLAIM_STRENGTHENING,
        ],
        SpanType.CROSS_REFERENCE: [
            ErrorCategory.NUMERIC_PARAMETER,  # wrong figure/table number
        ],
        SpanType.CONDITION: [
            ErrorCategory.CONDITION_OR_ASSUMPTION,
            ErrorCategory.OPERATOR_OR_SIGN,
        ],
    }
    return mapping.get(span_type, [])
