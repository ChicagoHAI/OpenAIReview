#!/usr/bin/env python3
"""Sweep the substring-match threshold for perturbation detection.

Reuses already-completed reviewer outputs under
``results/<run>/<reviewer-model>/<error_type>/<method>/paper_*/review/`` and
recomputes detection recall at a range of fuzzy-coverage thresholds. The
LLM-judge step (``_explanation_match_llm``) is independent of the threshold,
so each (perturbation, comment) pair is judged once and cached on disk;
sweeping is then a pure re-aggregation.

Usage (one-domain, one-model slice):

    python -m benchmarks.perturbation.threshold_sweep \\
        --results-dir benchmarks/perturbation/results/full_math_all/claude-opus-4.7 \\
        --perturb-dir benchmarks/perturbation/results/full_math_all/perturb \\
        --judge-model anthropic/claude-haiku-4-5 \\
        --cache benchmarks/perturbation/results/full_math_all/threshold_sweep_cache.json \\
        --out benchmarks/perturbation/results/full_math_all/threshold_sweep.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

_BENCHMARKS_DIR = Path(__file__).resolve().parents[1]
if str(_BENCHMARKS_DIR) not in sys.path:
    sys.path.insert(0, str(_BENCHMARKS_DIR))

from reviewer.utils import _normalize_for_match, _quote_coverage  # noqa: E402
from perturbation.score import _explanation_match_llm  # noqa: E402

THRESHOLDS = [0.50, 0.60, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00]
MIN_TAU = THRESHOLDS[0]


def _iter_units(results_dir: Path, perturb_dir: Path):
    """Yield (paper_label, error_type, method, manifest_path, review_path)."""
    for err_dir in sorted(p for p in results_dir.iterdir() if p.is_dir()):
        if err_dir.name in ("perturb", "_cost_tmp"):
            continue
        err = err_dir.name
        for method_dir in sorted(p for p in err_dir.iterdir() if p.is_dir()):
            method = method_dir.name
            for paper_dir in sorted(p for p in method_dir.iterdir() if p.is_dir()):
                if not paper_dir.name.startswith("paper_"):
                    continue
                review_subdir = paper_dir / "review"
                if not review_subdir.exists():
                    continue
                cands = [p for p in review_subdir.glob("*.json")
                         if not p.name.endswith(".raw.json")]
                if not cands:
                    continue
                review_path = max(cands, key=lambda p: p.stat().st_mtime)
                manifest_path = (perturb_dir / err / paper_dir.name
                                 / f"{paper_dir.name}_perturbations.json")
                if not manifest_path.exists():
                    continue
                yield paper_dir.name, err, method, manifest_path, review_path


def _load_perturbations(manifest_path: Path):
    return json.loads(manifest_path.read_text()).get("perturbations", [])


def _load_comments(review_path: Path):
    """Return list of (comment_id, comment_dict)."""
    data = json.loads(review_path.read_text())
    out = []
    if "methods" in data:
        for m_key, m_data in data["methods"].items():
            for i, c in enumerate(m_data.get("comments", [])):
                out.append((c.get("id") or f"{m_key}_{i}", c))
    elif isinstance(data, list):
        for i, c in enumerate(data):
            out.append((c.get("id") or f"c_{i}", c))
    else:
        for i, c in enumerate(data.get("comments", [])):
            out.append((c.get("id") or f"c_{i}", c))
    return out


def _cache_key(paper, err, method, pid, cid):
    return f"{paper}|{err}|{method}|{pid}|{cid}"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results-dir", required=True, type=Path,
                    help="<run>/<reviewer-model>/ root (contains <error_type>/<method>/paper_*/).")
    ap.add_argument("--perturb-dir", required=True, type=Path,
                    help="<run>/perturb/ root (staged manifests).")
    ap.add_argument("--judge-model", default="anthropic/claude-haiku-4-5",
                    help="Cheap+fast LLM judge for explanation matching.")
    ap.add_argument("--cache", required=True, type=Path,
                    help="JSON file for caching judge results across runs.")
    ap.add_argument("--out", required=True, type=Path,
                    help="Output CSV with one row per threshold.")
    ap.add_argument("--limit-papers", type=int, default=None,
                    help="Stop after N papers per (error_type, method) cell. Smoke-test only.")
    args = ap.parse_args()

    cache: dict[str, bool] = {}
    if args.cache.exists():
        cache = json.loads(args.cache.read_text())
        print(f"loaded {len(cache)} cached judge results from {args.cache}", file=sys.stderr)

    pair_records: list[dict] = []
    perturbation_cells: dict[tuple, set[str]] = {}

    n_pairs_seen = n_pairs_kept = n_judge_calls = n_judge_cached = 0
    paper_count: dict[tuple, int] = {}

    for paper, err, method, manifest_path, review_path in _iter_units(
        args.results_dir, args.perturb_dir
    ):
        cell = (err, method)
        paper_count[cell] = paper_count.get(cell, 0) + 1
        if args.limit_papers is not None and paper_count[cell] > args.limit_papers:
            continue

        perturbations = _load_perturbations(manifest_path)
        comments = _load_comments(review_path)
        if not perturbations or not comments:
            continue

        cell_pids = perturbation_cells.setdefault((paper, err, method), set())
        for p in perturbations:
            cell_pids.add(p["perturbation_id"])

        for p in perturbations:
            p_norm = _normalize_for_match(p["perturbed"])
            if not p_norm:
                continue
            pid = p["perturbation_id"]
            why = p["why_wrong"]
            for cid, c in comments:
                n_pairs_seen += 1
                q_norm = _normalize_for_match(c.get("quote", ""))
                if not q_norm:
                    continue
                cov = _quote_coverage(p_norm, q_norm)
                if cov < MIN_TAU:
                    continue
                n_pairs_kept += 1

                ck = _cache_key(paper, err, method, pid, cid)
                if ck in cache:
                    judge = cache[ck]
                    n_judge_cached += 1
                else:
                    judge = _explanation_match_llm(
                        c.get("explanation", ""), why, args.judge_model
                    )
                    cache[ck] = judge
                    n_judge_calls += 1
                    if n_judge_calls % 25 == 0:
                        args.cache.parent.mkdir(parents=True, exist_ok=True)
                        args.cache.write_text(json.dumps(cache, indent=2))
                        print(f"  ...checkpointed cache ({len(cache)} entries)",
                              file=sys.stderr)

                pair_records.append({
                    "paper": paper, "err": err, "method": method,
                    "pid": pid, "cid": cid,
                    "coverage": cov, "judge": judge,
                })

    args.cache.parent.mkdir(parents=True, exist_ok=True)
    args.cache.write_text(json.dumps(cache, indent=2))

    n_injected = sum(len(v) for v in perturbation_cells.values())
    rows: list[dict] = []
    for tau in THRESHOLDS:
        n_pairs_pass = 0
        detected_keys: set[tuple] = set()
        for r in pair_records:
            if r["coverage"] >= tau:
                n_pairs_pass += 1
                if r["judge"]:
                    detected_keys.add((r["paper"], r["err"], r["method"], r["pid"]))
        n_detected = len(detected_keys)
        recall = n_detected / n_injected if n_injected else 0.0
        rows.append({
            "tau": tau,
            "n_pairs_passing": n_pairs_pass,
            "n_detected": n_detected,
            "n_injected": n_injected,
            "recall": recall,
        })

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as f:
        w = csv.DictWriter(
            f, fieldnames=["tau", "n_pairs_passing", "n_detected", "n_injected", "recall"]
        )
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print()
    print(f"# Threshold sweep summary")
    print(f"pairs seen={n_pairs_seen}  pairs kept (cov>={MIN_TAU})={n_pairs_kept}  "
          f"judge calls={n_judge_calls}  judge cached={n_judge_cached}")
    print(f"cells={len(perturbation_cells)}  n_injected (sum across cells)={n_injected}")
    print()
    print(f"{'tau':>5}  {'pairs_pass':>10}  {'detected':>8}  {'recall':>7}")
    for r in rows:
        print(f"{r['tau']:>5.2f}  {r['n_pairs_passing']:>10}  "
              f"{r['n_detected']:>8}  {r['recall']:>7.4f}")

    print()
    print("% LaTeX (paste into appendix)")
    print(r"\begin{tabular}{rrrr}")
    print(r"\toprule")
    print(r"$\tau$ & pairs passing substring & detected & recall \\")
    print(r"\midrule")
    for r in rows:
        tag = r" \;\;(default)" if abs(r["tau"] - 0.75) < 1e-6 else ""
        print(rf"{r['tau']:.2f} & {r['n_pairs_passing']} & {r['n_detected']} "
              rf"& {r['recall']:.3f}{tag} \\")
    print(r"\bottomrule")
    print(r"\end{tabular}")


if __name__ == "__main__":
    main()
