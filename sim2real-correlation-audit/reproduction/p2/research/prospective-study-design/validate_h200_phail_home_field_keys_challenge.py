#!/usr/bin/env python3
"""Validate H200 independent key-only challenge and producer agreement."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


FAMILY = Path(__file__).resolve().parent
PRODUCER = FAMILY / "result-h200-phail-home-field-key-inventory.json"
CHALLENGE = (
    FAMILY
    / "result-h200-phail-home-field-key-inventory-independent-challenge.json"
)
ATTACKS = {
    "candidate_name_is_realized_draw",
    "joint_names_array_is_home_target",
    "joint_signal_string_is_reset_evidence",
    "pose_signals_array_is_home_target",
    "all_episode_presence_implies_varying_value",
    "key_only_inventory_exposes_primitive_values",
    "public_sidecar_null_would_prove_private_absence",
    "schema_descriptor_proves_historical_reset_execution",
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
        == "h200-phail-home-field-key-inventory-independent-challenge-v1",
        "schema",
    )
    method = challenge.get("method", "")
    require("Independent Node" in method, "method")
    require("no producer-module import" in method, "independence")
    require(challenge.get("input_sha256") == producer.get("input_sha256"), "input")
    require(challenge.get("episode_count") == 594, "episodes")
    require(challenge.get("verified_sidecar_object_count") == 1188, "sidecars")
    require(challenge.get("key_rows") == producer.get("key_rows"), "key agreement")
    require(
        challenge.get("candidate_count") == producer.get("candidate_count") == 3,
        "candidate count",
    )
    require(
        challenge.get("disposition") == producer.get("disposition"),
        "disposition",
    )
    attacks = challenge.get("attacks", [])
    require({row["attack"] for row in attacks} == ATTACKS, "attack roster")
    require(all(row.get("rejected") is True for row in attacks), "attack rejection")
    scope = challenge.get("scope", "")
    for term in ("no values", "physical-reset", "historical-execution", "performance"):
        require(term in scope, f"scope: {term}")
    print(f"PASS H200 independent challenge (source {sha256(CHALLENGE)})")


if __name__ == "__main__":
    validate()

