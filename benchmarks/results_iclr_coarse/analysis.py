import json                                                                                                                                                                          
from pathlib import Path
from collections import defaultdict
from rapidfuzz import fuzz
import numpy as np
import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn2_circles, venn3, venn3_circles

from sentence_transformers import SentenceTransformer     
from sklearn.feature_extraction.text import TfidfVectorizer                                                                                                                           
from sklearn.cluster import KMeans                                                                                                                                                   
from sklearn.manifold import TSNE                                                                                                                                                    
from collections import Counter                                                                                                                                                  
                                                                                                                                                                                                                                                                                                                                           
def load(path):                                                                                                                                                                      
  return json.loads(Path(path).read_text())   

def method_key(folder_name, model):
  prefix = {"coarse": "coarse", "progressive": "progressive", "zero_shot": "zero_shot"}                                                                                            
  return f"{prefix[folder_name]}__{model}" 

'''
folders = {method: folder path}
models = [models]
total_papers = # of papers

Ex:
FOLDERS = {                                                                                                                                                                          
  "coarse":       "./coarse_v2/",
  "progressive":  "./scaleup_v2_progressive/",
  "zero_shot": "./scaleup_v2_zero_shot/"
}                                                                                                                                                                                    

MODELS = ["deepseek-v4-flash", "gemini-3.1-flash-lite-preview", "glm-4.7-flash", "qwen3.6-35b-a3b"]  

TOTAL_PAPERS = len(list(Path(FOLDERS["coarse"]).glob("*.json"))) 
'''



# VOLUME 

def volume_dicts(folders, models, total_papers):
    volume = {}  # { slug -> { "coarse/deepseek": 5, "progressive/deepseek": 3, ... } }                                                                                                  
              
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
    
    print(f"Average number of comments per paper:\n")    
    print(f"{'Model':<40} {'Coarse':>10} {'Progressive':>12} {'Zero Shot':>11} {'Winner':>12}")                                                                                          
    print("-" * 90)                                                                                                                                                                      
    for model, counts in average_volume.items():                                                                                                                                         
        coarse = counts.get('coarse', 0)                                                                                                                                              
        prog = counts.get('progressive', 0)                                                                                                                                         
        zero_shot = counts.get('zero_shot', 0)
        winner = max(counts, key=counts.get)                                                                                                                                          
        print(f"{model:<40} {coarse:>10.2f} {prog:>12.2f} {zero_shot:>11.2f} {winner:>12}")

    return volume, highest_volume, average_volume



# Comment Overlap (Coarse, Progressive)

def get_papers(folders):
    first_folder = next(iter(folders.values()))
    if not first_folder:
        return None
    
    papers = []
    for p in list(Path(first_folder).glob("*.json")):
        papers.append(p.stem)
    
    return papers 

def overlap_cp(folders, models, total_papers):
    overlap_ind = defaultdict(lambda: defaultdict(dict))
    overlap_total = defaultdict(lambda: {"both_total": 0,  "only_c_total": 0,  "only_p_total": 0})
    overlap_avg = defaultdict(lambda: {"both_avg": 0,  "only_c_avg": 0,  "only_p_avg": 0, "jaccard_sim_avg": 0})

    papers = get_papers(folders)
    if not papers:
        return None

    temp_jaccard_sim = defaultdict(int)
    temp_count = defaultdict(int)
    for stem in papers:                                                                                                                                                                  
        coarse_data = load(Path(folders["coarse"]) / (stem + ".json"))                                                                                                                   
        prog_data   = load(Path(folders["progressive"]) / (stem + ".json"))
                                                                                                                                                                                                                                                                                                                        
        def para_set(d, method_key):                                                                                                                                                     
            comments = d.get("methods", {}).get(method_key, {}).get("comments", [])                                                                                                      
            return {c["paragraph_index"] for c in comments if "paragraph_index" in c}    

        for model in models:                                                                                                                                                                                 
            coarse_paras = para_set(coarse_data, method_key("coarse", model))                                                                                                                
            prog_paras   = para_set(prog_data, method_key("progressive", model))                                                                                                           
                                                                                                                                                                                            
            both_idx      = coarse_paras & prog_paras                                                                                                                                        
            only_c_idx    = coarse_paras - prog_paras
            only_p_idx    = prog_paras   - coarse_paras 
            
            both_num      = len(coarse_paras & prog_paras)                                                                                                                                        
            only_c_num    = len(coarse_paras - prog_paras)
            only_p_num    = len(prog_paras   - coarse_paras) 
            total_num = both_num + only_c_num + only_p_num

            overlap_ind[model][stem]["both_idx"] = both_idx
            overlap_ind[model][stem]["only_c_idx"] = only_c_idx
            overlap_ind[model][stem]["only_p_idx"] = only_p_idx
            overlap_ind[model][stem]["both_num"] = both_num 
            overlap_ind[model][stem]["only_c_num"] = only_c_num 
            overlap_ind[model][stem]["only_p_num"] = only_p_num
            overlap_ind[model][stem]["both_pct"] = both_num / total_num if total_num != 0 else None
            overlap_ind[model][stem]["only_c_pct"] = only_c_num / total_num if total_num != 0 else None
            overlap_ind[model][stem]["only_p_pct"] = only_p_num / total_num if total_num != 0 else None
            overlap_ind[model][stem]["jaccard_sim"] = both_num / total_num if total_num != 0 else None

            overlap_total[model]["both_total"] += both_num
            overlap_total[model]["only_c_total"] += only_c_num
            overlap_total[model]["only_p_total"] += only_p_num
            
            temp_jaccard_sim[model] += both_num / total_num if total_num != 0 else 0
            temp_count[model] += 1 if total_num != 0 else 0

    for model in models:
        overlap_avg[model]["both_avg"] = overlap_total[model]["both_total"] / total_papers
        overlap_avg[model]["only_c_avg"] = overlap_total[model]["only_c_total"] / total_papers
        overlap_avg[model]["only_p_avg"] = overlap_total[model]["only_p_total"] / total_papers
        overlap_avg[model]["jaccard_sim_avg"] = temp_jaccard_sim[model] / temp_count[model]
    
    print(f"Average overlap per paper:\n")
    print(f"{'Model':<35} {'Both':>8} {'Only C':>8} {'Only P':>8} {'Jaccard':>8}")
    print("-" * 71)
    for model, counts in overlap_avg.items():                                                                                                                                            
        print(f"{model:<35} {counts['both_avg']:>8.2f} {counts['only_c_avg']:>8.2f} {counts['only_p_avg']:>8.2f} {counts['jaccard_sim_avg']:>8.3f}")
    
    plot_overlap_cp(overlap_avg)

    return overlap_ind, overlap_total, overlap_avg

def plot_overlap_cp(overlap_avg):                                                                                                                                                                           
    COLORS = ["#2196F3", "#E53935"]  # blue, red
                                                                                                                                                                                    
    fig, axes = plt.subplots(2, 2, figsize=(14, 11), dpi=400)                                                                                                                            
    axes = axes.flatten()
                                                                                                                                                                                    
    for i, (model, counts) in enumerate(overlap_avg.items()):
        only_c = round(counts["only_c_avg"], 2)
        only_p = round(counts["only_p_avg"], 2)                                                                                                                                          
        both   = round(counts["both_avg"], 2)
                                                                                                                                                                                        
        v = venn2(                                                                                                                                                                       
            subsets=(only_c, only_p, both),
            set_labels=("Coarse", "Progressive"),                                                                                                                                        
            ax=axes[i],  
            set_colors=COLORS,
            alpha=0.15,                                                                                                                                                                  
        )
                                                                                                                                                                                        
        c = venn2_circles(
            subsets=(only_c, only_p, both),
            ax=axes[i],
            linewidth=2.0,
        )

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

        axes[i].set_title(f"{model}\nJaccard Similarity: {counts['jaccard_sim_avg']:.3f}",                                                                                               
                            fontsize=15, fontweight="bold", pad=10)
                                                                                                                                                                                        
    plt.tight_layout()                                                                                                                                                                   
    plt.subplots_adjust(hspace=0.2, wspace=0.1)                                                                                                                                                         
    plt.savefig("./venn_cp.png", dpi=400, bbox_inches="tight")



# Comment Overlap (Coarse, Progressive, Zero Shot)

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

    def para_set(d, mk):
        comments = d.get("methods", {}).get(mk, {}).get("comments", [])
        return {c["paragraph_index"] for c in comments if "paragraph_index" in c}

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

            all_idx     = coarse_paras & prog_paras & zero_paras
            only_c_idx  = coarse_paras - prog_paras - zero_paras
            only_p_idx  = prog_paras   - coarse_paras - zero_paras
            only_z_idx  = zero_paras   - coarse_paras - prog_paras
            only_c_p_idx = (coarse_paras & prog_paras)  - zero_paras
            only_c_z_idx = (coarse_paras & zero_paras)  - prog_paras
            only_p_z_idx = (prog_paras   & zero_paras)  - coarse_paras

            all_num     = len(all_idx)
            only_c_num  = len(only_c_idx)
            only_p_num  = len(only_p_idx)
            only_z_num  = len(only_z_idx)
            only_c_p_num = len(only_c_p_idx)
            only_c_z_num = len(only_c_z_idx)
            only_p_z_num = len(only_p_z_idx)
            total_num = all_num + only_c_num + only_p_num + only_z_num + only_c_p_num + only_c_z_num + only_p_z_num

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
            overlap_ind[model][stem]["jaccard_sim"]  = all_num / total_num if total_num != 0 else None

            overlap_total[model]["all_total"]      += all_num
            overlap_total[model]["only_c_total"]   += only_c_num
            overlap_total[model]["only_p_total"]   += only_p_num
            overlap_total[model]["only_z_total"]   += only_z_num
            overlap_total[model]["only_c_p_total"] += only_c_p_num
            overlap_total[model]["only_c_z_total"] += only_c_z_num
            overlap_total[model]["only_p_z_total"] += only_p_z_num

            temp_jaccard_sim[model] += all_num / total_num if total_num != 0 else 0
            temp_count[model]       += 1 if total_num != 0 else 0

    for model in models:
        overlap_avg[model]["all_avg"]       = overlap_total[model]["all_total"]       / total_papers
        overlap_avg[model]["only_c_avg"]    = overlap_total[model]["only_c_total"]    / total_papers
        overlap_avg[model]["only_p_avg"]    = overlap_total[model]["only_p_total"]    / total_papers
        overlap_avg[model]["only_z_avg"]    = overlap_total[model]["only_z_total"]    / total_papers
        overlap_avg[model]["only_c_p_avg"]  = overlap_total[model]["only_c_p_total"]  / total_papers
        overlap_avg[model]["only_c_z_avg"]  = overlap_total[model]["only_c_z_total"]  / total_papers
        overlap_avg[model]["only_p_z_avg"]  = overlap_total[model]["only_p_z_total"]  / total_papers
        overlap_avg[model]["jaccard_sim_avg"] = temp_jaccard_sim[model] / temp_count[model] if temp_count[model] else 0

    print(f"Average 3-way overlap per paper:\n")
    print(f"{'Model':<35} {'All':>6} {'Only C':>8} {'Only P':>8} {'Only Z':>8} {'C∩P':>6} {'C∩Z':>6} {'P∩Z':>6} {'Jaccard':>8}")
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
    COLORS = ["#2196F3", "#E53935", "#43A047"]  # blue, red, green

    fig, axes = plt.subplots(2, 2, figsize=(14, 11), dpi=400)
    axes = axes.flatten()

    for i, (model, counts) in enumerate(overlap_avg.items()):
        only_c    = round(counts["only_c_avg"],   2)
        only_p    = round(counts["only_p_avg"],   2)
        only_z    = round(counts["only_z_avg"],   2)
        only_cp   = round(counts["only_c_p_avg"], 2)
        only_cz   = round(counts["only_c_z_avg"], 2)
        only_pz   = round(counts["only_p_z_avg"], 2)
        all_three = round(counts["all_avg"],       2)

        v = venn3(
            subsets=(only_c, only_p, only_cp, only_z, only_cz, only_pz, all_three),
            set_labels=("Coarse", "Progressive", "Zero Shot"),
            ax=axes[i],
            set_colors=COLORS,
            alpha=0.15,
        )

        c = venn3_circles(
            subsets=(only_c, only_p, only_cp, only_z, only_cz, only_pz, all_three),
            ax=axes[i],
            linewidth=2.0,
        )

        for circle, color in zip(c, COLORS):
            circle.set_edgecolor(color)
            circle.set_linewidth(2.0)

        for label_id in ["100", "010", "110", "001", "101", "011", "111"]:
            lbl = v.get_label_by_id(label_id)
            if lbl:
                lbl.set_fontsize(13)
                lbl.set_color("black")
                lbl.set_fontweight("normal")
                lbl.set_ha("center")

        for set_label in v.set_labels:
            if set_label:
                set_label.set_fontsize(13)
                set_label.set_color("black")

        axes[i].set_title(f"{model}\nJaccard Similarity: {counts['jaccard_sim_avg']:.3f}",
                          fontsize=15, fontweight="bold", pad=10)

    plt.tight_layout()
    plt.subplots_adjust(hspace=0.2, wspace=0.1)
    plt.savefig("./venn_all.png", dpi=400, bbox_inches="tight")



# Cluster Analysis

def cluster_cp(folders, models):
    # 1. Collect comments                                                                                                       
    texts      = []                                                                                                                                                                      
    labels     = [] # "coarse" or "progressive"                                                                                                                                                                    
    models_tag = [] 

    papers = get_papers(folders)
    if not papers:
        return None

    for model in models:
        for stem in papers:
            coarse_data = load(Path(folders["coarse"]) / (stem + ".json"))                                                                                                               
            prog_data   = load(Path(folders["progressive"]) / (stem + ".json"))                                                                                                          
                                                                                                                                                                                        
            for c in coarse_data.get("methods", {}).get(method_key("coarse", model), {}).get("comments", []):                                                                            
                texts.append(c.get("title", "") + " " + c.get("explanation", ""))                                                                                                        
                labels.append("coarse")                                                                                                                                                  
                models_tag.append(model)

            for p in prog_data.get("methods", {}).get(method_key("progressive", model), {}).get("comments", []):                                                                         
                texts.append(p.get("title", "") + " " + p.get("explanation", ""))
                labels.append("progressive")                                                                                                                                             
                models_tag.append(model)
                                                                                                                                                                                    
    print(f"Total comments: {len(texts)}  (coarse: {labels.count('coarse')}, progressive: {labels.count('progressive')})")                                                               
                                                                                                                                                                                    
    # 2. Embed and cluster                                                                                                      
    model_emb = SentenceTransformer("all-MiniLM-L6-v2")
    X = model_emb.encode(texts, show_progress_bar=True)                                                                                                                                  
                                                                                                    
    N_CLUSTERS = 10
    km = KMeans(n_clusters=N_CLUSTERS, random_state=42)                                                                                                                                  
    cluster_ids = km.fit_predict(X)                                                                                                                                                      

    # 3. Results                  

    # fit TF-IDF on clustered comments for keywords                                                                                                                                                            
    tfidf = TfidfVectorizer(max_features=10000, stop_words="english")
    X_tfidf = tfidf.fit_transform(texts)                                                                                                                                                 
    terms = tfidf.get_feature_names_out()

    for cluster_id in range(N_CLUSTERS):                                                                                                                                                 
        indices = np.where(cluster_ids == cluster_id)[0]                                                                                                                                 
        method_counts = Counter(labels[i] for i in indices)                                                                                                                              
        total = len(indices)                                                                                                                                                             
                
        # find 5 comments closest to the cluster centroid                                                                                                                                
        centroid = km.cluster_centers_[cluster_id]
        distances = np.linalg.norm(X[indices] - centroid, axis=1)                                                                                                                        
        closest = indices[np.argsort(distances)[:5]]          

        # average TF-IDF score across all docs in this cluster                                                                                                                           
        cluster_tfidf = X_tfidf[indices].mean(axis=0)
        cluster_tfidf = np.asarray(cluster_tfidf).flatten()                                                                                                                              
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

    print(f"Total comments: {len(texts)}  (coarse: {labels.count('coarse')}, progressive: {labels.count('progressive')}, zero_shot: {labels.count('zero_shot')})")

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

        centroid  = km.cluster_centers_[cluster_id]
        distances = np.linalg.norm(X[indices] - centroid, axis=1)
        closest   = indices[np.argsort(distances)[:5]]

        cluster_tfidf = np.asarray(X_tfidf[indices].mean(axis=0)).flatten()
        top_keywords  = [terms[j] for j in cluster_tfidf.argsort()[-15:][::-1]]

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
    MODELS = ["deepseek-v4-flash", "gemini-3.1-flash-lite-preview", "glm-4.7-flash", "qwen3.6-35b-a3b"]
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
