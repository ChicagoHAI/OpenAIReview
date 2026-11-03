"""Ground-truth field deny-list (leakage guard).

These are evaluation-side / ground-truth field names that must NEVER reach the
PIS evaluator at inference time.

This module intentionally CONTAINS those names as data: it is the mechanism
that keeps them OUT of VerifierInput. The leakage source-scan test therefore
excludes this file by design, and a dedicated AST test enforces that this
module stays data-only (docstring + a single frozenset literal: no imports,
no functions, no subscript/attribute access), so the deny-list can never be
turned into a read path for records.

The PRIMARY structural guard is the allowlist in inputs.py:
build_verifier_input copies ONLY explicitly listed verifier-visible fields,
so a forbidden key cannot pass through even by accident. FORBIDDEN_KEYS is
the belt-and-suspenders layer: build_verifier_input refuses any feature
whose underlying record key is on this list, so a future edit that wires a
ground-truth field into the feature set fails loudly at runtime instead of
leaking silently.
"""

FORBIDDEN_KEYS = frozenset({
    "gold_label", "gold", "label", "rationale", "why_wrong", "correct",
    "pred_label", "prediction", "pred", "verdict", "verdict_pred",
    "confusion", "is_correct", "downstream", "eval_result",
})