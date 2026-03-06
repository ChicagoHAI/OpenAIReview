#!/usr/bin/env python3
"""Gather and merge all sub-agent comment JSON files from a review workspace.

Usage:
    python3 ~/.claude/commands/openaireview/scripts/consolidate_comments.py /tmp/<slug>_review

Reads every .json file in <review_dir>/comments/, annotates each issue with
its source file, and prints the merged array to stdout.
"""

import json
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("Usage: consolidate_comments.py <review_dir>", file=sys.stderr)
        sys.exit(1)

    comments_dir = Path(sys.argv[1]) / "comments"
    if not comments_dir.exists():
        print("[]")
        return

    all_issues = []
    for f in sorted(comments_dir.glob("*.json")):
        try:
            issues = json.loads(f.read_text())
        except json.JSONDecodeError:
            print(f"WARNING: Could not parse {f.name}", file=sys.stderr)
            continue
        if not isinstance(issues, list):
            issues = [issues]
        for issue in issues:
            issue["_source_file"] = f.name
        all_issues.extend(issues)

    print(json.dumps(all_issues, indent=2))


if __name__ == "__main__":
    main()
