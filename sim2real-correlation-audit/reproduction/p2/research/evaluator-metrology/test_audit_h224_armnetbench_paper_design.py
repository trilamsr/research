from __future__ import annotations

import copy

import pytest

import audit_h224_armnetbench_paper_design as h224


def synthetic_source() -> str:
    lines = ["unused"] * 590
    for unit in h224.EVIDENCE_UNITS:
        for anchor in unit["anchors"]:
            lines[anchor["line"] - 1] += " " + anchor["contains"]
    return "\n".join(lines) + "\n"


def test_all_fixed_units_are_unique_and_coded() -> None:
    assert [row["unit_id"] for row in h224.EVIDENCE_UNITS] == list(range(1, 13))
    assert len({row["name"] for row in h224.EVIDENCE_UNITS}) == 12
    assert {row["status"] for row in h224.EVIDENCE_UNITS} <= h224.ALLOWED_STATUSES
    assert all(row["anchors"] for row in h224.EVIDENCE_UNITS)


def test_anchor_validation_accepts_exact_synthetic_lines() -> None:
    h224.validate_source_anchors(synthetic_source())


def test_anchor_validation_rejects_changed_evidence() -> None:
    altered = synthetic_source().replace(
        h224.EVIDENCE_UNITS[4]["anchors"][0]["contains"],
        "materially changed source",
        1,
    )
    with pytest.raises(ValueError, match="anchor mismatch"):
        h224.validate_source_anchors(altered)


def test_saved_result_requires_least_permissive_decisions() -> None:
    result = h224.expected_result_record()
    h224.validate_result_record(result)

    altered = copy.deepcopy(result)
    altered["decisions"]["p2_classification"] = "positive_design_contrast"
    with pytest.raises(ValueError, match="decision mismatch"):
        h224.validate_result_record(altered)


def test_exposure_boundary_is_explicit_and_nonreliant() -> None:
    result = h224.expected_result_record()
    assert result["outcome_exposure"]["performance_values_incidentally_visible"]
    assert not result["outcome_exposure"]["performance_values_extracted_or_used"]
    assert result["decisions"]["h022_status"] == "refused_unchanged"
    assert result["decisions"]["p2_classification"] == "adverse_mismatch_contrast"
