from __future__ import annotations

import copy
import json
import math

import pytest

import audit_h202_phail_initial_joint_state as h202


def canonical() -> dict:
    return json.loads(h202.OUTPUT.read_text())


def test_linear_quantile_known_answers() -> None:
    values = [0.0, 10.0, 20.0, 30.0]
    assert h202.quantile_linear(values, 0.0) == 0.0
    assert h202.quantile_linear(values, 0.5) == 15.0
    assert math.isclose(h202.quantile_linear(values, 0.95), 28.5)
    assert h202.quantile_linear(values, 1.0) == 30.0


def test_population_std_known_answer() -> None:
    assert math.isclose(h202.population_std([0.0, 2.0]), 1.0)


def test_summary_known_answer_and_error_exclusion() -> None:
    base = h202.BASE
    rows = [
        {"error": 0, "q": [base[i] + 0.01 for i in range(7)]},
        {"error": 0, "q": [base[i] - 0.01 for i in range(7)]},
        {"error": 1, "q": [999.0] * 7},
    ]
    result = h202.summarize(rows)
    assert result["valid_achieved_state_count"] == 2
    assert result["first_error_count"] == 1
    assert all(
        math.isclose(row["mean_rad"], 0.0, abs_tol=1e-15)
        for row in result["joint_deviation_summary"]
    )
    assert math.isclose(
        result["euclidean_joint_deviation_summary"]["rms_rad"],
        math.sqrt(7) * 0.01,
    )


def test_classification_boundaries() -> None:
    summary = {"valid_achieved_state_count": 594}
    assert (
        h202.classify(summary, True)
        == "complete_initial_joint_state_reconstruction"
    )
    summary["valid_achieved_state_count"] = 535
    assert (
        h202.classify(summary, True)
        == "partial_initial_joint_state_reconstruction"
    )
    summary["valid_achieved_state_count"] = 534
    assert (
        h202.classify(summary, True)
        == "insufficient_initial_joint_state_coverage"
    )
    assert h202.classify(summary, False) == "semantic_trace_incomplete"


def test_canonical_scope_and_classification() -> None:
    result = canonical()
    h202.validate(result)
    assert result["classification"] in h202.CLASSIFICATIONS


def test_scope_attacks_fail() -> None:
    for key in (
        "later_joint_values_retained_or_summarized",
        "action_command_camera_media_or_performance_opened",
        "target_draw_recovered",
        "reset_acceptance_established",
        "historical_execution_fidelity_established",
    ):
        result = canonical()
        result[key] = True
        with pytest.raises(ValueError, match=key):
            h202.validate(result)


def test_source_blob_attack_fails() -> None:
    result = canonical()
    first = next(iter(result["source_trace"]["source_blobs"]))
    result["source_trace"]["source_blobs"][first] = "0" * 40
    with pytest.raises(ValueError, match="source blobs"):
        h202.validate(result)


def test_coverage_partition_attack_fails() -> None:
    result = canonical()
    attacked = copy.deepcopy(result)
    attacked["summary"]["first_error_count"] += 1
    with pytest.raises(ValueError, match="coverage partition"):
        h202.validate(attacked)
