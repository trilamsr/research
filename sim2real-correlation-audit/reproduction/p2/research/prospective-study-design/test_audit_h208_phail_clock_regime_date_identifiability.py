from __future__ import annotations

import copy
import json
import math

import pytest

import audit_h208_phail_clock_regime_date_identifiability as h208


def canonical() -> dict:
    return json.loads(h208.OUTPUT.read_text())


def test_synthetic_controls_pass() -> None:
    assert all(h208.synthetic_controls().values())


def test_exact_nested_alias() -> None:
    rows = [
        {"date": "a", "group": 1, "policy": "p"},
        {"date": "a", "group": 1, "policy": "q"},
        {"date": "b", "group": 2, "policy": "p"},
        {"date": "b", "group": 2, "policy": "q"},
    ]
    result = h208.date_alias(rows)
    assert result["exact_single_regime_per_date"]
    assert result["exact_indicator_reconstruction"]
    assert result["rank_increment"] == 0


def test_crossed_date_is_not_alias() -> None:
    rows = [
        {"date": "a", "group": 1, "policy": "p"},
        {"date": "a", "group": 2, "policy": "p"},
        {"date": "b", "group": 2, "policy": "q"},
    ]
    result = h208.date_alias(rows)
    assert not result["exact_single_regime_per_date"]
    assert not result["exact_indicator_reconstruction"]
    assert result["rank_increment"] == 1


def test_known_composition_metrics() -> None:
    table = {
        "policies": ["p", "q"],
        "counts": {"p": {"1": 1, "2": 0}, "q": {"1": 0, "2": 1}},
    }
    result = h208.composition_metrics(table)
    assert math.isclose(result["policy_distribution_total_variation"], 1)
    assert math.isclose(result["cramers_v"], 1)


def test_classification_boundaries() -> None:
    alias = {
        "exact_single_regime_per_date": True,
        "exact_indicator_reconstruction": True,
    }
    table = {"all_policy_regime_cells_positive": True}
    assert (
        h208.classify(alias, table)
        == "date_aliased_with_complete_policy_regime_support"
    )
    table["all_policy_regime_cells_positive"] = False
    assert (
        h208.classify(alias, table)
        == "date_aliased_with_policy_regime_support_gap"
    )
    alias["exact_single_regime_per_date"] = False
    alias["exact_indicator_reconstruction"] = False
    assert h208.classify(alias, table) == "date_separable_at_utc_day_resolution"


def test_stage_keeps_material_metrics_closed() -> None:
    stage = h208.staged_validation(h208.load_join())
    assert stage["material_date_alias_or_composition_metric_computed"] is False
    assert stage["episode_count"] == 594


def test_canonical_validates() -> None:
    h208.validate(canonical())


@pytest.mark.parametrize(
    ("key", "message"),
    [
        ("sampling_p_value_reported", "sampling p value"),
        ("performance_or_later_state_opened", "performance scope"),
        ("clock_regime_treated_as_session_or_cause", "regime scope"),
        ("outcome_analysis_authorized", "outcome scope"),
    ],
)
def test_scope_attacks_fail(key: str, message: str) -> None:
    result = canonical()
    result[key] = True
    with pytest.raises(ValueError, match=message):
        h208.validate(result)


def test_classification_attack_fails() -> None:
    result = canonical()
    result["classification"] = "date_separable_at_utc_day_resolution"
    if h208.classify(
        result["date_alias"], result["policy_regime_support"]
    ) == result["classification"]:
        result["classification"] = "date_aliased_with_policy_regime_support_gap"
    with pytest.raises(ValueError, match="classification"):
        h208.validate(result)
