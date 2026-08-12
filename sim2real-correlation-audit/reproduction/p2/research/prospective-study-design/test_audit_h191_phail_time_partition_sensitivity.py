import copy

import pytest

import audit_h191_phail_time_partition_sensitivity as h191


def test_input_is_exact_and_outcome_free() -> None:
    rows = h191.load_rows()
    assert len(rows) == 594
    assert tuple(rows[0]) == h191.ALLOWED_INPUT_FIELDS
    assert all("success" not in field.lower() for field in rows[0])
    assert all("outcome" not in field.lower() for field in rows[0])


def test_full_window_reproduces_h187_support() -> None:
    result = h191.summarize(h191.load_rows(), None)
    assert result["cell_count"] == 19
    assert result["supported_cell_count"] == 17


def test_utc_partition_reproduces_h187_and_thin_minima() -> None:
    result = h191.summarize(h191.load_rows(), 24, 0)
    assert result["cell_count"] == 126
    assert result["supported_cell_count"] == 18
    assert result["retained_episode_count"] == 194
    assert result["policy_counts"] == {
        "act": 45,
        "groot": 62,
        "openpi": 39,
        "smolvla": 48,
    }
    assert result["minimum_policy_count_distribution"] == {"1": 11, "2": 7}


def test_complete_phase_grid_and_conservation() -> None:
    result = h191.build()
    assert len(result["grid"]) == sum(h191.WIDTHS_HOURS)
    assert next(
        row for row in result["width_ranges"] if row["width_hours"] == 24
    )["phase_zero_retained_episode_count"] == 194
    assert all(
        row["retained_episode_count"] + row["excluded_episode_count"] == 594
        for row in result["grid"]
    )
    assert all(row["supported_cell_count"] <= row["cell_count"] for row in result["grid"])


def test_validate_known_result() -> None:
    h191.validate(h191.build())


def test_validate_rejects_duplicate_grid_and_missing_ranges() -> None:
    result = h191.build()
    corrupted = copy.deepcopy(result)
    corrupted["grid"] = [corrupted["grid"][0]] * len(corrupted["grid"])
    corrupted["width_ranges"] = []
    with pytest.raises(ValueError, match="exactly recompute"):
        h191.validate(corrupted)


def test_validate_rejects_one_cell_mutation() -> None:
    corrupted = copy.deepcopy(h191.build())
    corrupted["grid"][317]["retained_episode_count"] += 1
    with pytest.raises(ValueError, match="exactly recompute"):
        h191.validate(corrupted)
