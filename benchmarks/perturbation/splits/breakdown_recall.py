#!/usr/bin/env python3
"""Bucket per-cell score JSONs by error subtype using a split file.

Inputs:
  --split-file: splits/val.json or splits/test.json
  --baseline-root: results dir holding the baseline `full_<domain>/` trees
  --variant-roots: glob(s) of variant results dirs (one per variant×split×domain)
  --model: model slug (e.g. deepseek-v4-flash) — directory under each tree
  --method: review method to score (zero_shot | progressive | ...)

Output: a single JSON document at --out summarising per-bucket recall for
baseline (filtered to split papers only) and for each provided variant root,
both per-domain and micro-averaged across the split.

Buckets follow the paper's Table 6 columns:
  op_sign / idx_sub / numeric / computation   (surface math)
  claim / reasoning / experimental            (prose)
A given subtype's bucket is derived from its `error` field (see
benchmarks/perturbation/models.py:Error).
"""

from __future__ import annotations

import argparse
import glob
import json
import re
from collections import defaultdict
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]


# Subtype -> bucket. Bucket "claim" is shared across empirical and theoretical
# domains so the comparison table has one Claim row (matches paper Table 6).
SUBTYPE_BUCKET = {
    # surface
    "operator_or_sign":       "op_sign",
    "index_or_subscript":     "idx_sub",
    "numeric_parameter":      "numeric",
    "computation":            "computation",
    # symbol_binding is deprecated -> drop (not reported in Table 6)
    "symbol_binding":         None,
    # claim
    "incorrect_claim_theoretical":   "claim",
    "incorrect_statement_empirical": "claim",
    # reasoning (logic)
    "missing_case":           "reasoning",
    "induction":              "reasoning",
    "circular_reasoning":     "reasoning",
    "invalid_implication":    "reasoning",
    # experimental
    "misinterp":              "experimental",
    "causal_reversed":        "experimental",
    "p_hacking":              "experimental",
}

BUCKETS_ORDER = ["op_sign", "idx_sub", "numeric", "computation",
                 "claim", "reasoning", "experimental"]


def _empty_bucket_counts() -> dict:
    return {b: {"detected": 0, "total": 0} for b in BUCKETS_ORDER}


def _domain_from_dir(results_dir: Path, baseline: bool) -> str | None:
    """For baseline `full_<domain>` and variant `promptvariant_<...>_<domain>` dirs."""
    name = results_dir.name
    if baseline:
        m = re.match(r"^full_(.+?)(?:_reviewer3)?$", name)
        return m.group(1) if m else None
    m = re.match(r"^promptvariant_.+?_(?:val|test)_(.+)$", name)
    return m.group(1) if m else None


def _normalize_domain(d: str) -> str:
    # baseline dirs use underscores (full_physics_atm_clus) while split files use
    # the on-disk domain (physics_atm-clus). Normalize via the file system.
    candidates = [d, d.replace("_", "-", 1), d.replace("-", "_", 1)]
    # specific known transform: full_physics_atm_clus -> physics_atm-clus
    candidates += [d.replace("physics_atm_clus", "physics_atm-clus")]
    candidates += [d.replace("q_bio_GN", "q-bio_GN").replace("hep_ex", "hep-ex")]
    return next(iter(candidates))  # caller will retry with each


def _candidate_domains(d: str) -> list[str]:
    out = {d}
    out.add(d.replace("physics_atm_clus", "physics_atm-clus"))
    out.add(d.replace("q_bio_GN", "q-bio_GN"))
    out.add(d.replace("hep_ex", "hep-ex"))
    return list(out)


def _walk_cells(model_dir: Path, method: str, paper_labels: set[str]):
    """Yield (error_type, paper_label, score_json_path) for cells whose
    paper_label is in `paper_labels` and whose method dir matches `method`
    (or `method__<variant>`)."""
    for err_dir in model_dir.iterdir():
        if not err_dir.is_dir():
            continue
        err = err_dir.name
        for method_dir in err_dir.iterdir():
            if not method_dir.is_dir():
                continue
            # Accept either exact method or method__variant
            if method_dir.name != method and not method_dir.name.startswith(method + "__"):
                continue
            for paper_dir in method_dir.iterdir():
                if not paper_dir.is_dir() or paper_dir.name not in paper_labels:
                    continue
                score_root = paper_dir / "score"
                if not score_root.is_dir():
                    continue
                for sub in score_root.iterdir():
                    if not sub.is_dir():
                        continue
                    # Prefer llm_t4_grounded if present; otherwise pick the lone
                    # subdir we have.
                    pass
                # pick t4_grounded first
                preferred = score_root / "llm_t4_grounded"
                if preferred.is_dir():
                    sjson = next(preferred.glob("*_score.json"), None)
                    if sjson:
                        yield err, paper_dir.name, sjson
                        continue
                # fallback: any score subdir
                for sub in score_root.iterdir():
                    if sub.is_dir():
                        sjson = next(sub.glob("*_score.json"), None)
                        if sjson:
                            yield err, paper_dir.name, sjson
                            break


def _bucket_for_domain(results_dir: Path, domain: str, model: str, method: str,
                       paper_labels: set[str]) -> dict:
    """Return per-bucket {detected,total} counts for one (results_dir, domain)."""
    counts = _empty_bucket_counts()
    perturb_root = results_dir / "perturb"
    model_dir = results_dir / model
    if not model_dir.is_dir() or not perturb_root.is_dir():
        return counts

    for err, paper_label, sjson in _walk_cells(model_dir, method, paper_labels):
        manifest_path = perturb_root / err / paper_label / f"{paper_label}_perturbations.json"
        if not manifest_path.exists():
            continue
        manifest = json.loads(manifest_path.read_text())
        pid_to_error = {p["perturbation_id"]: p["error"] for p in manifest.get("perturbations", [])}
        score = json.loads(sjson.read_text())
        detected_pids = set(score.get("detected", []))
        for pid, err_subtype in pid_to_error.items():
            bucket = SUBTYPE_BUCKET.get(err_subtype)
            if bucket is None:
                continue
            counts[bucket]["total"] += 1
            if pid in detected_pids:
                counts[bucket]["detected"] += 1
    return counts


def _aggregate(domain_counts: dict[str, dict]) -> dict:
    """Sum per-domain bucket counts into one micro-averaged dict + recall."""
    out = _empty_bucket_counts()
    for dc in domain_counts.values():
        for b in BUCKETS_ORDER:
            out[b]["detected"] += dc[b]["detected"]
            out[b]["total"] += dc[b]["total"]
    for b in BUCKETS_ORDER:
        t = out[b]["total"]
        out[b]["recall"] = (out[b]["detected"] / t) if t else None
    return out


def _add_recalls(dc: dict) -> dict:
    for b in BUCKETS_ORDER:
        t = dc[b]["total"]
        dc[b]["recall"] = (dc[b]["detected"] / t) if t else None
    return dc


def _domain_from_config(results_dir: Path) -> str | None:
    """Read results_dir/config.yaml's input_dir and pull the domain name."""
    cfg = results_dir / "config.yaml"
    if not cfg.exists():
        return None
    data = yaml.safe_load(cfg.read_text()) or {}
    inp = data.get("input_dir", "")
    # .../data/perturbations_filtered/<domain>/all
    m = re.search(r"perturbations_filtered/([^/]+)/all", inp)
    return m.group(1) if m else None


def analyse_root(results_dir: Path, split: dict, model: str, method: str,
                 baseline: bool) -> dict:
    """For a single results_dir, return {domain: bucket_counts, _overall: ...}."""
    per_domain: dict[str, dict] = {}
    # Prefer reading the domain from the saved config.yaml — works for both
    # baseline trees (full_cs_LG/, cs_CC_scaleup_v2/) and variant trees.
    dom = _domain_from_config(results_dir) or _domain_from_dir(results_dir, baseline)
    if dom is None:
        return {"per_domain": {}, "_overall": _empty_bucket_counts()}
    target = next((c for c in _candidate_domains(dom) if c in split["domains"]), dom)
    labels = set(split["domains"].get(target, {}).get("paper_labels", []))
    if labels:
        per_domain[target] = _add_recalls(
            _bucket_for_domain(results_dir, target, model, method, labels))
    overall = _aggregate(per_domain)
    return {"per_domain": per_domain, "_overall": overall}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split-file", type=Path, required=True)
    ap.add_argument("--baseline-roots", nargs="+", default=[],
                    help="One or more baseline results dirs (each is one domain). "
                         "Glob patterns accepted.")
    ap.add_argument("--variant-roots", nargs="+", default=[],
                    help="One or more globs of variant results dirs")
    ap.add_argument("--model", default="deepseek-v4-flash",
                    help="Model dir slug under each results tree")
    ap.add_argument("--method", required=True, choices=["zero_shot", "progressive"])
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    split = json.loads(args.split_file.read_text())

    def _expand(patterns):
        out = []
        for p in patterns:
            matched = sorted(Path(x) for x in glob.glob(p))
            if not matched:
                # treat as a literal path
                matched = [Path(p)]
            out.extend(matched)
        return out

    report: dict = {}
    # baseline: list of one-domain dirs (e.g. full_cs_LG, cs_CC_scaleup_v2)
    baseline_dirs = _expand(args.baseline_roots)
    if baseline_dirs:
        merged_per_domain: dict[str, dict] = {}
        for rdir in baseline_dirs:
            sub = analyse_root(rdir, split, args.model, args.method, baseline=True)
            for d, dc in sub.get("per_domain", {}).items():
                merged_per_domain[d] = dc
        report["baseline"] = {
            "per_domain": merged_per_domain,
            "_overall": _aggregate(merged_per_domain),
        }

    # Expand every pattern, then group by derived label so domains aggregate
    # cleanly when the caller passes already-shell-expanded paths.
    all_variant_dirs = _expand(args.variant_roots)
    by_label: dict[str, list[Path]] = {}
    # Group by the variant-and-split prefix:
    # "promptvariant_<method>_<variant>_<splitname>_<domain>" → label
    # = "promptvariant_<method>_<variant>_<splitname>"
    for rdir in all_variant_dirs:
        parts = rdir.name.split("_")
        if len(parts) >= 5 and parts[0] == "promptvariant":
            # method may itself contain underscores ("zero_shot"); find the split
            # by matching against known splits via the splits/ dir lookup.
            # Simpler heuristic: drop the final segment (the domain) — but the
            # domain itself can contain underscores ("cs_LG", "physics_atm-clus"
            # has only one underscore in the raw name "physics_atm-clus" though
            # on disk hyphens appear in domain names too). Strategy: read the
            # config.yaml's results_dir parent to find the right grouping.
            from_cfg = (rdir / "config.yaml")
            if from_cfg.exists():
                cfg = yaml.safe_load(from_cfg.read_text()) or {}
                rd = cfg.get("results_dir", "")
                rd_name = Path(rd).name
                # rd_name = "promptvariant_<method>_<variant>_<split>_<domain>"
                # drop the last "_<domain>" segment
                # use the config.yaml's input_dir to derive the domain
                inp = cfg.get("input_dir", "")
                m2 = re.search(r"perturbations_filtered/([^/]+)/all", inp)
                dom = m2.group(1) if m2 else ""
                if dom and rd_name.endswith("_" + dom):
                    lab = rd_name[: -len("_" + dom)]
                else:
                    lab = rd_name
            else:
                lab = rdir.name
        else:
            lab = rdir.name
        by_label.setdefault(lab, []).append(rdir)
    for label, dirs in by_label.items():
        merged_per_domain: dict[str, dict] = {}
        for rdir in dirs:
            sub = analyse_root(rdir, split, args.model, args.method, baseline=False)
            for d, dc in sub.get("per_domain", {}).items():
                merged_per_domain[d] = dc
        report[label] = {
            "per_domain": merged_per_domain,
            "_overall": _aggregate(merged_per_domain),
        }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2))
    print(f"Wrote {args.out}")
    for label, payload in report.items():
        ov = payload["_overall"]
        bits = " ".join(
            f"{b}={ov[b]['detected']}/{ov[b]['total']}"
            for b in BUCKETS_ORDER if ov[b]['total']
        )
        print(f"  {label}: {bits}")


if __name__ == "__main__":
    main()
