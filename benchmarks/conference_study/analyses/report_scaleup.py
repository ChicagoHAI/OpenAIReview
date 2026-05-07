#!/usr/bin/env python
"""Pair-grouped report for the 4-pair signal-matrix scale-up.

Reads:
    manifests/combined.json      paper list + pair_memberships + word_count
    results/<name>/<slug>.json   methods dict with <method>__<model> keys

Emits one markdown table per pair showing high-tail vs low-tail comment
counts per (method, model), plus per-1K-words normalized counts. A "Δ"
column shows low − high (predicted sign positive — rejected/low-quality
papers should attract more comments than awarded/high-quality ones).

Usage:
    python report_scaleup.py                            # scan results/ for dirs
    python report_scaleup.py --dir scaleup_zero_shot    # one result dir
    python report_scaleup.py --dir scaleup_zero_shot scaleup_progressive
"""
from __future__ import annotations

import argparse
import fitz
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "manifests" / "combined.json"
RESULTS_BASE = HERE / "results"
BASELINE_MANIFEST = HERE / "manifest.json"

MODEL_ORDER = [
    "deepseek-v4-flash",
    "gemini-3.1-flash-lite-preview",
    "glm-4.7-flash",
    "qwen3.6-35b-a3b",
]
METHOD_ORDER = ["zero_shot", "progressive_raw", "progressive_consolidated", "coarse"]

# Models to drop from the report (set via --exclude-model). Compared as the
# short tail of `<method>__<model>`, so pass e.g. "gemini-3-flash-preview".
EXCLUDED_MODELS: set[str] = set()


def method_key_split(key: str) -> tuple[str, str] | None:
    """Split `<method>__<model>` into (method, model).

    Renames `progressive` → `progressive_consolidated` and
    `progressive_original` → `progressive_raw` so both pre- and
    post-consolidation runs appear as separate methods in the report.
    """
    if "__" not in key:
        return None
    method, model = key.split("__", 1)
    if model in EXCLUDED_MODELS:
        return None
    if method == "progressive":
        method = "progressive_consolidated"
    elif method == "progressive_original":
        method = "progressive_raw"
    elif method.endswith("_original"):
        # Other future `<method>_original` variants are still ignored —
        # only progressive has a meaningful pre/post split today.
        return None
    return method, model


def scan_result_dirs(explicit: list[str] | None) -> list[Path]:
    if explicit:
        return [RESULTS_BASE / d for d in explicit]
    return sorted(p for p in RESULTS_BASE.iterdir()
                  if p.is_dir() and any(p.glob("*.json")))


def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text())


def load_results(dirs: list[Path], slugs: set[str]) -> dict[tuple[Path, str], dict]:
    """Return {(result_dir, slug): result_json} for every paper we can find."""
    out: dict[tuple[Path, str], dict] = {}
    for d in dirs:
        for slug in slugs:
            path = d / f"{slug}.json"
            if path.exists():
                try:
                    out[(d, slug)] = json.loads(path.read_text())
                except json.JSONDecodeError:
                    print(f"  warning: unreadable {path}", file=sys.stderr)
    return out


def comments_by_exact_method(result: dict, method_name: str) -> dict[str, int]:
    """{model: count} for one exact method name, including *_original methods."""
    out = {}
    for key, data in result.get("methods", {}).items():
        if "__" not in key:
            continue
        method, model = key.split("__", 1)
        if method != method_name:
            continue
        out[model] = len(data.get("comments", []))
    return out


def normalize_for_match(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def estimate_paragraph_pages(result: dict, pdf_path: Path) -> list[int]:
    """Heuristically map saved paragraph indices back to 0-based PDF pages.

    The saved result JSON only stores paragraph indices, not page numbers. We
    recover an approximate page map by matching each saved paragraph's text
    against PyMuPDF page text and enforcing monotonicity.
    """
    paragraphs = result.get("paragraphs") or []
    if not paragraphs or not pdf_path.exists():
        return []

    doc = fitz.open(pdf_path)
    page_texts = [normalize_for_match(page.get_text("text")) for page in doc]
    matches: list[int | None] = []
    last_page = 0

    for para in paragraphs:
        text = para.get("text", "") if isinstance(para, dict) else ""
        norm = normalize_for_match(text)
        found = None
        if norm:
            snippets = []
            for n in (160, 120, 80, 50):
                if len(norm) >= n:
                    snippets.append(norm[:n])
            if not snippets and len(norm) >= 20:
                snippets.append(norm)
            for page_idx in range(last_page, len(page_texts)):
                page_text = page_texts[page_idx]
                if any(s in page_text for s in snippets):
                    found = page_idx
                    last_page = page_idx
                    break
        matches.append(found)

    # Fill gaps while preserving nondecreasing order.
    next_known = None
    for i in range(len(matches) - 1, -1, -1):
        if matches[i] is not None:
            next_known = matches[i]
        elif next_known is not None:
            matches[i] = next_known

    prev = 0
    out = []
    for m in matches:
        if m is None:
            m = prev
        if m < prev:
            m = prev
        prev = m
        out.append(m)
    return out


def comments_within_page_limit(method_data: dict, paragraph_pages: list[int], max_page: int) -> int:
    comments = method_data.get("comments", [])
    if not paragraph_pages:
        return 0
    count = 0
    for c in comments:
        idx = c.get("paragraph_index")
        if idx is None or idx < 0 or idx >= len(paragraph_pages):
            continue
        if paragraph_pages[idx] < max_page:
            count += 1
    return count


def comment_metrics_by_method(
    result: dict,
    paragraph_pages: list[int] | None = None,
) -> dict[tuple[str, str], tuple[int, int]]:
    """{(method, model): (count, first10_count)} for one result JSON.

    If paragraph_pages is None, every comment counts toward first10 — valid
    for runs where the reviewer was already capped to the first N pages
    (max_pages config), since no comment can fall outside that window.
    """
    out = {}
    for key, data in result.get("methods", {}).items():
        parsed = method_key_split(key)
        if not parsed:
            continue
        total = len(data.get("comments", []))
        if paragraph_pages is None:
            first10 = total
        else:
            first10 = comments_within_page_limit(data, paragraph_pages, max_page=10)
        out[parsed] = (total, first10)
    return out


# Coarse uses {minor, major, critical}; openaireview methods use
# {minor, moderate, major}. Normalize so a single set of tiers compares
# apples-to-apples (highest=major, mid=moderate, low=minor).
_COARSE_SEVERITY_MAP = {"critical": "major", "major": "moderate", "minor": "minor"}
SEVERITY_TIERS = ("major", "moderate", "minor")


def normalize_severity(method: str, raw: str | None) -> str | None:
    if not raw:
        return None
    raw = raw.lower()
    if method == "coarse":
        return _COARSE_SEVERITY_MAP.get(raw)
    return raw if raw in SEVERITY_TIERS else None


def severity_counts_by_method(
    result: dict,
) -> dict[tuple[str, str], dict[str, int]]:
    """{(method, model): {tier: count}} for one result JSON."""
    out: dict[tuple[str, str], dict[str, int]] = {}
    for key, data in result.get("methods", {}).items():
        parsed = method_key_split(key)
        if not parsed:
            continue
        method, _model = parsed
        counts = {t: 0 for t in SEVERITY_TIERS}
        for c in data.get("comments", []):
            tier = normalize_severity(method, c.get("severity"))
            if tier:
                counts[tier] += 1
        out[parsed] = counts
    return out


def word_count_from_paragraphs(result: dict) -> int | None:
    paragraphs = result.get("paragraphs", [])
    if not paragraphs:
        return None
    text = "\n\n".join(
        p.get("text", "") for p in paragraphs
        if isinstance(p, dict) and p.get("text")
    )
    words = text.split()
    return len(words) if words else None


def comments_by_method(result: dict) -> dict[tuple[str, str], int]:
    """{(method, model): count} for one result JSON."""
    out = {}
    for key, data in result.get("methods", {}).items():
        parsed = method_key_split(key)
        if not parsed:
            continue
        out[parsed] = len(data.get("comments", []))
    return out


def model_order(models: set[str]) -> list[str]:
    head = [m for m in MODEL_ORDER if m in models]
    return head + sorted(m for m in models if m not in MODEL_ORDER)


def method_order(methods: set[str]) -> list[str]:
    head = [m for m in METHOD_ORDER if m in methods]
    return head + sorted(m for m in methods if m not in METHOD_ORDER)


def fmt(x, width=6, dec=2):
    if x is None:
        return " " * (width - 1) + "-"
    return f"{x:{width}.{dec}f}"


def fmt_pct(x):
    if x is None:
        return "     -"
    return f"{x:6.1f}%"


def expected_tail_counts(manifest: dict) -> dict[tuple[int, str], int]:
    counts: dict[tuple[int, str], int] = defaultdict(int)
    for paper in manifest["papers"]:
        for mem in paper["pair_memberships"]:
            counts[(mem["pair"], mem["tail"])] += 1
    return counts


def successful_slugs_by_method_model(
    results: dict[tuple[Path, str], dict],
) -> dict[tuple[str, str], set[str]]:
    out: dict[tuple[str, str], set[str]] = defaultdict(set)
    for (_dir, slug), result in results.items():
        for method_model in comments_by_method(result):
            out[method_model].add(slug)
    return out


def build_pair_summaries(
    cells: dict[int, dict],
    pairs_meta: dict[int, dict],
    tail_counts: dict[tuple[int, str], int],
) -> list[dict]:
    out = []
    for pid, pair_cells in cells.items():
        meta = pairs_meta[pid]
        high_tail = meta["high"]
        low_tail = meta["low"]
        method_models = {(method, model) for (method, model, _tail) in pair_cells}
        for method, model in method_models:
            hi_rows = pair_cells.get((method, model, high_tail), [])
            lo_rows = pair_cells.get((method, model, low_tail), [])
            if not hi_rows or not lo_rows:
                continue
            hi_mean = mean(r[0] for r in hi_rows)
            lo_mean = mean(r[0] for r in lo_rows)
            hi_first10_mean = mean(r[2] for r in hi_rows)
            lo_first10_mean = mean(r[2] for r in lo_rows)
            sev_deltas = {}
            sev_totals = {}
            for tier in SEVERITY_TIERS:
                hi_sev = mean(r[3].get(tier, 0) for r in hi_rows)
                lo_sev = mean(r[3].get(tier, 0) for r in lo_rows)
                sev_deltas[f"d_{tier}"] = lo_sev - hi_sev
                # Pair-level total comments at this tier, split by tail:
                hi_tot = sum(r[3].get(tier, 0) for r in hi_rows)
                lo_tot = sum(r[3].get(tier, 0) for r in lo_rows)
                sev_totals[f"hi_{tier}"] = hi_tot
                sev_totals[f"lo_{tier}"] = lo_tot
                sev_totals[f"tot_{tier}"] = hi_tot + lo_tot
            hi_per_1k = [r[0] / r[1] * 1000 for r in hi_rows if r[1] and r[1] > 0]
            lo_per_1k = [r[0] / r[1] * 1000 for r in lo_rows if r[1] and r[1] > 0]
            hi_per_1k_mean = mean(hi_per_1k) if hi_per_1k else None
            lo_per_1k_mean = mean(lo_per_1k) if lo_per_1k else None
            pct_raw = ((lo_mean - hi_mean) / hi_mean * 100) if hi_mean else None
            pct_first10 = ((lo_first10_mean - hi_first10_mean) / hi_first10_mean * 100) if hi_first10_mean else None
            pct_per_1k = (
                (lo_per_1k_mean - hi_per_1k_mean) / hi_per_1k_mean * 100
                if lo_per_1k_mean is not None and hi_per_1k_mean is not None and hi_per_1k_mean
                else None
            )
            out.append({
                "pair": pid,
                "pair_label": meta["label"],
                "method": method,
                "model": model,
                "high_tail": high_tail,
                "low_tail": low_tail,
                "high_n": len(hi_rows),
                "low_n": len(lo_rows),
                "high_expected": tail_counts[(pid, high_tail)],
                "low_expected": tail_counts[(pid, low_tail)],
                "high_mean": hi_mean,
                "low_mean": lo_mean,
                "high_first10_mean": hi_first10_mean,
                "low_first10_mean": lo_first10_mean,
                "high_first10_counts": [r[2] for r in hi_rows],
                "low_first10_counts": [r[2] for r in lo_rows],
                "d_raw": lo_mean - hi_mean,
                "d_first10": lo_first10_mean - hi_first10_mean,
                "d_per_1k": (lo_per_1k_mean - hi_per_1k_mean
                             if lo_per_1k_mean is not None and hi_per_1k_mean is not None
                             else None),
                "pct_raw": pct_raw,
                "pct_first10": pct_first10,
                "pct_per_1k": pct_per_1k,
                **sev_deltas,
                **sev_totals,
            })
    return out


def format_metric_cell(value, positive_is_good: bool = True, is_pct: bool = False, incomplete: bool = False) -> str:
    if value is None:
        base = "-"
    elif is_pct:
        base = fmt_pct(value).strip()
    else:
        base = fmt(value).strip()
    if value is None:
        marker = "?"
    else:
        marker = "✓" if ((value > 0) == positive_is_good) else "✗"
    suffix = "*" if incomplete and value is not None else ""
    return f"{base} {marker}{suffix}"


def render_definition_metric_table(
    title: str,
    metric_key: str,
    pair_summaries: list[dict],
    is_pct: bool = False,
) -> str:
    pair_order = [1, 2, 3, 4]
    pair_labels = {row["pair"]: row["pair_label"] for row in pair_summaries}
    rows = {}
    raw_vals: dict[tuple[str, str], dict[int, float]] = {}
    for row in pair_summaries:
        key = (row["method"], row["model"])
        rows.setdefault(key, {})
        raw_vals.setdefault(key, {})
        complete = row["high_n"] == row["high_expected"] and row["low_n"] == row["low_expected"]
        rows[key][row["pair"]] = format_metric_cell(
            row.get(metric_key),
            positive_is_good=True,
            is_pct=is_pct,
            incomplete=not complete,
        )
        v = row.get(metric_key)
        if v is not None:
            raw_vals[key][row["pair"]] = v

    lines = [f"### {title}", ""]
    header = "| method | model | " + " | ".join(pair_labels.get(pid, str(pid)) for pid in pair_order) + " |"
    sep = "|---|---|" + "---|" * len(pair_order)
    lines.append(header)
    lines.append(sep)
    for method in method_order({k[0] for k in rows}):
        models = model_order({k[1] for k in rows if k[0] == method})
        for model in models:
            vals = rows.get((method, model), {})
            cell_vals = [vals.get(pid, "-") for pid in pair_order]
            lines.append("| " + " | ".join([method, model] + cell_vals) + " |")
    lines.append("")
    return "\n".join(lines)


def render_count_method_summary_table(
    title: str,
    metric_key: str,
    pair_summaries: list[dict],
) -> str:
    """Compact method × pair table for absolute-count metrics (no ✓/✗ markers
    since these aren't signed deltas)."""
    pair_order = [1, 2, 3, 4]
    pair_labels = {row["pair"]: row["pair_label"] for row in pair_summaries}
    by_method_pair: dict[tuple[str, int], list[float]] = {}
    for row in pair_summaries:
        v = row.get(metric_key)
        if v is None:
            continue
        by_method_pair.setdefault((row["method"], row["pair"]), []).append(v)

    methods = method_order({m for m, _ in by_method_pair})
    lines = [f"#### {title}", ""]
    header = "| method | " + " | ".join(pair_labels.get(pid, str(pid)) for pid in pair_order) + " |"
    lines.append(header)
    lines.append("|---|" + "---|" * len(pair_order))
    for method in methods:
        cells = []
        for pid in pair_order:
            vs = by_method_pair.get((method, pid), [])
            cells.append(fmt(mean(vs)).strip() if vs else "-")
        lines.append("| " + " | ".join([method] + cells) + " |")
    lines.append("")
    return "\n".join(lines)


def render_count_per_model_table(
    title: str,
    metric_key: str,
    pair_summaries: list[dict],
) -> str:
    """Per-model × pair table for absolute counts."""
    pair_order = [1, 2, 3, 4]
    pair_labels = {row["pair"]: row["pair_label"] for row in pair_summaries}
    by_key: dict[tuple[str, str], dict[int, float]] = {}
    for row in pair_summaries:
        v = row.get(metric_key)
        if v is None:
            continue
        by_key.setdefault((row["method"], row["model"]), {})[row["pair"]] = v

    lines = [f"### {title}", ""]
    header = "| method | model | " + " | ".join(pair_labels.get(pid, str(pid)) for pid in pair_order) + " |"
    lines.append(header)
    lines.append("|---|---|" + "---|" * len(pair_order))
    for method in method_order({k[0] for k in by_key}):
        for model in model_order({k[1] for k in by_key if k[0] == method}):
            vals = by_key.get((method, model), {})
            cells = [fmt(vals[pid]).strip() if pid in vals else "-" for pid in pair_order]
            lines.append("| " + " | ".join([method, model] + cells) + " |")
    lines.append("")
    return "\n".join(lines)


def render_per_model_aggregate_comments(pair_summaries: list[dict]) -> str:
    """Per-model averages across all (method, definition) cells. Lets you
    compare which model is best at picking up the quality signal.

    Sign hits are counted per-paper: for each (paper, definition) wing
    membership a paper is a hit if its first10 comment count lies on the
    expected side of the within-pair midpoint (low-wing > midpoint or
    high-wing < midpoint). Denominator is the total number of wing
    memberships across all (method, definition) cells for that model.
    """
    by_model: dict[str, list[dict]] = {}
    for row in pair_summaries:
        by_model.setdefault(row["model"], []).append(row)
    lines = ["#### Per-model aggregate (across methods and quality definitions)", ""]
    lines.append("| model | mean #comments — high | mean #comments — low | Δ first10 | % first10 | sign hits (per-paper) |")
    lines.append("|---|---|---|---|---|---|")
    for model in model_order(set(by_model)):
        rows = by_model[model]
        hi = mean(r["high_mean"] for r in rows)
        lo = mean(r["low_mean"] for r in rows)
        d_vals = [r["d_first10"] for r in rows if r["d_first10"] is not None]
        pct_vals = [r["pct_first10"] for r in rows if r["pct_first10"] is not None]
        d_mean = mean(d_vals) if d_vals else None
        pct_mean = mean(pct_vals) if pct_vals else None
        # Per-paper sign hits: paper is a hit if its first10 count is on
        # the expected side of its within-pair midpoint.
        hits = 0
        total = 0
        for r in rows:
            if r["high_first10_mean"] is None or r["low_first10_mean"] is None:
                continue
            mid = (r["high_first10_mean"] + r["low_first10_mean"]) / 2.0
            for c in r["low_first10_counts"]:
                total += 1
                if c > mid:
                    hits += 1
            for c in r["high_first10_counts"]:
                total += 1
                if c < mid:
                    hits += 1
        sign_hits_str = f"{hits}/{total}" if total else "-"
        lines.append(
            f"| {model} | {fmt(hi).strip()} | {fmt(lo).strip()} | "
            f"{format_metric_cell(d_mean)} | "
            f"{format_metric_cell(pct_mean, is_pct=True)} | "
            f"{sign_hits_str} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_comment_count_section(pair_summaries: list[dict]) -> str:
    """Absolute mean comment counts per (method, pair, tail)."""
    lines = ["## Mean Comment Counts", ""]
    lines.append(
        "Average number of comments per paper, split by tail (high vs low) "
        "and pair definition. Use these for absolute volume context — the "
        "delta tables above show the signed difference (low − high)."
    )
    lines.append("")
    lines.append("### Method comparison (averaged across models)")
    lines.append("")
    lines.append(render_count_method_summary_table("Mean #comments — high tail", "high_mean", pair_summaries))
    lines.append(render_count_method_summary_table("Mean #comments — low tail", "low_mean", pair_summaries))
    lines.append("### Per-model breakdown")
    lines.append("")
    lines.append(render_per_model_aggregate_comments(pair_summaries))
    lines.append(render_count_per_model_table("Mean #comments — high tail (per model)", "high_mean", pair_summaries))
    lines.append(render_count_per_model_table("Mean #comments — low tail (per model)", "low_mean", pair_summaries))
    return "\n".join(lines)


def render_method_summary_table(
    title: str,
    metric_key: str,
    pair_summaries: list[dict],
    is_pct: bool = False,
) -> str:
    """Compact method × pair table — one row per method, averaged across
    that method's models. Companion to render_definition_metric_table."""
    pair_order = [1, 2, 3, 4]
    pair_labels = {row["pair"]: row["pair_label"] for row in pair_summaries}
    by_method_pair: dict[tuple[str, int], list[float]] = {}
    for row in pair_summaries:
        v = row.get(metric_key)
        if v is None:
            continue
        by_method_pair.setdefault((row["method"], row["pair"]), []).append(v)

    methods = method_order({m for m, _ in by_method_pair})
    lines = [f"#### {title}", ""]
    header = "| method | " + " | ".join(pair_labels.get(pid, str(pid)) for pid in pair_order) + " |"
    sep = "|---|" + "---|" * len(pair_order)
    lines.append(header)
    lines.append(sep)
    for method in methods:
        cells = []
        for pid in pair_order:
            vs = by_method_pair.get((method, pid), [])
            if vs:
                cells.append(format_metric_cell(mean(vs), is_pct=is_pct))
            else:
                cells.append("-")
        lines.append("| " + " | ".join([method] + cells) + " |")
    lines.append("")
    return "\n".join(lines)


def render_severity_distribution_section(pair_summaries: list[dict]) -> str:
    """One table per pair definition; rows = methods (averaged across models),
    columns = severity tier %s of that method's total comments in the pair."""
    pair_labels = {row["pair"]: row["pair_label"] for row in pair_summaries}
    pair_order = sorted(pair_labels)

    # Pair tail labels (high/low names per pair):
    pair_tails: dict[int, dict[str, str]] = {}
    for row in pair_summaries:
        pair_tails.setdefault(row["pair"], {
            "high": row["high_tail"],
            "low": row["low_tail"],
        })

    # Aggregate tier counts per (pair, method, side) across all (model, paper).
    by_key: dict[tuple[int, str, str], dict[str, int]] = {}
    for row in pair_summaries:
        for side in ("high", "low"):
            prefix = "hi" if side == "high" else "lo"
            key = (row["pair"], row["method"], side)
            bucket = by_key.setdefault(key, {t: 0 for t in SEVERITY_TIERS})
            for tier in SEVERITY_TIERS:
                bucket[tier] += row.get(f"{prefix}_{tier}", 0)

    lines = ["## Severity Distribution by Method", ""]
    lines.append(
        "Share of each method's comments at each severity tier, split by "
        "tail (high vs low quality), per quality definition. Cells are "
        "percentages summing to ~100% per row."
    )
    lines.append("")

    # Aggregate across all pair definitions.
    agg: dict[tuple[str, str], dict[str, int]] = {}
    for (_pid, method, side), counts in by_key.items():
        bucket = agg.setdefault((method, side), {t: 0 for t in SEVERITY_TIERS})
        for tier in SEVERITY_TIERS:
            bucket[tier] += counts.get(tier, 0)
    lines.append("### Aggregate (all quality definitions)")
    lines.append("")
    lines.append("| method | tail | major | moderate | minor | total comments |")
    lines.append("|---|---|---|---|---|---|")
    for method in method_order({m for (m, _s) in agg}):
        for side in ("high", "low"):
            counts = agg.get((method, side), {t: 0 for t in SEVERITY_TIERS})
            total = sum(counts.values())
            if total == 0:
                cells = ["-", "-", "-", "0"]
            else:
                cells = [
                    f"{counts[tier] / total * 100:.1f}%"
                    for tier in SEVERITY_TIERS
                ] + [str(total)]
            lines.append("| " + " | ".join([method, side] + cells) + " |")
    lines.append("")

    for pid in pair_order:
        labels = pair_tails.get(pid, {"high": "high", "low": "low"})
        lines.append(f"### Pair {pid} — {pair_labels[pid]} "
                     f"({labels['high']} vs {labels['low']})")
        lines.append("")
        lines.append("| method | tail | major | moderate | minor | total comments |")
        lines.append("|---|---|---|---|---|---|")
        methods_present = method_order({m for (p, m, _s) in by_key if p == pid})
        for method in methods_present:
            for side in ("high", "low"):
                counts = by_key.get((pid, method, side), {t: 0 for t in SEVERITY_TIERS})
                total = sum(counts.values())
                tail_label = side
                if total == 0:
                    cells = ["-", "-", "-", "0"]
                else:
                    cells = [
                        f"{counts[tier] / total * 100:.1f}%"
                        for tier in SEVERITY_TIERS
                    ] + [str(total)]
                lines.append("| " + " | ".join([method, tail_label] + cells) + " |")
        lines.append("")
    return "\n".join(lines)


def render_severity_tables(pair_summaries: list[dict]) -> str:
    lines = ["## Severity Breakdown", ""]
    lines.append(
        "Δ low − high mean comment count, stratified by severity tier. "
        "Coarse's {minor, major, critical} is normalized to "
        "{minor, moderate, major} (highest=major). Positive = low-quality "
        "papers attract more issues at that severity."
    )
    lines.append("")
    lines.append("### Method comparison (averaged across models)")
    lines.append("")
    lines.append(render_method_summary_table("Δ Major — by method", "d_major", pair_summaries))
    lines.append(render_method_summary_table("Δ Moderate — by method", "d_moderate", pair_summaries))
    lines.append(render_method_summary_table("Δ Minor — by method", "d_minor", pair_summaries))
    lines.append("### Per-model breakdown")
    lines.append("")
    lines.append(render_per_model_aggregate_severity(pair_summaries))
    lines.append(render_definition_metric_table("Δ Major", "d_major", pair_summaries))
    lines.append(render_definition_metric_table("Δ Moderate", "d_moderate", pair_summaries))
    lines.append(render_definition_metric_table("Δ Minor", "d_minor", pair_summaries))
    return "\n".join(lines)


def render_per_model_aggregate_severity(pair_summaries: list[dict]) -> str:
    """Per-model severity Δs averaged across all (method, definition) cells."""
    by_model: dict[str, list[dict]] = {}
    for row in pair_summaries:
        by_model.setdefault(row["model"], []).append(row)
    lines = ["#### Per-model aggregate (across methods and quality definitions)", ""]
    lines.append("| model | Δ major | Δ moderate | Δ minor |")
    lines.append("|---|---|---|---|")
    for model in model_order(set(by_model)):
        rows = by_model[model]
        cells = []
        for tier in SEVERITY_TIERS:
            vals = [r.get(f"d_{tier}") for r in rows if r.get(f"d_{tier}") is not None]
            cells.append(format_metric_cell(mean(vals)) if vals else "-")
        lines.append("| " + " | ".join([model] + cells) + " |")
    lines.append("")
    return "\n".join(lines)


def render_definition_comparison_tables(pair_summaries: list[dict]) -> str:
    lines = ["## Cross-Definition Comparison", ""]
    lines.append(
        "Columns are the four signal definitions (`community`, `conference`, "
        "`reviewer`, `composed`). Rows are method/model cells. `*` marks an "
        "incomplete pair cell."
    )
    lines.append("")
    lines.append("### Method comparison (averaged across models)")
    lines.append("")
    lines.append(render_method_summary_table("Delta First 10 Pages — by method", "d_first10", pair_summaries))
    lines.append(render_method_summary_table("Percent Increase First 10 Pages — by method", "pct_first10", pair_summaries, is_pct=True))
    lines.append("### Per-model breakdown")
    lines.append("")
    lines.append(render_definition_metric_table("Delta First 10 Pages", "d_first10", pair_summaries))
    lines.append(render_definition_metric_table("Percent Increase First 10 Pages", "pct_first10", pair_summaries, is_pct=True))
    return "\n".join(lines)


def render_historical_baseline() -> str:
    """Render the prior ICLR'24 accepted-vs-rejected baseline as context."""
    if not BASELINE_MANIFEST.exists():
        return ""

    manifest = json.loads(BASELINE_MANIFEST.read_text())
    papers = manifest.get("papers", [])
    if not papers:
        return ""

    group_by_slug = {paper["slug"]: paper["group"] for paper in papers}
    slugs = set(group_by_slug)
    result_specs = [
        ("baseline progressive raw", RESULTS_BASE / "baseline", "progressive_original"),
        ("baseline progressive consolidated", RESULTS_BASE / "baseline", "progressive"),
        ("coarse", RESULTS_BASE / "coarse", "coarse"),
    ]

    overall: dict[tuple[str, str], list[int]] = defaultdict(list)
    overall_per_1k: dict[tuple[str, str], list[float]] = defaultdict(list)
    per_model: dict[tuple[str, str, str], list[int]] = defaultdict(list)
    per_model_per_1k: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    available_specs = []
    word_counts_by_slug: dict[str, int] = {}

    for label, result_dir, method_name in result_specs:
        if not result_dir.exists():
            continue
        available_specs.append((label, result_dir, method_name))
        results = load_results([result_dir], slugs)
        for (_dir, slug), result in results.items():
            if slug not in word_counts_by_slug:
                wc = word_count_from_paragraphs(result)
                if wc:
                    word_counts_by_slug[slug] = wc
            group = group_by_slug[slug]
            word_count = word_counts_by_slug.get(slug)
            for model, count in comments_by_exact_method(result, method_name).items():
                overall[(label, group)].append(count)
                per_model[(label, model, group)].append(count)
                if word_count and word_count > 0:
                    per_1k = count / word_count * 1000
                    overall_per_1k[(label, group)].append(per_1k)
                    per_model_per_1k[(label, model, group)].append(per_1k)

    if not available_specs:
        return ""

    lines = ["## Historical Baseline", ""]
    lines.append(
        "Older ICLR 2024 accepted-vs-rejected probe, included as context only. "
        "This is a different cohort from the scale-up matrix. Deltas here are "
        "reported as rejected minus accepted; per-1k normalization uses one "
        "paper-level word count per slug, computed from the saved paragraph extraction."
    )
    lines.append("")
    lines.append(
        "| system | accepted_mean | rejected_mean | delta_rej_minus_acc | "
        "accepted_per_1k | rejected_per_1k | delta_per_1k | successful runs |"
    )
    lines.append("|---|---|---|---|---|---|---|---|")
    for label, _result_dir, _method_name in available_specs:
        acc = overall[(label, "accepted")]
        rej = overall[(label, "rejected")]
        if not acc or not rej:
            continue
        acc_per_1k = overall_per_1k[(label, "accepted")]
        rej_per_1k = overall_per_1k[(label, "rejected")]
        acc_mean = mean(acc)
        rej_mean = mean(rej)
        delta = rej_mean - acc_mean
        acc_per_1k_mean = mean(acc_per_1k) if acc_per_1k else None
        rej_per_1k_mean = mean(rej_per_1k) if rej_per_1k else None
        delta_per_1k = (
            rej_per_1k_mean - acc_per_1k_mean
            if rej_per_1k_mean is not None and acc_per_1k_mean is not None
            else None
        )
        lines.append(
            f"| {label} | {fmt(acc_mean)} (n={len(acc)}) | {fmt(rej_mean)} (n={len(rej)}) | "
            f"{fmt(delta)} {'✓' if delta > 0 else '✗'} | "
            f"{fmt(acc_per_1k_mean)} | {fmt(rej_per_1k_mean)} | "
            f"{fmt(delta_per_1k)} "
            f"{'✓' if delta_per_1k is not None and delta_per_1k > 0 else ('?' if delta_per_1k is None else '✗')} | "
            f"{len(acc) + len(rej)} |"
        )

    lines.append("")
    lines.append("| system | model | delta_rej_minus_acc | delta_per_1k | n_acc/n_rej |")
    lines.append("|---|---|---|---|---|")
    system_order = [label for label, _, _ in available_specs]
    for label in system_order:
        models = {
            model for (system, model, _group) in per_model
            if system == label
        }
        for model in model_order(models):
            acc = per_model[(label, model, "accepted")]
            rej = per_model[(label, model, "rejected")]
            if not acc or not rej:
                continue
            delta = mean(rej) - mean(acc)
            acc_per_1k = per_model_per_1k[(label, model, "accepted")]
            rej_per_1k = per_model_per_1k[(label, model, "rejected")]
            delta_per_1k = (
                mean(rej_per_1k) - mean(acc_per_1k)
                if acc_per_1k and rej_per_1k else None
            )
            lines.append(
                f"| {label} | {model} | {fmt(delta)} {'✓' if delta > 0 else '✗'} | "
                f"{fmt(delta_per_1k)} "
                f"{'✓' if delta_per_1k is not None and delta_per_1k > 0 else ('?' if delta_per_1k is None else '✗')} | "
                f"n={len(acc)}/{len(rej)} |"
            )

    lines.append("")
    return "\n".join(lines)


def render_selection_rules() -> str:
    lines = ["## Selection Rules", ""]
    lines.append(
        "Tail labels below are the **implemented** selection rules from "
        "`select_papers.py`, not just the short names."
    )
    lines.append("")
    lines.append("Cohort: ICLR + NeurIPS, years 2021-2022.")
    lines.append("")
    lines.append("- Pair 1 `cited`: highest citations-per-year across the cohort (deterministic top-n).")
    lines.append("- Pair 1 `nopub`: rejected papers with substantive reviews and no formal publication venue (empty / arXiv-like). **Random sample** within the pool — avoids systematic overlap with Pair 3's bottom-score tail.")
    lines.append("- Pair 2 `award`: papers whose decision text matches award-like labels (`Outstanding`, `Best`, `Oral`, `Spotlight`). **Random sample** — avoids overlap with Pair 1's top-cited and Pair 3's top-score tails.")
    lines.append("- Pair 2 `rej`: rejected papers with substantive reviews. **Random sample** — avoids overlap with Pair 1's nopub and Pair 3's bot5.")
    lines.append("- Pair 3 `top5`: papers with substantive reviews, ranked by highest `review_score_avg` (deterministic).")
    lines.append("- Pair 3 `bot5`: papers with substantive reviews, ranked by lowest `review_score_avg` (deterministic).")
    lines.append("- Pair 4 `comp-hi`: awarded papers with reviews, ranked by **sum of citation-rank + score-rank** within the awarded pool (best on both axes simultaneously).")
    lines.append("- Pair 4 `comp-lo`: rejected, never-published papers with substantive reviews, ranked by lowest `review_score_avg`.")
    lines.append("")
    return "\n".join(lines)


def render_summary(
    manifest: dict,
    pairs_meta: dict[int, dict],
    pair_summaries: list[dict],
    success_slugs: dict[tuple[str, str], set[str]],
) -> str:
    manifest_slugs = {paper["slug"] for paper in manifest["papers"]}
    models_by_method: dict[str, set[str]] = defaultdict(set)
    for method, model in success_slugs:
        models_by_method[method].add(model)
    methods = method_order(set(models_by_method))

    lines = ["## Summary", ""]
    lines.append("| method | successful runs | complete pair cells | raw sign matches | first10 sign matches |")
    lines.append("|---|---|---|---|---|")
    for method in methods:
        models = model_order(models_by_method[method])
        total_runs = len(manifest_slugs) * len(models)
        successful_runs = sum(len(success_slugs[(method, model)]) for model in models)
        complete = [
            row for row in pair_summaries
            if row["method"] == method
            and row["high_n"] == row["high_expected"]
            and row["low_n"] == row["low_expected"]
        ]
        raw_ok = sum(1 for row in complete if row["d_raw"] > 0)
        first10_ok = sum(1 for row in complete if row["d_first10"] is not None and row["d_first10"] > 0)
        complete_total = len(pairs_meta) * len(models)
        lines.append(
            f"| {method} | {successful_runs}/{total_runs} | "
            f"{len(complete)}/{complete_total} | {raw_ok}/{len(complete)} | {first10_ok}/{len(complete)} |"
        )

    # Note: a per-(method,model) "Incomplete Runs" section was removed —
    # the missing-paper count per cell is already visible in the Summary
    # table's "successful runs" column, and the slug list bloated the report.

    return "\n".join(lines)


def render_pair_table(
    pair_id: int,
    pair_label: str,
    high_tail: str,
    low_tail: str,
    cells: dict,  # (method, model, tail) -> [(count, word_count), ...]
) -> str:
    """One markdown table for a pair in the original report style."""
    methods = method_order({k[0] for k in cells})
    models = model_order({k[1] for k in cells})

    lines = [f"### Pair {pair_id} — {pair_label} ({high_tail} vs {low_tail})", ""]
    detail_lines = [
        "| method | model | tail | n | comments_mean | first10_mean |",
        "|---|---|---|---|---|---|",
    ]

    for method in methods:
        for model in models:
            stats_per_tail = {}
            for tail in (high_tail, low_tail):
                rows = cells.get((method, model, tail), [])
                if not rows:
                    continue
                n = len(rows)
                c_mean = mean(r[0] for r in rows)
                first10_mean = mean(r[2] for r in rows)
                stats_per_tail[tail] = (n, c_mean, first10_mean)
                detail_lines.append(
                    f"| {method} | {model} | {tail} | {n} | "
                    f"{fmt(c_mean)} | {fmt(first10_mean)} |"
                )
            if len(stats_per_tail) == 2:
                hi = stats_per_tail[high_tail]
                lo = stats_per_tail[low_tail]
                d_raw = lo[1] - hi[1]
                d_first10 = lo[2] - hi[2]
                # Predicted sign: low − high > 0 (more comments on low-quality).
                ok_raw = "✓" if d_raw > 0 else "✗"
                ok_first10 = "✓" if d_first10 > 0 else "✗"
                detail_lines.append(
                    f"| {method} | {model} | **Δ (low−high)** | — | "
                    f"{fmt(d_raw)} {ok_raw} | {fmt(d_first10)} {ok_first10} |"
                )
    lines.extend(detail_lines)
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", nargs="+", help="Result directory name(s) under results/. "
                                              "Default: every dir with JSONs.")
    ap.add_argument("--manifest", type=Path, default=MANIFEST)
    ap.add_argument("--out", type=Path, help="Write markdown to this file.")
    ap.add_argument("--exclude-model", action="append", default=[],
                    help="Drop this model from the report (repeatable). "
                         "Match the short name in `<method>__<model>` keys, "
                         "e.g. gemini-3-flash-preview.")
    args = ap.parse_args()
    EXCLUDED_MODELS.update(args.exclude_model)

    manifest = json.loads(args.manifest.read_text())
    papers_by_slug = {p["slug"]: p for p in manifest["papers"]}
    pair_labels = {1: "community", 2: "conference", 3: "reviewer", 4: "composed"}

    dirs = scan_result_dirs(args.dir)
    if not dirs:
        sys.exit("No result directories found.")
    print(f"Scanning: {[d.name for d in dirs]}", file=sys.stderr)

    results = load_results(dirs, set(papers_by_slug))
    tail_counts = expected_tail_counts(manifest)

    # Build (pair_id, method, model, tail) -> list of (count, word_count).
    cells: dict[int, dict] = defaultdict(lambda: defaultdict(list))
    pairs_meta: dict[int, dict] = {}

    # max_pages was already enforced at review time, so every comment is
    # within the first-10-pages window by construction. Pass None to
    # comment_metrics_by_method to skip the (slow) PDF reparsing step.
    for (_dir, slug), result in results.items():
        paper = papers_by_slug[slug]
        word_count = paper.get("word_count")
        metrics = comment_metrics_by_method(result, None)
        severity = severity_counts_by_method(result)
        for (method, model), (count, first10_count) in metrics.items():
            sev = severity.get((method, model), {t: 0 for t in SEVERITY_TIERS})
            for mem in paper["pair_memberships"]:
                pid = mem["pair"]
                tail = mem["tail"]
                side = mem["side"]
                if pid not in pairs_meta:
                    pairs_meta[pid] = {"label": pair_labels.get(pid, "?"),
                                       "high": None, "low": None}
                pairs_meta[pid][side] = tail
                cells[pid][(method, model, tail)].append(
                    (count, word_count, first10_count, sev)
                )

    success_slugs = successful_slugs_by_method_model(results)
    pair_summaries = build_pair_summaries(cells, pairs_meta, tail_counts)

    blocks = []
    blocks.append(f"# Scale-up signal-matrix report\n")
    blocks.append(f"Manifest: `{args.manifest}` · {len(papers_by_slug)} papers · "
                  f"pairs: {sorted(pairs_meta)} · result dirs: "
                  f"{[d.name for d in dirs]}\n")
    blocks.append("Predicted sign: **low − high > 0** — lower-quality papers "
                  "should draw more comments than higher-quality ones if the "
                  "reviewer is tracking real issues (not hallucinating).\n")
    blocks.append(render_summary(manifest, pairs_meta, pair_summaries, success_slugs))
    baseline_block = render_historical_baseline()
    if baseline_block:
        blocks.append(baseline_block)
    blocks.append(render_selection_rules())
    blocks.append(
        "Metric note: `first10_comments` is a heuristic. Result JSONs store "
        "`paragraph_index` but not page number, so the report estimates page "
        "boundaries by matching saved paragraphs back onto PDF page text and then "
        "counts comments whose matched paragraph falls in pages 1-10.\n"
    )
    blocks.append(render_definition_comparison_tables(pair_summaries))
    blocks.append(render_comment_count_section(pair_summaries))
    blocks.append(render_severity_tables(pair_summaries))
    blocks.append(render_severity_distribution_section(pair_summaries))

    for pid in sorted(cells):
        meta = pairs_meta[pid]
        blocks.append(render_pair_table(
            pid, meta["label"], meta["high"], meta["low"], cells[pid]
        ))

    md = "\n".join(blocks)
    if args.out:
        args.out.write_text(md)
        print(f"Wrote {args.out}", file=sys.stderr)
    else:
        print(md)


if __name__ == "__main__":
    main()
