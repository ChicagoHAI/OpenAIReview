"""Multi-method × multi-model comparison on the v2 scaleup cohort.

Compares three OpenAIReview methods — `coarse`, `progressive`, `zero_shot` — across
four shared backbones (DeepSeek-V4-Flash, Gemini-3.1-Flash-Lite, GLM-4.7-Flash,
Qwen3.6-35B-A3B), all run on the same set of papers. Per (method, model) it loads
the per-paper result JSONs from `./coarse_v2/`, `./scaleup_v2_progressive/`, and
`./scaleup_v2_zero_shot/`, then reports:

  * `volume_dicts`     : average #comments per paper per (method, model), plus
                         which method "wins" most often per model.
  * `overlap_cp`       : 2-way paragraph-index overlap of coarse vs progressive,
                         per model, with a 2×2 panel of venn2 plots → venn_cp.{png,pdf}.
  * `overlap_all`      : 3-way overlap across coarse/progressive/zero_shot, per
                         model, with a 2×2 panel of venn3 plots → venn_all.{png,pdf}.
  * `cluster_cp` /
    `cluster_all`      : SentenceTransformer + KMeans (10 clusters) over comment
                         titles+explanations, with TF-IDF top keywords and 5
                         representative comments per cluster.

All shared helpers (`load`, `para_set`, region math, venn styling, `save_fig`)
live in `utils.py`. Plots are written to `./plots/` in both PNG and PDF.

Run: `python analysis.py` from this directory.
"""

from collections import defaultdict, Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.manifold import TSNE

from utils import (
    COLOR_BLUE, COLOR_RED, COLOR_GREEN,
    load, para_set, regions_2, regions_3, draw_venn2, draw_venn3, save_fig,
)


model_dict = {
    'deepseek-v4-flash':              'DeepSeek-V4-Flash',
    'gemini-3.1-flash-lite-preview':  'Gemini-3.1-Flash-Lite',
    'glm-4.7-flash':                  'GLM-4.7-Flash',
    'qwen3.6-35b-a3b':                'Qwen3.6-35B-A3B',
}


def method_key(folder_name, model):
    prefix = {"coarse": "coarse", "progressive": "progressive", "zero_shot": "zero_shot"}
    return f"{prefix[folder_name]}__{model}"


def get_papers(folders):
    first_folder = next(iter(folders.values()))
    if not first_folder:
        return None
    return [p.stem for p in Path(first_folder).glob("*.json")]


# ---------------------------------------------------------------------------
# Volume
# ---------------------------------------------------------------------------

def volume_dicts(folders, models, total_papers):
    volume = {}  # { slug -> { model -> { folder -> n_comments } } }

    for folder_name, folder_path in folders.items():
        for p in Path(folder_path).glob("*.json"):
            slug = p.stem
            d = load(p)
            if slug not in volume:
                volume[slug] = defaultdict(dict)
            for model in models:
                key = method_key(folder_name, model)
                comments = d.get("methods", {}).get(key, {}).get("comments", [])
                volume[slug][model][folder_name] = len(comments)

    highest_volume = defaultdict(dict)
    average_volume = defaultdict(dict)

    for _, models_volume in volume.items():
        for model, counts in models_volume.items():
            highest = max(counts, key=counts.get)
            if highest not in highest_volume[model]:
                highest_volume[model][highest] = 0
            highest_volume[model][highest] += 1

            for method, number in counts.items():
                if method not in average_volume[model]:
                    average_volume[model][method] = 0
                average_volume[model][method] += number / total_papers

    print("Average number of comments per paper:\n")
    print(f"{'Model':<40} {'Coarse':>10} {'Progressive':>12} {'Zero Shot':>11} {'Winner':>12}")
    print("-" * 90)
    for model, counts in average_volume.items():
        coarse = counts.get('coarse', 0)
        prog = counts.get('progressive', 0)
        zero_shot = counts.get('zero_shot', 0)
        winner = max(counts, key=counts.get)
        print(f"{model:<40} {coarse:>10.2f} {prog:>12.2f} {zero_shot:>11.2f} {winner:>12}")

    return volume, highest_volume, average_volume


# ---------------------------------------------------------------------------
# 2-way overlap: coarse vs progressive
# ---------------------------------------------------------------------------

def overlap_cp(folders, models, total_papers):
    overlap_ind = defaultdict(lambda: defaultdict(dict))
    overlap_total = defaultdict(lambda: {"both_total": 0, "only_c_total": 0, "only_p_total": 0})
    overlap_avg = defaultdict(lambda: {"both_avg": 0, "only_c_avg": 0, "only_p_avg": 0, "jaccard_sim_avg": 0})

    papers = get_papers(folders)
    if not papers:
        return None

    temp_jaccard_sim = defaultdict(int)
    temp_count = defaultdict(int)

    for stem in papers:
        coarse_data = load(Path(folders["coarse"]) / (stem + ".json"))
        prog_data   = load(Path(folders["progressive"]) / (stem + ".json"))

        for model in models:
            coarse_paras = para_set(coarse_data, method_key("coarse", model))
            prog_paras   = para_set(prog_data,   method_key("progressive", model))

            r = regions_2(coarse_paras, prog_paras)
            both_idx   = coarse_paras & prog_paras
            only_c_idx = coarse_paras - prog_paras
            only_p_idx = prog_paras   - coarse_paras
            both_num, only_c_num, only_p_num, total_num = r["both"], r["only_a"], r["only_b"], r["total"]

            overlap_ind[model][stem]["both_idx"]    = both_idx
            overlap_ind[model][stem]["only_c_idx"]  = only_c_idx
            overlap_ind[model][stem]["only_p_idx"]  = only_p_idx
            overlap_ind[model][stem]["both_num"]    = both_num
            overlap_ind[model][stem]["only_c_num"]  = only_c_num
            overlap_ind[model][stem]["only_p_num"]  = only_p_num
            overlap_ind[model][stem]["both_pct"]    = both_num   / total_num if total_num != 0 else None
            overlap_ind[model][stem]["only_c_pct"]  = only_c_num / total_num if total_num != 0 else None
            overlap_ind[model][stem]["only_p_pct"]  = only_p_num / total_num if total_num != 0 else None
            overlap_ind[model][stem]["jaccard_sim"] = r["jaccard"] if total_num != 0 else None

            overlap_total[model]["both_total"]   += both_num
            overlap_total[model]["only_c_total"] += only_c_num
            overlap_total[model]["only_p_total"] += only_p_num

            temp_jaccard_sim[model] += r["jaccard"]
            temp_count[model] += 1 if total_num != 0 else 0

    for model in models:
        overlap_avg[model]["both_avg"]        = overlap_total[model]["both_total"]   / total_papers
        overlap_avg[model]["only_c_avg"]      = overlap_total[model]["only_c_total"] / total_papers
        overlap_avg[model]["only_p_avg"]      = overlap_total[model]["only_p_total"] / total_papers
        overlap_avg[model]["jaccard_sim_avg"] = temp_jaccard_sim[model] / temp_count[model] if temp_count[model] else 0

    print("Average overlap per paper:\n")
    print(f"{'Model':<35} {'Both':>8} {'Only C':>8} {'Only P':>8} {'Jaccard':>8}")
    print("-" * 71)
    for model, counts in overlap_avg.items():
        print(f"{model:<35} {counts['both_avg']:>8.2f} {counts['only_c_avg']:>8.2f} "
              f"{counts['only_p_avg']:>8.2f} {counts['jaccard_sim_avg']:>8.3f}")

    plot_overlap_cp(overlap_avg)

    return overlap_ind, overlap_total, overlap_avg


def plot_overlap_cp(overlap_avg):
    # Style matches the single-panel main-paper venns (analysis_three_systems.py):
    # clean per-panel model-name titles, larger fonts, and no in-figure Jaccard
    # text (Jaccard is reported in the table columns instead).
    fig, axes = plt.subplots(2, 2, figsize=(12, 10), dpi=400)
    axes = axes.flatten()

    for i, (model, counts) in enumerate(overlap_avg.items()):
        sizes = (round(counts["only_c_avg"], 2),
                 round(counts["only_p_avg"], 2),
                 round(counts["both_avg"],   2))
        draw_venn2(axes[i], sizes, set_labels=("coarse", "OpenAIReview"),
                   colors=(COLOR_BLUE, COLOR_RED),
                   region_fontsize=24, set_fontsize=21)
        axes[i].set_title(model_dict.get(model, model), fontsize=21, pad=12)

    plt.tight_layout()
    plt.subplots_adjust(hspace=0.16, wspace=0.06)
    save_fig("venn_cp", dpi=400)


# ---------------------------------------------------------------------------
# 3-way overlap: coarse, progressive, zero_shot
# ---------------------------------------------------------------------------

def overlap_all(folders, models, total_papers):
    overlap_ind   = defaultdict(lambda: defaultdict(dict))
    overlap_total = defaultdict(lambda: {
        "all_total": 0, "only_c_total": 0, "only_p_total": 0, "only_z_total": 0,
        "only_c_p_total": 0, "only_c_z_total": 0, "only_p_z_total": 0,
    })
    overlap_avg   = defaultdict(lambda: {
        "all_avg": 0, "only_c_avg": 0, "only_p_avg": 0, "only_z_avg": 0,
        "only_c_p_avg": 0, "only_c_z_avg": 0, "only_p_z_avg": 0, "jaccard_sim_avg": 0,
    })

    papers = get_papers(folders)
    if not papers:
        return None

    temp_jaccard_sim = defaultdict(int)
    temp_count       = defaultdict(int)

    for stem in papers:
        coarse_data = load(Path(folders["coarse"])      / (stem + ".json"))
        prog_data   = load(Path(folders["progressive"]) / (stem + ".json"))
        zero_data   = load(Path(folders["zero_shot"])   / (stem + ".json"))

        for model in models:
            coarse_paras = para_set(coarse_data, method_key("coarse",      model))
            prog_paras   = para_set(prog_data,   method_key("progressive", model))
            zero_paras   = para_set(zero_data,   method_key("zero_shot",   model))

            all_idx      = coarse_paras & prog_paras & zero_paras
            only_c_idx   = coarse_paras - prog_paras - zero_paras
            only_p_idx   = prog_paras   - coarse_paras - zero_paras
            only_z_idx   = zero_paras   - coarse_paras - prog_paras
            only_c_p_idx = (coarse_paras & prog_paras) - zero_paras
            only_c_z_idx = (coarse_paras & zero_paras) - prog_paras
            only_p_z_idx = (prog_paras   & zero_paras) - coarse_paras

            r = regions_3(coarse_paras, prog_paras, zero_paras)
            all_num      = r["all"]
            only_c_num   = r["only_a"]
            only_p_num   = r["only_b"]
            only_z_num   = r["only_c"]
            only_c_p_num = r["a_b"]
            only_c_z_num = r["a_c"]
            only_p_z_num = r["b_c"]
            total_num    = r["total"]

            overlap_ind[model][stem]["all_idx"]      = all_idx
            overlap_ind[model][stem]["only_c_idx"]   = only_c_idx
            overlap_ind[model][stem]["only_p_idx"]   = only_p_idx
            overlap_ind[model][stem]["only_z_idx"]   = only_z_idx
            overlap_ind[model][stem]["only_c_p_idx"] = only_c_p_idx
            overlap_ind[model][stem]["only_c_z_idx"] = only_c_z_idx
            overlap_ind[model][stem]["only_p_z_idx"] = only_p_z_idx
            overlap_ind[model][stem]["all_num"]      = all_num
            overlap_ind[model][stem]["only_c_num"]   = only_c_num
            overlap_ind[model][stem]["only_p_num"]   = only_p_num
            overlap_ind[model][stem]["only_z_num"]   = only_z_num
            overlap_ind[model][stem]["only_c_p_num"] = only_c_p_num
            overlap_ind[model][stem]["only_c_z_num"] = only_c_z_num
            overlap_ind[model][stem]["only_p_z_num"] = only_p_z_num
            overlap_ind[model][stem]["jaccard_sim"]  = r["jaccard"] if total_num != 0 else None

            overlap_total[model]["all_total"]      += all_num
            overlap_total[model]["only_c_total"]   += only_c_num
            overlap_total[model]["only_p_total"]   += only_p_num
            overlap_total[model]["only_z_total"]   += only_z_num
            overlap_total[model]["only_c_p_total"] += only_c_p_num
            overlap_total[model]["only_c_z_total"] += only_c_z_num
            overlap_total[model]["only_p_z_total"] += only_p_z_num

            temp_jaccard_sim[model] += r["jaccard"]
            temp_count[model]       += 1 if total_num != 0 else 0

    for model in models:
        overlap_avg[model]["all_avg"]         = overlap_total[model]["all_total"]      / total_papers
        overlap_avg[model]["only_c_avg"]      = overlap_total[model]["only_c_total"]   / total_papers
        overlap_avg[model]["only_p_avg"]      = overlap_total[model]["only_p_total"]   / total_papers
        overlap_avg[model]["only_z_avg"]      = overlap_total[model]["only_z_total"]   / total_papers
        overlap_avg[model]["only_c_p_avg"]    = overlap_total[model]["only_c_p_total"] / total_papers
        overlap_avg[model]["only_c_z_avg"]    = overlap_total[model]["only_c_z_total"] / total_papers
        overlap_avg[model]["only_p_z_avg"]    = overlap_total[model]["only_p_z_total"] / total_papers
        overlap_avg[model]["jaccard_sim_avg"] = temp_jaccard_sim[model] / temp_count[model] if temp_count[model] else 0

    print("Average 3-way overlap per paper:\n")
    print(f"{'Model':<35} {'All':>6} {'Only C':>8} {'Only P':>8} {'Only Z':>8} "
          f"{'C∩P':>6} {'C∩Z':>6} {'P∩Z':>6} {'Jaccard':>8}")
    print("-" * 100)
    for model, counts in overlap_avg.items():
        print(f"{model:<35} "
              f"{counts['all_avg']:>6.2f} "
              f"{counts['only_c_avg']:>8.2f} "
              f"{counts['only_p_avg']:>8.2f} "
              f"{counts['only_z_avg']:>8.2f} "
              f"{counts['only_c_p_avg']:>6.2f} "
              f"{counts['only_c_z_avg']:>6.2f} "
              f"{counts['only_p_z_avg']:>6.2f} "
              f"{counts['jaccard_sim_avg']:>8.3f}")

    plot_overlap_all(overlap_avg)

    return overlap_ind, overlap_total, overlap_avg


def plot_overlap_all(overlap_avg):
    # Same clean style as plot_overlap_cp: model-name-only titles, no in-figure
    # Jaccard, consistent palette/edges via draw_venn3.
    fig, axes = plt.subplots(2, 2, figsize=(12, 11), dpi=400)
    axes = axes.flatten()

    for i, (model, counts) in enumerate(overlap_avg.items()):
        sizes = (
            round(counts["only_c_avg"],   2),
            round(counts["only_p_avg"],   2),
            round(counts["only_c_p_avg"], 2),
            round(counts["only_z_avg"],   2),
            round(counts["only_c_z_avg"], 2),
            round(counts["only_p_z_avg"], 2),
            round(counts["all_avg"],      2),
        )
        draw_venn3(axes[i], sizes, set_labels=("coarse", "OpenAIReview", "zero-shot"),
                   colors=(COLOR_BLUE, COLOR_RED, COLOR_GREEN),
                   region_fontsize=17, set_fontsize=18)
        axes[i].set_title(model_dict.get(model, model), fontsize=21, pad=12)

    plt.tight_layout()
    plt.subplots_adjust(hspace=0.16, wspace=0.06)
    save_fig("venn_all", dpi=400)


# ---------------------------------------------------------------------------
# Cluster analysis
# ---------------------------------------------------------------------------

def cluster_cp(folders, models):
    texts      = []
    labels     = []  # "coarse" or "progressive"
    models_tag = []

    papers = get_papers(folders)
    if not papers:
        return None

    for model in models:
        for stem in papers:
            coarse_data = load(Path(folders["coarse"])      / (stem + ".json"))
            prog_data   = load(Path(folders["progressive"]) / (stem + ".json"))

            for c in coarse_data.get("methods", {}).get(method_key("coarse", model), {}).get("comments", []):
                texts.append(c.get("title", "") + " " + c.get("explanation", ""))
                labels.append("coarse")
                models_tag.append(model)

            for p in prog_data.get("methods", {}).get(method_key("progressive", model), {}).get("comments", []):
                texts.append(p.get("title", "") + " " + p.get("explanation", ""))
                labels.append("progressive")
                models_tag.append(model)

    print(f"Total comments: {len(texts)}  "
          f"(coarse: {labels.count('coarse')}, progressive: {labels.count('progressive')})")

    model_emb = SentenceTransformer("all-MiniLM-L6-v2")
    X = model_emb.encode(texts, show_progress_bar=True)

    N_CLUSTERS = 10
    km = KMeans(n_clusters=N_CLUSTERS, random_state=42)
    cluster_ids = km.fit_predict(X)

    # TF-IDF for cluster keywords
    tfidf = TfidfVectorizer(max_features=10000, stop_words="english")
    X_tfidf = tfidf.fit_transform(texts)
    terms = tfidf.get_feature_names_out()

    for cluster_id in range(N_CLUSTERS):
        indices = np.where(cluster_ids == cluster_id)[0]
        method_counts = Counter(labels[i] for i in indices)
        total = len(indices)

        # 5 comments closest to the cluster centroid
        centroid = km.cluster_centers_[cluster_id]
        distances = np.linalg.norm(X[indices] - centroid, axis=1)
        closest = indices[np.argsort(distances)[:5]]

        cluster_tfidf = np.asarray(X_tfidf[indices].mean(axis=0)).flatten()
        top_keywords = [terms[j] for j in cluster_tfidf.argsort()[-15:][::-1]]

        print(f"\nCluster {cluster_id} ({total} comments)")
        print(f"  coarse: {method_counts['coarse']} ({method_counts['coarse']/total*100:.0f}%)  "
              f"progressive: {method_counts['progressive']} ({method_counts['progressive']/total*100:.0f}%)")
        print(f"  Keywords: {', '.join(top_keywords)}")
        print(f"  Most representative comments:")
        for i in closest:
            print(f"    [{labels[i]:12s}] {texts[i][:100]}")


def cluster_all(folders, models):
    texts      = []
    labels     = []
    models_tag = []

    papers = get_papers(folders)
    if not papers:
        return None

    for model in models:
        for stem in papers:
            coarse_data = load(Path(folders["coarse"])      / (stem + ".json"))
            prog_data   = load(Path(folders["progressive"]) / (stem + ".json"))
            zero_data   = load(Path(folders["zero_shot"])   / (stem + ".json"))

            for c in coarse_data.get("methods", {}).get(method_key("coarse", model), {}).get("comments", []):
                texts.append(c.get("title", "") + " " + c.get("explanation", ""))
                labels.append("coarse")
                models_tag.append(model)

            for p in prog_data.get("methods", {}).get(method_key("progressive", model), {}).get("comments", []):
                texts.append(p.get("title", "") + " " + p.get("explanation", ""))
                labels.append("progressive")
                models_tag.append(model)

            for z in zero_data.get("methods", {}).get(method_key("zero_shot", model), {}).get("comments", []):
                texts.append(z.get("title", "") + " " + z.get("explanation", ""))
                labels.append("zero_shot")
                models_tag.append(model)

    print(f"Total comments: {len(texts)}  (coarse: {labels.count('coarse')}, "
          f"progressive: {labels.count('progressive')}, zero_shot: {labels.count('zero_shot')})")

    model_emb = SentenceTransformer("all-MiniLM-L6-v2")
    X = model_emb.encode(texts, show_progress_bar=True)

    N_CLUSTERS = 10
    km = KMeans(n_clusters=N_CLUSTERS, random_state=42)
    cluster_ids = km.fit_predict(X)

    tfidf = TfidfVectorizer(max_features=10000, stop_words="english")
    X_tfidf = tfidf.fit_transform(texts)
    terms = tfidf.get_feature_names_out()

    for cluster_id in range(N_CLUSTERS):
        indices = np.where(cluster_ids == cluster_id)[0]
        method_counts = Counter(labels[i] for i in indices)
        total = len(indices)

        centroid = km.cluster_centers_[cluster_id]
        distances = np.linalg.norm(X[indices] - centroid, axis=1)
        closest = indices[np.argsort(distances)[:5]]

        cluster_tfidf = np.asarray(X_tfidf[indices].mean(axis=0)).flatten()
        top_keywords = [terms[j] for j in cluster_tfidf.argsort()[-15:][::-1]]

        print(f"\nCluster {cluster_id} ({total} comments)")
        print(f"  coarse:      {method_counts['coarse']} ({method_counts['coarse']/total*100:.0f}%)")
        print(f"  progressive: {method_counts['progressive']} ({method_counts['progressive']/total*100:.0f}%)")
        print(f"  zero_shot:   {method_counts['zero_shot']} ({method_counts['zero_shot']/total*100:.0f}%)")
        print(f"  Keywords: {', '.join(top_keywords)}")
        print(f"  Most representative comments:")
        for i in closest:
            print(f"    [{labels[i]:12s}] {texts[i][:100]}")


if __name__ == "__main__":
    FOLDERS = {
        "coarse":      "./coarse_v2/",
        "progressive": "./scaleup_v2_progressive/",
        "zero_shot":   "./scaleup_v2_zero_shot/",
    }
    MODELS = [
        "deepseek-v4-flash",
        "gemini-3.1-flash-lite-preview",
        "glm-4.7-flash",
        "qwen3.6-35b-a3b",
    ]
    TOTAL_PAPERS = len(list(Path(FOLDERS["coarse"]).glob("*.json")))

    print("=" * 90)
    print("VOLUME")
    print("=" * 90)
    volume_dicts(FOLDERS, MODELS, TOTAL_PAPERS)

    print("\n" + "=" * 90)
    print("2-WAY OVERLAP (Coarse vs. Progressive)")
    print("=" * 90)
    overlap_cp(FOLDERS, MODELS, TOTAL_PAPERS)

    print("\n" + "=" * 90)
    print("3-WAY OVERLAP (Coarse, Progressive, Zero Shot)")
    print("=" * 90)
    overlap_all(FOLDERS, MODELS, TOTAL_PAPERS)

    print("\n" + "=" * 90)
    print("CLUSTERING (Coarse + Progressive)")
    print("=" * 90)
    cluster_cp(FOLDERS, MODELS)

    print("\n" + "=" * 90)
    print("CLUSTERING (Coarse + Progressive + Zero Shot)")
    print("=" * 90)
    cluster_all(FOLDERS, MODELS)
