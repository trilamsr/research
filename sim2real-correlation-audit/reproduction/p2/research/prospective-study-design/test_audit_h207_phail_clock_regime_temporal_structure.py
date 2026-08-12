from __future__ import annotations

import copy
import json
import math

import numpy as np
import pytest

import audit_h207_phail_clock_regime_temporal_structure as h207


def canonical() -> dict:
    return json.loads(h207.OUTPUT.read_text())


def test_synthetic_controls_pass() -> None:
    assert all(h207.synthetic_controls().values())


def test_transform_known_answer() -> None:
    transformed = h207.transform(
        np.vstack([h207.BASE, h207.BASE + h207.HALF_WIDTHS / math.sqrt(3)])
    )
    assert np.allclose(transformed[0], 0)
    assert np.allclose(transformed[1], 1)


def test_known_successive_distance_and_pooling() -> None:
    states = np.zeros((6, 7))
    states[:3, 0] = [0.0, 1.0, 3.0]
    states[3:, 0] = [0.0, 1.0, 3.0]
    statistics = h207.three_statistics(
        states, {1: np.arange(3), 2: np.arange(3, 6)}
    )
    assert math.isclose(statistics["pooled_within_regime"], 2.5)
    assert math.isclose(statistics["regime_1"], 2.5)
    assert math.isclose(statistics["regime_2"], 2.5)


def test_restricted_permutation_never_crosses_groups() -> None:
    groups = {1: np.arange(4), 2: np.arange(4, 10)}
    draw = h207.draw_restricted_permutations(groups, np.random.default_rng(207))
    assert set(draw[1]) == set(groups[1])
    assert set(draw[2]) == set(groups[2])
    assert set(draw[1]).isdisjoint(set(draw[2]))


def test_permutation_replay_is_exact() -> None:
    states = np.arange(70, dtype=float).reshape(10, 7)
    groups = {1: np.arange(4), 2: np.arange(4, 10)}
    first = h207.permutation_distributions(
        states, groups, 25, np.random.Generator(np.random.PCG64(h207.SEED))
    )
    second = h207.permutation_distributions(
        states, groups, 25, np.random.Generator(np.random.PCG64(h207.SEED))
    )
    for key in h207.ANALYSIS_KEYS:
        assert np.array_equal(first[key], second[key])


def test_classification_boundaries() -> None:
    base = {
        "observed_to_permutation_median_ratio": 1.0,
        "two_sided_p": 0.5,
    }
    analyses = {key: copy.deepcopy(base) for key in h207.ANALYSIS_KEYS}
    assert (
        h207.classify(analyses)
        == "no_detectable_clock_regime_temporal_structure_at_fixed_resolution"
    )
    analyses["pooled_within_regime"]["two_sided_p"] = 0.01
    analyses["pooled_within_regime"][
        "observed_to_permutation_median_ratio"
    ] = 0.9
    assert (
        h207.classify(analyses)
        == "material_pooled_clock_regime_temporal_structure"
    )
    analyses["pooled_within_regime"][
        "observed_to_permutation_median_ratio"
    ] = 0.95
    assert (
        h207.classify(analyses)
        == "regime_specific_or_small_clock_regime_temporal_structure"
    )
    analyses = {key: copy.deepcopy(base) for key in h207.ANALYSIS_KEYS}
    analyses["regime_2"]["two_sided_p"] = 0.005
    assert (
        h207.classify(analyses)
        == "regime_specific_or_small_clock_regime_temporal_structure"
    )


def test_stage_does_not_compute_achieved_state_order_statistic() -> None:
    stage = h207.staged_validation(h207.load_join())
    assert stage["achieved_state_order_statistic_computed"] is False
    assert stage["pooled_pair_count"] == 592
    assert stage["synthetic_rehearsal_complete"] is True


def test_canonical_validates() -> None:
    h207.validate(canonical())


def test_rebuild_equivalence_ignores_only_os_build_label() -> None:
    retained = canonical()
    candidate = copy.deepcopy(retained)
    candidate["run_identity"]["platform"] = "different-patch-release"
    assert h207.rebuild_equivalent(candidate, retained)
    candidate["analyses"]["pooled_within_regime"][
        "observed_mean_successive_squared_distance"
    ] += 1e-9
    assert not h207.rebuild_equivalent(candidate, retained)


@pytest.mark.parametrize(
    ("key", "message"),
    [
        ("performance_or_later_state_opened", "performance scope"),
        ("clock_regime_treated_as_session", "regime scope"),
        ("independence_established", "independence scope"),
        ("confirmatory_claim_authorized", "confirmatory scope"),
    ],
)
def test_scope_attacks_fail(key: str, message: str) -> None:
    result = canonical()
    result[key] = True
    with pytest.raises(ValueError, match=message):
        h207.validate(result)


def test_classification_attack_fails() -> None:
    result = canonical()
    result["classification"] = "material_pooled_clock_regime_temporal_structure"
    if h207.classify(result["analyses"]) == result["classification"]:
        result[
            "classification"
        ] = "no_detectable_clock_regime_temporal_structure_at_fixed_resolution"
    with pytest.raises(ValueError, match="classification"):
        h207.validate(result)
