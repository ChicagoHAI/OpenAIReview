import csv
import json
from pathlib import Path

SOURCE_FILE = Path("benchmarks/viz_data/targeting-interventions-networks.json")
OUTPUT_FILE = Path("benchmarks/review_analysis/comment_quality_pilot.csv")

METHODS = [
    "zero_shot",
    "local",
    "progressive",
    "progressive_full",
]

# Manual semantic overlap with a Refine ground-truth issue.
# This is NOT the benchmark's automatic recall label.
#
# Tuple format:
# (ground_truth_match, correctness, specificity,
#  justification, actionability, substantiveness, notes)
ANNOTATIONS = {
    ("zero_shot", "pred_5"): (
        "no", 3, 4, 4, 3, 3,
        "Raises a legitimate scope question about the w<0 case, but does not establish a flaw. The concern is plausible and would benefit from an explicit clarification or proof."
    ),
    ("zero_shot", "pred_0"): (
        "no", 5, 5, 5, 5, 3,
        "Correctly identifies that the cosine-similarity definition omits the norm of the second vector and cross-checks the intended standard definition against later usage."
    ),
    ("zero_shot", "pred_4"): (
        "no", 4, 4, 4, 4, 2,
        "The underlying binding-budget argument is defensible, but the reviewer reasonably identifies that the w<0 case is terse and would benefit from a more explicit step showing why some coordinate can still move toward -1."
    ),
    ("zero_shot", "pred_2"): (
        "no", 3, 4, 3, 4, 3,
        "The concern is plausible but unresolved: the reviewer notes that the welfare simplification is non-trivial but does not establish that the formula is wrong. A derivation or citation would address the concern."
    ),
    ("zero_shot", "pred_1"): (
        "yes", 5, 5, 5, 5, 4,
        "Identifies the eigenvector-sign ambiguity that also appears in the Refine ground truth. The comment explains why an absolute cosine or an explicit orientation convention is needed."
    ),

    ("local", "pred_7"): (
        "no", 4, 4, 4, 4, 3,
        "The requested derivation is reasonable because the variable transformation is asserted without showing the intermediate first-order condition. The concern is about reproducibility and exposition rather than a demonstrated error."
    ),
    ("local", "pred_4"): (
        "no", 5, 5, 5, 4, 3,
        "Correctly separates individual strict concavity from the spectral-radius assumption. The first-order condition characterizes each best response independently, while Assumption 2 is needed for equilibrium-level properties such as uniqueness and stability."
    ),
    ("local", "pred_23"): (
        "no", 2, 4, 2, 2, 2,
        "The comment is based partly on treating b_i as if it were the intervention itself. In the paper b_i is the transformed standalone-return variable, so b_i*=0 can correspond to changing the underlying endowment to tau and inducing zero effort."
    ),
    ("local", "pred_3"): (
        "no", 3, 4, 4, 3, 3,
        "Provides a useful qualification about structured network classes, but it does not show that the paper's genericity statement is false for the continuous weighted-matrix setting used in the model."
    ),
    ("local", "pred_21"): (
        "no", 1, 5, 2, 2, 2,
        "The equality is already supplied by the binding-budget equation from Theorem 1, which the proof explicitly references. The criticism mainly reflects missing local context rather than a defect in the paper."
    ),

    ("progressive", "pred_8"): (
        "no", 5, 5, 5, 5, 2,
        "Correctly identifies the undefined alpha_2^* term and uses the following line to infer the intended alpha_2. The fix is precise but minor."
    ),
    ("progressive", "pred_1"): (
        "no", 5, 5, 5, 5, 3,
        "Correctly identifies the missing norm in the cosine-similarity definition and appropriately notes that later unit-eigenvector usage can mask the problem."
    ),
    ("progressive", "pred_6"): (
        "no", 5, 5, 5, 5, 2,
        "Correctly identifies that beta is a scalar but is typeset in bold in this equation. The correction is exact and low-impact."
    ),
    ("progressive", "pred_0"): (
        "no", 5, 5, 5, 5, 2,
        "Correctly identifies the variable-substitution typo, pinpoints the intended tilde-b term from context, and gives the exact correction."
    ),
    ("progressive", "pred_7"): (
        "no", 4, 5, 4, 5, 1,
        "Precisely identifies malformed summation notation and gives the intended form. Because the issue may partly reflect rendering or extraction rather than substantive mathematics, correctness is slightly qualified and substantiveness is low."
    ),

    ("progressive_full", "pred_2"): (
        "no", 1, 4, 2, 1, 1,
        "The comment precisely locates the passage but explicitly concludes that the apparent problem is only a passage-boundary artifact and is not a genuine error. It should have been filtered out."
    ),
    ("progressive_full", "pred_6"): (
        "no", 1, 5, 2, 1, 1,
        "The comment works through the sign issue but its own reasoning establishes that the formula is correct under Assumption 2. The supposed error is therefore not genuine and should have been filtered out."
    ),
    ("progressive_full", "pred_7"): (
        "no", 2, 4, 2, 2, 1,
        "The comment initially derives a contradiction, then corrects its own reasoning and concludes that the paper's statement is consistent. The remaining request for clarity is weak relative to the lengthy self-correction."
    ),
    ("progressive_full", "pred_16"): (
        "yes", 5, 5, 5, 5, 2,
        "Matches the Refine Lagrangian typo. The reviewer cross-checks the objective and subsequent first-order condition and correctly infers that the status-quo component should be squared."
    ),
    ("progressive_full", "pred_19"): (
        "no", 4, 5, 4, 5, 1,
        "Precisely identifies malformed summation notation and supplies the intended expression. The issue is easy to fix but may be a rendering artifact and is substantively trivial."
    ),

    # Previously annotated example outside the 20-comment random pilot.
    ("progressive", "pred_2"): (
        "yes", 5, 5, 5, 5, 2,
        "Matches the Refine maximizer-versus-minimizer issue and identifies the exact contradiction between the minimization problems and the following wording."
    ),
}

FIELDNAMES = [
    "comment_id",
    "paper",
    "method",
    "title",
    "quote",
    "explanation",
    "comment_type",
    "paragraph_index",
    "ground_truth_match",
    "correctness",
    "specificity",
    "justification",
    "actionability",
    "substantiveness",
    "notes",
]

with SOURCE_FILE.open("r", encoding="utf-8") as f:
    data = json.load(f)

rows = []

for method in METHODS:
    method_data = data["methods"][method]

    for comment in method_data.get("comments", []):
        annotation = ANNOTATIONS.get((method, comment["id"]))

        row = {
            "comment_id": comment.get("id", ""),
            "paper": data.get("slug", ""),
            "method": method,
            "title": comment.get("title", ""),
            "quote": comment.get("quote", ""),
            "explanation": comment.get("explanation", ""),
            "comment_type": comment.get("comment_type", ""),
            "paragraph_index": comment.get("paragraph_index", ""),
            "ground_truth_match": "",
            "correctness": "",
            "specificity": "",
            "justification": "",
            "actionability": "",
            "substantiveness": "",
            "notes": "",
        }

        if annotation is not None:
            (
                row["ground_truth_match"],
                row["correctness"],
                row["specificity"],
                row["justification"],
                row["actionability"],
                row["substantiveness"],
                row["notes"],
            ) = annotation

        rows.append(row)

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    writer.writeheader()
    writer.writerows(rows)

annotated_count = sum(
    1 for row in rows if row["correctness"] != ""
)

print(f"Done! Wrote {len(rows)} AI review comments to:")
print(OUTPUT_FILE)
print(f"Human annotations completed: {annotated_count}")
