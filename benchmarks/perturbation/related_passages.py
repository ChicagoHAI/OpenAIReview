"""Find passages elsewhere in the paper that reference the same symbols/names
as a candidate span.

Goal: give the generator whole-paper evidence of where a span's symbols are
used downstream, so it can choose perturbations that break a concrete
reference (substantive errors) rather than typo-shaped surface slips.

Two stages:
1. Distinctive-token extraction from the span's text (false-positive-aware).
2. Whole-paper search for each token, excluding the span's own offset range.
   Snippets are ±100 chars around each hit, merged if they overlap.
"""

import re

from .models import CandidateSpan


# ---------------------------------------------------------------------------
# Distinctive token extraction
# ---------------------------------------------------------------------------

# LaTeX control sequences with ≥2 letters: \alpha, \mathcal, \leq, etc.
# Skips \a, \b, and non-letter escapes like \{ \$.
_LATEX_CMD = re.compile(r"\\[a-zA-Z]{2,}")

# Subscripted / superscripted identifiers: W_{ij}, x_{t+1}, A^{n-1}.
_SCRIPTED = re.compile(r"[A-Za-z][_^]\{[^}]+\}")

# Variable assignments: n = 100, alpha=0.5, \lambda = 1e-3.
# Requires a LHS identifier of ≥1 char followed by "=" and a numeric literal.
_ASSIGNMENT = re.compile(
    r"(?:\\[a-zA-Z]+|[A-Za-z_][A-Za-z_0-9]*)\s*=\s*[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?"
)

# Named references: Theorem 2, Eq. 3.1, Section 4, \ref{...}, \eqref{...}.
_NAMED_REF = re.compile(
    r"(?:Theorem|Lemma|Proposition|Corollary|Eq\.?|Equation|Definition|Fig\.?|Figure|Section|Sec\.?)"
    r"~?\s*\d+(?:\.\d+)?",
    re.IGNORECASE,
)
_LATEX_REF = re.compile(r"\\(?:ref|eqref|cref|autoref)\{[^}]+\}")


def _extract_distinctive_tokens(span_text: str) -> list[str]:
    """Extract tokens from span_text that are likely to appear elsewhere in the paper.

    Deduplicates while preserving first-seen order.
    """
    tokens: list[str] = []
    seen: set[str] = set()

    def _add(tok: str) -> None:
        tok = tok.strip()
        if len(tok) < 2:
            return
        # Require at least 2 alphanumeric chars after stripping delimiters,
        # else the token is too generic (e.g., single letters, `x_i`).
        alnum = re.sub(r"[^A-Za-z0-9]", "", tok)
        if len(alnum) < 2:
            return
        if tok in seen:
            return
        seen.add(tok)
        tokens.append(tok)

    for pattern in (_LATEX_CMD, _SCRIPTED, _ASSIGNMENT, _LATEX_REF, _NAMED_REF):
        for m in pattern.finditer(span_text):
            _add(m.group(0))

    return tokens


# ---------------------------------------------------------------------------
# Passage search
# ---------------------------------------------------------------------------

def find_related_passages(
    span: CandidateSpan,
    paper_text: str,
    span_offset: int,
    max_passages: int = 5,
    snippet_window: int = 100,
) -> list[dict]:
    """Find passages in `paper_text` that reference the same symbols/names as
    `span.text`. The span's own occurrence at `[span_offset, span_offset+len(span.text))`
    is excluded.

    Each returned passage is a dict:
      - offset: int (first hit that seeded this snippet)
      - snippet: str (±snippet_window chars around the hit, extended if adjacent
        hits fall within the window)
      - matched_tokens: list[str] (distinctive tokens that hit inside the snippet)

    Passages are sorted by offset and capped at `max_passages`.
    """
    tokens = _extract_distinctive_tokens(span.text)
    if not tokens:
        return []

    exclude_start = span_offset
    exclude_end = span_offset + len(span.text)

    # Collect all hits (offset, token) across all tokens.
    raw_hits: list[tuple[int, str]] = []
    for tok in tokens:
        for m in re.finditer(re.escape(tok), paper_text):
            off = m.start()
            if exclude_start <= off < exclude_end:
                continue
            raw_hits.append((off, tok))
    if not raw_hits:
        return []

    raw_hits.sort(key=lambda t: t[0])

    # Single-pass merge: extend the last snippet if the next hit falls inside
    # its window; otherwise start a new snippet.
    snippets: list[dict] = []
    for off, tok in raw_hits:
        start = max(0, off - snippet_window)
        end = min(len(paper_text), off + snippet_window)
        if snippets and start <= snippets[-1]["snippet_end"]:
            last = snippets[-1]
            last["snippet_end"] = max(last["snippet_end"], end)
            last["snippet"] = paper_text[last["snippet_start"]:last["snippet_end"]]
            if tok not in last["matched_tokens"]:
                last["matched_tokens"].append(tok)
        else:
            snippets.append({
                "offset": off,
                "snippet_start": start,
                "snippet_end": end,
                "snippet": paper_text[start:end],
                "matched_tokens": [tok],
            })

    snippets = snippets[:max_passages]
    return [
        {"offset": s["offset"], "snippet": s["snippet"], "matched_tokens": s["matched_tokens"]}
        for s in snippets
    ]


# ---------------------------------------------------------------------------
# Convenience: attach related_passages to every CandidateSpan
# ---------------------------------------------------------------------------

def attach_related_passages(
    candidates: list[CandidateSpan],
    paper_text: str,
    span_offsets: dict[str, int],
    max_passages: int = 5,
    snippet_window: int = 100,
) -> None:
    """Populate `span.related_passages` in-place for each candidate.

    `span_offsets` is a dict mapping span_id -> offset in paper_text. Callers
    that extract candidates and know their offsets should pass them through.
    If a span_id is missing, the span.text is located via `paper_text.find` as
    a fallback (first occurrence).
    """
    for span in candidates:
        off = span_offsets.get(span.span_id)
        if off is None:
            off = paper_text.find(span.text)
            if off == -1:
                span.related_passages = []
                continue
        span.related_passages = find_related_passages(
            span, paper_text, off, max_passages=max_passages, snippet_window=snippet_window,
        )
