#!/usr/bin/env python3
"""Render a baseline-vs-variants comparison table from a breakdown JSON
produced by breakdown_recall.py."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

BUCKETS_ORDER = ["op_sign", "idx_sub", "numeric", "computation",
                 "claim", "reasoning", "experimental"]
BUCKET_HEADERS = ["Op./sign", "Idx./sub.", "Numeric", "Comput.",
                  "Claim", "Reason.", "Exper."]
SURFACE = ["op_sign", "idx_sub", "numeric", "computation"]
PROSE   = ["claim", "reasoning", "experimental"]


def _fmt_pct(rec: float | None) -> str:
    return "  -- " if rec is None else f"{rec*100:5.1f}%"


def _row(label: str, ov: dict, baseline_ov: dict | None) -> str:
    cells = []
    for b in BUCKETS_ORDER:
        rec = ov[b].get("recall")
        cells.append(_fmt_pct(rec))
    # surface micro-avg
    s_det = sum(ov[b]["detected"] for b in SURFACE)
    s_tot = sum(ov[b]["total"] for b in SURFACE)
    p_det = sum(ov[b]["detected"] for b in PROSE)
    p_tot = sum(ov[b]["total"] for b in PROSE)
    s_avg = (s_det / s_tot) if s_tot else None
    p_avg = (p_det / p_tot) if p_tot else None
    cells.append(_fmt_pct(s_avg))
    cells.append(_fmt_pct(p_avg))
    # deltas
    if baseline_ov:
        b_s_det = sum(baseline_ov[b]["detected"] for b in SURFACE)
        b_s_tot = sum(baseline_ov[b]["total"] for b in SURFACE)
        b_p_det = sum(baseline_ov[b]["detected"] for b in PROSE)
        b_p_tot = sum(baseline_ov[b]["total"] for b in PROSE)
        b_s = (b_s_det / b_s_tot) if b_s_tot else None
        b_p = (b_p_det / b_p_tot) if b_p_tot else None
        def _delta(a, b):
            if a is None or b is None:
                return "  -- "
            v = (a - b) * 100
            return f"{v:+5.1f}"
        cells.append(_delta(s_avg, b_s))
        cells.append(_delta(p_avg, b_p))
    else:
        cells += ["  -- ", "  -- "]
    return "| " + label.ljust(34) + " | " + " | ".join(cells) + " |"


def _table(report: dict) -> str:
    headers = BUCKET_HEADERS + ["Surf.avg", "Prose.avg", "ΔSurf", "ΔProse"]
    sep_cell = lambda h: "-" * max(len(h), 6)
    sep = "|" + "-" * 36 + "|" + "|".join(sep_cell(h) + "--" for h in headers) + "|"
    header_row = "| " + "Variant".ljust(34) + " | " + " | ".join(h.center(6) for h in headers) + " |"
    lines = [header_row, sep]
    baseline_ov = report.get("baseline", {}).get("_overall")
    # baseline row first
    if baseline_ov:
        lines.append(_row("baseline (val papers)", baseline_ov, None))
    for label, payload in report.items():
        if label == "baseline":
            continue
        ov = payload.get("_overall")
        if ov:
            lines.append(_row(label, ov, baseline_ov))
    return "\n".join(lines)


def _per_domain(report: dict) -> str:
    rows = []
    rows.append("\nPer-domain (recall on val papers), surface vs prose:")
    rows.append(f"  {'label':<40} {'domain':<22} {'surf':>8} {'prose':>8}")
    for label, payload in report.items():
        pd = payload.get("per_domain", {})
        for d in sorted(pd):
            dc = pd[d]
            s_det = sum(dc[b]["detected"] for b in SURFACE)
            s_tot = sum(dc[b]["total"] for b in SURFACE)
            p_det = sum(dc[b]["detected"] for b in PROSE)
            p_tot = sum(dc[b]["total"] for b in PROSE)
            s = (s_det / s_tot) if s_tot else None
            p = (p_det / p_tot) if p_tot else None
            rows.append(f"  {label:<40} {d:<22} {_fmt_pct(s):>8} {_fmt_pct(p):>8}")
    return "\n".join(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--breakdown", type=Path, required=True)
    ap.add_argument("--per-domain", action="store_true")
    args = ap.parse_args()
    report = json.loads(args.breakdown.read_text())
    print(_table(report))
    if args.per_domain:
        print(_per_domain(report))


if __name__ == "__main__":
    main()
