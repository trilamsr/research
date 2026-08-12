import itertools
from fractions import Fraction

import pytest

import audit_h212_zero_reference_weight_edge_box_boundary as h212


def test_nonnegative_normalization_and_invalid_inputs() -> None:
    assert h212.normalize_nonnegative(
        (Fraction(), Fraction(2), Fraction(2))
    ) == (Fraction(), Fraction(1, 2), Fraction(1, 2))
    for bad in (
        (Fraction(1), Fraction(2)),
        (Fraction(-1), Fraction(1), Fraction(1)),
        (Fraction(), Fraction(), Fraction()),
    ):
        with pytest.raises(ValueError):
            h212.normalize_nonnegative(bad)


def test_raw_endpoint_oracle_known_boundary_answers() -> None:
    controls = (
        ((Fraction(), Fraction(), Fraction(1)), (Fraction(), Fraction(), Fraction(1))),
        ((Fraction(), Fraction(1), Fraction(1)), (Fraction(), Fraction(1, 2), Fraction(1, 2))),
        ((Fraction(), Fraction(1), Fraction(2)), (Fraction(1, 6), Fraction(5, 18), Fraction(5, 9))),
    )
    for raw, lottery in controls:
        assert h212.reduced_regret(raw, lottery) == h212.raw_endpoint_regret(
            raw, lottery
        )


def test_segment_is_exact_for_all_small_census_cases() -> None:
    for raw in tuple(case for case in h212.canonical_cases() if len(case) <= 4):
        info = h212.segment_info(raw)
        for h in h212.segment_probes(raw):
            lottery = h212.segment_lottery(raw, h)
            assert h212.reduced_regret(raw, lottery) == info["value"]
            assert h212.raw_endpoint_regret(raw, lottery) == info["value"]


def test_support_size_one_boundary_geometry() -> None:
    k3 = (Fraction(), Fraction(), Fraction(1))
    info3 = h212.segment_info(k3)
    assert info3["value"] == Fraction(1, 4)
    assert info3["h_max"] == Fraction(1, 2)
    assert h212.segment_lottery(k3, Fraction()) == k3
    assert h212.segment_lottery(k3, Fraction(1, 2)) == (
        Fraction(1, 2),
        Fraction(1, 2),
        Fraction(),
    )

    k4 = (Fraction(), Fraction(), Fraction(), Fraction(1))
    info4 = h212.segment_info(k4)
    assert info4["value"] == Fraction(1, 4)
    assert info4["h_max"] == 0
    assert h212.segment_lottery(k4, Fraction()) == k4


def test_exactly_two_zero_weights_receive_equal_mass() -> None:
    raw = (Fraction(), Fraction(), Fraction(1), Fraction(3))
    info = h212.segment_info(raw)
    assert info["h_max"] == Fraction(1, 8)
    for h in h212.segment_probes(raw):
        p = h212.segment_lottery(raw, h)
        assert p[0] == p[1] == h
        assert h212.reduced_regret(raw, p) == Fraction(1, 4)


def test_at_least_three_zeros_force_unique_reference_lottery() -> None:
    for raw in (
        (Fraction(), Fraction(), Fraction(), Fraction(1)),
        (Fraction(), Fraction(), Fraction(), Fraction(1), Fraction(2)),
        (Fraction(), Fraction(), Fraction(), Fraction(), Fraction(1), Fraction(4)),
    ):
        info = h212.segment_info(raw)
        assert info["h_max"] == 0
        assert h212.segment_lottery(raw, Fraction()) == h212.normalize_nonnegative(raw)


def test_one_zero_has_no_new_face() -> None:
    raw = (Fraction(), Fraction(1), Fraction(2), Fraction(4))
    info = h212.segment_info(raw)
    assert info["h_max"] == Fraction(1, 14)
    for h in h212.segment_probes(raw):
        assert h212.reduced_regret(raw, h212.segment_lottery(raw, h)) == info["value"]


def test_label_invariance_on_boundary() -> None:
    raw = (Fraction(), Fraction(), Fraction(1), Fraction(3))
    expected = h212.segment_info(raw)["value"]
    for permuted in set(itertools.permutations(raw)):
        info = h212.segment_info(permuted)
        assert info["value"] == expected
        for h in h212.segment_probes(permuted):
            assert (
                h212.reduced_regret(permuted, h212.segment_lottery(permuted, h))
                == expected
            )


def test_positive_limit_converges_to_boundary_endpoints() -> None:
    raw = (Fraction(), Fraction(), Fraction(1), Fraction(3))
    boundary = h212.segment_lottery(raw, h212.segment_info(raw)["h_max"])
    errors = []
    for denominator in (10, 100, 1000):
        interior = tuple(
            Fraction(1, denominator) if value == 0 else value for value in raw
        )
        positive = h212.segment_lottery(
            interior, h212.segment_info(interior)["h_max"]
        )
        errors.append(sum(abs(left - right) for left, right in zip(boundary, positive)))
    assert errors[0] > errors[1] > errors[2]


def test_lp_known_answer_and_exact_face_directions() -> None:
    raw = (Fraction(), Fraction(), Fraction(1), Fraction(3))
    info = h212.segment_info(raw)
    value, _ = h212.solve_lp(raw)
    assert abs(value - float(info["value"])) < 1e-10
    for coordinate in range(len(raw)):
        direction = tuple(
            Fraction(index == coordinate) for index in range(len(raw))
        )
        expected_min, expected_max = h212.exact_direction_range(raw, direction)
        observed_min, _ = h212.solve_lp(raw, direction, value_cap=info["value"])
        observed_max, _ = h212.solve_lp(
            raw, direction, maximize=True, value_cap=info["value"]
        )
        assert abs(observed_min - float(expected_min)) < 2e-8
        assert abs(observed_max - float(expected_max)) < 2e-8


def test_rational_reconstruction_fails_closed() -> None:
    assert h212.reconstruct_fraction(1 / 3) == Fraction(1, 3)
    with pytest.raises(ValueError):
        h212.reconstruct_fraction(
            0.123456789, max_denominator=7, tolerance=1e-12
        )


def test_case_census_counts() -> None:
    cases = h212.canonical_cases()
    assert len(cases) == 242
    assert {k: sum(len(raw) == k for raw in cases) for k in range(3, 7)} == {
        3: 14,
        4: 34,
        5: 69,
        6: 125,
    }
