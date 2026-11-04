#!/usr/bin/env python
"""Produce the paper's quality-proxy tables from a run's results.

Reads the result JSONs for a run (selected by --config or --results-dir) and the
manifest's high/low group memberships, then prints the pairwise-accuracy
(Mann-Whitney AUC) tables with 95% cluster-bootstrap confidence intervals: the
per-model comment-volume table, the per-quality-proxy table, and the
per-severity-tier table.

The (method, model) cells are discovered from whatever is present in the
results, so no separate table config is needed: run the systems (step 4), then
point this at their results directories. Pass several to compare systems in one
table. By default it shows the manifest's roster models and openaireview's
pre-consolidation progressive output (the variant the paper reports). Use
--all-models and --consolidated to change that. The AUC and bootstrap math lives
in compute_auc.py and ci_auc.py, and this script is the reporting entry point
over them.

Usage:
    python analyses/generate_report.py --config configs/baseline.yaml
    # merge systems into one set of tables
    python analyses/generate_report.py --config configs/baseline.yaml configs/coarse.yaml
    python analyses/generate_report.py --results-dir results/baseline results/coarse \
        --manifest manifests/canonical/full.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

import ci_auc
from compute_auc import load_counts, load_manifest

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent  # benchmarks/conference_study

# (heading, ci_auc table kind) — printed in order over the discovered cells.
TABLES = [
    ("Comment volume and overall accuracy, per model", "comment_volume"),
    ("Accuracy by quality proxy", "by_proxy"),
    ("Accuracy by severity tier", "by_severity"),
]


def _resolve(path: Path, base: Path) -> Path:
    return path if path.is_absolute() else (base / path)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", type=Path, nargs="+",
                    help="one or more run config YAMLs, merged (e.g. baseline.yaml coarse.yaml)")
    ap.add_argument("--results-dir", type=Path, nargs="+",
                    help="one or more results directories, merged")
    ap.add_argument("--manifest", type=Path,
                    help="manifest JSON (defaults to the first config's, then manifests/canonical/full.json)")
    ap.add_argument("--all-models", action="store_true",
                    help="show every model found, not just the manifest's roster")
    ap.add_argument("--consolidated", action="store_true",
                    help="show openaireview's consolidated progressive output instead of the "
                         "pre-consolidation progressive_original the paper reports")
    args = ap.parse_args()
    if not args.config and not args.results_dir:
        ap.error("pass --config or --results-dir")

    configs = [yaml.safe_load(p.read_text()) for p in (args.config or [])]

    dirs = [_resolve(p, Path.cwd()) for p in (args.results_dir or [])]
    dirs += [STUDY / "results" / cfg["name"] for cfg in configs]
    missing = [str(d) for d in dirs if not d.exists()]
    if missing:
        sys.exit("results directory not found: " + ", ".join(missing))

    default_manifest = configs[0].get("manifest") if configs else None
    manifest = _resolve(args.manifest or Path(default_manifest or "manifests/canonical/full.json"), STUDY)
    if not manifest.exists():
        sys.exit(f"manifest not found: {manifest}")

    # Discover the (method, model) cells across the result dirs. By default keep
    # only the manifest's roster models (dropping exploratory runs that linger in
    # the result dirs) and the consolidated progressive output. A model-less
    # system keyed as <system>__<system> (e.g. reviewer3) is always kept.
    slug_to_mem = load_manifest(manifest)
    roster = {m.rsplit("/", 1)[-1] for m in json.loads(manifest.read_text()).get("models", [])}
    cells = sorted(load_counts(dirs, set(slug_to_mem)))
    if roster and not args.all_models:
        cells = [c for c in cells if c[1] in roster or c[1] == c[0]]
    # openaireview writes two variants per run: progressive_original (raw, the
    # variant the paper reports) and progressive (after consolidation). Show the
    # paper's by default; --consolidated switches to the consolidated one.
    drop_variant = "progressive_original" if args.consolidated else "progressive"
    cells = [c for c in cells if c[0] != drop_variant]
    if not cells:
        sys.exit("no (method, model) results found under: " + ", ".join(str(d) for d in dirs))

    print(f"Results: {', '.join(d.name for d in dirs)}\nManifest: {manifest.name} "
          f"({len(slug_to_mem)} papers)\nCells: {len(cells)} (method, model)\n")
    for heading, kind in TABLES:
        print(f"\n########## {heading} ##########")
        ci_auc.DISPATCH[kind](manifest, dirs, cells)


if __name__ == "__main__":
    main()
