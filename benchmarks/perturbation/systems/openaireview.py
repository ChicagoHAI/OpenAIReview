"""OAIR system: shells out to `openaireview review` per (unit, model, method)."""

from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from ._base import CellKey, System, ReviewJob, ReviewResult


REVIEW_TIMEOUT_SEC = 2100  # 35 min — kill stuck reviews so the cell pool can advance


def _model_slug(model: str) -> str:
    return model.split("/")[-1]


def _openaireview_bin() -> str:
    here = Path(sys.executable).parent / "openaireview"
    return str(here) if here.exists() else "openaireview"


_print_lock = threading.Lock()


def _pump(stream, prefix: str) -> None:
    for line in iter(stream.readline, ""):
        if not line:
            break
        with _print_lock:
            sys.stdout.write(f"{prefix}{line}" if line.endswith("\n") else f"{prefix}{line}\n")
            sys.stdout.flush()
    stream.close()


def _run_review(job: ReviewJob, timeout: int = REVIEW_TIMEOUT_SEC) -> ReviewResult:
    cmd = job.payload["cmd"]
    if cmd and cmd[0] == "openaireview":
        cmd = [_openaireview_bin()] + cmd[1:]
    env = {**os.environ, "PYTHONUNBUFFERED": "1"}
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, bufsize=1, env=env,
    )
    t_out = threading.Thread(target=_pump, args=(proc.stdout, f"[{job.tag}] "), daemon=True)
    t_err = threading.Thread(target=_pump, args=(proc.stderr, f"[{job.tag}][err] "), daemon=True)
    t_out.start(); t_err.start()
    start = time.time()
    try:
        rc = proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill(); proc.wait()
        t_out.join(timeout=2); t_err.join(timeout=2)
        elapsed = time.time() - start
        return ReviewResult(job, ok=False, elapsed_s=elapsed,
                            error=f"timeout after {timeout}s")
    t_out.join(timeout=2); t_err.join(timeout=2)
    elapsed = time.time() - start
    return ReviewResult(job, ok=(rc == 0), elapsed_s=elapsed,
                        error="" if rc == 0 else f"exit {rc}")


class OpenAIReviewSystem(System):
    name = "openaireview"

    def build_jobs(self, units, cfg, results_dir):
        models = cfg.get("models") or cfg.get("review_models") or []
        methods = cfg.get("methods") or cfg.get("review_methods") or []
        if not models or not methods:
            raise ValueError("openaireview system requires `models` and `methods` in config")
        domain = results_dir.name
        out: list[tuple[CellKey, ReviewJob]] = []
        for u in units:
            if not u.staged_corrupted.exists():
                continue
            for model in models:
                for method in methods:
                    review_dir = results_dir / _model_slug(model) / u.error_type / method / u.paper_label / "review"
                    review_dir.mkdir(parents=True, exist_ok=True)
                    if self.is_review_complete(review_dir):
                        continue
                    tag = f"{domain}/{u.paper_label}/{u.error_type}/{_model_slug(model)}/{method}"
                    cmd = [
                        "openaireview", "review", str(u.staged_corrupted),
                        "--method", method,
                        "--output-dir", str(review_dir),
                        "--model", model,
                    ]
                    job = ReviewJob(
                        tag=tag,
                        out_json=review_dir / f"{u.staged_corrupted.stem}.json",
                        review_dir=review_dir,
                        paper_label=f"{u.error_type}/{u.paper_label}",
                        payload={"cmd": cmd, "model": model, "method": method},
                    )
                    out.append(((model, method), job))
        return out

    def run_jobs(self, cell_key, jobs, parallel):
        if not jobs:
            return []
        if parallel <= 1 or len(jobs) == 1:
            return [_run_review(j) for j in jobs]
        results: list[ReviewResult] = []
        with ThreadPoolExecutor(max_workers=parallel) as pool:
            futures = {pool.submit(_run_review, j): j for j in jobs}
            for fut in as_completed(futures):
                results.append(fut.result())
        return results
