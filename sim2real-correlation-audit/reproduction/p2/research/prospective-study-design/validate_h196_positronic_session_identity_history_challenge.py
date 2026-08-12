#!/usr/bin/env python3
"""Validate the independent H196 Node reconstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h196-positronic-session-identity-history.md"
PRODUCER = FAMILY / "result-h196-positronic-session-identity-history.json"
CHALLENGE_SOURCE = FAMILY / "challenge_h196_positronic_session_identity_history.mjs"
CHALLENGE = FAMILY / "result-h196-positronic-session-identity-history-independent-challenge.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    producer = json.loads(PRODUCER.read_text(encoding="utf-8"))
    challenge = json.loads(CHALLENGE.read_text(encoding="utf-8"))
    require(
        challenge.get("schema")
        == "h196-positronic-session-identity-history-independent-challenge-v1",
        "schema mismatch",
    )
    require(challenge.get("producer_modules_imported") is False, "producer imported")
    require(challenge.get("protocol_sha256") == sha256(PROTOCOL), "protocol changed")
    require(challenge.get("producer_result_sha256") == sha256(PRODUCER), "producer changed")
    require(challenge.get("baseline_commit") == producer["upstream"]["baseline"]["commit"], "baseline mismatch")
    require(
        challenge.get("comparison_commit") == producer["upstream"]["comparison"]["commit"],
        "comparison mismatch",
    )
    require(
        challenge.get("independently_reconstructed_history_commit_count")
        == producer["history"]["commit_count"]
        == 51,
        "history count mismatch",
    )
    require(
        challenge.get("independently_reconstructed_final_static_rrd_key")
        == producer["trace"]["final_static_rrd_key"]
        == "inference.policy.server.recording.rrd",
        "RRD key mismatch",
    )
    require(
        challenge.get("independently_reconstructed_episode_uid")
        == "uuid.uuid4().hex in finalized episode meta.json",
        "episode UID mismatch",
    )
    require(challenge.get("episode_uid_is_shared_server_session_id") is False, "UID promoted")
    require(challenge.get("rrd_path_is_episode_to_server_recording_join") is True, "RRD join missing")
    require(challenge.get("rrd_filename_globally_unique_across_restarts") is False, "RRD uniqueness promoted")
    require(challenge.get("physical_reset_or_operator_session_established") is False, "cluster promoted")
    require(
        challenge.get("semantic_attacks_rejected") == len(challenge.get("semantic_attacks", [])) == 10
        and all(row.get("rejected") is True for row in challenge["semantic_attacks"]),
        "attack coverage incomplete",
    )
    require(challenge.get("performance_or_dataset_content_opened") is False, "dataset content opened")
    require(challenge.get("server_recording_opened") is False, "recording opened")
    require(challenge.get("agrees_with_producer_with_scope_narrowing") is True, "challenge disagrees")
    require(challenge.get("disposition") == "pass_with_scope_narrowing", "challenge did not pass")
    print(f"PASS H196 challenge validation (source {sha256(CHALLENGE_SOURCE)})")


if __name__ == "__main__":
    main()
