"""Method 1: Zero-shot paper review."""

from datetime import date

from .client import chat
from .models import ReviewResult
from .prompts import LARGE_PAPER_CHUNK_PROMPT, OCR_CAVEAT, ZERO_SHOT_PROMPT
from .utils import assign_paragraph_indices, chunk_text, count_tokens, parse_review_response

MAX_TOKENS_SINGLE = 100_000  # use single prompt if paper fits


def review_zero_shot(
    paper_slug: str,
    document_content: str,
    model: str = "anthropic/claude-opus-4-6",
    reasoning_effort: str | None = None,
    ocr: bool = False,
) -> ReviewResult:
    result = ReviewResult(method="zero_shot", paper_slug=paper_slug, model=model,
                          reasoning_effort=reasoning_effort)

    token_count = count_tokens(document_content)

    if token_count <= MAX_TOKENS_SINGLE:
        ocr_caveat = OCR_CAVEAT if ocr else ""
        prompt = ZERO_SHOT_PROMPT.format(paper_text=document_content, current_date=date.today().isoformat(), ocr_caveat=ocr_caveat)
        response, usage = chat(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            max_tokens=8192,
            reasoning_effort=reasoning_effort,
        )
        result.raw_responses.append(response)
        result.total_prompt_tokens += usage["prompt_tokens"]
        result.total_completion_tokens += usage["completion_tokens"]
        overall, comments = parse_review_response(response)
        result.overall_feedback = overall
        result.comments = comments
    else:
        # Chunked approach
        chunks = chunk_text(document_content, max_tokens=80_000)
        all_comments = []
        overall_parts = []
        for i, chunk in enumerate(chunks):
            ocr_caveat = OCR_CAVEAT if ocr else ""
            prompt = LARGE_PAPER_CHUNK_PROMPT.format(
                chunk_num=i + 1,
                total_chunks=len(chunks),
                chunk_text=chunk,
                current_date=date.today().isoformat(),
                ocr_caveat=ocr_caveat,
            )
            response, usage = chat(
                messages=[{"role": "user", "content": prompt}],
                model=model,
                max_tokens=8192,
                reasoning_effort=reasoning_effort,
            )
            result.raw_responses.append(response)
            result.total_prompt_tokens += usage["prompt_tokens"]
            result.total_completion_tokens += usage["completion_tokens"]
            overall, comments = parse_review_response(response)
            if overall:
                overall_parts.append(overall)
            all_comments.extend(comments)
        result.overall_feedback = "\n\n".join(overall_parts)
        result.comments = all_comments

    assign_paragraph_indices(result.comments, document_content)
    return result
