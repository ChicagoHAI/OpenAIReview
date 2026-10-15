import json

from benchmarks.perturbation.pis.parsing import (_loads_json_repairing,
                                                  parse_pis_output,
                                                  parse_scalar_output)


OK = """{"hypothesis_restated": "h", "evidence_items": [
  {"source_type": "quote", "description": "quote says L/2", "polarity": "supports_H",
   "strength": 0.8, "reliability": 0.9, "justification": "j"}],
  "self_reported_confidence_h": 0.75}"""


def test_parse_ok():
    pr = parse_pis_output(OK)
    assert pr.status == "ok" and pr.payload is not None
    assert pr.payload["self_reported_confidence_h"] == 0.75
    assert len(pr.payload["evidence_items"]) == 1


def test_parse_with_prose_and_fences():
    pr = parse_pis_output("Sure, here is the audit:\n```json\n" + OK + "\n```\nDone.")
    assert pr.status == "ok" and pr.payload is not None


def test_parse_garbage_fails():
    pr = parse_pis_output("this is not json")
    assert pr.status == "failed" and pr.payload is None and pr.error


def test_parse_nan_rejected():
    pr = parse_pis_output('{"evidence_items": [{"source_type": "quote", "description": "d",'
                          ' "polarity": "supports_H", "strength": NaN, "reliability": 0.5}]}')
    assert pr.status == "failed"


def test_parse_bool_strength_rejected():
    pr = parse_pis_output('{"evidence_items": [{"source_type": "quote", "description": "d",'
                          ' "polarity": "supports_H", "strength": true, "reliability": 0.5}]}')
    assert pr.status == "failed"


def test_parse_unknown_polarity_rejected_not_imputed():
    pr = parse_pis_output('{"evidence_items": [{"source_type": "quote", "description": "d",'
                          ' "polarity": "maybe", "strength": 0.5, "reliability": 0.5}]}')
    assert pr.status == "failed"


def test_parse_clamp_is_repaired_and_tracked():
    pr = parse_pis_output('{"evidence_items": [{"source_type": "quote", "description": "d",'
                          ' "polarity": "supports_H", "strength": 1.3, "reliability": 0.5}]}')
    assert pr.status == "repaired"
    assert any("clamped" in r for r in pr.repairs)


# ---- LaTeX backslash repair (failure mode observed in smoke run) ----

def test_parse_latex_unescaped_backslash_repaired():
    # Exact failure mode from the smoke run (uid paper_001::P005_S0043): the
    # model echoes LaTeX with single backslashes inside JSON strings, e.g.
    # "uses $\mu$ here" -> invalid JSON escape -> doubled -> tracked repair.
    raw = ('{"hypothesis_restated": "h", "evidence_items": ['
           '{"source_type": "quote", "description": "quote uses $\\mu$ here", '
           '"polarity": "supports_H", "strength": 0.5, "reliability": 0.5, '
           '"justification": "j"}], "self_reported_confidence_h": 0.6}')
    pr = parse_pis_output(raw)
    assert pr.status == "repaired"
    assert pr.payload is not None
    assert pr.payload["evidence_items"][0].description == "quote uses $\\mu$ here"
    assert any("backslash" in r for r in pr.repairs)


def test_double_backslash_latex_already_valid_is_ok():
    # A model that escapes correctly ("\\mu" in the JSON text) needs no repair.
    raw = ('{"evidence_items": [{"source_type": "quote", '
           '"description": "uses $\\\\mu$ here", "polarity": "supports_H", '
           '"strength": 0.5, "reliability": 0.5, "justification": "j"}]}')
    pr = parse_pis_output(raw)
    assert pr.status == "ok"
    assert pr.payload["evidence_items"][0].description == "uses $\\mu$ here"


def test_escape_repair_is_identity_on_valid_json():
    # Every valid JSON escape must survive the repair untouched.
    valid = '{"d": "a\\\\b \\n \\t \\u00b5 \\" \\/ \\b \\f \\r e"}'
    obj, repairs, err = _loads_json_repairing(valid)
    assert err is None and repairs == []
    assert obj == json.loads(valid)


def test_latex_backslash_u_without_hex_is_repaired():
    # \underbrace: '\u' is NOT followed by 4 hex digits, so it is invalid and
    # must be repaired (not mistaken for a unicode escape).
    raw = ('{"evidence_items": [{"source_type": "context", '
           '"description": "uses $\\underbrace{x}$", "polarity": "unresolved", '
           '"strength": 0.2, "reliability": 0.2, "justification": "j"}]}')
    pr = parse_pis_output(raw)
    assert pr.status == "repaired"
    assert pr.payload["evidence_items"][0].description == "uses $\\underbrace{x}$"


def test_escape_letter_latex_documented_limitation():
    # \beta begins with the VALID escape '\b', so no repair triggers and the
    # description silently decodes with a control character. Documented
    # limitation: affects only human-readable audit text, never the numeric
    # masses (strength/reliability/polarity are strictly validated regardless).
    raw = ('{"evidence_items": [{"source_type": "quote", "description": "$\\beta$ x", '
           '"polarity": "supports_H", "strength": 0.5, "reliability": 0.5, '
           '"justification": "j"}]}')
    pr = parse_pis_output(raw)
    assert pr.status == "ok"
    assert pr.payload["evidence_items"][0].description == "$\x08eta$ x"


def test_scalar_parse_with_latex_echo_repaired():
    pr = parse_scalar_output('{"note": "$\\mu-1$", "p_substantive": 0.7}')
    assert pr.status == "repaired"
    assert pr.payload["p_substantive"] == 0.7


def test_scalar_parse():
    assert parse_scalar_output('{"p_substantive": 0.7}').payload["p_substantive"] == 0.7
    assert parse_scalar_output("nope").status == "failed"
    pr = parse_scalar_output('{"p_substantive": 1.9}')
    assert pr.status == "repaired" and pr.payload["p_substantive"] == 1.0