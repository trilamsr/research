from fractions import Fraction
from pathlib import Path

import pytest

import interior_route_law_nonidentification as h238


HERE = Path(__file__).resolve().parent


def test_pair_interval_has_constant_width_and_exact_boundary() -> None:
    for observed in (Fraction(0), Fraction(1, 5), Fraction(1, 2), Fraction(1)):
        low, high = h238.pair_target_interval(observed)
        assert high - low == Fraction(1, 2)
        assert (low < Fraction(1, 2) < high) == (0 < observed < 1)


def test_every_policy_is_possible_interior_unique_winner() -> None:
    profile = (Fraction(0), Fraction(1, 4), Fraction(3, 4))
    witnesses = h238.unique_winner_witnesses(profile)
    assert set(witnesses) == {0, 1, 2}
    for winner, missing in witnesses.items():
        assert h238.winner_set(h238.target_order_values(profile, missing)) == (
            winner,
        )


def test_range_one_boundary_excludes_minimum_profile_policies() -> None:
    profile = (Fraction(0), Fraction(0), Fraction(1, 2), Fraction(1))
    witnesses = h238.unique_winner_witnesses(profile)
    assert 0 not in witnesses
    assert 1 not in witnesses
    assert set(witnesses) == {2, 3}


def test_regret_formula_matches_every_binary_missing_context_vertex() -> None:
    profiles = (
        (Fraction(0), Fraction(1, 4), Fraction(1, 2)),
        (Fraction(0), Fraction(1, 3), Fraction(2, 3), Fraction(5, 6)),
    )
    for profile in profiles:
        for lottery in h238.candidate_lotteries(len(profile)):
            assert h238.enumerated_worst_regret(
                profile, lottery
            ) == h238.formula_worst_regret(profile, lottery)


def test_constant_profile_reduces_to_h231_formula() -> None:
    profile = (Fraction(2, 5),) * 4
    for lottery in h238.candidate_lotteries(4):
        assert h238.formula_worst_regret(profile, lottery) == (
            Fraction(1, 4) * (1 - min(lottery))
        )


def test_common_offset_invariance() -> None:
    profile = (Fraction(0), Fraction(1, 5), Fraction(3, 5))
    shifted = tuple(value + Fraction(1, 5) for value in profile)
    for lottery in h238.candidate_lotteries(3):
        assert h238.formula_worst_regret(
            profile, lottery
        ) == h238.formula_worst_regret(shifted, lottery)


def test_non_strict_interior_mutation_is_rejected() -> None:
    boundary = (Fraction(0), Fraction(1, 2), Fraction(1))
    assert h238.profile_range(boundary) == 1
    assert set(h238.unique_winner_witnesses(boundary)) != {0, 1, 2}


def test_removing_weighted_observed_term_changes_heterogeneous_regret() -> None:
    profile = (Fraction(0), Fraction(1, 4), Fraction(3, 4))
    lottery = (Fraction(1, 2), Fraction(1, 3), Fraction(1, 6))
    correct = h238.formula_worst_regret(profile, lottery)
    mutated = Fraction(1, 4) * (
        1 + max(a - p for a, p in zip(profile, lottery))
    )
    assert mutated != correct


def test_invalid_inputs_fail_closed() -> None:
    with pytest.raises(ValueError):
        h238.pair_target_interval(Fraction(-1, 10))
    with pytest.raises(ValueError):
        h238.observed_score((Fraction(0), Fraction(1)), 0, 1)
    with pytest.raises(ValueError):
        h238.formula_worst_regret(
            (Fraction(0), Fraction(1, 2), Fraction(1)),
            (Fraction(1), Fraction(1), Fraction(-1)),
        )


def test_full_build_and_census() -> None:
    result = h238.build()
    h238.validate(result)
    assert result["classification"] == (
        "relative_open_within_additive_shared_success_model"
    )
    census = result["exhaustive_census"]
    assert census["total_profiles"] > 0
    assert census["interior_profiles"] > 0
    assert census["boundary_profiles"] > 0


def test_manuscript_and_supplement_bind_the_h238_result() -> None:
    paper = (HERE / "PAPER-identification-to-operation.md").read_text(
        encoding="utf-8"
    )
    supplement = (
        HERE / "SUPPLEMENT-identification-to-operation.md"
    ).read_text(encoding="utf-8")
    assert "range \\(D<1\\)" in paper
    assert "shared-success model (Supplement S4)" in paper
    assert "If \\(D<1\\)" in supplement
    assert "\\mathcal R(p;a)" in supplement
