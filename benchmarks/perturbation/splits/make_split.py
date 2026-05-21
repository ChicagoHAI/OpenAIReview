#!/usr/bin/env python3
"""Stratified 50/50 val/test split of the perturbation benchmark papers.

For each arXiv domain under data/perturbations_filtered/<domain>/all/, lists
paper_id subdirs in sorted order (so paper_NNN labels match discover_units in
_prepare.py), then splits ~50/50 with a fixed seed. Writes splits/val.json
and splits/test.json — each maps domain -> {paper_labels, paper_ids}.

The paper_labels list is what gets fed into Config.paper_subset; the
paper_ids list is for audit only.
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT_ROOT = REPO_ROOT / "benchmarks" / "perturbation" / "data" / "perturbations_filtered"


def _domains(input_root: Path) -> list[str]:
    return sorted(p.name for p in input_root.iterdir() if p.is_dir())


def _domain_papers(input_root: Path, domain: str) -> list[str]:
    domain_all = input_root / domain / "all"
    return sorted(p.name for p in domain_all.iterdir() if p.is_dir())


def build_split(input_root: Path, seed: int) -> tuple[dict, dict]:
    rng = random.Random(seed)
    val: dict = {"seed": seed, "domains": {}}
    test: dict = {"seed": seed, "domains": {}}
    for domain in _domains(input_root):
        paper_ids = _domain_papers(input_root, domain)
        n = len(paper_ids)
        indices = list(range(n))
        rng.shuffle(indices)
        cut = n // 2
        val_idx = sorted(indices[:cut])
        test_idx = sorted(indices[cut:])

        def pack(idxs: list[int]) -> dict:
            return {
                "paper_labels": [f"paper_{i+1:03d}" for i in idxs],
                "paper_ids": [paper_ids[i] for i in idxs],
            }

        val["domains"][domain] = pack(val_idx)
        test["domains"][domain] = pack(test_idx)
    return val, test


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--input-root", type=Path, default=DEFAULT_INPUT_ROOT)
    ap.add_argument("--out-dir", type=Path, default=Path(__file__).resolve().parent)
    args = ap.parse_args()

    val, test = build_split(args.input_root, args.seed)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "val.json").write_text(json.dumps(val, indent=2))
    (args.out_dir / "test.json").write_text(json.dumps(test, indent=2))

    nv = sum(len(v["paper_labels"]) for v in val["domains"].values())
    nt = sum(len(v["paper_labels"]) for v in test["domains"].values())
    print(f"seed={args.seed}  val={nv} papers  test={nt} papers  ({nv+nt} total)")
    for d in sorted(val["domains"]):
        print(f"  {d}: val={len(val['domains'][d]['paper_labels'])} "
              f"test={len(test['domains'][d]['paper_labels'])}")


if __name__ == "__main__":
    main()
