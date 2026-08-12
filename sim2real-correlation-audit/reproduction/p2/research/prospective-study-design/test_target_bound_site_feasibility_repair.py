import copy

import pytest

import target_bound_site_feasibility_repair as h170


def test_known_answers_and_counts_are_preserved():
    result = h170.build_result()
    observed = {
        row["dossier"]["dossier_name"]: row["classification"]["decision"]
        for row in result["dossiers"]
    }
    assert observed == h170.H164.EXPECTED_DECISIONS
    assert result["dossier_unit_row_count"] == 64
    assert result["artifact_count"] == 64


def test_canonical_target_binds_every_required_unit():
    assert h170.TARGET_SPEC["required_units"] == h170.H164.UNIT_ORDER
    assert h170.TARGET_SPEC["not_applicable_authorizations"] == []
    result = h170.build_result()
    assert result["canonical_target_spec_hash"] == h170.TARGET_HASH


@pytest.mark.parametrize(
    "unit_name",
    [
        "policy_observation_interface",
        "context_generation_and_assignment_order",
        "reset_washout_and_carryover_control",
    ],
)
def test_h169_not_applicable_bypasses_fail_closed(unit_name):
    dossier = h170.upgrade_dossier(h170.H164.build_known_answer_dossiers()[0])
    row = next(item for item in dossier["units"] if item["unit"] == unit_name)
    row["status"] = "not_applicable"
    row["missing_or_changed"] = "arbitrary reason"
    with pytest.raises(ValueError, match="lacks exact target authorization"):
        h170.classify_dossier(dossier)


def test_rehashed_altered_target_still_fails_exact_identity():
    dossier = h170.upgrade_dossier(h170.H164.build_known_answer_dossiers()[0])
    dossier["target_spec"]["max_allowed_start_delay_ns"] += 1
    dossier["study_spec_hash"] = h170.canonical_hash(dossier["target_spec"])
    with pytest.raises(ValueError, match="differs from canonical"):
        h170.classify_dossier(dossier)


def test_forged_authorization_fails():
    dossier = h170.upgrade_dossier(h170.H164.build_known_answer_dossiers()[0])
    row = next(
        item
        for item in dossier["units"]
        if item["unit"] == "policy_observation_interface"
    )
    row["status"] = "not_applicable"
    row["missing_or_changed"] = "forged reason"
    dossier["not_applicable_authorizations"].append(
        {
            "unit": row["unit"],
            "rationale": "forged",
            "target_spec_sha256": dossier["study_spec_hash"],
        }
    )
    with pytest.raises(ValueError, match="authorization roster differs"):
        h170.classify_dossier(dossier)


def test_all_legacy_and_authorization_attacks_fail_closed():
    result = h170.build_result()
    assert result["legacy_hostile_control_count"] == 14
    assert result["legacy_hostile_controls_rejected"] == 14
    assert result["authorization_control_count"] == 9
    assert result["authorization_controls_rejected"] == 9


def test_target_altering_decision_is_preserved():
    dossier = h170.upgrade_dossier(h170.H164.build_known_answer_dossiers()[0])
    dossier["policy_visible_instrumentation"] = True
    decision = h170.classify_dossier(dossier)
    assert decision["decision"] == "target_altering_only"


def test_repair_does_not_qualify_site_or_field_collection():
    result = h170.build_result()
    assert result["interface_decision"] == "synthetic_gate_logic_repaired_pass"
    assert result["independent_challenge_required"] is True
    assert result["real_site_qualified"] is False
    assert result["field_collection_authorized"] is False


def test_changed_artifact_bytes_remain_rejected():
    dossier = h170.upgrade_dossier(h170.H164.build_known_answer_dossiers()[0])
    dossier = copy.deepcopy(dossier)
    dossier["artifacts"][0]["content_b64"] = "Y2hhbmdlZA=="
    with pytest.raises(ValueError, match="artifact size mismatch|artifact hash mismatch"):
        h170.classify_dossier(dossier)
