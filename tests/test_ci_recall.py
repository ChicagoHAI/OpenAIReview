"""Unit tests for the perturbation recall + bootstrap-CI helpers (ci_recall.py).

Uses tiny in-memory (detected, injected) counts (no result files), so the math
is checkable by hand: papers whose per-paper recall is a round fraction, and a
degenerate case where every paper has the same recall so the CI collapses onto
the point estimate.
"""

import math
import sys
from pathlib import Path

import numpy as np
import pytest

_PERT = Path(__file__).resolve().parents[1] / "benchmarks" / "perturbation"
if str(_PERT) not in sys.path:
    sys.path.insert(0, str(_PERT))

import ci_recall  # noqa: E402
from ci_recall import DISPATCH, boot_ci, paper_rows  # noqa: E402


CATEGORIES = {"surface": "Surface", "logic": "Reasoning"}


def _per_paper():
    """Two papers, each with surface + logic error types.

    p1: surface 1/2 + logic 2/2  -> 3 detected of 4 injected.
    p2: surface 0/2 only         -> 0 detected of 2 injected.
    """
    return {
        "d/p1": {"surface": (1, 2), "logic": (2, 2)},
        "d/p2": {"surface": (0, 2)},
    }


# ---- paper_rows: per-paper aggregation and category filtering ----

def test_paper_rows_sums_error_types_per_paper():
    assert paper_rows(_per_paper()) == [(3, 4), (0, 2)]


def test_paper_rows_filters_by_category():
    # Surface keeps both papers' surface counts.
    assert paper_rows(_per_paper(), CATEGORIES, "Surface") == [(1, 2), (0, 2)]
    # Reasoning (logic) exists only on p1; p2 is dropped.
    assert paper_rows(_per_paper(), CATEGORIES, "Reasoning") == [(2, 2)]


def test_paper_rows_drops_zero_injected_paper():
    per_paper = {"d/p1": {"surface": (1, 2)}, "d/p3": {"surface": (0, 0)}}
    assert paper_rows(per_paper) == [(1, 2)]


# ---- boot_ci: pooled recall point estimate and CI ----

def test_boot_ci_point_estimate_and_counts():
    point, lo, hi, det, inj = boot_ci([(3, 4), (0, 2)])
    assert point == 0.5 and det == 3 and inj == 6
    assert 0.0 <= lo <= point <= hi <= 1.0


def test_boot_ci_pins_exact_bounds_under_fixed_seed():
    # Reseed the module generator so the resampling is reproducible, then pin the
    # exact percentile bounds for papers with genuine between-paper variance. This
    # checks the percentile core itself, which the inequality assertions above and
    # the degenerate case below cannot.
    saved = ci_recall.RNG
    ci_recall.RNG = np.random.default_rng(0)
    try:
        point, lo, hi, detected, injected = boot_ci([(1, 2), (3, 4), (0, 5)])
    finally:
        ci_recall.RNG = saved
    assert (detected, injected) == (4, 11)
    assert point == pytest.approx(4 / 11)
    assert lo == pytest.approx(0.0)
    assert hi == pytest.approx(0.75)
    assert lo < point < hi  # a real spread, not a collapsed interval


def test_boot_ci_degenerate_equal_recall_collapses_ci():
    # Every paper has recall 1/2, so every resample pools to 1/2 exactly.
    point, lo, hi, det, inj = boot_ci([(1, 2), (3, 6)])
    assert point == 0.5 and lo == 0.5 and hi == 0.5


def test_boot_ci_empty_is_nan():
    point, lo, hi, det, inj = boot_ci([])
    assert math.isnan(point) and math.isnan(lo) and math.isnan(hi)
    assert det == 0 and inj == 0


def test_dispatch_covers_the_two_kinds():
    assert set(DISPATCH) == {"by_model", "by_category"}
