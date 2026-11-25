import csv
import random
from collections import defaultdict
from pathlib import Path

INPUT_FILE = Path(
    "benchmarks/review_analysis/comment_quality_pilot.csv"
)

OUTPUT_FILE = Path(
    "benchmarks/review_analysis/comment_quality_sample.csv"
)

METHODS = [
    "zero_shot",
    "local",
    "progressive",
    "progressive_full",
]

SAMPLE_PER_METHOD = 5
RANDOM_SEED = 42

with INPUT_FILE.open("r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    fieldnames = reader.fieldnames

by_method = defaultdict(list)

for row in rows:
    by_method[row["method"]].append(row)

random.seed(RANDOM_SEED)

sampled_rows = []

for method in METHODS:
    method_rows = by_method[method]
    n = min(SAMPLE_PER_METHOD, len(method_rows))
    sampled_rows.extend(random.sample(method_rows, n))

with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(sampled_rows)

print(f"Done! Sampled {len(sampled_rows)} comments.")

for method in METHODS:
    count = sum(row["method"] == method for row in sampled_rows)
    print(f"{method}: {count}")

print(f"Saved to: {OUTPUT_FILE}")
