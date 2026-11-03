#!/usr/bin/env python
"""Surrogate local verifier for Step D (FALLBACK PATH B).

Use ONLY when no credentials for the production verifier API are obtainable.
Reuses the production verifier's LOGIC verbatim (structural_precheck,
VERIFIER_PROMPT formatting, _pick_quote, _parse_verdict — imported from
benchmarks.perturbation.verify, variant "after", span=None as in run_eval)
and replaces ONLY the chat() call with local HF greedy generation.

Every output is stamped verifier_config="surrogate-local"; conclusions drawn
from these predictions must be scoped as "verifier with production logic,
surrogate local model", and the analysis report must disclose this plus the
model-lineage caveat (surrogate shares the Qwen2.5 family with the PIS
primary evaluator).

Guardrail: the surrogate model MUST differ from the PIS primary evaluator
model, so the uncertainty signal and the system under study are never the
same model.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[4]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from benchmarks.perturbation.models import Error, Perturbation  # noqa: E402
from benchmarks.perturbation.verify import (  # noqa: E402
    VERIFIER_PROMPT, _parse_verdict, _pick_quote, structural_precheck)
from benchmarks.perturbation.pis.backends import HFBackend  # noqa: E402

PIS_PRIMARY_MODEL = "Qwen/Qwen2.5-7B-Instruct"


def assert_model_differs(model: str, pis_primary: str = PIS_PRIMARY_MODEL) -> None:
    if model == pis_primary:
        raise ValueError(
            f"surrogate verifier model must differ from the PIS primary "
            f"evaluator model ({pis_primary!r}) to avoid same-model "
            "circularity between the uncertainty signal and the system "
            "under study")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold-set", required=True,
                    help="UID-rewritten gold copy from make_uid_gold_set.py")
    ap.add_argument("--out", required=True, help="run_eval-compatible results JSON")
    ap.add_argument("--model", default="Qwen/Qwen2.5-14B-Instruct")
    ap.add_argument("--revision", default=None)
    ap.add_argument("--device", default="cuda:0")
    ap.add_argument("--quantization", default="nf4", choices=["nf4", "none"])
    ap.add_argument("--dtype", default="float16")
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--max-new-tokens", type=int, default=512)
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    assert_model_differs(args.model)

    examples = json.loads(
        Path(args.gold_set).read_text(encoding="utf-8"))["examples"]
    if args.limit:
        examples = examples[:args.limit]

    # Identical construction to run_eval._make_perturbation.
    perturbations = [
        Perturbation(
            perturbation_id=ex["perturbation_id"], span_id=ex["span_id"],
            error=Error(ex["error"]), original=ex["original"],
            offset=ex.get("offset", 0), perturbed=ex["perturbed"],
            why_wrong=ex.get("why_wrong", ""),
            contradicts_quote=ex.get("contradicts_quote", ""),
        ) for ex in examples]

    # Pass 1: deterministic structural precheck (identical to production;
    # rejects never reach the model).
    prechecked: list[tuple[Perturbation, str, str]] = []
    llm_jobs: list[tuple[Perturbation, str]] = []
    for p in perturbations:
        status, reason, _sp_quote = structural_precheck(p)
        if status == "reject-typo":
            prechecked.append((p, "typo-shaped", f"structural precheck: {reason}"))
            continue
        quote, quote_source = _pick_quote(p, None)
        # Identical formatting to _verify_one (variant "after": template has
        # no {why_wrong}; str.format ignores extra kwargs so we mirror it).
        prompt = VERIFIER_PROMPT.format(
            error_type=p.error.value, original=p.original, perturbed=p.perturbed,
            quote=quote,
            quote_source=("provided by the generator" if quote_source == "generator"
                         else "randomly sampled from the paper"
                         if quote_source == "random-sampled"
                         else "no quote was available"))
        llm_jobs.append((p, prompt))

    t0 = time.time()
    backend = HFBackend(args.model, revision=args.revision, device=args.device,
                        quantization=args.quantization, dtype=args.dtype)
    verdicts: dict[str, tuple[str, str]] = {
        p.perturbation_id: (v, r) for p, v, r in prechecked}
    for i in range(0, len(llm_jobs), args.batch_size):
        chunk = llm_jobs[i:i + args.batch_size]
        outputs = backend.generate([c[1] for c in chunk], args.max_new_tokens)
        for (p, _), out in zip(chunk, outputs):
            v, r = _parse_verdict(out)  # production parser incl. salvage
            verdicts[p.perturbation_id] = (v, r)
        print(f"[surrogate] {min(i + len(chunk), len(llm_jobs))}/{len(llm_jobs)} "
              f"llm-judged", flush=True)

    gold_by = {ex["perturbation_id"]: ex for ex in examples}
    rows = []
    for p in perturbations:
        ex = gold_by[p.perturbation_id]
        v, r = verdicts[p.perturbation_id]
        rows.append({
            "perturbation_id": p.perturbation_id, "error": p.error.value,
            "original": p.original, "perturbed": p.perturbed,
            "contradicts_quote": p.contradicts_quote,
            "gold_label": ex["gold_label"], "pred_label": v,
            "pred_reason": r, "rationale": ex.get("rationale", ""),
            "correct": ex["gold_label"] == v,
        })

    n_parse = sum(1 for r in rows if r["pred_label"] == "parse-error")
    results = {
        "variant": "after-surrogate-local",
        "model": args.model,
        "resolved_revision": getattr(backend, "resolved_revision", None),
        "verifier_config": (
            "surrogate-local: production logic (structural_precheck + "
            "VERIFIER_PROMPT + _parse_verdict, variant 'after', span=None) "
            "with chat() replaced by local HF greedy generation. NOT the "
            "production verifier model. Conclusions must be scoped "
            "accordingly."),
        "reasoning_effort": None,
        "quantization": args.quantization, "dtype": args.dtype,
        "device": args.device, "decoding": "greedy (do_sample=False)",
        "n_examples": len(rows),
        "n_precheck_rejected": len(prechecked),
        "n_llm_judged": len(llm_jobs),
        "parse_errors": n_parse,
        "wall_time_sec": round(time.time() - t0, 1),
        "rows": rows,
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(results, indent=2, ensure_ascii=False),
                              encoding="utf-8")
    print(f"wrote {args.out}")
    print(f"precheck-rejected: {len(prechecked)} | llm-judged: {len(llm_jobs)} "
          f"| parse-errors: {n_parse}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())