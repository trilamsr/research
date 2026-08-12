from __future__ import annotations

import copy
import json

import pytest

import audit_h198_current_phail_lifecycle_binding as h198


def canonical_units():
    return h198.units()


def canonical_result():
    return json.loads(h198.OUTPUT.read_text())


def test_expected_classification() -> None:
    assert h198.classify(canonical_units()) == "mechanics_bound_evidence_incomplete"


def test_full_support_classifies_bound() -> None:
    rows = copy.deepcopy(canonical_units())
    for row in rows:
        row["status"] = "supported"
    assert h198.classify(rows) == "lifecycle_evidence_bound"


def test_no_bound_mechanics_classifies_generic_only() -> None:
    rows = copy.deepcopy(canonical_units())
    for row in rows:
        if row["unit"] in {
            "pre_session_scene_reset_call",
            "inter_episode_home_command",
            "post_reset_recording_boundary",
        }:
            row["status"] = "not_supported"
    assert h198.classify(rows) == "generic_capability_not_bound_to_phail"


def test_home_command_does_not_promote_completion_gate() -> None:
    rows = {row["unit"]: row for row in canonical_units()}
    assert rows["inter_episode_home_command"]["status"] == "supported"
    assert rows["home_completion_gate"]["status"] == "not_supported"


def test_arbitrary_context_does_not_promote_operator_identity() -> None:
    rows = {row["unit"]: row for row in canonical_units()}
    assert rows["persistent_directive_context"]["status"] == "supported"
    assert rows["persistent_operator_session_identity"]["status"] == "not_supported"


def test_episode_uuid_does_not_promote_operator_identity() -> None:
    rows = {row["unit"]: row for row in canonical_units()}
    assert rows["persistent_episode_identity"]["status"] == "supported"
    assert rows["persistent_operator_session_identity"]["status"] == "not_supported"


def test_abort_does_not_count_as_persistent_reset_evidence() -> None:
    rows = {row["unit"]: row for row in canonical_units()}
    assert rows["persistent_reset_carryover_evidence"]["status"] == "not_supported"


def test_missing_unit_fails_validator() -> None:
    result = canonical_result()
    result["units"].pop()
    with pytest.raises(ValueError, match="unit roster"):
        h198.validate(result)


def test_wrong_blob_fails_validator() -> None:
    result = canonical_result()
    result["source_files"][0]["git_blob"] = "0" * 40
    with pytest.raises(ValueError, match="blob roster"):
        h198.validate(result)


def test_excerpt_corruption_fails_validator() -> None:
    result = canonical_result()
    result["facts"][0]["excerpt"] += "\ncorrupt"
    with pytest.raises(ValueError, match="fact hash"):
        h198.validate(result)


def test_scope_flags_are_fail_closed() -> None:
    result = canonical_result()
    result["physical_success_established"] = True
    with pytest.raises(ValueError, match="physical_success_established"):
        h198.validate(result)
