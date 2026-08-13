"""Cluster-bootstrap-over-papers 95% CIs for the pairwise-accuracy (Mann-Whitney
AUC) cells in the conference study.

Each quality proxy splits the papers into two sides: a high-quality group and a
low-quality group. The AUC is the pairwise accuracy of that split, the
probability that the system puts more comments on a randomly drawn low-quality
paper than on a randomly drawn high-quality one (0.5 means no separation).

Resampling unit = paper, stratified by (proxy, side): within each proxy we
resample the high-side papers and the low-side papers with replacement and take
2.5/97.5 percentiles. No significance tests.

Paper sets, result dirs, and the tables to print are defined in a JSON config
(--config, defaults to ci_auc_tables.json). The config and the result JSONs and
manifests it points at are kept locally (gitignored, large); the math is covered
by tests/test_ci_auc.py on in-memory data. Three table kinds, one per paper
format: "comment_volume" (Table 1, mean comments + delta + overall AUC),
"by_proxy" (Table 2, accuracy per quality proxy), and "by_severity" (Table 9,
accuracy per severity tier).
"""
import sys
from pathlib import Path
from collections import defaultdict
import numpy as np

HERE = Path(__file__).resolve().parent
from compute_auc import load_manifest, load_counts, cell_summary, auc_from  # noqa: E402

B = 5000
RNG = np.random.default_rng(42)


def by_proxy_totals(counts_for_cell, slug_to_mem):
    """proxy_id -> {'high': [counts], 'low': [counts]} (total comments)."""
    by_proxy = defaultdict(lambda: {"high": [], "low": []})
    for slug, rec in counts_for_cell.items():
        for m in slug_to_mem.get(slug, []):
            # "pair" is the manifest's field name for a quality proxy.
            by_proxy[m["pair"]][m["side"]].append(rec["total"])
    return by_proxy


def cell_aucs(by_proxy):
    """Return (overall_auc, {proxy: auc})."""
    per = {}
    H = T = 0.0
    for proxy_id, d in by_proxy.items():
        a, hits, tot = auc_from(d["high"], d["low"])
        per[proxy_id] = a
        H += hits; T += tot
    return (H / T if T else np.nan), per


def bootstrap(by_proxy):
    """Cluster-bootstrap CIs for one cell's overall and per-proxy AUC.

    Each of B draws resamples papers with replacement, stratified by (proxy,
    side): within every proxy the high-side and low-side papers are resampled
    on their own. Per draw, each proxy's resampled AUC is recorded, and hits and
    pairs are pooled across proxies for that draw's overall AUC. Returns
    ((overall_lo, overall_hi), {proxy_id: (lo, hi)}) from the 2.5/97.5
    percentiles of those draws.
    """
    overalls = []
    per_lists = defaultdict(list)
    proxy_ids = sorted(by_proxy)
    arrs = {proxy_id: (np.asarray(by_proxy[proxy_id]["high"]), np.asarray(by_proxy[proxy_id]["low"])) for proxy_id in proxy_ids}
    for _ in range(B):
        H = T = 0.0
        for proxy_id in proxy_ids:
            high, low = arrs[proxy_id]
            if high.size == 0 or low.size == 0:
                continue
            high_resampled = high[RNG.integers(0, high.size, high.size)]
            low_resampled = low[RNG.integers(0, low.size, low.size)]
            a, hits, tot = auc_from(high_resampled, low_resampled)
            per_lists[proxy_id].append(a)
            H += hits; T += tot
        overalls.append(H / T if T else np.nan)
    # A proxy with papers on only one side never gets a draw appended, so guard
    # the empty case (mirrors the nan the point-estimate paths return there).
    ci = lambda xs: tuple(np.percentile(xs, [2.5, 97.5])) if xs else (float("nan"), float("nan"))
    return ci(overalls), {proxy_id: ci(per_lists[proxy_id]) for proxy_id in proxy_ids}


PROXY = {1: "Community", 2: "Conference", 3: "Reviewer", 4: "Composite"}


# ---- per-severity-tier AUCs (appendix tier tables) ----

def by_proxy_recs(counts_for_cell, slug_to_mem):
    """proxy_id -> {'high': [rec], 'low': [rec]}.

    A rec is one paper's comment counts from load_counts:
    {'total', 'major', 'moderate', 'minor'}. Keeps the whole rec (not just the
    total) so per-severity-tier AUCs can be computed."""
    by_proxy = defaultdict(lambda: {"high": [], "low": []})
    for slug, rec in counts_for_cell.items():
        for m in slug_to_mem.get(slug, []):
            by_proxy[m["pair"]][m["side"]].append(rec)
    return by_proxy


def bootstrap_tiers(by_proxy, tiers):
    """Cluster-bootstrap CI per tier. Returns {tier: (lo, hi)}.

    'tiers' may include 'total' (the overall comment count) alongside the
    severity tiers. One paper resample per (proxy, side) is shared across all
    tiers within a draw, so the tiers stay correlated. Supplies the CIs for the
    volume table (overall) and the tier table (overall + per-severity).
    """
    proxy_ids = sorted(by_proxy)
    draws = {t: [] for t in tiers}
    for _ in range(B):
        Ht = {t: 0.0 for t in tiers}; Tt = {t: 0.0 for t in tiers}
        for proxy_id in proxy_ids:
            high = by_proxy[proxy_id]["high"]; low = by_proxy[proxy_id]["low"]
            if not high or not low:
                continue
            high_idx = RNG.integers(0, len(high), len(high))
            low_idx = RNG.integers(0, len(low), len(low))
            for t in tiers:
                high_resampled = [high[j][t] for j in high_idx]
                low_resampled = [low[j][t] for j in low_idx]
                _, hits, tot = auc_from(high_resampled, low_resampled)
                Ht[t] += hits; Tt[t] += tot
        for t in tiers:
            draws[t].append(Ht[t] / Tt[t] if Tt[t] else np.nan)
    return {t: tuple(np.percentile(draws[t], [2.5, 97.5])) for t in tiers}


def auc_cell(point, lo_hi):
    """Format one AUC point estimate with its CI as 'point [lo, hi]'."""
    lo, hi = lo_hi
    return f"{point:.2f} [{lo:.2f}, {hi:.2f}]"


def _labels_and_width(cells):
    """Row labels ('method__model') and the first-column width to align them."""
    labels = [f"{method}__{model}" for method, model in cells]
    return labels, max([len("method__model")] + [len(x) for x in labels]) + 2


def run_comment_volume(manifest, dirs, cells):
    """Table 1 (model-aggregate): mean comments on the high/low-quality groups,
    their difference (delta, % increase), and overall AUC with CI."""
    slug_to_mem = load_manifest(manifest)
    counts = load_counts(dirs, set(slug_to_mem))
    labels, w = _labels_and_width(cells)
    print(f"{'method__model':<{w}}{'c_high':>8}{'c_low':>8}{'delta':>8}{'%inc':>8}   {'Overall':<18}".rstrip())
    for (method, model), label in zip(cells, labels):
        cc = counts.get((method, model))
        if not cc:
            print(f"{label:<{w}}NO DATA"); continue
        s = cell_summary(cc, slug_to_mem)
        overall_ci = bootstrap_tiers(by_proxy_recs(cc, slug_to_mem), ["total"])["total"]
        row = (f"{label:<{w}}{s['c_high']:>8.2f}{s['c_low']:>8.2f}{s['delta']:>+8.2f}"
               f"{s['pct_increase']:>7.1f}%   {auc_cell(s['auc_overall'], overall_ci)}")
        print(row.rstrip())


def run_by_proxy(manifest, dirs, cells):
    """Table 2 (system-deltas): mean comments and per-quality-proxy AUC plus
    overall, with CIs, one (method, model) per row."""
    slug_to_mem = load_manifest(manifest)
    counts = load_counts(dirs, set(slug_to_mem))
    labels, w = _labels_and_width(cells)
    proxy_ids = sorted(PROXY)  # Community / Conference / Reviewer / Composite
    head = (f"{'method__model':<{w}}{'c_bar':>8}   "
            + "".join(f"{PROXY[p]:<18}" for p in proxy_ids) + f"{'Overall':<18}")
    print(head.rstrip())
    for (method, model), label in zip(cells, labels):
        cc = counts.get((method, model))
        if not cc:
            print(f"{label:<{w}}NO DATA"); continue
        s = cell_summary(cc, slug_to_mem)
        by_proxy = by_proxy_totals(cc, slug_to_mem)
        overall, per = cell_aucs(by_proxy)
        (olo, ohi), perci = bootstrap(by_proxy)
        c_bar = (s["c_high"] + s["c_low"]) / 2
        row = f"{label:<{w}}{c_bar:>8.2f}   "
        row += "".join(f"{(auc_cell(per[p], perci[p]) if p in per else '-'):<18}" for p in proxy_ids)
        row += f"{auc_cell(overall, (olo, ohi)):<18}"
        print(row.rstrip())


def run_by_severity(manifest, dirs, cells):
    """Table 9 (severity-aggregate): mean comments on the low-quality group and
    per-severity-tier AUC (Major / Moderate / Minor) plus overall, with CIs."""
    slug_to_mem = load_manifest(manifest)
    counts = load_counts(dirs, set(slug_to_mem))
    labels, w = _labels_and_width(cells)
    # (column header, cell_summary point key, bootstrap tier key)
    TIER_COLS = [("Major", "auc_major", "major"), ("Moderate", "auc_moderate", "moderate"),
                 ("Minor", "auc_minor", "minor"), ("Overall", "auc_overall", "total")]
    print((f"{'method__model':<{w}}{'c_low':>8}   "
           + "".join(f"{name:<18}" for name, _, _ in TIER_COLS)).rstrip())
    for (method, model), label in zip(cells, labels):
        cc = counts.get((method, model))
        if not cc:
            print(f"{label:<{w}}NO DATA"); continue
        s = cell_summary(cc, slug_to_mem)
        ci = bootstrap_tiers(by_proxy_recs(cc, slug_to_mem), [t for _, _, t in TIER_COLS])
        row = f"{label:<{w}}{s['c_low']:>8.2f}   "
        row += "".join(f"{auc_cell(s[pkey], ci[tkey]):<18}" for _, pkey, tkey in TIER_COLS)
        print(row.rstrip())


# Table kind -> the report function that prints it. cells come from the config.
# Each kind maps to one paper-table format: comment_volume = Table 1
# (model-aggregate), by_proxy = Table 2 (system-deltas), by_severity = Table 9
# (severity-aggregate).
DISPATCH = {"comment_volume": run_comment_volume, "by_proxy": run_by_proxy, "by_severity": run_by_severity}


def run_cohort(config, name, base):
    """Run every table defined for one cohort. manifest and dirs in the config
    are resolved relative to `base` (the config file's directory)."""
    cohort = config["cohorts"][name]
    manifest = base / cohort["manifest"]
    dirs = [base / d for d in cohort["dirs"]]
    for table in cohort["tables"]:
        print(f"\n########## {table['title']} ##########")
        cells = [tuple(c) for c in table["cells"]]
        DISPATCH[table["kind"]](manifest, dirs, cells)


if __name__ == "__main__":
    import argparse
    import json
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", type=Path, default=HERE / "ci_auc_tables.json",
                    help="JSON defining cohorts, result dirs, and tables. "
                         "Paths inside it are relative to the config's directory. "
                         "Defaults to ci_auc_tables.json.")
    ap.add_argument("--cohort", help="cohort name from the config "
                                     "(default: the first one defined)")
    args = ap.parse_args()
    config = json.loads(args.config.read_text())
    cohort = args.cohort or next(iter(config["cohorts"]))
    if cohort not in config["cohorts"]:
        ap.error(f"unknown cohort {cohort!r}; choices: {list(config['cohorts'])}")
    run_cohort(config, cohort, args.config.resolve().parent)
