#!/usr/bin/env python
"""Batch runner for the accept-vs-reject conference study.

For each (paper, model) combination in manifest.json, shell out to
`openaireview review` in progressive mode. Results merge into one JSON
per paper under the results dir, with method keys progressive__<model>
AND progressive_original__<model> (the CLI mod from cli.py:cmd_review
writes both in a single run).

Idempotent: if the result JSON already contains the expected method keys
for a (paper, model) combo, skip it. Logs each run to <results>/run_log.jsonl.

Run knobs (max-pages, max-tokens, timeout, parallelism, results-subdir
name) are read from a YAML config (--config), with CLI flags overriding
individual values.

Usage:
    python run_study.py --config configs/baseline.yaml
    python run_study.py --config configs/baseline.yaml --dry-run
    python run_study.py --config configs/baseline.yaml --paper iclr24-acc-vit-need-registers
    python run_study.py --max-pages 30   # ad-hoc run without a config
"""
from __future__ import annotations

import argparse
import json
import os
import queue
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent

# Defaults — overridden by YAML config and/or CLI flags in main().
DEFAULT_RESULTS_BASE = HERE / "results"
DEFAULT_MAX_PAGES = 20
DEFAULT_MAX_TOKENS = 20_000
DEFAULT_TIMEOUT_SEC = 60 * 60  # 60 min/run
# Parallelism: max N concurrent runs *per model* (to respect each model's
# OpenRouter rate-limit pool independently). Total in-flight is at most
# MAX_PER_MODEL * len(models). Default 2 per model -> 6 in flight for 3 models.
DEFAULT_MAX_PER_MODEL = 2

# Runtime values — populated in main() from (defaults < YAML < CLI).
RESULTS_DIR: Path = DEFAULT_RESULTS_BASE
LOG_FILE: Path = DEFAULT_RESULTS_BASE / "run_log.jsonl"
MAX_PAGES: int = DEFAULT_MAX_PAGES
MAX_TOKENS: int = DEFAULT_MAX_TOKENS
TIMEOUT_SEC: int = DEFAULT_TIMEOUT_SEC
MAX_PER_MODEL: int = DEFAULT_MAX_PER_MODEL
METHOD: str = "progressive"

# Lock printing + log writes so concurrent workers don't interleave bytes.
_print_lock = threading.Lock()
_log_lock = threading.Lock()

# Resolve the openaireview CLI binary. Prefer the project venv so we get
# Python 3.12 + the freshly-modified cli.py instead of whatever is on PATH.
_VENV_BIN = HERE.parent.parent / ".venv" / "bin" / "openaireview"
OPENAIREVIEW_BIN = str(_VENV_BIN) if _VENV_BIN.exists() else "openaireview"


def model_short(model: str) -> str:
    return model.split("/")[-1] if "/" in model else model


def already_done(slug: str, model: str) -> bool:
    """Return True if results/<slug>.json already has the expected method keys.

    progressive runs also emit `progressive_original__<short>` (pre-consolidation
    comments, see cli.py:cmd_review); zero_shot only emits `zero_shot__<short>`.
    """
    out = RESULTS_DIR / f"{slug}.json"
    if not out.exists():
        return False
    try:
        data = json.loads(out.read_text())
    except json.JSONDecodeError:
        return False
    methods = data.get("methods", {})
    short = model_short(model)
    if METHOD == "progressive":
        needed = {f"progressive__{short}", f"progressive_original__{short}"}
    else:
        needed = {f"{METHOD}__{short}"}
    return needed.issubset(methods.keys())


def log_run(entry: dict) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with _log_lock, LOG_FILE.open("a") as f:
        f.write(json.dumps(entry) + "\n")


def safe_print(msg: str) -> None:
    with _print_lock:
        print(msg, flush=True)


def resolve_pdf_path(paper: dict) -> Path:
    """Locate the paper's PDF on disk.

    New-style manifests set `pdf_path` explicitly (relative to HERE).
    Old-style (manifest.json) used `papers/<group>/<slug>.pdf`.
    """
    if paper.get("pdf_path"):
        return HERE / paper["pdf_path"]
    return HERE / "papers" / paper.get("group", "") / f"{paper['slug']}.pdf"


def run_one(paper: dict, model: str, dry_run: bool = False) -> dict:
    pdf = resolve_pdf_path(paper)
    if not pdf.exists():
        return {"slug": paper["slug"], "model": model, "ok": False,
                "error": f"pdf not found: {pdf}"}

    cmd = [
        OPENAIREVIEW_BIN, "review", str(pdf),
        "--method", METHOD,
        "--model", model,
        "--provider", "openrouter",
        "--output-dir", str(RESULTS_DIR),
        "--name", paper["slug"],
        "--max-pages", str(MAX_PAGES),
        "--max-tokens", str(MAX_TOKENS),
    ]

    if dry_run:
        print("  [dry] " + " ".join(cmd))
        return {"slug": paper["slug"], "model": model, "ok": True, "dry": True}

    started = datetime.now(timezone.utc).isoformat()
    t0 = time.time()
    try:
        proc = subprocess.run(
            cmd,
            timeout=TIMEOUT_SEC,
            capture_output=True,
            text=True,
            check=False,
        )
        ok = proc.returncode == 0 and already_done(paper["slug"], model)
        entry = {
            "slug": paper["slug"],
            "group": paper.get("group"),
            "model": model,
            "started": started,
            "duration_sec": round(time.time() - t0, 1),
            "exit_code": proc.returncode,
            "ok": ok,
            "stdout_tail": proc.stdout[-1500:],
            "stderr_tail": proc.stderr[-1500:],
        }
    except subprocess.TimeoutExpired as e:
        entry = {
            "slug": paper["slug"],
            "group": paper.get("group"),
            "model": model,
            "started": started,
            "duration_sec": round(time.time() - t0, 1),
            "ok": False,
            "error": f"TIMEOUT after {TIMEOUT_SEC}s",
            "stdout_tail": (e.stdout or b"")[-1500:].decode("utf-8", "replace") if e.stdout else "",
        }
    log_run(entry)
    return entry


def load_config(path: str) -> dict:
    """Load a YAML run-config file. Returns {} if path is None."""
    if not path:
        return {}
    cfg_path = Path(path)
    if not cfg_path.is_absolute():
        # Try as-given (cwd-relative), then relative to this script.
        cfg_path = cfg_path if cfg_path.exists() else HERE / path
    if not cfg_path.exists():
        sys.exit(f"config file not found: {path}")
    with cfg_path.open() as f:
        return yaml.safe_load(f) or {}


def main() -> None:
    global RESULTS_DIR, LOG_FILE, MAX_PAGES, MAX_TOKENS, TIMEOUT_SEC, MAX_PER_MODEL, METHOD

    ap = argparse.ArgumentParser()
    ap.add_argument("--config", help="YAML config file with run parameters.")
    ap.add_argument("--name", help="Experiment name. Results -> <results>/<name>/. "
                                   "Overrides config's 'name'.")
    ap.add_argument("--manifest", type=Path,
                    help="Path to manifest JSON. Overrides config's 'manifest' "
                         "and the default manifest.json.")
    ap.add_argument("--method", choices=["progressive", "zero_shot"], default=None,
                    help="Review method. Overrides config's 'method' "
                         "(default: progressive).")
    ap.add_argument("--max-pages", type=int, default=None,
                    help=f"Max pages passed to CLI (default: {DEFAULT_MAX_PAGES}).")
    ap.add_argument("--max-tokens", type=int, default=None,
                    help=f"Max tokens passed to CLI (default: {DEFAULT_MAX_TOKENS}).")
    ap.add_argument("--timeout-sec", type=int, default=None,
                    help=f"Per-run subprocess timeout in seconds "
                         f"(default: {DEFAULT_TIMEOUT_SEC}).")
    ap.add_argument("--max-per-model", type=int, default=None,
                    help=f"Concurrent runs per model "
                         f"(default: {DEFAULT_MAX_PER_MODEL}).")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print what would run, do not call the API.")
    ap.add_argument("--paper", help="Run only this paper slug.")
    ap.add_argument("--model", help="Run only this model.")
    ap.add_argument("--limit", type=int,
                    help="Run only the first N papers in the manifest.")
    ap.add_argument("--force", action="store_true",
                    help="Re-run even if already complete.")
    args = ap.parse_args()

    # Resolve run knobs: CLI flag > YAML config > built-in default.
    cfg = load_config(args.config)
    name = args.name or cfg.get("name")
    METHOD = args.method or cfg.get("method", "progressive")
    MAX_PAGES = args.max_pages if args.max_pages is not None \
        else cfg.get("max_pages", DEFAULT_MAX_PAGES)
    MAX_TOKENS = args.max_tokens if args.max_tokens is not None \
        else cfg.get("max_tokens", DEFAULT_MAX_TOKENS)
    TIMEOUT_SEC = args.timeout_sec if args.timeout_sec is not None \
        else cfg.get("timeout_sec", DEFAULT_TIMEOUT_SEC)
    MAX_PER_MODEL = args.max_per_model if args.max_per_model is not None \
        else cfg.get("max_per_model", DEFAULT_MAX_PER_MODEL)

    RESULTS_DIR = DEFAULT_RESULTS_BASE / name if name else DEFAULT_RESULTS_BASE
    LOG_FILE = RESULTS_DIR / "run_log.jsonl"

    manifest_path = args.manifest or Path(cfg.get("manifest", "manifest.json"))
    if not manifest_path.is_absolute():
        manifest_path = HERE / manifest_path
    manifest = json.loads(manifest_path.read_text())
    papers = manifest["papers"]
    models = cfg.get("models") or manifest.get("models", [])

    # Skip papers that have no PDF on disk (e.g. download failures).
    papers = [
        p for p in papers
        if resolve_pdf_path(p).exists()
    ]

    if args.paper:
        papers = [p for p in papers if p["slug"] == args.paper]
        if not papers:
            sys.exit(f"unknown paper slug: {args.paper}")
    if args.model:
        if args.model not in models:
            sys.exit(f"unknown model: {args.model}  (manifest: {models})")
        models = [args.model]
    if args.limit:
        papers = papers[:args.limit]

    if not args.dry_run and not os.environ.get("OPENROUTER_API_KEY"):
        sys.exit("OPENROUTER_API_KEY is not set in env. Set it before running.")

    todo = []
    skipped = []
    for p in papers:
        for m in models:
            if not args.force and already_done(p["slug"], m):
                skipped.append((p["slug"], m))
            else:
                todo.append((p, m))

    print(f"Binary:       {OPENAIREVIEW_BIN}")
    if args.config:
        print(f"Config:       {args.config}")
    if name:
        print(f"Experiment:   {name}")
    print(f"Manifest:     {manifest_path}")
    print(f"Method:       {METHOD}")
    print(f"Results dir:  {RESULTS_DIR}")
    print(f"Caps:         {MAX_PAGES} pages, {MAX_TOKENS} tokens, "
          f"{TIMEOUT_SEC}s timeout")
    print(f"Combinations: {len(papers)} papers x {len(models)} models = "
          f"{len(papers)*len(models)} total")
    print(f"  already complete: {len(skipped)}")
    print(f"  to run:           {len(todo)}")
    print(f"  parallelism:      {MAX_PER_MODEL} per model "
          f"(<= {MAX_PER_MODEL * len(models)} concurrent)\n", flush=True)

    if args.dry_run:
        for p, m in todo:
            run_one(p, m, dry_run=True)
        return

    # Design:
    #   * One queue per model. Per-model concurrency is naturally capped at
    #     MAX_PER_MODEL by spawning that many worker threads per queue.
    #   * Per-paper locks prevent two threads (necessarily from different
    #     models) from concurrently rewriting the same paper JSON file —
    #     cli.py merges by read-modify-write, not append, so concurrent
    #     writes would clobber each other.
    paper_locks: dict[str, threading.Lock] = {p["slug"]: threading.Lock()
                                              for p in papers}
    model_queues: dict[str, "queue.Queue[tuple[dict,str] | None]"] = {
        m: queue.Queue() for m in models
    }
    for paper, model in todo:
        model_queues[model].put((paper, model))

    counter = {"done": 0, "ok": 0, "fail": 0}
    counter_lock = threading.Lock()
    total = len(todo)
    t_batch_start = time.time()

    def worker(model: str) -> None:
        q = model_queues[model]
        while True:
            task = q.get()
            if task is None:
                q.task_done()
                return
            paper, _model = task
            lock = paper_locks[paper["slug"]]
            # Non-blocking acquire. If another model is currently writing
            # to this paper's JSON, requeue at the back and try the next
            # task instead of stalling this worker thread.
            if not lock.acquire(blocking=False):
                q.task_done()
                q.put(task)
                time.sleep(0.5)  # tiny backoff to avoid hot-looping
                continue
            try:
                t_start = time.time()
                safe_print(f"  >>> START  {paper['slug']:42s} | {model_short(model)}")
                result = run_one(paper, model)
                dur = time.time() - t_start
                with counter_lock:
                    counter["done"] += 1
                    if result.get("ok"):
                        counter["ok"] += 1
                        tag = "OK  "
                    else:
                        counter["fail"] += 1
                        tag = "FAIL"
                    done = counter["done"]
                extra = ""
                if not result.get("ok"):
                    extra = (f"  exit={result.get('exit_code')}  "
                             f"err={result.get('error','')}  "
                             f"stderr_tail={result.get('stderr_tail','')[:120]}")
                safe_print(f"  [{done:>2}/{total}] {tag} "
                           f"{paper['slug']:42s} | {model_short(model):25s}  "
                           f"{dur:5.0f}s{extra}")
            finally:
                lock.release()
                q.task_done()

    # Spawn MAX_PER_MODEL worker threads per model.
    threads: list[threading.Thread] = []
    for m in models:
        for _ in range(MAX_PER_MODEL):
            t = threading.Thread(target=worker, args=(m,), daemon=True)
            t.start()
            threads.append(t)

    # Wait for all queues to drain.
    for q in model_queues.values():
        q.join()
    # Send sentinels to terminate workers.
    for m in models:
        for _ in range(MAX_PER_MODEL):
            model_queues[m].put(None)
    for t in threads:
        t.join()

    elapsed = time.time() - t_batch_start
    print(f"\nDone. ok={counter['ok']} fail={counter['fail']}  "
          f"wall={elapsed/60:.1f} min", flush=True)
    print(f"Logs: {LOG_FILE}", flush=True)


if __name__ == "__main__":
    main()
