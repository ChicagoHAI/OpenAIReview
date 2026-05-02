"""COARSE system: shells out to coarse_driver.py via coarse's venv.

Wraps the lower-level helpers in `coarse_adapter.py` (subprocess management,
heartbeat logging, cost estimator) behind the unified `System` protocol.
"""

from __future__ import annotations

import json
from pathlib import Path

from . import coarse_adapter
from ._base import CellKey, System, CostReport, ReviewJob, ReviewResult


def _model_slug(model: str) -> str:
    return model.split("/")[-1]


def _has_content(out_json: Path) -> bool:
    try:
        existing = json.loads(out_json.read_text())
    except Exception:
        return False
    methods = existing.get("methods") or {}
    return bool(methods) and any(m.get("comments") for m in methods.values())


class CoarseSystem(System):
    name = "coarse"

    def build_jobs(self, units, cfg, results_dir):
        models = cfg.get("models") or cfg.get("coarse_models") or []
        if not models:
            raise ValueError("coarse system requires `models` in config")
        domain = results_dir.name
        out: list[tuple[CellKey, ReviewJob]] = []
        for u in units:
            if not u.staged_corrupted.exists():
                continue
            for model in models:
                slug = _model_slug(model)
                review_dir = results_dir / slug / u.error_type / "coarse" / u.paper_label / "review"
                review_dir.mkdir(parents=True, exist_ok=True)
                out_json = review_dir / f"{u.staged_corrupted.stem}.json"
                if out_json.exists():
                    if _has_content(out_json):
                        continue
                    out_json.unlink()                # empty stub from prior failure
                tag = f"{domain}/{u.paper_label}/{u.error_type}/{slug}"
                job = ReviewJob(
                    tag=tag, out_json=out_json, review_dir=review_dir,
                    paper_label=f"{u.error_type}/{u.paper_label}",
                    payload={"paper": u.staged_corrupted, "model": model},
                )
                out.append(((model,), job))
        return out

    def run_jobs(self, cell_key, jobs, parallel):
        if not jobs:
            return []
        adapter_jobs = [
            coarse_adapter.Job(
                paper=j.payload["paper"], model=j.payload["model"],
                out_json=j.out_json, paper_label=j.tag,
            )
            for j in jobs
        ]
        results = coarse_adapter.run_coarse_review(adapter_jobs, parallel=parallel)
        by_path = {j.out_json: j for j in jobs}
        return [
            ReviewResult(by_path[r.job.out_json], ok=r.ok,
                         elapsed_s=r.elapsed_s, error=r.error)
            for r in results
        ]

    def is_review_complete(self, review_dir):
        for p in review_dir.glob("*.json"):
            if p.name.endswith(".raw.json"):
                continue
            if _has_content(p):
                return True
        return False

    def pick_review_for_score(self, review_dir):
        candidates = [p for p in review_dir.glob("*.json") if not p.name.endswith(".raw.json")]
        return max(candidates, key=lambda p: p.stat().st_mtime, default=None)

    def supports_cost_estimate(self) -> bool:
        return True

    def estimate_cost(self, units, cfg, results_dir, parallel):
        models = cfg.get("models") or cfg.get("coarse_models") or []
        tmp_dir = results_dir / "_cost_tmp"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        cost_jobs: list[coarse_adapter.CostJob] = []
        for u in units:
            if not u.staged_corrupted.exists():
                continue
            for model in models:
                slug = _model_slug(model)
                label = f"{u.error_type}/{u.paper_label}"
                safe = label.replace("/", "__")
                cost_jobs.append(coarse_adapter.CostJob(
                    paper=u.staged_corrupted, model=model, paper_label=label,
                    out_json=tmp_dir / f"{safe}__{slug}.json",
                ))
        results = coarse_adapter.estimate_coarse_cost(cost_jobs, parallel=parallel)
        rows = [
            {"unit": r.job.paper_label, "model_slug": _model_slug(r.job.model),
             "cost_usd": r.total_cost_usd if r.ok else 0.0,
             "tokens": r.token_estimate if r.ok else 0,
             "ok": r.ok, "error": r.error}
            for r in results
        ]
        total = sum(row["cost_usd"] for row in rows)
        return CostReport(rows=rows, total_usd=total)
