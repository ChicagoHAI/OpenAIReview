"""All review prompts in one place."""

# ── Shared building blocks ──────────────────────────────────────────────────

REVIEWER_PREAMBLE = """\
You are a thoughtful reviewer checking a passage from an academic paper. \
Today's date is {current_date}. \
Engage deeply with the material. For each potential issue, first try to understand the authors' \
intent and check whether your concern is resolved by context before flagging it."""

CHECK_CRITERIA = """\
Check for:
1. Mathematical / formula errors: wrong formulas, sign errors, missing factors, incorrect derivations, subscript or index errors
2. Notation inconsistencies: symbols used in a way that contradicts their earlier definition
3. Inconsistency between text and formal definitions: prose says one thing but the equation says another
4. Parameter / numerical inconsistencies: stated values contradict what can be derived from definitions or tables elsewhere
5. Insufficient justification: a key derivation step is skipped where the result is non-trivial
6. Questionable claims: statements that overstate what has actually been shown
7. Ambiguity that could mislead: flag only if a careful reader could reasonably reach an incorrect conclusion
8. Underspecified methods: an algorithm, procedure, or modification is described too vaguely for a reader to reproduce — key choices, boundary conditions, or parameter settings are left implicit"""

EXPLANATION_STYLE = """\
For each issue, write like a careful reader thinking aloud. Describe what initially confused or \
concerned you, what you checked to resolve it, and what specifically remains problematic. \
Acknowledge what the authors got right before noting the issue. Reference standard results \
or conventions in the field when relevant."""

LENIENCY_RULES = """\
Be lenient with:
- Introductory and overview sections, which intentionally simplify or gloss over details
- Forward references — symbols or claims that may be defined or justified later in the paper
- Informal prose that paraphrases a formal result without repeating every qualifier"""

DO_NOT_FLAG_BASE = """\
Do NOT flag:
- Formatting, typesetting, or capitalization issues
- References to equations or sections not shown in the context (they exist elsewhere)
- Trivial observations that any reader in the field would immediately resolve"""

DO_NOT_FLAG_CHUNKED = DO_NOT_FLAG_BASE.rstrip() + """
- Incomplete text at passage boundaries"""

DO_NOT_FLAG_PROGRESSIVE = DO_NOT_FLAG_CHUNKED.rstrip() + """
- Notation not yet in the summary — it may be introduced later"""

JSON_ARRAY_OUTPUT = """\
Return ONLY a JSON array (can be []). Each item:
- "title": concise title of the issue
- "quote": the exact verbatim text (preserving LaTeX)
- "explanation": deep reasoning — what you initially thought, whether context resolves it, and what specifically remains problematic
- "type": "technical" or "logical"
"""

JSON_OBJECT_OUTPUT = """\
Return a JSON object with this structure:
{{{{
  "overall_feedback": "{feedback_desc}",
  "comments": [
    {{{{
      "title": "short descriptive title of the issue",
      "quote": "the exact verbatim text from the paper containing the issue (copy it exactly, preserving LaTeX)",
      "explanation": "deep reasoning — what you initially thought, whether context resolves it, and what specifically remains problematic",
      "type": "technical" or "logical"
    }}}}
  ]
}}}}

Return ONLY the JSON object{empty_note}. No other text."""


# ── Deep-check prompt (used by local and progressive methods) ───────────────

DEEP_CHECK_PROMPT = f"""{REVIEWER_PREAMBLE}

FULL PAPER CONTEXT (relevant sections):
{{context}}

---

PASSAGE TO CHECK:
{{passage}}

---

{CHECK_CRITERIA}

{EXPLANATION_STYLE}

{LENIENCY_RULES}

{DO_NOT_FLAG_CHUNKED}

{JSON_ARRAY_OUTPUT}"""

DEEP_CHECK_PROGRESSIVE_PROMPT = f"""{REVIEWER_PREAMBLE}

FULL PAPER CONTEXT (relevant sections):
{{context}}

---

PASSAGE TO CHECK:
{{passage}}

---

{CHECK_CRITERIA}

{EXPLANATION_STYLE}

{LENIENCY_RULES}

{DO_NOT_FLAG_PROGRESSIVE}

{JSON_ARRAY_OUTPUT}"""


# ── Zero-shot prompts ───────────────────────────────────────────────────────

ZERO_SHOT_PROMPT = f"""\
You are a thoughtful reviewer reading the following academic paper. \
Today's date is {{current_date}}. \
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

{EXPLANATION_STYLE}

{LENIENCY_RULES}

{DO_NOT_FLAG_BASE}

Return a JSON object with this structure:
{{{{
  "overall_feedback": "One paragraph high-level assessment of the paper's quality and main issues",
  "comments": [
    {{{{
      "title": "short descriptive title of the issue",
      "quote": "the exact verbatim text from the paper containing the issue (copy it exactly, preserving LaTeX)",
      "explanation": "deep reasoning — what you initially thought, whether context resolves it, and what specifically remains problematic",
      "type": "technical" or "logical"
    }}}}
  ]
}}}}

Return ONLY the JSON object, no other text.

---

PAPER:

{{paper_text}}
"""

LARGE_PAPER_CHUNK_PROMPT = f"""\
You are a thoughtful reviewer checking a section of an academic paper. \
Today's date is {{current_date}}. \
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

{EXPLANATION_STYLE}

{LENIENCY_RULES}

{DO_NOT_FLAG_CHUNKED}

Return a JSON object:
{{{{
  "overall_feedback": "brief assessment of this section",
  "comments": [
    {{{{
      "title": "short descriptive title of the issue",
      "quote": "the exact verbatim text from the paper containing the issue (copy it exactly, preserving LaTeX)",
      "explanation": "deep reasoning — what you initially thought, whether context resolves it, and what specifically remains problematic",
      "type": "technical" or "logical"
    }}}}
  ]
}}}}

Return ONLY the JSON object (comments can be [] if no issues found). No other text.

---

SECTION {{chunk_num}} of {{total_chunks}}:

{{chunk_text}}
"""


# ── Progressive-only prompts ────────────────────────────────────────────────

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


# ── Overall feedback (shared by local and progressive) ──────────────────────

OVERALL_FEEDBACK_PROMPT = """\
You are an expert academic reviewer. Based on the beginning of the paper below, \
write one paragraph of high-level feedback on the paper's quality, clarity, \
and most significant issues.

PAPER (first 8000 characters):
{paper_start}
"""
