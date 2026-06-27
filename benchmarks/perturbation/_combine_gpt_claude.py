"""Compute combined-system (GPT-5.5 OR Claude-Opus-4.7) recall on the 24-paper
frontier subset for tab:recall-overall in perturbation.tex.

A perturbation is detected by the combined system if either GPT-5.5 OR
Claude-Opus-4.7 detected it under the progressive (OpenAIReview) method.
Perturbation IDs are namespaced by (results_dir, paper, type) to avoid
cross-paper collisions.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "results"

# (results_dir, [paper_ids], [ptypes]) — must mirror configs/submission/subset_bigmodels_*.yaml.
# Note: cs_CC uses a different ptype taxonomy (claim_theoretical/logic instead
# of statement_empirical/experimental).
DOMAINS = [
    ("cs_CC_scaleup_v2",        ["paper_001", "paper_003", "paper_004"], ["surface", "claim_theoretical", "logic"]),
    ("full_cs_LG",              ["paper_001", "paper_002", "paper_003"], ["surface", "statement_empirical", "experimental"]),
    ("full_econ_EM",            ["paper_001", "paper_002", "paper_003"], ["surface", "statement_empirical", "experimental"]),
    ("full_hep_ex",             ["paper_001", "paper_002", "paper_003"], ["surface", "statement_empirical", "experimental"]),
    ("full_math_all",           ["paper_001", "paper_002", "paper_004"], ["surface", "statement_empirical", "experimental"]),
    ("full_physics_atm_clus",   ["paper_001", "paper_002", "paper_003"], ["surface", "statement_empirical", "experimental"]),
    ("full_q_bio_GN",           ["paper_001", "paper_002", "paper_003"], ["surface", "statement_empirical", "experimental"]),
    ("full_stat_AP",            ["paper_001", "paper_002", "paper_003"], ["surface", "statement_empirical", "experimental"]),
]
METHOD = "progressive"   # = OpenAIReview column


def load_score(domain: str, model: str, ptype: str, paper: str):
    p = ROOT / domain / model / ptype / METHOD / paper / "score" / "llm_t4_grounded" / f"{paper}_score.json"
    if not p.exists():
        return None
    return json.loads(p.read_text())


def keyset(score, prefix: str, kind: str) -> set[str]:
    """kind='detected' or 'all' (detected ∪ missed)."""
    if kind == "detected":
        items = score["detected"]
    else:
        items = list(score["detected"]) + list(score["missed"])
    return {f"{prefix}::{x}" for x in items}


def collect(model: str) -> tuple[set[str], set[str]]:
    detected, injected = set(), set()
    for domain, papers, ptypes in DOMAINS:
        for paper in papers:
            for ptype in ptypes:
                s = load_score(domain, model, ptype, paper)
                if s is None:
                    continue
                prefix = f"{domain}|{ptype}|{paper}"
                detected |= keyset(s, prefix, "detected")
                injected |= keyset(s, prefix, "all")
    return detected, injected


MODELS = [
    ("GPT-5.5",                "gpt-5.5"),
    ("Claude-Opus-4.7",        "claude-opus-4.7"),
    ("Grok-4.1-Fast",          "grok-4.1-fast"),
    ("DeepSeek-V4-Flash",      "deepseek-v4-flash"),
    ("Qwen3.6-35B-A3B",        "qwen3.6-35b-a3b"),
    ("Gemini-3.1-Flash-Lite",  "gemini-3.1-flash-lite-preview"),
]


def main():
    per_model = {}
    for label, slug in MODELS:
        det, inj = collect(slug)
        per_model[label] = (det, inj)
        print(f"{label:23s}: {len(det):>4} / {len(inj):>4} = {len(det)/len(inj)*100:5.1f}%")

    all_det = set().union(*(d for d, _ in per_model.values()))
    all_inj = set().union(*(i for _, i in per_model.values()))
    print()
    print("Combined (ANY of the 6 models, progressive/OpenAIReview):")
    print(f"  union injected : {len(all_inj)}")
    print(f"  union detected : {len(all_det)}")
    print(f"  recall         : {len(all_det)/len(all_inj)*100:5.1f}%")
    print()

    # Cumulative-by-rank: add models in descending single-model recall order
    print("Cumulative recall as models are added (best single first):")
    order = sorted(per_model.items(), key=lambda kv: -len(kv[1][0]))
    cum_det, cum_inj = set(), set()
    for label, (d, i) in order:
        cum_det |= d
        cum_inj |= i
        print(f"  + {label:23s}: {len(cum_det):>4} / {len(cum_inj):>4} = {len(cum_det)/len(cum_inj)*100:5.1f}%")
    print()

    # How many perturbations only ONE model caught
    print("Coverage by # of detecting models (perturbations in union):")
    coverage = {}
    for pid in all_inj:
        n = sum(1 for d, _ in per_model.values() if pid in d)
        coverage[n] = coverage.get(n, 0) + 1
    for n in sorted(coverage):
        tag = "missed by all" if n == 0 else f"caught by {n} model(s)"
        print(f"  {tag:25s}: {coverage[n]:>4}")


if __name__ == "__main__":
    main()
