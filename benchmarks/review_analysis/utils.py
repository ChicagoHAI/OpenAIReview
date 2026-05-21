"""Shared helpers for benchmarks/review_analysis/analysis_*.py scripts.

Each `analysis_*.py` script has its own comparison target (4-system × model
matrix, 2-way Claude/GPT, 3-system, human-vs-AI-union) but shares the same
plumbing: load a per-paper result JSON, pull the set of paragraph_index for a
method, compute Venn regions, and apply consistent styling.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn2_circles, venn3, venn3_circles


PLOTS_DIR = Path(__file__).resolve().parent / "plots"


def save_fig(base_name: str, *, dpi: int = 300, formats: tuple[str, ...] = ("png", "pdf")) -> list[Path]:
    """Save the current matplotlib figure to plots/{base_name}.{ext} for each format.

    Returns the list of paths written.
    """
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    out = []
    for fmt in formats:
        path = PLOTS_DIR / f"{base_name}.{fmt}"
        plt.savefig(path, dpi=dpi, bbox_inches="tight")
        out.append(path)
    return out


# Palette used across scripts.
COLOR_BLUE  = "#2196F3"
COLOR_RED   = "#E53935"
COLOR_GREEN = "#43A047"


def load(path) -> dict:
    """Read a JSON result file."""
    return json.loads(Path(path).read_text())


def para_set(d: dict, method_key: str) -> set[int]:
    """Set of paragraph_index touched by `method_key`'s comments in result `d`."""
    comments = d.get("methods", {}).get(method_key, {}).get("comments", [])
    return {c["paragraph_index"] for c in comments if c.get("paragraph_index") is not None}


def stems(folder) -> set[str]:
    """Set of paper slugs (.json file stems) in a results folder."""
    return {p.stem for p in Path(folder).glob("*.json")}


def regions_2(a: set, b: set) -> dict:
    """2-way region counts: only_a, only_b, both, total, jaccard."""
    only_a = len(a - b)
    only_b = len(b - a)
    both   = len(a & b)
    total  = only_a + only_b + both
    return {
        "only_a": only_a, "only_b": only_b, "both": both,
        "total": total,
        "jaccard": both / total if total else 0.0,
    }


def regions_3(a: set, b: set, c: set) -> dict:
    """3-way region counts: only_a/b/c, a_b, a_c, b_c, all, total, jaccard."""
    only_a = len(a - b - c)
    only_b = len(b - a - c)
    only_c = len(c - a - b)
    a_b    = len((a & b) - c)
    a_c    = len((a & c) - b)
    b_c    = len((b & c) - a)
    all3   = len(a & b & c)
    total  = only_a + only_b + only_c + a_b + a_c + b_c + all3
    return {
        "only_a": only_a, "only_b": only_b, "only_c": only_c,
        "a_b": a_b, "a_c": a_c, "b_c": b_c, "all": all3,
        "total": total,
        "jaccard": all3 / total if total else 0.0,
    }


def style_venn2(v, circles, colors, *, region_fontsize=30, set_fontsize=18):
    """Apply consistent edge colors and font sizes to a venn2 figure."""
    for circle, color in zip(circles, colors):
        circle.set_edgecolor(color)
        circle.set_linewidth(2.0)
    for label_id in ("10", "01", "11"):
        lbl = v.get_label_by_id(label_id)
        if lbl:
            lbl.set_fontsize(region_fontsize)
            lbl.set_color("black")
            lbl.set_ha("center")
    for sl in v.set_labels:
        if sl:
            sl.set_fontsize(set_fontsize)
            sl.set_color("black")


def style_venn3(v, circles, colors, *, region_fontsize=26, set_fontsize=16):
    """Apply consistent edge colors and font sizes to a venn3 figure."""
    for circle, color in zip(circles, colors):
        circle.set_edgecolor(color)
        circle.set_linewidth(2.0)
    for label_id in ("100", "010", "110", "001", "101", "011", "111"):
        lbl = v.get_label_by_id(label_id)
        if lbl:
            lbl.set_fontsize(region_fontsize)
            lbl.set_color("black")
            lbl.set_ha("center")
    for sl in v.set_labels:
        if sl:
            sl.set_fontsize(set_fontsize)
            sl.set_color("black")


def draw_venn2(ax, sizes, set_labels, colors=(COLOR_BLUE, COLOR_RED), *,
               alpha=0.15, region_fontsize=30, set_fontsize=18):
    """Draw a styled venn2 on `ax`. `sizes` = (only_a, only_b, both)."""
    v = venn2(subsets=sizes, set_labels=set_labels, ax=ax, set_colors=colors, alpha=alpha)
    circles = venn2_circles(subsets=sizes, ax=ax, linewidth=2.0)
    style_venn2(v, circles, colors, region_fontsize=region_fontsize, set_fontsize=set_fontsize)
    return v, circles


def draw_venn3(ax, sizes, set_labels, colors=(COLOR_BLUE, COLOR_RED, COLOR_GREEN), *,
               alpha=0.15, region_fontsize=26, set_fontsize=16):
    """Draw a styled venn3 on `ax`. `sizes` = (Abc, aBc, ABc, abC, AbC, aBC, ABC)."""
    v = venn3(subsets=sizes, set_labels=set_labels, ax=ax, set_colors=colors, alpha=alpha)
    circles = venn3_circles(subsets=sizes, ax=ax, linewidth=2.0)
    style_venn3(v, circles, colors, region_fontsize=region_fontsize, set_fontsize=set_fontsize)
    return v, circles
