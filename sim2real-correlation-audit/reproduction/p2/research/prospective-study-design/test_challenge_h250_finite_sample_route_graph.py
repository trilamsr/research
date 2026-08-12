import copy
import json

import pytest

import challenge_h250_finite_sample_route_graph as challenge


def test_vertex_challenge_passes() -> None:
    result = challenge.build()
    assert result["status"] == "pass"
    assert result["cases"]["h233_point_case"]["target_vertex_count"] > 0


def test_lottery_mutation_is_rejected() -> None:
    result = challenge.build()
    mutated = copy.deepcopy(result)
    mutated["cases"]["h233_point_case"]["minimax_lottery"] = [1, 0, 0]
    with pytest.raises(ValueError, match="lottery"):
        challenge.compare(
            json.loads(challenge.PRODUCER_RESULT.read_text(encoding="utf-8")), mutated
        )
