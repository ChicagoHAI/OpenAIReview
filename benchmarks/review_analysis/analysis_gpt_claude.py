from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
import matplotlib.pyplot as plt
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

from utils import COLOR_BLUE, COLOR_RED, load, para_set, stems, regions_2, draw_venn2, save_fig

model_dict = {
    'claude-opus-4.7': 'Claude Opus 4.7',
    'gpt-5.5':         'GPT-5.5',
}

def method_key(model):
    return f"progressive__{model}"

def get_papers(folder):
    return sorted(stems(folder))


# VOLUME

def volume_dicts(folder, models, total_papers):
    volume = {}

    for p in Path(folder).glob("*.json"):
        slug = p.stem
        d = load(p)
        if slug not in volume:
            volume[slug] = {}
        for model in models:
            key = method_key(model)
            comments = d.get("methods", {}).get(key, {}).get("comments", [])
            volume[slug][model] = len(comments)

    average_volume = defaultdict(int)
    for slug, counts in volume.items():
        for model, n in counts.items():
            average_volume[model] += n / total_papers

    print(f"Average number of comments per paper:\n")
    print(f"{'Model':<30} {'Progressive':>12}")
    print("-" * 45)
    for model, avg in average_volume.items():
        print(f"{model:<30} {avg:>12.2f}")

    return volume, average_volume


# OVERLAP

def overlap(folder, models, total_papers):
    papers = get_papers(folder)

    overlap_ind   = defaultdict(lambda: defaultdict(dict))
    overlap_total = {"both_total": 0, "only_c_total": 0, "only_p_total": 0}
    overlap_avg   = defaultdict(lambda: {"both_avg": 0, "only_c_avg": 0, "only_p_avg": 0, "jaccard_sim_avg": 0})

    temp_jaccard_sim = defaultdict(int)
    temp_count       = defaultdict(int)

    claude, gpt = models[0], models[1]

    for stem in papers:
        d = load(Path(folder) / (stem + ".json"))

        claude_paras = para_set(d, method_key(claude))
        gpt_paras    = para_set(d, method_key(gpt))

        r = regions_2(claude_paras, gpt_paras)
        both_num, only_c_num, only_p_num, total_num = r["both"], r["only_a"], r["only_b"], r["total"]

        overlap_ind[stem]["both_idx"]   = claude_paras & gpt_paras
        overlap_ind[stem]["only_c_idx"] = claude_paras - gpt_paras
        overlap_ind[stem]["only_p_idx"] = gpt_paras - claude_paras
        overlap_ind[stem]["both_num"]   = both_num
        overlap_ind[stem]["only_c_num"] = only_c_num
        overlap_ind[stem]["only_p_num"] = only_p_num
        overlap_ind[stem]["jaccard_sim"] = r["jaccard"] if total_num else None

        overlap_total["both_total"]   += both_num
        overlap_total["only_c_total"] += only_c_num
        overlap_total["only_p_total"] += only_p_num

        temp_jaccard_sim["all"] += r["jaccard"]
        temp_count["all"]       += 1 if total_num else 0

    overlap_avg["both_avg"]        = overlap_total["both_total"]   / total_papers
    overlap_avg["only_c_avg"]      = overlap_total["only_c_total"] / total_papers
    overlap_avg["only_p_avg"]      = overlap_total["only_p_total"] / total_papers
    overlap_avg["jaccard_sim_avg"] = temp_jaccard_sim["all"] / temp_count["all"] if temp_count["all"] else 0

    print(f"\nAverage overlap per paper:\n")
    print(f"{'Both':>8} {'Only Claude':>12} {'Only GPT':>10} {'Jaccard':>8}")
    print("-" * 45)
    print(f"{overlap_avg['both_avg']:>8.2f} {overlap_avg['only_c_avg']:>12.2f} {overlap_avg['only_p_avg']:>10.2f} {overlap_avg['jaccard_sim_avg']:>8.3f}")

    plot_overlap(overlap_avg, models)

    return overlap_ind, overlap_total, overlap_avg


def plot_overlap(overlap_avg, models):
    sizes = (round(overlap_avg["only_c_avg"], 2),
             round(overlap_avg["only_p_avg"], 2),
             round(overlap_avg["both_avg"],   2))

    fig, ax = plt.subplots(1, 1, figsize=(7, 6), dpi=400)
    draw_venn2(
        ax, sizes,
        set_labels=(model_dict.get(models[0], models[0]), model_dict.get(models[1], models[1])),
        colors=(COLOR_BLUE, COLOR_RED),
        region_fontsize=22, set_fontsize=20,
    )
    plt.tight_layout()
    save_fig("venn_gpt_claude", dpi=400)


# CLUSTERING

def cluster(folder, models):
    texts      = []
    labels     = []

    papers = get_papers(folder)

    for stem in papers:
        d = load(Path(folder) / (stem + ".json"))
        for model in models:
            for c in d.get("methods", {}).get(method_key(model), {}).get("comments", []):
                texts.append(c.get("title", "") + " " + c.get("explanation", ""))
                labels.append(model_dict.get(model, model))

    print(f"\nTotal comments: {len(texts)}")
    for model in models:
        label = model_dict.get(model, model)
        print(f"  {label}: {labels.count(label)}")

    model_emb  = SentenceTransformer("all-MiniLM-L6-v2")
    X          = model_emb.encode(texts, show_progress_bar=True)

    N_CLUSTERS = 10
    km         = KMeans(n_clusters=N_CLUSTERS, random_state=42)
    cluster_ids = km.fit_predict(X)

    tfidf    = TfidfVectorizer(max_features=10000, stop_words="english")
    X_tfidf  = tfidf.fit_transform(texts)
    terms    = tfidf.get_feature_names_out()

    for cluster_id in range(N_CLUSTERS):
        indices       = np.where(cluster_ids == cluster_id)[0]
        method_counts = Counter(labels[i] for i in indices)
        total         = len(indices)

        centroid  = km.cluster_centers_[cluster_id]
        distances = np.linalg.norm(X[indices] - centroid, axis=1)
        closest   = indices[np.argsort(distances)[:5]]

        cluster_tfidf = np.asarray(X_tfidf[indices].mean(axis=0)).flatten()
        top_keywords  = [terms[j] for j in cluster_tfidf.argsort()[-15:][::-1]]

        print(f"\nCluster {cluster_id} ({total} comments)")
        for model in models:
            label = model_dict.get(model, model)
            print(f"  {label}: {method_counts[label]} ({method_counts[label]/total*100:.0f}%)")
        print(f"  Keywords: {', '.join(top_keywords)}")
        print(f"  Most representative comments:")
        for i in closest:
            print(f"    [{labels[i]:20s}] {texts[i][:100]}")


# PERTURBATION SOURCE
#
# On the perturbation benchmark the OpenAIReview (progressive) reviews live in a tree
#   perturbation/results/<domain>/<model>/<error_type>/progressive/paper_xxx/review/*.json
# rather than a flat folder of per-paper JSONs. Each leaf JSON carries
# methods["progressive__<model>"]. We treat each (domain, paper, error_type) as one cell
# (matching the _fused_for_venn granularity) and average the 2-way Venn over cells in
# which both models are present.

PERTURB_ROOT = Path(__file__).resolve().parent.parent / "perturbation" / "results"


def perturb_cells(models, root=PERTURB_ROOT):
    """Return {cell_id: {model: set(paragraph_index)}} from the perturbation tree.

    cell_id = "<domain>__<paper>__<error_type>". Only the progressive (OpenAIReview)
    method is read. Skips the _fused_for_venn/ helper dir and any non-domain dirs.
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


def overlap_perturb(models, root=PERTURB_ROOT):
    claude, gpt = models[0], models[1]
    cells = perturb_cells(models, root)
    paired = sorted(cid for cid, m in cells.items() if claude in m and gpt in m)
    print(f"Cells with both {claude} and {gpt}: {len(paired)}")

    totals = {"both": 0, "only_c": 0, "only_p": 0}
    jaccard_sum, jaccard_n = 0.0, 0
    vol = {claude: 0, gpt: 0}
    for cid in paired:
        ca, gp = cells[cid][claude], cells[cid][gpt]
        r = regions_2(ca, gp)
        totals["both"]   += r["both"]
        totals["only_c"] += r["only_a"]
        totals["only_p"] += r["only_b"]
        vol[claude] += len(ca)
        vol[gpt]    += len(gp)
        if r["total"]:
            jaccard_sum += r["jaccard"]
            jaccard_n   += 1

    n = len(paired)
    overlap_avg = {
        "both_avg":        totals["both"]   / n if n else 0,
        "only_c_avg":      totals["only_c"] / n if n else 0,
        "only_p_avg":      totals["only_p"] / n if n else 0,
        "jaccard_sim_avg": jaccard_sum / jaccard_n if jaccard_n else 0,
    }

    print(f"\nAverage comments per cell: {claude} {vol[claude]/n:.2f}, {gpt} {vol[gpt]/n:.2f}")
    print(f"\nAverage overlap per cell:\n")
    print(f"{'Both':>8} {'Only Claude':>12} {'Only GPT':>10} {'Jaccard':>8}")
    print("-" * 45)
    print(f"{overlap_avg['both_avg']:>8.2f} {overlap_avg['only_c_avg']:>12.2f} {overlap_avg['only_p_avg']:>10.2f} {overlap_avg['jaccard_sim_avg']:>8.3f}")

    plot_overlap(overlap_avg, models)
    return overlap_avg


if __name__ == "__main__":
    MODELS = ["claude-opus-4.7", "gpt-5.5"]

    print("=" * 90)
    print("OVERLAP (Claude vs. GPT) -- PERTURBATION benchmark")
    print("=" * 90)
    overlap_perturb(MODELS)
