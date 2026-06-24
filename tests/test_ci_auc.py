"""Unit tests for the conference-study AUC + bootstrap-CI helpers (ci_auc.py).

Uses tiny in-memory count tables (no result files), so the math is checkable by
hand: two high-quality papers with few comments and two low-quality papers with
more, giving perfect low-over-high separation (AUC = 1.0).
"""

import math
import sys
from pathlib import Path

_ANALYSES = Path(__file__).resolve().parents[1] / "benchmarks" / "conference_study" / "analyses"
if str(_ANALYSES) not in sys.path:
    sys.path.insert(0, str(_ANALYSES))

from ci_auc import (  # noqa: E402
    DISPATCH,
    auc_from,
    bootstrap,
    bootstrap_tiers,
    by_proxy_recs,
    by_proxy_totals,
)
from compute_auc import cell_summary  # noqa: E402


# ---- auc_from: pairwise accuracy over the high x low outer product ----

def test_auc_from_perfect_separation():
    auc, hits, total = auc_from([1, 1], [2, 2])  # every low > every high
    assert auc == 1.0 and hits == 4.0 and total == 4


def test_auc_from_reversed():
    auc, _, _ = auc_from([2, 2], [1, 1])
    assert auc == 0.0


def test_auc_from_ties_get_half_credit():
    auc, hits, total = auc_from([1], [1])
    assert auc == 0.5 and hits == 0.5 and total == 1


def test_auc_from_empty_side_is_nan():
    auc, hits, total = auc_from([], [1, 2])
    assert math.isnan(auc) and hits == 0.0 and total == 0


# ---- cell_summary / bootstrap on a toy cell ----

def _toy_cell():
    """One proxy: 2 high papers (2 comments each), 2 low papers (5 each)."""
    counts = {
        "p1": {"total": 2, "major": 1, "moderate": 1, "minor": 0},
        "p2": {"total": 2, "major": 1, "moderate": 1, "minor": 0},
        "p3": {"total": 5, "major": 2, "moderate": 2, "minor": 1},
        "p4": {"total": 5, "major": 2, "moderate": 2, "minor": 1},
    }
    mem = {
        "p1": [{"pair": 1, "side": "high"}], "p2": [{"pair": 1, "side": "high"}],
        "p3": [{"pair": 1, "side": "low"}], "p4": [{"pair": 1, "side": "low"}],
    }
    return counts, mem


def test_cell_summary_point_estimates():
    s = cell_summary(*_toy_cell())
    assert s["c_high"] == 2.0
    assert s["c_low"] == 5.0
    assert s["delta"] == 3.0
    assert s["auc_overall"] == 1.0  # low always exceeds high
    assert s["auc_major"] == 1.0


def test_bootstrap_tiers_ci_shape():
    ci = bootstrap_tiers(by_proxy_recs(*_toy_cell()), ("total", "major"))
    for tier in ("total", "major"):
        lo, hi = ci[tier]
        assert 0.0 <= lo <= hi <= 1.0
        assert hi == 1.0  # degenerate perfect-separation data


def test_bootstrap_overall_and_per_proxy():
    (lo, hi), per_proxy = bootstrap(by_proxy_totals(*_toy_cell()))
    assert 0.0 <= lo <= hi <= 1.0
    assert 1 in per_proxy  # CI present for the one proxy


def test_dispatch_covers_the_three_kinds():
    assert set(DISPATCH) == {"comment_volume", "by_proxy", "by_severity"}
