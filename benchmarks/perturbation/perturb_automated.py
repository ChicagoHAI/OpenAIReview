#!/usr/bin/env python3
"""Run openaireview perturb over all papers in papers/theoretical/latex and papers/experimental/latex.

Usage:
    python perturb.py [--model MODEL] [--reasoning-effort EFFORT] [--output-dir DIR] [--category theoretical|experimental]
"""

import argparse
import subprocess
from pathlib import Path

PAPERS_DIR = Path(__file__).parent / "papers"
CATEGORIES = ["theoretical", "experimental"]


def main() -> None:
    for category in CATEGORIES:
        latex_dir = PAPERS_DIR / category / "latex"
        if not latex_dir.exists():
            print(f"Warning: {latex_dir} not found, skipping")
            continue

        tex_files = sorted(latex_dir.glob("*.tex"))
        print(f"\n{category}: {len(tex_files)} papers")

        for tex_path in tex_files:
            output_dir = Path(__file__).parent / "results" / "perturbations" / category / tex_path.stem
            cmd = [
                "openaireview", "perturb", str(tex_path),
                "--category", category,
                "--model", "anthropic/claude-opus-4-6",
                "--output-dir", str(output_dir),
            ]

            print(f"\n  $ {' '.join(cmd)}")
            rc = subprocess.run(cmd).returncode
            if rc != 0:
                print(f"  ERROR (exit {rc}), continuing...")

    print(f"\nDone.")


if __name__ == "__main__":
    main()
