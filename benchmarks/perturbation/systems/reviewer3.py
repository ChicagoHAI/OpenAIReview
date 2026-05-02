"""REVIEWER3 system: closed-source HTTP API.

Wraps `reviewer3_adapter.py` (HTTP submit/poll/normalize) behind the unified
`System` protocol. Single bucket because there's no model selector.
"""

from __future__ import annotations

import json
from pathlib import Path

from . import reviewer3_adapter
from ._base import CellKey, System, ReviewJob, ReviewResult


REVIEWER3_SLUG = reviewer3_adapter.REVIEWER3_SLUG


def _has_content(out_json: Path) -> bool:
    try:
        existing = json.loads(out_json.read_text())
    except Exception:
        return False
    methods = existing.get("methods") or {}
    return bool(methods) and any(m.get("comments") for m in methods.values())


class Reviewer3System(System):
    name = "reviewer3"

    def build_jobs(self, units, cfg, results_dir):
        domain = results_dir.name
        out: list[tuple[CellKey, ReviewJob]] = []
        for u in units:
            if not u.staged_corrupted.exists():
                continue
            review_dir = results_dir / REVIEWER3_SLUG / u.error_type / REVIEWER3_SLUG / u.paper_label / "review"
            review_dir.mkdir(parents=True, exist_ok=True)
            out_json = review_dir / f"{u.staged_corrupted.stem}.json"
            if out_json.exists():
                if _has_content(out_json):
                    continue
                out_json.unlink()
            tag = f"{domain}/{u.paper_label}/{u.error_type}/{REVIEWER3_SLUG}"
            job = ReviewJob(
                tag=tag, out_json=out_json, review_dir=review_dir,
                paper_label=f"{u.error_type}/{u.paper_label}",
                payload={"paper": u.staged_corrupted},
            )
            out.append(((REVIEWER3_SLUG,), job))
        return out

    def run_jobs(self, cell_key, jobs, parallel):
        if not jobs:
            return []
        cfg = reviewer3_adapter.config_from_env()
        # cfg overrides come from the caller via run_jobs_with_cfg; default cfg is fine here.
        adapter_jobs = [
            reviewer3_adapter.Reviewer3Job(
                paper=j.payload["paper"],
                out_json=j.out_json,
                paper_label=j.tag,
            )
            for j in jobs
        ]
        results = reviewer3_adapter.run_reviewer3_review(adapter_jobs, parallel=parallel, cfg=cfg)
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
