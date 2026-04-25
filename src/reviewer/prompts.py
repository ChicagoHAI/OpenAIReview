"""All review prompts in one place."""

# ── Shared building blocks ──────────────────────────────────────────────────

REVIEWER_PREAMBLE = """\
You are a thoughtful reviewer checking a passage from an academic paper. \
Today's date is {current_date}. \
Engage with the material in DETAIL. For each potential issue, first try to understand the authors' \
intent and check whether your concern is resolved by context before flagging it."""

CHECK_CRITERIA = """\
Check for:
1. Mathematical correctness (e.g. wrong formulas, sign errors, missing factors, incorrect derivations, subscript or index errors)
2. Notation inconsistencies (e.g. symbols used differently than defined, undefined notation)
3. Definition/Theorem inconsistencies (e.g. statements that contradict formal definitions/theorems)
4. Numerical inconsistencies (e.g. stated values contradict what can be derived from definitions, tables, or other sections)
5. Insufficient justification (e.g. skipped non-trivial step in derivation)
6. Overclaiming (e.g. statements that claim more than the evidence supports)
7. Ambiguity (e.g. lack of detail/specification that could lead reader to incorrect conclusions)"""

EXPLANATION_STYLE = """\
For each issue, state precisely what is correct, as well as what is wrong and why. Quote the exact text, explain the specific error, and if relevant, show what the correct version should be. Do not flag issues that can be resolved from context. Reference standard results or conventions in the field when relevant."""

LENIENCY_RULES = """\
Be lenient with:
- Introductory and overview sections
- Forward references (e.g. notation/claims that may be defined/justified later in the paper)
- Informal prose (e.g. conceptual descriptions for the purpose of intuition)"""

OCR_CAVEAT = """\
NOTE: This text was extracted via OCR and may contain notation errors. If a symbol appears inconsistent with surrounding usage, consider whether it is an OCR misread before flagging it."""

DO_NOT_FLAG_BASE = """\
Do NOT flag:
- Standard field conventions and notational shorthands (e.g. dropping summation bounds, overloading common symbols)
- Formatting, typesetting, capitalization
- References to content that exists elsewhere in the paper but isn't shown in the current context
- Issues resolvable by a competent reader through basic inference
- Stylistic or presentation preferences that don't affect correctness"""

DO_NOT_FLAG_CHUNKED = DO_NOT_FLAG_BASE.rstrip() + """
- Incomplete text at passage boundaries"""

JSON_ARRAY_OUTPUT = """\
Return ONLY a JSON array (can be []). Each item:
- "title": concise title of the issue
- "quote": the exact verbatim text (preserving LaTeX)
- "explanation": deep reasoning — what you initially thought, whether context resolves it, and what specifically remains problematic
- "type": "technical" or "logical"
"""

# ── Deep-check prompt (used by local and progressive methods) ───────────────

DEEP_CHECK_PROMPT = f"""{REVIEWER_PREAMBLE}

{{ocr_caveat}}

CONTEXT:
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


# ── Zero-shot prompts ───────────────────────────────────────────────────────

ZERO_SHOT_PROMPT = f"""{REVIEWER_PREAMBLE}

{{ocr_caveat}}

---

PAPER:

{{paper_text}}

---

{CHECK_CRITERIA}

{EXPLANATION_STYLE}

{LENIENCY_RULES}

{DO_NOT_FLAG_BASE}

Return a JSON object with this structure:
{{{{
  "overall_feedback": "one paragraph high-level assessment of the paper's quality and main issues",
  "comments": [
    {{{{
      "title": "concise title of the issue",
      "quote": "exact verbatim text from the paper (preserving LaTeX)",
      "explanation": "precise explanation of what is wrong and why",
      "type": "technical" or "logical"
    }}}}
  ]
}}}}

Return ONLY the JSON object. No other text."""

ZERO_SHOT_CHUNK_PROMPT = f"""{REVIEWER_PREAMBLE}

{{ocr_caveat}}

---

PASSAGE TO CHECK:

{{chunk_text}}

---

{CHECK_CRITERIA}

{EXPLANATION_STYLE}

{LENIENCY_RULES}

{DO_NOT_FLAG_CHUNKED}

Return a JSON object with this structure:
{{{{
  "overall_feedback": "brief assessment of this section",
  "comments": [
    {{{{
      "title": "concise title of the issue",
      "quote": "exact verbatim text from the paper (preserving LaTeX)",
      "explanation": "precise explanation of what is wrong and why",
      "type": "technical" or "logical"
    }}}}
  ]
}}}}

Return ONLY the JSON object. No other text."""


# ── Progressive-only prompts ────────────────────────────────────────────────

SUMMARY_UPDATE_PROMPT = """\
You are maintaining a concise running summary of an academic paper. \
This summary will be used as context when reviewing later sections of the paper.

CURRENT SUMMARY:
{current_summary}

---

NEW PASSAGE:
{passage_text}

---

Update the summary to incorporate any NEW information from this passage. \
Keep the summary structured and concise. Include:

1. **Notation and Definitions**: Any new symbols, variables, or terms defined
2. **Key Equations**: Important equations or formulas introduced (write them out, preserving LaTeX)
3. **Theorems and Propositions**: Statements of theorems, lemmas, corollaries (brief statement, not proof)
4. **Assumptions**: Any stated assumptions or conditions
5. **Key Claims**: Important results or conclusions established

Rules:
- PRESERVE ALL existing summary content unless it is superseded by new information
- Do NOT include commentary, proof details, or experimental results
- Do NOT include information not in the passage or existing summary
- Keep entries brief (one line per item where possible)
- If the passage contains no new definitions, equations, or key claims, return the summary unchanged

Return the updated summary directly."""

SUBSTANTIAL_FILTER_PROMPT = """\
Does this passage from an academic paper contain substantial content worth checking for errors? \
Substantial content includes: equations, derivations, definitions, theorems, proofs, algorithms, \
logical reasoning/claims.

Non-substantial content includes: introductions, citations, acknowledgments, author bios.

PASSAGE TO CHECK:
{passage}

Answer with ONLY "yes" or "no"."""

CONSOLIDATION_PROMPT = """\
You are reviewing the complete list of issues found in an academic paper. \
Your job is to consolidate this list by removing duplicates. If multiple issues flag the SAME underlying problem, keep the most detailed and well-explained one and remove the others. 

ISSUES FOUND:
{issues_json}

Return a JSON array containing the consolidated issues (same format as input). \
Return [] if none survive filtering."""


# ── Overall feedback (shared by local and progressive) ──────────────────────

OVERALL_FEEDBACK_PROMPT = """\
You are an expert academic reviewer. Based on the beginning of the paper below, write one paragraph of high-level feedback that:
- Identifies the paper's strongest contributions
- Raises 3-5 major thematic critiques (reference specific passages)
- Identifies conceptual tensions or unresolved contradictions in the paper's core argument
- If empirical, evaluates whether the experimental design, baselines, and metrics are appropriate and whether the results actually support the conclusions

Be direct and specific. Read like a domain expert, not a general-purpose critic. Do NOT summarize the paper. Do NOT list individual errors. 

Things to consider:
- Scope of claims: are the results narrow but presented as broadly applicable?
- Mising baselines or comparisons: what obvious alternative approaches are not discussed?
- Assumptions: are the key assumptions stated clearly, and are the realistic?           
- Internal consistency: do the different parts of the paper (theory, experiments, conclusions) tell a coherent story?
- Unresolved ideas: what are the most important questions the paper doesn't address?           

PAPER (first 8000 characters):
{paper_start}
"""
