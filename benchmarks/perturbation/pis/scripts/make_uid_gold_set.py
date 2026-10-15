#!/usr/bin/env python
"""Write a copy of the verifier gold set with globally unique perturbation_ids.

WHY: run_eval.py keys its verdict/gold joins on perturbation_id ALONE, but
perturbation_id is NOT unique across papers in the gold set (e.g. "P000_S0000"
appears under paper_003, paper_004, paper_009 and paper_010). For colliding ids,
run_eval assigns one (completion-order dependent) verdict to ALL colliding
examples and scores them all against a single gold label; the output rows also
lack a paper field, so the conflation cannot be repaired after the fact.

This script rewrites perturbation_id -> "<paper>::<perturbation_id>" in a COPY
of the gold set. The verifier prompt does not contain perturbation_id, so the
per-example model inputs (and hence the verdicts) are byte-identical to a
direct run; only the bookkeeping keys become unique. Feeding the rewritten
file to run_eval.py via --gold therefore yields collision-free predictions
whose perturbation_id IS the composite uid used by the PIS analysis.

NOTE: the rewritten file is for run_eval.py ONLY. Do not feed it to the PIS
runner or analysis (they build composite uids themselves and would double
the prefix).
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[4]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from benchmarks.perturbation.pis.gold_io import load_gold_set  # noqa: E402
from benchmarks.perturbation.pis.inputs import record_uid      # noqa: E402


def rewrite(records: list[dict]) -> tuple[list[dict], dict[str, int], int]:
    """Return (rewritten_records, collision_report, n_span_id_filled).

    Also restores repo-native conventions for the copy: empty quotes become
    "" (not None), and records missing span_id get a placeholder so that
    run_eval's _make_perturbation (Perturbation(span_id=...)) never KeyErrors.
    """
    pid_counts = Counter(str(r["perturbation_id"]) for r in records)
    collisions = {pid: n for pid, n in pid_counts.items() if n > 1}
    out: list[dict] = []
    n_filled = 0
    for r in records:
        r2 = dict(r)
        r2["perturbation_id"] = record_uid(r)
        if not str(r2.get("contradicts_quote") or "").strip():
            r2["contradicts_quote"] = ""
        if "span_id" not in r2:
            r2["span_id"] = "SYN"
            n_filled += 1
        out.append(r2)
    assert len({r["perturbation_id"] for r in out}) == len(out), \
        "rewrite failed to uniquify (paper::pid should be unique by construction)"
    return out, collisions, n_filled


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold-set", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    records, _report = load_gold_set(a.gold_set)  # validates + duplicate-uid check
    out, collisions, n_filled = rewrite(records)

    n_affected = sum(collisions.values())
    print(f"gold set: {len(records)} examples; "
          f"{len(collisions)} colliding perturbation_id(s) affecting {n_affected} examples")
    for pid, n in sorted(collisions.items()):
        papers = sorted(str(r["paper"]) for r in records
                        if str(r["perturbation_id"]) == pid)
        print(f"  {pid} x{n}: {papers}")
    if n_filled:
        print(f"[note] filled missing span_id placeholder on {n_filled} record(s)")

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(
        json.dumps({"examples": out}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {a.out} ({len(out)} examples, composite perturbation_ids)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())