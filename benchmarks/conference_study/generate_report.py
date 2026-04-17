#!/usr/bin/env python
"""Compute summary tables from conference study results.

Reads the result JSONs and run log to produce the markdown tables found in
reports/baseline.md. Can optionally parse PDFs to compute per-paper page
counts and effective token counts (requires papers/ on disk).

Usage:
    python generate_report.py                                 # legacy results/
    python generate_report.py --config configs/baseline.yaml  # results/<name>/
    python generate_report.py --results-dir results/baseline  # explicit
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent

# Models in display order (short name -> full name mapping built at runtime).
MODEL_ORDER = ["gemini-3-flash-preview", "glm-4.6", "qwen3-235b-a22b-2507"]


# ---------------------------------------------------------------------------
# Config loading (same pattern as run_study.py / estimate_cost.py)
# ---------------------------------------------------------------------------

def load_config(path: str) -> dict:
    if not path:
        return {}
    cfg_path = Path(path)
    if not cfg_path.is_absolute():
        cfg_path = cfg_path if cfg_path.exists() else HERE / path
    if not cfg_path.exists():
        sys.exit(f"config file not found: {path}")
    with cfg_path.open() as f:
        return yaml.safe_load(f) or {}


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_results(results_dir: Path, manifest: dict) -> dict[str, dict]:
    """Load result JSONs for all papers in the manifest."""
    results = {}
    for p in manifest["papers"]:
        slug = p["slug"]
        path = results_dir / f"{slug}.json"
        if not path.exists():
            print(f"  warning: missing {path}", file=sys.stderr)
            continue
        results[slug] = json.loads(path.read_text())
    return results


def load_run_log(results_dir: Path) -> list[dict]:
    """Load run_log.jsonl entries."""
    log_path = results_dir / "run_log.jsonl"
    if not log_path.exists():
        return []
    entries = []
    for line in log_path.read_text().splitlines():
        if line.strip():
            entries.append(json.loads(line))
    return entries


def model_short(model: str) -> str:
    return model.split("/")[-1] if "/" in model else model


def paper_group(slug: str, manifest: dict) -> str:
    for p in manifest["papers"]:
        if p["slug"] == slug:
            return p["group"]
    return "unknown"


# ---------------------------------------------------------------------------
# Papers table (requires PDFs on disk)
# ---------------------------------------------------------------------------

def compute_papers_table(manifest: dict, max_pages: int, max_tokens: int) -> list[dict]:
    """Parse PDFs to get page counts and effective token counts."""
    sys.path.insert(0, str(REPO / "src"))
    from reviewer.parsers import parse_document
    from reviewer.utils import count_tokens

    rows = []
    for p in manifest["papers"]:
        slug = p["slug"]
        pdf = HERE / "papers" / p["group"] / f"{slug}.pdf"
        if not pdf.exists():
            rows.append({"slug": slug, "group": p["group"],
                         "title": p["title"], "pages": None, "eff_tokens": None})
            continue
        try:
            import fitz
            doc = fitz.open(pdf)
            pages = len(doc)
            doc.close()
        except Exception:
            pages = None

        try:
            _title, content, _ocr = parse_document(pdf, max_pages=max_pages)
            eff_tokens = min(count_tokens(content), max_tokens)
        except Exception:
            eff_tokens = None

        rows.append({"slug": slug, "group": p["group"],
                     "title": p["title"], "pages": pages, "eff_tokens": eff_tokens})
    return rows


# ---------------------------------------------------------------------------
# Comment counting helpers
# ---------------------------------------------------------------------------

def count_comments(result: dict, method_prefix: str) -> dict[str, int]:
    """Count comments per model for a given method prefix.

    Returns {model_short: total_count}.
    """
    counts: dict[str, int] = {}
    methods = result.get("methods", {})
    for key, data in methods.items():
        if not key.startswith(method_prefix + "__"):
            continue
        model = key[len(method_prefix) + 2:]
        counts[model] = len(data.get("comments", []))
    return counts


def get_cost(result: dict) -> dict[str, float]:
    """Return {model_short: cost_usd} for consolidated methods."""
    costs: dict[str, float] = {}
    methods = result.get("methods", {})
    for key, data in methods.items():
        if not key.startswith("progressive__"):
            continue
        model = key[len("progressive__"):]
        costs[model] = data.get("cost_usd", 0.0)
    return costs


# ---------------------------------------------------------------------------
# Table builders
# ---------------------------------------------------------------------------

def build_overall_table(manifest: dict, results: dict[str, dict]) -> list[dict]:
    """Overall: accepted vs rejected."""
    groups: dict[str, dict] = {
        "accepted": {"n": 0, "raw": 0, "consolidated": 0},
        "rejected": {"n": 0, "raw": 0, "consolidated": 0},
    }
    for slug, res in results.items():
        group = paper_group(slug, manifest)
        raw_counts = count_comments(res, "progressive_original")
        cons_counts = count_comments(res, "progressive")
        for model in raw_counts:
            groups[group]["n"] += 1
            groups[group]["raw"] += raw_counts[model]
            groups[group]["consolidated"] += cons_counts.get(model, 0)

    rows = []
    for g in ["accepted", "rejected"]:
        d = groups[g]
        n = d["n"]
        if n == 0:
            continue
        raw_avg = d["raw"] / n
        cons_avg = d["consolidated"] / n
        shrink = 1 - cons_avg / raw_avg if raw_avg > 0 else 0
        rows.append({"group": g, "n": n,
                     "raw_total": d["raw"], "raw_avg": raw_avg,
                     "cons_total": d["consolidated"], "cons_avg": cons_avg,
                     "shrink": shrink})
    return rows


def build_per_model_table(manifest: dict, results: dict[str, dict]) -> list[dict]:
    """Per-model breakdown."""
    # {(group, model): {n, raw, consolidated}}
    cells: dict[tuple[str, str], dict] = defaultdict(
        lambda: {"n": 0, "raw": 0, "consolidated": 0}
    )
    for slug, res in results.items():
        group = paper_group(slug, manifest)
        raw_counts = count_comments(res, "progressive_original")
        cons_counts = count_comments(res, "progressive")
        for model in raw_counts:
            cells[(group, model)]["n"] += 1
            cells[(group, model)]["raw"] += raw_counts[model]
            cells[(group, model)]["consolidated"] += cons_counts.get(model, 0)

    rows = []
    for group in ["accepted", "rejected"]:
        for model in MODEL_ORDER:
            d = cells.get((group, model))
            if not d or d["n"] == 0:
                continue
            raw_avg = d["raw"] / d["n"]
            cons_avg = d["consolidated"] / d["n"]
            shrink = 1 - cons_avg / raw_avg if raw_avg > 0 else 0
            rows.append({"group": group, "model": model, "n": d["n"],
                         "raw_total": d["raw"], "raw_avg": raw_avg,
                         "cons_total": d["consolidated"], "cons_avg": cons_avg,
                         "shrink": shrink})
    return rows



def build_consolidation_table(manifest: dict, results: dict[str, dict]) -> list[dict]:
    """Consolidation shrink per model, split by group."""
    # {(group, model): {raw, consolidated}}
    cells: dict[tuple[str, str], dict] = defaultdict(
        lambda: {"raw": 0, "consolidated": 0}
    )
    for slug, res in results.items():
        group = paper_group(slug, manifest)
        raw_counts = count_comments(res, "progressive_original")
        cons_counts = count_comments(res, "progressive")
        for model in raw_counts:
            cells[(group, model)]["raw"] += raw_counts[model]
            cells[(group, model)]["consolidated"] += cons_counts.get(model, 0)

    rows = []
    for model in MODEL_ORDER:
        acc = cells.get(("accepted", model), {"raw": 0, "consolidated": 0})
        rej = cells.get(("rejected", model), {"raw": 0, "consolidated": 0})
        acc_shrink = 1 - acc["consolidated"] / acc["raw"] if acc["raw"] > 0 else 0
        rej_shrink = 1 - rej["consolidated"] / rej["raw"] if rej["raw"] > 0 else 0
        rows.append({"model": model, "acc_shrink": acc_shrink, "rej_shrink": rej_shrink})
    return rows


def build_cost_table(manifest: dict, results: dict[str, dict]) -> list[dict]:
    """Cost per model, split by group."""
    # {(group, model): cost}
    cells: dict[tuple[str, str], float] = defaultdict(float)
    for slug, res in results.items():
        group = paper_group(slug, manifest)
        costs = get_cost(res)
        for model, cost in costs.items():
            cells[(group, model)] += cost

    rows = []
    for model in MODEL_ORDER:
        acc = cells.get(("accepted", model), 0.0)
        rej = cells.get(("rejected", model), 0.0)
        rows.append({"model": model, "accepted": acc, "rejected": rej,
                     "total": acc + rej})
    return rows


def build_runtime_table(run_log: list[dict], manifest: dict) -> list[dict]:
    """Runtime per model from run_log.jsonl."""
    manifest_slugs = {p["slug"] for p in manifest["papers"]}
    # {model_short: [durations]}
    durations: dict[str, list[float]] = defaultdict(list)
    for entry in run_log:
        if not entry.get("ok") or entry["slug"] not in manifest_slugs:
            continue
        model = model_short(entry["model"])
        durations[model].append(entry["duration_sec"])

    rows = []
    for model in MODEL_ORDER:
        durs = durations.get(model, [])
        if not durs:
            continue
        avg_min = (sum(durs) / len(durs)) / 60
        min_min = min(durs) / 60
        max_min = max(durs) / 60
        rows.append({"model": model, "avg_min": avg_min,
                     "min_min": min_min, "max_min": max_min})
    return rows


# ---------------------------------------------------------------------------
# Markdown formatting
# ---------------------------------------------------------------------------

def fmt_papers(rows: list[dict]) -> str:
    lines = []
    lines.append("| Slug | Group | Title | Pages | Eff. tokens |")
    lines.append("| --- | --- | --- | --- | --- |")
    for r in rows:
        pages = str(r["pages"]) if r["pages"] is not None else "N/A"
        tokens = f"{r['eff_tokens']:,}" if r["eff_tokens"] is not None else "N/A"
        lines.append(f"| {r['slug']} | {r['group']} | {r['title']} | {pages} | {tokens} |")
    return "\n".join(lines)


def fmt_overall(rows: list[dict]) -> str:
    lines = []
    lines.append("| Group | N runs | Raw (total) | Raw (avg) | Consolidated (total) | Consolidated (avg) | Shrink |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for r in rows:
        lines.append(f"| **{r['group'].title()}** | {r['n']} | {r['raw_total']} | {r['raw_avg']:.1f} "
                     f"| {r['cons_total']} | {r['cons_avg']:.1f} | {r['shrink']:.0%} |")
    return "\n".join(lines)


def fmt_per_model(rows: list[dict]) -> str:
    lines = []
    lines.append("| Group | Model | N | Raw (total) | Raw (avg) | Cons. (total) | Cons. (avg) | Shrink |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for r in rows:
        lines.append(f"| {r['group']} | {r['model']} | {r['n']} | {r['raw_total']} | {r['raw_avg']:.1f} "
                     f"| {r['cons_total']} | {r['cons_avg']:.1f} | {r['shrink']:.0%} |")
    return "\n".join(lines)



def fmt_consolidation(rows: list[dict]) -> str:
    lines = []
    lines.append("| Model | Accepted shrink | Rejected shrink |")
    lines.append("| --- | --- | --- |")
    for r in rows:
        # Use short display name
        name = r["model"].split("-")[0].title()
        lines.append(f"| {name} | {r['acc_shrink']:.0%} | {r['rej_shrink']:.0%} |")
    return "\n".join(lines)


def fmt_cost(rows: list[dict]) -> str:
    lines = []
    lines.append("| Model | Accepted | Rejected | Total |")
    lines.append("| --- | --- | --- | --- |")
    grand_acc = grand_rej = grand_total = 0.0
    for r in rows:
        name = r["model"].split("-")[0].title()
        lines.append(f"| {name} | ${r['accepted']:.2f} | ${r['rejected']:.2f} "
                     f"| ${r['total']:.2f} |")
        grand_acc += r["accepted"]
        grand_rej += r["rejected"]
        grand_total += r["total"]
    lines.append(f"| **Total** | **${grand_acc:.2f}** | **${grand_rej:.2f}** "
                 f"| **${grand_total:.2f}** |")
    return "\n".join(lines)


def fmt_runtime(rows: list[dict]) -> str:
    lines = []
    lines.append("| Model | Avg per run | Range |")
    lines.append("| --- | --- | --- |")
    for r in rows:
        name = r["model"].split("-")[0].title()
        lines.append(f"| {name} | {r['avg_min']:.1f} min "
                     f"| {r['min_min']:.1f}-{r['max_min']:.1f} min |")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", help="YAML config file (same schema as run_study.py).")
    ap.add_argument("--results-dir", help="Explicit results directory.")
    ap.add_argument("--papers", action="store_true",
                    help="Include papers table (parses PDFs, slow).")
    args = ap.parse_args()

    cfg = load_config(args.config)
    name = cfg.get("name")
    max_pages = cfg.get("max_pages", 20)
    max_tokens = cfg.get("max_tokens", 20_000)

    if args.results_dir:
        results_dir = Path(args.results_dir)
    elif name:
        results_dir = HERE / "results" / name
    else:
        results_dir = HERE / "results"

    if not results_dir.exists():
        sys.exit(f"results directory not found: {results_dir}")

    manifest = json.loads((HERE / "manifest.json").read_text())
    results = load_results(results_dir, manifest)
    run_log = load_run_log(results_dir)

    if not results:
        sys.exit("No result files found.")

    print(f"Loaded {len(results)} result files from {results_dir}\n")

    # --- Papers table ---
    pdfs_available = any((HERE / "papers" / p["group"] / f"{p['slug']}.pdf").exists()
                         for p in manifest["papers"])
    if args.papers and pdfs_available:
        try:
            print("### Papers\n")
            papers_rows = compute_papers_table(manifest, max_pages, max_tokens)
            print(fmt_papers(papers_rows))
            # Summary stats
            acc_pages = [r["pages"] for r in papers_rows if r["group"] == "accepted" and r["pages"]]
            rej_pages = [r["pages"] for r in papers_rows if r["group"] == "rejected" and r["pages"]]
            acc_tok = [r["eff_tokens"] for r in papers_rows if r["group"] == "accepted" and r["eff_tokens"]]
            rej_tok = [r["eff_tokens"] for r in papers_rows if r["group"] == "rejected" and r["eff_tokens"]]
            if acc_pages and rej_pages:
                print(f"\nAccepted avg: {sum(acc_pages)/len(acc_pages):.1f} pages, "
                      f"~{sum(acc_tok)/len(acc_tok):,.0f} tokens")
                print(f"Rejected avg: {sum(rej_pages)/len(rej_pages):.1f} pages, "
                      f"~{sum(rej_tok)/len(rej_tok):,.0f} tokens")
        except Exception as e:
            print(f"(Papers table skipped — {e})\n", file=sys.stderr)
    elif args.papers:
        print("(Papers table skipped — PDFs not on disk. Run download_papers.py first.)\n")

    # --- Overall ---
    print("\n### Overall: accepted vs rejected\n")
    overall = build_overall_table(manifest, results)
    print(fmt_overall(overall))

    # --- Per-model ---
    print("\n### Per-model breakdown\n")
    per_model = build_per_model_table(manifest, results)
    print(fmt_per_model(per_model))

    # --- Consolidation effect ---
    print("\n### Consolidation effect\n")
    consolidation = build_consolidation_table(manifest, results)
    print(fmt_consolidation(consolidation))

    # --- Cost ---
    print("\n### Cost\n")
    cost = build_cost_table(manifest, results)
    print(fmt_cost(cost))

    # --- Runtime ---
    if run_log:
        print("\n### Runtime\n")
        runtime = build_runtime_table(run_log, manifest)
        print(fmt_runtime(runtime))
    else:
        print("\n(Runtime table skipped — no run_log.jsonl found.)")


if __name__ == "__main__":
    main()
