#!/usr/bin/env python
"""Pre-flight cost estimator driver run inside coarse's venv.

Invokes `coarse.cost.build_cost_estimate` (no LLM calls) for one
(paper, model) pair and dumps the per-stage + total USD to JSON.
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from pathlib import Path

from coarse.config import load_config
from coarse.cost import build_cost_estimate
from coarse.extraction import extract_file


def estimate(paper_path: Path, model: str) -> dict:
    config = load_config()
    paper_text = extract_file(paper_path)
    is_pdf = paper_path.suffix.lower() == ".pdf"
    estimate = build_cost_estimate(
        paper_text=paper_text,
        config=config,
        is_pdf=is_pdf,
        model=model,
    )
    return {
        "paper": str(paper_path),
        "model": model,
        "token_estimate": paper_text.token_estimate,
        "total_cost_usd": estimate.total_cost_usd,
        "stages": [
            {
                "name": s.name,
                "model": s.model,
                "tokens_in": s.estimated_tokens_in,
                "tokens_out": s.estimated_tokens_out,
                "cost_usd": s.estimated_cost_usd,
            }
            for s in estimate.stages
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--paper", required=True, type=Path)
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    try:
        data = estimate(args.paper, args.model)
    except Exception:
        traceback.print_exc()
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps({"error": traceback.format_exc()}, indent=2))
        return 1

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, indent=2))
    print(f"[cost_driver] {args.paper.stem} / {args.model}: ${data['total_cost_usd']:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
