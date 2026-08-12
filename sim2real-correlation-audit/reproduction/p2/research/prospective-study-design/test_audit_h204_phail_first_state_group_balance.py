from __future__ import annotations

import copy
import json

import numpy as np
import pytest

import audit_h204_phail_first_state_group_balance as h204


def canonical() -> dict:
    return json.loads(h204.OUTPUT.read_text())


def test_synthetic_controls_pass() -> None:
    assert all(h204.synthetic_controls().values())


def test_partial_r2_known_policy_shift() -> None:
    labels = ["a", "a", "b", "b"]
    nuisance, full, _, _ = h204.combined_matrix(None, labels)
    outcomes = np.array([[0.0], [0.0], [2.0], [2.0]])
    assert h204.observed_partial_r2(nuisance, full, outcomes) == 1.0


def test_stratum_permutation_replay() -> None:
    outcomes = np.arange(56, dtype=float).reshape(8, 7)
    nuisance, full, _, _ = h204.combined_matrix(
        ["x"] * 4 + ["y"] * 4,
        ["a", "b"] * 4,
    )
    strata = h204.strata_indices(["x"] * 4 + ["y"] * 4, 8)
    first = h204.permuted_partial_r2(
        outcomes,
        nuisance,
        full,
        strata,
        25,
        np.random.Generator(np.random.PCG64(h204.SEED)),
    )[1]
    second = h204.permuted_partial_r2(
        outcomes,
        nuisance,
        full,
        strata,
        25,
        np.random.Generator(np.random.PCG64(h204.SEED)),
    )[1]
    assert np.array_equal(first, second)


def test_analysis_is_json_serializable() -> None:
    outcomes = np.random.default_rng(1).normal(size=(12, 7))
    result = h204.analyze(
        outcomes,
        ["x"] * 6 + ["y"] * 6,
        ["a", "b", "c"] * 4,
        ["x"] * 6 + ["y"] * 6,
        9,
        np.random.Generator(np.random.PCG64(h204.SEED)),
    )
    json.dumps(result)


def test_collinearity_rejected() -> None:
    with pytest.raises(ValueError, match="full design rank"):
        h204.combined_matrix(["a", "a", "b", "b"], ["a", "a", "b", "b"])


def test_classification_paths() -> None:
    base = {"upper_tail_p": 0.5, "observed_partial_r2": 0.0}
    analyses = {
        "policy_conditional_on_date": copy.deepcopy(base),
        "date_conditional_on_policy": copy.deepcopy(base),
        "policy_unadjusted": copy.deepcopy(base),
    }
    assert (
        h204.classify(analyses)
        == "no_material_group_mean_association_at_fixed_resolution"
    )
    analyses["policy_conditional_on_date"] = {
        "upper_tail_p": 0.01,
        "observed_partial_r2": 0.02,
    }
    assert h204.classify(analyses) == "material_policy_initial_state_association"
    analyses["policy_conditional_on_date"] = copy.deepcopy(base)
    analyses["date_conditional_on_policy"] = {
        "upper_tail_p": 0.01,
        "observed_partial_r2": 0.02,
    }
    assert (
        h204.classify(analyses)
        == "material_date_initial_state_association_only"
    )


def test_canonical_validates() -> None:
    h204.validate(canonical())


@pytest.mark.parametrize(
    ("key", "message"),
    [
        ("later_state_or_outcome_opened", "scope"),
        ("causal_or_assignment_effect_established", "causal scope"),
        ("full_physical_balance_established", "balance scope"),
    ],
)
def test_scope_attacks_fail(key: str, message: str) -> None:
    result = canonical()
    result[key] = True
    with pytest.raises(ValueError, match=message):
        h204.validate(result)


def test_classification_attack_fails() -> None:
    result = canonical()
    expected = h204.classify(result["analyses"])
    result["classification"] = (
        "material_policy_initial_state_association"
        if expected != "material_policy_initial_state_association"
        else "no_material_group_mean_association_at_fixed_resolution"
    )
    with pytest.raises(ValueError, match="classification"):
        h204.validate(result)
