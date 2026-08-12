from fractions import Fraction

import pytest

import shared_binary_success_sensitivity as h231


def test_binary_half_tie_identity_without_independence() -> None:
    laws = (
        (Fraction(1), Fraction(0), Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(1, 3), Fraction(1, 6), Fraction(1, 2)),
        (Fraction(1, 4),) * 4,
    )
    for law in laws:
        score = h231.binary_half_tie_score(*law)
        mean_i = law[2] + law[3]
        mean_j = law[1] + law[3]
        assert score == Fraction(1, 2) + Fraction(1, 2) * (mean_i - mean_j)


def test_gradient_cycle_constraints() -> None:
    x = (Fraction(1), Fraction(1, 3), Fraction(0), Fraction(3, 4))
    edges = h231.gradient_edges(x)
    delta = {edge: value - Fraction(1, 2) for edge, value in edges.items()}
    for i in range(len(x)):
        for j in range(i + 1, len(x)):
            for k in range(j + 1, len(x)):
                assert delta[(i, k)] == delta[(i, j)] + delta[(j, k)]


def test_reference_cancels_from_regret() -> None:
    x = (Fraction(1), Fraction(1, 3), Fraction(0), Fraction(3, 4))
    p = (Fraction(1, 2), Fraction(1, 4), Fraction(1, 4), Fraction(0))
    references = h231.reference_vectors(4)
    values = {h231.regret(x, p, reference) for reference in references}
    assert len(values) == 1


def test_exact_vertex_oracle_matches_formula() -> None:
    for k in range(3, 8):
        for reference in h231.reference_vectors(k):
            for lottery in h231.candidate_lotteries(k):
                assert h231.enumerated_regret(lottery, reference) == (
                    h231.formula_regret(lottery)
                )


def test_unique_uniform_minimax_on_exact_grids() -> None:
    for k, denominator in ((3, 12), (4, 8)):
        grid = h231.simplex_grid(k, denominator)
        values = [h231.formula_regret(lottery) for lottery in grid]
        optimum = min(values)
        minimizers = [grid[i] for i, value in enumerate(values) if value == optimum]
        assert minimizers == [tuple(Fraction(1, k) for _ in range(k))]


def test_opposite_unique_winner_witnesses() -> None:
    for k in range(3, 33):
        reference = tuple(Fraction(1, k) for _ in range(k))
        first = (Fraction(1),) + (Fraction(0),) * (k - 1)
        last = (Fraction(0),) * (k - 1) + (Fraction(1),)
        assert h231.winner_set(h231.policy_values(first, reference)) == (0,)
        assert h231.winner_set(h231.policy_values(last, reference)) == (k - 1,)


def test_invalid_inputs_fail_closed() -> None:
    with pytest.raises(ValueError):
        h231.gradient_edges((Fraction(0), Fraction(1)))
    with pytest.raises(ValueError):
        h231.gradient_edges((Fraction(0), Fraction(1), Fraction(2)))
    with pytest.raises(ValueError):
        h231.policy_values(
            (Fraction(0), Fraction(1), Fraction(0)),
            (Fraction(1, 2), Fraction(1, 2)),
        )
    with pytest.raises(ValueError):
        h231.formula_regret((Fraction(1), Fraction(1), Fraction(-1)))


def test_build_and_validate() -> None:
    result = h231.build()
    h231.validate(result)
    assert result["classification"] == (
        "central_result_survives_with_gradient_geometry"
    )
    assert result["closed_forms"]["opponent_reference_cancels"] is True
