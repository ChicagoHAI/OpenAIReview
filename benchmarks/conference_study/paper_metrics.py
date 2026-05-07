#!/usr/bin/env python
"""Compute paper-level metrics (word count, equation density) for
normalization in the report.

Reads the combined scale-up manifest, parses each downloaded PDF with
the project's shared parser, and writes metrics back to the manifest
(word_count, equation_count, equations_per_1k_words).

Equation count is a rough heuristic on extracted text: lines that look
math-like (inline ` = ` occurrences + display blocks). PDF extraction
loses a lot of LaTeX formatting, so this is only a density proxy, not
an exact count.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_MANIFEST = HERE / "manifests" / "combined.json"

# Make the openaireview package importable when running from this dir.
sys.path.insert(0, str(HERE.parent.parent / "src"))

EQ_INLINE_RX = re.compile(r"(?<![<>=!])=(?!=)")  # `=` that isn't `==`, `<=`, etc.


def compute_metrics(text: str) -> dict:
    words = text.split()
    word_count = len(words)
    # Heuristic: count `=` occurrences as rough stand-in for equation count.
    # PDF→text extraction destroys LaTeX markers, so this is just density.
    eq_count = len(EQ_INLINE_RX.findall(text))
    return {
        "word_count": word_count,
        "equation_count": eq_count,
        "equations_per_1k_words": round(eq_count / max(1, word_count) * 1000, 2),
    }


def process(manifest_path: Path, force: bool = False) -> None:
    from reviewer.parsers import parse_document

    manifest = json.loads(manifest_path.read_text())
    papers = manifest["papers"]

    to_do = []
    for p in papers:
        if not p.get("pdf_path"):
            continue  # skip papers that failed to download
        if not force and p.get("word_count"):
            continue
        to_do.append(p)

    print(f"Computing metrics for {len(to_do)} papers "
          f"(of {len(papers)} in manifest)")

    for i, p in enumerate(to_do):
        pdf = HERE / p["pdf_path"]
        if not pdf.exists():
            print(f"  [{i+1}/{len(to_do)}] MISS  {p['slug']}  ({pdf})")
            continue
        try:
            _title, text, _was_ocr = parse_document(pdf)
        except Exception as e:
            print(f"  [{i+1}/{len(to_do)}] FAIL  {p['slug']}  ({type(e).__name__}: {e})")
            continue
        m = compute_metrics(text)
        p.update(m)
        print(f"  [{i+1}/{len(to_do)}] OK    {p['slug']}  "
              f"words={m['word_count']:>5}  eq_density={m['equations_per_1k_words']}")

    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"\nManifest updated: {manifest_path}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    ap.add_argument("--force", action="store_true",
                    help="Recompute metrics even if already present.")
    args = ap.parse_args()
    process(args.manifest, force=args.force)


if __name__ == "__main__":
    main()
