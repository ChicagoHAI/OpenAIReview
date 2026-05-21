#!/usr/bin/env python3
"""Score every (already-reviewed) cell under one or more results_dirs by
calling `openaireview score` directly.

Works around a bug in run_benchmark.py's score stage: that stage uses
build_jobs() which skips cells whose review is complete, so once reviews
finish in the same invocation it has nothing to score.
"""

from __future__ import annotations

import argparse
import glob
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
OPENAIREVIEW = Path(sys.executable).parent / "openaireview"


def _score_one(manifest: Path, review_json: Path, score_dir: Path,
               model: str, method: str, threshold: int,
               substring_gate: bool) -> tuple[Path, int, str]:
    score_dir.mkdir(parents=True, exist_ok=True)
    cmd = [str(OPENAIREVIEW), "score", str(manifest), str(review_json),
           "--model", model, "--method", method,
           "--threshold", str(threshold),
           "--output-dir", str(score_dir)]
    if substring_gate:
        cmd.append("--substring-gate")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return review_json, proc.returncode, (proc.stderr or "")[-300:]


def collect_jobs(results_dir: Path, subdir: str, force: bool) -> list[tuple[Path, Path, Path]]:
    """Return list of (manifest, review_json, score_dir) tuples."""
    perturb_root = results_dir / "perturb"
    if not perturb_root.is_dir():
        return []
    jobs = []
    for model_dir in results_dir.iterdir():
        if not model_dir.is_dir() or model_dir.name in {"perturb", "_cost_tmp"}:
            continue
        # Walk <model>/<err>/<method>/<paper_label>/review/*.json
        for review_json in model_dir.glob("*/*/*/review/*.json"):
            parts = review_json.relative_to(model_dir).parts
            # err, method, paper_label, "review", file
            if len(parts) < 5 or parts[3] != "review":
                continue
            err, method, paper_label = parts[0], parts[1], parts[2]
            paper_dir = review_json.parent.parent  # .../<paper_label>/
            score_dir = paper_dir / "score" / subdir
            if not force and any(score_dir.glob("*_score.json")):
                continue
            manifest_dir = perturb_root / err / paper_label
            manifests = sorted(manifest_dir.glob("*_perturbations.json"),
                               key=lambda p: p.stat().st_mtime, reverse=True)
            if not manifests:
                continue
            jobs.append((manifests[0], review_json, score_dir))
    return jobs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", nargs="+", required=True,
                    help="One or more results dirs (glob patterns OK)")
    ap.add_argument("--score-method", default="llm")
    ap.add_argument("--score-model", default="google/gemini-3-flash-preview")
    ap.add_argument("--threshold", type=int, default=4)
    ap.add_argument("--substring-gate", action="store_true", default=True)
    ap.add_argument("--no-substring-gate", dest="substring_gate", action="store_false")
    ap.add_argument("--subdir", default="llm_t4_grounded",
                    help="Score output subdir under <paper>/score/")
    ap.add_argument("--parallel", type=int, default=4)
    ap.add_argument("--force", action="store_true",
                    help="Re-score even if a score JSON already exists")
    args = ap.parse_args()

    dirs = []
    for pat in args.results:
        matched = sorted(Path(x) for x in glob.glob(pat))
        if not matched:
            matched = [Path(pat)]
        dirs.extend(matched)
    print(f"Walking {len(dirs)} results dirs...")
    jobs = []
    for d in dirs:
        sub = collect_jobs(d, args.subdir, args.force)
        print(f"  {d.name}: {len(sub)} cells to score")
        jobs.extend(sub)
    if not jobs:
        print("Nothing to score.")
        return
    print(f"Total {len(jobs)} score jobs; parallel={args.parallel}")
    n_done = n_fail = 0
    with ThreadPoolExecutor(max_workers=args.parallel) as pool:
        futs = {pool.submit(_score_one, m, r, s, args.score_model,
                            args.score_method, args.threshold, args.substring_gate): r
                for m, r, s in jobs}
        for i, fut in enumerate(as_completed(futs), 1):
            rj, rc, err = fut.result()
            if rc == 0:
                n_done += 1
            else:
                n_fail += 1
                print(f"  FAIL {rj}: {err.strip()[:200]}")
            if i % 20 == 0 or i == len(jobs):
                print(f"  progress: {i}/{len(jobs)} (done={n_done} fail={n_fail})")
    print(f"score: done={n_done} failed={n_fail}")


if __name__ == "__main__":
    main()
