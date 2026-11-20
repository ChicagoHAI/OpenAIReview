"""Quantify generator selection bias: selected perturbation spans vs. the candidate pool.

The generator LLM picks which candidate spans to perturb (in batches of 10).
Random selection would yield a selected subset whose feature distribution
matches the pool, so any divergence between selected and pool measures
selection bias directly, with no new LLM calls.

Walks `--input-root` for `*_perturbations.json` files, re-extracts the
candidate pool from the matching `_clean.md` (extraction is deterministic,
so span_ids are reproduced exactly), reconstructs the batches the generator
saw, and marks which candidates were selected (survived generation +
structural validation) and which were kept (survived the substantive-error
verifier, from `--filtered-root`).

Analyses:
  1. Sanity check: manifest `original` matches the re-extracted span text.
  2. Selection rates per run; runs with 100% selection have no freedom and
     are excluded from bias tests.
  3. Span type: selection rate per span_type within mixed-type pools.
  4. Span length: selected vs unselected, within-paper.
  5. Within-batch position: permutation test for primacy bias.
  6. Document position: selection rate by offset quartile.
  7. Pool truncation: how much the 20-per-type extraction cap discards.
  8. Equation error-subtype choice (free choice, no pool baseline).

Confidence intervals use a cluster bootstrap over papers.

Usage:
    python -m benchmarks.perturbation.analyses.selection_bias
    python -m benchmarks.perturbation.analyses.selection_bias --error-type surface
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from .. import extract as extract_mod
from ..extract import extract_candidates
from ..generate import _BATCH_SIZE
from .verify_existing import _paper_category_for

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT_ROOT = REPO_ROOT / "benchmarks" / "perturbation" / "data" / "perturbations"
DEFAULT_FILTERED_ROOT = REPO_ROOT / "benchmarks" / "perturbation" / "data" / "perturbations_filtered"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "benchmarks" / "perturbation" / "results" / "selection_bias"

RNG = np.random.default_rng(0)
N_BOOT = 2000
N_PERM = 10000

EQUATION_TYPES = {"equation_display", "equation_inline", "equation_named"}


def _collect_rows(input_root: Path, filtered_root: Path, error_type_filter: str | None):
    """One row per (run, candidate). Returns (rows, run_stats, sanity)."""
    rows: list[dict] = []
    run_stats: list[dict] = []
    sanity = {"n_perturbations": 0, "span_id_missing": 0, "text_mismatch": 0, "runs_skipped": []}

    for perts_path in sorted(input_root.rglob("*_perturbations.json")):
        rel = perts_path.relative_to(input_root)
        error_type_run = perts_path.parent.name
        if error_type_filter and error_type_run != error_type_filter:
            continue
        slug = perts_path.name.replace("_perturbations.json", "")
        clean_md = perts_path.with_name(f"{slug}_clean.md")
        if not clean_md.exists():
            sanity["runs_skipped"].append(f"{rel}: no _clean.md")
            continue

        manifest = json.loads(perts_path.read_text())
        field = rel.parts[0]
        paper = rel.parts[2]  # <field>/all/<arxiv_id>/<error_type>/
        text = clean_md.read_text()
        category = _paper_category_for(error_type_run)
        candidates = extract_candidates(category, error_type_run, text)

        # Sanity: re-extraction must reproduce the pool the generator saw.
        if len(candidates) != manifest["n_candidates"]:
            sanity["runs_skipped"].append(
                f"{rel}: re-extracted {len(candidates)} candidates, manifest says {manifest['n_candidates']}"
            )
            continue

        by_id = {c.span_id: c for c in candidates}
        selected: dict[str, str] = {}  # span_id -> chosen error subtype
        for p in manifest["perturbations"]:
            sanity["n_perturbations"] += 1
            cand = by_id.get(p["span_id"])
            if cand is None:
                sanity["span_id_missing"] += 1
                continue
            if p["original"] != cand.text and p["original"] not in cand.text:
                sanity["text_mismatch"] += 1
            selected[p["span_id"]] = p["error"]

        kept_ids: set[str] = set()
        kept_path = filtered_root / rel.parent / f"{slug}_kept_perturbations.json"
        if kept_path.exists():
            kept = json.loads(kept_path.read_text())
            kept_ids = {p["span_id"] for p in kept.get("perturbations", [])}

        # Full pool without the per-type cap, to measure truncation.
        cap = extract_mod._MAX_PER_SPAN_TYPE
        extract_mod._MAX_PER_SPAN_TYPE = 10 ** 9
        try:
            uncapped = extract_candidates(category, error_type_run, text)
        finally:
            extract_mod._MAX_PER_SPAN_TYPE = cap
        uncapped_counts = Counter(c.span_type.value for c in uncapped)
        capped_counts = Counter(c.span_type.value for c in candidates)

        batches = [candidates[i:i + _BATCH_SIZE] for i in range(0, len(candidates), _BATCH_SIZE)]
        for batch_idx, batch in enumerate(batches):
            for pos, c in enumerate(batch):
                rows.append({
                    "field": field,
                    "paper": paper,
                    "error_type_run": error_type_run,
                    "slug": slug,
                    "span_id": c.span_id,
                    "span_type": c.span_type.value,
                    "len_chars": len(c.text),
                    "offset_frac": c.offset / max(1, len(text)),
                    "batch_idx": batch_idx,
                    "n_batches": len(batches),
                    "pos_in_batch": pos,
                    "batch_size": len(batch),
                    "selected": int(c.span_id in selected),
                    "kept": int(c.span_id in kept_ids),
                    "chosen_error": selected.get(c.span_id, ""),
                })

        run_stats.append({
            "run": str(rel.parent),
            "error_type_run": error_type_run,
            "paper": paper,
            "n_candidates": len(candidates),
            "n_selected": len(selected),
            "n_kept": len(kept_ids),
            "n_generated": manifest.get("n_generated"),
            "selection_rate": len(selected) / max(1, len(candidates)),
            "truncation": {
                t: {"uncapped": uncapped_counts[t], "capped": capped_counts[t]}
                for t in uncapped_counts
            },
        })

    return rows, run_stats, sanity


# ---------------------------------------------------------------------------
# Statistics helpers
# ---------------------------------------------------------------------------

def _cluster_bootstrap_rate_diff(rows, key_fn, group_a, group_b, outcome="selected"):
    """Bootstrap CI (over papers) for rate(group_a) - rate(group_b)."""
    by_paper: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_paper[r["paper"]].append(r)
    papers = sorted(by_paper)

    def point(sample_papers):
        a_n = a_d = b_n = b_d = 0
        for p in sample_papers:
            for r in by_paper[p]:
                g = key_fn(r)
                if g == group_a:
                    a_n += r[outcome]; a_d += 1
                elif g == group_b:
                    b_n += r[outcome]; b_d += 1
        if a_d == 0 or b_d == 0:
            return None
        return a_n / a_d - b_n / b_d

    est = point(papers)
    if est is None:
        return None
    boots = []
    for _ in range(N_BOOT):
        sample = RNG.choice(papers, size=len(papers), replace=True)
        v = point(list(sample))
        if v is not None:
            boots.append(v)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {"diff": est, "ci_lo": float(lo), "ci_hi": float(hi)}


def _position_permutation_test(rows):
    """Within-batch primacy test.

    Statistic: mean within-batch position of selected candidates minus its
    expectation under random within-batch selection (averaged over batches
    with partial selection). Negative = primacy bias (early items favored).
    The null is built by permuting the selected mask within each batch.
    """
    batches: dict[tuple, list[dict]] = defaultdict(list)
    for r in rows:
        batches[(r["slug"], r["error_type_run"], r["paper"], r["batch_idx"])].append(r)

    obs_terms, perm_batches = [], []
    for key, items in batches.items():
        items.sort(key=lambda r: r["pos_in_batch"])
        sel = np.array([r["selected"] for r in items])
        k, m = int(sel.sum()), len(sel)
        if k == 0 or k == m or m < 2:
            continue  # no selection freedom in this batch
        pos = np.arange(m)
        expected = pos.mean()
        obs_terms.append(pos[sel == 1].mean() - expected)
        perm_batches.append((pos, k, expected))

    if not obs_terms:
        return None
    observed = float(np.mean(obs_terms))

    null = np.empty(N_PERM)
    for i in range(N_PERM):
        terms = [
            RNG.choice(pos, size=k, replace=False).mean() - expected
            for pos, k, expected in perm_batches
        ]
        null[i] = np.mean(terms)
    p_value = float(np.mean(np.abs(null) >= abs(observed)))
    return {
        "observed_mean_position_shift": observed,
        "p_value": p_value,
        "n_partial_batches": len(perm_batches),
        "null_sd": float(null.std()),
    }


def _rate_by_bin(rows, value_fn, n_bins=4, outcome="selected"):
    """Selection rate by within-run quantile bin of a numeric feature."""
    by_run: dict[tuple, list[dict]] = defaultdict(list)
    for r in rows:
        by_run[(r["slug"], r["error_type_run"], r["paper"])].append(r)

    bin_counts = np.zeros(n_bins)
    bin_sel = np.zeros(n_bins)
    for items in by_run.values():
        vals = np.array([value_fn(r) for r in items], dtype=float)
        if len(set(vals)) < 2:
            continue
        edges = np.quantile(vals, np.linspace(0, 1, n_bins + 1))
        bins = np.clip(np.searchsorted(edges, vals, side="right") - 1, 0, n_bins - 1)
        for b, r in zip(bins, items):
            bin_counts[b] += 1
            bin_sel[b] += r[outcome]
    return {
        f"q{i + 1}": {"rate": float(bin_sel[i] / bin_counts[i]), "n": int(bin_counts[i])}
        for i in range(n_bins) if bin_counts[i] > 0
    }


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input-root", type=Path, default=DEFAULT_INPUT_ROOT)
    ap.add_argument("--filtered-root", type=Path, default=DEFAULT_FILTERED_ROOT)
    ap.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    ap.add_argument("--error-type", default=None,
                    help="Restrict to one error_type run dir (e.g. surface)")
    args = ap.parse_args()

    rows, run_stats, sanity = _collect_rows(args.input_root, args.filtered_root, args.error_type)
    print(f"{len(run_stats)} runs, {len(rows)} candidate rows")
    print(f"Sanity: {sanity['n_perturbations']} perturbations, "
          f"{sanity['span_id_missing']} missing span_ids, "
          f"{sanity['text_mismatch']} text mismatches, "
          f"{len(sanity['runs_skipped'])} runs skipped")
    for s in sanity["runs_skipped"]:
        print(f"  SKIPPED {s}")

    # Restrict bias analyses to runs with selection freedom.
    full_runs = {s["run"] for s in run_stats if s["selection_rate"] >= 1.0}
    free_rows = [
        r for r in rows
        if f"{Path(r['field']) / 'all' / r['paper'] / r['error_type_run']}" not in full_runs
    ]
    print(f"{len(full_runs)} runs selected 100% of candidates (excluded from bias tests); "
          f"{len(free_rows)} rows remain")

    summary: dict = {
        "n_runs": len(run_stats),
        "n_rows": len(rows),
        "sanity": sanity,
        "n_full_selection_runs": len(full_runs),
        "by_error_type": {},
    }

    error_types = sorted({r["error_type_run"] for r in free_rows})
    for et in error_types:
        sub = [r for r in free_rows if r["error_type_run"] == et]
        et_summary: dict = {
            "n_rows": len(sub),
            "overall_selection_rate": float(np.mean([r["selected"] for r in sub])),
        }

        # 3. Span type rates (only informative for mixed-type pools).
        type_rates = {}
        for st in sorted({r["span_type"] for r in sub}):
            st_rows = [r for r in sub if r["span_type"] == st]
            type_rates[st] = {
                "rate": float(np.mean([r["selected"] for r in st_rows])),
                "n_pool": len(st_rows),
                "n_selected": int(sum(r["selected"] for r in st_rows)),
            }
        et_summary["selection_rate_by_span_type"] = type_rates
        types = sorted(type_rates, key=lambda t: -type_rates[t]["n_pool"])
        if len(types) >= 2:
            et_summary["span_type_top2_diff"] = _cluster_bootstrap_rate_diff(
                sub, lambda r: r["span_type"], types[0], types[1])

        # 4. Length and 6. document position, by within-run quartile.
        et_summary["selection_rate_by_length_quartile"] = _rate_by_bin(
            sub, lambda r: r["len_chars"])
        et_summary["selection_rate_by_offset_quartile"] = _rate_by_bin(
            sub, lambda r: r["offset_frac"])

        # 5. Within-batch position permutation test.
        et_summary["within_batch_position"] = _position_permutation_test(sub)

        # 8. Chosen subtype distribution for equation spans.
        eq_sel = [r for r in sub if r["span_type"] in EQUATION_TYPES and r["selected"]]
        if eq_sel:
            et_summary["equation_subtype_choice"] = {
                st: dict(Counter(r["chosen_error"] for r in eq_sel if r["span_type"] == st))
                for st in sorted({r["span_type"] for r in eq_sel})
            }

        summary["by_error_type"][et] = et_summary

    # 7. Pool truncation from the 20-per-type extraction cap.
    trunc: dict[str, dict[str, int]] = defaultdict(lambda: {"uncapped": 0, "capped": 0, "runs_capped": 0})
    for s in run_stats:
        for t, c in s["truncation"].items():
            trunc[t]["uncapped"] += c["uncapped"]
            trunc[t]["capped"] += c["capped"]
            trunc[t]["runs_capped"] += int(c["uncapped"] > c["capped"])
    summary["pool_truncation_by_span_type"] = {
        t: {**v, "fraction_discarded": 1 - v["capped"] / v["uncapped"]}
        for t, v in sorted(trunc.items())
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows_path = args.output_dir / "candidate_rows.csv"
    with rows_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    (args.output_dir / "run_stats.json").write_text(json.dumps(run_stats, indent=2))
    summary_path = args.output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    print(f"\nWrote {rows_path}")
    print(f"Wrote {summary_path}")

    # Console digest.
    for et, s in summary["by_error_type"].items():
        print(f"\n=== {et} (selection rate {s['overall_selection_rate']:.2f}) ===")
        for st, v in s["selection_rate_by_span_type"].items():
            print(f"  {st:22s} rate {v['rate']:.2f}  ({v['n_selected']}/{v['n_pool']})")
        d = s.get("span_type_top2_diff")
        if d:
            print(f"  top-2 type rate diff {d['diff']:+.2f}  CI [{d['ci_lo']:+.2f}, {d['ci_hi']:+.2f}]")
        lq = s["selection_rate_by_length_quartile"]
        print("  by length quartile:  " + "  ".join(f"{k}={v['rate']:.2f}" for k, v in lq.items()))
        oq = s["selection_rate_by_offset_quartile"]
        print("  by offset quartile:  " + "  ".join(f"{k}={v['rate']:.2f}" for k, v in oq.items()))
        wb = s["within_batch_position"]
        if wb:
            print(f"  within-batch position shift {wb['observed_mean_position_shift']:+.2f} "
                  f"(p={wb['p_value']:.4f}, {wb['n_partial_batches']} partial batches)")


if __name__ == "__main__":
    main()
