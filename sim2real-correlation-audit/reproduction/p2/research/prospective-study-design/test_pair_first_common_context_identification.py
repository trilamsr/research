from fractions import Fraction

import pytest

from pair_first_common_context_identification import (
    TARGET_LOWER,
    TARGET_UPPER,
    common_target_edges,
    endpoint_regret_census,
    observed_projection,
    policy_values,
    potential_schedule,
    world,
)


def test_pair_conditioned_panel_ties_exactly():
    assert policy_values((Fraction(1, 2),) * 3) == (Fraction(1, 2),) * 3


def test_observationally_equivalent_worlds_reverse_winner():
    low = world(TARGET_LOWER)
    high = world(TARGET_UPPER)
    assert low["observed_projection"] == high["observed_projection"]
    assert low["unique_winner"] == 2
    assert high["unique_winner"] == 0


def test_every_compatible_target_has_bounded_potential_schedule():
    for target in (
        TARGET_LOWER,
        Fraction(1, 3),
        Fraction(1, 2),
        Fraction(2, 3),
        TARGET_UPPER,
    ):
        schedule = potential_schedule(target)
        assert common_target_edges(schedule) == (target,) * 3
        assert all(
            Fraction() <= value <= 1
            for contexts in schedule.values()
            for value in contexts.values()
        )
        assert all(row[2] == Fraction(1, 2) for row in observed_projection(schedule))


def test_endpoint_census_gives_every_singleton_one_third_floor():
    result = endpoint_regret_census()
    assert result["endpoint_completions_exhausted"] == 8
    assert [row["text"] for row in result["singleton_worst_regret"]] == [
        "1/3",
        "1/3",
        "1/3",
    ]


def test_incompatible_targets_refuse():
    with pytest.raises(ValueError, match="compatible"):
        potential_schedule(Fraction(1, 5))
    with pytest.raises(ValueError, match=r"\[0,1\]"):
        policy_values((Fraction(2), Fraction(), Fraction()))
