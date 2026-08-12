from __future__ import annotations

import copy
import hashlib
import json

import pytest

import audit_h200_phail_home_field_keys as h200


def test_fixed_matching_is_punctuation_aware_and_nested() -> None:
    raw = json.dumps(
        {
            "home-target": "DO_NOT_RETAIN_A",
            "nested": {"rng_state": "DO_NOT_RETAIN_B"},
            "unrelated": "DO_NOT_RETAIN_C",
        }
    ).encode()
    rows = h200.project_schema(raw, "static")
    assert rows == [
        {
            "key_path": "static.home-target",
            "category": "home_field_candidate",
            "node_type": "string",
        },
        {
            "key_path": "static.nested.rng_state",
            "category": "home_field_candidate",
            "node_type": "string",
        },
    ]
    assert "DO_NOT_RETAIN" not in json.dumps(rows)


def test_prohibited_action_observation_and_outcome_paths_are_excluded() -> None:
    raw = json.dumps(
        {
            "action": {"target_pose": [1, 2, 3]},
            "observation.initial_pose": [4, 5],
            "success.home": "DO_NOT_RETAIN",
            "home_joints": [0] * 7,
        }
    ).encode()
    rows = h200.project_schema(raw, "meta")
    assert rows == [
        {
            "key_path": "meta.home_joints",
            "category": "home_field_candidate",
            "node_type": "array",
        }
    ]


def test_malformed_root_fails() -> None:
    with pytest.raises(ValueError, match="root"):
        h200.project_schema(b"[]", "meta")


def test_hash_mismatch_fails(tmp_path) -> None:
    expected = hashlib.sha256(b"expected").hexdigest()
    with pytest.raises(ValueError, match="hash"):
        h200.h193.fetch_verified(
            "https://invalid.example/object",
            expected,
            lambda _url: b"wrong",
            tmp_path / "object.json",
            attempts=1,
        )


def test_duplicate_and_missing_cohort_rows_fail() -> None:
    rows = h200.h193.load_cohort()
    with pytest.raises(ValueError, match="episode count"):
        h200.h193.validate_cohort_rows(rows[:-1])
    duplicated = copy.deepcopy(rows)
    duplicated[-1] = copy.deepcopy(duplicated[0])
    with pytest.raises(ValueError, match="duplicate"):
        h200.h193.validate_cohort_rows(duplicated)


def test_aggregate_is_order_invariant_and_deduplicates() -> None:
    row_a = {
        "episode_id": "a",
        "key_path": "static.home_joints",
        "category": "home_field_candidate",
        "node_type": "array",
    }
    row_b = {**row_a, "episode_id": "b"}
    assert h200.aggregate([row_b, row_a, row_a]) == h200.aggregate([row_a, row_b])


def test_aggregate_rejects_schema_and_category_changes() -> None:
    row = {
        "episode_id": "a",
        "key_path": "static.home",
        "category": "wrong",
        "node_type": "number",
    }
    with pytest.raises(ValueError, match="category"):
        h200.aggregate([row])
    with pytest.raises(ValueError, match="schema"):
        h200.aggregate([{**row, "extra": "x"}])


def test_validate_rejects_value_and_scope_flags() -> None:
    if not h200.OUTPUT.exists():
        pytest.skip("material result not generated yet")
    result = json.loads(h200.OUTPUT.read_text())
    for key in (
        "primitive_values_retained",
        "source_content_emitted",
        "performance_or_trajectory_values_opened",
    ):
        attacked = copy.deepcopy(result)
        attacked[key] = True
        with pytest.raises(ValueError, match=key):
            h200.validate(attacked)


def test_validate_rejects_prohibited_projected_path() -> None:
    if not h200.OUTPUT.exists():
        pytest.skip("material result not generated yet")
    result = json.loads(h200.OUTPUT.read_text())
    attacked = copy.deepcopy(result)
    attacked["key_rows"] = [
        {
            "key_path": "static.action.target",
            "category": "home_field_candidate",
            "episode_count": 1,
            "episode_set_sha256": "0" * 64,
            "node_type_counts": {"number": 1},
        }
    ]
    attacked["candidate_count"] = 1
    attacked["disposition"] = "candidate_home_field_key_found"
    with pytest.raises(ValueError, match="prohibited"):
        h200.validate(attacked)
