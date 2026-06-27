"""3-way paragraph overlap on the perturbation benchmark, under OpenAIReview
(progressive): Claude Opus 4.7 vs GPT-5.5 vs the UNION of the efficient models.

Mirrors analysis_gpt_claude.py (same perturbation tree and per-cell granularity:
one cell per domain x paper x error_type), but adds a third set that pools all
efficient backbones. Output: plots/venn_claude_gpt_efficient.{png,pdf}.
"""

from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

from utils import (
    COLOR_BLUE, COLOR_RED, COLOR_GREEN,
    load, para_set, regions_3, draw_venn3, save_fig,
)

PERTURB_ROOT = Path(__file__).resolve().parent.parent / "perturbation" / "results"

CLAUDE = "claude-opus-4.7"
GPT    = "gpt-5.5"
# Efficient backbones with full progressive coverage on the perturbation tree
# (glm-4.7-flash is excluded: only ~13 cells available).
EFFICIENT = ["deepseek-v4-flash", "gemini-3.1-flash-lite-preview", "grok-4.1-fast", "qwen3.6-35b-a3b"]
MODELS = [CLAUDE, GPT] + EFFICIENT


def method_key(model):
    return f"progressive__{model}"


def perturb_cells(models, root=PERTURB_ROOT):
    """Return {cell_id: {model: set(paragraph_index)}} from the perturbation tree.

    cell_id = "<domain>__<paper>__<error_type>"; only the progressive method is read.
    """
    cells = defaultdict(dict)
    for domain_dir in sorted(root.glob("*")):
        if not domain_dir.is_dir() or domain_dir.name.startswith("_"):
            continue
        for model in models:
            mdir = domain_dir / model
            if not mdir.is_dir():
                continue
            for etype_dir in sorted(p for p in mdir.glob("*") if p.is_dir()):
                prog = etype_dir / "progressive"
                if not prog.is_dir():
                    continue
                for paper_dir in sorted(prog.glob("paper_*")):
                    review_jsons = sorted((paper_dir / "review").glob("*.json"))
                    if not review_jsons:
                        continue
                    d = load(review_jsons[0])
                    cell_id = f"{domain_dir.name}__{paper_dir.name}__{etype_dir.name}"
                    cells[cell_id][model] = para_set(d, method_key(model))
    return cells


def overlap_three():
    cells = perturb_cells(MODELS)
    # Match the Claude-vs-GPT figure: cells where both frontier models are present.
    paired = sorted(cid for cid, m in cells.items() if CLAUDE in m and GPT in m)
    print(f"Cells with both {CLAUDE} and {GPT}: {len(paired)}")

    totals = defaultdict(float)
    jaccard_sum, jaccard_n = 0.0, 0
    eff_models_seen = set()

    for cid in paired:
        m = cells[cid]
        a = m[CLAUDE]
        b = m[GPT]
        c = set()
        for em in EFFICIENT:
            if em in m:
                c |= m[em]
                eff_models_seen.add(em)
        r = regions_3(a, b, c)
        for k in ("only_a", "only_b", "only_c", "a_b", "a_c", "b_c", "all"):
            totals[k] += r[k]
        if r["total"]:
            jaccard_sum += r["jaccard"]
            jaccard_n   += 1

    n = len(paired)
    avg = {k: v / n for k, v in totals.items()}
    jaccard_avg = jaccard_sum / jaccard_n if jaccard_n else 0.0

    print(f"Efficient models pooled: {sorted(eff_models_seen)}")
    print(f"\n{'Region':<26} {'Avg/cell':>10}")
    print("-" * 38)
    print(f"{'Only Claude':<26} {avg['only_a']:>10.2f}")
    print(f"{'Only GPT':<26} {avg['only_b']:>10.2f}")
    print(f"{'Only Efficient':<26} {avg['only_c']:>10.2f}")
    print(f"{'Claude & GPT':<26} {avg['a_b']:>10.2f}")
    print(f"{'Claude & Efficient':<26} {avg['a_c']:>10.2f}")
    print(f"{'GPT & Efficient':<26} {avg['b_c']:>10.2f}")
    print(f"{'All three':<26} {avg['all']:>10.2f}")
    print(f"{'Jaccard (3-way)':<26} {jaccard_avg:>10.3f}")

    plot(avg, jaccard_avg)


def plot(avg, jaccard_avg):
    sizes = tuple(round(avg[k], 2) for k in ("only_a", "only_b", "a_b", "only_c", "a_c", "b_c", "all"))
    names = ("Opus 4.7", "GPT-5.5", "Efficient models\n(union)")

    fig, ax = plt.subplots(figsize=(8, 7), dpi=400)
    draw_venn3(ax, sizes, names, colors=(COLOR_BLUE, COLOR_RED, COLOR_GREEN),
               region_fontsize=26, set_fontsize=30)
    plt.tight_layout()
    paths = save_fig("venn_claude_gpt_efficient", dpi=400)
    print(f"\nWrote {', '.join(str(p) for p in paths)}")


if __name__ == "__main__":
    overlap_three()
