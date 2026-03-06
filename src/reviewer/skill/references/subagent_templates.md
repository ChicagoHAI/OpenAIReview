# Sub-agent Templates

Use these templates when launching sub-agents in Step 3b. Fill in all `<PLACEHOLDERS>` with actual values.

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

## Output
Write your findings as a JSON array to:
  <REVIEW_DIR>/comments/<DESCRIPTIVE_NAME>.json

Return a brief summary: how many issues found and a one-line title for each.
```

---

## Suggested cross-cutting checks

Pick 2-3 based on what the paper needs:

- **Claims vs evidence**: Do abstract/introduction claims match the evidence in the results?
- **Evaluation fairness**: Are comparisons fair and consistent across conditions?
- **Limitations coherence**: Do stated limitations and mitigations hold up across the paper?
- **Statistical consistency**: Are metrics/statistics computed and reported consistently?
- **Notation coherence**: Are symbols used consistently with their definitions throughout?
- **Method-results alignment**: Does the methodology section fully describe what was actually evaluated?
