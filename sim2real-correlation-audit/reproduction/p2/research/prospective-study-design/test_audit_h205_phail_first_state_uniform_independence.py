from __future__ import annotations

import copy
import json

import numpy as np
import pytest

import audit_h205_phail_first_state_uniform_independence as h205


def canonical() -> dict:
    return json.loads(h205.OUTPUT.read_text())


def test_synthetic_controls_pass() -> None:
    assert all(h205.synthetic_controls().values())


def test_known_ks_arithmetic() -> None:
    states = np.tile(np.linspace(-1.0, 1.0, 5)[:, None], (1, 7))
    assert np.allclose(h205.ks_per_joint(states), 0.2)


def test_uniform_cdf_clamps_outside_support() -> None:
    states = np.tile(np.array([-3.0, -2.0, 2.0, 3.0])[:, None], (1, 7))
    assert np.allclose(h205.ks_per_joint(states), 0.5)


def test_perfect_correlation_detected() -> None:
    first = np.linspace(-1.0, 1.0, 101)
    states = np.column_stack([first] * 7)
    pairs, maximum = h205.correlation_diagnostics(states)
    assert np.allclose(pairs, 1.0)
    assert maximum == pytest.approx(1.0)


def test_support_accounting() -> None:
    states = np.array(
        [
            [0.0] * 7,
            [1.01] + [0.0] * 6,
            [-1.02] + [0.0] * 6,
        ]
    )
    support = h205.support_diagnostics(states)
    assert support["per_joint_outside_count"] == [2, 0, 0, 0, 0, 0, 0]
    assert support["total_outside_count"] == 2
    assert support["maximum_absolute_exceedance"] == pytest.approx(0.02)


def test_reference_replay() -> None:
    first = h205.simulated_omnibus(
        99, np.random.Generator(np.random.PCG64(h205.SEED))
    )
    second = h205.simulated_omnibus(
        99, np.random.Generator(np.random.PCG64(h205.SEED))
    )
    assert np.array_equal(first[0], second[0])
    assert np.array_equal(first[1], second[1])


@pytest.mark.parametrize(
    ("marginal", "dependence", "expected"),
    [
        (
            {"upper_tail_p": 0.01, "observed": 0.08},
            {"upper_tail_p": 0.01, "observed": 0.15},
            "material_marginal_and_joint_departure",
        ),
        (
            {"upper_tail_p": 0.01, "observed": 0.08},
            {"upper_tail_p": 0.02, "observed": 0.15},
            "material_marginal_departure_only",
        ),
        (
            {"upper_tail_p": 0.02, "observed": 0.08},
            {"upper_tail_p": 0.01, "observed": 0.15},
            "material_joint_dependence_only",
        ),
        (
            {"upper_tail_p": 0.01, "observed": 0.079},
            {"upper_tail_p": 0.50, "observed": 0.01},
            "small_or_diagnostic_only_departure",
        ),
        (
            {"upper_tail_p": 0.50, "observed": 0.20},
            {"upper_tail_p": 0.50, "observed": 0.20},
            "no_material_uniform_independence_departure_at_fixed_resolution",
        ),
    ],
)
def test_classification_boundaries(
    marginal: dict, dependence: dict, expected: str
) -> None:
    assert h205.classify(marginal, dependence) == expected


def test_canonical_validates() -> None:
    h205.validate(canonical())


@pytest.mark.parametrize(
    ("key", "message"),
    [
        ("commanded_draw_or_rng_validity_established", "commanded"),
        ("later_state_or_outcome_opened", "later"),
        ("full_physical_balance_established", "physical"),
    ],
)
def test_scope_attacks_fail(key: str, message: str) -> None:
    result = canonical()
    result[key] = True
    with pytest.raises(ValueError, match=message):
        h205.validate(result)


def test_classification_attack_fails() -> None:
    result = canonical()
    expected = h205.classify(
        result["marginal_uniformity"], result["joint_dependence"]
    )
    result["classification"] = (
        "material_marginal_departure_only"
        if expected != "material_marginal_departure_only"
        else "no_material_uniform_independence_departure_at_fixed_resolution"
    )
    with pytest.raises(ValueError, match="classification"):
        h205.validate(result)


def test_simulation_count_attack_fails() -> None:
    result = canonical()
    result["marginal_uniformity"]["reference_simulations"] -= 1
    with pytest.raises(ValueError, match="marginal simulations"):
        h205.validate(result)
