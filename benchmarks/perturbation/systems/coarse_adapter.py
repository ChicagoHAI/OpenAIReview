"""Adapter that runs `coarse` through the perturbation benchmark pipeline.

Each (paper, model) pair shells out to coarse_driver.py (inside coarse's
venv) and writes a JSON file with the schema that `openaireview score`
consumes. Supports parallel execution across pairs.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

from .progress import heartbeat, stream_prefixed


_HERE = Path(__file__).resolve().parent


def _resolve_coarse_python() -> Path | None:
    """Resolve the path to coarse's venv python.

    Reads `COARSE_PYTHON` (full path to the binary) or `COARSE_PATH` (root of
    a coarse checkout containing `.venv/bin/python`). Returns None if neither
    is set; callers must check existence and emit a helpful error.
    """
    explicit = os.environ.get("COARSE_PYTHON")
    if explicit:
        return Path(explicit)
    root = os.environ.get("COARSE_PATH")
    if root:
        return Path(root) / ".venv" / "bin" / "python"
    return None


DEFAULT_COARSE_PYTHON: Path | None = _resolve_coarse_python()


def model_slug(model: str) -> str:
    return model.split("/")[-1]


@dataclass
class Job:
    paper: Path                # path to *_corrupted.md
    model: str                 # e.g. "google/gemini-3-flash-preview"
    out_json: Path             # where the driver writes the pipeline JSON
    paper_label: str           # e.g. "paper_001"


@dataclass
class JobResult:
    job: Job
    ok: bool
    elapsed_s: float
    return_code: int
    error: str = ""


def _run_driver(
    job: Job,
    *,
    driver: Path,
    coarse_python: Path,
    heartbeat_interval: float,
) -> JobResult:
    """Run coarse_driver.py for one (paper, model) pair with heartbeat logs."""
    job.out_json.parent.mkdir(parents=True, exist_ok=True)
    tag = f"coarse/{model_slug(job.model)}/{job.paper_label}"
    cmd = [
        str(coarse_python),
        str(driver),
        "--paper", str(job.paper),
        "--model", job.model,
        "--out", str(job.out_json),
    ]
    print(f"[{tag}] starting: {job.paper.name}", file=sys.stderr, flush=True)
    start = time.time()
    with heartbeat(tag, interval=heartbeat_interval):
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ},
        )
        stream_prefixed(proc, tag)
        rc = proc.wait()
    elapsed = time.time() - start
    ok = (rc == 0 and job.out_json.exists())
    status = "done" if ok else "FAILED"
    print(f"[{tag}] {status} in {elapsed:.0f}s (rc={rc})", file=sys.stderr, flush=True)
    return JobResult(job=job, ok=ok, elapsed_s=elapsed, return_code=rc,
                     error="" if ok else f"rc={rc}")


def run_coarse_review(
    jobs: list[Job],
    *,
    parallel: int = 1,
    coarse_python: Path | None = DEFAULT_COARSE_PYTHON,
    heartbeat_interval: float = 30.0,
) -> list[JobResult]:
    """Execute the given jobs, up to `parallel` concurrently. Returns one result per job.

    Parallel work is dispatched across (paper, model) pairs since each coarse
    process is independent. coarse internally parallelizes across sections,
    so the outer pool multiplies throughput against external LLM APIs.
    """
    driver = _HERE / "coarse_driver.py"
    if not driver.exists():
        raise FileNotFoundError(f"coarse_driver not found at {driver}")
    if coarse_python is None:
        raise RuntimeError(
            "coarse python not configured. Set $COARSE_PATH (root of your coarse "
            "checkout) or $COARSE_PYTHON (full path to its venv python). "
            "See competitors/README.md."
        )
    if not coarse_python.exists():
        raise FileNotFoundError(
            f"coarse venv python not found at {coarse_python}. "
            "Run `uv sync` in the coarse repo first (see competitors/README.md)."
        )

    if parallel <= 1 or len(jobs) <= 1:
        return [
            _run_driver(j, driver=driver, coarse_python=coarse_python,
                        heartbeat_interval=heartbeat_interval)
            for j in jobs
        ]

    results: list[JobResult] = []
    with ThreadPoolExecutor(max_workers=parallel) as pool:
        futures = {
            pool.submit(_run_driver, j, driver=driver, coarse_python=coarse_python,
                        heartbeat_interval=heartbeat_interval): j
            for j in jobs
        }
        for fut in as_completed(futures):
            results.append(fut.result())
    # keep deterministic order matching input
    order = {id(j): i for i, j in enumerate(jobs)}
    results.sort(key=lambda r: order[id(r.job)])
    return results


# ---------------------------------------------------------------------------
# Cost estimation
# ---------------------------------------------------------------------------

@dataclass
class CostJob:
    paper: Path
    model: str
    out_json: Path
    paper_label: str


@dataclass
class CostResult:
    job: CostJob
    ok: bool
    total_cost_usd: float
    token_estimate: int
    error: str = ""


def _run_cost_driver(
    job: CostJob,
    *,
    driver: Path,
    coarse_python: Path,
) -> CostResult:
    job.out_json.parent.mkdir(parents=True, exist_ok=True)
    tag = f"cost/{model_slug(job.model)}/{job.paper_label}"
    cmd = [
        str(coarse_python), str(driver),
        "--paper", str(job.paper),
        "--model", job.model,
        "--out", str(job.out_json),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True,
                                env={**os.environ}, timeout=300)
    except subprocess.TimeoutExpired:
        return CostResult(job=job, ok=False, total_cost_usd=0.0,
                          token_estimate=0, error="timeout")
    if result.returncode != 0 or not job.out_json.exists():
        return CostResult(job=job, ok=False, total_cost_usd=0.0,
                          token_estimate=0,
                          error=result.stderr[-2000:] if result.stderr else "unknown")
    import json
    data = json.loads(job.out_json.read_text())
    if "error" in data:
        return CostResult(job=job, ok=False, total_cost_usd=0.0,
                          token_estimate=0, error=data["error"][-2000:])
    print(f"[{tag}] ${data['total_cost_usd']:.4f} "
          f"(tokens≈{data.get('token_estimate', 0)})",
          file=sys.stderr, flush=True)
    return CostResult(
        job=job, ok=True,
        total_cost_usd=data["total_cost_usd"],
        token_estimate=data.get("token_estimate", 0),
    )


def estimate_coarse_cost(
    jobs: list[CostJob],
    *,
    parallel: int = 4,
    coarse_python: Path | None = DEFAULT_COARSE_PYTHON,
) -> list[CostResult]:
    """Run the cost-estimator driver on each pair. Cheap: no LLM calls."""
    driver = _HERE / "cost_driver.py"
    if not driver.exists():
        raise FileNotFoundError(f"cost_driver not found at {driver}")
    if not coarse_python.exists():
        raise FileNotFoundError(
            f"coarse venv python not found at {coarse_python}. "
            "Run `uv sync` in the coarse repo first."
        )

    if parallel <= 1 or len(jobs) <= 1:
        return [_run_cost_driver(j, driver=driver, coarse_python=coarse_python)
                for j in jobs]

    results: list[CostResult] = []
    with ThreadPoolExecutor(max_workers=parallel) as pool:
        futures = {
            pool.submit(_run_cost_driver, j, driver=driver, coarse_python=coarse_python): j
            for j in jobs
        }
        for fut in as_completed(futures):
            results.append(fut.result())
    order = {id(j): i for i, j in enumerate(jobs)}
    results.sort(key=lambda r: order[id(r.job)])
    return results
