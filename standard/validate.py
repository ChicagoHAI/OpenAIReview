#!/usr/bin/env python3
"""Validate a file against the Anchored Review Format.

This checker uses only the Python standard library, so you can run it without
installing anything:

    python validate.py my_review.json

It prints clear, line-by-line diagnostics and exits 0 if the file is valid,
1 if it is not. Warnings point out recommended fields you left out; they do
not fail the file unless you pass --strict.

See README.md for the full format description.
"""

import argparse
import json
import sys

REQUIRED_TOP = ("standard_version", "comments")
RECOMMENDED_TOP = ("standard", "paper_id", "system")
REQUIRED_COMMENT = ("quote", "explanation")
RECOMMENDED_COMMENT = ("title",)


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)


def _is_nonempty_str(value):
    return isinstance(value, str) and value.strip() != ""


def validate(data, report):
    """Run all checks on the parsed JSON, recording errors and warnings."""
    if not isinstance(data, dict):
        report.error(
            f"Top level must be a JSON object, got {type(data).__name__}. "
            "Wrap your comments like {\"standard_version\": \"1.0\", \"comments\": [...]}."
        )
        return

    for key in REQUIRED_TOP:
        if key not in data:
            report.error(f"Missing required top-level field: \"{key}\".")

    if "standard_version" in data and not _is_nonempty_str(data["standard_version"]):
        report.error("\"standard_version\" must be a non-empty string, e.g. \"1.0\".")

    for key in RECOMMENDED_TOP:
        if key not in data:
            report.warn(f"Recommended top-level field missing: \"{key}\".")

    paragraphs = data.get("paragraphs")
    n_paragraphs = None
    if paragraphs is not None:
        if not isinstance(paragraphs, list):
            report.error("\"paragraphs\" must be an array if present.")
        else:
            n_paragraphs = len(paragraphs)

    comments = data.get("comments")
    if comments is None:
        return  # already reported as a missing required field
    if not isinstance(comments, list):
        report.error("\"comments\" must be an array.")
        return
    if not comments:
        report.warn("\"comments\" is empty. A review with no comments scores zero detections.")

    for i, comment in enumerate(comments):
        _validate_comment(comment, i, n_paragraphs, report)


def _validate_comment(comment, i, n_paragraphs, report):
    where = f"comments[{i}]"
    if not isinstance(comment, dict):
        report.error(f"{where} must be an object, got {type(comment).__name__}.")
        return

    for key in REQUIRED_COMMENT:
        if key not in comment:
            report.error(f"{where} is missing required field \"{key}\".")
        elif not _is_nonempty_str(comment[key]):
            report.error(f"{where}.{key} must be a non-empty string.")

    for key in RECOMMENDED_COMMENT:
        if key not in comment:
            report.warn(f"{where} is missing recommended field \"{key}\".")

    pidx = comment.get("paragraph_index")
    if pidx is not None:
        if not isinstance(pidx, int) or isinstance(pidx, bool):
            report.error(f"{where}.paragraph_index must be an integer or null.")
        elif pidx < 0:
            report.error(f"{where}.paragraph_index must be >= 0.")
        elif n_paragraphs is not None and pidx >= n_paragraphs:
            report.error(
                f"{where}.paragraph_index is {pidx} but only {n_paragraphs} "
                "paragraphs were provided."
            )


def main():
    parser = argparse.ArgumentParser(
        description="Validate a file against the Anchored Review Format."
    )
    parser.add_argument("file", help="Path to the JSON file to validate.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as failures.",
    )
    args = parser.parse_args()

    try:
        with open(args.file, encoding="utf-8") as f:
            raw = f.read()
    except OSError as e:
        print(f"✗ Could not read {args.file}: {e}", file=sys.stderr)
        return 1

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"✗ {args.file} is not valid JSON: {e}", file=sys.stderr)
        return 1

    report = Report()
    validate(data, report)

    for w in report.warnings:
        print(f"  warning: {w}")
    for err in report.errors:
        print(f"  error:   {err}")

    n_comments = len(data["comments"]) if isinstance(data, dict) and isinstance(data.get("comments"), list) else 0
    failed = bool(report.errors) or (args.strict and report.warnings)

    print()
    if failed:
        why = "errors" if report.errors else "warnings (--strict)"
        print(f"✗ INVALID — {len(report.errors)} error(s), {len(report.warnings)} warning(s). Fix the {why} above.")
        return 1

    suffix = f", {len(report.warnings)} warning(s)" if report.warnings else ""
    print(f"✓ VALID — {n_comments} comment(s){suffix}. Ready to submit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
