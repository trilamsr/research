import copy

import pytest

import audit_h178_cross_system_action_order as h178


def system(name):
    coding = h178.load(h178.CODING)
    return next(row for row in coding["systems"] if row["system"] == name)


def unit(system_row, name):
    return next(row for row in system_row["units"] if row["unit"] == name)


def test_fixed_inputs_are_complete_and_hash_bound():
    systems = h178.validate_inputs(h178.load(h178.ROSTER), h178.load(h178.CODING))
    assert len(systems) == 7
    assert sum(len(row["units"]) for row in systems) == 70


def test_positive_contrasts_and_no_second_mismatch():
    result = h178.build_result()
    assert result["positive_contrast_systems"] == ["umi_bench", "robodojo"]
    assert result["second_mismatch_systems"] == []
    assert result["decision"] == "positive_contrast_found"
    assert result["positive_contrast_strength"] == "source_described"


@pytest.mark.parametrize("name", ["umi_bench", "robodojo"])
def test_each_positive_contrast_requires_every_conjunction_unit(name):
    original = system(name)
    assert h178.positive_contrast(original)
    for required in h178.POSITIVE_UNITS:
        attacked = copy.deepcopy(original)
        row = unit(attacked, required)
        row["status"] = "partial"
        row["value"] = "unresolved"
        assert not h178.positive_contrast(attacked), required


@pytest.mark.parametrize(
    "name,unit_name",
    [
        ("autoeval", "stable_context_law_public"),
        ("autoeval", "declared_target_support_complete_or_bounded"),
        ("autoeval", "reset_carryover_rule_public"),
        ("practical_recipe", "context_fixed_before_candidate_assignment"),
        ("practical_recipe", "stable_assignment_law_public"),
        ("gesim_2", "cluster_or_session_identity_public"),
    ],
)
def test_single_favorable_fact_cannot_promote(name, unit_name):
    row = system(name)
    assert unit(row, unit_name)["value"] == "satisfied"
    assert not h178.positive_contrast(row)


def test_roboarena_positive_control_is_not_a_discovered_second_case():
    row = system("roboarena")
    assert not h178.second_mismatch(row)
    attacked = copy.deepcopy(row)
    attacked["system"] = "other"
    # Missing stable-context evidence cannot be converted into affirmative
    # evidence that a common-context bridge is absent.
    assert not h178.second_mismatch(attacked)


def test_outcome_fields_are_not_retained():
    result = h178.build_result()
    assert result["outcome_fields_retained"] == []
    assert result["paper_status_change_authorized_before_independent_challenge"] is False
    assert result["roster_expansion_authorized"] is False
