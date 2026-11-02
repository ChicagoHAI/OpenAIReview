#!/usr/bin/env python3
"""Fill in the paper text for rows whose license does not allow redistribution.

For each row with `text_included == False`, this downloads the paper's LaTeX
source from arXiv, rebuilds the clean paper with the same parser the benchmark
used, re-applies the listed edits, truncates to the review-input length, and
checks all three texts against the SHA-256 hashes stored in the row.

Requires `pip install openaireview==0.3.0 datasets`.

Usage:
  python rebuild.py --out rebuilt.jsonl                 # from the Hub
  python rebuild.py --data test.jsonl --out rebuilt.jsonl
"""

from __future__ import annotations

import argparse
import hashlib
import json
import tarfile
import tempfile
import time
import urllib.request
from pathlib import Path

from reviewer.parsers import parse_document
from reviewer.utils import count_tokens, truncate_text

REPO_ID = "ChicagoHAI/openaireview-perturbation"
MAX_TOKENS = 13000


def find_main_tex(directory: Path) -> Path | None:
    """Pick the root .tex file the way the benchmark pipeline did."""
    tex_files = list(directory.rglob("*.tex"))
    if not tex_files:
        return None
    roots = [f for f in tex_files if r"\documentclass" in f.read_text(errors="ignore")]
    candidates = roots or tex_files
    for preferred in ("main.tex", "paper.tex", "manuscript.tex", "article.tex"):
        for f in candidates:
            if f.name.lower() == preferred:
                return f
    return max(candidates, key=lambda f: f.stat().st_size)


def clean_paper(arxiv_id: str, workdir: Path) -> str:
    req = urllib.request.Request(f"https://arxiv.org/src/{arxiv_id}",
                                 headers={"User-Agent": "openaireview-perturbation-rebuild/1.0"})
    tarball = workdir / f"{arxiv_id}.tar.gz"
    tarball.write_bytes(urllib.request.urlopen(req, timeout=120).read())
    src = workdir / arxiv_id
    src.mkdir(exist_ok=True)
    with tarfile.open(tarball) as tf:
        tf.extractall(src, filter="data")
    main = find_main_tex(src)
    if main is None:
        raise RuntimeError(f"{arxiv_id}: no .tex file in source")
    _, content, _ = parse_document(str(main))
    return content


def apply_edits(clean: str, edits: list[dict]) -> str:
    text = clean
    for e in sorted(edits, key=lambda e: e["offset"], reverse=True):
        text = text[:e["offset"]] + e["perturbed"] + text[e["offset"] + len(e["original"]):]
    return text


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", type=Path, help="local JSONL export (default: download from the Hub)")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    if args.data:
        rows = [json.loads(line) for line in args.data.open()]
    else:
        from datasets import load_dataset
        rows = list(load_dataset(REPO_ID, split="test"))

    cache: dict[str, str] = {}
    failed = 0
    with tempfile.TemporaryDirectory() as tmp:
        for row in rows:
            if row["text_included"]:
                continue
            aid = row["arxiv_id"]
            try:
                if aid not in cache:
                    cache[aid] = clean_paper(aid, Path(tmp))
                    time.sleep(3)  # arXiv asks for at most one request every 3 seconds
                clean = cache[aid]
                perturbed = apply_edits(clean, row["perturbations"])
                review_input = truncate_text(perturbed, MAX_TOKENS) if count_tokens(perturbed) > MAX_TOKENS else perturbed
                for name, text in (("clean", clean), ("perturbed", perturbed), ("review_input", review_input)):
                    if sha256(text) != row[f"{name}_sha256"]:
                        raise RuntimeError(f"{name} text does not match its hash")
                row.update(clean_paper=clean, perturbed_paper=perturbed, review_input=review_input)
                print(f"ok      {row['id']}")
            except Exception as e:
                failed += 1
                print(f"FAILED  {row['id']}: {e}")

    with args.out.open("w") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} rows to {args.out}; {failed} rows could not be rebuilt")


if __name__ == "__main__":
    main()
