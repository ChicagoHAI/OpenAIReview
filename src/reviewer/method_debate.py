"""Method: Progressive review with adversarial debate.

Replaces monolithic consolidation with per-comment adversarial adjudication.
Discovery phase is identical to the progressive method. Then for each comment:
  1. Challenger (small model): argues why the finding is NOT a real issue
  2. Verdict (large model): weighs the original comment against the challenge
     and decides keep/drop with reasoning

This preserves true positives that consolidation drops (43% recall loss on
Refine benchmark) while still filtering noise through adversarial pressure.

See: https://github.com/ChicagoHAI/OpenAIReview/issues/35
      https://github.com/ChicagoHAI/OpenAIReview/issues/36
"""

import json
import re
from datetime import date

from .client import chat
from .models import Comment, ReviewResult
from .prompts import (
    DEEP_CHECK_PROGRESSIVE_PROMPT as DEEP_CHECK_PROMPT,
    OVERALL_FEEDBACK_PROMPT,
    SUMMARY_UPDATE_PROMPT,
)
from .method_progressive import (
    split_into_paragraphs,
    merge_into_passages,
    get_window_context,
    update_running_summary,
)
from .utils import count_tokens, locate_comment_in_document, parse_comments_from_list


# ---------------------------------------------------------------------------
# Debate prompts
# ---------------------------------------------------------------------------

CHALLENGE_PROMPT = """\
You are a devil's advocate reviewing a comment made about an academic paper. \
Your job is to argue that this comment is WRONG — that the supposed issue is \
not actually a problem.

PAPER CONTEXT:
{context}

---

COMMENT TO CHALLENGE:
Title: {title}
Quote: {quote}
Explanation: {explanation}

---

Argue forcefully (but honestly) why this comment is incorrect. Consider:
- Does the author actually make the claimed error, or is the reviewer misreading?
- Is this a standard convention or well-known result the reviewer is unfamiliar with?
- Does surrounding context resolve the apparent inconsistency?
- Is this a trivial formatting issue disguised as a technical error?
- Could the reviewer be applying the wrong framework or making their own mistake?

If the comment is genuinely correct and you cannot find a reasonable counterargument, \
say so explicitly: "I cannot find a strong counterargument. The issue appears legitimate."

Keep your response to 2-4 sentences. Be specific."""

VERDICT_PROMPT = """\
You are an impartial editor adjudicating a dispute about an academic paper.

PAPER CONTEXT:
{context}

---

ORIGINAL COMMENT:
Title: {title}
Quote: {quote}
Explanation: {explanation}
Type: {comment_type}

---

CHALLENGE (arguing the comment is wrong):
{challenge}

---

Weigh both sides carefully. The original comment flags a potential issue; \
the challenge argues it is not a real problem. Consider:
- Does the paper text actually contain the claimed error?
- Is the challenge's counterargument substantive or merely dismissive?
- Would a domain expert consider this a genuine issue worth flagging?

Return ONLY a JSON object:
{{
  "verdict": "keep" or "drop",
  "confidence": "high" or "medium" or "low",
  "reason": "one sentence explaining your decision"
}}"""

MERGE_CLUSTER_PROMPT = """\
You have a list of validated comments about an academic paper. \
Some may refer to the same underlying issue from different passages. \
Merge duplicates into single, well-explained entries.

COMMENTS:
{comments_json}

Rules:
- If two comments flag the same underlying error, merge them (keep the better explanation, combine quotes)
- Do NOT remove any comment that flags a distinct issue
- Preserve all fields (title, quote, explanation, type, paragraph_index)
- For merged comments, keep the lower paragraph_index

Return ONLY a JSON array of the merged comments (same format as input)."""


# ---------------------------------------------------------------------------
# Debate logic
# ---------------------------------------------------------------------------

def _get_passage_context_for_comment(
    comment: Comment,
    passages: list[tuple[list[int], str]],
    paragraphs: list[str],
) -> str:
    """Find the passage containing this comment and return window context."""
    if comment.paragraph_index is not None:
        # Find which passage contains this paragraph
        for idx, (para_indices, _) in enumerate(passages):
            if comment.paragraph_index in para_indices:
                return get_window_context(passages, idx, window=3)
        # Fallback: use the passage closest to the paragraph index
        best_idx = 0
        best_dist = float("inf")
        for idx, (para_indices, _) in enumerate(passages):
            dist = min(abs(comment.paragraph_index - pi) for pi in para_indices)
            if dist < best_dist:
                best_dist = dist
                best_idx = idx
        return get_window_context(passages, best_idx, window=3)

    # No paragraph index — use the first 8000 chars as context
    return "\n\n".join(p for _, p in passages[:3])[:8000]


def debate_comment(
    comment: Comment,
    context: str,
    large_model: str,
    small_model: str,
    result: ReviewResult,
    reasoning_effort: str | None = None,
) -> tuple[bool, str, str]:
    """Run adversarial debate on a single comment.

    Returns (keep: bool, challenge: str, verdict_reason: str).
    """
    # Step 1: Challenge (small model)
    challenge_prompt = CHALLENGE_PROMPT.format(
        context=context,
        title=comment.title,
        quote=comment.quote,
        explanation=comment.explanation,
    )
    challenge_response, usage = chat(
        messages=[{"role": "user", "content": challenge_prompt}],
        model=small_model,
        max_tokens=1024,
        reasoning_effort=reasoning_effort,
    )
    result.total_prompt_tokens += usage["prompt_tokens"]
    result.total_completion_tokens += usage["completion_tokens"]

    # Step 2: Verdict (large model)
    verdict_prompt = VERDICT_PROMPT.format(
        context=context,
        title=comment.title,
        quote=comment.quote,
        explanation=comment.explanation,
        comment_type=comment.comment_type,
        challenge=challenge_response.strip(),
    )
    verdict_response, usage = chat(
        messages=[{"role": "user", "content": verdict_prompt}],
        model=large_model,
        max_tokens=512,
        reasoning_effort=reasoning_effort,
    )
    result.total_prompt_tokens += usage["prompt_tokens"]
    result.total_completion_tokens += usage["completion_tokens"]

    # Parse verdict
    keep = True  # default to keeping if parsing fails
    reason = ""
    try:
        obj_match = re.search(r"\{.*\}", verdict_response, re.DOTALL)
        if obj_match:
            verdict = json.loads(obj_match.group(0))
            keep = verdict.get("verdict", "keep").lower() == "keep"
            reason = verdict.get("reason", "")
    except (json.JSONDecodeError, AttributeError):
        reason = "Could not parse verdict; keeping comment by default"

    return keep, challenge_response.strip(), reason


def merge_duplicates(
    comments: list[Comment],
    model: str,
    result: ReviewResult,
    reasoning_effort: str | None = None,
) -> list[Comment]:
    """Merge duplicate comments that flag the same underlying issue."""
    if len(comments) <= 1:
        return comments

    issues = [c.to_dict() for c in comments]
    issues_json = json.dumps(issues, indent=2)

    prompt = MERGE_CLUSTER_PROMPT.format(comments_json=issues_json)
    response, usage = chat(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        max_tokens=count_tokens(issues_json) + 1024,
        reasoning_effort=reasoning_effort,
    )
    result.total_prompt_tokens += usage["prompt_tokens"]
    result.total_completion_tokens += usage["completion_tokens"]

    arr_match = re.search(r"\[.*\]", response, re.DOTALL)
    if arr_match:
        try:
            items = json.loads(arr_match.group(0))
            merged = parse_comments_from_list(items)
            # Preserve paragraph_index from originals
            orig_by_quote = {c.quote[:200]: c.paragraph_index for c in comments}
            for c in merged:
                if c.paragraph_index is None:
                    c.paragraph_index = orig_by_quote.get(c.quote[:200])
            return merged
        except json.JSONDecodeError:
            pass

    return comments  # fallback


# ---------------------------------------------------------------------------
# Main review function
# ---------------------------------------------------------------------------

def review_progressive_debate(
    paper_slug: str,
    document_content: str,
    model: str = "anthropic/claude-opus-4-6",
    small_model: str | None = None,
    reasoning_effort: str | None = None,
    window_size: int = 3,
) -> tuple[ReviewResult, ReviewResult]:
    """Review a paper using progressive discovery + adversarial debate.

    Phase 1: Progressive discovery (identical to review_progressive, no consolidation)
    Phase 2: Per-comment adversarial debate (challenge → verdict)
    Phase 3: Merge duplicate survivors

    Args:
        model: Large model for discovery, verdicts, and merging.
        small_model: Small model for challenges. Defaults to haiku.

    Returns (debated_result, full_result).
    """
    if small_model is None:
        # Infer a small model from the same provider
        if "/" in model:
            provider = model.split("/")[0]
            small_model = f"{provider}/claude-haiku-4-5"
        else:
            small_model = "claude-haiku-4-5"

    result = ReviewResult(
        method="progressive_debate",
        paper_slug=paper_slug,
        model=model,
        reasoning_effort=reasoning_effort,
    )

    # ── Phase 1: Progressive discovery ──────────────────────────────────────
    paragraphs = split_into_paragraphs(document_content)
    passages = merge_into_passages(paragraphs)
    doc_tokens = count_tokens(document_content)
    max_summary_tokens = max(4000, doc_tokens // 10)
    print(f"  Debate: {len(passages)} passages (from {len(paragraphs)} paragraphs), "
          f"doc length: {doc_tokens} tokens")

    running_summary = ""
    all_comments: list[Comment] = []

    for idx in range(len(passages)):
        para_indices, passage_text = passages[idx]

        # Build context: running summary + window
        window_context = get_window_context(passages, idx, window=window_size)
        if running_summary:
            context = (
                f"PAPER SUMMARY (key definitions, equations, and claims so far):\n"
                f"{running_summary}\n\n---\n\n{window_context}"
            )
        else:
            context = window_context

        # Deep-check
        prompt = DEEP_CHECK_PROMPT.format(
            context=context, passage=passage_text,
            current_date=date.today().isoformat(),
        )
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
        if response.strip():
            arr_match = re.search(r"\[.*\]", response, re.DOTALL)
            if arr_match:
                try:
                    items = json.loads(arr_match.group(0))
                    new_comments = parse_comments_from_list(items)
                    passage_paras = [paragraphs[i] for i in para_indices]
                    for c in new_comments:
                        located = locate_comment_in_document(c.quote, passage_paras)
                        if located is not None and located < len(para_indices):
                            c.paragraph_index = para_indices[located]
                        else:
                            c.paragraph_index = para_indices[0]
                    all_comments.extend(new_comments)
                except json.JSONDecodeError:
                    pass

        print(f"    Passage {idx+1}/{len(passages)}: "
              f"{len(new_comments)} comments, "
              f"summary {count_tokens(running_summary)} tokens")

        # Update running summary
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

    # Generate overall feedback
    paper_start = document_content[:8000]
    feedback_response, usage = chat(
        messages=[{"role": "user", "content": OVERALL_FEEDBACK_PROMPT.format(
            paper_start=paper_start
        )}],
        model=model,
        max_tokens=2048,
        reasoning_effort=reasoning_effort,
    )
    result.overall_feedback = feedback_response.strip()
    result.total_prompt_tokens += usage["prompt_tokens"]
    result.total_completion_tokens += usage["completion_tokens"]

    print(f"\n  Phase 1 complete: {len(all_comments)} raw comments")

    # ── Phase 2: Adversarial debate ─────────────────────────────────────────
    print(f"  Phase 2: Debating {len(all_comments)} comments "
          f"(challenger={small_model.split('/')[-1]}, "
          f"judge={model.split('/')[-1]})...")

    survivors: list[Comment] = []
    dropped = 0

    for i, comment in enumerate(all_comments):
        context = _get_passage_context_for_comment(comment, passages, paragraphs)

        keep, challenge, reason = debate_comment(
            comment=comment,
            context=context,
            large_model=model,
            small_model=small_model,
            result=result,
            reasoning_effort=reasoning_effort,
        )

        status = "KEEP" if keep else "DROP"
        print(f"    [{i+1}/{len(all_comments)}] {status}: {comment.title}")
        if not keep:
            print(f"      Reason: {reason}")
            dropped += 1
        else:
            survivors.append(comment)

    print(f"\n  Phase 2 complete: {len(survivors)} survived, {dropped} dropped")

    # ── Phase 3: Merge duplicates ───────────────────────────────────────────
    if len(survivors) > 1:
        print(f"  Phase 3: Merging duplicates...")
        merged = merge_duplicates(survivors, model, result, reasoning_effort)
        print(f"  After merging: {len(merged)} comments "
              f"(merged {len(survivors) - len(merged)})")
    else:
        merged = survivors

    result.comments = merged

    # Build full (pre-debate) result
    import copy
    full_result = copy.deepcopy(result)
    full_result.method = "progressive_debate_full"
    full_result.comments = all_comments

    return result, full_result
