from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

from utils import (
    COLOR_BLUE, COLOR_RED, COLOR_GREEN,
    load, para_set, stems, regions_3, draw_venn3, save_fig,
)


# Three systems to compare, each pinned to (results folder, method key in that folder).
SYSTEMS = {
    "coarse / DeepSeek":         ("../conference_study/results/coarse_v2",                 "coarse__deepseek-v4-flash"),
    "OpenAIReview / GPT-5.5":    ("../conference_study/results/frontier_subset_progressive", "progressive__gpt-5.5"),
    "Reviewer 3":                ("../conference_study/results/reviewer3_v2",              "reviewer3__reviewer3"),
}


def overlap_three(systems):
    names = list(systems.keys())
    folders = {n: Path(systems[n][0]) for n in names}
    keys    = {n: systems[n][1]       for n in names}

    # Restrict to papers present in all three folders.
    papers = sorted(set.intersection(*(stems(folders[n]) for n in names)))
    print(f"Papers in all 3 systems: {len(papers)}")

    totals = defaultdict(int)
    jaccard_sum = 0.0
    jaccard_n   = 0

    a, b, c = names

    for stem in papers:
        sa = para_set(load(folders[a] / f"{stem}.json"), keys[a])
        sb = para_set(load(folders[b] / f"{stem}.json"), keys[b])
        sc = para_set(load(folders[c] / f"{stem}.json"), keys[c])

        r = regions_3(sa, sb, sc)
        for k in ("only_a", "only_b", "only_c", "a_b", "a_c", "b_c", "all"):
            totals[k] += r[k]
        if r["total"]:
            jaccard_sum += r["jaccard"]
            jaccard_n   += 1

    n_papers = len(papers)
    avg = {k: v / n_papers for k, v in totals.items()}
    jaccard_avg = jaccard_sum / jaccard_n if jaccard_n else 0.0

    print(f"\n{'Region':<28} {'Avg/paper':>10}")
    print("-" * 40)
    print(f"{'Only ' + a:<28} {avg['only_a']:>10.2f}")
    print(f"{'Only ' + b:<28} {avg['only_b']:>10.2f}")
    print(f"{'Only ' + c:<28} {avg['only_c']:>10.2f}")
    print(f"{a + ' & ' + b:<28} {avg['a_b']:>10.2f}")
    print(f"{a + ' & ' + c:<28} {avg['a_c']:>10.2f}")
    print(f"{b + ' & ' + c:<28} {avg['b_c']:>10.2f}")
    print(f"{'All three':<28} {avg['all']:>10.2f}")
    print(f"{'Jaccard (3-way)':<28} {jaccard_avg:>10.3f}")

    plot(names, avg, jaccard_avg, n_papers)


def plot(names, avg, jaccard_avg, n_papers):
    sizes = tuple(round(avg[k], 2) for k in ("only_a", "only_b", "a_b", "only_c", "a_c", "b_c", "all"))

    fig, ax = plt.subplots(figsize=(8, 7), dpi=400)
    draw_venn3(ax, sizes, tuple(names), colors=(COLOR_BLUE, COLOR_RED, COLOR_GREEN))
    ax.set_title(
        f"Comment overlap by paragraph index ({n_papers} papers)\n"
        f"Jaccard Similarity: {jaccard_avg:.3f}",
        fontsize=14, fontweight="bold", pad=12,
    )
    plt.tight_layout()
    paths = save_fig("venn_three_systems", dpi=400)
    print(f"\nWrote {', '.join(str(p) for p in paths)}")


if __name__ == "__main__":
    overlap_three(SYSTEMS)
