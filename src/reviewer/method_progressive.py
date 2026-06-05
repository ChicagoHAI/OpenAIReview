"""Method: Progressive summary-based review.

Processes the paper sequentially, maintaining a running summary of definitions,
equations, theorems, and key claims. For each passage:
  1. (Optional) Pre-filter to skip non-technical content
  2. Deep-check: running summary + window context + passage → find errors
  3. Summary update: current summary + passage → updated summary
  4. Post-hoc consolidation: one final call to deduplicate and prune low-confidence issues
"""

import json
import re
from datetime import date

from .client import chat
from .models import ReviewResult
from .prompts import (
    CONSOLIDATION_PROMPT,
    DEEP_CHECK_PROGRESSIVE_PROMPT as DEEP_CHECK_PROMPT,
    OCR_CAVEAT,
    OVERALL_FEEDBACK_PROMPT,
    SUMMARY_UPDATE_PROMPT,
    TECHNICAL_FILTER_PROMPT,
)
from .utils import count_tokens, locate_comments_in_window, parse_comments_from_list


# ---------------------------------------------------------------------------
# Paragraph / passage helpers
# ---------------------------------------------------------------------------

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


def merge_into_passages(
    paragraphs: list[str],
    target_chars: int = 8000,
) -> list[tuple[list[int], str]]:
    """Merge adjacent paragraphs into passages of ~target_chars.

    Returns list of (paragraph_indices, merged_text) tuples.
    """
    passages: list[tuple[list[int], str]] = []
    current_indices: list[int] = []
    current_text = ""

    for i, para in enumerate(paragraphs):
        if current_text and len(current_text) + len(para) > target_chars:
            passages.append((current_indices, current_text))
            current_indices = []
            current_text = ""
        current_indices.append(i)
        current_text = (current_text + "\n\n" + para).strip()

    if current_text:
        passages.append((current_indices, current_text))

    return passages


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_window_context(
    passages: list[tuple[list[int], str]],
    passage_idx: int,
    window: int = 3,
    max_tokens: int = 6000,
) -> str:
    """Get surrounding passages as context (asymmetric: more before, less after)."""
    before = window + 2  # e.g. window=3 → 5 before
    after = max(1, window - 1)  # e.g. window=3 → 2 after
    start = max(0, passage_idx - before)
    end = min(len(passages), passage_idx + after + 1)
    context_parts = []
    for i in range(start, end):
        _, text = passages[i]
        marker = ">>> " if i == passage_idx else "    "
        context_parts.append(f"{marker}[section {i}] {text}")
    context = "\n\n".join(context_parts)
    if count_tokens(context) > max_tokens:
        context = context[: max_tokens * 4]
    return context


def update_running_summary(
    current_summary: str,
    passage_text: str,
    passage_idx: int,
    total_passages: int,
    model: str,
    result: ReviewResult,
    reasoning_effort: str | None = None,
    max_summary_tokens: int = 2000,
) -> str:
    """Call the model to update the running summary with new content."""
    prompt = SUMMARY_UPDATE_PROMPT.format(
        current_summary=current_summary if current_summary else "(empty — this is the first passage)",
        passage_text=passage_text,
        passage_idx=passage_idx,
        total_passages=total_passages,
    )
    response, usage = chat(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        max_tokens=3000,
        reasoning_effort=reasoning_effort,
    )
    result.total_prompt_tokens += usage["prompt_tokens"]
    result.total_completion_tokens += usage["completion_tokens"]

    updated = response.strip()
    if count_tokens(updated) > max_summary_tokens:
        updated = updated[: max_summary_tokens * 4]

    return updated


def is_technical_passage(
    passage_text: str,
    model: str,
    result: ReviewResult,
    reasoning_effort: str | None = None,
) -> bool:
    """Use the model to decide if a passage has technical content worth checking."""
    prompt = TECHNICAL_FILTER_PROMPT.format(passage=passage_text[:2000])
    response, usage = chat(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        max_tokens=8,
        reasoning_effort=reasoning_effort,
    )
    result.total_prompt_tokens += usage["prompt_tokens"]
    result.total_completion_tokens += usage["completion_tokens"]
    return response.strip().lower().startswith("yes")


def consolidate_comments(
    comments: list,
    model: str,
    result: ReviewResult,
    reasoning_effort: str | None = None,
) -> list:
    """Post-hoc consolidation: deduplicate and prune low-quality issues."""
    if not comments:
        return comments

    issues = [c.to_dict() for c in comments]
    issues_json = json.dumps(issues, indent=2)

    prompt = CONSOLIDATION_PROMPT.format(issues_json=issues_json)
    output_cap = count_tokens(issues_json) + 1024
    response, usage = chat(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        max_tokens=output_cap,
        reasoning_effort=reasoning_effort,
    )
    result.total_prompt_tokens += usage["prompt_tokens"]
    result.total_completion_tokens += usage["completion_tokens"]

    arr_match = re.search(r"\[.*\]", response, re.DOTALL)
    if arr_match:
        try:
            items = json.loads(arr_match.group(0))
            consolidated = parse_comments_from_list(items)
            # Preserve paragraph_index from original comments by matching quotes
            orig_by_quote = {}
            for c in comments:
                orig_by_quote[c.quote[:200]] = c.paragraph_index
            for c in consolidated:
                if c.paragraph_index is None:
                    c.paragraph_index = orig_by_quote.get(c.quote[:200])
            return consolidated
        except json.JSONDecodeError:
            pass

    return comments  # fallback: return originals if parsing fails


# ---------------------------------------------------------------------------
# Main review function
# ---------------------------------------------------------------------------

def review_progressive(
    paper_slug: str,
    document_content: str,
    model: str = "anthropic/claude-opus-4-6",
    reasoning_effort: str | None = None,
    skip_nontechnical: bool = False,
    window_size: int = 3,
    ocr: bool = False,
) -> tuple[ReviewResult, ReviewResult]:
    """Review a paper using progressive summary approach.

    Processes the paper sequentially. For each passage:
      1. (Optional) Pre-filter non-technical content
      2. Deep-check with running summary + window context
      3. Update the running summary
    Then consolidate all comments in a final pass.

    Returns (consolidated_result, full_result).
    """
    result = ReviewResult(
        method="progressive",
        paper_slug=paper_slug,
        model=model,
        reasoning_effort=reasoning_effort,
    )

    paragraphs = split_into_paragraphs(document_content)
    passages = merge_into_passages(paragraphs)
    # Scale summary budget with document length: ~10% of document tokens, floor 2000
    doc_tokens = count_tokens(document_content)
    max_summary_tokens = max(4000, doc_tokens // 10)
    print(f"  Progressive: {len(passages)} passages (from {len(paragraphs)} paragraphs), "
          f"doc length: {doc_tokens} tokens, summary budget: {max_summary_tokens} tokens")

    running_summary = ""
    all_comments = []
    skipped = 0

    for idx in range(len(passages)):
        _, passage_text = passages[idx]

        # Step 0: Optional pre-filter
        if skip_nontechnical:
            if not is_technical_passage(passage_text, model, result, reasoning_effort):
                skipped += 1
                print(f"    Passage {idx+1}/{len(passages)}: SKIPPED (non-technical)")
                # Still update summary even for skipped passages (may have definitions)
                running_summary = update_running_summary(
                    current_summary=running_summary,
                    passage_text=passage_text,
                    passage_idx=idx,
                    total_passages=len(passages),
                    model=model,
                    result=result,
                    reasoning_effort=reasoning_effort,
                    max_summary_tokens=max_summary_tokens,
                )
                continue

        # Build context: running summary + window
        window_context = get_window_context(passages, idx, window=window_size)
        if running_summary:
            context = (
                f"PAPER SUMMARY (key definitions, equations, and claims so far):\n"
                f"{running_summary}\n\n---\n\n{window_context}"
            )
        else:
            context = window_context

        # Step 1: Deep-check
        ocr_caveat = OCR_CAVEAT if ocr else ""
        prompt = DEEP_CHECK_PROMPT.format(context=context, passage=passage_text, current_date=date.today().isoformat(), ocr_caveat=ocr_caveat)
        response, usage = chat(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            max_tokens=16384,
            reasoning_effort=reasoning_effort,
        )
        result.raw_responses.append(response)
        result.total_prompt_tokens += usage["prompt_tokens"]
        result.total_completion_tokens += usage["completion_tokens"]

        # Parse comments
        new_comments = []
        if not response.strip():
            print(f"    WARNING: Empty response for passage {idx+1}/{len(passages)} "
                  f"(model={model}). No comments extracted from this passage.")
        else:
            arr_match = re.search(r"\[.*\]", response, re.DOTALL)
            if arr_match:
                try:
                    items = json.loads(arr_match.group(0))
                    new_comments = parse_comments_from_list(items)
                    locate_comments_in_window(
                        new_comments, idx, passages, paragraphs, window_size,
                    )
                    all_comments.extend(new_comments)
                except json.JSONDecodeError:
                    pass

        print(f"    Passage {idx+1}/{len(passages)}: "
              f"{len(new_comments)} comments, "
              f"summary {count_tokens(running_summary)} tokens")

        # Step 2: Update running summary
        running_summary = update_running_summary(
            current_summary=running_summary,
            passage_text=passage_text,
            passage_idx=idx,
            total_passages=len(passages),
            model=model,
            result=result,
            reasoning_effort=reasoning_effort,
            max_summary_tokens=max_summary_tokens,
        )

    if skip_nontechnical:
        print(f"  Skipped {skipped}/{len(passages)} non-technical passages")

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

    # Step 3: Consolidation pass
    print(f"  Consolidating {len(all_comments)} comments...")
    result.comments = consolidate_comments(all_comments, model, result, reasoning_effort)
    print(f"  After consolidation: {len(result.comments)} comments")

    # Build full (pre-consolidation) result
    import copy
    full_result = copy.deepcopy(result)
    full_result.method = "progressive_full"
    full_result.comments = all_comments

    return result, full_result
