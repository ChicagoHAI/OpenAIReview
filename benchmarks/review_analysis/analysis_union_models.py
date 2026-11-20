"""Three-system paragraph overlap on the quality-proxy (conference) papers, where each
system's paragraph set is the UNION over all of its backbone models.

This is the aggregate-over-models counterpart to analysis_three_systems.py (which pins
one best model per system). coarse unions over all coarse__<model> runs, OpenAIReview
unions over all progressive__<model> runs, and Reviewer3 has no model selector so it is
used as-is. Output: plots/venn_union_models.{png,pdf}.
"""

from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

from utils import (
    COLOR_BLUE, COLOR_RED, COLOR_GREEN,
    load, stems, regions_3, draw_venn3, save_fig,
)


# Each system: (results folder, method-key prefix to union over).
# Prefix "progressive__" excludes the "progressive_original__" (pre-consolidation) keys.
SYSTEMS = {
    "coarse":       ("../conference_study/results/coarse_v2",               "coarse__"),
    "OpenAIReview": ("../conference_study/results/scaleup_v2_progressive",  "progressive__"),
    "Reviewer 3":   ("../conference_study/results/reviewer3_v2",            "reviewer3__"),
}


def para_set_union(d: dict, prefix: str) -> set:
    """Union of paragraph_index over every method whose key starts with `prefix`."""
    union = set()
    for key, m in d.get("methods", {}).items():
        if not key.startswith(prefix):
            continue
        union |= {c["paragraph_index"] for c in m.get("comments", [])
                  if c.get("paragraph_index") is not None}
    return union


def overlap_union(systems):
    names   = list(systems.keys())
    folders = {n: Path(systems[n][0]) for n in names}
    prefix  = {n: systems[n][1]       for n in names}

    papers = sorted(set.intersection(*(stems(folders[n]) for n in names)))
    print(f"Papers in all 3 systems: {len(papers)}")

    totals = defaultdict(int)
    jaccard_sum, jaccard_n = 0.0, 0
    a, b, c = names

    for stem in papers:
        sa = para_set_union(load(folders[a] / f"{stem}.json"), prefix[a])
        sb = para_set_union(load(folders[b] / f"{stem}.json"), prefix[b])
        sc = para_set_union(load(folders[c] / f"{stem}.json"), prefix[c])

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

    plot(names, avg, jaccard_avg)


def plot(names, avg, jaccard_avg):
    sizes = tuple(round(avg[k], 2) for k in ("only_a", "only_b", "a_b", "only_c", "a_c", "b_c", "all"))

    fig, ax = plt.subplots(figsize=(8, 7), dpi=400)
    draw_venn3(ax, sizes, tuple(names), colors=(COLOR_BLUE, COLOR_RED, COLOR_GREEN),
               region_fontsize=18, set_fontsize=20)
    plt.tight_layout()
    paths = save_fig("venn_union_models", dpi=400)
    print(f"\nWrote {', '.join(str(p) for p in paths)}")


if __name__ == "__main__":
    overlap_union(SYSTEMS)
