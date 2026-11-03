"""Gold-blind evidence audit and post-hoc failure forensics.

Two subcommands with strict information separation:
  audit      — model-vs-model evidence audit. Takes ONLY PIS prediction
               files and never touches the gold set; run it BEFORE looking
               at any gold-error analysis. This is the pre-outcome evidence
               for the assessor-dependence finding (RESULTS.md §7).
  forensics  — evaluation-stage error analysis (confusion, strata).
               Exploratory by construction; no claims may be built on it
               without new pre-registration.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional

from .common import build_rows, read_jsonl, spearman, write_json

WIDTH_EDGES = [0.05, 0.1, 0.25, 0.5, 0.75, 1.0]
WIDTH_LABELS = ["==0", "(0,.05)", "[.05,.1)", "[.1,.25)", "[.25,.5)",
                "[.5,.75)", "[.75,1)", "==1"]


def _bucket(w: float) -> str:
    if w == 0.0:
        return "==0"
    if w == 1.0:
        return "==1"
    for i, e in enumerate(WIDTH_EDGES):
        if w < e:
            return WIDTH_LABELS[i + 1]
    return "==1"


def _committed(it) -> bool:
    return it["strength"] * it["reliability"] > 0


def _audit_one(lines: List[dict]) -> dict:
    items = [it for l in lines for it in (l.get("evidence_items") or [])]
    rep = Counter()
    for l in lines:
        for note in l.get("repairs", []):
            rep["backslash" if "doubled" in note
                else "clamp" if "clamped" in note else "OTHER"] += 1
    widths = [l["interval"]["width"] for l in lines]
    mixed = one_sided = empty_items = 0
    for l in lines:
        its = l.get("evidence_items") or []
        if not its:
            empty_items += 1
            continue
        hp = any(i["polarity"] == "supports_H" and _committed(i) for i in its)
        hm = any(i["polarity"] == "against_H" and _committed(i) for i in its)
        mixed += (hp and hm)
        one_sided += (hp != hm)
    zero_win = Counter()
    for l in lines:
        if l["interval"]["width"] == 0.0:
            its = l.get("evidence_items") or []
            if any(i["polarity"] == "supports_H"
                   and i["strength"] * i["reliability"] >= 1.0 for i in its):
                zero_win["supports_H"] += 1
            elif any(i["polarity"] == "against_H"
                     and i["strength"] * i["reliability"] >= 1.0 for i in its):
                zero_win["against_H"] += 1
            else:
                zero_win["non-saturated"] += 1
    # W = 1 classification (self-checking). By the aggregation algebra
    # (unit-tested in test_evidence.py), m(Theta) = 1 exactly iff either
    # (a) NO committed supports/against evidence exists -- pure vacuity;
    # unresolved-polarity items commit no mass by construction; or
    # (b) a saturated witness (c = strength*reliability = 1.0) exists on
    # BOTH sides -- maximal conflict. A W = 1 record with committed
    # evidence that is NOT both-sides saturated is internally inconsistent
    # (interval vs items) and lands in the tripwire bucket.
    vac = conflict = inconsistent = 0
    for l in lines:
        if l["interval"]["width"] != 1.0:
            continue
        its = l.get("evidence_items") or []
        committed = [i for i in its
                     if i["polarity"] in ("supports_H", "against_H")
                     and _committed(i)]
        if not committed:
            vac += 1
            continue
        sat_sup = any(i["polarity"] == "supports_H"
                      and i["strength"] * i["reliability"] >= 1.0
                      for i in committed)
        sat_agn = any(i["polarity"] == "against_H"
                      and i["strength"] * i["reliability"] >= 1.0
                      for i in committed)
        if sat_sup and sat_agn:
            conflict += 1
        else:
            inconsistent += 1
    conf = sorted(l["self_reported_confidence_h"] for l in lines
                  if isinstance(l.get("self_reported_confidence_h"), (int, float)))
    return {
        "n": len(lines),
        "status": dict(Counter(l.get("status", "?") for l in lines)),
        "attempts": dict(Counter(l.get("attempts", "?") for l in lines)),
        "repair_types": dict(rep),
        "width_buckets": {k: sum(1 for w in widths if _bucket(w) == k)
                          for k in WIDTH_LABELS},
        "items": {"n": len(items),
                  "saturated_s1_r1": sum(1 for i in items
                                         if i["strength"] == 1.0 and i["reliability"] == 1.0),
                  "mean_strength": (sum(i["strength"] for i in items) / len(items)) if items else None,
                  "mean_reliability": (sum(i["reliability"] for i in items) / len(items)) if items else None,
                  "polarity": dict(Counter(i["polarity"] for i in items))},
        "examples": {"mixed_polarity": mixed, "one_sided": one_sided,
                     "empty_items": empty_items},
        "width_zero_winner_side": dict(zero_win),
        "width_one": {"no_committed_evidence": vac,
                      "maximal_conflict": conflict,
                      "inconsistent": inconsistent},
        "self_confidence": ({"n": len(conf), "min": conf[0],
                             "median": conf[len(conf) // 2], "max": conf[-1],
                             "frac_ge_0.9": sum(c >= 0.9 for c in conf) / len(conf)}
                            if conf else None),
    }


def audit(pis_by_model: Dict[str, str], out_dir: str, top_k: int = 15) -> dict:
    """GOLD-BLIND: takes ONLY PIS prediction files; never touches the gold
    set. Run before any gold-error analysis."""
    loaded = {name: read_jsonl(p) for name, p in pis_by_model.items()}
    per_model = {name: _audit_one(lines) for name, lines in loaded.items()}
    widths = {name: {l["uid"]: l["interval"]["width"] for l in lines}
              for name, lines in loaded.items()}
    cross = {}
    names = sorted(loaded)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            common = sorted(set(widths[a]) & set(widths[b]))
            entry = {"n": len(common)}
            if len(common) >= 3:
                entry["spearman_width"] = spearman(
                    [widths[a][u] for u in common], [widths[b][u] for u in common])
                entry[f"top{top_k}_by_{a}"] = [
                    {"uid": u, a: widths[a][u], b: widths[b][u]}
                    for u in sorted(common, key=lambda u: -widths[a][u])[:top_k]]
                entry[f"top{top_k}_by_{b}"] = [
                    {"uid": u, a: widths[a][u], b: widths[b][u]}
                    for u in sorted(common, key=lambda u: -widths[b][u])[:top_k]]
            cross[f"{a}_vs_{b}"] = entry
    out = {"gold_blind": True, "per_model": per_model, "cross_model": cross}
    write_json(Path(out_dir) / "evidence_audit.json", out)
    return out


def forensics(pis_path, predictions_path, gold_set_path, out_dir,
              scalar_path: Optional[str] = None) -> dict:
    """POST-HOC (evaluation stage): confusion + strata. Exploratory by
    construction; no claims may be built on this without new
    pre-registration."""
    rows, exclusions = build_rows(pis_path, predictions_path, gold_set_path)
    confusion = Counter((r.gold_label, r.pred_label) for r in rows)

    def stratum(pred):
        us = [r for r in rows if pred(r)]
        errs = [r for r in us if not r.correct]
        ok = [r for r in us if r.correct]
        mean = lambda xs: (sum(x.width for x in xs) / len(xs)) if xs else None
        return {"n": len(us), "n_error": len(errs),
                "error_rate": (len(errs) / len(us)) if us else None,
                "width_mean_all": mean(us), "width_mean_error": mean(errs),
                "width_mean_correct": mean(ok)}

    strata = {
        "synthetic": stratum(lambda r: r.paper == "synthetic"),
        "real_papers": stratum(lambda r: r.paper != "synthetic"),
        "quote_available": stratum(lambda r: r.quote_available),
        "no_quote": stratum(lambda r: not r.quote_available),
    }
    for t in sorted({r.error_type for r in rows}):
        strata[f"error={t}"] = stratum(lambda r, t=t: r.error_type == t)

    out = {"n": len(rows), "exclusions": exclusions,
           "confusion_gold_to_pred": {f"{g} -> {p}": c
                                      for (g, p), c in sorted(confusion.items())},
           "pred_label_counts": dict(Counter(r.pred_label for r in rows)),
           "strata": strata}
    if scalar_path:
        vals = [l.get("value") for l in read_jsonl(scalar_path)]
        out["scalar_self_confidence"] = {
            "n": len(vals), "distinct": len(set(vals)),
            "top_values": Counter(vals).most_common(5)}
    write_json(Path(out_dir) / "failure_forensics.json", out)
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="python -m benchmarks.perturbation.pis.analysis.diagnostics")
    sub = p.add_subparsers(dest="cmd", required=True)
    pa = sub.add_parser("audit")
    pa.add_argument("--pis", action="append", required=True, metavar="NAME=PATH",
                    help="repeatable: <model name>=<PIS predictions jsonl>")
    pa.add_argument("--out", required=True)
    pf = sub.add_parser("forensics")
    pf.add_argument("--pis", required=True)
    pf.add_argument("--predictions", required=True)
    pf.add_argument("--gold-set", required=True)
    pf.add_argument("--scalar", default=None)
    pf.add_argument("--out", required=True)
    a = p.parse_args(argv)
    if a.cmd == "audit":
        pis_by = {}
        for spec in a.pis:
            name, _, path = spec.partition("=")
            if not name or not path:
                raise SystemExit(f"--pis expects NAME=PATH, got {spec!r}")
            pis_by[name] = path
        res = audit(pis_by, a.out)
    else:
        res = forensics(a.pis, a.predictions, a.gold_set, a.out, a.scalar)
    print(json.dumps(res, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())