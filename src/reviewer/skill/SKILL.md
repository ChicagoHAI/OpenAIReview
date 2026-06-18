---
description: >
  Deep-review an academic paper using parallel sub-agents for section-level scrutiny.
  Produces tiered findings (major/moderate/minor) and saves viz-compatible results.
  Usage: /openaireview <path-or-arxiv-url>
  TRIGGER when: user provides a paper path or URL and asks for a deep or thorough review.
  DO NOT TRIGGER when: user is asking about code, general questions, or non-paper documents.
---

Review the academic paper provided in the user's message using a multi-agent architecture for comprehensive section-level coverage. Follow every step below in order.

## Resources

All bundled resources live alongside this SKILL.md. Use this base path for all references:

    SKILL_DIR=~/.claude/commands/openaireview

| File | Purpose | How to use |
|------|---------|------------|
| `scripts/prepare_workspace.py` | Parse paper, split sections, write workspace | Run via Bash |
| `scripts/consolidate_comments.py` | Merge sub-agent comment JSONs | Run via Bash |
| `scripts/save_viz_json.py` | Build viz JSON for `openaireview serve` | Run via Bash |
| `references/criteria.md` | Review criteria for sub-agents | Copied into workspace by `prepare_workspace.py` |
| `references/subagent_templates.md` | Prompt templates for sub-agents | Read before Step 3b |

---

## Step 0 — Track progress

If a task tracking tool is available (TaskCreate, todo_write, or equivalent), create these tasks:

1. "Obtain paper text and prepare workspace"
2. "Pass A: Understand the paper"
3. "Pass B: Sub-agent reviews" (sub-tasks added after planning)
4. "Consolidate and tier findings"
5. "Present summary"
6. "Save viz JSON"

Mark each in-progress/completed as you go. Skip if no tracking tool is available.

---

## Step 1 — Prepare workspace

Run the preparation script:

```bash
python3 $SKILL_DIR/scripts/prepare_workspace.py "<input>" \
  --criteria $SKILL_DIR/references/criteria.md \
  --output-dir ./review_results
```

Replace `<input>` with the paper path or URL from the user's message. The script auto-detects input type (PDF, arXiv URL, `.tex`/`.txt`/`.md`), downloads if needed (arXiv HTML preferred, PDF fallback), parses, splits into sections, and writes the workspace to `./review_results/<slug>_review/`.

Note the SLUG, REVIEW_DIR, and section list from the output.

---

## Step 2 — Pass A: Understand the paper

Read `./review_results/<slug>_review/full_text.md` using the Read tool. Read the **complete text including all appendices and tables**.

Build a comprehensive mental model:
- For math-heavy papers: every symbol and its definition, every key equation, every theorem/proposition, every assumption, every numerical parameter.
- For empirical/systems papers: every numerical threshold or hyperparameter, every experimental design choice, every component, every aggregate statistic, every claim in the abstract/introduction.

Then **write** a structured summary to `./review_results/<slug>_review/summary.md`:

```markdown
# Paper Summary: [Title]

## Research Question
[One sentence]

## Core Hypothesis / Thesis
[What the paper claims to show]

## Methodology Overview
[2-3 sentences]

## Key Definitions & Notation
- [Term/symbol]: [definition]

## Key Numerical Parameters
- [Parameter]: [value and context]

## Main Claims (with evidence location)
1. "[Claim]" — [Section X, Table Y]

## Section Map
- [Section N] ([Title]): [one-line summary]

## Notable Cross-References
- [Section X] references [Section Y] for [what]
```

---

## Step 3 — Pass B: Parallel sub-agent review

### 3a — Plan sub-agents

Read `./review_results/<slug>_review/sections/index.json`. Based on Pass A, plan **7-10 sub-agents**:

**Section sub-agents** (one per major section or logical group):
- Each gets a primary section file and 1-3 related section files for cross-references
- Group small or closely related sections together (e.g., Abstract + Introduction)

**Cross-cutting sub-agents** (3-5, chosen based on what the paper needs):
- "Do abstract/introduction claims match evidence in results?"
- "Are evaluation comparisons fair and consistent?"
- "Do stated limitations and mitigations hold up?"
- "Are all formal definitions, tables, and enumerated lists internally consistent with each other and with the prose?"
- "Do numerical claims agree across sections, tables, and appendices? Cross-check headline figures against per-item or per-category breakdowns."
- "Does the paper hold itself to the same standards it applies to others — e.g., evaluation protocols, uncertainty quantification, or inclusion criteria?"
- Other paper-specific concerns from Pass A

If tracking tasks, create a sub-task for each planned sub-agent.

### 3b — Launch sub-agents

Read `$SKILL_DIR/references/subagent_templates.md` for the prompt templates. Launch all sub-agents **in parallel** using the Agent tool, filling in each template with the appropriate sections, focus areas, and file paths.

After all complete, mark sub-tasks done.

---

## Step 4 — Consolidate and tier findings

### 4a — Gather results

```bash
python3 $SKILL_DIR/scripts/consolidate_comments.py ./review_results/<slug>_review
```

The script prints a compact title list to stdout (one line per comment, always small enough to read inline — never truncated). It also writes `./review_results/<slug>_review/comments/all_comments.json` with the full text of every comment, indexed by `_index`.

Use the title list to identify duplicate clusters and plan merges. For any **singleton finding** (appearing in only one sub-agent), read its full text before deciding to drop — these are the most likely to be unique insights, not noise.

To fetch the full explanation of a specific comment (e.g., index 7):

```bash
python3 -c "
import json
it = json.load(open('./review_results/<slug>_review/comments/all_comments.json'))[7]
print(it['title'])
print(it['explanation'])
print(it.get('suggestion', ''))
"
```

### 4b — Deduplicate, merge, and validate

Review the title list:

- **Merge by root cause**: two comments share a root cause if fixing the underlying issue would resolve both. When multiple comments share a root cause, **merge them into one comment** that makes the strongest version of the argument, incorporating evidence from all. However, keep issues **separate** when they require different fixes or affect different paper-level conclusions — even if they stem from the same design decision. For example, "AND-logic inflates failure counts" and "AND-logic makes agreement figures unfair" share a root cause but affect different claims and should remain separate. When merging, check whether any comment in the group makes a **distinct argument** not covered by the merged version — e.g., it cites different evidence, targets a different claim, or identifies a different consequence. If so, keep it as a separate issue rather than folding it in. The goal is to eliminate true duplicates, not to compress distinct observations that happen to relate to the same design choice.
- **Remove false positives**: issues resolved by context, conventions, or leniency rules.
- **Verify quotes**: confirm each quote appears in the paper text.
- **Assign comment_type**: use `"methodology"`, `"claim_accuracy"`, `"presentation"`, or `"missing_information"`. Choose the type that best tells an author *what kind of fix is needed*. Sub-agents may output `"technical"`/`"logical"` — reclassify to the 4-type scheme during consolidation.
- **Write a suggestion**: every retained issue needs a `suggestion` field with the concrete revision, check, derivation, experiment, caveat, or clarification that would address it. If you merge comments, merge their suggestions into one actionable next step.

**Do not drop issues just because they feel minor.** When uncertain, keep the issue but note the uncertainty.

### 4c — Assign severity tiers

- **major** — Undermines a key claim, methodology, or comparison; affects conclusions.
- **moderate** — Real error or gap that is localized and fixable.
- **minor** — Framing concern, mild overclaim, or ambiguity resolvable from context.

**Calibration**: A well-calibrated review of a publishable paper typically has 3-7 major issues, but papers with multiple independent validity threats may legitimately have more. If you have more than 10, re-examine each: a major issue must threaten a **paper-level conclusion**, not just a single claim or paragraph. But do not under-count — if a paper has genuinely many independent validity threats (e.g., flawed evaluation protocol AND misleading statistics AND unacknowledged conflicts), each deserves a major. A missing justification for a parameter is moderate unless that parameter directly determines a headline finding. A design choice that could reasonably have gone differently is moderate unless the current choice demonstrably biases results in the paper's favor. Most papers should have a mix of tiers — reconsider if all issues cluster in one. The total comment count (across all severities) for a thorough review is typically **15-30** — if you have fewer than 15 after dedup, you may have over-merged and should revisit whether distinct arguments were incorrectly folded together.

---

## Step 5 — Present summary

Give a **brief** summary — full findings are in the viz UI.

Write 1–2 sentences of overall assessment (quality, key strengths, most significant concerns), then report counts:

- **Major**: N issues
- **Moderate**: N issues
- **Minor**: N issues

Tell the user to run `openaireview serve` to browse all findings.

---

## Step 6 — Save viz JSON

Write the final issues and overall assessment to the workspace, then run the viz script:

1. **Write** the consolidated issues (after dedup/tiering) as a JSON array to `./review_results/<slug>_review/final_issues.json`. Each object needs: `title`, `quote`, `explanation`, `suggestion`, `comment_type`, `severity`.

2. **Write** the overall assessment to `./review_results/<slug>_review/overall_assessment.txt`. This is the first thing users see in the viz UI. Keep it to **one short paragraph** (3-5 sentences, ~150 words). It should:
   - State whether the core contribution is sound and worth revising
   - Name the 2-3 most important problems (by reference, not full re-explanation — the comments have the details)
   - Give a calibrated bottom-line judgment (e.g., "these issues are fixable" vs "fundamental concerns")

   Do NOT restate all findings as prose — that's what the comment list is for.

3. **Run**:
```bash
python3 $SKILL_DIR/scripts/save_viz_json.py ./review_results/<slug>_review --slug-suffix _skill
```

The script reads `metadata.json`, `full_text.md`, `final_issues.json`, and `overall_assessment.txt` from the workspace, builds the viz JSON, and saves to `./review_results/<slug>_skill.json` (the `_skill` suffix distinguishes skill output from the normal CLI pipeline).

Tell the user:

```
Results saved to ./review_results/<slug>_skill.json

To visualize:
  openaireview serve

Then open http://localhost:8080 in your browser.
The workspace is at ./review_results/<slug>_review/ and can be deleted once you're done.
```
