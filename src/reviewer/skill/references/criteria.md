# Review Criteria

## What to check
1. **Mathematical / formula errors** -- wrong formulas, sign errors, missing factors, incorrect derivations, subscript or index errors
2. **Notation inconsistencies** -- symbols used differently than defined
3. **Text vs formal definition mismatch** -- prose says one thing but equation/table says another
4. **Parameter / numerical inconsistencies** -- stated values contradict derivable values; aggregate statistics with unclear or conflated denominators
5. **Insufficient justification** -- non-trivial derivation steps skipped; thresholds or design choices stated without rationale
6. **Questionable claims** -- overstatement of what has been shown; novelty claims that cited work may satisfy; domain-norm mismatches
7. **Misleading ambiguity** -- only if a careful reader could reasonably reach an incorrect conclusion
8. **Underspecified methods** -- procedure too vague to reproduce; key parameters left implicit; components mentioned but never described
9. **Internal contradictions** -- a claim contradicted by another section; a stated mitigation undermined later

## Reasoning style
For each issue: describe what concerned you, what you checked to resolve it (context, definitions, standard conventions), and what specifically remains problematic. Acknowledge what the authors got right. Reference standard results or conventions when relevant.

## Be lenient with
- Introductory and overview sections that intentionally simplify
- Forward references -- symbols or claims that may be defined or justified later
- Notation not yet defined at the point of use -- it may be introduced later
- Informal prose that paraphrases a formal result without every qualifier

## Do NOT flag
- Formatting, typesetting, or capitalization issues
- References to equations or sections outside your assigned text (they exist elsewhere)
- Trivial observations that any reader in the field would immediately resolve

## Output format
Write findings as a JSON array. Each issue is a JSON object with these fields:

    title            -- short descriptive title
    quote            -- exact verbatim quote from the paper, character-for-character, preserving any LaTeX
    explanation      -- your reasoning
    comment_type     -- "technical" or "logical"
    confidence       -- "high", "medium", or "low"
    source_section   -- section name where issue appears
    related_sections -- list of other sections involved (may be empty)

If you find no issues, write an empty array: []
