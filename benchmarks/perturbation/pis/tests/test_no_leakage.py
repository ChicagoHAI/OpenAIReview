import ast
import json
import re
from pathlib import Path

import pytest

from benchmarks.perturbation.pis.backends import MockBackend
from benchmarks.perturbation.pis.evaluator import PISEvaluator
from benchmarks.perturbation.pis.inputs import build_verifier_input

PKG = Path(__file__).resolve().parents[1]

SENTINELS = ["SENTINEL_GOLD_XYZ", "SENTINEL_RATIONALE_XYZ", "SENTINEL_WHY_XYZ"]

RESPONSE = json.dumps({
    "hypothesis_restated": "h",
    "evidence_items": [{"source_type": "quote", "description": "d",
                        "polarity": "supports_H", "strength": 0.5,
                        "reliability": 0.5, "justification": "j"}],
    "self_reported_confidence_h": 0.6})


def _record():
    return {"paper": "paper_A", "perturbation_id": "P001_S0001",
            "error": "numeric_parameter", "original": "$w = L/2$",
            "perturbed": "$w = L/4$", "contradicts_quote": "we choose $w = L/2$",
            "quote_source": "generator", "gold_label": SENTINELS[0],
            "rationale": SENTINELS[1], "why_wrong": SENTINELS[2]}


def test_runtime_sentinel_leakage_check():
    backend = MockBackend([RESPONSE])
    ev = PISEvaluator(backend, max_retries=0)
    vin = build_verifier_input(_record())
    res = ev.evaluate_batch([vin], max_new_tokens=16)[0]
    assert backend.calls, "no prompt was captured"
    for sent in SENTINELS:
        for prompt in backend.calls:
            assert sent not in prompt
        assert sent not in json.dumps(res.to_dict())


def test_source_scan_inference_modules_never_mention_gold():
    # Inference-side modules must not reference ground-truth / evaluation-side
    # fields. leakage.py is deliberately EXCLUDED: it is the data-only
    # deny-list that enumerates those names precisely in order to block them
    # (kept honest by test_leakage_module_is_data_only below).
    pattern = re.compile(r"\b(gold_label|rationale|why_wrong|pred_label|gold_set)\b")
    for name in ("evaluator.py", "prompts.py", "parsing.py", "backends.py",
                 "evidence.py", "interval.py", "inputs.py"):
        src = (PKG / name).read_text(encoding="utf-8")
        assert not pattern.search(src), f"{name} references ground-truth fields"


def test_leakage_module_is_data_only():
    # leakage.py must contain ONLY the FORBIDDEN_KEYS assignment (+ docstring):
    # no imports, functions, subscripts or attribute access, so the deny-list
    # can never become a read path for records.
    tree = ast.parse((PKG / "leakage.py").read_text(encoding="utf-8"))
    banned = (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.AsyncFunctionDef,
              ast.ClassDef, ast.Subscript, ast.Attribute, ast.Lambda,
              ast.If, ast.For, ast.While, ast.Try)
    n_calls = 0
    for node in ast.walk(tree):
        assert not isinstance(node, banned), \
            "leakage.py must stay data-only (docstring + FORBIDDEN_KEYS literal)"
        if isinstance(node, ast.Call):
            n_calls += 1
    assert n_calls == 1, "expected exactly the frozenset(...) constructor call"


def test_default_feature_set_reads_no_forbidden_keys():
    from benchmarks.perturbation.pis.inputs import (_FEATURE_TO_RECORD_KEY,
                                                    DEFAULT_FEATURE_SET)
    from benchmarks.perturbation.pis.leakage import FORBIDDEN_KEYS
    assert set(DEFAULT_FEATURE_SET) == set(_FEATURE_TO_RECORD_KEY)
    for feat, key in _FEATURE_TO_RECORD_KEY.items():
        assert key not in FORBIDDEN_KEYS, f"feature {feat!r} would read {key!r}"


def test_feature_guard_blocks_forbidden_wiring(monkeypatch):
    # Simulate a future (bad) edit that maps a feature onto a ground-truth
    # record key; the runtime guard in build_verifier_input must refuse it.
    import benchmarks.perturbation.pis.inputs as inputs_mod
    monkeypatch.setitem(inputs_mod._FEATURE_TO_RECORD_KEY, "gold_label", "gold_label")
    with pytest.raises(ValueError, match="forbidden"):
        inputs_mod.build_verifier_input(_record(), feature_set=("gold_label",))


def test_no_imports_of_production_verifier_modules():
    # Scope note: this guard protects the PIS EVALUATOR CORE (evaluator.py,
    # prompts.py, backends.py, evidence/interval/inputs) — the code that
    # computes intervals from verifier-visible inputs must not depend on the
    # production verifier. Step-D pipeline scripts (convert_predictions,
    # run_surrogate_verifier) are evaluation-side glue that deliberately
    # interfaces with repo artifacts; they are excluded here and covered by
    # their own tests.
    pattern = re.compile(r"^\s*(from|import)\s+.*\b(verify|score|models)\b", re.M)
    for f in PKG.rglob("*.py"):
        if "tests" in f.parts or "convert_predictions" in f.name \
                or "run_surrogate_verifier" in f.name:
            continue
        assert not pattern.search(f.read_text(encoding="utf-8")), \
            f"{f} imports a production verifier module"