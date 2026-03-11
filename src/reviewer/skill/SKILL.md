---
description: >
  Deep-review an academic paper using parallel sub-agents for section-level scrutiny.
  Produces tiered findings (major/moderate/minor) and saves viz-compatible results.
  Usage: /openaireview <path-or-arxiv-url>
  Trigger when the user provides a paper path or URL and asks for a deep or thorough review.
  Do not trigger for code questions, general questions, or non-paper documents.
---

Review the academic paper provided in the user's message using the OpenAIReview workflow below. Follow every step in order.

## Resources

This skill directory contains all bundled resources. Use paths relative to this `SKILL.md` after installation:

- `scripts/prepare_workspace.py`
- `scripts/consolidate_comments.py`
- `scripts/save_viz_json.py`
- `references/criteria.md`
- `references/subagent_templates.md`

## Step 0 - Track progress

If a task tracking tool is available (`TaskCreate`, `todo_write`, or equivalent), create these tasks:

1. Obtain paper text and prepare workspace
2. Pass A: Understand the paper
3. Pass B: Sub-agent reviews
4. Consolidate and tier findings
5. Present summary
6. Save viz JSON

## Step 1 - Prepare workspace

Run:

```bash
python3 scripts/prepare_workspace.py "<input>" \
  --criteria references/criteria.md \
  --output-dir ./review_results
```

Replace `<input>` with the paper path or URL from the user's message. The script writes `./review_results/<slug>_review/`.

## Step 2 - Pass A: Understand the paper

Read `./review_results/<slug>_review/full_text.md` completely, including appendices and tables.

Then write `./review_results/<slug>_review/summary.md` with a structured summary covering the research question, core thesis, methodology overview, key definitions, key numerical parameters, main claims, section map, and notable cross-references.

## Step 3 - Pass B: Parallel sub-agent review

Read `./review_results/<slug>_review/sections/index.json` and plan 7-10 sub-agents:

- section sub-agents for major sections or logical section groups
- cross-cutting sub-agents for claim-evidence consistency, numerical consistency, evaluation fairness, and limitations

Read `references/subagent_templates.md`, then launch all sub-agents in parallel using the `Agent` tool. Each sub-agent should write its findings as JSON into `./review_results/<slug>_review/comments/`.

## Step 4 - Consolidate and tier findings

Run:

```bash
python3 scripts/consolidate_comments.py ./review_results/<slug>_review
```

Use the title list and `comments/all_comments.json` to merge duplicates, verify quotes, remove false positives, reclassify comment types into `methodology`, `claim_accuracy`, `presentation`, or `missing_information`, and assign `major`, `moderate`, or `minor` severity.

## Step 5 - Present summary

Give a brief overall assessment, then report counts for:

- Major issues
- Moderate issues
- Minor issues

Tell the user to run `openaireview serve` to browse the findings.

## Step 6 - Save viz JSON

Write:

- `./review_results/<slug>_review/final_issues.json`
- `./review_results/<slug>_review/overall_assessment.txt`

Then run:

```bash
python3 scripts/save_viz_json.py ./review_results/<slug>_review \
  --method-key openaireview__claude \
  --method-label "OpenAIReview (claude)" \
  --model claude \
  --slug-suffix _claude
```

Tell the user:

```text
Results saved to ./review_results/<slug>_claude.json

To visualize:
  openaireview serve

Then open http://localhost:8080 in your browser.
The workspace is at ./review_results/<slug>_review/ and can be deleted once you're done.
```
