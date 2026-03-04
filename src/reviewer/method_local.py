"""Local window review: deep-check each chunk with surrounding context."""

import json
import re

from .client import chat
from .models import ReviewResult
from .utils import count_tokens, locate_comment_in_document, parse_comments_from_list


DEEP_CHECK_PROMPT = """\
You are a thoughtful reviewer checking a passage from an academic paper. \
Engage deeply with the material. For each potential issue, first try to understand the authors' \
intent and check whether your concern is resolved by context before flagging it.

FULL PAPER CONTEXT (relevant sections):
{context}

---

PASSAGE TO CHECK:
{passage}

---

Check for:
1. Mathematical / formula errors: wrong formulas, sign errors, missing factors, incorrect derivations, subscript or index errors
2. Notation inconsistencies: symbols used in a way that contradicts their earlier definition
3. Inconsistency between text and formal definitions: prose says one thing but the equation says another
4. Parameter / numerical inconsistencies: stated values contradict what can be derived from definitions or tables elsewhere
5. Insufficient justification: a key derivation step is skipped where the result is non-trivial
6. Questionable claims: statements that overstate what has actually been shown
7. Ambiguity that could mislead: flag only if a careful reader could reasonably reach an incorrect conclusion
8. Underspecified methods: an algorithm, procedure, or modification is described too vaguely for a reader to reproduce — key choices, boundary conditions, or parameter settings are left implicit

For each issue, write like a careful reader thinking aloud. Describe what initially confused or \
concerned you, what you checked to resolve it, and what specifically remains problematic. \
Acknowledge what the authors got right before noting the issue. Reference standard results \
or conventions in the field when relevant.

Be lenient with:
- Introductory and overview sections, which intentionally simplify or gloss over details
- Forward references — symbols or claims that may be defined or justified later in the paper
- Informal prose that paraphrases a formal result without repeating every qualifier

Do NOT flag:
- Formatting, typesetting, or capitalization issues
- References to equations or sections not shown in the context (they exist elsewhere)
- Incomplete text at passage boundaries
- Trivial observations that any reader in the field would immediately resolve

Return ONLY a JSON array (can be []). Each item:
- "title": concise title of the issue
- "quote": the exact verbatim text (preserving LaTeX)
- "explanation": deep reasoning — what you initially thought, whether context resolves it, and what specifically remains problematic
- "type": "technical" or "logical"
"""

OVERALL_FEEDBACK_PROMPT = """\
You are an expert academic reviewer. Based on the beginning of the paper below, \
write one paragraph of high-level feedback on the paper's quality, clarity, \
and most significant issues.

PAPER (first 8000 characters):
{paper_start}
"""


def split_into_paragraphs(text: str, min_chars: int = 100) -> list[str]:
    """Split document into paragraphs, merging short ones with the next."""
    raw = [p.strip() for p in text.split("\n\n") if p.strip()]
    paragraphs: list[str] = []
    carry = ""
    for p in raw:
        if carry:
            p = carry + "\n\n" + p
            carry = ""
        if len(p) < min_chars:
            carry = p
        else:
            paragraphs.append(p)
    if carry:
        if paragraphs:
            paragraphs[-1] = paragraphs[-1] + "\n\n" + carry
        else:
            paragraphs.append(carry)
    return paragraphs


def merge_into_chunks(
    paragraphs: list[str],
    target_chars: int = 4000,
) -> list[tuple[list[int], str]]:
    """Merge adjacent paragraphs into chunks of ~target_chars.

    Returns list of (paragraph_indices, merged_text) tuples.
    """
    chunks: list[tuple[list[int], str]] = []
    current_indices: list[int] = []
    current_text = ""

    for i, para in enumerate(paragraphs):
        if current_text and len(current_text) + len(para) > target_chars:
            chunks.append((current_indices, current_text))
            current_indices = []
            current_text = ""
        current_indices.append(i)
        current_text = (current_text + "\n\n" + para).strip()

    if current_text:
        chunks.append((current_indices, current_text))

    return chunks


def get_chunk_window_context(
    chunks: list[tuple[list[int], str]],
    chunk_idx: int,
    window: int = 3,
    max_tokens: int = 6000,
) -> str:
    """Get surrounding passages as context (asymmetric: more before, less after)."""
    before = window + 2
    after = max(1, window - 1)
    start = max(0, chunk_idx - before)
    end = min(len(chunks), chunk_idx + after + 1)
    context_parts = []
    for i in range(start, end):
        _, text = chunks[i]
        marker = ">>> " if i == chunk_idx else "    "
        context_parts.append(f"{marker}[section {i}] {text}")
    context = "\n\n".join(context_parts)
    if count_tokens(context) > max_tokens:
        context = context[: max_tokens * 4]
    return context


def review_local(
    paper_slug: str,
    document_content: str,
    model: str = "anthropic/claude-opus-4-5",
    reasoning_effort: str | None = None,
    window_size: int = 3,
) -> ReviewResult:
    """Review a paper by deep-checking each chunk with surrounding window context."""
    result = ReviewResult(
        method="local",
        paper_slug=paper_slug,
        model=model,
    )

    paragraphs = split_into_paragraphs(document_content)
    chunks = merge_into_chunks(paragraphs)
    print(f"  Local: {len(chunks)} chunks (from {len(paragraphs)} paragraphs)")

    all_comments = []

    for chunk_idx in range(len(chunks)):
        para_indices, chunk_text = chunks[chunk_idx]
        context = get_chunk_window_context(chunks, chunk_idx, window=window_size)

        prompt = DEEP_CHECK_PROMPT.format(context=context, passage=chunk_text)
        response, usage = chat(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            max_tokens=4096,
            reasoning_effort=reasoning_effort,
        )
        result.raw_responses.append(response)
        result.total_prompt_tokens += usage["prompt_tokens"]
        result.total_completion_tokens += usage["completion_tokens"]

        arr_match = re.search(r"\[.*\]", response, re.DOTALL)
        if arr_match:
            try:
                items = json.loads(arr_match.group(0))
                new_comments = parse_comments_from_list(items)
                chunk_paras = [paragraphs[i] for i in para_indices]
                for c in new_comments:
                    located = locate_comment_in_document(c.quote, chunk_paras)
                    if located is not None and located < len(para_indices):
                        c.paragraph_index = para_indices[located]
                    else:
                        c.paragraph_index = para_indices[0]
                all_comments.extend(new_comments)
            except json.JSONDecodeError:
                pass

        print(f"    Chunk {chunk_idx+1}/{len(chunks)}: {len(all_comments)} comments so far")

    result.comments = all_comments

    # Generate overall feedback
    paper_start = document_content[:8000]
    feedback_response, usage = chat(
        messages=[{"role": "user", "content": OVERALL_FEEDBACK_PROMPT.format(paper_start=paper_start)}],
        model=model,
        max_tokens=512,
        reasoning_effort=reasoning_effort,
    )
    result.overall_feedback = feedback_response.strip()
    result.total_prompt_tokens += usage["prompt_tokens"]
    result.total_completion_tokens += usage["completion_tokens"]

    return result
