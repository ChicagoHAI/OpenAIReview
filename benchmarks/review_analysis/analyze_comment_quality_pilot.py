import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean

INPUT_FILE = Path(
    "benchmarks/review_analysis/comment_quality_sample.csv"
)

SUMMARY_FILE = Path(
    "benchmarks/review_analysis/comment_quality_summary.csv"
)

REPORT_FILE = Path(
    "benchmarks/review_analysis/COMMENT_QUALITY_RESULTS.md"
)

SCORED_FIELDS = [
    "correctness",
    "specificity",
    "justification",
    "actionability",
    "substantiveness",
]

QUALITY_FIELDS = [
    "correctness",
    "specificity",
    "justification",
    "actionability",
]

with INPUT_FILE.open("r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

if not rows:
    raise ValueError("The sample CSV is empty.")

missing = []

for row in rows:
    for field in SCORED_FIELDS:
        if row.get(field, "") == "":
            missing.append(
                (row["method"], row["comment_id"], field)
            )

if missing:
    preview = "\n".join(
        f"  {method}/{comment_id}: missing {field}"
        for method, comment_id, field in missing[:20]
    )
    raise ValueError(
        "Some sampled comments are still unannotated:\n"
        + preview
    )

for row in rows:
    for field in SCORED_FIELDS:
        row[field] = float(row[field])

    row["quality_mean"] = mean(
        row[field] for field in QUALITY_FIELDS
    )

by_method = defaultdict(list)

for row in rows:
    by_method[row["method"]].append(row)

method_order = [
    "zero_shot",
    "local",
    "progressive",
    "progressive_full",
]

summary_rows = []

for method in method_order:
    group = by_method[method]

    if not group:
        continue

    summary = {
        "method": method,
        "n": len(group),
        "correctness": mean(
            row["correctness"] for row in group
        ),
        "specificity": mean(
            row["specificity"] for row in group
        ),
        "justification": mean(
            row["justification"] for row in group
        ),
        "actionability": mean(
            row["actionability"] for row in group
        ),
        "quality_mean": mean(
            row["quality_mean"] for row in group
        ),
        "substantiveness": mean(
            row["substantiveness"] for row in group
        ),
        "low_correctness_count": sum(
            row["correctness"] <= 2
            for row in group
        ),
        "minor_or_trivial_count": sum(
            row["substantiveness"] <= 2
            for row in group
        ),
        "ground_truth_match_count": sum(
            row["ground_truth_match"] == "yes"
            for row in group
        ),
    }

    summary_rows.append(summary)

summary_fields = [
    "method",
    "n",
    "correctness",
    "specificity",
    "justification",
    "actionability",
    "quality_mean",
    "substantiveness",
    "low_correctness_count",
    "minor_or_trivial_count",
    "ground_truth_match_count",
]

with SUMMARY_FILE.open(
    "w",
    newline="",
    encoding="utf-8",
) as f:
    writer = csv.DictWriter(
        f,
        fieldnames=summary_fields
    )
    writer.writeheader()

    for row in summary_rows:
        out = row.copy()

        for field in [
            "correctness",
            "specificity",
            "justification",
            "actionability",
            "quality_mean",
            "substantiveness",
        ]:
            out[field] = f"{out[field]:.2f}"

        writer.writerow(out)

highest_quality = max(
    summary_rows,
    key=lambda row: row["quality_mean"]
)

lowest_correctness = min(
    summary_rows,
    key=lambda row: row["correctness"]
)

highest_substantiveness = max(
    summary_rows,
    key=lambda row: row["substantiveness"]
)

total_low_correctness = sum(
    row["low_correctness_count"]
    for row in summary_rows
)

total_minor = sum(
    row["minor_or_trivial_count"]
    for row in summary_rows
)

total_gt = sum(
    row["ground_truth_match_count"]
    for row in summary_rows
)

table_lines = [
    "| Method | n | Correctness | Specificity | Justification | Actionability | Mean quality | Substantiveness | Low-correctness comments | Minor/trivial comments | GT overlaps |",
    "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
]

for row in summary_rows:
    table_lines.append(
        "| {method} | {n} | {correctness:.2f} | "
        "{specificity:.2f} | {justification:.2f} | "
        "{actionability:.2f} | {quality_mean:.2f} | "
        "{substantiveness:.2f} | "
        "{low_correctness_count} | "
        "{minor_or_trivial_count} | "
        "{ground_truth_match_count} |".format(**row)
    )

report = f"""# Comment Quality Pilot

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

{chr(10).join(table_lines)}

## Pilot observations

- In this 20-comment pilot, **{highest_quality["method"]}** has the
  highest mean comment-quality score
  ({highest_quality["quality_mean"]:.2f}/5).
- **{lowest_correctness["method"]}** has the lowest mean correctness
  ({lowest_correctness["correctness"]:.2f}/5).
- **{highest_substantiveness["method"]}** has the highest mean
  substantiveness ({highest_substantiveness["substantiveness"]:.2f}/5).
- Across the full pilot, {total_low_correctness} of 20 comments have
  correctness scores of 2 or below.
- {total_minor} of 20 comments concern issues rated minor or trivial
  (`substantiveness <= 2`).
- {total_gt} of 20 sampled comments have manual semantic overlap with a
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
"""

REPORT_FILE.write_text(
    report,
    encoding="utf-8"
)

print("Done!")
print(f"Annotated sample: {len(rows)}/{len(rows)}")
print(f"Summary: {SUMMARY_FILE}")
print(f"Report: {REPORT_FILE}")
print()
print("Method summary:")

for row in summary_rows:
    print(
        f"- {row['method']}: "
        f"quality={row['quality_mean']:.2f}, "
        f"correctness={row['correctness']:.2f}, "
        f"substantiveness={row['substantiveness']:.2f}"
    )
