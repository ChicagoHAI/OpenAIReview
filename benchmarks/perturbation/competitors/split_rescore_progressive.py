#!/usr/bin/env python3
"""Split each progressive review JSON into consolidated and pre-consolidation
variants, rescore each via `openaireview score`, and write the results under
new `progressive_consolidated/` and `progressive_preconsol/` method dirs.

Lets the report generator surface the two variants as separate columns
instead of the pooled progressive recall.

Usage:
  python benchmarks/perturbation/competitors/split_rescore_progressive.py \\
      --results-dir benchmarks/perturbation/results/short \\
      --results-dir benchmarks/perturbation/results/medium \\
      --parallel 6
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


def _openaireview_bin() -> str:
    here = Path(sys.executable).parent / "openaireview"
    return str(here) if here.exists() else "openaireview"


def split_review(review_json: Path) -> dict[str, dict]:
    """Return {variant: review_json_dict} for 'consolidated' and 'preconsol'."""
    data = json.loads(review_json.read_text())
    methods = data.get("methods", {})
    consolidated_keys = [k for k in methods if k.startswith("progressive__")]
    preconsol_keys = [k for k in methods if k.startswith("progressive_original__")]
    if not consolidated_keys or not preconsol_keys:
        return {}

    out: dict[str, dict] = {}
    for variant, keys in [("consolidated", consolidated_keys), ("preconsol", preconsol_keys)]:
        new = dict(data)
        new["methods"] = {k: methods[k] for k in keys}
        out[variant] = new
    return out


def _score_one(manifest: Path, review_json: Path, score_dir: Path,
               score_model: str, score_method: str) -> int:
    score_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        _openaireview_bin(), "score", str(manifest), str(review_json),
        "--model", score_model, "--method", score_method,
        "--output-dir", str(score_dir),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, env={**os.environ})
    if proc.returncode != 0:
        print(f"[split-rescore] FAILED score for {review_json}:\n{proc.stderr[-600:]}",
              file=sys.stderr)
    return proc.returncode


def process_one(
    review_json: Path,
    perturb_dir: Path,
    model_dir: Path,
    error_type: str,
    paper_label: str,
    score_model: str,
    score_method: str,
) -> list[tuple[str, int]]:
    """Split a single progressive review JSON and rescore both variants."""
    splits = split_review(review_json)
    if not splits:
        return []
    manifest = max(perturb_dir.glob("*_perturbations.json"),
                   key=lambda p: p.stat().st_mtime, default=None)
    if manifest is None:
        print(f"[split-rescore] no manifest for {perturb_dir}", file=sys.stderr)
        return []

    results: list[tuple[str, int]] = []
    for variant, data in splits.items():
        new_method = f"progressive_{variant}"
        new_review_dir = model_dir / error_type / new_method / paper_label / "review"
        new_score_dir = model_dir / error_type / new_method / paper_label / "score" / score_method
        new_review_dir.mkdir(parents=True, exist_ok=True)
        new_review_path = new_review_dir / review_json.name
        new_review_path.write_text(json.dumps(data, indent=2))
        rc = _score_one(manifest, new_review_path, new_score_dir, score_model, score_method)
        results.append((variant, rc))
    return results


def collect_jobs(results_dir: Path, error_type: str) -> list[dict]:
    jobs: list[dict] = []
    for review_json in results_dir.glob(f"*/{error_type}/progressive/paper_*/review/*.json"):
        # <results>/<model>/<error_type>/progressive/<paper>/review/<name>.json
        # parents:  [0]=review [1]=paper [2]=progressive [3]=error_type [4]=model
        model_dir = review_json.parents[4]
        paper_dir = review_json.parents[1]
        paper_label = paper_dir.name
        perturb_dir = results_dir / "perturb" / error_type / paper_label
        jobs.append({
            "review_json": review_json,
            "perturb_dir": perturb_dir,
            "model_dir": model_dir,
            "error_type": error_type,
            "paper_label": paper_label,
        })
    return jobs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", action="append", required=True, type=Path)
    ap.add_argument("--error-type", default="surface")
    ap.add_argument("--score-model", default="google/gemini-3-flash-preview")
    ap.add_argument("--score-method", default="llm")
    ap.add_argument("--parallel", type=int, default=6)
    args = ap.parse_args()

    all_jobs: list[dict] = []
    for rd in args.results_dir:
        if not rd.exists():
            print(f"results dir not found: {rd}", file=sys.stderr)
            return 1
        all_jobs.extend(collect_jobs(rd, args.error_type))
    if not all_jobs:
        print("no progressive review JSONs found")
        return 0
    print(f"Found {len(all_jobs)} progressive review JSONs to split+rescore "
          f"({len(all_jobs)*2} score runs, parallel={args.parallel})")

    done = 0
    with ThreadPoolExecutor(max_workers=args.parallel) as pool:
        futures = {
            pool.submit(
                process_one,
                j["review_json"], j["perturb_dir"], j["model_dir"],
                j["error_type"], j["paper_label"],
                args.score_model, args.score_method,
            ): j for j in all_jobs
        }
        for fut in as_completed(futures):
            j = futures[fut]
            try:
                res = fut.result()
            except Exception as e:
                print(f"[split-rescore] exception on {j['review_json']}: {e}",
                      file=sys.stderr)
                continue
            done += 1
            tag = f"{j['review_json'].parents[4].name}/{j['paper_label']}"
            status = ", ".join(f"{v}:rc={rc}" for v, rc in res) or "skipped"
            print(f"[{done}/{len(all_jobs)}] {tag} — {status}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
