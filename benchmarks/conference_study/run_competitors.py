#!/usr/bin/env python
"""Batch runner for competitor review systems on the conference_study papers.

Runs `competitors/<name>_adapter.py` in-process against each (paper, model)
combo in manifest.json, and merges the output into `results/<name>/<slug>.json`
using openaireview's result-JSON schema (so the viz + report tooling Just
Works). Adapters decide how to invoke their competitor; this orchestrator
handles paper iteration, per-model parallelism, idempotency, paragraph-index
assignment, and logging.

Pattern mirrors `run_study.py` (per-model queues, per-paper locks, JSONL log).
The two differ in only one place: this script calls `adapter.review(...)` in
the worker thread instead of shelling out to the openaireview CLI.

Usage:
    python run_competitors.py --config configs/coarse.yaml
    python run_competitors.py --config configs/coarse.yaml --dry-run
    python run_competitors.py --config configs/coarse.yaml --paper iclr24-acc-vit-need-registers
    python run_competitors.py --config configs/coarse.yaml --model z-ai/glm-4.6
    python run_competitors.py --config configs/coarse.yaml --force
"""
from __future__ import annotations

import argparse
import json
import os
import queue
import sys
import threading
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent

# Make `reviewer` + `competitors` importable when run as a plain script.
sys.path.insert(0, str(HERE.parent.parent / "src"))
sys.path.insert(0, str(HERE))

from competitors import get_adapter  # noqa: E402
from competitors.helpers import build_method_data, merge_into_paper_json, model_short  # noqa: E402
from reviewer.parsers import parse_document  # noqa: E402
from reviewer.utils import split_into_paragraphs  # noqa: E402

DEFAULT_RESULTS_BASE = HERE / "results"
DEFAULT_TIMEOUT_SEC = 60 * 60
DEFAULT_MAX_PER_MODEL = 2
DEFAULT_MAX_PAGES = 20

_print_lock = threading.Lock()
_log_lock = threading.Lock()

# Populated in main() from (defaults < YAML < CLI).
RESULTS_DIR: Path = DEFAULT_RESULTS_BASE
LOG_FILE: Path = DEFAULT_RESULTS_BASE / "run_log.jsonl"
TIMEOUT_SEC: int = DEFAULT_TIMEOUT_SEC
MAX_PER_MODEL: int = DEFAULT_MAX_PER_MODEL
MAX_PAGES: int = DEFAULT_MAX_PAGES


def safe_print(msg: str) -> None:
    with _print_lock:
        print(msg, flush=True)


def log_run(entry: dict) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with _log_lock, LOG_FILE.open("a") as f:
        f.write(json.dumps(entry) + "\n")


def already_done(slug: str, method_key: str) -> bool:
    out = RESULTS_DIR / f"{slug}.json"
    if not out.exists():
        return False
    try:
        data = json.loads(out.read_text())
    except json.JSONDecodeError:
        return False
    return method_key in data.get("methods", {})


def resolve_pdf_path(paper: dict) -> Path:
    """Locate the paper's PDF on disk.

    New-style manifests set `pdf_path` (relative to HERE).
    Old-style used `papers/<group>/<slug>.pdf`.
    """
    if paper.get("pdf_path"):
        return HERE / paper["pdf_path"]
    return HERE / "papers" / paper.get("group", "") / f"{paper['slug']}.pdf"


def run_one(paper: dict, model: str, adapter, cfg: dict, dry_run: bool = False) -> dict:
    pdf = resolve_pdf_path(paper)
    method_key = adapter.method_key(model)
    if not pdf.exists():
        return {
            "slug": paper["slug"], "model": model, "method_key": method_key,
            "ok": False, "error": f"pdf not found: {pdf}",
        }

    if dry_run:
        print(f"  [dry] {adapter.name}  {paper['slug']:42s} | "
              f"{model_short(model):25s} -> {method_key}")
        return {"slug": paper["slug"], "model": model, "method_key": method_key,
                "ok": True, "dry": True}

    started = datetime.now(timezone.utc).isoformat()
    t0 = time.time()
    entry: dict = {
        "slug": paper["slug"],
        "group": paper.get("group", ""),
        "model": model,
        "competitor": adapter.name,
        "method_key": method_key,
        "started": started,
    }
    try:
        # Parse the PDF with the same parser openaireview uses so paragraph
        # granularity matches the progressive__* entries in the same file.
        title, content, _was_ocr = parse_document(pdf, max_pages=MAX_PAGES)
        paragraphs = split_into_paragraphs(content)

        review = adapter.review(pdf, model, cfg)

        method_data = build_method_data(
            review=review,
            method_key=method_key,
            method_label=f"{adapter.name.title()} ({model_short(model)})",
            paragraphs=paragraphs,
        )

        out_file = RESULTS_DIR / f"{paper['slug']}.json"
        merge_into_paper_json(
            out_file=out_file,
            slug=paper["slug"],
            title=paper.get("title") or title,
            paragraphs=paragraphs,
            method_key=method_key,
            method_data=method_data,
        )

        entry.update({
            "duration_sec": round(time.time() - t0, 1),
            "ok": True,
            "num_comments": len(review.comments),
            "cost_usd": review.cost_usd,
            "cost_method": review.cost_method,
        })
    except Exception as exc:
        entry.update({
            "duration_sec": round(time.time() - t0, 1),
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc()[-2000:],
        })
    log_run(entry)
    return entry


def load_config(path: str) -> dict:
    if not path:
        return {}
    cfg_path = Path(path)
    if not cfg_path.is_absolute():
        cfg_path = cfg_path if cfg_path.exists() else HERE / path
    if not cfg_path.exists():
        sys.exit(f"config file not found: {path}")
    with cfg_path.open() as f:
        return yaml.safe_load(f) or {}


def main() -> None:
    global RESULTS_DIR, LOG_FILE, TIMEOUT_SEC, MAX_PER_MODEL, MAX_PAGES

    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, help="YAML config file (required).")
    ap.add_argument("--manifest", type=Path,
                    help="Path to manifest JSON. Overrides config's 'manifest' "
                         "and the default manifest.json.")
    ap.add_argument("--name", help="Experiment name. Overrides config's 'name'. "
                                   "Results -> results/<name>/.")
    ap.add_argument("--competitor", help="Override the competitor name from config.")
    ap.add_argument("--timeout-sec", type=int, default=None)
    ap.add_argument("--max-per-model", type=int, default=None)
    ap.add_argument("--max-pages", type=int, default=None,
                    help="Max pages passed to parse_document (for paragraph split). "
                         f"Default: {DEFAULT_MAX_PAGES}.")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--paper", help="Run only this paper slug.")
    ap.add_argument("--model", help="Run only this model (must be in manifest).")
    ap.add_argument("--force", action="store_true",
                    help="Re-run even if method_key already present.")
    args = ap.parse_args()

    cfg = load_config(args.config)
    name = args.name or cfg.get("name")
    competitor_name = args.competitor or cfg.get("competitor")
    if not competitor_name:
        sys.exit("config must specify `competitor: <name>` (or pass --competitor).")

    TIMEOUT_SEC = args.timeout_sec if args.timeout_sec is not None \
        else cfg.get("timeout_sec", DEFAULT_TIMEOUT_SEC)
    MAX_PER_MODEL = args.max_per_model if args.max_per_model is not None \
        else cfg.get("max_per_model", DEFAULT_MAX_PER_MODEL)
    MAX_PAGES = args.max_pages if args.max_pages is not None \
        else cfg.get("max_pages", DEFAULT_MAX_PAGES)

    RESULTS_DIR = DEFAULT_RESULTS_BASE / name if name else DEFAULT_RESULTS_BASE
    LOG_FILE = RESULTS_DIR / "run_log.jsonl"

    adapter = get_adapter(competitor_name)

    manifest_path = args.manifest or Path(cfg.get("manifest", "manifest.json"))
    if not manifest_path.is_absolute():
        manifest_path = HERE / manifest_path
    manifest = json.loads(manifest_path.read_text())
    papers = manifest["papers"]
    models = cfg.get("models") or manifest["models"]

    if args.paper:
        papers = [p for p in papers if p["slug"] == args.paper]
        if not papers:
            sys.exit(f"unknown paper slug: {args.paper}")
    if args.model:
        if args.model not in models:
            sys.exit(f"unknown model: {args.model}  (manifest: {models})")
        models = [args.model]

    if not args.dry_run:
        missing = [e for e in adapter.required_env if not os.environ.get(e)]
        if missing:
            sys.exit(f"missing required env vars for {competitor_name}: {missing}")

    todo = []
    skipped = []
    for p in papers:
        for m in models:
            mk = adapter.method_key(m)
            if not args.force and already_done(p["slug"], mk):
                skipped.append((p["slug"], m))
            else:
                todo.append((p, m))

    print(f"Competitor:   {competitor_name}")
    print(f"Config:       {args.config}")
    if name:
        print(f"Experiment:   {name}")
    print(f"Results dir:  {RESULTS_DIR}")
    print(f"Combinations: {len(papers)} papers x {len(models)} models = "
          f"{len(papers) * len(models)} total")
    print(f"  already complete: {len(skipped)}")
    print(f"  to run:           {len(todo)}")
    print(f"  parallelism:      {MAX_PER_MODEL} per model "
          f"(<= {MAX_PER_MODEL * len(models)} concurrent)\n", flush=True)

    if args.dry_run:
        for p, m in todo:
            run_one(p, m, adapter, cfg, dry_run=True)
        return

    # Per-model queues with per-paper locks (same pattern as run_study.py).
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
            if not lock.acquire(blocking=False):
                q.task_done()
                q.put(task)
                time.sleep(0.5)
                continue
            try:
                t_start = time.time()
                safe_print(f"  >>> START  {paper['slug']:42s} | "
                           f"{model_short(model)}")
                result = run_one(paper, model, adapter, cfg)
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
                    extra = f"  err={result.get('error', '')[:200]}"
                safe_print(f"  [{done:>2}/{total}] {tag} "
                           f"{paper['slug']:42s} | {model_short(model):25s}  "
                           f"{dur:5.0f}s{extra}")
            finally:
                lock.release()
                q.task_done()

    threads: list[threading.Thread] = []
    for m in models:
        for _ in range(MAX_PER_MODEL):
            t = threading.Thread(target=worker, args=(m,), daemon=True)
            t.start()
            threads.append(t)

    for q in model_queues.values():
        q.join()
    for m in models:
        for _ in range(MAX_PER_MODEL):
            model_queues[m].put(None)
    for t in threads:
        t.join()

    elapsed = time.time() - t_batch_start
    print(f"\nDone. ok={counter['ok']} fail={counter['fail']}  "
          f"wall={elapsed / 60:.1f} min", flush=True)
    print(f"Logs: {LOG_FILE}", flush=True)


if __name__ == "__main__":
    main()
