from __future__ import annotations

import copy
import json
import math

import numpy as np
import pytest

import audit_h203_phail_first_state_temporal_structure as h203


def canonical() -> dict:
    return json.loads(h203.OUTPUT.read_text())


def test_synthetic_controls_pass() -> None:
    assert all(h203.synthetic_controls().values())


def test_known_successive_distance() -> None:
    states = np.zeros((3, 7))
    states[:, 0] = [0.0, 1.0, 3.0]
    assert math.isclose(
        h203.mean_successive_squared_distance(states, [np.arange(3)]),
        2.5,
    )


def test_group_pair_accounting() -> None:
    rows = [
        {"episode_id": f"e{i}", "timestamp": i, "policy": "a" if i < 3 else "b"}
        for i in range(6)
    ]
    groups = h203.group_indices(rows, "policy")
    assert len(groups) == 2
    assert h203.pair_count(groups) == 4


def test_permutation_replay_is_exact() -> None:
    states = np.arange(70, dtype=float).reshape(10, 7)
    groups = [np.arange(10)]
    first = h203.permutation_distribution(
        states, groups, 25, np.random.Generator(np.random.PCG64(h203.SEED))
    )
    second = h203.permutation_distribution(
        states, groups, 25, np.random.Generator(np.random.PCG64(h203.SEED))
    )
    assert np.array_equal(first, second)


def test_classification_boundaries() -> None:
    base = {
        "observed_to_permutation_median_ratio": 1.0,
        "two_sided_p": 0.5,
    }
    analyses = {
        "global": copy.deepcopy(base),
        "within_policy": copy.deepcopy(base),
        "within_utc_date": copy.deepcopy(base),
    }
    assert (
        h203.classify(analyses)
        == "no_detectable_temporal_structure_at_fixed_resolution"
    )
    analyses["global"]["two_sided_p"] = 0.01
    analyses["global"]["observed_to_permutation_median_ratio"] = 0.9
    assert h203.classify(analyses) == "material_global_temporal_structure"
    analyses["global"]["observed_to_permutation_median_ratio"] = 0.95
    assert (
        h203.classify(analyses)
        == "secondary_only_or_small_temporal_structure"
    )


def test_canonical_validates() -> None:
    h203.validate(canonical())


@pytest.mark.parametrize(
    ("key", "message"),
    [
        ("later_state_or_outcome_opened", "scope"),
        ("recorded_chronology_treated_as_physical_order", "chronology scope"),
        ("independence_established", "independence scope"),
    ],
)
def test_scope_attacks_fail(key: str, message: str) -> None:
    result = canonical()
    result[key] = True
    with pytest.raises(ValueError, match=message):
        h203.validate(result)


def test_classification_attack_fails() -> None:
    result = canonical()
    result["classification"] = "material_global_temporal_structure"
    if h203.classify(result["analyses"]) == result["classification"]:
        result["classification"] = "no_detectable_temporal_structure_at_fixed_resolution"
    with pytest.raises(ValueError, match="classification"):
        h203.validate(result)
