"""Known-answer tests for mmrv_conventions.py — the §7.2 convention-grid brute force.

Locks the three published claims: (a) Table I matches exactly one of the 60 grid
variants, and it is the claimed one; (b) the same convention reproduces the
200-episode appendix figure as exact rational lattice points; (c) REALM's V-VIEW
panel draws 14 of its 21 design points and no variant reaches its printed 0.253.
"""
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mmrv_conventions import (  # noqa: E402
    check_fig3, check_fig9, check_realm,
    load_fig3, load_fig9, load_realm_panel, mmrv,
)

CLAIMED = ("leq-xor", "sim", "N")


def test_table1_match_is_unique_and_claimed():
    matches = check_fig3(load_fig3())[0]
    assert matches == [CLAIMED]


def test_fig9_exact_rational_lattice():
    by_panel = load_fig9()
    expected = {
        "toy_packing": Fraction(21, 200),
        "rope_routing": Fraction(307, 2000),
        "t_block_pushing": Fraction(209, 3000),
    }
    for panel, frac in expected.items():
        assert mmrv(by_panel[panel], *CLAIMED) == frac


def test_vview_draws_14_of_21():
    assert len(load_realm_panel("V-VIEW")) == 14


def test_vview_unreachable_and_simpler_value():
    points = load_realm_panel("V-VIEW")
    vals, reaching = check_realm(points)
    assert not reaching  # no variant within 0.0005 of the printed 0.253
    assert abs(vals[("sign<0", "real", "N")] - 0.117) <= 0.0005
