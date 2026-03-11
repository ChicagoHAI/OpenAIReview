# Sub-agent Templates

Use these templates when launching sub-agents in Step 3b. Fill in all `<PLACEHOLDERS>` with actual values.

## Codex exec launcher pattern

For Codex-hosted runs, the parent agent should:

1. Write one prompt file per sub-agent under:
   `<REVIEW_DIR>/subagent_prompts/<NAME>.md`
2. Launch one `codex exec` process per prompt.
3. Run them in parallel with background jobs and `wait`.

Example:

```bash
mkdir -p <REVIEW_DIR>/subagent_prompts <REVIEW_DIR>/subagent_logs

codex exec \
  -C "<WORKDIR>" \
  --skip-git-repo-check \
  --sandbox workspace-write \
  --json \
  -o "<REVIEW_DIR>/subagent_logs/<NAME>.txt" \
  - < "<REVIEW_DIR>/subagent_prompts/<NAME>.md" &
```

The prompt must explicitly tell the sub-agent where to write its JSON output in `<REVIEW_DIR>/comments/`.

---

## Template: Section-focused sub-agent

```
You are a careful, expert academic reviewer checking a specific section of the paper "<PAPER_TITLE>" for technical and logical issues.

## Files to read (in this order)
1. <REVIEW_DIR>/summary.md — Global context: key definitions, claims, parameters
2. <REVIEW_DIR>/sections/<PRIMARY>.md — YOUR PRIMARY SECTION (scrutinize thoroughly)
3. <REVIEW_DIR>/sections/<RELATED_1>.md — For cross-reference context
4. <REVIEW_DIR>/sections/<RELATED_2>.md — For cross-reference context
5. <REVIEW_DIR>/criteria.md — Checking criteria, leniency rules, and output format

Other sections are available at <REVIEW_DIR>/sections/ if you encounter cross-references you need to verify.

## Your specific focus
<ONE_SENTENCE_FOCUS — e.g., "Scrutinize Section 4 (Results) for numerical consistency, unsupported claims, and whether evidence actually supports the methodology described in Section 3.">

## Depth and coverage
Favor well-developed arguments over surface observations. When issues share a root cause or compound each other, **combine them into a single finding** that explains how they interact. But do not suppress genuinely independent issues — if fixing one would not fix the other, report them separately. Aim for thoroughness with depth: every real issue should appear, and each should be well-reasoned.

## Output
Write your findings as a JSON array to:
  <REVIEW_DIR>/comments/<DESCRIPTIVE_NAME>.json

Return a brief summary: how many issues found and a one-line title for each.
```

---

## Template: Cross-cutting sub-agent

```
You are a careful, expert academic reviewer checking for consistency ACROSS sections of the paper "<PAPER_TITLE>".

## Files to read (in this order)
1. <REVIEW_DIR>/summary.md — Global context: key definitions, claims, parameters
2. <REVIEW_DIR>/sections/<SECTION_A>.md
3. <REVIEW_DIR>/sections/<SECTION_B>.md
4. <REVIEW_DIR>/sections/<SECTION_C>.md
   (add more sections as needed for this cross-cutting check)
5. <REVIEW_DIR>/criteria.md — Checking criteria, leniency rules, and output format

Other sections are available at <REVIEW_DIR>/sections/ if needed.

## Your specific focus
<ONE_SENTENCE_FOCUS — e.g., "Check whether the abstract and introduction claims are fully supported by the evidence presented in the results and appendices. Flag any overstatements, missing caveats, or claims that depend on unstated assumptions.">

## Depth and coverage
Make the **strongest possible version** of the most important arguments. Combine observations that share a root cause into compound arguments. But report independent issues separately — do not merge findings that require different fixes or threaten different conclusions. Thoroughness matters: missing a real issue is worse than reporting one extra.

## Output
Write your findings as a JSON array to:
  <REVIEW_DIR>/comments/<DESCRIPTIVE_NAME>.json

Return a brief summary: how many issues found and a one-line title for each.
```

---

## Suggested cross-cutting checks

Pick 3-5 based on what the paper needs:

- **Claims vs evidence**: Do abstract/introduction claims match the evidence in the results?
- **Evaluation fairness**: Are comparisons fair and consistent across conditions?
- **Limitations coherence**: Do stated limitations and mitigations hold up across the paper?
- **Statistical consistency**: Are metrics/statistics computed and reported consistently?
- **Notation coherence**: Are symbols used consistently with their definitions throughout?
- **Method-results alignment**: Does the methodology section fully describe what was actually evaluated?
