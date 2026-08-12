#!/usr/bin/env python3
"""Validate independence and agreement of the H198 Node challenge."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


FAMILY = Path(__file__).resolve().parent
PRODUCER = FAMILY / "result-h198-current-phail-lifecycle-binding.json"
CHALLENGE = FAMILY / "result-h198-current-phail-lifecycle-binding-independent-challenge.json"
H196 = FAMILY / "result-h196-positronic-session-identity-history.json"
UNIT_NAMES = (
    "phail_real_hardware_binding",
    "phail_task_binding",
    "pre_session_scene_reset_call",
    "scene_reset_completion_gate",
    "inter_episode_home_command",
    "home_completion_gate",
    "post_reset_recording_boundary",
    "persistent_episode_identity",
    "persistent_operator_session_identity",
    "persistent_reset_carryover_evidence",
    "persistent_directive_context",
    "server_recording_join",
)
ATTACKS = {
    "generic_task_reset_is_phail_binding",
    "synchronous_driver_reset_is_preopen_acceptance",
    "robot_state_filter_gates_all_recording",
    "arbitrary_context_is_operator_session_id",
    "episode_uuid_is_operator_session_id",
    "reset_command_is_persistent_reset_evidence",
    "abort_is_persistent_reset_evidence",
    "current_source_proves_historical_v1_deployment",
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
        == "h198-current-phail-lifecycle-binding-independent-challenge-v1",
        "schema",
    )
    require("Node" in challenge.get("method", ""), "independent method")
    require("imports no producer module" in challenge.get("method", ""), "independence")
    require(challenge.get("commit") == producer.get("commit"), "commit")
    require(challenge.get("h196_sha256") == sha256(H196), "H196 binding")
    producer_units = {row["unit"]: row["status"] for row in producer["units"]}
    challenge_units = {row["unit"]: row["status"] for row in challenge["units"]}
    require(list(challenge_units) == list(UNIT_NAMES), "unit roster/order")
    require(challenge_units == producer_units, "unit agreement")
    require(
        challenge.get("classification") == producer.get("classification"),
        "classification agreement",
    )
    require(challenge.get("supported_count") == 5, "supported count")
    require(challenge.get("not_supported_count") == 7, "not-supported count")
    attacks = challenge.get("attacks")
    require({row["attack"] for row in attacks} == ATTACKS, "attack roster")
    require(all(row.get("rejected") is True for row in attacks), "attack rejection")
    require(challenge.get("disposition") == "pass_with_scope", "disposition")
    require(len(challenge.get("source_blobs", [])) == 12, "source blob coverage")
    scope = challenge.get("scope", "")
    require(
        "no physical-success" in scope
        and "historical-deployment" in scope
        and "exchangeability" in scope,
        "scope",
    )
    print(f"PASS H198 challenge validation (source {sha256(CHALLENGE)})")


if __name__ == "__main__":
    validate()
