#!/usr/bin/env python3
"""Validate independent H201 source-semantics challenge."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


FAMILY = Path(__file__).resolve().parent
PRODUCER = FAMILY / "result-h201-phail-home-field-semantics.json"
CHALLENGE = (
    FAMILY / "result-h201-phail-home-field-semantics-independent-challenge.json"
)
ATTACKS = {
    "joint_names_are_joint_positions",
    "joint_signal_name_is_signal_samples",
    "pose_signal_names_are_pose_samples",
    "all_episode_presence_is_per_reset_variation",
    "random_target_in_same_driver_is_serialized_metadata",
    "static_item_is_necessarily_realized_value",
    "visualization_role_is_reset_evidence",
    "tagged_source_proves_historical_execution",
    "candidate_keys_require_value_opening_after_source_null",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate() -> None:
    producer = json.loads(PRODUCER.read_text())
    challenge = json.loads(CHALLENGE.read_text())
    require(
        challenge.get("schema")
        == "h201-phail-home-field-semantics-independent-challenge-v1",
        "schema",
    )
    method = challenge.get("method", "")
    require("Independent Node" in method, "method")
    require("imports no producer module" in method, "independence")
    require(challenge.get("revision") == producer.get("revision"), "revision")
    require(
        challenge.get("classification") == producer.get("classification"),
        "classification",
    )
    inventory = challenge.get("inventory", {})
    require(
        inventory.get("hit_counts")
        == {"joint_names": 40, "joint_signal": 14, "pose_signals": 8},
        "hit counts",
    )
    require(
        set(inventory.get("union_paths", []))
        == set(producer.get("source_blobs", {})) - {
            row["path"] for row in producer["direct_expansions"]
        },
        "matched path agreement",
    )
    producer_units = {
        row["key"]: row for row in producer.get("candidates", [])
    }
    challenge_units = {
        row["key"]: row for row in challenge.get("units", [])
    }
    require(set(challenge_units) == set(producer_units), "unit roster")
    for key, unit in challenge_units.items():
        expected = producer_units[key]
        for field in (
            "value_class",
            "behavior",
            "semantic_class",
            "realized_home_target_present",
            "rng_identity_present",
        ):
            require(unit[field] == expected[field], f"{key}: {field}")
    attacks = challenge.get("attacks", [])
    require({row["attack"] for row in attacks} == ATTACKS, "attack roster")
    require(all(row.get("rejected") is True for row in attacks), "attack rejection")
    require(challenge.get("disposition") == "pass_with_scope", "disposition")
    scope = challenge.get("scope", "")
    for term in ("no sidecar values", "physical-reset", "historical-execution", "performance"):
        require(term in scope, f"scope: {term}")
    print(f"PASS H201 independent challenge (source {sha256(CHALLENGE)})")


if __name__ == "__main__":
    validate()

