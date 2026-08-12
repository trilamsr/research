from __future__ import annotations

import copy
import json
import math

import pytest

import audit_h199_phail_randomized_home_target as h199


def canonical_result():
    return json.loads(h199.OUTPUT.read_text())


def test_expected_classification() -> None:
    result = canonical_result()
    assert (
        result["classification"]
        == "historical_and_current_unrecorded_randomized_home"
    )


def test_zero_vector_removes_randomized_home() -> None:
    result = canonical_result()
    endpoints = copy.deepcopy(result["endpoints"])
    for row in endpoints:
        row["effective_home_joints_variation_rad"] = [0.0] * 7
    assert h199.classify(endpoints) == "no_randomized_home_bound"


def test_current_only_classification() -> None:
    result = canonical_result()
    endpoints = copy.deepcopy(result["endpoints"])
    endpoints[0]["random_draw_bound"] = False
    assert h199.classify(endpoints) == "current_only_unrecorded_randomized_home"


def test_recorded_draw_classification() -> None:
    result = canonical_result()
    endpoints = copy.deepcopy(result["endpoints"])
    endpoints[1]["realized_target_serialized"] = True
    assert h199.classify(endpoints) == "randomized_home_draw_recorded"


def test_maximum_and_rms_are_distinct() -> None:
    vector = [0.03, 0.05, 0.08, 0.08, 0.10, 0.10, 0.10]
    q = h199.quantitative_summary(vector)
    assert q["maximum_euclidean_joint_perturbation_rad"] > q[
        "rms_euclidean_joint_perturbation_rad"
    ]
    assert math.isclose(
        q["maximum_euclidean_joint_perturbation_rad"],
        q["rms_euclidean_joint_perturbation_rad"] * math.sqrt(3),
    )


def test_degrees_conversion() -> None:
    q = h199.quantitative_summary([0.10] * 7)
    assert math.isclose(q["half_widths_deg"][0], 5.729577951308233)


def test_wrong_blob_fails() -> None:
    result = canonical_result()
    result["source_files"][h199.BASE][0]["git_blob"] = "0" * 40
    with pytest.raises(ValueError, match="source blobs"):
        h199.validate(result)


def test_maximum_corruption_fails() -> None:
    result = canonical_result()
    result["quantitative_summary"]["maximum_euclidean_joint_perturbation_rad"] = 0.0
    with pytest.raises(ValueError, match="maximum"):
        h199.validate(result)


def test_physical_adequacy_claim_fails() -> None:
    result = canonical_result()
    result["physical_reset_adequacy_established"] = True
    with pytest.raises(ValueError, match="physical_reset_adequacy_established"):
        h199.validate(result)


def test_historical_execution_claim_fails() -> None:
    result = canonical_result()
    result["historical_execution_fidelity_established"] = True
    with pytest.raises(ValueError, match="historical_execution_fidelity_established"):
        h199.validate(result)

