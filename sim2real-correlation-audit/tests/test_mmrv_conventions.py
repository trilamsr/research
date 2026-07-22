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
    SIMPLER_CONVENTION, SUBJECT_CONVENTION, TIE_EXCLUSIVE_CONVENTION,
    check_fig3, check_fig9, check_realm,
    load_fig3, load_fig9, load_realm_panel, mmrv,
)

CLAIMED = ("leq-xor", "sim", "N")


def _reference_simpler_mmrv(points):
    """SIMPLER's MMRV transcribed literally from its released code / paper Eq. 1:
    mean over items of max over j of |R_i - R_j| * 1[(S_i > S_j) != (R_i > R_j)].
    """
    n = len(points)
    total = 0
    for i in range(n):
        best = 0
        for j in range(n):
            if j == i:
                continue
            (Ri, Si), (Rj, Sj) = points[i], points[j]
            if (Si > Sj) != (Ri > Rj):
                best = max(best, abs(Ri - Rj))
        total += best
    return total / n


def test_simpler_convention_matches_reference_semantics():
    """The grid's leq-xor/real/N is exactly SIMPLER's strict-> XOR convention.

    Hand-checked set includes both one-sided tie cases:
      pts[0] vs pts[1]: real tie, sim differs  -> violation, weight |dR| = 0
      pts[1] vs pts[2]: sim tie, real differs  -> violation, weight 0.3
      pts[0] vs pts[2]: concordant             -> no violation
    Per-item maxima 0, 0.3, 0 -> MMRV = 0.1 exactly.
    """
    pts = [(Fraction(1, 2), Fraction(1, 2)),
           (Fraction(1, 2), Fraction(3, 10)),
           (Fraction(1, 5), Fraction(3, 10))]
    assert SIMPLER_CONVENTION == ("leq-xor", "real", "N")
    got = mmrv(pts, *SIMPLER_CONVENTION)
    assert got == Fraction(1, 10)
    assert abs(float(got) - _reference_simpler_mmrv(
        [(float(r), float(s)) for r, s in pts])) < 1e-12
    # tie-exclusive reading sees no violating pair at all here
    assert mmrv(pts, *TIE_EXCLUSIVE_CONVENTION) == 0


def test_simpler_convention_matches_reference_on_real_data():
    for panel, pts in load_fig9().items():
        floats = [(float(r), float(s)) for r, s in pts]
        assert abs(float(mmrv(pts, *SIMPLER_CONVENTION))
                   - _reference_simpler_mmrv(floats)) < 1e-12
    vv = load_realm_panel("V-VIEW")
    assert abs(mmrv(vv, *SIMPLER_CONVENTION) - _reference_simpler_mmrv(vv)) < 1e-12


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
    # SIMPLER's actual convention (leq-xor/real/N) gives the quoted 0.117;
    # the tie-exclusive variant coincides to print precision on these 14 points.
    assert abs(vals[SIMPLER_CONVENTION] - 0.117) <= 0.0005
    assert abs(vals[TIE_EXCLUSIVE_CONVENTION] - 0.117) <= 0.0005


def test_subject_paper_differs_from_simpler_only_in_gap_side():
    assert SUBJECT_CONVENTION[0] == SIMPLER_CONVENTION[0] == "leq-xor"
    assert SUBJECT_CONVENTION[2] == SIMPLER_CONVENTION[2] == "N"
    assert (SUBJECT_CONVENTION[1], SIMPLER_CONVENTION[1]) == ("sim", "real")
