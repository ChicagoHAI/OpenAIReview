import numpy as np
import pytest

from benchmarks.perturbation.pis.analysis.selective import _aurc, aurc_calibration


def test_aurc_exact_known_value():
    e = np.array([0, 1, 0, 1])
    w = np.array([0.1, 0.9, 0.2, 0.8])
    # width-sorted error order [0, 0, 1, 1]; risks at coverages
    # [.25, .5, .75, 1] = [0, 0, 1/3, 1/2]; trapezoid = 7/48.
    assert _aurc(e, w) == pytest.approx(7.0 / 48.0)


def test_aurc_ordering_direction():
    e = np.array([0, 0, 1, 1])
    base = 0.5
    assert base - _aurc(e, np.array([0.1, 0.2, 0.8, 0.9])) > 0   # errors last: helpful
    assert base - _aurc(e, np.array([0.9, 0.8, 0.2, 0.1])) < 0   # errors first: harmful


def test_calibration_perfect_separation_significant():
    e = np.array([0] * 10 + [1] * 10)
    w = np.concatenate([np.linspace(0.01, 0.10, 10), np.linspace(0.90, 0.99, 10)])
    res = aurc_calibration(e, w, n_perm=2000, n_boot=500, seed=0)
    assert res["gain"] > 0.30
    assert res["perm_p_one_sided"] <= 0.01
    assert res["boot_ci95_gain"][0] > 0


def test_calibration_deterministic_and_valid_p():
    e = np.array([1, 0, 0, 1, 0, 1, 0, 0, 1, 0])
    w = np.arange(10) / 10.0
    r1 = aurc_calibration(e, w, n_perm=500, n_boot=200, seed=0)
    r2 = aurc_calibration(e, w, n_perm=500, n_boot=200, seed=0)
    assert r1 == r2
    assert 0.0 <= r1["perm_p_one_sided"] <= 1.0
    assert r1["boot_ci95_gain"][0] <= r1["boot_ci95_gain"][1]