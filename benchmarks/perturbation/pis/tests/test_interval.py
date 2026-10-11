import json
import math
import random

import pytest

from benchmarks.perturbation.pis.interval import PISInterval


def test_zero_information_gives_maximal_interval():
    iv = PISInterval(0.0, 0.0, 1.0)
    assert iv.L == 0.0 and iv.U == 1.0 and iv.width == 1.0


def test_fully_committed_positive_evidence():
    iv = PISInterval(1.0, 0.0, 0.0)
    assert (iv.L, iv.U, iv.width) == (1.0, 1.0, 0.0)


def test_fully_committed_negative_evidence():
    iv = PISInterval(0.0, 1.0, 0.0)
    assert (iv.L, iv.U, iv.width) == (0.0, 0.0, 0.0)


def test_bounds_property_random():
    rng = random.Random(0)
    checked = 0
    for _ in range(2000):
        a, b = rng.random(), rng.random()
        if a + b > 1.0:
            continue
        iv = PISInterval(a, b, 1.0 - a - b)
        assert 0.0 <= iv.L <= iv.U <= 1.0
        assert math.isclose(iv.width, iv.m_unresolved, abs_tol=1e-12)
        assert math.isclose(iv.U, 1.0 - iv.m_against, abs_tol=1e-12)
        assert math.isclose(iv.L + iv.U + iv.m_against, 1.0 + iv.m_support, abs_tol=1e-12)
        checked += 1
    assert checked > 500


@pytest.mark.parametrize("args", [(-0.1, 0.0, 1.1), (0.5, 0.6, 0.0), (0.3, 0.3, 0.3),
                                  (1.2, 0.0, 0.0), (float("nan"), 0.0, 1.0)])
def test_invalid_masses_raise(args):
    with pytest.raises(ValueError):
        PISInterval(*args)


def test_serialization_roundtrip_exact():
    iv = PISInterval(0.123456789012345, 0.234567890123456, 1 - 0.123456789012345 - 0.234567890123456)
    assert PISInterval.from_json(iv.to_json()) == iv
    assert PISInterval.from_dict(iv.to_dict()) == iv
    d = iv.to_dict()
    assert json.loads(json.dumps(d)) == d