import math

import numpy as np
import pytest

from finite_sample_route_graph import (
    Context,
    analyze,
    context_constraints,
    hoeffding_difference_interval,
)


def test_h233_point_case_reproduces_exact_action() -> None:
    result = analyze(
        3,
        (
            Context(0.5, ((0, 2), (1, 2)), (0.0, 0.0), (0.0, 0.0)),
            Context(0.5, ((0, 1),), (0.5,), (0.5,)),
        ),
    )
    assert np.allclose(result["minimax_lottery"], [2 / 3, 0, 1 / 3], atol=1e-9)
    assert result["minimax_half_credit_regret"] == pytest.approx(1 / 12, abs=1e-9)
    assert result["possible_winners"] == [0, 2]
    assert result["certified_unique_winners"] == []


def test_connected_exact_path_certifies_winner() -> None:
    result = analyze(
        3, (Context(1.0, ((0, 1), (1, 2)), (0.3, 0.3), (0.3, 0.3)),)
    )
    assert result["target_difference_bounds"]["0-2"] == pytest.approx(
        {"lower": 0.6, "upper": 0.6}, abs=1e-10
    )
    assert result["possible_winners"] == [0]
    assert result["certified_unique_winners"] == [0]
    assert result["minimax_lottery"] == pytest.approx([1, 0, 0], abs=1e-9)
    assert result["minimax_half_credit_regret"] == pytest.approx(0, abs=1e-9)


def test_disconnected_exact_graph_retains_ambiguity() -> None:
    result = analyze(3, (Context(1.0, ((0, 1),), (0.3,), (0.3,)),))
    assert result["possible_winners"] == [0, 2]
    assert result["certified_unique_winners"] == []
    assert result["target_difference_bounds"]["0-2"] == pytest.approx(
        {"lower": -0.7, "upper": 1.0}, abs=1e-10
    )


def test_interval_widening_cannot_narrow_projection() -> None:
    point = analyze(
        3, (Context(1.0, ((0, 1), (1, 2)), (0.3, 0.3), (0.3, 0.3)),)
    )
    wide = analyze(
        3, (Context(1.0, ((0, 1), (1, 2)), (0.2, 0.2), (0.4, 0.4)),)
    )
    for key, interval in point["target_difference_bounds"].items():
        assert wide["target_difference_bounds"][key]["lower"] <= interval["lower"]
        assert wide["target_difference_bounds"][key]["upper"] >= interval["upper"]


def test_hoeffding_mapping() -> None:
    lower, upper = hoeffding_difference_interval(0.65, 100, 6, 0.05)
    radius = math.sqrt(math.log(240) / 200)
    assert lower == pytest.approx(2 * (0.65 - radius) - 1)
    assert upper == pytest.approx(2 * (0.65 + radius) - 1)


@pytest.mark.parametrize(
    "context",
    [
        Context(1.0, ((0, 1),), (0.5,), (0.4,)),
        Context(1.0, ((0, 1),), (-1.1,), (0.4,)),
        Context(1.0, ((0, 1),), (0.2, 0.2), (0.4,)),
        Context(1.0, ((0, 1), (1, 0)), (0.8, 0.8), (1.0, 1.0)),
    ],
)
def test_invalid_or_infeasible_intervals_fail_closed(context: Context) -> None:
    with pytest.raises(ValueError):
        context_constraints(3, context)
