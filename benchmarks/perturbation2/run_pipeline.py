#!/usr/bin/env python3
"""Run perturb → review → score on proof-pile arxiv papers.

Results layout:
  results/
    perturb/
      <error-type>/
        paper_001/
        paper_002/
        ...
    <review-model>/
      <error-type>/
        <method>/
          paper_001/
            review/
            <score-method>/
              score/
          paper_002/
            ...
"""

import re
import json
import subprocess
from pathlib import Path

from datasets import load_dataset

# ---------------------------------------------------------------------------
# Config — edit these as needed
# ---------------------------------------------------------------------------

MAX_PAPERS = 2

ERROR_TYPE = "all"  # "surface" or "formal"
SCORE_METHOD = "llm" # llm, fuzzy, semantic

PERTURB_MODEL = "anthropic/claude-opus-4-6"  # only used when GENERATE_METHOD = "llm"

REVIEW_MODELS = [
    # "google/gemini-3.1-pro-preview",
    "anthropic/claude-opus-4-6",
    # "anthropic/claude-sonnet-4-6",
    # "openai/gpt-4o",
    # "google/gemini-2.5-pro",
]

SCORE_MODEL = "anthropic/claude-opus-4-6" # only used when VALIDATE_METHOD = "llm"

REVIEW_METHODS = [
    "zero_shot",
    "local",
    "progressive",
]

RESULTS_DIR = Path("results")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def paper_length(paper: dict) -> int:
    text = re.sub(r'\\[a-zA-Z]+\*?', ' ', paper['text'])
    text = re.sub(r'[\{\}\$\[\]]', ' ', text)
    return len(text.split())


def model_slug(model: str) -> str:
    """e.g. 'anthropic/claude-opus-4-6' -> 'claude-opus-4-6'"""
    return model.split("/")[-1]


def run(cmd: list[str]) -> int:
    print(f"    $ {' '.join(str(c) for c in cmd)}")
    return subprocess.run(cmd).returncode


def load_papers(length) -> list[dict]:
    print("Loading proof-pile dataset (streaming)...")
    ds = load_dataset("hoskinson-center/proof-pile", split="train", streaming=True)

    papers_short = []
    papers_medium = []
    papers_long = []
    papers_all = []

    for paper in ds:
        meta = json.loads(paper["meta"]) if isinstance(paper["meta"], str) else paper["meta"]
        if meta.get("config", "") == "arxiv":
            papers_all.append(paper)
            if paper_length(paper) > 2000 and paper_length(paper) <= 7000:
                papers_short.append(paper)
            elif paper_length(paper) > 7000 and paper_length(paper) <= 17000:
                papers_medium.append(paper)
            else:
                papers_long.append(paper)
            if len(papers_all) >= MAX_PAPERS:
                break

    if length == "short":
        papers = papers_short
    elif length == "medium":
        papers = papers_medium
    else:
        papers = papers_long

    print(f"Collected {len(papers)} arxiv papers\n")
    return papers


# ---------------------------------------------------------------------------
# Pipeline stages
# ---------------------------------------------------------------------------

def perturb(papers: list[dict]) -> None:
    """Generate seeded perturbations for each paper."""
    RESULTS_DIR.mkdir(exist_ok=True)

    for i, paper in enumerate(papers, start=1):
        paper_label = f"paper_{i:03d}"
        perturb_dir = RESULTS_DIR / "perturb" / ERROR_TYPE / paper_label
        perturb_dir.mkdir(parents=True, exist_ok=True)

        print(f"{'='*60}")
        print(f"Paper {i:03d}/{len(papers)}  ({paper_length(paper):,} words)")
        print(f"{'='*60}")

        tmp_path = perturb_dir / f"paper_{i:03d}.md"
        tmp_path.write_text(paper["text"])

        print(f"\n  [1] Perturb  (model: {model_slug(PERTURB_MODEL)})")
        rc = run(["openaireview", "perturb", str(tmp_path),
                "--error_type", ERROR_TYPE,
                "--output-dir", str(perturb_dir),
                "--model", PERTURB_MODEL])
        if rc != 0:
            print(f"  perturb failed (exit {rc}), skipping paper")


def review(papers: list[dict]) -> None:
    """Review each corrupted paper with every (model, method) combination."""
    for i, paper in enumerate(papers, start=1):
        paper_label = f"paper_{i:03d}"
        perturb_dir = RESULTS_DIR / "perturb" / ERROR_TYPE / paper_label

        corrupted = max(perturb_dir.glob("*_corrupted.md"), key=lambda p: p.stat().st_mtime, default=None)
        if not corrupted:
            print(f"  No corrupted paper found for {ERROR_TYPE}/{paper_label}, skipping")
            continue

        print(f"{'='*60}")
        print(f"Paper {i:03d}/{len(papers)}  ({paper_length(paper):,} words)")
        print(f"{'='*60}")

        for model in REVIEW_MODELS:
            for method in REVIEW_METHODS:
                review_dir = RESULTS_DIR / model_slug(model) / ERROR_TYPE / method / paper_label / "review"
                review_dir.mkdir(parents=True, exist_ok=True)

                print(f"\n  [2] Review  ({model_slug(model)} / {ERROR_TYPE} / {method})")
                rc = run(["openaireview", "review", str(corrupted),
                          "--method", method,
                          "--output-dir", str(review_dir),
                          "--model", model])
                if rc != 0:
                    print(f"  review failed (exit {rc}), skipping")


def score(papers: list[dict]) -> None:
    """Score each review against its perturbation manifest."""
    for i, paper in enumerate(papers, start=1):
        paper_label = f"paper_{i:03d}"
        perturb_dir = RESULTS_DIR / "perturb" / ERROR_TYPE / paper_label

        manifest = max(perturb_dir.glob("*_perturbations.json"), key=lambda p: p.stat().st_mtime, default=None)
        if not manifest:
            print(f"  No manifest found for {ERROR_TYPE}/{paper_label}, skipping")
            continue

        print(f"{'='*60}")
        print(f"Paper {i:03d}/{len(papers)}  ({paper_length(paper):,} words)")
        print(f"{'='*60}")

        for model in REVIEW_MODELS:
            for review_method in REVIEW_METHODS:
                review_dir = RESULTS_DIR / model_slug(model) / ERROR_TYPE / review_method / paper_label / "review"

                score_dir = RESULTS_DIR / model_slug(model) / ERROR_TYPE / review_method / paper_label / SCORE_METHOD / "score"
                score_dir.mkdir(parents=True, exist_ok=True)

                review_json = max(review_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, default=None)
                if not review_json:
                    print(f"  No review found for {model_slug(model)}/{ERROR_TYPE}/{review_method}/{paper_label}, skipping")
                    continue

                print(f"\n  [3] Score   ({model_slug(model)} / {ERROR_TYPE} / {review_method} / {SCORE_METHOD})")
                rc = run(["openaireview", "score", str(manifest), str(review_json),
                        "--model", SCORE_MODEL,
                        "--method", SCORE_METHOD,
                        "--output-dir", str(score_dir)])
                if rc != 0:
                    print(f"  score failed (exit {rc}), skipping")

        print(f"\n  Done: {paper_label}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    papers = load_papers("short")
    perturb(papers)
    review(papers)
    score(papers)
    print(f"\nAll done. Results in {RESULTS_DIR}/")


if __name__ == "__main__":
    main()
