import hashlib
import json

import audit_h193_phail_lifecycle_keys as module


def test_projection_is_key_only_and_excludes_prohibited_paths():
    forbidden = "NEVER_EMIT_THIS_VALUE"
    raw = json.dumps(
        {
            "run_id": forbidden,
            "robot": {"host-name": forbidden},
            "created_ts_ns": 123,
            "operator_success": forbidden,
            "eval.successful_items": 999,
            "nested": [{"batch-seq": 7, "video": forbidden}],
        }
    ).encode()
    rows = module.project_schema(raw, "static")
    encoded = json.dumps(rows, sort_keys=True)
    assert forbidden not in encoded
    assert "successful" not in encoded
    assert "video" not in encoded
    assert {row["key_path"] for row in rows} == {
        "static.created_ts_ns",
        "static.nested.[].batch-seq",
        "static.robot",
        "static.robot.host-name",
        "static.run_id",
    }
    assert all(set(row) == {"key_path", "category", "node_type"} for row in rows)


def test_punctuation_aware_matching_does_not_match_substrings():
    raw = json.dumps(
        {
            "runtime": "not the fixed run component",
            "runner": "not the fixed run component",
            "run-id": "match",
            "cluster_id": "match",
        }
    ).encode()
    rows = module.project_schema(raw, "meta")
    assert {row["key_path"] for row in rows} == {
        "meta.cluster_id",
        "meta.run-id",
    }


def test_inspect_one_fails_closed_on_hash_mismatch():
    payload = b'{"run_id":"opaque"}'
    row = {
        "episode_id": "episode",
        "meta_source_path": "meta.json",
        "meta_sha256": hashlib.sha256(payload).hexdigest(),
        "static_source_path": "static.json",
        "static_sha256": "0" * 64,
    }

    def fetch(url):
        return payload

    try:
        module.inspect_one(row, fetch=fetch, cache_dir=None)
    except ValueError as error:
        assert "source hash mismatch" in str(error)
    else:
        raise AssertionError("hash mismatch accepted")


def test_cohort_validation_rejects_duplicate_episode():
    base = {
        "episode_id": "same",
        "meta_source_path": "x/meta.json",
        "meta_sha256": "1" * 64,
        "static_source_path": "x/static.json",
        "static_sha256": "2" * 64,
    }
    rows = [dict(base) for _ in range(module.EXPECTED_EPISODES)]
    try:
        module.validate_cohort_rows(rows)
    except ValueError as error:
        assert "duplicate episode" in str(error)
    else:
        raise AssertionError("duplicate cohort accepted")


def test_validator_rejects_duplicate_projected_rows():
    result = {
        "schema": "h193-phail-lifecycle-key-inventory-v1",
        "protocol_sha256": module.sha256(module.PROTOCOL),
        "input_sha256": module.INPUT_SHA256,
        "episode_count": module.EXPECTED_EPISODES,
        "sidecar_object_count": 1188,
        "fixed_lifecycle_tokens": list(module.LIFECYCLE_TOKENS),
        "primitive_values_retained": False,
        "source_content_emitted": False,
        "performance_field_values_opened": False,
        "key_rows": [
            {
                "key_path": "meta.run_id",
                "category": "lifecycle_candidate",
                "episode_count": 1,
                "episode_set_sha256": "a" * 64,
                "node_type_counts": {"string": 1},
            }
        ]
        * 2,
        "lifecycle_candidate_count": 2,
        "disposition": "candidate_lifecycle_key_found",
    }
    try:
        module.validate(result)
    except ValueError as error:
        assert "duplicate key row" in str(error)
    else:
        raise AssertionError("duplicate rows accepted")
