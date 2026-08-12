from fractions import Fraction

import pytest

import audit_h213_support_constrained_zero_reference_boundary as h213


def test_support_constraint_rejects_zero_policy_mass() -> None:
    raw = (Fraction(), Fraction(1), Fraction(2))
    h213.validate_support_constraint(raw, (Fraction(), Fraction(1, 3), Fraction(2, 3)))
    with pytest.raises(ValueError):
        h213.validate_support_constraint(
            raw, (Fraction(1, 10), Fraction(3, 10), Fraction(3, 5))
        )


def test_any_zero_set_has_value_quarter_and_unique_reference() -> None:
    for raw in (
        (Fraction(), Fraction(1), Fraction(2)),
        (Fraction(), Fraction(), Fraction(1), Fraction(3)),
        (Fraction(), Fraction(), Fraction(), Fraction(1)),
    ):
        solution = h213.constrained_solution(raw)
        assert solution["value"] == Fraction(1, 4)
        assert solution["unique"]
        assert solution["optimizer"] == h213.h212.normalize_nonnegative(raw)
        assert h213.constrained_regret(raw, solution["optimizer"]) == Fraction(1, 4)


def test_exactly_one_zero_creates_value_gap() -> None:
    raw = (Fraction(), Fraction(1), Fraction(2), Fraction(4))
    reference = h213.h212.normalize_nonnegative(raw)
    unrestricted = h213.h212.segment_info(raw)
    assert unrestricted["value"] == Fraction(13, 56)
    assert Fraction(1, 4) - unrestricted["value"] == reference[1] / 8
    for h in h213.h212.segment_probes(raw):
        with pytest.raises(ValueError):
            h213.validate_support_constraint(
                raw, h213.h212.segment_lottery(raw, h)
            )


def test_exactly_two_zeros_change_face_only() -> None:
    raw = (Fraction(), Fraction(), Fraction(1), Fraction(3))
    unrestricted = h213.h212.segment_info(raw)
    assert unrestricted["value"] == Fraction(1, 4)
    assert unrestricted["h_max"] == Fraction(1, 8)
    constrained = h213.constrained_solution(raw)
    assert constrained["optimizer"] == h213.h212.segment_lottery(raw, Fraction())


def test_three_zeros_change_nothing() -> None:
    raw = (Fraction(), Fraction(), Fraction(), Fraction(1))
    unrestricted = h213.h212.segment_info(raw)
    constrained = h213.constrained_solution(raw)
    assert unrestricted["value"] == constrained["value"] == Fraction(1, 4)
    assert unrestricted["h_max"] == 0
    assert h213.h212.segment_lottery(raw, Fraction()) == constrained["optimizer"]


def test_zero_winner_identity_and_equality() -> None:
    raw = (Fraction(), Fraction(1), Fraction(2))
    p = h213.h212.normalize_nonnegative(raw)
    assert h213.support_dispersion(raw, p) == 0
    assert h213.constrained_regret(raw, p) == Fraction(1, 4)
    other = (Fraction(), Fraction(1, 2), Fraction(1, 2))
    assert h213.support_dispersion(raw, other) > 0
    assert h213.constrained_regret(raw, other) > Fraction(1, 4)


def test_raw_endpoint_parity_at_constrained_optimum() -> None:
    for raw in (
        (Fraction(), Fraction(1), Fraction(2)),
        (Fraction(), Fraction(), Fraction(1), Fraction(3)),
        (Fraction(), Fraction(1), Fraction(2), Fraction(3), Fraction(4)),
    ):
        p = h213.h212.normalize_nonnegative(raw)
        assert h213.constrained_regret(raw, p) == h213.h212.raw_endpoint_regret(
            raw, p
        )


def test_support_grid_respects_mask_and_unique_equality() -> None:
    raw = (Fraction(), Fraction(), Fraction(1), Fraction(1))
    equalities = []
    for p in h213.support_grid(raw, 8):
        h213.validate_support_constraint(raw, p)
        regret = h213.constrained_regret(raw, p)
        assert regret >= Fraction(1, 4)
        if regret == Fraction(1, 4):
            equalities.append(p)
    assert equalities == [(Fraction(), Fraction(), Fraction(1, 2), Fraction(1, 2))]


def test_lp_value_and_unique_face() -> None:
    raw = (Fraction(), Fraction(1), Fraction(2), Fraction(4))
    reference = h213.h212.normalize_nonnegative(raw)
    value, _ = h213.solve_support_lp(raw)
    assert abs(value - 0.25) < 1e-10
    for coordinate in range(len(raw)):
        observed_min, _ = h213.solve_support_lp(
            raw, coordinate, value_cap=Fraction(1, 4)
        )
        observed_max, _ = h213.solve_support_lp(
            raw, coordinate, maximize=True, value_cap=Fraction(1, 4)
        )
        assert abs(observed_min - float(reference[coordinate])) < 2e-8
        assert abs(observed_max - float(reference[coordinate])) < 2e-8


def test_positive_interior_reproduces_h212() -> None:
    raw = (Fraction(1), Fraction(2), Fraction(3), Fraction(4))
    assert h213.constrained_solution(raw)["value"] == h213.h212.segment_info(raw)[
        "value"
    ]
