#!/usr/bin/env python3
"""Run perturb → review → score on proof-pile arxiv papers.

Results are saved to:
  results/
    paper_001/
      perturb/   (manifest, corrupted paper, clean paper)
      review/    (review JSON)
      score/     (score JSON)
    paper_002/
      ...
"""

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from datasets import load_dataset

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

MAX_PAPERS = 2
RESULTS_DIR = Path("results")
MODEL = os.environ.get("MODEL", "anthropic/claude-opus-4-6")
REVIEW_METHOD = os.environ.get("REVIEW_METHOD", "progressive")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def paper_length(paper: dict) -> int:
    return len(paper["text"])


def run(cmd: list[str]) -> int:
    print(f"    $ {' '.join(str(c) for c in cmd)}")
    return subprocess.run(cmd).returncode


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    # Load papers
    print("Loading proof-pile dataset (streaming)...")
    ds = load_dataset("hoskinson-center/proof-pile", split="train", streaming=True)

    papers = []
    for paper in ds:
        meta = json.loads(paper["meta"]) if isinstance(paper["meta"], str) else paper["meta"]
        if meta.get("config", "") == "arxiv":
            papers.append(paper)
            if len(papers) >= MAX_PAPERS:
                break

    print(f"Collected {len(papers)} arxiv papers\n")

    RESULTS_DIR.mkdir(exist_ok=True)

    for i, paper in enumerate(papers, start=1):
        paper_dir = RESULTS_DIR / f"paper_{i:03d}"
        perturb_dir = paper_dir / "perturb"
        review_dir = paper_dir / "review"
        score_dir = paper_dir / "score"

        for d in (perturb_dir, review_dir, score_dir):
            d.mkdir(parents=True, exist_ok=True)

        print(f"{'='*60}")
        print(f"Paper {i:03d}/{MAX_PAPERS}  ({paper_length(paper):,} chars)")
        print(f"{'='*60}")

        # Write paper text to a named temp file so the CLI can parse it
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", prefix=f"paper_{i:03d}_", delete=False
        )
        tmp.write(paper["text"])
        tmp.close()
        tmp_path = Path(tmp.name)

        try:
            # ------------------------------------------------------------------
            # Step 1: Perturb
            # ------------------------------------------------------------------
            print(f"\n  [1/3] Perturb")
            rc = run(["openaireview", "perturb", str(tmp_path),
                      "--output-dir", str(perturb_dir),
                      "--model", MODEL])
            if rc != 0:
                print(f"  perturb failed (exit {rc}), skipping")
                continue

            manifest = next(perturb_dir.glob("*_perturbations.json"), None)
            corrupted = next(perturb_dir.glob("*_corrupted.md"), None)
            if not manifest or not corrupted:
                print("  perturb outputs missing, skipping")
                continue

            # ------------------------------------------------------------------
            # Step 2: Review the corrupted paper
            # ------------------------------------------------------------------
            print(f"\n  [2/3] Review")
            rc = run(["openaireview", "review", str(corrupted),
                      "--method", REVIEW_METHOD,
                      "--output-dir", str(review_dir),
                      "--model", MODEL])
            if rc != 0:
                print(f"  review failed (exit {rc}), skipping")
                continue

            review_json = next(review_dir.glob("*.json"), None)
            if not review_json:
                print("  review output missing, skipping")
                continue

            # ------------------------------------------------------------------
            # Step 3: Score
            # ------------------------------------------------------------------
            print(f"\n  [3/3] Score")
            rc = run(["openaireview", "score", str(manifest), str(review_json)])
            if rc != 0:
                print(f"  score failed (exit {rc}), skipping")
                continue

            # score saves next to the manifest — move it to score/
            score_file = next(perturb_dir.glob("*_score.json"), None)
            if score_file:
                shutil.move(str(score_file), str(score_dir / score_file.name))

            print(f"\n  Saved to {paper_dir}")

        finally:
            tmp_path.unlink(missing_ok=True)

    print(f"\nDone. Results in {RESULTS_DIR}/")


if __name__ == "__main__":
    main()
