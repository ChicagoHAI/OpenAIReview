"""Deterministic span extraction from academic papers.

Identifies candidate spans for perturbation: display, inline, and named equations.
Each span is tagged with its type and compatible error categories.
"""

import re
from .models import CandidateSpan, Error, SpanType
from .related_passages import find_related_passages

# Valid context modes for extract_candidates.
CONTEXT_MODES = ("none", "window", "related")


def extract_candidates(
    text: str,
    error_type: str,
    context_mode: str = "window",
    context_window: int = 200,
    related_passages_max: int = 5,
) -> list[CandidateSpan]:
    """Extract all perturbation candidates from a paper's text.

    Returns spans sorted by position in the document.

    Parameters
    ----------
    text : str
        The paper text.
    error_type : str
        "surface", "formal", or "all".
    context_mode : str
        Controls what the GENERATOR sees. The verifier always has access to the
        full related_passages list (see below).

        "none"    — span.context is empty; span.related_passages is empty (so
                    the generator sees no context at all).
        "window"  — span.context is a ±context_window-char slice; related
                    passages not shown to the generator.
        "related" — span.context is the ±context_window slice AND span.related_passages
                    is populated from whole-paper search (shown to the generator).

    Regardless of context_mode, span.verifier_related_passages is ALWAYS populated
    from the whole-paper lexical search. The verifier uses this to evaluate
    perturbations on equal footing across modes: when the generator didn't provide
    a contradicts_quote (none mode), the verifier can sample one from here.

    context_window : int
        Width of the local context window (±this many chars). Used when
        context_mode in {"window", "related"}.
    related_passages_max : int
        Maximum number of merged snippets per span. Caps both related_passages
        (generator-visible, related mode only) and verifier_related_passages.
    """
    if context_mode not in CONTEXT_MODES:
        raise ValueError(f"context_mode must be one of {CONTEXT_MODES}, got {context_mode!r}")

    if error_type == "surface":
        _EXTRACTORS = _EXTRACTORS_SURFACE
    elif error_type == "formal":
        _EXTRACTORS = _EXTRACTORS_FORMAL
    else:
        _EXTRACTORS = _EXTRACTORS_ALL

    candidates: list[CandidateSpan] = []
    span_offsets: list[int] = []  # parallel to `candidates`
    span_counter = 0

    # Extract spans of each type
    for extractor in _EXTRACTORS: # CAN return overlapping spans (diff categories)
        for span_type, match_text, match_offset in extractor(text):
            if context_mode == "none":
                context = ""
            else:
                context = _get_context(text, match_offset, match_len=len(match_text), window=context_window)
            errors = _compatible_errors(span_type)

            if extractor in _EXTRACTORS_SURFACE:
                error_type = "surface"
            elif extractor in _EXTRACTORS_FORMAL:
                error_type = "formal"

            candidates.append(CandidateSpan(
                span_id=f"S{span_counter:04d}",
                span_type=span_type,
                text=match_text,
                offset=match_offset,
                context=context,
                error_type=error_type,
                compatible_errors=errors,
            ))
            span_offsets.append(match_offset)
            span_counter += 1

    # Always compute verifier_related_passages (independent of context_mode).
    # The verifier uses these when the generator didn't provide a contradicts_quote.
    for span, off in zip(candidates, span_offsets):
        passages = find_related_passages(
            span, text, off,
            max_passages=related_passages_max,
        )
        span.verifier_related_passages = passages
        if context_mode == "related":
            # In related mode, the generator also sees them.
            span.related_passages = passages

    return candidates


# ---------------------------------------------------------------------------
# Error Type 1: Surface 
# ---------------------------------------------------------------------------

def _extract_display_equations(text: str):
    """Find display math: $$...$$ and \\[...\\]."""
    for pattern in [
        r"\$\$(.+?)\$\$",
        r"\\\[(.+?)\\\]",
    ]:
        for m in re.finditer(pattern, text, re.DOTALL):
            yield SpanType.EQUATION_DISPLAY, m.group(0), m.start()


def _extract_inline_equations(text: str):
    """Find inline math: $...$ and \\(...\\).

    Filters out dollar amounts (e.g., $18,426) by requiring LaTeX commands
    or multi-character math content.
    """
    for pattern in [
        r"(?<!\$)\$(?!\$)(.+?)\$(?!\$)",
        r"\\\((.+?)\\\)",
    ]:
        for m in re.finditer(pattern, text, re.DOTALL):
            inner = m.group(1)
            # Skip dollar amounts and trivially short content
            if re.match(r"^[\d,.\s]+$", inner):
                continue
            if len(inner.strip()) < 2:
                continue
            yield SpanType.EQUATION_INLINE, m.group(0), m.start()

               
def _extract_named_equations(text: str):
    """Find named math environments: align, equation, cases, etc."""                                                                                                                       
    NAMED_ENVS = ['equation', 'equation*',
                 'align', 'align*',
                 'alignat', 'alignat*',
                 'gather', 'gather*',
                 'multline', 'multline*',
                 'cases']          
    
    for env in NAMED_ENVS:
        pattern = rf'\\begin\{{{re.escape(env)}\}}(.+?)\\end\{{{re.escape(env)}\}}'
        for m in re.finditer(pattern, text, re.DOTALL):
            yield SpanType.EQUATION_NAMED, m.group(0), m.start()


_EXTRACTORS_SURFACE = [
    _extract_display_equations,
    _extract_inline_equations,
    _extract_named_equations,
]


# ---------------------------------------------------------------------------
# Error Type 2: Formal 
# ---------------------------------------------------------------------------

def _extract_definitions(text: str):
    """Find definition environments."""
    DEF_ENVS = ['definition', 'definition*']
    for env in DEF_ENVS:
        pattern = rf'\\begin\{{{re.escape(env)}\}}.*?\\end\{{{re.escape(env)}\}}'
        for m in re.finditer(pattern, text, re.DOTALL):
            yield SpanType.DEFINITION, m.group(0), m.start()


def _extract_theorems(text: str):
    """Find theorem-like environments: theorem, corollary, lemma, proposition."""
    THM_ENVS = ['theorem', 'theorem*', 'corollary', 'corollary*',
            'lemma', 'lemma*', 'proposition', 'proposition*']
    for env in THM_ENVS:
        pattern = rf'\\begin\{{{re.escape(env)}\}}.*?\\end\{{{re.escape(env)}\}}'
        for m in re.finditer(pattern, text, re.DOTALL):
            yield SpanType.THEOREM, m.group(0), m.start()


def _extract_proofs(text: str):
    """Find proof environments."""
    PRF_ENVS = ['proof', 'proof*']
    for env in PRF_ENVS:
        pattern = rf'\\begin\{{{re.escape(env)}\}}.*?\\end\{{{re.escape(env)}\}}'
        for m in re.finditer(pattern, text, re.DOTALL):
            yield SpanType.PROOF, m.group(0), m.start()


_EXTRACTORS_FORMAL = [
    _extract_definitions,
    _extract_theorems,
    _extract_proofs,
]


# ---------------------------------------------------------------------------
# All Errors:
# ---------------------------------------------------------------------------

_EXTRACTORS_ALL = _EXTRACTORS_SURFACE + _EXTRACTORS_FORMAL


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_context(text: str, offset: int, match_len: int = 0, window: int = 200) -> str:
    """Get surrounding context for a match."""
    start = max(0, offset - window)
    end = min(len(text), offset + match_len + window)
    return text[start:end]


def _compatible_errors(span_type: SpanType) -> list[Error]:
    """Which errors can be applied to a given span type."""
    mapping = {
        SpanType.EQUATION_DISPLAY: [
            Error.OPERATOR_OR_SIGN,
            Error.SYMBOL_BINDING,
            Error.INDEX_OR_SUBSCRIPT,
            Error.NUMERIC_PARAMETER,
        ],
        SpanType.EQUATION_INLINE: [
            Error.OPERATOR_OR_SIGN,
            Error.SYMBOL_BINDING,
            Error.INDEX_OR_SUBSCRIPT,
            Error.NUMERIC_PARAMETER,
        ],
        SpanType.EQUATION_NAMED: [
            Error.OPERATOR_OR_SIGN,
            Error.SYMBOL_BINDING,
            Error.INDEX_OR_SUBSCRIPT,
            Error.NUMERIC_PARAMETER,
        ], 

        SpanType.DEFINITION: [
            Error.DEF_WRONG
        ],
        SpanType.THEOREM: [
            Error.THM_WRONG_CONDITION, 
            Error.THM_WRONG_CONCLUSION,
            Error.THM_WRONG_SCOPE
        ],
        SpanType.PROOF: [
            Error.PROOF_WRONG_DIRECTION,
            Error.PROOF_MISSING_CASE,
            Error.PROOF_WRONG_ASSUMPTION,
            Error.PROOF_MISMATCH
        ]
    }
    return mapping.get(span_type, [])
