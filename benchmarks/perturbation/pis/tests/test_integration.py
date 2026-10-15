import json

import numpy as np
import pytest

from benchmarks.perturbation.pis.analysis import controls, failure_prediction, selective
from benchmarks.perturbation.pis.backends import MockBackend
from benchmarks.perturbation.pis.runner import RunnerConfig, run_evaluation

S, A = "supports_H", "against_H"
HIGH = [  # conflicting evidence -> wide interval
    {"source_type": "quote", "description": "d1", "polarity": S,
     "strength": 0.8, "reliability": 0.8, "justification": "j"},
    {"source_type": "span_comparison", "description": "d2", "polarity": A,
     "strength": 0.8, "reliability": 0.8, "justification": "j"}]
LOW_SUB = [{"source_type": "quote", "description": "d1", "polarity": S,
            "strength": 0.9, "reliability": 0.9, "justification": "j"}]
LOW_AGAINST = [{"source_type": "quote", "description": "d1", "polarity": A,
                "strength": 0.9, "reliability": 0.9, "justification": "j"}]


def _resp(items, conf=0.8):
    return json.dumps({"hypothesis_restated": "h", "evidence_items": items,
                       "self_reported_confidence_h": conf})


def _gold():
    def rec(paper, pid, gold, err="numeric_parameter", quote="q"):
        return {"paper": paper, "perturbation_id": pid, "span_id": "S0001",
                "error": err, "original": "$w = L/2$", "perturbed": "$w = L/4$",
                "why_wrong": "w", "contradicts_quote": quote, "quote_source": "generator",
                "gold_label": gold, "rationale": "r"}
    # 5 verifier-correct (low width), 4 verifier-wrong (high width).
    # papers A/B deliberately share perturbation_ids to exercise the composite uid.
    return {"examples": [
        rec("paper_A", "P001_S0001", "substantive"),
        rec("paper_A", "P002_S0002", "typo-shaped"),
        rec("paper_A", "P003_S0003", "substantive"),
        rec("paper_A", "P004_S0004", "typo-shaped"),      # retry case (garbage first)
        rec("paper_A", "P005_S0005", "substantive"),
        rec("paper_B", "P001_S0001", "substantive"),      # WRONG pred
        rec("paper_B", "P002_S0002", "typo-shaped"),      # WRONG pred
        rec("paper_B", "P003_S0003", "substantive", err="symbol_binding"),  # WRONG
        rec("paper_B", "P004_S0004", "typo-shaped", quote=""),              # WRONG
    ]}


def _responses():
    # order = gold order; index 3 is garbage, retry consumes index 9.
    return [
        _resp(LOW_SUB), _resp(LOW_AGAINST), _resp(LOW_SUB),
        "GARBAGE NOT JSON",
        _resp(LOW_AGAINST),
        _resp(HIGH), _resp(HIGH), _resp(HIGH), _resp(HIGH),
        _resp(LOW_AGAINST),  # retry for index 3
    ]


@pytest.fixture()
def pipeline(tmp_path):
    gold = tmp_path / "gold.json"
    gold.write_text(json.dumps(_gold()))
    resp = tmp_path / "resp.json"
    resp.write_text(json.dumps(_responses()))
    out = tmp_path / "run"
    cfg = RunnerConfig(gold_set=str(gold), task="pis", out_dir=str(out),
                      backend_kind="mock", mock_responses=str(resp),
                      model_id="mock-model", batch_size=16, max_new_tokens=32,
                      device="cpu", quantization="none")
    manifest = run_evaluation(cfg)
    pis_path = out / "predictions_pis.jsonl"
    preds = tmp_path / "preds.jsonl"
    flip = {"paper_B::P001_S0001", "paper_B::P002_S0002",
            "paper_B::P003_S0003", "paper_B::P004_S0004"}
    lines = []
    for ex in _gold()["examples"]:
        uid = f"{ex['paper']}::{ex['perturbation_id']}"
        pred = {"substantive": "typo-shaped", "typo-shaped": "substantive"}[ex["gold_label"]] \
            if uid in flip else ex["gold_label"]
        lines.append(json.dumps({"uid": uid, "pred_label": pred}))
    preds.write_text("\n".join(lines) + "\n")
    return {"tmp": tmp_path, "gold": str(gold), "pis": str(pis_path),
            "preds": str(preds), "out": str(out), "manifest": manifest, "cfg": cfg}


def test_runner_counts_and_resume(pipeline):
    m = pipeline["manifest"]
    assert m["counts"] == {"ok": 9, "cached_skipped": 0}
    # rerun: everything cached, no new inference consumed
    m2 = run_evaluation(pipeline["cfg"])
    assert m2["counts"]["cached_skipped"] == 9
    lines = [json.loads(l) for l in
             open(pipeline["pis"], encoding="utf-8")]
    assert len(lines) == 9
    by_uid = {l["uid"]: l for l in lines}
    assert by_uid["paper_A::P004_S0004"]["attempts"] == 2  # garbage -> retry ok
    assert by_uid["paper_A::P004_S0004"]["status"] == "ok"


def test_failure_prediction_end_to_end(pipeline):
    s = failure_prediction.run(pipeline["pis"], pipeline["preds"], pipeline["gold"],
                               str(pipeline["tmp"] / "a1"))
    assert s["n"] == 9 and s["n_incorrect"] == 4
    assert s["exclusions"] == {"no_pis": [], "pis_failed_or_no_interval": [], "no_prediction": []}
    assert s["auroc_width_for_incorrect"]["value"] == pytest.approx(1.0, abs=1e-9)
    assert (pipeline["tmp"] / "a1" / "summary.json").exists()
    assert (pipeline["tmp"] / "a1" / "report.md").exists()


def test_selective_verification_end_to_end(pipeline):
    s = selective.run(pipeline["pis"], pipeline["preds"], pipeline["gold"],
                      str(pipeline["tmp"] / "a2"))
    curve = json.loads((pipeline["tmp"] / "a2" / "risk_coverage_curve.json").read_text())
    cov = [p["coverage"] for p in curve["curve"]]
    risk = [p["selective_risk"] for p in curve["curve"]]
    assert cov[0] == pytest.approx(1 / 9) and cov[-1] == pytest.approx(1.0)
    assert risk[4] == 0.0                     # 5 lowest-width accepted: all correct
    assert risk[-1] == pytest.approx(4 / 9)   # full coverage == overall risk
    # abstention never counts as correct: recompute one point manually
    rows_sorted = sorted(curve["curve"], key=lambda p: p["k"])
    p5 = rows_sorted[4]
    assert p5["n_error_accepted"] == 0


def test_controls_end_to_end(pipeline):
    s = controls.run(pipeline["pis"], pipeline["preds"], pipeline["gold"],
                     str(pipeline["tmp"] / "a3"))
    assert "quote" in s["leave_one_source_type_out"]
    assert s["base_auroc_width_for_incorrect"] == pytest.approx(1.0, abs=1e-9)
    assert (pipeline["tmp"] / "a3" / "controls_summary.json").exists()


def test_rerun_retries_only_failed_examples(tmp_path):
    # Smoke-run scenario: one ok, one failed (deterministically unparseable).
    # After a parser fix (simulated by a healthy backend), a re-run must
    # re-attempt ONLY the failed example, keep the cached ok line verbatim,
    # and never leave duplicate uids in the cache file.

    def _rec(paper, pid, gold, err="numeric_parameter", quote="q"):
        return {"paper": paper, "perturbation_id": pid, "span_id": "S0001",
                "error": err, "original": "$w = L/2$", "perturbed": "$w = L/4$",
                "why_wrong": "w", "contradicts_quote": quote,
                "quote_source": "generator", "gold_label": gold, "rationale": "r"}

    gold = tmp_path / "gold.json"
    gold.write_text(json.dumps({"examples": [
        _rec("paper_A", "P001_S0001", "substantive"),
        _rec("paper_A", "P002_S0002", "typo-shaped")]}))
    resp1 = tmp_path / "resp1.json"
    resp1.write_text(json.dumps([_resp(LOW_SUB), "GARBAGE NOT JSON",
                                 "GARBAGE NOT JSON", "GARBAGE NOT JSON"]))
    out = tmp_path / "run"
    cfg = RunnerConfig(gold_set=str(gold), task="pis", out_dir=str(out),
                       backend_kind="mock", mock_responses=str(resp1),
                       model_id="mock-model", batch_size=8, max_new_tokens=32,
                       device="cpu", quantization="none")
    m1 = run_evaluation(cfg)
    assert m1["counts"].get("ok") == 1 and m1["counts"].get("failed") == 1

    fixed = MockBackend([_resp(LOW_AGAINST)])
    m2 = run_evaluation(cfg, backend=fixed)
    assert m2["counts"].get("ok") == 1 and m2["counts"].get("cached_skipped") == 1
    assert m2["resume"] == {"kept": 1, "dropped_failed": 1,
                            "dropped_stale": 0, "force": False}
    assert len(fixed.calls) == 1  # exactly one prompt: the previously failed uid

    lines = [json.loads(l) for l in
             (out / "predictions_pis.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(lines) == 2
    by_uid = {l["uid"]: l for l in lines}
    assert by_uid["paper_A::P001_S0001"]["attempts"] == 1   # cached, untouched
    assert by_uid["paper_A::P001_S0001"]["status"] == "ok"
    assert by_uid["paper_A::P002_S0002"]["status"] == "ok"  # recovered on rerun
    assert by_uid["paper_A::P002_S0002"]["attempts"] == 1