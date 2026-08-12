from __future__ import annotations

import copy
import json
import math

import pytest

import audit_h206_phail_monotonic_wall_clock_bridge as h206


def canonical() -> dict:
    return json.loads(h206.OUTPUT.read_text())


def test_synthetic_controls_pass() -> None:
    assert all(h206.synthetic_controls().values())


def test_threshold_is_strict() -> None:
    rows = [
        {"offset_ns": 0, "episode_id": "a"},
        {"offset_ns": 10, "episode_id": "b"},
        {"offset_ns": 21, "episode_id": "c"},
    ]
    assert h206.labels_for_threshold(rows, 10) == [0, 0, 1]
    assert h206.labels_for_threshold(rows, 11) == [0, 0, 0]


def test_kendall_known_answers() -> None:
    concordant = [
        {"episode_id": "a", "created_ts_ns": 1, "first_timestamp_ns": 1},
        {"episode_id": "b", "created_ts_ns": 2, "first_timestamp_ns": 2},
        {"episode_id": "c", "created_ts_ns": 3, "first_timestamp_ns": 3},
    ]
    reversed_rows = [
        {"episode_id": "a", "created_ts_ns": 1, "first_timestamp_ns": 3},
        {"episode_id": "b", "created_ts_ns": 2, "first_timestamp_ns": 2},
        {"episode_id": "c", "created_ts_ns": 3, "first_timestamp_ns": 1},
    ]
    assert h206.discordant_pairs(concordant) == (0, 1.0)
    discordant, tau = h206.discordant_pairs(reversed_rows)
    assert discordant == 3
    assert tau == -1.0


def test_contiguity_logic() -> None:
    assert h206.positions_contiguous([0, 0, 1, 1], 0)
    assert not h206.positions_contiguous([0, 1, 0], 0)


def test_classification_scale_separation() -> None:
    gaps = [100, 200_000]
    memberships = {
        threshold: [0, 0, 1]
        for threshold in (
            1_000_000_000,
            10_000_000_000,
            60_000_000_000,
            600_000_000_000,
            3_600_000_000_000,
            21_600_000_000_000,
        )
    }
    gaps = [1_000_000_000, 100_000_000_000_000]
    assert (
        h206.classify(gaps, memberships)
        == "scale_separated_clock_offset_regimes"
    )


def test_canonical_validates() -> None:
    h206.validate(canonical())


@pytest.mark.parametrize(
    "key",
    [
        "performance_or_later_state_opened",
        "host_or_session_identity_established",
        "dependence_cluster_established",
        "confirmatory_claim_authorized",
    ],
)
def test_scope_attacks_fail(key: str) -> None:
    result = canonical()
    result[key] = True
    with pytest.raises(ValueError, match=key):
        h206.validate(result)


def test_status_attack_fails() -> None:
    result = canonical()
    result["status"] = "confirmatory"
    with pytest.raises(ValueError, match="status"):
        h206.validate(result)


def test_projection_count_attack_fails() -> None:
    result = canonical()
    result["projection_rows"] -= 1
    with pytest.raises(ValueError, match="projection rows"):
        h206.validate(result)
