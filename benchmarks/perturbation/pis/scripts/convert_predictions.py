#!/usr/bin/env python
"""Convert a verifier-eval output into the predictions schema expected by the
PIS analysis (see docs/PREDICTIONS_SCHEMA.md).

Supported inputs:
  1. run_eval.py results JSON {"variant": ..., "model": ..., "rows": [...]}
     (recommended path: run run_eval.py on the gold set rewritten by
     make_uid_gold_set.py, so rows carry composite "paper::pid" ids).
  2. A bare JSON array, {"examples": [...]}, or JSONL of prediction objects.

uid resolution: "uid" key > "paper"+"perturbation_id" > "perturbation_id"
containing "::". Gold-ish keys ('gold_label', 'label', ...) are REFUSED as
prediction sources, and gold-derived fields are never copied into the output:
the analysis recomputes correctness itself from the gold set.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

PRED_KEYS = ("pred_label", "verdict", "predicted_label", "prediction",
             "final_verdict", "classifier_label")
REFUSED_KEYS = ("gold_label", "gold", "label", "rationale")


def load_any(path: str):
    """Return (records, meta). meta is the top-level dict minus the record list
    when the file is a single JSON object, else {}."""
    text = Path(path).read_text(encoding="utf-8")
    stripped = text.lstrip()
    if stripped[:1] not in ("[", "{"):
        return [json.loads(ln) for ln in text.splitlines() if ln.strip()], {}
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        # JSONL whose first record is an object also starts with '{'.
        return [json.loads(ln) for ln in text.splitlines() if ln.strip()], {}
    if isinstance(obj, list):
        return obj, {}
    if isinstance(obj, dict):
        for key in ("rows", "examples"):
            if isinstance(obj.get(key), list):
                return obj[key], {k: v for k, v in obj.items() if k != key}
        return [obj], obj
    raise ValueError(f"unrecognized structure in {path}")


def inspect(records, meta) -> None:
    print(f"n records: {len(records)}")
    if meta:
        print(f"top-level meta: {json.dumps(meta, ensure_ascii=False)[:400]}")
    first = records[0] if records else {}
    print(f"record type: {type(first).__name__}")
    if isinstance(first, dict):
        print(f"record keys: {sorted(first.keys())}")
        print("first record (truncated to 800 chars):")
        print(json.dumps(first, ensure_ascii=False)[:800])


def convert(records, meta, out_path: str) -> None:
    keep_meta = {k: meta[k] for k in ("variant", "model", "reasoning_effort")
                 if isinstance(meta.get(k), (str, int, float, bool))}
    lines, problems = [], []
    for i, o in enumerate(records):
        if not isinstance(o, dict):
            problems.append(f"record {i}: not an object"); continue
        uid = o.get("uid")
        if uid is None and isinstance(o.get("paper"), str) \
                and isinstance(o.get("perturbation_id"), str):
            uid = f"{o['paper']}::{o['perturbation_id']}"
        if uid is None and isinstance(o.get("perturbation_id"), str) \
                and "::" in o["perturbation_id"]:
            uid = o["perturbation_id"]  # composite id from make_uid_gold_set.py
        if uid is None:
            problems.append(f"record {i}: no resolvable uid"); continue
        pred = None
        for k in PRED_KEYS:
            v = o.get(k)
            if isinstance(v, str) and v.strip():
                pred = v; break
        if pred is None:
            refused = [k for k in REFUSED_KEYS if k in o]
            problems.append(f"record {i} ({uid}): no prediction key found"
                            + (f" [refused gold-ish keys: {refused}]" if refused else ""))
            continue
        rec = {"uid": uid, "pred_label": pred.strip(), **keep_meta}
        for src, dst in (("pred_reason", "verifier_reason"), ("reason", "verifier_reason")):
            if isinstance(o.get(src), str) and o[src].strip():
                rec["verifier_reason"] = o[src].strip()
                break
        if isinstance(o.get("quote_source"), str) and o["quote_source"].strip():
            rec["quote_source"] = o["quote_source"].strip()
        lines.append(json.dumps(rec, ensure_ascii=False))
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    print(f"wrote {len(lines)} predictions -> {out_path}")
    if problems:
        print(f"{len(problems)} records could not be converted (DO NOT guess; "
              "send these to the implementation owner):")
        for p in problems:
            print("  -", p)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--inspect", action="store_true")
    a = p.parse_args()
    records, meta = load_any(a.input)
    if a.inspect or not records:
        inspect(records if records else [{}], meta)
        return 0
    convert(records, meta, a.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())