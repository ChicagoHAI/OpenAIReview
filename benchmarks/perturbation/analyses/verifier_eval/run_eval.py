"""Evaluate the verifier against a labeled gold set.

Usage:
    python -m benchmarks.perturbation.analyses.verifier_eval.run_eval --variant before
    python -m benchmarks.perturbation.analyses.verifier_eval.run_eval --variant after
    python -m benchmarks.perturbation.analyses.verifier_eval.run_eval --variant checklist

Variants:
    before    — legacy prompt (with why_wrong), no structural precheck. Baseline.
    after     — production prose prompt (no why_wrong), structural precheck enabled.
    checklist — 4-item Y/N checklist with deterministic verdict rule, structural precheck enabled.
                Designed to reduce circular vibe-matching against gold labels.

Writes results/{split}_{variant}.json.

TODO: the accuracy/F1 tables in README.md are currently hand-copied from
stdout. A separate report_eval.py should read results/*.json and emit those
tables (and plots later). This script stays gen-only.
"""

from __future__ import annotations

import argparse
import json
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path

from benchmarks.perturbation.models import Error, Perturbation
from benchmarks.perturbation.verify import (
    DEFAULT_MAX_WORKERS,
    DEFAULT_VERIFIER_MODEL,
    DEFAULT_VERIFIER_REASONING,
    VERIFIER_PROMPT,
    VERIFIER_PROMPT_LEGACY,
    VerifierVerdict,
    _verify_one,
)


HERE = Path(__file__).parent
GOLD_PATH = HERE / "gold_set.json"


def _load_gold(path: Path = GOLD_PATH) -> list[dict]:
    return json.loads(path.read_text())["examples"]


def _make_perturbation(ex: dict) -> Perturbation:
    return Perturbation(
        perturbation_id=ex["perturbation_id"],
        span_id=ex["span_id"],
        error=Error(ex["error"]),
        original=ex["original"],
        offset=ex.get("offset", 0),
        perturbed=ex["perturbed"],
        why_wrong=ex.get("why_wrong", ""),
        contradicts_quote=ex.get("contradicts_quote", ""),
    )


def _run(
    variant: str,
    model: str,
    reasoning_effort: str,
    max_workers: int,
    limit: int | None,
    gold_path: Path = GOLD_PATH,
    tag: str = "",
) -> dict:
    examples = _load_gold(gold_path)
    if limit:
        examples = examples[:limit]

    if variant == "before":
        prompt_template = VERIFIER_PROMPT_LEGACY
        use_structural = False
    elif variant == "after":
        prompt_template = VERIFIER_PROMPT
        use_structural = True
    elif variant == "checklist":
        # Sentinel: _verify_one routes to the per-error checklist via CHECKLIST_BY_ERROR.
        prompt_template = "checklist"
        use_structural = True
    else:
        raise ValueError(f"unknown variant: {variant}")

    perturbations = [_make_perturbation(ex) for ex in examples]
    gold_by_id = {ex["perturbation_id"]: ex for ex in examples}

    print(f"Running variant={variant} on {len(perturbations)} examples "
          f"(model={model}, reasoning={reasoning_effort}, workers={max_workers})")
    t0 = time.time()

    verdicts: dict[str, VerifierVerdict] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {
            ex.submit(
                _verify_one,
                p,
                None,
                model,
                reasoning_effort,
                prompt_template,
                use_structural,
            ): p
            for p in perturbations
        }
        for i, fut in enumerate(as_completed(futures), start=1):
            v = fut.result()
            verdicts[v.perturbation_id] = v
            if i % 5 == 0 or i == len(futures):
                print(f"  progress: {i}/{len(futures)}")

    wall = time.time() - t0

    # Score.
    confusion: dict[tuple[str, str], int] = Counter()
    per_row = []
    for p in perturbations:
        v = verdicts[p.perturbation_id]
        gold = gold_by_id[p.perturbation_id]["gold_label"]
        pred = v.verdict
        confusion[(gold, pred)] += 1
        per_row.append({
            "perturbation_id": p.perturbation_id,
            "error": p.error.value,
            "original": p.original,
            "perturbed": p.perturbed,
            "contradicts_quote": p.contradicts_quote,
            "gold_label": gold,
            "pred_label": pred,
            "pred_reason": v.reason,
            "rationale": gold_by_id[p.perturbation_id].get("rationale", ""),
            "correct": gold == pred,
        })

    labels = ["substantive", "typo-shaped", "not-an-error"]
    per_class: dict[str, dict[str, float]] = {}
    for lab in labels:
        tp = confusion[(lab, lab)]
        fp = sum(confusion[(g, lab)] for g in labels if g != lab)
        fn = sum(confusion[(lab, pr)] for pr in labels if pr != lab)
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        per_class[lab] = {
            "tp": tp, "fp": fp, "fn": fn,
            "precision": round(prec, 3),
            "recall": round(rec, 3),
            "f1": round(f1, 3),
        }

    n_correct = sum(1 for r in per_row if r["correct"])
    accuracy = n_correct / len(per_row) if per_row else 0.0

    # Also break down by error type (how accurate are we per category?)
    per_err: dict[str, Counter] = defaultdict(Counter)
    for r in per_row:
        per_err[r["error"]]["total"] += 1
        if r["correct"]:
            per_err[r["error"]]["correct"] += 1

    results = {
        "variant": variant,
        "model": model,
        "reasoning_effort": reasoning_effort,
        "n_examples": len(per_row),
        "wall_time_sec": round(wall, 1),
        "accuracy": round(accuracy, 3),
        "per_class": per_class,
        "confusion_matrix": {f"gold={g}|pred={p}": c for (g, p), c in confusion.items()},
        "per_error_type": {
            err: {
                "total": cc["total"],
                "correct": cc["correct"],
                "accuracy": round(cc["correct"] / cc["total"], 3) if cc["total"] else 0.0,
            }
            for err, cc in per_err.items()
        },
        "rows": per_row,
    }

    # Save. Canonical name is results/{split}_{variant}.json, where split is
    # inferred from the tag ("heldout" → heldout, otherwise → training). Reruns
    # overwrite in place so the README can link to stable paths.
    split = tag if tag else "training"
    results_dir = HERE / "results"
    results_dir.mkdir(exist_ok=True)
    out_path = results_dir / f"{split}_{variant}.json"
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nWrote {out_path}")
    print(f"Accuracy: {accuracy:.3f}  (correct={n_correct}/{len(per_row)})")
    print(f"Per class: {json.dumps(per_class, indent=2)}")
    print(f"Per error type: {json.dumps(results['per_error_type'], indent=2)}")
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", choices=("before", "after", "checklist"), required=True)
    ap.add_argument("--model", default=DEFAULT_VERIFIER_MODEL)
    ap.add_argument("--reasoning", default=DEFAULT_VERIFIER_REASONING)
    ap.add_argument("--workers", type=int, default=DEFAULT_MAX_WORKERS)
    ap.add_argument("--limit", type=int, default=None,
                    help="Only run first N examples (for smoke tests).")
    ap.add_argument("--gold", default=None,
                    help="Path to gold set JSON (default: gold_set.json alongside this script).")
    ap.add_argument("--tag", default="",
                    help="Optional tag for result filename, e.g. 'heldout'.")
    args = ap.parse_args()
    gold_path = Path(args.gold) if args.gold else GOLD_PATH
    _run(args.variant, args.model, args.reasoning, args.workers, args.limit, gold_path, args.tag)


if __name__ == "__main__":
    main()
