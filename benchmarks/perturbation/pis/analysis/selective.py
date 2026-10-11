from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from .common import build_rows, save_fig, write_json


def _aurc(errors: np.ndarray, widths: np.ndarray) -> float:
    """Area under the risk-coverage curve when accepting lowest-width first
    (trapezoid over coverage in [1/n, 1])."""
    order = np.argsort(widths, kind="mergesort")
    k = np.arange(1, len(errors) + 1)
    risks = np.cumsum(errors[order]) / k
    trapz = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
    return float(trapz(risks, k / len(errors)))


def aurc_calibration(errors, widths, n_perm: int = 20000, n_boot: int = 2000,
                     seed: int = 0) -> dict:
    """Permutation test + bootstrap CI for the width-gating gain
    (always-accept risk minus width-gated AURC).

    Deterministic given (seed, numpy version): the PCG64 stream is fixed by
    the seed; numpy reserves the right to change Generator streams across
    releases (NEP 19), so record the numpy version with the results.

    Note on the permutation null: elicited widths are heavily tied, and
    stable-sort tie-breaking preserves index order within tied groups, so
    the null mean gain is slightly positive (rather than ~base/n). The
    test compares the observed gain against exactly this conditional null,
    which is the appropriate reference for tied scores.
    """
    e = np.asarray(errors, int)
    w = np.asarray(widths, float)
    n = len(e)
    if n < 2:
        raise ValueError("calibration needs at least 2 examples")
    base = float(e.mean())
    obs_gain = base - _aurc(e, w)
    rng = np.random.default_rng(seed)
    null = base - np.array([_aurc(e, rng.permutation(w)) for _ in range(n_perm)])
    p_perm = float((1 + int(np.sum(null >= obs_gain))) / (1 + n_perm))
    boot = np.array([e[i].mean() - _aurc(e[i], w[i])
                     for i in (rng.integers(0, n, size=n) for _ in range(n_boot))])
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return {"always_accept_risk": base, "aurc_width_gated": base - obs_gain,
            "gain": obs_gain, "perm_p_one_sided": p_perm,
            "perm_null_mean_gain": float(null.mean()),
            "boot_ci95_gain": [float(lo), float(hi)],
            "n_perm": n_perm, "n_boot": n_boot, "seed": seed}


def run(pis_path, predictions_path, gold_set_path, out_dir,
        calibrate: bool = True, n_perm: int = 20000, n_boot: int = 2000,
        seed: int = 0) -> dict:
    rows, exclusions = build_rows(pis_path, predictions_path, gold_set_path)
    n = len(rows)
    out = Path(out_dir)
    if n == 0:
        summary = {"experiment": "selective_verification", "n": 0,
                   "exclusions": exclusions, "note": "no joined rows"}
        write_json(out / "summary.json", summary)
        return summary

    order = sorted(rows, key=lambda r: r.width)
    errs = np.array([0 if r.correct else 1 for r in order], int)
    k = np.arange(1, n + 1)
    cum_err = np.cumsum(errs)
    coverages = k / n
    risks = cum_err / k
    accs = 1.0 - risks
    overall_risk = float(errs.mean())

    # Structural guarantee: accuracy is computed ONLY over accepted examples;
    # abstained examples are never counted as correct. At full coverage the
    # selective risk must equal the overall risk:
    assert abs(float(risks[-1]) - overall_risk) < 1e-12, "coverage-1 point mismatch"

    curve = [{"k": int(ki), "coverage": float(cov),
              "threshold_width": float(order[ki - 1].width),
              "selective_risk": float(rsk), "selective_accuracy": float(acc),
              "n_error_accepted": int(ce)}
             for ki, cov, rsk, acc, ce in zip(k, coverages, risks, accs, cum_err)]

    oracle_errs = np.sort(errs)
    oracle_risks = np.cumsum(oracle_errs) / k

    trapz = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
    aurc = float(trapz(risks, coverages)) if n > 1 else None
    risk_at = {}
    for c in (0.5, 0.7, 0.8, 0.9):
        ki = int(np.ceil(c * n))
        risk_at[str(c)] = {"k": ki, "coverage": ki / n,
                           "selective_risk": float(risks[ki - 1])}

    # Calibration is computed on ROW order (as loaded), matching the
    # pre-registered calibration script exactly, so the shipped code
    # reproduces the reported numbers bit-for-bit on the same environment.
    calibration = None
    if calibrate:
        if n >= 2:
            calibration = aurc_calibration(
                np.array([0 if r.correct else 1 for r in rows], int),
                np.array([r.width for r in rows], float),
                n_perm=n_perm, n_boot=n_boot, seed=seed)
        else:
            calibration = {"note": "n < 2; calibration undefined"}

    summary = {
        "experiment": "selective_verification",
        "policy": "accept verifier prediction iff PIS width <= tau; else abstain "
                  "(abstain is NEVER counted as correct)",
        "n": n, "overall_risk": overall_risk, "overall_accuracy": 1.0 - overall_risk,
        "aurc_trapezoid": aurc,
        "calibration": calibration,
        "risk_at_target_coverage_posthoc": risk_at,
        "exclusions": exclusions,
        "note": ("No operating threshold is selected on this set (no dev/eval split "
                 "is feasible at this n); the FULL curve is the result. Any single "
                 "point reported above is post-hoc illustration only."),
    }
    write_json(out / "summary.json", summary)
    write_json(out / "risk_coverage_curve.json",
               {"curve": curve,
                "oracle_risks": [float(x) for x in oracle_risks],
                "overall_risk": overall_risk})

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(5.5, 4))
        ax.plot(coverages, risks, label="PIS width gating")
        ax.plot(coverages, oracle_risks, "--", label="oracle ordering")
        ax.axhline(overall_risk, color="k", ls=":", lw=0.8, label="always-accept")
        ax.set_xlabel("coverage"); ax.set_ylabel("selective risk")
        ax.set_title("Risk-coverage (abstention on high PIS width)")
        ax.legend()
        save_fig(fig, out / "fig_risk_coverage.png")
    except Exception as e:  # noqa: BLE001
        print(f"[warn] figure generation skipped: {e}")
    return summary


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="python -m benchmarks.perturbation.pis.analysis.selective")
    p.add_argument("--pis", required=True)
    p.add_argument("--predictions", required=True)
    p.add_argument("--gold-set", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--no-calibrate", action="store_true")
    p.add_argument("--perm", type=int, default=20000)
    p.add_argument("--boot", type=int, default=2000)
    p.add_argument("--seed", type=int, default=0)
    a = p.parse_args(argv)
    print(json.dumps(run(a.pis, a.predictions, a.gold_set, a.out,
                        calibrate=not a.no_calibrate, n_perm=a.perm,
                        n_boot=a.boot, seed=a.seed), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())