# Comment Quality Pilot

## Research question

Existing OpenAIReview benchmarks primarily measure whether a reviewer
recalls known issues. This pilot asks a different question:

**When an AI reviewer produces an individual comment, how useful is that
comment as feedback to an author?**

The pilot evaluates comments along five dimensions:

- correctness
- specificity
- justification
- actionability
- substantiveness

The first four dimensions are averaged into `mean quality`.
Substantiveness is reported separately so that a perfectly written
comment about a trivial typo is not treated as equivalent to a comment
about a major technical issue.

## Data

The pilot uses 20 comments from
`targeting-interventions-networks.json`, with five comments sampled from
each review method:

- Zero Shot
- Local
- Progressive
- Progressive Full

The sample was generated with a fixed random seed (`42`) for
reproducibility.

`ground_truth_match` is a manual semantic-overlap annotation with the
existing Refine ground-truth issues. It is not the benchmark's automatic
recall label.

## Results

| Method | n | Correctness | Specificity | Justification | Actionability | Mean quality | Substantiveness | Low-correctness comments | Minor/trivial comments | GT overlaps |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| zero_shot | 5 | 4.00 | 4.40 | 4.20 | 4.20 | 4.20 | 3.00 | 0 | 1 | 1 |
| local | 5 | 3.00 | 4.40 | 3.40 | 3.00 | 3.45 | 2.60 | 2 | 2 | 0 |
| progressive | 5 | 4.80 | 5.00 | 4.80 | 5.00 | 4.90 | 2.00 | 0 | 4 | 0 |
| progressive_full | 5 | 2.60 | 4.60 | 3.00 | 2.80 | 3.25 | 1.20 | 3 | 5 | 1 |

## Pilot observations

- In this 20-comment pilot, **progressive** has the
  highest mean comment-quality score
  (4.90/5).
- **progressive_full** has the lowest mean correctness
  (2.60/5).
- **zero_shot** has the highest mean
  substantiveness (3.00/5).
- Across the full pilot, 5 of 20 comments have
  correctness scores of 2 or below.
- 12 of 20 comments concern issues rated minor or trivial
  (`substantiveness <= 2`).
- 2 of 20 sampled comments have manual semantic overlap with a
  Refine ground-truth issue.

A recurring failure mode is **self-invalidating feedback**: a reviewer
raises a criticism, reasons through the issue, and then effectively
establishes that the paper is correct, but still surfaces the criticism
as a final review comment.

A second pattern is that high correctness and high writing quality do
not necessarily imply high value. Several comments precisely identify
small notation or typesetting problems. This motivates reporting
substantiveness separately from comment-writing quality.

## Limitations

This is an exploratory pilot rather than a benchmark result.

- It uses one paper only.
- It contains five comments per review method.
- Scores come from a single annotation pass.
- The rubric has not yet been tested for inter-rater reliability.
- Ground-truth overlap is manually assessed.
- Some apparent notation problems may arise from document extraction or
  rendering rather than the source PDF itself.

The next step would be to expand the annotations across additional
papers and compare human ratings with an automated multidimensional
comment-quality judge.
