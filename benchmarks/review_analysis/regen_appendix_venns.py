"""Regenerate the appendix per-model Venn grids (venn_cp, venn_all) in the
main-paper style.

The raw result JSONs are not always co-located with this script, so this driver
plots directly from the per-model region averages already reported in the EMNLP
appendix tables (tab:overlap_cp and tab:overlap_all). The styling mirrors the
single-panel main-paper venns (analysis_three_systems.py / analysis_gpt_claude.py):
clean per-panel model-name titles, consistent palette and edge styling, larger
fonts, and no in-figure Jaccard text (Jaccard lives in the table columns).

Run with an env that has matplotlib + matplotlib_venn:
    python regen_appendix_venns.py
Outputs are written straight into the paper's plots/ directory.
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import COLOR_BLUE, COLOR_RED, COLOR_GREEN, draw_venn2, draw_venn3

# Write into the EMNLP paper's plots dir.
PAPER_PLOTS = Path("/data/dangnguyen/openaireview_project/openaireview_emnlp/plots")

MODEL_ORDER = ["DeepSeek-V4-Flash", "Qwen3.6-35B-A3B", "Gemini-3.1-Flash-Lite", "GLM-4.7-Flash"]

# tab:overlap_cp  -> (coarse_only, openaireview_only, both)
CP = {
    "DeepSeek-V4-Flash":     (10.54, 5.34, 2.41),
    "Qwen3.6-35B-A3B":       (8.87,  5.66, 2.88),
    "Gemini-3.1-Flash-Lite": (4.19,  5.15, 1.05),
    "GLM-4.7-Flash":         (2.69,  4.87, 0.38),
}

# tab:overlap_all -> region averages keyed C=coarse, O=openaireview, Z=zero-shot
# columns: C only, O only, Z only, C&O only, C&Z only, O&Z only, C&O&Z
ALL = {
    "DeepSeek-V4-Flash":     dict(c=9.85, o=4.61, z=1.30, co=1.83, cz=0.70, oz=0.73, all=0.58),
    "Qwen3.6-35B-A3B":       dict(c=8.38, o=4.93, z=1.10, co=2.36, cz=0.49, oz=0.73, all=0.52),
    "Gemini-3.1-Flash-Lite": dict(c=4.01, o=4.47, z=1.06, co=0.84, cz=0.18, oz=0.69, all=0.21),
    "GLM-4.7-Flash":         dict(c=2.66, o=4.63, z=0.72, co=0.36, cz=0.03, oz=0.23, all=0.02),
}


def save(base):
    PAPER_PLOTS.mkdir(parents=True, exist_ok=True)
    for fmt in ("png", "pdf"):
        plt.savefig(PAPER_PLOTS / f"{base}.{fmt}", dpi=400, bbox_inches="tight")
    print("wrote", base)


def plot_cp():
    fig, axes = plt.subplots(2, 2, figsize=(12, 10), dpi=400)
    axes = axes.flatten()
    for ax, model in zip(axes, MODEL_ORDER):
        draw_venn2(ax, CP[model], set_labels=("coarse", "OpenAIReview"),
                   colors=(COLOR_BLUE, COLOR_RED),
                   region_fontsize=24, set_fontsize=21)
        ax.set_title(model, fontsize=21, pad=12)
    plt.tight_layout()
    plt.subplots_adjust(hspace=0.16, wspace=0.06)
    save("venn_cp")
    plt.close(fig)


def plot_all():
    fig, axes = plt.subplots(2, 2, figsize=(12, 11), dpi=400)
    axes = axes.flatten()
    for ax, model in zip(axes, MODEL_ORDER):
        r = ALL[model]
        # draw_venn3 order: (Abc, aBc, ABc, abC, AbC, aBC, ABC)
        sizes = (r["c"], r["o"], r["co"], r["z"], r["cz"], r["oz"], r["all"])
        draw_venn3(ax, sizes, set_labels=("coarse", "OpenAIReview", "zero-shot"),
                   colors=(COLOR_BLUE, COLOR_RED, COLOR_GREEN),
                   region_fontsize=17, set_fontsize=18)
        ax.set_title(model, fontsize=21, pad=12)
    plt.tight_layout()
    plt.subplots_adjust(hspace=0.16, wspace=0.06)
    save("venn_all")
    plt.close(fig)


if __name__ == "__main__":
    plot_cp()
    plot_all()
