#!/usr/bin/env python
"""Mann-Whitney AUC for the conference outcomes study.

For each (method, model) found in the supplied result directories, computes:

  - Overall pair-hit AUC: for every (low-group paper, high-group paper) pair
    within a quality proxy, count a hit if the low-group paper has more
    comments than the high-group one (ties count as 0.5). AUC = hits / pairs.
    0.5 = chance, 1.0 = perfect ranking.
  - Per-tier AUC (major, moderate, minor) using the same pair-hit definition
    on per-tier comment counts.
  - Mean comments per paper on the high and low groups, Δ, % increase.
  - Paper coverage and pair-count denominator.

\\coarse's native {minor, major, critical} severity tiers are normalized to
{minor, moderate, major} via {critical→major, major→moderate, minor→minor}
so that severity AUCs are comparable across systems.

The script keys papers by the full ``slug`` field from the manifest (not by
forum-id prefix), since some forum-ids start with ``-`` and would collide
under naive splitting.

Usage:
    # Frontier subset (Tables 1/2 in the paper)
    python compute_auc.py \\
        --manifest manifests/v2_frontier/combined.json \\
        --dir frontier_subset_progressive frontier_subset_zero_shot \\
              scaleup_v2_progressive scaleup_v2_zero_shot coarse_v2 \\
              scaleup_v2_grok_progressive scaleup_v2_grok_zero_shot coarse_v2_grok

    # Full 240-paper cohort (Tables 3/4 + appendix)
    python compute_auc.py \\
        --manifest manifests/v2/combined.json \\
        --dir scaleup_v2_zero_shot scaleup_v2_progressive coarse_v2 \\
              scaleup_v2_grok_zero_shot scaleup_v2_grok_progressive coarse_v2_grok

    # Just one (method, model)
    python compute_auc.py --manifest ... --dir ... \\
        --method progressive_original --model grok-4.1-fast
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent  # benchmarks/conference_study/
RESULTS_ROOT = REPO_ROOT / "results"

COARSE_SEVERITY_MAP = {"critical": "major", "major": "moderate", "minor": "minor"}
SEVERITY_TIERS = ("major", "moderate", "minor")


def normalize_severity(method: str, raw: str | None) -> str | None:
    if not raw:
        return None
    raw = raw.lower()
    if method == "coarse":
        return COARSE_SEVERITY_MAP.get(raw)
    return raw if raw in SEVERITY_TIERS else None


def load_manifest(path: Path) -> dict[str, list[dict]]:
    """Returns slug -> list of {pair, side, ...} memberships."""
    data = json.loads(path.read_text())
    return {p["slug"]: p["pair_memberships"] for p in data["papers"]}


def load_counts(
    dirs: list[Path],
    manifest_slugs: set[str],
) -> dict[tuple[str, str], dict[str, dict]]:
    """Returns (method, model) -> {slug: {'total': int, 'major': int, 'moderate': int, 'minor': int}}."""
    counts: dict[tuple[str, str], dict[str, dict]] = defaultdict(dict)
    for d in dirs:
        for f in d.glob("*.json"):
            data = json.loads(f.read_text())
            slug = data.get("slug", "")
            if slug not in manifest_slugs:
                continue
            for mname, mdata in (data.get("methods") or {}).items():
                if "__" not in mname:
                    continue
                method, model = mname.split("__", 1)
                comments = mdata.get("comments") or []
                rec = {"total": len(comments), "major": 0, "moderate": 0, "minor": 0}
                for c in comments:
                    tier = normalize_severity(method, c.get("severity"))
                    if tier:
                        rec[tier] += 1
                # If the same (method, model, slug) appears in multiple dirs,
                # last write wins. Result dirs should be partitioned by run, so
                # this typically does not happen.
                counts[(method, model)][slug] = rec
    return counts


def pair_auc(highs: list[int], lows: list[int]) -> tuple[float, int, int]:
    """Returns (auc, strict_wins, total_pairs). 0.5 credit for ties."""
    hits = 0.0
    wins = 0
    total = 0
    for cl in lows:
        for ch in highs:
            if cl > ch:
                hits += 1
                wins += 1
            elif cl == ch:
                hits += 0.5
            total += 1
    return (hits / total if total else float("nan"), wins, total)


def cell_summary(
    counts_for_cell: dict[str, dict],
    slug_to_memberships: dict[str, list[dict]],
) -> dict:
    """Compute per-cell summary stats. counts_for_cell is {slug: rec}."""
    # Group counts by (pair, side) — for the Δ and AUC computations
    by_pair: dict[int, dict[str, dict[str, list[int]]]] = defaultdict(
        lambda: {"high": {"total": [], "major": [], "moderate": [], "minor": []},
                 "low": {"total": [], "major": [], "moderate": [], "minor": []}}
    )
    for slug, rec in counts_for_cell.items():
        for m in slug_to_memberships.get(slug, []):
            side = m["side"]
            for k in ("total", "major", "moderate", "minor"):
                by_pair[m["pair"]][side][k].append(rec[k])

    # Δ and means across the four (or fewer) proxies
    highs_means: list[float] = []
    lows_means: list[float] = []
    deltas: list[float] = []
    auc_overall_hits = 0.0
    auc_overall_total = 0
    auc_overall_wins = 0
    auc_tier: dict[str, list[float]] = {t: [] for t in SEVERITY_TIERS}
    auc_tier_hits: dict[str, float] = {t: 0.0 for t in SEVERITY_TIERS}
    auc_tier_total: dict[str, int] = {t: 0 for t in SEVERITY_TIERS}
    auc_tier_wins: dict[str, int] = {t: 0 for t in SEVERITY_TIERS}

    for pid in sorted(by_pair):
        h_total = by_pair[pid]["high"]["total"]
        l_total = by_pair[pid]["low"]["total"]
        if not h_total or not l_total:
            continue
        h_mean = mean(h_total)
        l_mean = mean(l_total)
        highs_means.append(h_mean)
        lows_means.append(l_mean)
        deltas.append(l_mean - h_mean)
        # Overall pair AUC
        _, w, t = pair_auc(h_total, l_total)
        auc_overall_wins += w
        auc_overall_total += t
        # accumulate by counting hits directly to avoid float-mean drift
        for cl in l_total:
            for ch in h_total:
                if cl > ch:
                    auc_overall_hits += 1
                elif cl == ch:
                    auc_overall_hits += 0.5
        # Per-tier AUCs
        for tier in SEVERITY_TIERS:
            ht = by_pair[pid]["high"][tier]
            lt = by_pair[pid]["low"][tier]
            for cl in lt:
                for ch in ht:
                    if cl > ch:
                        auc_tier_hits[tier] += 1
                        auc_tier_wins[tier] += 1
                    elif cl == ch:
                        auc_tier_hits[tier] += 0.5
                    auc_tier_total[tier] += 1

    if not highs_means:
        return {}

    h = mean(highs_means)
    l = mean(lows_means)
    d = mean(deltas)
    pct = (d / h * 100) if h else float("nan")
    out = {
        "n_papers": len(counts_for_cell),
        "c_high": h,
        "c_low": l,
        "delta": d,
        "pct_increase": pct,
        "auc_overall": auc_overall_hits / auc_overall_total if auc_overall_total else float("nan"),
        "auc_overall_wins": auc_overall_wins,
        "auc_overall_total": auc_overall_total,
    }
    for tier in SEVERITY_TIERS:
        tot = auc_tier_total[tier]
        out[f"auc_{tier}"] = auc_tier_hits[tier] / tot if tot else float("nan")
        out[f"auc_{tier}_wins"] = auc_tier_wins[tier]
        out[f"auc_{tier}_total"] = tot
    return out


def render_markdown(rows: list[tuple[str, str, dict]]) -> str:
    """Render the summary as a markdown table on stdout."""
    lines = []
    lines.append(
        "| method | model | n_papers | c_high | c_low | Δ | %inc | "
        "AUC overall | AUC major | AUC mod | AUC minor | pairs |"
    )
    lines.append(
        "|---|---|---|---|---|---|---|---|---|---|---|---|"
    )
    for method, model, s in rows:
        if not s:
            lines.append(f"| {method} | {model} | 0 | - | - | - | - | - | - | - | - | 0 |")
            continue
        lines.append(
            f"| {method} | {model} | {s['n_papers']} | "
            f"{s['c_high']:.2f} | {s['c_low']:.2f} | "
            f"{s['delta']:+.2f} | {s['pct_increase']:.1f}% | "
            f"**{s['auc_overall']:.3f}** | "
            f"{s['auc_major']:.3f} | {s['auc_moderate']:.3f} | {s['auc_minor']:.3f} | "
            f"{s['auc_overall_total']} |"
        )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--manifest", required=True, type=Path, help="Path to manifest JSON (e.g., manifests/v2/combined.json).")
    p.add_argument("--dir", nargs="+", required=True, dest="dirs",
                   help="One or more result subdirectories under results/ (e.g., scaleup_v2_progressive).")
    p.add_argument("--method", default=None, help="Filter to one method (e.g., progressive_original, zero_shot, coarse).")
    p.add_argument("--model", default=None, help="Filter to one model (e.g., grok-4.1-fast).")
    args = p.parse_args()

    manifest_path = args.manifest if args.manifest.is_absolute() else (REPO_ROOT / args.manifest)
    if not manifest_path.exists():
        print(f"manifest not found: {manifest_path}", file=sys.stderr)
        return 1
    slug_to_memberships = load_manifest(manifest_path)

    dirs = []
    for d in args.dirs:
        path = Path(d)
        if not path.is_absolute():
            path = RESULTS_ROOT / d
        if not path.is_dir():
            print(f"warning: result dir not found: {path}", file=sys.stderr)
            continue
        dirs.append(path)
    if not dirs:
        print("no valid result dirs", file=sys.stderr)
        return 1

    counts = load_counts(dirs, set(slug_to_memberships))

    rows: list[tuple[str, str, dict]] = []
    for (method, model) in sorted(counts):
        if args.method and method != args.method:
            continue
        if args.model and model != args.model:
            continue
        s = cell_summary(counts[(method, model)], slug_to_memberships)
        rows.append((method, model, s))

    if not rows:
        print("no (method, model) cells matched the filters", file=sys.stderr)
        return 1

    print(f"# AUC summary")
    print(f"manifest: `{manifest_path.relative_to(REPO_ROOT) if manifest_path.is_relative_to(REPO_ROOT) else manifest_path}` ({len(slug_to_memberships)} papers)")
    print(f"dirs: {[d.name for d in dirs]}")
    print()
    print(render_markdown(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
