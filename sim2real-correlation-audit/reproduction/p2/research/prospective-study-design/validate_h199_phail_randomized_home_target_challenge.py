#!/usr/bin/env python3
"""Validate independence, agreement, and scope of the H199 challenge."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


FAMILY = Path(__file__).resolve().parent
PRODUCER = FAMILY / "result-h199-phail-randomized-home-target.json"
CHALLENGE = (
    FAMILY
    / "result-h199-phail-randomized-home-target-independent-challenge.json"
)
ATTACKS = {
    "driver_default_alone_proves_phail_binding",
    "zero_variation_is_randomized_home",
    "base_home_config_is_realized_draw",
    "synchronous_motion_is_persistent_evidence",
    "outside_window_command_is_recorded_evidence",
    "maximum_joint_norm_equals_rms",
    "joint_norm_is_end_effector_displacement",
    "tagged_source_proves_historical_execution",
    "randomization_itself_is_reset_defect",
    "unrecorded_draw_proves_performance_effect",
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
        == "h199-phail-randomized-home-target-independent-challenge-v1",
        "schema",
    )
    method = challenge.get("method", "")
    require("Independent Node" in method, "independent method")
    require("imports no producer module" in method, "module independence")
    require(
        challenge.get("classification") == producer.get("classification"),
        "classification agreement",
    )
    producer_endpoints = {
        row["revision"]: row for row in producer.get("endpoints", [])
    }
    challenge_endpoints = {
        row["revision"]: row for row in challenge.get("endpoints", [])
    }
    require(set(challenge_endpoints) == set(producer_endpoints), "endpoint roster")
    for revision, observed in challenge_endpoints.items():
        expected = producer_endpoints[revision]
        require(
            observed["phail_droid_binding"] == expected["phail_droid_binding"],
            f"PhAIL binding: {revision}",
        )
        require(
            observed["droid_arm_reset_binding"]
            == expected["droid_arm_reset_binding"],
            f"reset binding: {revision}",
        )
        require(
            observed["variation_rad"]
            == expected["effective_home_joints_variation_rad"],
            f"variation: {revision}",
        )
        require(
            observed["realized_target_serialized"]
            == expected["realized_target_serialized"],
            f"target serialization: {revision}",
        )
        require(
            observed["seed_or_rng_state_serialized"]
            == expected["seed_or_rng_state_serialized"],
            f"RNG serialization: {revision}",
        )
        require(len(observed["source_blobs"]) == 11, f"source roster: {revision}")
    q_producer = producer["quantitative_summary"]
    q_challenge = challenge["quantitative"]
    for field in (
        "maximum_euclidean_joint_perturbation_rad",
        "rms_euclidean_joint_perturbation_rad",
    ):
        require(
            math.isclose(q_challenge[field], q_producer[field], abs_tol=1e-15),
            field,
        )
    attacks = challenge.get("attacks", [])
    require({row["attack"] for row in attacks} == ATTACKS, "attack roster")
    require(all(row.get("rejected") is True for row in attacks), "attack rejection")
    require(challenge.get("disposition") == "pass_with_scope", "disposition")
    scope = challenge.get("scope", "")
    for term in (
        "historical-execution",
        "physical-reset-adequacy",
        "end-effector",
        "exchangeability",
        "performance-effect",
    ):
        require(term in scope, f"scope: {term}")
    print(f"PASS H199 challenge validation (source {sha256(CHALLENGE)})")


if __name__ == "__main__":
    validate()

