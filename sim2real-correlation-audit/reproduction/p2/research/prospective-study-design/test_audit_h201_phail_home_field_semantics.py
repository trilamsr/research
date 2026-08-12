from __future__ import annotations

import copy
import json

import pytest

import audit_h201_phail_home_field_semantics as h201


def canonical() -> dict:
    return json.loads(h201.OUTPUT.read_text())


def test_expected_classification() -> None:
    assert canonical()["classification"] == "generic_signal_schema_not_home_draw"


def test_realized_target_changes_classification() -> None:
    result = canonical()
    candidates = copy.deepcopy(result["candidates"])
    candidates[0]["realized_home_target_present"] = True
    assert (
        h201.classify(candidates, result["controls"])
        == "realized_home_or_rng_evidence_source_defined"
    )


def test_missing_control_is_incomplete() -> None:
    result = canonical()
    controls = copy.deepcopy(result["controls"])
    controls["static_json_sink"] = False
    assert h201.classify(result["candidates"], controls) == "source_trace_incomplete"


def test_ambiguous_semantics_are_not_null() -> None:
    result = canonical()
    candidates = copy.deepcopy(result["candidates"])
    candidates[1]["semantic_class"] = "ambiguous"
    assert (
        h201.classify(candidates, result["controls"])
        == "mixed_or_ambiguous_candidate_semantics"
    )


def test_candidate_roster_corruption_fails() -> None:
    result = canonical()
    result["candidates"][0]["key"] = "home_target"
    with pytest.raises(ValueError, match="candidates"):
        h201.validate(result)


def test_blob_corruption_fails() -> None:
    result = canonical()
    first = next(iter(result["source_blobs"]))
    result["source_blobs"][first] = "0" * 40
    with pytest.raises(ValueError, match="blobs"):
        h201.validate(result)


def test_scope_overclaims_fail() -> None:
    for key in (
        "sidecar_values_opened",
        "trajectory_or_performance_content_opened",
        "historical_execution_fidelity_established",
    ):
        result = canonical()
        result[key] = True
        with pytest.raises(ValueError, match=key):
            h201.validate(result)

