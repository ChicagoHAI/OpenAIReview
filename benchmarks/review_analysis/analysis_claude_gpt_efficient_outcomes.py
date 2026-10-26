"""Quality-proxy counterpart of analysis_claude_gpt_efficient.py.

3-way paragraph overlap on the quality-proxy (conference) papers, under
OpenAIReview (progressive): Claude Opus 4.7 vs GPT-5.5 vs the UNION of the
efficient models. Same efficient-model pool as the main-text figure.

Frontier models are read from frontier_subset_progressive; efficient models
from scaleup_v2_progressive (grok lives in its own scaleup_v2_grok_progressive
folder). Per-paper granularity, restricted to papers with both frontier
models. Output: plots/venn_claude_gpt_efficient_outcomes.{png,pdf}.
"""

from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

from utils import (
    COLOR_BLUE, COLOR_RED, COLOR_GREEN,
    load, para_set, stems, regions_3, draw_venn3, save_fig,
)

RESULTS = Path(__file__).resolve().parent.parent / "conference_study" / "results"

FRONTIER_DIR = RESULTS / "frontier_subset_progressive"
CLAUDE = "claude-opus-4.7"
GPT    = "gpt-5.5"
# Same efficient pool as analysis_claude_gpt_efficient.py (main-text figure).
EFFICIENT = {
    "deepseek-v4-flash":             RESULTS / "scaleup_v2_progressive",
    "gemini-3.1-flash-lite-preview": RESULTS / "scaleup_v2_progressive",
    "grok-4.1-fast":                 RESULTS / "scaleup_v2_grok_progressive",
    "qwen3.6-35b-a3b":               RESULTS / "scaleup_v2_progressive",
}


def method_key(model):
    return f"progressive__{model}"


def overlap_three():
    papers = sorted(stems(FRONTIER_DIR))

    totals = defaultdict(float)
    jaccard_sum, jaccard_n = 0.0, 0
    n_used = 0
    eff_models_seen = set()

    for stem in papers:
        d = load(FRONTIER_DIR / f"{stem}.json")
        a = para_set(d, method_key(CLAUDE))
        b = para_set(d, method_key(GPT))
        if not a or not b:
            continue
        c = set()
        for em, folder in EFFICIENT.items():
            p = folder / f"{stem}.json"
            if not p.exists():
                continue
            s = para_set(load(p), method_key(em))
            if s:
                c |= s
                eff_models_seen.add(em)
        r = regions_3(a, b, c)
        for k in ("only_a", "only_b", "only_c", "a_b", "a_c", "b_c", "all"):
            totals[k] += r[k]
        if r["total"]:
            jaccard_sum += r["jaccard"]
            jaccard_n   += 1
        n_used += 1

    print(f"Papers with both {CLAUDE} and {GPT}: {n_used}")
    avg = {k: v / n_used for k, v in totals.items()}
    jaccard_avg = jaccard_sum / jaccard_n if jaccard_n else 0.0

    print(f"Efficient models pooled: {sorted(eff_models_seen)}")
    print(f"\n{'Region':<26} {'Avg/paper':>10}")
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
    # Smaller fonts than the main-text figure: this one renders at 0.85\columnwidth
    # like the other appendix venns (analysis_three_systems.py), not in a half-width subfigure.
    draw_venn3(ax, sizes, names, colors=(COLOR_BLUE, COLOR_RED, COLOR_GREEN),
               region_fontsize=18, set_fontsize=20)
    plt.tight_layout()
    paths = save_fig("venn_claude_gpt_efficient_outcomes", dpi=400)
    print(f"\nWrote {', '.join(str(p) for p in paths)}")


if __name__ == "__main__":
    overlap_three()
