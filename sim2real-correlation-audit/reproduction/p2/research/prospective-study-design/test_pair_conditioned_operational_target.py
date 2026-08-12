from fractions import Fraction

import pytest

from pair_conditioned_operational_target import (
    LOWER_INDEX_ROUTE,
    OPTIMAL_ROUTE,
    PI,
    THETA,
    build,
    missing_edge_decision,
    route_value,
    support_matrix,
    tournament_values,
)


def test_cyclic_edges_have_exact_pairwise_route():
    assert OPTIMAL_ROUTE == {"01": 0, "02": 2, "12": 1}
    assert route_value(OPTIMAL_ROUTE) == Fraction(3, 4)


def test_lower_index_rule_has_exact_regret():
    lower = route_value(LOWER_INDEX_ROUTE)
    assert lower == Fraction(7, 12)
    assert route_value(OPTIMAL_ROUTE) - lower == Fraction(1, 6)


def test_tournament_ties_despite_routing_advantage():
    assert tournament_values() == (Fraction(1, 2),) * 3
    result = build()
    assert result["known_answer"]["unique_global_policy_identified"] is False


def test_missing_positive_weight_edge_refuses_value():
    reduced = {"01": THETA["01"], "12": THETA["12"]}
    refusal = missing_edge_decision(reduced)
    assert refusal["decision"] == "not_identified"
    assert refusal["positive_weight_edges_missing"] == ["02"]
    with pytest.raises(ValueError, match="not identified"):
        route_value(OPTIMAL_ROUTE, theta=reduced, weights=PI)


def test_invalid_route_choice_refuses():
    invalid = dict(OPTIMAL_ROUTE)
    invalid["01"] = 2
    with pytest.raises(ValueError, match="not in pair"):
        route_value(invalid)


def test_support_matrix_preserves_required_refusals():
    rows = {row["target"]: row["decision"] for row in support_matrix()}
    assert rows["pair_routing_rule"] == "supported_conditionally"
    assert rows["common_context_single_policy_selection"].startswith("refused")
    assert rows["per_policy_task_success"].startswith("refused")
    assert rows["evaluator_or_simulator_causal_effect"].startswith("refused")
    assert rows["new_policy_task_site_or_context_transport"].startswith("refused")
    assert rows["outcome_adaptive_pair_weights"].startswith("refused")
    assert rows["unmeasured_positive_weight_edge_decision"].startswith("refused")


def test_h151_h152_boundary_is_hash_bound_and_retained():
    boundary = build()["upstream_boundary"]
    assert boundary["independent_challenge_agrees"] is True
    assert boundary["compatible_common_context_unique_winners"] == [2, 0]
    assert boundary["every_singleton_common_context_regret_floor"]["text"] == "1/3"
    assert boundary["common_context_target_identified"] is False


def test_field_collection_is_not_authorized():
    result = build()
    assert result["real_site_qualified"] is False
    assert result["field_collection_authorized"] is False
    assert result["standalone_paper_novelty_claimed"] is False
