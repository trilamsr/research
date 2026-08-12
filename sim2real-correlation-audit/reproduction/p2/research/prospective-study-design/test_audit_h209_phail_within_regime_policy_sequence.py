from __future__ import annotations

import copy
import json

import numpy as np
import pytest

import audit_h209_phail_within_regime_policy_sequence as h209


def canonical() -> dict:
    return json.loads(h209.OUTPUT.read_text())


def test_synthetic_controls_pass() -> None:
    assert all(h209.synthetic_controls().values())


def test_adjacency_known_answers() -> None:
    groups = {1: np.arange(4), 2: np.arange(4, 8)}
    constant = np.array(["a"] * 8)
    alternating = np.array(["a", "b"] * 4)
    assert all(value == 1 for value in h209.three_statistics(constant, groups).values())
    assert all(
        value == 0 for value in h209.three_statistics(alternating, groups).values()
    )


def test_analytic_expectation_known_answer() -> None:
    labels = np.array(["a", "a", "b", "a", "a", "b"])
    groups = {1: np.arange(3), 2: np.arange(3, 6)}
    expected = h209.analytic_expectations(labels, groups)
    assert np.isclose(expected["pooled_within_regime"], 1 / 3)
    assert np.isclose(expected["regime_1"], 1 / 3)
    assert np.isclose(expected["regime_2"], 1 / 3)


def test_restricted_permutation_replay() -> None:
    labels = np.array(["a", "b", "c", "d"] * 5)
    groups = {1: np.arange(8), 2: np.arange(8, 20)}
    first = h209.permutation_distributions(
        labels, groups, 25, np.random.Generator(np.random.PCG64(h209.SEED))
    )
    second = h209.permutation_distributions(
        labels, groups, 25, np.random.Generator(np.random.PCG64(h209.SEED))
    )
    assert all(
        np.array_equal(first[key], second[key]) for key in h209.ANALYSIS_KEYS
    )


def test_classification_boundaries() -> None:
    base = {
        "observed_minus_permutation_median": 0.0,
        "two_sided_p": 0.5,
    }
    analyses = {key: copy.deepcopy(base) for key in h209.ANALYSIS_KEYS}
    assert (
        h209.classify(analyses)
        == "no_detectable_policy_sequence_structure_at_fixed_resolution"
    )
    analyses["pooled_within_regime"]["two_sided_p"] = 0.01
    analyses["pooled_within_regime"]["observed_minus_permutation_median"] = 0.10
    assert h209.classify(analyses) == "material_pooled_policy_sequence_structure"
    analyses["pooled_within_regime"]["observed_minus_permutation_median"] = 0.05
    assert (
        h209.classify(analyses)
        == "regime_specific_or_small_policy_sequence_structure"
    )


def test_stage_keeps_ordered_statistic_closed() -> None:
    stage = h209.staged_validation(h209.load_join())
    assert stage["material_ordered_policy_adjacency_computed"] is False
    assert stage["pooled_pair_count"] == 592
    assert stage["synthetic_rehearsal_complete"] is True


def test_canonical_validates() -> None:
    h209.validate(canonical())


@pytest.mark.parametrize(
    ("key", "message"),
    [
        ("permutation_reference_treated_as_assignment_law", "assignment scope"),
        ("state_or_performance_opened", "data scope"),
        ("scheduler_or_cause_identified", "cause scope"),
        ("outcome_analysis_authorized", "outcome scope"),
    ],
)
def test_scope_attacks_fail(key: str, message: str) -> None:
    result = canonical()
    result[key] = True
    with pytest.raises(ValueError, match=message):
        h209.validate(result)


def test_classification_attack_fails() -> None:
    result = canonical()
    result["classification"] = "material_pooled_policy_sequence_structure"
    if h209.classify(result["analyses"]) == result["classification"]:
        result[
            "classification"
        ] = "no_detectable_policy_sequence_structure_at_fixed_resolution"
    with pytest.raises(ValueError, match="classification"):
        h209.validate(result)
