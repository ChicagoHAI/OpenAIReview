#!/usr/bin/env python3
"""Run openaireview perturb over all papers in papers/theoretical/latex and papers/experimental/latex.

Usage:
    python perturb.py [--model MODEL] [--reasoning-effort EFFORT] [--output-dir DIR] [--category theoretical|experimental]
"""

import argparse
import subprocess
from pathlib import Path

PAPERS_DIR = Path(__file__).parent / "papers"

CATEGORY = "theoretical" # ["theoretical", "experimental"]
ERROR_TYPE = "logic" # theoretical: ["all", "surface", "claim_theoretical", "logic"], 
                     # experimental: ["all", "surface", "statement_empirical", "experimental"]
N_TOTAL = 20

def main() -> None:
    latex_dir = PAPERS_DIR / CATEGORY / "latex"
    if not latex_dir.exists():
        print(f"Warning: {latex_dir} not found")
        return

    tex_files = sorted(latex_dir.glob("*.tex"))
    print(f"\n{CATEGORY}: {len(tex_files)} papers")

    for tex_path in tex_files:
        output_dir = Path(__file__).parent / "_temp_results" / "perturbations" / CATEGORY / tex_path.stem
        cmd = [
            "openaireview", "perturb", str(tex_path),
            "--category", CATEGORY,
            "--error-type", ERROR_TYPE,
            "--n-total", str(N_TOTAL),
            "--model", "anthropic/claude-opus-4-6",
            "--output-dir", str(output_dir),
        ]

        print(f"\n  $ {' '.join(cmd)}")
        rc = subprocess.run(cmd).returncode
        if rc != 0:
            print(f"  ERROR (exit {rc})")

    print(f"\nDone.")


if __name__ == "__main__":
    main()
