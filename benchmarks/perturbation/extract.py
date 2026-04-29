"""Deterministic span extraction from academic papers.

Identifies candidate spans for perturbation: display, inline, and named equations.
Each span is tagged with its type and compatible error categories.
"""

import re
from .models import CandidateSpan, Error, SpanType

def extract_abstract(text: str) -> str | None:
    """Extract abstract text from LaTeX.

    Tries, in order: \\begin{abstract}, then a section named
    abstract/introduction/background/motivation/overview.
    """
    m = re.search(r'\\begin\{abstract\}(.+?)\\end\{abstract\}', text, re.DOTALL)
    if m:
        return m.group(1).strip()

    section_re = re.compile(
        r'\\(?:section|subsection)\*?\{(abstract|introduction|background|motivation|overview)[^}]*\}',
        re.IGNORECASE,
    )
    m = section_re.search(text)
    if m:
        start = m.end()
        next_sec = re.search(r'\\(?:section|subsection)\*?\{', text[start:])
        end = start + next_sec.start() if next_sec else start + 2000
        return text[start:end].strip()

    return None

_MAX_PER_SPAN_TYPE = 20

def extract_candidates(category, error_type, text: str) -> list[CandidateSpan]:
    """Extract all perturbation candidates from a paper's text.

    Returns spans sorted by position in the document.
    """
    candidates: list[CandidateSpan] = []
    span_counter = 0
    type_counts: dict[SpanType, int] = {}

    if category == "theoretical":
        if error_type == "all":
            extractors = _EXTRACTORS_THEORETICAL
        elif error_type == "surface":
            extractors = _EXTRACTORS_SURFACE
        elif error_type == "claim_theoretical":
            extractors = _EXTRACTORS_CLAIM_THEORETICAL
        elif error_type == "logic":
            extractors = _EXTRACTORS_LOGIC
    elif category == "experimental":
        if error_type == "all":
            extractors = _EXTRACTORS_EMPIRICAL
        elif error_type == "surface":
            extractors = _EXTRACTORS_SURFACE
        elif error_type == "statement_empirical":
            extractors = _EXTRACTORS_STATEMENT_EMPIRICAL
        elif error_type == "experimental":
            extractors = _EXTRACTORS_EXPERIMENTAL

    for extractor in extractors:
        for span_type, match_text, match_offset in extractor(text):
            if type_counts.get(span_type, 0) >= _MAX_PER_SPAN_TYPE:
                continue

            context = _get_context(text, match_offset, match_len=len(match_text), window=200)
            errors = _compatible_errors(span_type)

            error = extractor_dict[extractor]

            candidates.append(CandidateSpan(
                span_id=f"S{span_counter:04d}",
                span_type=span_type,
                text=match_text,
                offset=match_offset,
                context=context,
                error_type=error,
                compatible_errors=errors,
            ))
            span_counter += 1
            type_counts[span_type] = type_counts.get(span_type, 0) + 1

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
# Error Type 2: Claim 
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


_EXTRACTORS_CLAIM_THEORETICAL = [
    _extract_definitions,
    _extract_theorems,
]

# ---------------------------------------------------------------------------
# Error Type 3: Logic 
# ---------------------------------------------------------------------------

def _extract_proofs(text: str):
    """Find proof environments."""
    PRF_ENVS = ['proof', 'proof*']
    for env in PRF_ENVS:
        pattern = rf'\\begin\{{{re.escape(env)}\}}.*?\\end\{{{re.escape(env)}\}}'
        for m in re.finditer(pattern, text, re.DOTALL):
            yield SpanType.PROOF, m.group(0), m.start()

_EXTRACTORS_LOGIC = [
    _extract_proofs,
]

# ---------------------------------------------------------------------------
# Error Type 4: Empirical 
# ---------------------------------------------------------------------------
_SKIP_SECTIONS = re.compile(
    r'bibliograph|reference|appendix|acknowledge|acknowledgement',
    re.IGNORECASE,
)

def _extract_paragraphs(text: str):
    """Extract paragraphs from non-experimental sections (intro, related work, conclusion, etc.)"""
    EXPERIMENTAL_KEYWORDS = re.compile(
        r'result|evaluation|empirical|numerical|case stud|analysis|method|approach|statistical',
        re.IGNORECASE
    )
    section_re = re.compile(r'\\section\*?\{([^}]+)\}')
    sections = list(section_re.finditer(text))

    for i, match in enumerate(sections):
        title = match.group(1)
        if EXPERIMENTAL_KEYWORDS.search(title) or _SKIP_SECTIONS.search(title):
            continue                                                                                                  
        start = match.start()
        end = sections[i + 1].start() if i + 1 < len(sections) else len(text)
        section_text = text[start:end]
                                                                                                                    
        for para in re.split(r'\n\n+', section_text):
            para = para.strip()                                                                                       
            if len(para) < 50:
                continue
            para_offset = text.find(para, start)                                                                      
            if para_offset == -1:
                continue                                                                                              
            yield SpanType.PARAGRAPH, para, para_offset

_EXTRACTORS_STATEMENT_EMPIRICAL = [_extract_paragraphs]

def _extract_experimental(text: str):                                                                                 
    """Find experimental/results/methods sections, yielding individual paragraphs."""
    EXPERIMENTAL_KEYWORDS = re.compile(                                                                               
        r'result|evaluation|empirical|numerical|case stud|analysis|method|approach|statistical',
        re.IGNORECASE                                                                                                 
    )           
    section_re = re.compile(r'\\section\*?\{([^}]+)\}')
    sections = list(section_re.finditer(text))                                                                        

    for i, match in enumerate(sections):
        title = match.group(1)
        if not EXPERIMENTAL_KEYWORDS.search(title) or _SKIP_SECTIONS.search(title):
            continue
        start = match.start()
        end = sections[i + 1].start() if i + 1 < len(sections) else len(text)                                         
        section_text = text[start:end]
                                                                                                                    
        for para in re.split(r'\n\n+', section_text):                                                                 
            para = para.strip()
            if len(para) < 50:                                                                                        
                continue
            para_offset = text.find(para, start)
            if para_offset == -1:
                continue
            yield SpanType.EXPERIMENTAL, para, para_offset

_EXTRACTORS_EXPERIMENTAL = [_extract_experimental]

# ---------------------------------------------------------------------------
# All Errors
# ---------------------------------------------------------------------------

_EXTRACTORS_THEORETICAL = _EXTRACTORS_SURFACE + _EXTRACTORS_CLAIM_THEORETICAL + _EXTRACTORS_LOGIC
_EXTRACTORS_EMPIRICAL = _EXTRACTORS_SURFACE + _EXTRACTORS_STATEMENT_EMPIRICAL + _EXTRACTORS_EXPERIMENTAL

extractor_dict = {
    _extract_display_equations: "surface",
    _extract_inline_equations: "surface",
    _extract_named_equations: "surface",

    _extract_definitions: "claim_theoretical",
    _extract_theorems: "claim_theoretical",

    _extract_proofs: "logic",

    _extract_paragraphs: "statement_empirical",
    _extract_experimental: "experimental"
}

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
            Error.INDEX_OR_SUBSCRIPT,
            Error.NUMERIC_PARAMETER,
            Error.COMPUTATION,
        ],
        SpanType.EQUATION_INLINE: [
            Error.OPERATOR_OR_SIGN,
            Error.COMPUTATION,
            Error.INDEX_OR_SUBSCRIPT,
            Error.NUMERIC_PARAMETER,
        ],
        SpanType.EQUATION_NAMED: [
            Error.OPERATOR_OR_SIGN,
            Error.COMPUTATION,
            Error.INDEX_OR_SUBSCRIPT,
            Error.NUMERIC_PARAMETER,
        ], 

        SpanType.DEFINITION: [
            Error.INCORRECT_CLAIM_THEORETICAL,
        ],
        SpanType.THEOREM: [
            Error.INCORRECT_CLAIM_THEORETICAL,
        ],

        SpanType.PROOF: [
            Error.MISSING_CASE,
            Error.INDUCTION,
            Error.CIRCULAR_REASONING,
            Error.INVALID_IMPLICATION,
        ],

        SpanType.PARAGRAPH: [
            Error.INCORRECT_STATEMENT_EMPIRICAL
        ],
        SpanType.EXPERIMENTAL: [
            Error.MISINTERP,
            Error.CAUSAL_REVERSED,
            Error.P_HACKING,
        ]
    }
    return mapping.get(span_type, [])
