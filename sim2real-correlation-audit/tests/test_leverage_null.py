"""Known-answer tests for leverage_null.py's drop-one null simulation.

All assertions run at the --quick replicate count (4,000) with the script's
own per-cell seeds, so they are deterministic and the whole file stays fast
(well under a second). The reference values are the independently computed
40,000-rep gate numbers quoted in leverage_null.GATE_REFS; the quick-mode
tolerances below are wide enough for 4,000-rep Monte-Carlo error.
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import leverage_null as ln  # noqa: E402

QUICK_NSIM = 4_000  # matches the script's --quick gate replicate count


def test_gate_roboworld_fires():
    # k=8, rho=0.989 fixed, m=1, w=1.0; observed swing 0.191. Reference:
    # P ~= 0.002, null median ~= 0.007 -- a healthy design almost never
    # produces RoboWorld 9a's swing.
    _, mx = ln.simulate_max_dr(QUICK_NSIM, 8, 1, 0.989, 1.0, seed=1000)
    assert float(np.mean(mx >= 0.191)) < 0.01
    assert float(np.median(mx)) < 0.02


def test_gate_digital_cousins_clears():
    # k=4, rho=0.909 fixed, m=1, w=1.0; observed swing 0.013. Reference:
    # P ~= 0.868 -- the observed swing is smaller than typical for a healthy
    # design of this size.
    _, mx = ln.simulate_max_dr(QUICK_NSIM, 4, 1, 0.909, 1.0, seed=1001)
    p = float(np.mean(mx >= 0.013))
    assert 0.75 < p < 0.95
    assert abs(float(np.median(mx)) - 0.097) < 0.03


def test_gate_cosmos_k3_null_is_huge():
    # k=3, rho=0.718 fixed, m=1, w=1.0; observed swing 0.124. Reference:
    # P ~= 0.603, null median ~= 1.036 -- at k=3 drop-one leaves two points
    # (r = +/-1), so enormous swings are the healthy-design NORM.
    _, mx = ln.simulate_max_dr(QUICK_NSIM, 3, 1, 0.718, 1.0, seed=1002)
    assert abs(float(np.mean(mx >= 0.124)) - 0.603) < 0.05
    assert abs(float(np.median(mx)) - 1.036) < 0.15


def test_molmospaces_open_from_csv():
    # The open panel has 4 points and reproduces the printed R = 0.85.
    k, r = ln.molmospaces_open()
    assert k == 4
    assert abs(r - 0.85) < 0.01
