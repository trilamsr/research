from fractions import Fraction

import pair_first_arbitrary_roster_identification as h183


def test_every_fixed_k_passes_exact_checks() -> None:
    for k in range(3, 33):
        row = h183.check_k(k)
        assert row["pair_count"] == k * (k - 1) // 2
        assert row["pair_conditioned_winner_set"] == [0, 1, 2]
        assert row["low_unique_winner"] == 2
        assert row["high_unique_winner"] == 0
        assert row["cross_world_extreme_regret"]["text"] == f"1/{k}"


def test_closed_forms_at_large_roster() -> None:
    k = 101
    row = h183.check_k(k)
    assert row["low_values"][0]["text"] == "99/101"
    assert row["low_values"][1]["text"] == "199/202"
    assert row["low_values"][2]["text"] == "100/101"
    assert row["low_values"][3]["text"] == "49/101"


def test_added_policy_gap_is_positive() -> None:
    for k in (4, 7, 32, 101):
        low = h183.expected_values(k, "low")
        assert min(low[:3]) - max(low[3:]) == Fraction(k - 1, 2 * k)


def test_observed_law_is_projected_from_each_potential_world() -> None:
    for k in (3, 7, 101):
        low = h183.potential_schedule(k, h183.LOW)
        high = h183.potential_schedule(k, h183.HIGH)
        assert h183.observed_projection(k, low) == h183.observed_projection(k, high)
        assert h183.common_target_edges(low) == h183.edge_map(k, h183.LOW)
        assert h183.common_target_edges(high) == h183.edge_map(k, h183.HIGH)


def test_build_and_schema() -> None:
    result = h183.build()
    h183.validate(result)
    assert result["checked_k_count"] == 30
    assert result["for_every_integer_k_ge_3_there_exists_this_construction"]
    assert result["complete_pair_support_identifies_common_context_winner"] is False
