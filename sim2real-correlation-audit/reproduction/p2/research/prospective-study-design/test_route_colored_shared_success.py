from fractions import Fraction

import numpy as np

import route_colored_shared_success as h233


def test_component_rank_identity() -> None:
    edges = ((0, 1), (2, 3))
    assert h233.components(5, edges) == [[0, 1], [2, 3], [4]]
    assert np.linalg.matrix_rank(h233.incidence(5, edges)) == 2


def test_binary_route_known_answer() -> None:
    vertices = h233.known_answer_vertices()
    assert len(vertices) == 4
    assert (Fraction(1, 2), Fraction(0), Fraction(0)) in vertices
    assert (Fraction(1, 2), Fraction(0), Fraction(1)) in vertices


def test_exact_optimizer_and_value() -> None:
    p = (Fraction(2, 3), Fraction(0), Fraction(1, 3))
    assert h233.exact_regret(p) == Fraction(1, 12)
    numeric_p, numeric_value = h233.numerical_minimax()
    assert np.allclose(numeric_p, [2 / 3, 0, 1 / 3], atol=1e-9)
    assert abs(numeric_value - 1 / 12) <= 1e-9
    dual_p, dual_value = h233.numerical_dual_minimax()
    assert np.allclose(dual_p, numeric_p, atol=1e-9)
    assert abs(dual_value - numeric_value) <= 1e-9


def test_mutated_optimizer_is_worse() -> None:
    uniform = (Fraction(1, 3),) * 3
    assert h233.exact_regret(uniform) > Fraction(1, 12)
