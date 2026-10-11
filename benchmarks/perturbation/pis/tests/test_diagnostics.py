import json

from benchmarks.perturbation.pis.analysis import diagnostics


def _pis_line(uid, width, items, conf=0.9):
    # Masses consistent with the width (PISInterval's sum-to-1 invariant is
    # re-validated by build_rows via from_dict, so fixtures must be valid).
    committed = (1.0 - width) / 2.0
    return {"uid": uid, "status": "ok", "attempts": 1,
            "interval": {"m_support": committed, "m_against": committed,
                         "m_unresolved": width, "L": committed,
                         "U": committed + width, "width": width,
                         "source": "test"},
            "evidence_items": items, "repairs": [],
            "self_reported_confidence_h": conf}


def _item(pol, s, r, src="quote"):
    return {"source_type": src, "description": "d", "polarity": pol,
            "strength": s, "reliability": r, "justification": "j"}


def test_audit_gold_blind_counts(tmp_path):
    a = tmp_path / "a.jsonl"
    lines = [
        _pis_line("u1", 0.5, [_item("supports_H", 0.8, 0.8),
                              _item("against_H", 0.7, 0.9)]),
        _pis_line("u2", 0.0, [_item("supports_H", 1.0, 1.0)]),
        # unresolved-polarity items commit no mass: W=1 here is pure vacuity
        _pis_line("u3", 1.0, [_item("unresolved", 0.5, 0.5)]),
        # tripwire: committed supports evidence but W=1 is inconsistent with
        # the aggregation algebra (single-side saturation cannot give W=1)
        _pis_line("u4", 1.0, [_item("supports_H", 0.9, 0.9)]),
    ]
    a.write_text("\n".join(json.dumps(l) for l in lines) + "\n", encoding="utf-8")
    b = tmp_path / "b.jsonl"
    b.write_text("\n".join(
        json.dumps(_pis_line(u, w, [_item("supports_H", 0.5, 0.5)]))
        for u, w in [("u1", 0.2), ("u2", 0.4), ("u3", 0.6)]) + "\n",
        encoding="utf-8")
    res = diagnostics.audit({"a": str(a), "b": str(b)}, str(tmp_path / "out"))
    assert res["gold_blind"] is True
    assert res["per_model"]["a"]["n"] == 4
    assert res["per_model"]["a"]["examples"]["mixed_polarity"] == 1
    assert res["per_model"]["a"]["examples"]["one_sided"] == 2
    assert res["per_model"]["a"]["width_zero_winner_side"] == {"supports_H": 1}
    assert res["per_model"]["a"]["width_one"] == {
        "no_committed_evidence": 1, "maximal_conflict": 0, "inconsistent": 1}
    assert res["cross_model"]["a_vs_b"]["n"] == 3
    assert "spearman_width" in res["cross_model"]["a_vs_b"]
    assert (tmp_path / "out" / "evidence_audit.json").exists()


def test_forensics_confusion_and_strata(tmp_path):
    def g(paper, pid, gold):
        return {"paper": paper, "perturbation_id": pid, "span_id": "S0001",
                "error": "numeric_parameter", "original": "$a$", "perturbed": "$b$",
                "why_wrong": "w", "contradicts_quote": "q",
                "quote_source": "generator", "gold_label": gold, "rationale": "r"}
    gold = tmp_path / "gold.json"
    gold.write_text(json.dumps({"examples": [
        g("paper_A", "P001", "substantive"),
        g("paper_A", "P002", "typo-shaped"),
        g("synthetic", "SYN1", "not-an-error"),
        g("synthetic", "SYN2", "not-an-error")]}), encoding="utf-8")
    pis = tmp_path / "pis.jsonl"
    pis.write_text("\n".join(json.dumps(_pis_line(uid, w, []))
                            for uid, w in [("paper_A::P001", 0.3),
                                           ("paper_A::P002", 0.6),
                                           ("synthetic::SYN1", 0.5),
                                           ("synthetic::SYN2", 0.9)]) + "\n",
                   encoding="utf-8")
    preds = tmp_path / "preds.jsonl"
    preds.write_text("\n".join(json.dumps({"uid": u, "pred_label": p}) for u, p in [
        ("paper_A::P001", "substantive"), ("paper_A::P002", "typo-shaped"),
        ("synthetic::SYN1", "not-an-error"), ("synthetic::SYN2", "substantive")]) + "\n",
        encoding="utf-8")
    res = diagnostics.forensics(str(pis), str(preds), str(gold), str(tmp_path / "out"))
    assert res["n"] == 4 and not any(res["exclusions"].values())
    assert sum(res["confusion_gold_to_pred"].values()) == 4
    assert res["strata"]["synthetic"]["n"] == 2
    assert res["strata"]["synthetic"]["n_error"] == 1
    assert res["strata"]["real_papers"]["n_error"] == 0
    assert (tmp_path / "out" / "failure_forensics.json").exists()