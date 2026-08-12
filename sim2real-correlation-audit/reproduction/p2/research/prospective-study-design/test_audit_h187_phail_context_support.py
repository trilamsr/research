import json

import audit_h187_phail_context_support as module


def test_sanitizer_emits_exact_whitelist_and_no_outcomes():
    meta = {"created_ts_ns": 1_700_000_000_000_000_000, "duration_ns": 99}
    static = {
        "model": "act",
        "variant": "checkpoint",
        "task": "task",
        "eval.object": "bottle",
        "eval.tote_placement": "left",
        "eval.external_camera": "right",
        "eval.successful_items": 999,
        "eval.outcome": "forbidden",
        "eval.duration": 999,
        "eval": {
            "successful_items": 999,
            "outcome": "forbidden",
            "duration": 999,
        },
    }
    payloads = {
        f"{module.ENDPOINT}/meta": json.dumps(meta).encode(),
        f"{module.ENDPOINT}/static": json.dumps(static).encode(),
    }
    row = module.sanitize_episode(
        "episode", "session", "meta", "static", fetch=payloads.__getitem__
    )
    assert tuple(row) == module.ALLOWED_FIELDS
    assert not {"outcome", "successful_items", "duration"} & set(row)
    assert row["policy_model"] == "act"
    assert row["object"] == "bottle"
    assert row["session_id"] is None


def test_episode_pairs_requires_complete_exact_cohort():
    inventory = []
    for value in range(module.EXPECTED_EPISODES):
        episode = f"{value:012d}"
        stem = f"{module.ROLLOUT_PREFIX}000000000000/{episode}/"
        inventory.extend(({"key": stem + "meta.json"}, {"key": stem + "static.json"}))
    pairs = module.episode_pairs(inventory)
    assert len(pairs) == module.EXPECTED_EPISODES
    assert pairs[0][0] == "000000000000"
    assert pairs[-1][0] == "000000000593"


def test_missing_context_is_adverse_not_common_support():
    rows = []
    for index, policy in enumerate(module.POLICIES):
        rows.append(
            {
                "episode_id": str(index),
                "policy_model": policy,
                "checkpoint_variant": "v",
                "task": "task",
                "object": None,
                "tote_placement": None,
                "external_camera": None,
                "created_ts_ns": 1_700_000_000_000_000_000 + index,
                "utc_date": "2023-11-14",
                "session_id": "session",
                "meta_source_path": "meta",
                "meta_sha256": "m",
                "static_source_path": "static",
                "static_sha256": "s",
            }
        )
    result = module.summarize(rows)
    assert result["complete_context_cell_count"] == 0
    assert result["metadata_gate_pass"] is False
    assert result["full_release_metadata_gate_pass"] is False
    assert result["disposition"] == "adverse_no_common_support_target"
    assert "missing_declared_context_metadata" in result["adverse_reasons"]


def test_complete_balanced_cell_passes():
    rows = []
    for index, policy in enumerate(module.POLICIES):
        rows.append(
            {
                "episode_id": str(index),
                "policy_model": policy,
                "checkpoint_variant": "v",
                "task": "task",
                "object": "bottle",
                "tote_placement": "left",
                "external_camera": "right",
                "created_ts_ns": 1_700_000_000_000_000_000 + index,
                "utc_date": "2023-11-14",
                "session_id": "session",
                "meta_source_path": "meta",
                "meta_sha256": "m",
                "static_source_path": "static",
                "static_sha256": "s",
            }
        )
    result = module.summarize(rows)
    assert result["metadata_gate_pass"] is False
    assert result["full_release_metadata_gate_pass"] is True
    assert result["context_cells"][0]["minimum_policy_count"] == 1
    assert result["narrow_target"]["retained_cell_count"] == 1
    assert result["narrow_target"]["identified"] is True
    assert result["conditional_outcome_phase_authorized"] is False
