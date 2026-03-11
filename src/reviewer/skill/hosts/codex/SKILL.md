---
name: openaireview
description: >
  Deep-review an academic paper using OpenAIReview's preparation, codex-exec sub-agent, and consolidation scripts.
  Produces tiered findings (major/moderate/minor) and saves viz-compatible results.
  Trigger when the user asks for a deep or thorough review of a paper and provides a paper path or URL.
  Do not trigger for code questions, general questions, or non-paper documents.
---

Review the academic paper from the user's request using the OpenAIReview workflow below. Follow the steps in order.

## Resources

This skill directory contains all bundled resources. Use paths relative to this `SKILL.md`:

- `scripts/prepare_workspace.py` - parse paper, split sections, write workspace
- `scripts/consolidate_comments.py` - merge section review JSON files
- `scripts/save_viz_json.py` - build viz JSON for `openaireview serve`
- `references/criteria.md` - review criteria to apply throughout the review
- `references/subagent_templates.md` - prompt templates and launcher pattern for `codex exec` section reviews

## Step 0 - Track progress

If the `update_plan` tool is available, create these steps and keep them updated:

1. Obtain paper text and prepare workspace
2. Understand the paper
3. Launch codex-exec sub-agents for section and cross-cutting review
4. Consolidate and tier findings
5. Save viz JSON and report results

If `update_plan` is unavailable, maintain the same checklist in your working notes and continue.

## Step 1 - Prepare workspace

Run:

```bash
python3 scripts/prepare_workspace.py "<input>" \
  --criteria references/criteria.md \
  --output-dir ./review_results
```

Replace `<input>` with the paper path or URL from the user's request. The script writes `./review_results/<slug>_review/`.

Record the `slug`, `review_dir`, and the section list from `sections/index.json`.

## Step 2 - Understand the paper

Read `./review_results/<slug>_review/full_text.md` completely, including appendices and tables.

Then write `./review_results/<slug>_review/summary.md` with:

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
1. "[Claim]" - [Section X, Table Y]

## Section Map
- [Section N] ([Title]): [one-line summary]

## Notable Cross-References
- [Section X] references [Section Y] for [what]
```

## Step 3 - Launch codex-exec sub-agents for review

Use `codex exec` as the sub-agent mechanism. Do not do the full section review only in the parent agent unless `codex` is unavailable or repeated subprocess launches fail.

Read `./review_results/<slug>_review/sections/index.json` and plan 7-10 review tasks:

- section-focused sub-agents for major sections or logical section groups
- cross-cutting sub-agents for:
  - abstract and introduction claims versus evidence in results
  - numerical consistency across prose, tables, and appendices
  - fairness and consistency of comparisons
  - limitations, caveats, and whether they match the paper's actual risks

Read `references/subagent_templates.md` and use those templates to build prompts for each sub-agent.

### Sub-agent execution pattern

For each planned sub-agent:

1. Create a prompt file under `./review_results/<slug>_review/subagent_prompts/`.
2. Launch a separate `codex exec` process that reads the prompt and writes its findings JSON under `./review_results/<slug>_review/comments/`.
3. Run multiple sub-agents in parallel via background jobs and `wait`.

Use a command pattern like:

```bash
mkdir -p \
  ./review_results/<slug>_review/subagent_prompts \
  ./review_results/<slug>_review/subagent_logs

codex exec \
  -C "$(pwd)" \
  --skip-git-repo-check \
  --sandbox workspace-write \
  --json \
  -o ./review_results/<slug>_review/subagent_logs/<name>.txt \
  - < ./review_results/<slug>_review/subagent_prompts/<name>.md &
```

Launch several of these in parallel, then `wait`. If needed, use a second pass only for sub-agents that failed to produce a valid JSON file.

The parent agent is responsible for:

- planning the section/group coverage
- generating prompt files with concrete paths filled in
- verifying that each expected `comments/*.json` file was actually written
- reading and lightly sanity-checking the outputs before consolidation

Each sub-agent should be instructed to write a JSON array. Each comment object should contain:

```json
{
  "title": "Short issue title",
  "quote": "Exact quote from the paper",
  "explanation": "Why this is a problem and what claim it affects",
  "comment_type": "technical",
  "confidence": "high",
  "source_section": "Section name",
  "related_sections": []
}
```

If `codex` is missing or the environment blocks subprocess execution, fall back to a sequential parent-agent review and say so in the final report.

## Step 4 - Consolidate and tier findings

Run:

```bash
python3 scripts/consolidate_comments.py ./review_results/<slug>_review
```

Use the printed title list plus `comments/all_comments.json` to:

- merge true duplicates by root cause
- keep distinct arguments separate when they affect different conclusions
- remove false positives only when the paper clearly resolves them
- verify every quote against the paper text
- classify each issue as `methodology`, `claim_accuracy`, `presentation`, or `missing_information`

Assign severity:

- `major` - undermines a key claim, methodology, or comparison
- `moderate` - real but localized error or gap
- `minor` - framing concern, mild overclaim, or ambiguity

Keep enough distinct issues for a thorough review. Do not over-merge.

## Step 5 - Save viz JSON and report results

Write:

- `./review_results/<slug>_review/final_issues.json`
- `./review_results/<slug>_review/overall_assessment.txt`

Then run:

```bash
python3 scripts/save_viz_json.py ./review_results/<slug>_review \
  --method-key openaireview__codex \
  --method-label "OpenAIReview (codex)" \
  --model codex \
  --slug-suffix _codex
```

Report:

- counts for major, moderate, and minor issues
- `Results saved to ./review_results/<slug>_codex.json`
- `openaireview serve` to visualize results
