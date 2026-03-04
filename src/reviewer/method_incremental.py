"""Method: Incremental summary-based review.

Processes the paper sequentially, maintaining a running summary of definitions,
equations, theorems, and key claims. For each passage:
  1. (Optional) Pre-filter to skip non-technical content
  2. Deep-check: running summary + window context + passage → find errors
  3. Summary update: current summary + passage → updated summary
  4. Post-hoc consolidation: one final call to deduplicate and prune low-confidence issues
"""

import json
import re

from .client import chat
from .models import ReviewResult
from .utils import count_tokens, locate_comment_in_document, parse_comments_from_list


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
# Prompts
# ---------------------------------------------------------------------------

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
- Notation not yet in the summary — it may be introduced later

Return ONLY a JSON array (can be []). Each item:
- "title": concise title of the issue
- "quote": the exact verbatim text (preserving LaTeX)
- "explanation": deep reasoning — what you initially thought, whether context resolves it, and what specifically remains problematic
- "type": "technical" or "logical"
"""

SUMMARY_UPDATE_PROMPT = """\
You are maintaining a concise running summary of an academic paper's key technical content. \
This summary will be used as context when reviewing later sections of the paper.

CURRENT SUMMARY:
{current_summary}

---

NEW PASSAGE (section {passage_idx} of {total_passages}):
{passage_text}

---

Update the summary to incorporate any NEW information from this passage. \
Keep the summary structured and concise. Include:

1. **Notation & Definitions**: Any new symbols, variables, or terms defined
2. **Key Equations**: Important equations or formulas introduced (write them out, preserving LaTeX)
3. **Theorems & Propositions**: Statements of theorems, lemmas, corollaries (brief statement, not proof)
4. **Assumptions**: Any stated assumptions or conditions
5. **Key Claims**: Important results or conclusions established

Rules:
- PRESERVE all existing summary content unless it is superseded by new information
- ADD new items from the passage
- Do NOT include commentary, proof details, or experimental results
- Do NOT include information not in the passage or existing summary
- Keep entries brief — one line per item where possible
- If the passage contains no new definitions, equations, or key claims, return the summary unchanged

Return the updated summary directly (no JSON, no code fences)."""

TECHNICAL_FILTER_PROMPT = """\
Does this passage from an academic paper contain technical content worth checking for errors? \
Technical content includes: equations, proofs, derivations, theorems, algorithms, \
specific quantitative claims, or formal definitions.

Non-technical content includes: introductions, related work surveys, acknowledgments, \
reference lists, author bios, general motivation, or high-level overviews without formal claims.

PASSAGE:
{passage}

Answer with ONLY "yes" or "no"."""

CONSOLIDATION_PROMPT = """\
You are reviewing the complete list of issues found in an academic paper. \
Your job is to consolidate this list: remove duplicates and merge closely related issues.

Remove issues that:
- Flag the same underlying problem as another issue (keep the better-explained one)
- Flag standard conventions, notational shorthands, or well-known results

ISSUES FOUND:
{issues_json}

Return a JSON array containing the consolidated issues (same format as input). \
Return [] if none survive filtering."""

OVERALL_FEEDBACK_PROMPT = """\
You are an expert academic reviewer. Based on the beginning of the paper below, \
write one paragraph of high-level feedback on the paper's quality, clarity, \
and most significant issues.

PAPER (first 8000 characters):
{paper_start}
"""


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

    # If the list is very long, we may need to truncate
    if count_tokens(issues_json) > 30000:
        issues_json = issues_json[:120000]

    prompt = CONSOLIDATION_PROMPT.format(issues_json=issues_json)
    response, usage = chat(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        max_tokens=8192,
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

def review_incremental(
    paper_slug: str,
    document_content: str,
    model: str = "anthropic/claude-opus-4-5",
    reasoning_effort: str | None = None,
    skip_nontechnical: bool = False,
    window_size: int = 3,
) -> tuple[ReviewResult, ReviewResult]:
    """Review a paper using incremental summary approach.

    Processes the paper sequentially. For each passage:
      1. (Optional) Pre-filter non-technical content
      2. Deep-check with running summary + window context
      3. Update the running summary
    Then consolidate all comments in a final pass.

    Returns (consolidated_result, full_result).
    """
    result = ReviewResult(
        method="incremental",
        paper_slug=paper_slug,
        model=model,
        reasoning_effort=reasoning_effort,
    )

    paragraphs = split_into_paragraphs(document_content)
    passages = merge_into_passages(paragraphs)
    print(f"  Incremental: {len(passages)} passages (from {len(paragraphs)} paragraphs)")

    running_summary = ""
    all_comments = []
    skipped = 0

    for idx in range(len(passages)):
        para_indices, passage_text = passages[idx]

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
        prompt = DEEP_CHECK_PROMPT.format(context=context, passage=passage_text)
        response, usage = chat(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            max_tokens=4096,
            reasoning_effort=reasoning_effort,
        )
        result.raw_responses.append(response)
        result.total_prompt_tokens += usage["prompt_tokens"]
        result.total_completion_tokens += usage["completion_tokens"]

        # Parse comments
        new_comments = []
        arr_match = re.search(r"\[.*\]", response, re.DOTALL)
        if arr_match:
            try:
                items = json.loads(arr_match.group(0))
                new_comments = parse_comments_from_list(items)
                # Locate each comment within the passage's paragraphs
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

        # Step 2: Update running summary
        running_summary = update_running_summary(
            current_summary=running_summary,
            passage_text=passage_text,
            passage_idx=idx,
            total_passages=len(passages),
            model=model,
            result=result,
            reasoning_effort=reasoning_effort,
        )

    if skip_nontechnical:
        print(f"  Skipped {skipped}/{len(passages)} non-technical passages")

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

    # Step 3: Consolidation pass
    print(f"  Consolidating {len(all_comments)} comments...")
    result.comments = consolidate_comments(all_comments, model, result, reasoning_effort)
    print(f"  After consolidation: {len(result.comments)} comments")

    # Build full (pre-consolidation) result
    import copy
    full_result = copy.deepcopy(result)
    full_result.method = "incremental_full"
    full_result.comments = all_comments

    return result, full_result
