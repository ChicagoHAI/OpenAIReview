import json
import pytest

from benchmarks.perturbation.pis.scripts.convert_predictions import convert, load_any
from benchmarks.perturbation.pis.scripts.make_uid_gold_set import rewrite


def _gold_rec(paper, pid, **kw):
    base = {"paper": paper, "perturbation_id": pid, "span_id": "S0001",
            "error": "numeric_parameter", "original": "$w = L/2$",
            "perturbed": "$w = L/4$", "why_wrong": "w",
            "contradicts_quote": "q", "quote_source": "generator",
            "gold_label": "substantive", "rationale": "r"}
    base.update(kw)
    return base


def test_rewrite_uniquifies_and_reports_collisions():
    recs = [_gold_rec("paper_A", "P000_S0000"),
            _gold_rec("paper_B", "P000_S0000"),
            _gold_rec("paper_C", "P001_S0001")]
    out, collisions, n_filled = rewrite(recs)
    assert collisions == {"P000_S0000": 2}
    uids = [r["perturbation_id"] for r in out]
    assert uids == ["paper_A::P000_S0000", "paper_B::P000_S0000",
                    "paper_C::P001_S0001"]
    assert len(set(uids)) == 3 and n_filled == 0


def test_rewrite_restores_repo_native_fields():
    rec = _gold_rec("paper_A", "P001_S0001", contradicts_quote=None)
    del rec["span_id"]
    out, _, n_filled = rewrite([rec])
    assert out[0]["contradicts_quote"] == ""      # repo-native, not None
    assert out[0]["span_id"] == "SYN" and n_filled == 1
    assert out[0]["gold_label"] == "substantive"  # untouched: run_eval needs it


def test_load_any_unwraps_run_eval_rows(tmp_path):
    rows = [{"perturbation_id": "paper_001::P004_S0001", "pred_label": "substantive",
             "gold_label": "substantive", "correct": True, "pred_reason": "r"},
            {"perturbation_id": "paper_002::P001_S0030", "pred_label": "typo-shaped",
             "gold_label": "substantive", "correct": False, "pred_reason": "r"}]
    p = tmp_path / "res.json"
    p.write_text(json.dumps({"variant": "after", "model": "m",
                             "reasoning_effort": "none", "n_examples": 2, "rows": rows}))
    recs, meta = load_any(str(p))
    assert len(recs) == 2
    assert meta["variant"] == "after" and meta["model"] == "m"


def test_convert_maps_composite_uids_and_strips_gold(tmp_path):
    rows = [{"perturbation_id": "paper_001::P004_S0001", "pred_label": "substantive",
             "gold_label": "substantive", "correct": True,
             "pred_reason": "quote states it", "quote_source": "generator"},
            {"perturbation_id": "paper_002::P001_S0030", "pred_label": "parse-error",
             "gold_label": "substantive", "correct": False,
             "pred_reason": "chat failed: x"}]
    out = tmp_path / "preds.jsonl"
    convert(rows, {"variant": "after", "model": "m"}, str(out))
    lines = [json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(lines) == 2
    assert lines[0]["uid"] == "paper_001::P004_S0001"
    assert lines[0]["pred_label"] == "substantive"
    assert lines[0]["verifier_reason"] == "quote states it"
    assert lines[0]["model"] == "m" and lines[0]["variant"] == "after"
    assert "gold_label" not in lines[0] and "correct" not in lines[0]
    assert lines[1]["pred_label"] == "parse-error"


def test_convert_refuses_gold_keys_as_predictions(tmp_path, capsys):
    rows = [{"perturbation_id": "paper_001::P004_S0001", "gold_label": "substantive"}]
    out = tmp_path / "preds.jsonl"
    convert(rows, {}, str(out))
    assert out.read_text(encoding="utf-8").strip() == ""
    assert "could not be converted" in capsys.readouterr().out


def test_surrogate_refuses_pis_primary_model():
    from benchmarks.perturbation.pis.scripts.run_surrogate_verifier import (
        PIS_PRIMARY_MODEL, assert_model_differs)
    with pytest.raises(ValueError):
        assert_model_differs(PIS_PRIMARY_MODEL)
    assert_model_differs("Qwen/Qwen2.5-14B-Instruct")  # different model: OK