from __future__ import annotations

import argparse
import difflib
import json
from pathlib import Path

import numpy as np

from ..evidence import EvidenceItem, aggregate_evidence
from ..gold_io import load_gold_set
from ..inputs import record_uid
from ..interval import PISInterval
from .common import (auroc, build_rows, read_jsonl, spearman, write_json)

_ITEM_KEYS = ("source_type", "description", "polarity", "strength", "reliability",
              "justification")


def _items_from_line(line):
    return [EvidenceItem(**{k: it[k] for k in _ITEM_KEYS if k in it})
            for it in (line.get("evidence_items") or [])]


def run(pis_path, predictions_path, gold_set_path, out_dir, pis_b_path=None) -> dict:
    rows, exclusions = build_rows(pis_path, predictions_path, gold_set_path)
    inc = np.array([0 if r.correct else 1 for r in rows], int)
    widths = np.array([r.width for r in rows], float)
    pis_by = {l["uid"]: l for l in read_jsonl(pis_path)}
    items_by = {r.uid: _items_from_line(pis_by[r.uid]) for r in rows}

    source_types = sorted({it.source_type for its in items_by.values() for it in its})
    presence = {s: int(sum(any(it.source_type == s for it in items_by[r.uid]) for r in rows))
                for s in source_types}
    base = auroc(widths, inc)
    loo = {}
    for s in source_types:
        w2 = np.array([aggregate_evidence([it for it in items_by[r.uid]
                                          if it.source_type != s]).width for r in rows])
        loo[s] = {"auroc_width": auroc(w2, inc), "mean_width": float(w2.mean()),
                  "mean_delta_width_vs_full": float((w2 - widths).mean())}

    gold_records, _ = load_gold_set(gold_set_path)
    lex, lendiff = {}, {}
    for g in gold_records:
        uid = record_uid(g)
        lex[uid] = 1.0 - difflib.SequenceMatcher(
            None, str(g["original"]), str(g["perturbed"])).ratio()
        lendiff[uid] = float(abs(len(str(g["original"])) - len(str(g["perturbed"]))))

    confounds = {
        "spearman_width_vs_lexical_distance": spearman(widths, [lex[r.uid] for r in rows]),
        "spearman_width_vs_abs_len_diff": spearman(widths, [lendiff[r.uid] for r in rows]),
        "spearman_width_vs_n_items": spearman(widths, [float(r.n_items) for r in rows]),
        "spearman_width_vs_ambiguity": spearman(widths, [r.ambiguity for r in rows]),
    }

    cross = None
    if pis_b_path:
        b_by = {l["uid"]: l for l in read_jsonl(pis_b_path)}
        common = [r for r in rows if b_by.get(r.uid, {}).get("interval")]
        if len(common) >= 5:
            wb = np.array([PISInterval.from_dict(b_by[r.uid]["interval"]).width
                           for r in common])
            wa = np.array([r.width for r in common])
            inc_c = np.array([0 if r.correct else 1 for r in common], int)
            cross = {"n": len(common),
                     "spearman_width_a_vs_width_b": spearman(wa, wb),
                     "auroc_width_b": auroc(wb, inc_c),
                     "auroc_width_a_same_subset": auroc(wa, inc_c),
                     "auroc_mean_width_ab": auroc(0.5 * (wa + wb), inc_c)}
        else:
            cross = {"n": len(common), "note": "too few common uids for cross-model check"}

    summary = {"experiment": "controls_and_ablations",
               "questions": [
                   "Does the width signal survive removing each evidence source "
                   "type (leave-one-source-out, recomputed from cached items)?",
                   "Is width merely proxying lexical distance / length / item count?",
                   "Is the signal robust across a second evaluator model?"],
               "n": len(rows), "exclusions": exclusions,
               "base_auroc_width_for_incorrect": base,
               "source_type_presence": presence,
               "leave_one_source_type_out": loo,
               "confound_correlations": confounds,
               "cross_model": cross}
    write_json(Path(out_dir) / "controls_summary.json", summary)
    return summary


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="python -m benchmarks.perturbation.pis.analysis.controls")
    p.add_argument("--pis", required=True)
    p.add_argument("--predictions", required=True)
    p.add_argument("--gold-set", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--pis-b", default=None, help="optional second PIS run for cross-model check")
    a = p.parse_args(argv)
    print(json.dumps(run(a.pis, a.predictions, a.gold_set, a.out, a.pis_b), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())