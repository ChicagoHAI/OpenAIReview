"""System adapter protocol shared by the unified `run_benchmark.py` runner.

A system is anything that turns a staged corrupted paper into a JSON file
matching the schema `openaireview score` consumes. Each concrete system
(openaireview, coarse, reviewer3) implements this protocol; the runner owns
config loading, prepare, scheduling, score, and report stages.

Scheduling model
----------------

Every system produces a flat list of (cell_key, ReviewJob) tuples from
`build_jobs`. The runner buckets jobs by `cell_key` and runs each bucket with
`parallel_per_cell` workers. This unifies:

  * OAIR's per-(model, method) cells (cell_key = (model, method))
  * COARSE's per-model flat pool (cell_key = (model,))
  * REVIEWER3's single-bucket pool (cell_key = ("reviewer3",))

Multi-domain runs feed jobs from every config into the same bucket map, so
workers stay busy across domain boundaries — exactly the behavior the previous
`run_all_domains.py` provided.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


CellKey = tuple[str, ...]


@dataclass
class ReviewJob:
    """One unit of review work. `payload` is system-specific."""
    tag: str                                # e.g. "<domain>/<paper>/<err>/<slug>[/<method>]"
    out_json: Path                          # canonical "review complete" marker
    review_dir: Path                        # directory `out_json` lives in
    paper_label: str                        # "<error_type>/<paper_label>"
    payload: dict = field(default_factory=dict)


@dataclass
class ReviewResult:
    job: ReviewJob
    ok: bool
    elapsed_s: float
    error: str = ""


@dataclass
class CostReport:
    rows: list[dict]                        # [{"unit": "...", "model_slug": "...", "cost_usd": ...}, ...]
    total_usd: float


class System(ABC):
    """Adapter protocol for a single review backend."""

    name: str                               # registry key: "openaireview" | "coarse" | "reviewer3"

    @abstractmethod
    def build_jobs(
        self,
        units: list[Any],                   # _prepare.Unit
        cfg: dict,
        results_dir: Path,
    ) -> list[tuple[CellKey, ReviewJob]]:
        """Return (cell_key, job) pairs for each (unit × model × method) combo."""

    @abstractmethod
    def run_jobs(
        self,
        cell_key: CellKey,
        jobs: list[ReviewJob],
        parallel: int,
    ) -> list[ReviewResult]:
        """Execute jobs in this cell with `parallel` workers."""

    # Optional hooks with sane defaults --------------------------------------

    def is_review_complete(self, review_dir: Path) -> bool:
        """Return True if `review_dir` already holds a usable review."""
        return any(review_dir.glob("*.json"))

    def pick_review_for_score(self, review_dir: Path) -> Path | None:
        """Choose the JSON to feed into `openaireview score`."""
        candidates = list(review_dir.glob("*.json"))
        return max(candidates, key=lambda p: p.stat().st_mtime, default=None)

    def supports_cost_estimate(self) -> bool:
        return False

    def estimate_cost(
        self,
        units: list[Any],
        cfg: dict,
        results_dir: Path,
        parallel: int,
    ) -> CostReport:
        raise NotImplementedError(
            f"{self.name} does not implement cost estimation"
        )
