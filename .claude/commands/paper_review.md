---
description: >
  Deep-review an academic paper for technical and logical errors, then save viz-compatible results.
  Usage: /paper_review <path-or-arxiv-url>
  TRIGGER when: user provides a paper path or URL to review, or asks to review a paper.
  DO NOT TRIGGER when: user is asking about code, general questions, or non-paper documents.
---

Review the academic paper provided in the user's message. Follow every step below in order.

---

## Step 0 — Create a task list to track progress

If a todo list or task tracking tool is available (e.g. TaskCreate, todo_write, or equivalent), create the following tasks before doing anything else:

1. "Obtain paper text" — fetch and parse the paper
2. "Pass A: Understand the paper" — build a complete mental model
3. "Pass B: Check for issues" — find technical and logical errors
4. "Consolidate findings" — remove duplicates and false positives
5. "Present review" — output the formatted review to the user
6. "Save viz JSON" — write results to review_results/<slug>.json

Mark each task as in-progress when you start it and completed when done before moving to the next step. If no such tool is available, skip this step and proceed.

---

## Step 1 — Obtain the paper text

If tracking tasks, mark "Obtain paper text" as in-progress.

Determine the input type from the argument and extract the text:

- **`.tex` / `.txt` / `.md`** — Use the Read tool directly. The content is the paper text.
- **`.pdf` or non-arXiv PDF URL** — First download the PDF if it's a URL (`curl -sL <url> -o /tmp/<slug>.pdf`). Then parse:
  ```
  python3 -c "
  from reviewer.parsers import parse_document
  title, text = parse_document('THE_FILE_PATH')
  print('TITLE:', title)
  print('---TEXT---')
  print(text)
  "
  ```
  If that fails, fall back to: `python3 -c "import pymupdf; d=pymupdf.open('THE_FILE_PATH'); print('\n\n'.join(p.get_text() for p in d))"`

  **If the output is being extracted via pymupdf** (you'll see the warning "Marker not available"), scan the extracted text for an arXiv ID (pattern `arXiv:\d{4}\.\d{4,5}` or `arxiv.org/abs/`). If found, re-fetch from `https://arxiv.org/html/<id>` using WebFetch for much better structure and math rendering.
- **arXiv HTML URL** (`arxiv.org/html/...`) — Use WebFetch.
- **arXiv abs URL** (`arxiv.org/abs/<id>`) — Replace `/abs/` with `/html/` and use WebFetch. If the HTML version is unavailable, try `arxiv.org/pdf/<id>` and download/parse the PDF.

Identify the paper **title** and a **slug** (URL-friendly name derived from the filename stem or arXiv ID, lowercase, hyphens only, max 80 chars).

If tracking tasks, mark "Obtain paper text" as completed.

---

## Step 2 — Review the paper

If tracking tasks, mark "Pass A: Understand the paper" as in-progress.

You are a thoughtful, expert reviewer. Work in two passes:

**Pass A — Understand the paper.** Read through the **full text including all appendices and tables**. Note (mentally, no output needed):
- For math-heavy papers: every symbol and its definition, every key equation, every theorem/proposition statement, every stated assumption, and every numerical parameter.
- For empirical/systems papers: every stated numerical threshold or hyperparameter, every experimental design choice, every component mentioned in the system description, every aggregate statistic and what it includes/excludes, and every claim made in the abstract and introduction.
- Build a complete picture before judging anything.

If tracking tasks, mark "Pass A: Understand the paper" as completed and "Pass B: Check for issues" as in-progress.

**Pass B — Check for issues.** Work through the paper in reading order, **including appendices and tables**. For every claim, formula, definition, proof step, and stated parameter: first try to understand the authors' intent and check whether your concern is resolved by context before flagging it.

### What to check

1. **Mathematical / formula errors** — wrong formulas, sign errors, missing factors, incorrect derivations, subscript or index errors
2. **Notation inconsistencies** — symbols used in a way that contradicts their earlier definition
3. **Text ↔ formal definition mismatch** — prose says one thing but the equation or table says another
4. **Parameter / numerical inconsistencies** — stated values contradict what can be derived from definitions or tables elsewhere in the paper; aggregate statistics that conflate evaluated and non-evaluated cases (e.g., reporting a rate over N items when only a subset were actually tested)
5. **Insufficient justification** — a key derivation step is skipped where the result is non-trivial and not standard; a threshold or design choice stated as fact with no rationale
6. **Questionable claims** — statements that overstate what has actually been shown; novelty claims ("first," "only") that cited related work may already satisfy; domain-norm mismatches (applying a criterion that is not standard in the evaluated field and presenting violations as research deficiencies)
7. **Misleading ambiguity** — flag only if a careful reader could reasonably reach an incorrect conclusion
8. **Underspecified methods** — an algorithm or procedure described too vaguely to reproduce; key choices, boundary conditions, or parameter settings left implicit; system components mentioned in passing but never described
9. **Internal contradictions** — a claim in one section of the paper that is directly contradicted by another section (including appendices); a stated mitigation ("prevents X") that is undermined later in the same paper

### Reasoning style

Write like a careful reader thinking aloud. For each issue:
- Describe what initially concerned you
- State what you checked to try to resolve it (looking at context, definitions, standard conventions)
- Explain what specifically remains problematic

Acknowledge what the authors got right before noting the issue. Reference standard results or conventions in the field when relevant.

### Be lenient with

- Introductory and overview sections, which intentionally simplify or gloss over details
- Forward references — symbols or claims that may be defined or justified later in the paper
- Notation not yet defined at the point of use — it may be introduced later in the paper
- Informal prose that paraphrases a formal result without repeating every qualifier

### Do NOT flag

- Formatting, typesetting, or capitalization issues
- References to equations or sections not visible in the current passage (they exist elsewhere in the paper)
- Trivial observations that any reader in the field would immediately resolve

---

## Step 3 — Consolidate your findings

If tracking tasks, mark "Pass B: Check for issues" as completed and "Consolidate findings" as in-progress.

Before outputting anything, review your own issue list:

- **Remove duplicates**: if two issues flag the same underlying problem, keep the better-explained one.
- **Remove false positives**: if an issue flags a standard convention, a well-known result, or something the paper actually resolves elsewhere, drop it.
- **Check leniency**: re-read each issue against the leniency rules above.

**Do not drop issues just because they feel minor or embarrassing to raise.** A copy-paste error in a published table, an unjustified threshold, or a contradiction between two sections are all worth flagging even if each is fixable in one sentence. When genuinely uncertain whether an issue is real, keep it but note the uncertainty in the explanation rather than silently dropping it.

Only clear false positives (resolved by context, standard conventions, or the leniency rules) should be removed.

---

## Step 4 — Conversational output

If tracking tasks, mark "Consolidate findings" as completed and "Present review" as in-progress.

Present the review in the following format:

---

**Overall assessment**

[One paragraph: high-level quality of the paper, clarity, and the most significant issues found.]

---

**Issues found** (or "No genuine issues found" if none)

**[1] Title of issue** `technical` or `logical`

> "Exact verbatim quote from the paper — copy it character-for-character, preserving any LaTeX."

Explanation: Your reasoning — what concerned you, what you checked, what specifically remains problematic.

**[2] ...** *(repeat for each issue)*

---

## Step 5 — Save viz-compatible JSON

If tracking tasks, mark "Present review" as completed and "Save viz JSON" as in-progress.

After presenting the review, save results so the user can run `openaireview serve` to visualize them.

### Build the data

1. **Split the paper text into paragraphs** using this Python snippet (handles pymupdf's per-page output and removes repeated headers):

```python
import re
from collections import Counter

# Step 1: Remove repeating page headers.
# Lines that appear 3+ times across the text are likely headers/footers.
lines = text.split('\n')
freq = Counter(l.strip() for l in lines if len(l.strip()) > 10)
noise = {l for l, n in freq.items() if n >= 3}
text = '\n'.join(l for l in lines if l.strip() not in noise)

# Step 2: Split on double newlines, then re-split each chunk on single newlines
# where a line ends a sentence (ends with . ! ? or is short) and the next
# starts a new one (capital letter or a section keyword). This recovers
# real paragraphs from pymupdf's per-page blocks.
raw_chunks = re.split(r'\n{2,}', text)
candidates = []
for chunk in raw_chunks:
    chunk = chunk.strip()
    if not chunk or re.match(r'^\d{1,3}$', chunk):  # skip page numbers
        continue
    # Try to sub-split on single newlines at sentence boundaries
    sub = re.split(r'\n(?=[A-Z0-9\[])', chunk)
    candidates.extend(s.replace('\n', ' ').strip() for s in sub if s.strip())

# Step 3: Merge very short fragments into the next chunk
paragraphs = []
buf = ''
for c in candidates:
    if buf and len(buf) < 120:
        buf = buf + ' ' + c
    else:
        if buf:
            paragraphs.append(buf)
        buf = c
if buf:
    paragraphs.append(buf)

indexed = [{'index': i, 'text': p} for i, p in enumerate(paragraphs)]
```

2. **Assign a paragraph index to each issue**: find the paragraph whose text contains the quote (exact prefix match on the first 80 chars). If not found, use fuzzy matching (pick the paragraph with the most shared substrings). Fall back to index 0.

3. **Build the JSON** using this structure:
```json
{
  "slug": "<slug>",
  "title": "<paper title>",
  "paragraphs": [
    {"index": 0, "text": "..."},
    ...
  ],
  "methods": {
    "paper_review__claude": {
      "label": "Paper Review (claude)",
      "model": "claude",
      "overall_feedback": "<overall assessment text>",
      "comments": [
        {
          "id": "paper_review__claude_0",
          "title": "<issue title>",
          "quote": "<exact verbatim quote>",
          "explanation": "<explanation text>",
          "comment_type": "technical",
          "paragraph_index": 0
        }
      ],
      "cost_usd": 0,
      "prompt_tokens": 0,
      "completion_tokens": 0
    }
  }
}
```

4. **Merge with existing file** if `./review_results/<slug>.json` already exists: read it, add/overwrite the `"paper_review__claude"` key inside `"methods"`, preserve all other method keys.

5. **Write** the JSON to `./review_results/<slug>.json` (create the directory if needed), formatted with 2-space indentation.

6. Tell the user: `Results saved to ./review_results/<slug>.json — run \`openaireview serve\` to visualize.`

If tracking tasks, mark "Save viz JSON" as completed.
