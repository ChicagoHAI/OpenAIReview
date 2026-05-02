"""Local window review: deep-check each chunk with surrounding context."""

import json
import re
from datetime import date

from .client import chat
from .models import ReviewResult
from .prompts import DEEP_CHECK_PROMPT, OCR_CAVEAT, OVERALL_FEEDBACK_PROMPT
from .utils import count_tokens, locate_comments_in_window, parse_comments_from_list


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
    model: str = "anthropic/claude-opus-4-6",
    reasoning_effort: str | None = None,
    window_size: int = 3,
    ocr: bool = False,
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

        ocr_caveat = OCR_CAVEAT if ocr else ""
        prompt = DEEP_CHECK_PROMPT.format(context=context, passage=chunk_text, current_date=date.today().isoformat(), ocr_caveat=ocr_caveat)
        response, usage = chat(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            max_tokens=16384,
            reasoning_effort=reasoning_effort,
        )
        result.raw_responses.append(response)
        result.total_prompt_tokens += usage["prompt_tokens"]
        result.total_completion_tokens += usage["completion_tokens"]

        if not response.strip():
            print(f"    WARNING: Empty response for chunk {chunk_idx+1}/{len(chunks)} "
                  f"(model={model}). No comments extracted from this chunk.")
        else:
            arr_match = re.search(r"\[.*\]", response, re.DOTALL)
            if arr_match:
                try:
                    items = json.loads(arr_match.group(0))
                    new_comments = parse_comments_from_list(items)
                    locate_comments_in_window(
                        new_comments, chunk_idx, chunks, paragraphs, window_size,
                    )
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
        max_tokens=2048,
        reasoning_effort=reasoning_effort,
    )
    result.overall_feedback = feedback_response.strip()
    result.total_prompt_tokens += usage["prompt_tokens"]
    result.total_completion_tokens += usage["completion_tokens"]

    return result
