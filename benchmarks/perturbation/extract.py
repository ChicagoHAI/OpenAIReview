"""Deterministic span extraction from academic papers.

Identifies candidate spans for perturbation: display, inline, and named equations.
Each span is tagged with its type and compatible error categories.
"""

import re
from .models import CandidateSpan, Error, SpanType

def extract_abstract(text: str):
    """Extract abstract text from LaTeX."""                                                                           
    m = re.search(r'\\begin\{abstract\}(.+?)\\end\{abstract\}', text, re.DOTALL)                                      
    if m:
        return m.group(1).strip()        
                                                                                 
    return None 

def extract_candidates(text: str) -> list[CandidateSpan]:
    """Extract all perturbation candidates from a paper's text.

    Returns spans sorted by position in the document.
    """
    candidates: list[CandidateSpan] = []
    span_counter = 0

    # Extract spans of each type
    for extractor in _EXTRACTORS: # CAN return overlapping spans (diff categories)
        for span_type, match_text, match_offset in extractor(text):
            context = _get_context(text, match_offset, match_len=len(match_text), window=200)
            errors = _compatible_errors(span_type)

            if extractor in _EXTRACTORS_SURFACE:
                error_type = "surface"
            elif extractor in _EXTRACTORS_CLAIM:
                error_type = "claim"
            elif extractor in _EXTRACTORS_LOGIC:
                error_type = "logic"
            elif extractor in _EXTRACTORS_EXPERIMENTAL:
                error_type = "experimental"

            candidates.append(CandidateSpan(
                span_id=f"S{span_counter:04d}",
                span_type=span_type,
                text=match_text,
                offset=match_offset,
                context=context,
                error_type=error_type,
                compatible_errors=errors,
            ))
            span_counter += 1

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


_EXTRACTORS_CLAIM = [
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
# Error Type 4: Experimental 
# ---------------------------------------------------------------------------

def _extract_experimental(text: str):                                                                                 
      """Find experimental/results sections by heading, up to the next \\section."""
      EXPERIMENTAL_KEYWORDS = re.compile(                                                                               
          r'result|evaluation|empirical|numerical|case stud|analysis',                            
          re.IGNORECASE                                                                                                 
      )                                                                                                                 
      section_re = re.compile(r'\\section\*?\{([^}]+)\}')                                                               
      sections = list(section_re.finditer(text))
                                                                                                                        
      for i, match in enumerate(sections):
          if not EXPERIMENTAL_KEYWORDS.search(match.group(1)):                                                          
              continue
          start = match.start()
          end = sections[i + 1].start() if i + 1 < len(sections) else len(text)
          yield SpanType.EXPERIMENTAL, text[start:end], start          

_EXTRACTORS_EXPERIMENTAL = [
    _extract_experimental,
]

# ---------------------------------------------------------------------------
# All Errors
# ---------------------------------------------------------------------------

_EXTRACTORS = _EXTRACTORS_SURFACE + _EXTRACTORS_CLAIM + _EXTRACTORS_LOGIC + _EXTRACTORS_EXPERIMENTAL

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
            Error.INCORRECT_CLAIM 
        ],
        SpanType.THEOREM: [
            Error.INCORRECT_CLAIM 
        ],

        SpanType.PROOF: [
            Error.MISSING_CASE,
            Error.INDUCTION,
            Error.CIRCULAR_REASONING,
            Error.INVALID_IMPLICATION
        ],

        SpanType.EXPERIMENTAL: [
            Error.MISINTERP,
            Error.CAUSAL_REVERSED,
            Error.P_HACKING
        ]
    }
    return mapping.get(span_type, [])
