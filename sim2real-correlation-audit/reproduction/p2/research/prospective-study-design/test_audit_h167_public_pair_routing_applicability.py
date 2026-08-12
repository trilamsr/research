from audit_h167_public_pair_routing_applicability import (
    REQUIRED_UNIT_IDS,
    build,
)


def units_by_id():
    return {row["unit_id"]: row for row in build()["units"]}


def test_all_fixed_units_emitted_in_order():
    result = build()
    assert result["unit_count"] == 15
    assert [row["unit_id"] for row in result["units"]] == list(range(1, 16))


def test_public_action_is_ranking_not_pair_routing():
    units = units_by_id()
    assert units[1]["status"] == "absent"
    assert units[2]["status"] == "available"
    assert units[3]["status"] == "absent"
    assert build()["public_action_mismatch"] is True


def test_paper_description_does_not_promote_deployed_assignment():
    units = units_by_id()
    assert units[4]["status"] == "paper_described_only"
    assert units[5]["status"] == "absent"
    assert units[6]["status"] == "absent"
    assert units[8]["status"] == "absent"


def test_cumulative_support_does_not_promote_newest_increment():
    units = units_by_id()
    assert units[12]["status"] == "available"
    assert units[13]["status"] == "partial"
    assert units[14]["status"] == "contradicted_by_public_record"
    assert build()["cumulative_support_does_not_establish_current_applicability"]


def test_every_required_gate_currently_fails():
    result = build()
    assert result["required_unit_ids"] == list(REQUIRED_UNIT_IDS)
    assert result["failed_required_unit_count"] == len(REQUIRED_UNIT_IDS)
    assert {row["unit_id"] for row in result["failed_required_units"]} == set(
        REQUIRED_UNIT_IDS
    )


def test_negative_decision_does_not_preclude_prospective_adoption():
    result = build()
    assert result["decision"] == "not_qualified_for_public_pair_routing_application"
    assert result["prospective_adoption_possible"] is True
    assert result["field_collection_authorized"] is False


def test_no_outcomes_entered_applicability_audit():
    assert build()["outcome_fields_accessed_or_used"] is False
