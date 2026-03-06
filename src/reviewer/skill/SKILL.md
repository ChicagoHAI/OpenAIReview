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
5. "Present review"
6. "Save viz JSON"

Mark each in-progress/completed as you go. Skip if no tracking tool is available.

---

## Step 1 — Prepare workspace

Run the preparation script:

```bash
python3 $SKILL_DIR/scripts/prepare_workspace.py "<input>" \
  --criteria $SKILL_DIR/references/criteria.md
```

Replace `<input>` with the paper path or URL from the user's message. The script auto-detects input type (PDF, arXiv URL, `.tex`/`.txt`/`.md`), downloads if needed (arXiv HTML preferred, PDF fallback), parses, splits into sections, and writes the workspace to `/tmp/<slug>_review/`.

Note the SLUG, REVIEW_DIR, and section list from the output.

---

## Step 2 — Pass A: Understand the paper

Read `/tmp/<slug>_review/full_text.md` using the Read tool. Read the **complete text including all appendices and tables**.

Build a comprehensive mental model:
- For math-heavy papers: every symbol and its definition, every key equation, every theorem/proposition, every assumption, every numerical parameter.
- For empirical/systems papers: every numerical threshold or hyperparameter, every experimental design choice, every component, every aggregate statistic, every claim in the abstract/introduction.

Then **write** a structured summary to `/tmp/<slug>_review/summary.md`:

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

Read `/tmp/<slug>_review/sections/index.json`. Based on Pass A, plan **6-9 sub-agents**:

**Section sub-agents** (one per major section or logical group):
- Each gets a primary section file and 1-3 related section files for cross-references
- Group small or closely related sections together (e.g., Abstract + Introduction)

**Cross-cutting sub-agents** (2-3, chosen based on what the paper needs):
- "Do abstract/introduction claims match evidence in results?"
- "Are evaluation comparisons fair and consistent?"
- "Do stated limitations and mitigations hold up?"
- Other paper-specific concerns from Pass A

If tracking tasks, create a sub-task for each planned sub-agent.

### 3b — Launch sub-agents

Read `$SKILL_DIR/references/subagent_templates.md` for the prompt templates. Launch all sub-agents **in parallel** using the Agent tool, filling in each template with the appropriate sections, focus areas, and file paths.

After all complete, mark sub-tasks done.

---

## Step 4 — Consolidate and tier findings

### 4a — Gather results

```bash
python3 $SKILL_DIR/scripts/consolidate_comments.py /tmp/<slug>_review
```

### 4b — Deduplicate and validate

Review the merged list:

- **Remove duplicates**: keep the better-explained one.
- **Remove false positives**: issues resolved by context, conventions, or leniency rules.
- **Verify quotes**: confirm each quote appears in the paper text.

**Do not drop issues just because they feel minor.** When uncertain, keep the issue but note the uncertainty.

### 4c — Assign severity tiers

- **major** — Undermines a key claim, methodology, or comparison; affects conclusions.
- **moderate** — Real error or gap that is localized and fixable.
- **minor** — Framing concern, mild overclaim, or ambiguity resolvable from context.

**Calibration**: most papers have a mix. Reconsider if all issues are one tier.

---

## Step 5 — Present review

Present grouped by severity:

---

**Overall assessment**

[One paragraph: high-level quality, clarity, and most significant issues.]

---

### Major issues

**[1] Title** `technical` or `logical`

> "Exact verbatim quote."

Explanation: ...

*(repeat, or "No major issues found.")*

### Moderate issues

**[N] Title** `technical` or `logical`

> "Exact verbatim quote."

Explanation: ...

### Minor issues

**[N] Title** `technical` or `logical`

> "Exact verbatim quote."

Explanation: ...

---

Number issues sequentially across all tiers.

---

## Step 6 — Save viz JSON

Write the final issues and overall assessment to the workspace, then run the viz script:

1. **Write** the consolidated issues (after dedup/tiering) as a JSON array to `/tmp/<slug>_review/final_issues.json`. Each object needs: `title`, `quote`, `explanation`, `comment_type`, `severity`.

2. **Write** the overall assessment paragraph to `/tmp/<slug>_review/overall_assessment.txt`.

3. **Run**:
```bash
python3 $SKILL_DIR/scripts/save_viz_json.py /tmp/<slug>_review
```

The script reads `metadata.json`, `full_text.md`, `final_issues.json`, and `overall_assessment.txt` from the workspace, builds the viz JSON, and merges with any existing `./review_results/<slug>.json`.

Tell the user: `Results saved to ./review_results/<slug>.json — run `openaireview serve` to visualize.`
