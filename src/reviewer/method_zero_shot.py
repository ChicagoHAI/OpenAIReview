"""Method 1: Zero-shot paper review."""

from .client import chat
from .models import ReviewResult
from .utils import assign_paragraph_indices, chunk_text, count_tokens, parse_review_response

ZERO_SHOT_PROMPT = """\
You are a thoughtful reviewer reading the following academic paper. \
Engage deeply with the material. For each potential issue, first try to understand the authors' \
intent and check whether your concern is resolved by context before flagging it.

Carefully check for:
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
- Trivial observations that any reader in the field would immediately resolve

Return a JSON object with this structure:
{{
  "overall_feedback": "One paragraph high-level assessment of the paper's quality and main issues",
  "comments": [
    {{
      "title": "short descriptive title of the issue",
      "quote": "the exact verbatim text from the paper containing the issue (copy it exactly, preserving LaTeX)",
      "explanation": "deep reasoning — what you initially thought, whether context resolves it, and what specifically remains problematic",
      "type": "technical" or "logical"
    }}
  ]
}}

Return ONLY the JSON object, no other text.

---

PAPER:

{paper_text}
"""

LARGE_PAPER_CHUNK_PROMPT = """\
You are a thoughtful reviewer checking a section of an academic paper. \
Engage deeply with the material. For each potential issue, first try to understand the authors' \
intent and check whether your concern is resolved by context before flagging it.

Carefully check for:
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

Return a JSON object:
{{
  "overall_feedback": "brief assessment of this section",
  "comments": [
    {{
      "title": "short descriptive title of the issue",
      "quote": "the exact verbatim text from the paper containing the issue (copy it exactly, preserving LaTeX)",
      "explanation": "deep reasoning — what you initially thought, whether context resolves it, and what specifically remains problematic",
      "type": "technical" or "logical"
    }}
  ]
}}

Return ONLY the JSON object (comments can be [] if no issues found). No other text.

---

SECTION {chunk_num} of {total_chunks}:

{chunk_text}
"""

MAX_TOKENS_SINGLE = 100_000  # use single prompt if paper fits


def review_zero_shot(
    paper_slug: str,
    document_content: str,
    model: str = "anthropic/claude-opus-4-5",
    reasoning_effort: str | None = None,
) -> ReviewResult:
    result = ReviewResult(method="zero_shot", paper_slug=paper_slug, model=model,
                          reasoning_effort=reasoning_effort)

    token_count = count_tokens(document_content)

    if token_count <= MAX_TOKENS_SINGLE:
        prompt = ZERO_SHOT_PROMPT.format(paper_text=document_content)
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
            prompt = LARGE_PAPER_CHUNK_PROMPT.format(
                chunk_num=i + 1,
                total_chunks=len(chunks),
                chunk_text=chunk,
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
