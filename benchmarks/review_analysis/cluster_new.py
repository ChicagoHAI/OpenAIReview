"""One-off clustering for the two new tables (3-system + human-vs-AI).

Mirrors the pipeline in analysis.py:cluster_cp but on the (coarse, OpenAIReview,
Reviewer 3) triple and on (human union, AI union) — same 70-paper cohort that
analysis_three_systems.py and analysis_with_humans.py use.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer


RESULTS = Path("../conference_study/results")
HUMAN_DIR = RESULTS / "human_v1"

SYSTEMS = [
    ("coarse",       RESULTS / "coarse_v2",                    "coarse__deepseek-v4-flash"),
    ("openaireview", RESULTS / "frontier_subset_progressive",  "progressive__gpt-5.5"),
    ("reviewer3",    RESULTS / "reviewer3_v2",                 "reviewer3__reviewer3"),
]

N_CLUSTERS = 10
TOP_KEYWORDS = 15
N_REPRESENTATIVE = 6


def load_comments(folder: Path, method_key: str, slugs: set[str]) -> list[dict]:
    """Return list of {text, source} for `method_key` comments in `folder`."""
    out = []
    for slug in slugs:
        p = folder / f"{slug}.json"
        if not p.exists():
            continue
        d = json.loads(p.read_text())
        for c in d.get("methods", {}).get(method_key, {}).get("comments", []):
            text = (c.get("title", "") + " " + c.get("explanation", "")).strip()
            if text:
                out.append(text)
    return out


def stems(folder: Path) -> set[str]:
    return {p.stem for p in folder.glob("*.json")}


def cluster_and_report(texts: list[str], labels: list[str], source_names: list[str]) -> dict:
    """Run kmeans + TF-IDF, print cluster summaries, return per-cluster source shares."""
    print(f"Total comments: {len(texts)}")
    for name in source_names:
        n = labels.count(name)
        print(f"  {name}: {n}  ({n / len(texts) * 100:.0f}%)")

    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    X = embedder.encode(texts, show_progress_bar=False)

    km = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init="auto")
    cluster_ids = km.fit_predict(X)

    tfidf = TfidfVectorizer(max_features=10000, stop_words="english")
    X_tfidf = tfidf.fit_transform(texts)
    terms = tfidf.get_feature_names_out()

    cluster_info = []
    for cid in range(N_CLUSTERS):
        idx = np.where(cluster_ids == cid)[0]
        n = len(idx)
        if n == 0:
            continue
        counts = Counter(labels[i] for i in idx)
        centroid = km.cluster_centers_[cid]
        dists = np.linalg.norm(X[idx] - centroid, axis=1)
        closest = idx[np.argsort(dists)[:N_REPRESENTATIVE]]
        cluster_tfidf = np.asarray(X_tfidf[idx].mean(axis=0)).flatten()
        top = [terms[j] for j in cluster_tfidf.argsort()[-TOP_KEYWORDS:][::-1]]

        info = {
            "id": cid,
            "size": n,
            "share": {name: counts.get(name, 0) for name in source_names},
            "keywords": top,
            "representative": [texts[i][:140] for i in closest],
        }
        cluster_info.append(info)

        print(f"\n--- Cluster {cid}  (n={n}) ---")
        for name in source_names:
            k = counts.get(name, 0)
            print(f"  {name:15s} {k:5d}  ({k / n * 100:5.1f}%)")
        print(f"  keywords: {', '.join(top)}")
        for s in info["representative"]:
            print(f"    > {s}")
    return cluster_info


def main_three_systems() -> None:
    print("=" * 90)
    print("3-WAY CLUSTERING: coarse vs OpenAIReview vs Reviewer 3")
    print("=" * 90)
    slugs = set.intersection(*(stems(folder) for _, folder, _ in SYSTEMS))
    print(f"Papers in all 3 systems: {len(slugs)}")

    texts, labels = [], []
    for name, folder, mk in SYSTEMS:
        cs = load_comments(folder, mk, slugs)
        texts.extend(cs)
        labels.extend([name] * len(cs))

    info = cluster_and_report(texts, labels, [n for n, _, _ in SYSTEMS])
    Path("cluster_three_systems.json").write_text(json.dumps(info, indent=2))


def main_human_vs_ai() -> None:
    print("\n" + "=" * 90)
    print("HUMAN vs AI-UNION CLUSTERING")
    print("=" * 90)
    ai_intersection = set.intersection(*(stems(folder) for _, folder, _ in SYSTEMS))
    human_present = stems(HUMAN_DIR)
    slugs = sorted(ai_intersection & human_present)
    print(f"Papers in 3 AI systems AND human_v1/: {len(slugs)}")

    texts, labels = [], []
    # Human side
    for slug in slugs:
        d = json.loads((HUMAN_DIR / f"{slug}.json").read_text())
        for c in d.get("methods", {}).get("human__openreview", {}).get("comments", []):
            text = (c.get("title", "") + " " + c.get("explanation", "")).strip()
            if text:
                texts.append(text)
                labels.append("human")
    # AI union side
    for name, folder, mk in SYSTEMS:
        for slug in slugs:
            p = folder / f"{slug}.json"
            if not p.exists():
                continue
            d = json.loads(p.read_text())
            for c in d.get("methods", {}).get(mk, {}).get("comments", []):
                text = (c.get("title", "") + " " + c.get("explanation", "")).strip()
                if text:
                    texts.append(text)
                    labels.append("ai")

    info = cluster_and_report(texts, labels, ["human", "ai"])
    Path("cluster_human_vs_ai.json").write_text(json.dumps(info, indent=2))


if __name__ == "__main__":
    main_three_systems()
    main_human_vs_ai()
