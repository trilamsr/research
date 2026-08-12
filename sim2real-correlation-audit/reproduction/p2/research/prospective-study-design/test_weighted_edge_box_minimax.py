import itertools
from fractions import Fraction

import pytest

import weighted_edge_box_minimax as h188


def test_formula_matches_raw_endpoint_oracle() -> None:
    for raw in h188.cases()[:5]:
        info = h188.minimax_segment(raw)
        for h in (info["h_min"], (info["h_min"] + info["h_max"]) / 2, info["h_max"]):
            p = h188.segment_lottery(raw, h)
            assert h188.weighted_formula_regret(raw, p) == (
                h188.enumerated_weighted_regret(raw, p)
            )


def test_uniform_reduces_to_h186() -> None:
    for k in range(3, 33):
        raw = (Fraction(1),) * k
        info = h188.minimax_segment(raw)
        assert info["value"] == Fraction(k - 1, 4 * k)
        assert info["h_max"] == 0
        assert h188.segment_lottery(raw, Fraction()) == (Fraction(1, k),) * k


def test_nonunique_interior_is_not_strong_water_filling() -> None:
    raw = (
        Fraction(1, 10),
        Fraction(1, 5),
        Fraction(3, 10),
        Fraction(2, 5),
    )
    h = Fraction(1, 40)
    p = h188.segment_lottery(raw, h)
    assert p == (
        Fraction(7, 40),
        Fraction(19, 90),
        Fraction(221, 840),
        Fraction(221, 630),
    )
    assert h188.weighted_formula_regret(raw, p) == Fraction(17, 80)
    ratios = [p[index] / raw[index] for index in range(1, 4)]
    assert len(set(ratios)) > 1


def test_tie_regimes_and_permutations() -> None:
    for raw in (
        (Fraction(1), Fraction(1), Fraction(2)),
        (Fraction(1), Fraction(2), Fraction(2)),
        (Fraction(1), Fraction(1), Fraction(1), Fraction(4)),
    ):
        for permuted in (raw, tuple(reversed(raw))):
            info = h188.minimax_segment(permuted)
            for h in (info["h_min"], info["h_max"]):
                p = h188.segment_lottery(permuted, h)
                assert h188.weighted_formula_regret(permuted, p) == info["value"]
    raw = (Fraction(1), Fraction(2), Fraction(3), Fraction(5))
    for permuted in itertools.permutations(raw):
        info = h188.minimax_segment(permuted)
        for h in (info["h_min"], info["h_max"]):
            p = h188.segment_lottery(permuted, h)
            assert h188.weighted_formula_regret(permuted, p) == info["value"]


def test_raw_weight_normalization_and_invalid_inputs() -> None:
    raw = (Fraction(1), Fraction(2), Fraction(3))
    scaled = tuple(7 * value for value in raw)
    assert h188.minimax_segment(raw)["value"] == h188.minimax_segment(scaled)["value"]
    assert h188.segment_lottery(raw, Fraction()) == h188.segment_lottery(
        scaled, Fraction()
    )
    with pytest.raises(ValueError):
        h188.minimax_segment((Fraction(1), Fraction(2)))
    with pytest.raises(ValueError):
        h188.minimax_segment((Fraction(1), Fraction(), Fraction(2)))
    with pytest.raises(ValueError):
        h188.segment_lottery(raw, Fraction(100))
    with pytest.raises(ValueError):
        h188.segment_lottery(raw, Fraction(-1, 100))


def test_build_and_validate() -> None:
    result = h188.build()
    h188.validate(result)
    assert result["closed_form"]["uniqueness_condition"] == "r_(2)=r_(3)"
