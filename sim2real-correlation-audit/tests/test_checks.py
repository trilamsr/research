"""Known-answer tests for correlation_audit.py's five checks.

Fixtures are the released extraction CSVs; expected values are the
paper-verified ground truth quoted in PAPER.md. If these fail, the audited
code or the released data changed -- fix neither from here.
"""
import csv
import sys
from math import comb
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from correlation_audit import audit  # noqa: E402


def _rows(fname):
    with open(ROOT / fname) as f:
        return list(csv.DictReader(l for l in f if not l.startswith("#")))


@pytest.fixture(scope="module")
def roboworld_9a():
    rows = [r for r in _rows("data/survey-roboworld.csv") if r["panel"].startswith("9a")]
    points = [(float(r["x_real"]), float(r["y_sim"])) for r in rows]
    units = [r["series"] for r in rows]
    return audit(points, units)


@pytest.fixture(scope="module")
def digital_cousins():
    rows = _rows("data/survey-digital-cousins.csv")
    points = [(float(r["x_real"]), float(r["y_sim"])) for r in rows]
    units = [r["policy"] for r in rows]
    return audit(points, units)


# ---------------------------------------------------------------- RoboWorld 9a

class TestRoboWorld9a:
    def test_pearson_r(self, roboworld_9a):
        assert roboworld_9a.r == pytest.approx(0.9888, abs=5e-4)

    def test_leverage_max_drop_one(self, roboworld_9a):
        # Removing one of eight policies moves r by ~0.191 -- the headline finding.
        assert roboworld_9a.leverage == pytest.approx(0.191, abs=2e-3)
        assert roboworld_9a.one_unit_carries

    def test_fisher_z_interval(self, roboworld_9a):
        lo, hi = roboworld_9a.fisher_z
        assert lo == pytest.approx(0.937, abs=2e-3)
        assert hi == pytest.approx(0.998, abs=2e-3)


# ---------------------------------------------------------- Digital Cousins

class TestDigitalCousins:
    def test_pearson_r(self, digital_cousins):
        assert digital_cousins.r == pytest.approx(0.9094, abs=5e-4)

    def test_leverage_max_drop_one(self, digital_cousins):
        assert digital_cousins.leverage == pytest.approx(0.013, abs=2e-3)
        assert not digital_cousins.one_unit_carries

    def test_min_permutation_p(self, digital_cousins):
        # k=4 -> 4! labelings -> min attainable p = 1/24
        assert digital_cousins.k_units == 4
        assert digital_cousins.min_p == pytest.approx(1 / 24)

    def test_bootstrap_distinct_values(self, digital_cousins):
        assert digital_cousins.atom_ceiling == 35
        assert not digital_cousins.bootstrap_meaningful


# ------------------------------------------------------------- Combinatorics

BOOTSTRAP_ATOMS = {2: 3, 3: 10, 4: 35, 5: 126, 6: 462, 7: 1716, 8: 6435}


@pytest.mark.parametrize("k,expected", sorted(BOOTSTRAP_ATOMS.items()))
def test_bootstrap_atom_ceiling(k, expected):
    """atom_ceiling must equal C(2k-1, k) for k = 2..8."""
    # Synthetic data: 2 points per unit so every k >= 2 gives >= 4 points
    # with variance on both axes.
    points, units = [], []
    for i in range(k):
        points += [(i, i + 0.1), (i + 0.5, i + 0.4)]
        units += [f"u{i}", f"u{i}"]
    a = audit(points, units)
    assert a.k_units == k
    assert a.atom_ceiling == expected == comb(2 * k - 1, k)


# --------------------------------------------------------------- Granularity

@pytest.mark.parametrize("n_points,n_episodes,expected_fp", [
    (12, 16, 0.192),
    (21, 25, 0.525),
])
def test_granularity_false_pass_rate(n_points, n_episodes, expected_fp):
    """false_pass_rate = min(1, 0.001 * N * n_episodes) with 3-decimal slack."""
    points = [(i, i + ((-1) ** i) * 0.3) for i in range(n_points)]
    units = [f"u{i}" for i in range(n_points)]
    a = audit(points, units, n_episodes=n_episodes, reported_mmrv=0.1)
    assert a.granularity is not None
    assert a.granularity["false_pass_rate"] == pytest.approx(expected_fp, abs=1e-9)
    assert a.granularity["informative"] == (expected_fp <= 0.35)
