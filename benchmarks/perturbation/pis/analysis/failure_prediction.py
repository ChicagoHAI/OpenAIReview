from __future__ import annotations

import argparse
import difflib
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

from ..gold_io import load_gold_set
from ..inputs import record_uid
from .common import (auroc, binned_stats, build_rows, bootstrap_auroc_ci,
                     mann_whitney_u, quantile_bins, read_jsonl, roc_curve,
                     save_fig, spearman, stats_of, write_json)


def _baseline_from_map(rows, values_by_uid, name, transform=None, B=2000, seed=0):
    vals, labs, widths = [], [], []
    for r in rows:
        v = values_by_uid.get(r.uid)
        if not isinstance(v, (int, float)) or isinstance(v, bool):
            continue
        vals.append(float(transform(v)) if transform else float(v))
        labs.append(0 if r.correct else 1)
        widths.append(r.width)
    out = {"n": len(vals)}
    if len(vals) >= 5 and len(set(labs)) == 2:
        a = auroc(np.array(vals), np.array(labs))
        lo, hi, _ = bootstrap_auroc_ci(np.array(vals), np.array(labs), B, seed)
        out.update({"auroc": a, "ci95": [lo, hi],
                    "auroc_pis_width_same_subset": auroc(np.array(widths), np.array(labs))})
    else:
        out.update({"auroc": None, "note": "insufficient n or single class"})
    return out


def run(pis_path, predictions_path, gold_set_path, out_dir,
        scalar_path=None, logit_path=None, B=2000, seed=0) -> dict:
    rows, exclusions = build_rows(pis_path, predictions_path, gold_set_path)
    n = len(rows)
    inc = np.array([0 if r.correct else 1 for r in rows], int)
    widths = np.array([r.width for r in rows], float)
    summary = {
        "experiment": "verifier_failure_prediction",
        "primary_signal": "pis_width (U - L)",
        "pre_registered_hypothesis": (
            "Higher evidential uncertainty (interval width) predicts verifier "
            "prediction errors. All other signals below are SECONDARY/exploratory "
            "and must not be reported as primary evidence."),
        "n": n, "n_correct": int((inc == 0).sum()), "n_incorrect": int(inc.sum()),
        "verifier_error_rate": (float(inc.mean()) if n else None),
        "exclusions": exclusions, "seed": seed, "bootstrap_B": B,
    }
    if 0 < inc.sum() < n:
        wc, wi = widths[inc == 0], widths[inc == 1]
        summary["width_stats"] = {"correct": stats_of(wc), "incorrect": stats_of(wi)}
        U, z, p = mann_whitney_u(wi, wc)
        summary["mann_whitney_width"] = {"U": U, "z": z, "p_two_sided": p,
                                         "n_correct": len(wc), "n_incorrect": len(wi)}
        a = auroc(widths, inc)
        lo, hi, sk = bootstrap_auroc_ci(widths, inc, B, seed)
        summary["auroc_width_for_incorrect"] = {"value": a, "ci95": [lo, hi],
                                                 "n_bootstrap_skipped": sk}
    else:
        summary["note_single_class"] = (
            "AUROC undefined: verifier is either always correct or always wrong on "
            "the joined set; report raw error rate only.")

    amb = np.array([r.ambiguity for r in rows], float)
    if 0 < inc.sum() < n:
        lo, hi, _ = bootstrap_auroc_ci(amb, inc, B, seed)
        summary["auroc_ambiguity_secondary"] = {
            "value": auroc(amb, inc), "ci95": [lo, hi],
            "definition": "min(U, 1-L): distance of interval from nearest pole"}

    edges, nb = quantile_bins(widths, 4, 5)
    summary["error_rate_by_width_bin"] = {
        "n_bins": nb, "bins": binned_stats(widths, inc, edges),
        "note": "binned empirical error rates double as the reliability analysis "
                "of width as a risk score; formal recalibration needs a dev split"}

    by_type = {}
    for t in sorted({r.error_type for r in rows}):
        sub = [r for r in rows if r.error_type == t]
        s_inc = np.array([0 if r.correct else 1 for r in sub], int)
        s_w = np.array([r.width for r in sub], float)
        entry = {"n": len(sub), "n_incorrect": int(s_inc.sum()),
                 "error_rate": (float(s_inc.mean()) if len(sub) else None),
                 "width_stats_correct": stats_of(s_w[s_inc == 0]) if 0 < s_inc.sum() < len(sub) else None,
                 "width_stats_incorrect": stats_of(s_w[s_inc == 1]) if 0 < s_inc.sum() < len(sub) else None,
                 "auroc_width": (auroc(s_w, s_inc)
                                 if 0 < s_inc.sum() < len(sub) else None),
                 "note": ("cell too small for stable inference"
                          if min(int(s_inc.sum()), len(sub) - int(s_inc.sum())) < 5 else None)}
        by_type[t] = entry
    summary["by_error_type"] = by_type

    by_quote = {}
    for qa in (True, False):
        sub = [r for r in rows if r.quote_available == qa]
        s_inc = np.array([0 if r.correct else 1 for r in sub], int)
        s_w = np.array([r.width for r in sub], float)
        by_quote[str(qa)] = {"n": len(sub), "n_incorrect": int(s_inc.sum()),
                            "error_rate": (float(s_inc.mean()) if len(sub) else None),
                            "width_stats": stats_of(s_w),
                            "auroc_width_within_stratum": (auroc(s_w, s_inc)
                                                           if 0 < s_inc.sum() < len(sub) else None)}
    summary["by_quote_availability"] = by_quote

    # ---- baselines (secondary; confound checks) ----
    gold_records, _ = load_gold_set(gold_set_path)
    lex, lendiff = {}, {}
    for g in gold_records:
        uid = record_uid(g)
        lex[uid] = 1.0 - difflib.SequenceMatcher(
            None, str(g["original"]), str(g["perturbed"])).ratio()
        lendiff[uid] = float(abs(len(str(g["original"])) - len(str(g["perturbed"]))))
    baselines = {
        "lexical_distance_1_sequencematcher": _baseline_from_map(rows, lex, "lex", None, B, seed),
        "abs_len_diff": _baseline_from_map(rows, lendiff, "len", None, B, seed),
    }
    if scalar_path:
        m = {l["uid"]: l.get("value") for l in read_jsonl(scalar_path) if l.get("status") != "failed"}
        baselines["abs_self_confidence_minus_half"] = _baseline_from_map(
            rows, m, "conf", lambda v: abs(v - 0.5), B, seed)
    if logit_path:
        m = {}
        for l in read_jsonl(logit_path):
            sc = l.get("score")
            if l.get("status") != "failed" and isinstance(sc, dict):
                m[l["uid"]] = sc.get("p_yes")
        baselines["abs_token_prob_minus_half"] = _baseline_from_map(
            rows, m, "logit", lambda v: abs(v - 0.5), B, seed)
    summary["baselines_secondary"] = baselines

    summary["confound_correlations"] = {
        "spearman_width_vs_lexical_distance": spearman(widths, [lex[r.uid] for r in rows]),
        "spearman_width_vs_abs_len_diff": spearman(widths, [lendiff[r.uid] for r in rows]),
        "spearman_width_vs_n_items": spearman(widths, [float(r.n_items) for r in rows]),
    }

    out = Path(out_dir)
    write_json(out / "summary.json", summary)

    # ---- report.md ----
    md = ["# Experiment 1: Verifier Failure Prediction", "",
          f"- n (joined) = {n}; verifier error rate = {summary.get('verifier_error_rate')}",
          f"- exclusions: { {k: len(v) for k, v in exclusions.items()} }", ""]
    if "width_stats" in summary:
        md += [f"- width (correct): {summary['width_stats']['correct']}",
               f"- width (incorrect): {summary['width_stats']['incorrect']}",
               f"- Mann-Whitney: {summary['mann_whitney_width']}",
               f"- AUROC(width -> incorrect): {summary['auroc_width_for_incorrect']}", ""]
    md += [f"- binned error rates: n_bins={nb}",
           *[f"  - bin {b['bin']}: n={b['n']}, err={b['error_rate']}, CI={b['error_rate_ci95_wilson']}"
             for b in summary["error_rate_by_width_bin"]["bins"]], "",
           "Baselines (secondary): " + json_dumps_compact(baselines)]
    (out / "report.md").write_text("\n".join(md), encoding="utf-8")

    # ---- figures ----
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        if 0 < inc.sum() < n:
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.hist(widths[inc == 0], bins=np.linspace(0, 1, 11), alpha=0.6, label="correct")
            ax.hist(widths[inc == 1], bins=np.linspace(0, 1, 11), alpha=0.6, label="incorrect")
            ax.set_xlabel("PIS width (U - L)"); ax.set_ylabel("count"); ax.legend()
            save_fig(fig, out / "fig_width_hist.png")
            fpr, tpr = roc_curve(widths, inc)
            if fpr is not None:
                fig, ax = plt.subplots(figsize=(4.5, 4))
                ax.plot(fpr, tpr); ax.plot([0, 1], [0, 1], "k--", lw=0.7)
                ax.set_xlabel("FPR"); ax.set_ylabel("TPR")
                ax.set_title("width -> verifier error")
                save_fig(fig, out / "fig_roc_width.png")
            bins = summary["error_rate_by_width_bin"]["bins"]
            xs = [b["bin"] for b in bins]
            ys = [b["error_rate"] for b in bins]
            es = [(max(0.0, (b["error_rate_ci95_wilson"] or [None, None])[1] - (b["error_rate"] or 0)),
                   max(0.0, (b["error_rate"] or 0) - (b["error_rate_ci95_wilson"] or [0, 0])[0]))
                  for b in bins]
            fig, ax = plt.subplots(figsize=(5, 4))
            ax.errorbar(xs, ys, yerr=list(zip(*es)), fmt="o-")
            ax.set_xlabel("PIS width bin"); ax.set_ylabel("verifier error rate")
            save_fig(fig, out / "fig_error_by_width_bin.png")
    except Exception as e:  # noqa: BLE001 - figures are best-effort
        print(f"[warn] figure generation skipped: {e}")
    return summary


def json_dumps_compact(obj) -> str:
    import json
    return json.dumps(obj, default=str)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="python -m benchmarks.perturbation.pis.analysis.failure_prediction")
    p.add_argument("--pis", required=True)
    p.add_argument("--predictions", required=True)
    p.add_argument("--gold-set", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--scalar", default=None)
    p.add_argument("--logit", default=None)
    p.add_argument("--bootstrap-B", type=int, default=2000)
    p.add_argument("--seed", type=int, default=0)
    a = p.parse_args(argv)
    s = run(a.pis, a.predictions, a.gold_set, a.out, a.scalar, a.logit,
            a.bootstrap_B, a.seed)
    import json
    print(json.dumps(s, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())