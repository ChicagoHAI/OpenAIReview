"""Cluster-bootstrap-over-papers 95% CIs for the §5 recall tables.

Resampling unit = paper. For each (method, model[, category]) cell we collect
per-paper (detected, injected) counts over the 24-paper frontier subset (the
same papers/ptypes as _combine_gpt_claude.py / configs/submission/subset_bigmodels_*),
then bootstrap-resample the contributing papers with replacement, recompute
pooled recall = sum(detected)/sum(injected), and take 2.5/97.5 percentiles.

Point estimate matches the paper (e.g., GPT-5.5 progressive = 571/797 = 71.6%).
No significance tests — CIs only.
"""
import json
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "results"
SCORE = "llm_t4_grounded"
B = 5000
RNG = np.random.default_rng(42)

# (results_dir, [papers], [ptypes]) — frontier 24-paper subset.
DOMAINS = [
    ("cs_CC_scaleup_v2",      ["paper_001", "paper_003", "paper_004"], ["surface", "claim_theoretical", "logic"]),
    ("full_cs_LG",            ["paper_001", "paper_002", "paper_003"], ["surface", "statement_empirical", "experimental"]),
    ("full_econ_EM",          ["paper_001", "paper_002", "paper_003"], ["surface", "statement_empirical", "experimental"]),
    ("full_hep_ex",           ["paper_001", "paper_002", "paper_003"], ["surface", "statement_empirical", "experimental"]),
    ("full_math_all",         ["paper_001", "paper_002", "paper_004"], ["surface", "statement_empirical", "experimental"]),
    ("full_physics_atm_clus", ["paper_001", "paper_002", "paper_003"], ["surface", "statement_empirical", "experimental"]),
    ("full_q_bio_GN",         ["paper_001", "paper_002", "paper_003"], ["surface", "statement_empirical", "experimental"]),
    ("full_stat_AP",          ["paper_001", "paper_002", "paper_003"], ["surface", "statement_empirical", "experimental"]),
]

# ptype -> high-level category for tab:recall-by-type
CAT = {
    "surface": "Surface",
    "statement_empirical": "Claim",
    "claim_theoretical": "Claim",
    "logic": "Reasoning",
    "experimental": "Experimental",
}

MODELS = {
    "GPT-5.5": "gpt-5.5", "Claude-Opus-4.7": "claude-opus-4.7",
    "Grok-4.1-Fast": "grok-4.1-fast", "DeepSeek-V4-Flash": "deepseek-v4-flash",
    "Qwen3.6-35B-A3B": "qwen3.6-35b-a3b", "Gemini-3.1-Flash-Lite": "gemini-3.1-flash-lite-preview",
}


def base_of(domain):
    return domain.replace("full_", "").replace("_scaleup_v2", "")


def load(domain, model, ptype, method, paper):
    if method == "reviewer3":
        p = ROOT / f"full_{base_of(domain)}_reviewer3" / "reviewer3" / ptype / "reviewer3" / paper / "score" / SCORE / f"{paper}_score.json"
    else:
        p = ROOT / domain / model / ptype / method / paper / "score" / SCORE / f"{paper}_score.json"
    if not p.exists():
        return None
    return json.loads(p.read_text())


def per_paper_counts(model_slug, method, category=None):
    """Return list of (detected, injected) per paper for this cell."""
    rows = []
    for domain, papers, ptypes in DOMAINS:
        for paper in papers:
            det = inj = 0
            got = False
            for pt in ptypes:
                if category and CAT.get(pt) != category:
                    continue
                s = load(domain, model_slug, pt, method, paper)
                if s is None:
                    continue
                got = True
                det += s["n_detected"]
                inj += s["n_injected"]
            if got and inj > 0:
                rows.append((det, inj))
    return rows


def boot_ci(rows):
    if not rows:
        return (float("nan"), float("nan"), float("nan"), 0, 0)
    det = np.array([r[0] for r in rows], float)
    inj = np.array([r[1] for r in rows], float)
    point = det.sum() / inj.sum()
    n = len(rows)
    idx = RNG.integers(0, n, size=(B, n))
    bd = det[idx].sum(axis=1)
    bi = inj[idx].sum(axis=1)
    rec = bd / bi
    lo, hi = np.percentile(rec, [2.5, 97.5])
    return (point, lo, hi, int(det.sum()), int(inj.sum()))


def fmt(point, lo, hi, d, i):
    return f"{point*100:5.1f}% [{lo*100:4.1f}, {hi*100:4.1f}]  ({d}/{i})"


if __name__ == "__main__":
    print("=== tab:recall-overall (per model × method), frontier subset ===")
    for label, slug in MODELS.items():
        line = f"{label:22s}"
        for method in ("zero_shot", "coarse", "progressive"):
            rows = per_paper_counts(slug, method)
            line += " | " + fmt(*boot_ci(rows))
        print(line)
    r3 = per_paper_counts("reviewer3", "reviewer3")
    print("Reviewer3 (overall)   | " + fmt(*boot_ci(r3)))

    print("\n=== tab:recall-by-type (best backend per system) ===")
    cells = [
        ("coarse / DeepSeek-V4", "deepseek-v4-flash", "coarse"),
        ("zero-shot / GPT-5.5",  "gpt-5.5",           "zero_shot"),
        ("OpenAIReview / GPT-5.5","gpt-5.5",          "progressive"),
        ("Reviewer3",            "reviewer3",         "reviewer3"),
    ]
    cats = [None, "Experimental", "Claim", "Reasoning", "Surface"]
    print(f"{'cell':24s} | " + " | ".join((c or 'Overall') for c in cats))
    for name, slug, method in cells:
        line = f"{name:24s}"
        for c in cats:
            rows = per_paper_counts(slug, method, c)
            p, lo, hi, d, i = boot_ci(rows)
            line += f" | {p*100:4.1f}[{lo*100:.1f},{hi*100:.1f}]n{len(rows)}"
        print(line)
