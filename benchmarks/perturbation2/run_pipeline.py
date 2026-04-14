#!/usr/bin/env python3
"""Run perturb → review → score on proof-pile arxiv papers.

Config is loaded from a YAML file (see configs/default.yaml). To run a
variant, copy default.yaml, edit, and point at the new file — committed
configs serve as the experiment log.

Usage:
  python run_pipeline.py configs/default.yaml

Results layout:
  <results-dir>/
    config.yaml                       # resolved config used for the run
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
            score/
              <score-method>/
          paper_002/
            ...
"""

import re
import json
import argparse
import subprocess
from dataclasses import MISSING, dataclass, field, asdict, fields
from pathlib import Path

import yaml
from datasets import load_dataset


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

@dataclass
class Config:
    max_papers: int = 2
    length: str = field(default="short", metadata={"choices": ["short", "medium", "long"]})
    error_type: str = field(default="all", metadata={"choices": ["surface", "formal", "all"]})
    score_method: str = field(default="llm", metadata={"choices": ["llm", "fuzzy", "semantic"]})
    perturb_model: str = "google/gemini-3-flash-preview"
    score_model: str = "google/gemini-3-flash-preview"
    review_models: list[str] = field(default_factory=lambda: ["google/gemini-3-flash-preview"])
    review_methods: list[str] = field(default_factory=lambda: ["zero_shot", "local", "progressive"])
    results_dir: str = "results"


def load_config(path: Path) -> Config:
    with path.open() as f:
        data = yaml.safe_load(f) or {}
    valid_keys = {f.name for f in fields(Config)}
    unknown = set(data) - valid_keys
    if unknown:
        raise ValueError(f"Unknown config keys in {path}: {sorted(unknown)}")
    for f in fields(Config):
        choices = f.metadata.get("choices")
        if choices is None or f.name not in data:
            continue
        if data[f.name] not in choices:
            raise ValueError(
                f"{path}: {f.name}={data[f.name]!r} not in choices {choices}"
            )
    return Config(**data)


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


def load_papers(cfg: Config) -> list[dict]:
    print("Loading proof-pile dataset (streaming)...")
    ds = load_dataset(
        "hoskinson-center/proof-pile",
        split="train",
        streaming=True,
        trust_remote_code=True,
    )

    papers_short: list[dict] = []
    papers_medium: list[dict] = []
    papers_long: list[dict] = []

    if cfg.length == "short":
        target = papers_short
    elif cfg.length == "medium":
        target = papers_medium
    else:
        target = papers_long

    inspected = 0
    for paper in ds:
        meta = json.loads(paper["meta"]) if isinstance(paper["meta"], str) else paper["meta"]
        if meta.get("config", "") != "arxiv":
            continue
        inspected += 1
        n = paper_length(paper)
        if 2000 < n <= 7000:
            papers_short.append(paper)
        elif 7000 < n <= 17000:
            papers_medium.append(paper)
        else:
            papers_long.append(paper)
        if len(target) >= cfg.max_papers:
            break

    print(
        f"Inspected {inspected} arxiv papers "
        f"(short={len(papers_short)}, medium={len(papers_medium)}, long={len(papers_long)})"
    )
    print(f"Collected {len(target)} arxiv papers for length={cfg.length}\n")
    return target


# ---------------------------------------------------------------------------
# Pipeline stages
# ---------------------------------------------------------------------------

def perturb(papers: list[dict], cfg: Config) -> None:
    """Generate seeded perturbations for each paper."""
    results_dir = Path(cfg.results_dir)
    results_dir.mkdir(exist_ok=True)

    for i, paper in enumerate(papers, start=1):
        paper_label = f"paper_{i:03d}"
        perturb_dir = results_dir / "perturb" / cfg.error_type / paper_label
        perturb_dir.mkdir(parents=True, exist_ok=True)

        print(f"{'='*60}")
        print(f"Paper {i:03d}/{len(papers)}  ({paper_length(paper):,} words)")
        print(f"{'='*60}")

        tmp_path = perturb_dir / f"paper_{i:03d}.md"
        tmp_path.write_text(paper["text"])

        print(f"\n  [1] Perturb  (model: {model_slug(cfg.perturb_model)})")
        rc = run(["openaireview", "perturb", str(tmp_path),
                  "--error_type", cfg.error_type,
                  "--output-dir", str(perturb_dir),
                  "--model", cfg.perturb_model])
        if rc != 0:
            print(f"  perturb failed (exit {rc}), skipping paper")


def review(papers: list[dict], cfg: Config) -> None:
    """Review each corrupted paper with every (model, method) combination."""
    results_dir = Path(cfg.results_dir)

    for i, paper in enumerate(papers, start=1):
        paper_label = f"paper_{i:03d}"
        perturb_dir = results_dir / "perturb" / cfg.error_type / paper_label

        corrupted = max(perturb_dir.glob("*_corrupted.md"),
                        key=lambda p: p.stat().st_mtime, default=None)
        if not corrupted:
            print(f"  No corrupted paper found for {cfg.error_type}/{paper_label}, skipping")
            continue

        print(f"{'='*60}")
        print(f"Paper {i:03d}/{len(papers)}  ({paper_length(paper):,} words)")
        print(f"{'='*60}")

        for model in cfg.review_models:
            for method in cfg.review_methods:
                review_dir = results_dir / model_slug(model) / cfg.error_type / method / paper_label / "review"
                review_dir.mkdir(parents=True, exist_ok=True)

                print(f"\n  [2] Review  ({model_slug(model)} / {cfg.error_type} / {method})")
                rc = run(["openaireview", "review", str(corrupted),
                          "--method", method,
                          "--output-dir", str(review_dir),
                          "--model", model])
                if rc != 0:
                    print(f"  review failed (exit {rc}), skipping")


def score(papers: list[dict], cfg: Config) -> None:
    """Score each review against its perturbation manifest."""
    results_dir = Path(cfg.results_dir)

    for i, paper in enumerate(papers, start=1):
        paper_label = f"paper_{i:03d}"
        perturb_dir = results_dir / "perturb" / cfg.error_type / paper_label

        manifest = max(perturb_dir.glob("*_perturbations.json"),
                       key=lambda p: p.stat().st_mtime, default=None)
        if not manifest:
            print(f"  No manifest found for {cfg.error_type}/{paper_label}, skipping")
            continue

        print(f"{'='*60}")
        print(f"Paper {i:03d}/{len(papers)}  ({paper_length(paper):,} words)")
        print(f"{'='*60}")

        for model in cfg.review_models:
            for review_method in cfg.review_methods:
                review_dir = results_dir / model_slug(model) / cfg.error_type / review_method / paper_label / "review"
                score_dir = results_dir / model_slug(model) / cfg.error_type / review_method / paper_label / "score" / cfg.score_method
                score_dir.mkdir(parents=True, exist_ok=True)

                review_json = max(review_dir.glob("*.json"),
                                  key=lambda p: p.stat().st_mtime, default=None)
                if not review_json:
                    print(f"  No review found for {model_slug(model)}/{cfg.error_type}/{review_method}/{paper_label}, skipping")
                    continue

                print(f"\n  [3] Score   ({model_slug(model)} / {cfg.error_type} / {review_method} / {cfg.score_method})")
                rc = run(["openaireview", "score", str(manifest), str(review_json),
                          "--model", cfg.score_model,
                          "--method", cfg.score_method,
                          "--output-dir", str(score_dir)])
                if rc != 0:
                    print(f"  score failed (exit {rc}), skipping")

        print(f"\n  Done: {paper_label}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _schema_help() -> str:
    """Render the Config dataclass as a YAML schema for --help."""
    lines = ["config schema (set these in the YAML file):", ""]
    for f in fields(Config):
        if f.default is not MISSING:
            default = f.default
        elif f.default_factory is not MISSING:  # type: ignore[misc]
            default = f.default_factory()
        else:
            default = "<required>"
        type_name = getattr(f.type, "__name__", str(f.type))
        line = f"  {f.name}: {type_name} = {default!r}"
        choices = f.metadata.get("choices")
        if choices:
            line += f"  (choices: {' | '.join(choices)})"
        lines.append(line)
    lines.append("")
    lines.append("see configs/default.yaml for an annotated example.")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run perturb → review → score pipeline",
        epilog=_schema_help(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("config", type=Path, help="Path to YAML config file")
    parser.add_argument(
        "--stages",
        type=str,
        default="perturb,review,score",
        help="Comma-separated subset of stages to run: perturb,review,score (default: all)",
    )
    args = parser.parse_args()
    valid = {"perturb", "review", "score"}
    args.stages = [s.strip() for s in args.stages.split(",") if s.strip()]
    invalid = set(args.stages) - valid
    if invalid:
        parser.error(f"--stages: unknown stage(s) {sorted(invalid)}; valid: {sorted(valid)}")
    return args


def main() -> None:
    args = parse_args()
    cfg = load_config(args.config)

    results_dir = Path(cfg.results_dir)
    results_dir.mkdir(exist_ok=True)
    resolved = asdict(cfg)
    with (results_dir / "config.yaml").open("w") as f:
        yaml.safe_dump(resolved, f, sort_keys=False)
    print("Resolved config:")
    print(yaml.safe_dump(resolved, sort_keys=False))

    papers = load_papers(cfg)
    print(f"Stages to run: {', '.join(args.stages)}\n")
    if "perturb" in args.stages:
        perturb(papers, cfg)
    if "review" in args.stages:
        review(papers, cfg)
    if "score" in args.stages:
        score(papers, cfg)
    print(f"\nAll done. Results in {cfg.results_dir}/")


if __name__ == "__main__":
    main()
