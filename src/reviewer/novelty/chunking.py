"""Section-aware chunking and claim extraction.

Design notes
------------
* **Structure first, size second.** We split on section headings (Markdown
  ``#`` headings produced by every parser in ``reviewer.parsers``, plus raw
  LaTeX ``\\section{}``), then on sentence boundaries, and only then pack
  sentences up to a token budget. Fixed-size character windows routinely cut
  a definition in half, which hurts both BM25 and dense retrieval.
* **Small chunks.** Novelty evidence is usually one or two sentences ("we
  propose X, which does Y"). Embedding models also degrade on long inputs, so
  the default budget is ~200 tokens with one sentence of overlap.
* **Contextual headers.** Each chunk's indexed text is prefixed with the
  paper title and section name. A chunk reading "our method uses a learned
  router" is otherwise impossible to match against "mixture-of-experts".
* **Skip non-content sections** (references, acknowledgements, appendix
  checklists): they dominate lexical overlap without saying anything about
  what the paper contributes.
"""

from __future__ import annotations

import re
from functools import lru_cache

from .types import Chunk


@lru_cache(maxsize=1)
def _encoder():
    """Resolve the tokenizer once. ``reviewer.utils.count_tokens`` re-resolves
    per call, which is fine for whole papers but slow when counting every
    sentence -- and very slow offline, where each call retries the download."""
    try:
        import tiktoken
        return tiktoken.get_encoding("o200k_base")
    except Exception:
        return None


def count_tokens(text: str) -> int:
    enc = _encoder()
    if enc is None:
        return max(1, len(text) // 4) if text else 0
    return len(enc.encode(text, disallowed_special=()))

_MD_HEADING = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$")
_TEX_HEADING = re.compile(r"^\s*\\(?:sub)*section\*?\{(.+?)\}\s*$")
_BOLD_HEADING = re.compile(r"^\s*\*\*((?:\d+(?:\.\d+)*\.?\s+)?[A-Z][^*]{1,80})\*\*\s*$")

_SKIP_SECTIONS = re.compile(
    r"^\s*(?:\d+(?:\.\d+)*\.?\s*)?(references|bibliography|acknowledg|checklist|"
    r"neurips paper checklist|broader impact|ethics statement|author contributions|"
    r"funding|competing interests)",
    re.IGNORECASE,
)

# Abbreviations that end in "." but do not end a sentence.
_ABBREV = (
    "e.g", "i.e", "et al", "etc", "cf", "vs", "fig", "figs", "eq", "eqs", "sec",
    "secs", "tab", "thm", "lem", "def", "prop", "cor", "resp", "approx", "no",
)
_SENT_SPLIT = re.compile(r"(?<=[.!?])[\"')\]]*\s+(?=[A-Z0-9\\$(\[])")

# Sentences that state a contribution or a priority claim. These are the
# queries: novelty is a property of claims, not of the whole document.
_CLAIM_CUES = re.compile(
    r"\b("
    r"we (?:propose|introduce|present|develop|design|derive|establish|prove|show|"
    r"demonstrate|formulate|provide|release|construct|identify|obtain)|"
    r"our (?:main )?(?:contribution|method|approach|framework|model|algorithm|result|"
    r"analysis|theorem|finding)s?|"
    r"(?:we|i) find|"
    r"i (?:propose|introduce|present|develop|show|demonstrate|prove|document|provide)|"
    r"(?:in )?this (?:paper|work|article|study),? (?:we|i)|"
    r"this (?:paper|work|article|study) (?:addresses|provides|shows|proposes|introduces|presents|"
    r"develops|offers|establishes|documents|demonstrates|is the first)|"
    r"(?:results|findings|paper|work) contribute|contribute[sd]? to|"
    r"to (?:the best of )?our knowledge|"
    r"(?:is|are) the first|for the first time|first (?:to|time|method|work)|"
    r"novel|new (?:method|approach|framework|algorithm|dataset|benchmark|bound)|"
    r"unlike (?:prior|previous|existing|earlier)|in contrast to (?:prior|previous|existing)|"
    r"outperform|state[- ]of[- ]the[- ]art"
    r")\b",
    re.IGNORECASE,
)

# "The remainder of this paper proceeds as follows" -- structure, not a claim.
_ROADMAP = re.compile(
    r"\b(remainder of (?:this|the) (?:paper|article)|(?:is|are) organi[sz]ed as follows|"
    r"proceeds as follows|section \d+ (?:provides|describes|presents|reviews|concludes))",
    re.IGNORECASE,
)


def split_sections(text: str) -> list[tuple[str, str]]:
    """Split a document into ``(heading, body)`` pairs.

    Text before the first heading is returned under the heading ``""``.
    """
    sections: list[tuple[str, list[str]]] = [("", [])]
    for line in text.splitlines():
        m = _MD_HEADING.match(line) or _TEX_HEADING.match(line) or _BOLD_HEADING.match(line)
        if m:
            heading = re.sub(r"[*_`]", "", m.group(m.lastindex or 1)).strip()
            sections.append((heading, []))
        else:
            sections[-1][1].append(line)
    out = [(h, "\n".join(body).strip()) for h, body in sections]
    return [(h, b) for h, b in out if b]


def split_sentences(text: str) -> list[str]:
    """Rule-based sentence splitter tuned for academic prose.

    Avoids splitting after common abbreviations ("et al.", "Fig.", "Eq.")
    and inside inline math, and joins hard-wrapped lines first.
    """
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)  # unwrap single newlines
    sentences: list[str] = []
    for para in re.split(r"\n\s*\n", text):
        para = re.sub(r"\s+", " ", para).strip()
        if not para:
            continue
        parts = _SENT_SPLIT.split(para)
        buf = ""
        for part in parts:
            buf = f"{buf} {part}".strip() if buf else part
            tail = buf.rstrip(".!?\"')] ").lower()
            ends_with_abbrev = any(tail.endswith(a) for a in _ABBREV)
            in_math = buf.count("$") % 2 == 1
            if ends_with_abbrev or in_math:
                continue
            sentences.append(buf)
            buf = ""
        if buf:
            sentences.append(buf)
    return sentences


def _header(title: str, section: str) -> str:
    bits = [b for b in (title.strip(), section.strip()) if b]
    return (" | ".join(bits) + "\n") if bits else ""


def chunk_document(
    text: str,
    doc_id: str,
    title: str = "",
    max_tokens: int = 200,
    overlap_sentences: int = 1,
    min_tokens: int = 25,
) -> list[Chunk]:
    """Chunk a document into section-scoped, sentence-aligned passages."""
    chunks: list[Chunk] = []
    pos = 0
    for heading, body in split_sections(text):
        if heading and _SKIP_SECTIONS.match(heading):
            continue
        sents = split_sentences(body)
        if not sents:
            continue
        lens = [count_tokens(s) for s in sents]
        start = 0
        while start < len(sents):
            end, used = start, 0
            while end < len(sents) and (used + lens[end] <= max_tokens or end == start):
                used += lens[end]
                end += 1
            body_text = " ".join(sents[start:end])
            prev = chunks[-1] if chunks else None
            if (used < min_tokens and prev is not None and prev.section == heading
                    and start > 0):
                # Fold a tiny tail into the previous chunk of the same section
                # instead of emitting a fragment with almost no signal.
                fresh = [s for s in sents[start:end] if s not in prev.text]
                if fresh:
                    prev.text = prev.text + " " + " ".join(fresh)
            else:
                chunks.append(Chunk(
                    chunk_id=f"{doc_id}#{pos}",
                    doc_id=doc_id,
                    text=_header(title, heading) + body_text,
                    section=heading,
                    kind="passage",
                    position=pos,
                ))
                pos += 1
            if end >= len(sents):
                break
            start = max(end - overlap_sentences, start + 1)
    return chunks


def find_abstract(text: str, max_words: int = 350) -> str:
    """Best-effort abstract: an 'Abstract' section, else the opening words."""
    for heading, body in split_sections(text):
        if heading.lower().strip(" .:0123456789") == "abstract":
            return body
    m = re.search(r"\\begin\{abstract\}(.+?)\\end\{abstract\}", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    m = re.search(r"(?im)^\s*abstract[.:\s]+(.+?)(?:\n\s*\n)", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    words = text.split()
    return " ".join(words[:max_words])


def extract_claims(
    text: str,
    title: str = "",
    max_claims: int = 12,
    min_chars: int = 50,
    max_chars: int = 600,
) -> list[Chunk]:
    """Extract the submission's contribution claims to use as queries.

    Always returns the abstract first (a document-level query), followed by
    cue-matched contribution sentences from the abstract, introduction and
    conclusion (where authors state what is new), then other sections.
    Each claim gets its preceding sentence as context when it starts with a
    pronoun-like reference ("This", "It", "These") that would otherwise be
    unresolvable.
    """
    doc_id = "submission"
    claims: list[Chunk] = []
    abstract = find_abstract(text)
    if abstract:
        claims.append(Chunk(
            chunk_id=f"{doc_id}#claim0", doc_id=doc_id,
            text=_header(title, "Abstract") + re.sub(r"\s+", " ", abstract)[:2000],
            section="Abstract", kind="abstract", position=0,
        ))

    priority = re.compile(r"abstract|intro|contribution|conclu|summary|discussion|^$", re.I)
    ranked: list[tuple[int, int, str, str]] = []
    seen: set[str] = set()
    order = 0
    for heading, body in split_sections(text):
        if heading and _SKIP_SECTIONS.match(heading):
            continue
        sents = split_sentences(body)
        for i, s in enumerate(sents):
            order += 1
            if not (min_chars <= len(s) <= max_chars) or not _CLAIM_CUES.search(s):
                continue
            if _ROADMAP.search(s):
                continue
            if i > 0 and re.match(
                    r"(?i)(this|these|it|they|such)\b(?!\s+(?:paper|work|study|article|thesis|chapter)\b)", s):
                s = f"{sents[i - 1]} {s}"
            key = re.sub(r"\W+", " ", s.lower()).strip()
            if key in seen:
                continue
            seen.add(key)
            tier = 0 if priority.search(heading or "") else 1
            ranked.append((tier, order, heading, s))

    ranked.sort(key=lambda r: (r[0], r[1]))
    for tier, _order, heading, s in ranked[: max(0, max_claims - len(claims))]:
        claims.append(Chunk(
            chunk_id=f"{doc_id}#claim{len(claims)}", doc_id=doc_id,
            text=_header(title, heading) + s, section=heading,
            kind="claim", position=len(claims),
        ))
    return claims
