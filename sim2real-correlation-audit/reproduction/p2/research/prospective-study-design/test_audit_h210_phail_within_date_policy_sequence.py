from __future__ import annotations

import copy
import json

import pytest

import audit_h210_phail_within_date_policy_sequence as h210


def canonical() -> dict:
    return json.loads(h210.OUTPUT.read_text())


def test_synthetic_controls_pass() -> None:
    assert all(h210.synthetic_controls().values())


def test_production_pair_accounting() -> None:
    rows = h210.load_join()
    groups, regimes = h210.date_groups(rows)
    assert sum(len(indices) - 1 for indices in groups.values()) == 581
    assert sum(len(groups[d]) - 1 for d in groups if regimes[d] == 1) == 243
    assert sum(len(groups[d]) - 1 for d in groups if regimes[d] == 2) == 338


def test_classification_boundaries() -> None:
    base = {"observed_minus_permutation_median": 0.0, "two_sided_p": 0.5}
    analyses = {key: copy.deepcopy(base) for key in h210.KEYS}
    assert h210.classify(analyses) == "no_detectable_within_date_policy_sequence_structure_at_fixed_resolution"
    analyses["pooled_within_date"]["two_sided_p"] = 0.01
    analyses["pooled_within_date"]["observed_minus_permutation_median"] = 0.10
    assert h210.classify(analyses) == "material_pooled_within_date_policy_sequence_structure"
    analyses["pooled_within_date"]["observed_minus_permutation_median"] = 0.05
    assert h210.classify(analyses) == "regime_specific_or_small_within_date_policy_sequence_structure"


def test_stage_keeps_material_statistic_closed() -> None:
    stage = h210.staged_validation(h210.load_join())
    assert stage["material_within_date_adjacency_computed"] is False
    assert stage["pair_counts"] == h210.EXPECTED_PAIR_COUNTS


def test_canonical_validates() -> None:
    h210.validate(canonical())


@pytest.mark.parametrize(
    ("key", "message"),
    [
        ("permutation_reference_treated_as_assignment_law", "assignment scope"),
        ("date_treated_as_physical_session_or_cause", "date scope"),
        ("state_or_performance_opened", "data scope"),
        ("outcome_analysis_authorized", "outcome scope"),
    ],
)
def test_scope_attacks_fail(key: str, message: str) -> None:
    result = canonical()
    result[key] = True
    with pytest.raises(ValueError, match=message):
        h210.validate(result)


def test_classification_attack_fails() -> None:
    result = canonical()
    result["classification"] = "material_pooled_within_date_policy_sequence_structure"
    if h210.classify(result["analyses"]) == result["classification"]:
        result["classification"] = "no_detectable_within_date_policy_sequence_structure_at_fixed_resolution"
    with pytest.raises(ValueError, match="classification"):
        h210.validate(result)
