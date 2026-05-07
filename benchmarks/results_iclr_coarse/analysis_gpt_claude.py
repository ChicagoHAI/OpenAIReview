import json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn2_circles
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

model_dict = {
    'claude-opus-4.7': 'Claude Opus 4.7',
    'gpt-5.5':         'GPT-5.5',
}

def load(path):
    return json.loads(Path(path).read_text())

def method_key(model):
    return f"progressive__{model}"

def get_papers(folder):
    return [p.stem for p in Path(folder).glob("*.json")]


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

    def para_set(d, mk):
        comments = d.get("methods", {}).get(mk, {}).get("comments", [])
        return {c["paragraph_index"] for c in comments if "paragraph_index" in c}

    claude, gpt = models[0], models[1]

    for stem in papers:
        d = load(Path(folder) / (stem + ".json"))

        claude_paras = para_set(d, method_key(claude))
        gpt_paras    = para_set(d, method_key(gpt))

        both_num    = len(claude_paras & gpt_paras)
        only_c_num  = len(claude_paras - gpt_paras)
        only_p_num  = len(gpt_paras - claude_paras)
        total_num   = both_num + only_c_num + only_p_num

        overlap_ind[stem]["both_idx"]   = claude_paras & gpt_paras
        overlap_ind[stem]["only_c_idx"] = claude_paras - gpt_paras
        overlap_ind[stem]["only_p_idx"] = gpt_paras - claude_paras
        overlap_ind[stem]["both_num"]   = both_num
        overlap_ind[stem]["only_c_num"] = only_c_num
        overlap_ind[stem]["only_p_num"] = only_p_num
        overlap_ind[stem]["jaccard_sim"] = both_num / total_num if total_num else None

        overlap_total["both_total"]   += both_num
        overlap_total["only_c_total"] += only_c_num
        overlap_total["only_p_total"] += only_p_num

        temp_jaccard_sim["all"] += both_num / total_num if total_num else 0
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
    COLORS = ["#2196F3", "#E53935"]  # blue, red

    fig, ax = plt.subplots(1, 1, figsize=(7, 6), dpi=400)

    only_c = round(overlap_avg["only_c_avg"], 2)
    only_p = round(overlap_avg["only_p_avg"], 2)
    both   = round(overlap_avg["both_avg"],   2)

    v = venn2(
        subsets=(only_c, only_p, both),
        set_labels=(model_dict.get(models[0], models[0]), model_dict.get(models[1], models[1])),
        ax=ax,
        set_colors=COLORS,
        alpha=0.15,
    )

    c = venn2_circles(subsets=(only_c, only_p, both), ax=ax, linewidth=2.0)
    for circle, color in zip(c, COLORS):
        circle.set_edgecolor(color)
        circle.set_linewidth(2.0)

    for label_id in ["10", "01", "11"]:
        lbl = v.get_label_by_id(label_id)
        if lbl:
            lbl.set_fontsize(15)
            lbl.set_color("black")
            lbl.set_fontweight("normal")
            lbl.set_ha("center")

    for set_label in v.set_labels:
        if set_label:
            set_label.set_fontsize(15)
            set_label.set_color("black")

    ax.set_title(f"Claude Opus 4.7 vs. GPT-5.5\nJaccard Similarity: {overlap_avg['jaccard_sim_avg']:.3f}",
                 fontsize=15, fontweight="bold", pad=10)

    plt.tight_layout()
    plt.savefig("./venn_gpt_claude.png", dpi=400, bbox_inches="tight")


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


if __name__ == "__main__":
    FOLDER       = "./frontier_subset_progressive/"
    MODELS       = ["claude-opus-4.7", "gpt-5.5"]
    TOTAL_PAPERS = len(list(Path(FOLDER).glob("*.json")))

    print("=" * 90)
    print("VOLUME")
    print("=" * 90)
    volume_dicts(FOLDER, MODELS, TOTAL_PAPERS)

    print("\n" + "=" * 90)
    print("OVERLAP (Claude vs. GPT)")
    print("=" * 90)
    overlap(FOLDER, MODELS, TOTAL_PAPERS)

    print("\n" + "=" * 90)
    print("CLUSTERING")
    print("=" * 90)
    cluster(FOLDER, MODELS)
