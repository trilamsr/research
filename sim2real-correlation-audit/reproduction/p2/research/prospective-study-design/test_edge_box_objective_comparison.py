from fractions import Fraction

import pytest

import edge_box_objective_comparison as h232


def test_zero_matrix_makes_every_candidate_maximal() -> None:
    for k in range(3, 7):
        matrix = h232.zero_matrix(k)
        for lottery in h232.candidate_lotteries(k):
            assert h232.min_pure_opponent_margin(lottery, matrix) == 0


def test_endpoint_oracle_matches_robust_formula() -> None:
    for k in range(3, 6):
        for lottery in h232.candidate_lotteries(k):
            assert h232.enumerated_robust_margin(lottery) == (
                h232.formula_robust_margin(lottery)
            )


def test_uniform_is_unique_on_exact_grids() -> None:
    for k, denominator in ((3, 12), (4, 8), (5, 5)):
        grid = h232.simplex_grid(k, denominator)
        values = [h232.formula_robust_margin(lottery) for lottery in grid]
        optimum = max(values)
        maximizers = [grid[i] for i, value in enumerate(values) if value == optimum]
        assert maximizers == [tuple(Fraction(1, k) for _ in range(k))]
        assert optimum == Fraction(-(k - 1), 2 * k)


def test_no_action_is_necessary_across_completions() -> None:
    for k in range(3, 8):
        for excluded in range(k):
            winner = (excluded + 1) % k
            matrix = h232.condorcet_completion(k, winner)
            h232.verify_unique_condorcet_action(matrix, winner, k)
            assert winner != excluded


def test_same_uniform_action_has_different_values() -> None:
    for k in range(3, 33):
        robust_margin = Fraction(-(k - 1), 2 * k)
        borda_regret = h232.borda_uniform_regret(k)
        assert robust_margin == -2 * borda_regret
        assert Fraction(1, 2) + robust_margin / 2 == Fraction(k + 1, 4 * k)


def test_invalid_inputs_fail_closed() -> None:
    with pytest.raises(ValueError):
        h232.formula_robust_margin((Fraction(1), Fraction(0)))
    with pytest.raises(ValueError):
        h232.formula_robust_margin(
            (Fraction(1), Fraction(1), Fraction(-1))
        )
    with pytest.raises(ValueError):
        h232.min_pure_opponent_margin(
            (Fraction(1), Fraction(0), Fraction(0)),
            {(0, 1): Fraction(1, 2)},
        )


def test_build_and_validate() -> None:
    result = h232.build()
    h232.validate(result)
    assert result["classification"] == "same_uniform_action_different_objectives"
