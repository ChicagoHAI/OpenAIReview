"""Validate the OpenReview benchmark file and optionally verify PDF download + parsing.

Does not call the review LLM — safe to run without API keys.

Usage:
    python benchmarks/openreview_benchmark/scripts/validate_openreview_benchmark.py
    python benchmarks/openreview_benchmark/scripts/validate_openreview_benchmark.py --parse-one
"""

import argparse
import json
import sys
import tempfile
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_TRACK_ROOT = _SCRIPT_DIR.parent
_DATA_DIR = _TRACK_ROOT / "data"
_REPO_ROOT = _SCRIPT_DIR.parents[3]
BENCHMARK = _DATA_DIR / "openreview_benchmark.jsonl"

if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from openreview_http import create_openreview_session

sys.path.insert(0, str(_REPO_ROOT / "src"))


def main():
    parser = argparse.ArgumentParser(description="Validate OpenReview benchmark JSONL")
    parser.add_argument(
        "--parse-one",
        action="store_true",
        help="Download first paper PDF and run reviewer.parsers.parse_document (no LLM)",
    )
    parser.add_argument(
        "--benchmark",
        type=Path,
        default=BENCHMARK,
        help=f"Path to JSONL (default: {BENCHMARK})",
    )
    args = parser.parse_args()

    path = args.benchmark
    if not path.exists():
        print(f"Missing file: {path}")
        sys.exit(1)

    papers = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            papers.append(json.loads(line))

    print(f"Loaded {len(papers)} papers from {path}\n")

    required = (
        "paper_id",
        "title",
        "pdf_url",
        "reviews",
        "venue",
    )
    errors = []
    for i, p in enumerate(papers):
        for key in required:
            if key not in p:
                errors.append(f"Line {i + 1} ({p.get('paper_id', '?')}): missing {key}")
        if p.get("reviews") is not None and len(p["reviews"]) == 0:
            errors.append(f"Paper {p.get('paper_id')}: no reviews")

    if errors:
        print("Validation errors:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)

    for p in papers:
        n = len(p["reviews"])
        d = p.get("num_discussions", len(p.get("discussions", [])))
        print(f"  OK  {p['paper_id']}: {p['title'][:55]}... | {n} reviews | {d} discussions")

    print("\nSchema check passed.")

    if not args.parse_one:
        print(
            "\nTo smoke-test PDF parsing for one paper, run:\n"
            "  python benchmarks/openreview_benchmark/scripts/validate_openreview_benchmark.py --parse-one\n"
            "\nTo run an actual review (needs API keys), download a PDF or use a local path:\n"
            "  openaireview review <path-or-url> --method zero_shot\n"
            "(OpenReview PDF URLs are not parsed as URLs by the CLI; use a downloaded file.)\n"
        )
        return

    first = papers[0]
    pdf_url = first["pdf_url"]
    print(f"\n--parse-one: fetching {pdf_url}")

    sess = create_openreview_session(mode="pdf", warmup_timeout=60.0, warmup_max_attempts=3)
    r = sess.get(pdf_url, timeout=120)
    if r.status_code != 200:
        print(f"HTTP {r.status_code}: {r.text[:200]}")
        sys.exit(1)

    from reviewer.parsers import parse_document

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(r.content)
        tmp_path = Path(tmp.name)

    try:
        title, text, was_ocr = parse_document(tmp_path, ocr="pymupdf")
        print(f"  Parsed title: {title[:80]}...")
        print(f"  Text length: {len(text)} chars, was_ocr={was_ocr}")
        print("  PDF parse OK.")
    finally:
        tmp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
