import random

from benchmarks.perturbation.pis.evidence import (EvidenceItem, aggregate_evidence)
from benchmarks.perturbation.pis.interval import PISInterval


def item(polarity, strength, reliability=1.0, src="quote", desc="d"):
    return EvidenceItem(source_type=src, description=desc, polarity=polarity,
                        strength=strength, reliability=reliability)


S, A = "supports_H", "against_H"


def test_no_evidence_is_maximally_uncertain():
    iv = aggregate_evidence([])
    assert (iv.L, iv.U, iv.width) == (0.0, 1.0, 1.0)


def test_certain_support_collapses_to_one():
    iv = aggregate_evidence([item(S, 1.0)])
    assert (iv.L, iv.U, iv.width) == (1.0, 1.0, 0.0)


def test_certain_against_collapses_to_zero():
    iv = aggregate_evidence([item(A, 1.0)])
    assert (iv.L, iv.U, iv.width) == (0.0, 0.0, 0.0)


def test_conflict_becomes_vacuity_not_cancellation():
    # Certain evidence both ways must NOT average to a confident 0.5 point;
    # it must leave the interval fully unresolved.
    iv = aggregate_evidence([item(S, 1.0), item(A, 1.0)])
    assert (iv.L, iv.U, iv.width) == (0.0, 1.0, 1.0)


def test_strong_conflict_yields_wide_interval():
    iv = aggregate_evidence([item(S, 0.8, 0.8), item(A, 0.8, 0.8)])
    assert iv.width > 0.5  # 0.36^2 + 0.64^2 = 0.5392


def test_unresolved_items_cannot_narrow_interval():
    base = aggregate_evidence([item(S, 0.7)])
    with_extra = aggregate_evidence([item(S, 0.7),
                                     item("unresolved", 0.9, 0.9, src="missing_evidence")])
    assert base == with_extra


def test_corroboration_reduces_width():
    w1 = aggregate_evidence([item(S, 0.5)]).width
    w2 = aggregate_evidence([item(S, 0.5), item(S, 0.5, src="context")]).width
    assert w2 < w1
    assert abs(w1 - 0.5) < 1e-12 and abs(w2 - 0.25) < 1e-12


def test_single_weak_witness():
    iv = aggregate_evidence([item(S, 0.3)])
    assert abs(iv.L - 0.3) < 1e-12 and abs(iv.U - 1.0) < 1e-12 and abs(iv.width - 0.7) < 1e-12


def test_order_independence_bitwise():
    items = [item(S, 0.4, 0.9, src="quote", desc=f"d{i}") for i in range(3)] + \
            [item(A, 0.6, 0.5, src="context", desc=f"e{i}") for i in range(3)]
    rng = random.Random(1)
    shuffled = items[:]
    rng.shuffle(shuffled)
    assert aggregate_evidence(items) == aggregate_evidence(shuffled)


def test_commitment_is_strength_times_reliability():
    it = item(S, 0.5, 0.5)
    assert abs(it.commitment - 0.25) < 1e-12


def test_strict_validation_rejects_out_of_range():
    import pytest
    with pytest.raises(ValueError):
        EvidenceItem("quote", "d", S, 1.5, 1.0)
    with pytest.raises(ValueError):
        EvidenceItem("quote", "d", "bogus_polarity", 0.5, 1.0)


def test_from_payload_clamps_and_reports():
    it, repairs = EvidenceItem.from_payload(
        {"source_type": "quote", "description": "d", "polarity": S,
         "strength": 1.4, "reliability": -0.2})
    assert it.strength == 1.0 and it.reliability == 0.0 and len(repairs) == 2


def test_interval_always_valid_for_random_items():
    rng = random.Random(2)
    for _ in range(500):
        items = [item(rng.choice([S, A, "unresolved"]), rng.random(), rng.random())
                 for _ in range(rng.randint(0, 6))]
        iv = aggregate_evidence(items)
        assert 0.0 <= iv.L <= iv.U <= 1.0
        assert isinstance(iv, PISInterval)