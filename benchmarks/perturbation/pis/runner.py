from __future__ import annotations

import argparse
import hashlib
import json
import platform
import statistics
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import __version__
from .backends import HFBackend, LLMBackend, MockBackend
from .evaluator import PISEvaluator, PISResult, ScalarConfidenceEvaluator
from .gold_io import load_gold_set
from .inputs import (FEATURE_SET_VERSION, VerifierInput, build_verifier_input,
                     load_context_file)
from .prompts import (BINARY_PROMPT_VERSION, PROMPT_VERSION, SCALAR_PROMPT_VERSION,
                      build_binary_prompt)

TASKS = ("pis", "scalar_confidence", "binary_logit")


@dataclass
class RunnerConfig:
    gold_set: str
    task: str
    out_dir: str
    model_id: str = "Qwen/Qwen2.5-7B-Instruct"
    revision: Optional[str] = None
    backend_kind: str = "hf"            # hf | mock
    quantization: str = "nf4"           # nf4 | none
    dtype: str = "float16"              # T4 (Turing) has no bfloat16
    device: str = "cuda:0"
    batch_size: int = 8
    max_new_tokens: int = 768
    max_retries: int = 2
    context_file: Optional[str] = None
    limit: Optional[int] = None
    force: bool = False
    seed: int = 0
    mock_responses: Optional[str] = None
    use_chat_template: bool = True      # instruct models: keep True


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _input_dict(vin: VerifierInput) -> Dict[str, Any]:
    return {"error_type": vin.error_type, "original": vin.original,
            "perturbed": vin.perturbed, "contradicts_quote": vin.contradicts_quote,
            "quote_source": vin.quote_source,
            "surrounding_context": vin.surrounding_context,
            "related_passages": list(vin.related_passages)}


def _library_versions() -> Dict[str, Any]:
    out: Dict[str, Any] = {"python": platform.python_version()}
    for name in ("torch", "transformers", "bitsandbytes", "numpy", "huggingface_hub"):
        try:
            mod = __import__(name)
            out[name] = getattr(mod, "__version__", "unknown")
        except Exception:
            out[name] = None
    return out


def _device_name() -> str:
    try:
        import torch
        return torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu-or-mock"


def _width_stats(widths: List[float]) -> Optional[Dict[str, Any]]:
    if not widths:
        return None
    return {"n": len(widths), "mean": statistics.fmean(widths),
            "median": statistics.median(widths),
            "min": min(widths), "max": max(widths),
            "stdev": statistics.stdev(widths) if len(widths) > 1 else 0.0}


def run_evaluation(cfg: RunnerConfig, backend: Optional[LLMBackend] = None) -> Dict[str, Any]:
    t0 = time.time()
    if cfg.task not in TASKS:
        raise ValueError(f"unknown task {cfg.task!r}; expected one of {TASKS}")
    records, gold_report = load_gold_set(cfg.gold_set)
    context = load_context_file(cfg.context_file) if cfg.context_file else None
    inputs = [build_verifier_input(r, context_provider=context) for r in records]
    if cfg.limit:
        inputs = inputs[:cfg.limit]

    out_dir = Path(cfg.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"predictions_{cfg.task}.jsonl"
    prompt_version = {"pis": PROMPT_VERSION, "scalar_confidence": SCALAR_PROMPT_VERSION,
                      "binary_logit": BINARY_PROMPT_VERSION}[cfg.task]

    # Resolve the CONCRETE model revision before computing cache keys, so
    # cached results are tied to the exact weights, and a re-run under a
    # different quantization/dtype/chat-template config never reuses stale
    # inference outputs. NOTE: max_new_tokens/batch_size are deliberately NOT
    # in the cache key: a completed (parsed) generation is invariant to a
    # larger budget under greedy decoding, and budget-truncated outputs fail
    # to parse, hence land in status "failed" and are re-attempted anyway.
    effective_revision = cfg.revision
    resolved_revision: Optional[str] = None
    if backend is None and cfg.backend_kind == "hf":
        resolved_revision = HFBackend._resolve_revision(cfg.model_id, cfg.revision)
        if resolved_revision:
            effective_revision = resolved_revision
        else:
            print("[warn] could not resolve the model revision from the HF Hub "
                  "(offline?); cache keys and manifest fall back to the "
                  "requested revision", flush=True)

    def cache_key(vin: VerifierInput) -> str:
        payload = {
            "task": cfg.task, "model_id": cfg.model_id,
            "revision": effective_revision or "",
            "quantization": cfg.quantization, "dtype": cfg.dtype,
            "chat_template": bool(cfg.use_chat_template),
            "prompt_version": prompt_version,
            "feature_set": vin.feature_set, "uid": vin.uid,
            "input": _input_dict(vin),
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()

    # ---- resume semantics ----
    # A cached line is reusable only if its cache_key matches the current
    # configuration AND it did not end in status "failed" (a failed parse
    # carries no result, so it must be re-attempted on the next run; this also
    # lets a parser fix recover failed examples without --force). Stale lines
    # (different config / not in the current input set) are dropped so the
    # file can never accumulate duplicate uids. --force truncates the file.
    key_by_uid = {v.uid: cache_key(v) for v in inputs}
    keep_lines: List[str] = []
    kept_uids: set = set()
    dropped = {"failed": 0, "stale": 0}
    if out_path.exists() and not cfg.force:
        existing = [ln for ln in out_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        for i, ln in enumerate(existing):
            try:
                obj = json.loads(ln)
            except json.JSONDecodeError as e:
                if i == len(existing) - 1:
                    # crash-safety: a torn trailing line from an interrupted run
                    print(f"[warn] dropping torn trailing cache line in {out_path}: {e}",
                          flush=True)
                    dropped["stale"] += 1
                    continue
                raise ValueError(f"corrupt cache line {i + 1} in {out_path}: {e}") from e
            uid = obj.get("uid")
            if uid not in key_by_uid or obj.get("cache_key") != key_by_uid[uid]:
                dropped["stale"] += 1
            elif obj.get("status") == "failed":
                dropped["failed"] += 1
            else:
                if uid in kept_uids:
                    raise ValueError(
                        f"duplicate uid {uid!r} in existing cache {out_path}; "
                        "refusing to continue with an ambiguous cache")
                keep_lines.append(ln)
                kept_uids.add(uid)
        if len(keep_lines) != len(existing):
            out_path.write_text("".join(l + "\n" for l in keep_lines), encoding="utf-8")
    elif out_path.exists():  # --force: truncate so appends cannot duplicate uids
        out_path.write_text("", encoding="utf-8")
    pending = [v for v in inputs if v.uid not in kept_uids]
    n_cached = len(keep_lines)

    if backend is None:
        if cfg.backend_kind == "mock":
            responses = json.loads(Path(cfg.mock_responses).read_text(encoding="utf-8"))
            backend = MockBackend(responses)
        else:
            backend = HFBackend(cfg.model_id, revision=effective_revision,
                                device=cfg.device, quantization=cfg.quantization,
                                dtype=cfg.dtype,
                                use_chat_template=cfg.use_chat_template)

    counts: Dict[str, int] = {}
    widths: List[float] = []
    chunk_seconds: List[float] = []

    with out_path.open("a", encoding="utf-8") as fout:
        if cfg.task == "pis":
            ev = PISEvaluator(backend, max_retries=cfg.max_retries)
            for i in range(0, len(pending), cfg.batch_size):
                chunk = pending[i:i + cfg.batch_size]
                tc = time.time()
                results = ev.evaluate_batch(chunk, max_new_tokens=cfg.max_new_tokens)
                chunk_seconds.append(round(time.time() - tc, 3))
                for vin, res in zip(chunk, results):
                    r: PISResult = res
                    counts[r.status] = counts.get(r.status, 0) + 1
                    if r.interval is not None:
                        widths.append(r.interval.width)
                    line = {**r.to_dict(), "uid": vin.uid, "paper": vin.paper,
                            "perturbation_id": vin.perturbation_id, "task": "pis",
                            "cache_key": cache_key(vin)}
                    fout.write(json.dumps(line, ensure_ascii=False) + "\n")
                fout.flush()
                print(f"[pis] {min(i + len(chunk), len(pending))}/{len(pending)} "
                      f"counts={counts}", flush=True)
        elif cfg.task == "scalar_confidence":
            ev = ScalarConfidenceEvaluator(backend, max_retries=cfg.max_retries)
            for i in range(0, len(pending), cfg.batch_size):
                chunk = pending[i:i + cfg.batch_size]
                tc = time.time()
                results = ev.evaluate_batch(chunk, max_new_tokens=128)
                chunk_seconds.append(round(time.time() - tc, 3))
                for vin, res in zip(chunk, results):
                    counts[res.status] = counts.get(res.status, 0) + 1
                    line = {**res.to_dict(), "uid": vin.uid, "paper": vin.paper,
                            "perturbation_id": vin.perturbation_id,
                            "task": "scalar_confidence", "cache_key": cache_key(vin)}
                    fout.write(json.dumps(line, ensure_ascii=False) + "\n")
                fout.flush()
                print(f"[scalar] {min(i + len(chunk), len(pending))}/{len(pending)} "
                      f"counts={counts}", flush=True)
        else:  # binary_logit
            for i, vin in enumerate(pending):
                tc = time.time()
                try:
                    score = backend.score_binary(build_binary_prompt(vin))
                    status, repairs = "ok", []
                except Exception as e:  # noqa: BLE001 - tracked, never silent
                    score, status, repairs = None, "failed", [f"score_binary error: {e}"]
                chunk_seconds.append(round(time.time() - tc, 3))
                counts[status] = counts.get(status, 0) + 1
                line = {"uid": vin.uid, "paper": vin.paper,
                        "perturbation_id": vin.perturbation_id, "task": "binary_logit",
                        "cache_key": cache_key(vin), "status": status, "score": score,
                        "repairs": repairs, "model_id": cfg.model_id,
                        "prompt_version": prompt_version,
                        "feature_set": vin.feature_set}
                fout.write(json.dumps(line, ensure_ascii=False) + "\n")
                fout.flush()
                if (i + 1) % 10 == 0 or i + 1 == len(pending):
                    print(f"[binary] {i + 1}/{len(pending)} counts={counts}", flush=True)

    manifest = {
        "pis_package_version": __version__, "task": cfg.task, "model_id": cfg.model_id,
        "requested_revision": cfg.revision,
        "resolved_revision": (resolved_revision
                              or getattr(backend, "resolved_revision", None)),
        "chat_template_requested": bool(cfg.use_chat_template),
        "chat_template_applied": getattr(backend, "chat_template_applied", None),
        "quantization": cfg.quantization, "dtype": cfg.dtype, "device": cfg.device,
        "device_name": _device_name(),
        "attn_implementation": getattr(backend, "attn_implementation", None),
        "batch_size": cfg.batch_size, "max_new_tokens": cfg.max_new_tokens,
        "max_retries": cfg.max_retries, "seed": cfg.seed,
        "prompt_version": prompt_version, "feature_set": FEATURE_SET_VERSION,
        "gold_set_path": str(cfg.gold_set), "gold_set_sha256": _sha256_file(cfg.gold_set),
        "context_file": cfg.context_file, "limit": cfg.limit,
        "library_versions": _library_versions(),
        "decoding": ("greedy (do_sample=False)" if cfg.task != "binary_logit"
                     else "first-token logit scoring (2 forward passes)"),
        "counts": {**counts, "cached_skipped": n_cached},
        "resume": {"kept": len(keep_lines), "dropped_failed": dropped["failed"],
                   "dropped_stale": dropped["stale"], "force": cfg.force},
        "n_gold": gold_report.n_examples, "gold_set_report": gold_report.to_dict(),
        "width_stats": (_width_stats(widths) if cfg.task == "pis" else None),
        "chunk_seconds": chunk_seconds,
        "wall_time_sec": round(time.time() - t0, 1),
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t0)),
        "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    (out_dir / f"manifest_{cfg.task}.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"output": str(out_path), "counts": manifest["counts"],
                      "resume": manifest["resume"],
                      "width_stats": manifest["width_stats"]}, indent=2))
    return manifest


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="python -m benchmarks.perturbation.pis.runner",
        description="PIS evidential-uncertainty evaluator for the perturbation benchmark")
    p.add_argument("--gold-set", required=True)
    p.add_argument("--task", required=True, choices=TASKS)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--model", default="Qwen/Qwen2.5-7B-Instruct")
    p.add_argument("--revision", default=None)
    p.add_argument("--backend", default="hf", choices=["hf", "mock"])
    p.add_argument("--quantization", default="nf4", choices=["nf4", "none"])
    p.add_argument("--dtype", default="float16", choices=["float16", "bfloat16", "float32"])
    p.add_argument("--device", default="cuda:0")
    p.add_argument("--batch-size", type=int, default=8)
    p.add_argument("--max-new-tokens", type=int, default=768)
    p.add_argument("--max-retries", type=int, default=2)
    p.add_argument("--context-file", default=None)
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--force", action="store_true")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--mock-responses", default=None)
    p.add_argument("--no-chat-template", action="store_true",
                   help="disable chat-template wrapping (base completion models only)")
    a = p.parse_args(argv)
    cfg = RunnerConfig(gold_set=a.gold_set, task=a.task, out_dir=a.out_dir,
                       model_id=a.model, revision=a.revision, backend_kind=a.backend,
                       quantization=a.quantization, dtype=a.dtype, device=a.device,
                       batch_size=a.batch_size, max_new_tokens=a.max_new_tokens,
                       max_retries=a.max_retries, context_file=a.context_file,
                       limit=a.limit, force=a.force, seed=a.seed,
                       mock_responses=a.mock_responses,
                       use_chat_template=not a.no_chat_template)
    run_evaluation(cfg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())