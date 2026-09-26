# Comment Quality Rubric

This rubric evaluates the quality of individual AI-generated peer-review comments.

The rubric is intentionally separate from benchmark recall. A comment may fail to match an existing ground-truth comment while still identify a valid issue, and a comment may be highly specific while nevertheless being incorrect.

## 1. Correctness

Does the criticism itself hold given the paper and surrounding context?

**1 — Incorrect**  
The criticism is false, caused by a parsing/context artifact, or explicitly undermined by the reviewer's own reasoning.

**2 — Mostly incorrect**  
There may be a superficial concern, but the main criticism rests on a misunderstanding or unsupported inference.

**3 — Plausible but unresolved**  
The concern is reasonable, but the available evidence is insufficient to establish whether it is actually correct.

**4 — Mostly correct**  
The criticism is substantively correct, with a minor caveat, qualification, or uncertainty.

**5 — Clearly correct**  
The criticism is directly supported by the paper, mathematical reasoning, or clear contextual evidence.

## 2. Specificity

How precisely does the comment identify the problem?

**1 — Very vague**  
Does not identify a specific passage, claim, equation, or problem.

**2 — Broad**  
Identifies a general area of concern but not the exact problematic element.

**3 — Moderately specific**  
Identifies the relevant passage and general issue, but the precise mechanism is not fully stated.

**4 — Specific**  
Clearly identifies the problematic element and explains what is wrong with it.

**5 — Highly specific**  
Pinpoints the exact symbol, statement, assumption, equation, or logical step and precisely contrasts it with the correct or expected form.

## 3. Justification

How well does the comment explain why the criticism is warranted?

**1 — No justification**  
Merely asserts that something is wrong or unclear.

**2 — Weak justification**  
Provides a reason, but the reasoning is incomplete, speculative, self-undermining, or unsupported.

**3 — Adequate justification**  
Provides a plausible explanation, but important reasoning or evidence is missing.

**4 — Strong justification**  
Provides coherent reasoning tied to the paper, relevant definitions, equations, or surrounding context.

**5 — Excellent justification**  
Provides rigorous reasoning and independently verifies the issue using derivation, cross-reference, comparison with another passage, or other strong contextual evidence.

## 4. Actionability

Would the comment help an author improve the paper?

**1 — Not actionable**  
There is no genuine issue to fix, or the comment should have been filtered out entirely.

**2 — Weakly actionable**  
The author can see that the reviewer is dissatisfied, but it is unclear what should be changed.

**3 — Moderately actionable**  
The direction of revision is understandable, although the exact correction must be inferred.

**4 — Actionable**  
The comment gives a clear revision, clarification, or verification task.

**5 — Highly actionable**  
The comment identifies a precise correction or concrete revision and appropriately scopes what needs to change.

## 5. Substantiveness

How important is the issue identified by the comment?

**1 — Trivial**  
Purely cosmetic, formatting-related, rendering-related, or inconsequential.

**2 — Minor**  
A small typo or notation issue with negligible effect on interpretation or results.

**3 — Moderate**  
A meaningful clarity, presentation, reproducibility, or localized technical issue.

**4 — Substantive**  
A technical or logical issue that could affect interpretation, derivation, or argumentation.

**5 — Major**  
An issue that materially affects a central result, conclusion, or core argument.

## Important distinction

`ground_truth_match` and comment quality are different variables.

In this pilot, `ground_truth_match` means manual semantic overlap with an existing Refine ground-truth issue. It is not the benchmark's automatic recall label.

A comment that does not match the benchmark ground truth is not automatically incorrect. Likewise, matching a benchmark issue does not automatically imply that the generated review comment is well-written or useful.
