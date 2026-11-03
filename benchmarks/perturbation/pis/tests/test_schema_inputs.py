import json

import pytest

from benchmarks.perturbation.pis import inputs as inp
from benchmarks.perturbation.pis.gold_io import load_gold_set


def rec(**kw):
    base = {"paper": "paper_A", "perturbation_id": "P001_S0001", "span_id": "S0001",
            "error": "numeric_parameter", "original": "$w = L/2$", "perturbed": "$w = L/4$",
            "why_wrong": "X", "contradicts_quote": "we choose $w = L/2$",
            "quote_source": "generator", "gold_label": "substantive", "rationale": "Y"}
    base.update(kw)
    return base


def test_build_verifier_input_copies_only_allowed_fields():
    r = rec()
    vi = inp.build_verifier_input(r)
    assert vi.uid == "paper_A::P001_S0001"
    assert vi.error_type == "numeric_parameter"
    assert vi.original == "$w = L/2$" and vi.perturbed == "$w = L/4$"
    assert vi.quote_available
    d = {f: getattr(vi, f) for f in vi.__dataclass_fields__}
    for forbidden in ("gold_label", "rationale", "why_wrong"):
        assert forbidden not in d
        assert forbidden not in json.dumps(d)


def test_empty_quote_normalized_to_none():
    vi = inp.build_verifier_input(rec(contradicts_quote="   ", quote_source="none-available"))
    assert vi.contradicts_quote is None and not vi.quote_available


def test_composite_uid_required():
    with pytest.raises(ValueError):
        inp.record_uid({"paper": "p"})


def test_gold_loader_detects_duplicate_uids(tmp_path):
    p = tmp_path / "g.json"
    p.write_text(json.dumps({"examples": [rec(), rec()]}))
    with pytest.raises(ValueError, match="duplicate uid"):
        load_gold_set(str(p))


def test_gold_loader_report_and_quote_normalization(tmp_path):
    p = tmp_path / "g.json"
    p.write_text(json.dumps({"examples": [
        rec(), rec(paper="paper_B", perturbation_id="P001_S0001",
                  contradicts_quote="", quote_source="none-available",
                  gold_label="typo-shaped")]}))
    recs, rep = load_gold_set(str(p))
    assert len(recs) == 2
    assert recs[1]["contradicts_quote"] is None
    assert rep.label_counts == {"substantive": 1, "typo-shaped": 1}
    assert rep.quote_source_counts == {"generator": 1, "none-available": 1}


def test_gold_loader_accepts_jsonl(tmp_path):
    p = tmp_path / "g.jsonl"
    p.write_text(json.dumps(rec()) + "\n" +
                 json.dumps(rec(perturbation_id="P002_S0002")) + "\n")
    recs, _ = load_gold_set(str(p))
    assert len(recs) == 2


def test_gold_loader_accepts_bare_json_array(tmp_path):
    p = tmp_path / "g.json"
    p.write_text(json.dumps([rec(), rec(perturbation_id="P002_S0002")]))
    recs, _ = load_gold_set(str(p))
    assert len(recs) == 2


def test_gold_loader_rejects_nonfinite_constants_jsonl(tmp_path):
    p = tmp_path / "g.jsonl"
    good = json.dumps(rec())
    bad = good.replace('"substantive"', "NaN")
    p.write_text(good + "\n" + bad + "\n")
    with pytest.raises(ValueError, match="non-finite"):
        load_gold_set(str(p))


def test_gold_loader_rejects_nonfinite_constants_single_document(tmp_path):
    p = tmp_path / "g.json"
    inner = json.dumps(rec()).replace('"substantive"', "NaN")
    p.write_text('{"examples": [' + inner + ']}')
    with pytest.raises(ValueError, match="non-finite"):
        load_gold_set(str(p))