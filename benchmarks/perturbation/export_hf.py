#!/usr/bin/env python3
"""Export the perturbation benchmark as a Hugging Face dataset.

One row per (paper, error type): the clean paper, the perturbed paper, the
truncated perturbed paper that review systems were given, and the list of
injected errors with their offsets into the clean paper.

Full text is included only for papers whose arXiv license allows
redistributing modified copies (CC BY, CC BY-SA, CC BY-NC, CC BY-NC-SA). For
the rest, the text columns are empty, and `rebuild.py` (uploaded alongside the
data) downloads the arXiv source and re-applies the edits.

Usage:
  python benchmarks/perturbation/export_hf.py --meta arxiv_meta.json --out hf_export
  python benchmarks/perturbation/export_hf.py ... --push ChicagoHAI/<repo> [--public]

`--meta` maps each arXiv id to {title, primary_category, license}, as
returned by the arXiv API and OAI-PMH endpoints.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(HERE.parent))

from perturbation.extract import extract_candidates  # noqa: E402
from reviewer.utils import count_tokens, truncate_text  # noqa: E402

RESULTS = HERE / "results"
CLEAN_ROOT = HERE / "data" / "perturbations"
MAX_TOKENS = 13000  # review-input length used for every run in the paper

# Benchmark run directory -> benchmark domain (the arXiv listing papers were sampled from)
RUNS = {
    "cs_CC_scaleup_v2": "cs.CC",
    "full_cs_LG": "cs.LG",
    "full_econ_EM": "econ.EM",
    "full_hep_ex": "hep-ex",
    "full_math_all": "math",
    "full_physics_atm_clus": "physics.atm-clus",
    "full_q_bio_GN": "q-bio.GN",
    "full_stat_AP": "stat.AP",
}
CATEGORY = {"surface": "Surface", "statement_empirical": "Claim", "claim_theoretical": "Claim",
            "logic": "Reasoning", "experimental": "Experimental"}
# Papers the frontier models (GPT-5.5, Claude Opus 4.7) were also run on: the first
# three per run, skipping papers that the minimum-perturbation filter removed entirely
FRONTIER = {run: {"paper_001", "paper_002", "paper_003"} for run in RUNS} | {
    "cs_CC_scaleup_v2": {"paper_001", "paper_003", "paper_004"},
    "full_math_all": {"paper_001", "paper_002", "paper_004"},
}
REDISTRIBUTABLE = ("/by/", "/by-sa/", "/by-nc/", "/by-nc-sa/")


def sha256(text: str | None) -> str | None:
    return hashlib.sha256(text.encode()).hexdigest() if text is not None else None


def locate(clean: str, paper_type: str, error_type: str, perts: list[dict]) -> list[int]:
    """Offset of each edit in the clean paper, recovered the way reinject_existing.py does."""
    by_span = {c.span_id: c.offset for c in extract_candidates(paper_type, error_type, clean)}
    offsets = []
    for p in perts:
        off = by_span.get(p["span_id"])
        if off is None or clean[off:off + len(p["original"])] != p["original"]:
            off = clean.find(p["original"])
        if off < 0:
            raise ValueError(f"cannot locate {p['perturbation_id']}")
        offsets.append(off)
    return offsets


def apply_edits(clean: str, edits: list[dict]) -> str:
    text = clean
    for e in sorted(edits, key=lambda e: e["offset"], reverse=True):
        text = text[:e["offset"]] + e["perturbed"] + text[e["offset"] + len(e["original"]):]
    return text


def build_rows(meta: dict) -> list[dict]:
    rows = []
    for run, domain in RUNS.items():
        rdir = RESULTS / run
        cfg = (rdir / "config.yaml").read_text()
        input_dir = REPO_ROOT / next(l.split(":", 1)[1].strip() for l in cfg.splitlines() if l.startswith("input_dir:"))
        index = json.loads((rdir / "paper_index.json").read_text())
        for staged in sorted(rdir.glob("perturb/*/paper_*/paper_*_perturbations.json")):
            label, error_type = staged.parent.name, staged.parents[1].name
            aid = index[label]
            unit = input_dir / aid / error_type
            kept_path = next(unit.glob("*_kept_perturbations.json"))
            kept = json.loads(kept_path.read_text())
            kept = kept["perturbations"] if isinstance(kept, dict) else kept
            # The pipeline read papers in text mode, which turns any stray carriage
            # return in an edit (e.g. "\right" mis-parsed as "\r" + "ight") into "\n".
            for p in kept:
                p["perturbed"] = p["perturbed"].replace("\r\n", "\n").replace("\r", "\n")
            clean = next(CLEAN_ROOT.glob(f"*/*/{aid}/{error_type}/*_clean.md")).read_text()
            paper_type = "empirical" if error_type in ("statement_empirical", "experimental") else "theoretical"

            offsets = locate(clean, paper_type, error_type, kept)
            scored = {p["perturbation_id"] for p in json.loads(staged.read_text())["perturbations"]}
            edits = [{
                "perturbation_id": p["perturbation_id"],
                "error_subtype": p["error"],
                "original": p["original"],
                "perturbed": p["perturbed"],
                "offset": off,
                "why_wrong": p.get("why_wrong", ""),
                "verifier_quote": p.get("quote", ""),
                "verifier_reason": p.get("reason", ""),
                "scored": p["perturbation_id"] in scored,
            } for p, off in sorted(zip(kept, offsets), key=lambda x: x[1])]

            perturbed = apply_edits(clean, edits)
            recorrupted = kept_path.with_name(kept_path.name.replace("_kept_perturbations.json", "_recorrupted.md"))
            assert perturbed == recorrupted.read_text(), f"{aid}/{error_type}: edits do not reproduce the perturbed paper"
            review_input = truncate_text(perturbed, MAX_TOKENS) if count_tokens(perturbed) > MAX_TOKENS else perturbed
            assert review_input == staged.with_name(f"{label}_corrupted.md").read_text(), f"{aid}/{error_type}: truncation mismatch"

            m = meta[aid]
            included = any(s in m["license"] for s in REDISTRIBUTABLE)
            rows.append({
                "id": f"{aid}__{error_type}",
                "arxiv_id": aid,
                "title": m["title"],
                "domain": domain,
                "primary_category": m["primary_category"],
                "paper_type": paper_type,
                "error_type": error_type,
                "error_category": CATEGORY[error_type],
                "in_frontier_subset": label in FRONTIER[run],
                "license": m["license"],
                "text_included": included,
                "clean_paper": clean if included else None,
                "perturbed_paper": perturbed if included else None,
                "review_input": review_input if included else None,
                "clean_sha256": sha256(clean),
                "perturbed_sha256": sha256(perturbed),
                "review_input_sha256": sha256(review_input),
                "n_perturbations": len(edits),
                "n_scored": sum(e["scored"] for e in edits),
                "perturbations": edits,
            })
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--meta", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--push", help="Hugging Face repo id to upload to")
    ap.add_argument("--public", action="store_true", help="create the repo as public (default private)")
    args = ap.parse_args()

    rows = build_rows(json.loads(args.meta.read_text()))
    args.out.mkdir(parents=True, exist_ok=True)
    with open(args.out / "test.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    n_inc = sum(r["text_included"] for r in rows)
    print(f"{len(rows)} rows ({n_inc} with text), {len({r['arxiv_id'] for r in rows})} papers, "
          f"{sum(r['n_scored'] for r in rows)} scored perturbations -> {args.out}")

    if args.push:
        from datasets import load_dataset
        from huggingface_hub import HfApi
        ds = load_dataset("json", data_files={"test": str(args.out / "test.jsonl")}, split="test")
        ds.push_to_hub(args.push, private=not args.public)
        api = HfApi()
        for name in ("README.md", "rebuild.py"):
            if (args.out / name).exists():
                api.upload_file(path_or_fileobj=str(args.out / name), path_in_repo=name,
                                repo_id=args.push, repo_type="dataset")
        print(f"pushed to https://huggingface.co/datasets/{args.push}")


if __name__ == "__main__":
    main()
