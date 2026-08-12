from fractions import Fraction

import full_roster_edge_box_minimax as h186


def test_endpoint_enumeration_matches_formula() -> None:
    for k in range(3, 7):
        for weights in h186.candidate_weights(k):
            assert h186.enumerated_regret(k, weights) == h186.formula_regret(
                k, weights
            )


def test_every_deterministic_singleton_has_exact_value() -> None:
    for k in range(3, 33):
        expected = Fraction(k - 1, 2 * k)
        for policy in range(k):
            assert h186.formula_regret(k, h186.singleton(k, policy)) == expected


def test_uniform_randomization_halves_deterministic_value() -> None:
    for k in range(3, 101):
        randomized = h186.formula_regret(k, h186.uniform(k))
        deterministic = h186.formula_regret(k, h186.singleton(k))
        assert randomized == Fraction(k - 1, 4 * k)
        assert 2 * randomized == deterministic


def test_asymmetric_candidates_are_strictly_worse_than_uniform() -> None:
    for k in (3, 4, 7, 16, 32):
        optimum = h186.formula_regret(k, h186.uniform(k))
        for weights in h186.candidate_weights(k)[1:]:
            assert h186.formula_regret(k, weights) > optimum


def test_hidden_context_map_covers_valid_extremes() -> None:
    assert h186.compatible_hidden_outcome(h186.LOW) == 0
    assert h186.compatible_hidden_outcome(h186.HALF) == Fraction(1, 2)
    assert h186.compatible_hidden_outcome(h186.HIGH) == 1


def test_full_schedules_project_to_target_and_common_observed_law() -> None:
    values = (
        h186.LOW,
        Fraction(1, 3),
        Fraction(2, 5),
        h186.HALF,
        Fraction(3, 5),
        Fraction(2, 3),
        h186.HIGH,
    )
    for k in (3, 4, 7, 16, 32):
        target = h186.witness_target_edges(k, values)
        schedule = h186.potential_schedule(k, target)
        assert h186.target_projection(schedule) == target
        assert set(h186.observed_projection(schedule).values()) == {h186.HALF}


def test_build_and_schema() -> None:
    result = h186.build()
    h186.validate(result)
    assert result["endpoint_exhaustion_k_max"] == 6
    assert result["closed_forms"]["unique_randomized_minimizer"] == (
        "uniform over all K policies"
    )
    assert all(
        witness["all_edges_projected"]
        for witness in result["compatibility_witnesses"]
    )
