#!/usr/bin/env python3
"""Validate independent H171 target-bound repair challenge."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h170-target-bound-site-feasibility-repair.md"
TARGET_SPEC = FAMILY / "input-h170-target-spec.json"
PRODUCER = FAMILY / "result-h170-target-bound-site-feasibility-repair.json"
CHALLENGE_SOURCE = FAMILY / "challenge_h171_target_bound_site_feasibility_repair.mjs"
CHALLENGE_RESULT = (
    FAMILY / "result-h171-target-bound-site-feasibility-independent-challenge.json"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(challenge: dict[str, Any], producer: dict[str, Any]) -> None:
    require(
        challenge.get("schema")
        == "h171-target-bound-site-feasibility-independent-challenge-v1",
        "unexpected schema",
    )
    require(
        challenge.get("producer_modules_imported") is False,
        "producer module imported",
    )
    require(
        challenge.get("protocol_sha256") == sha256(PROTOCOL),
        "protocol changed",
    )
    require(
        challenge.get("target_spec_file_sha256") == sha256(TARGET_SPEC),
        "target spec changed",
    )
    require(
        challenge["upstream_hashes"]["h170_result_sha256"] == sha256(PRODUCER),
        "H170 result changed",
    )
    require(
        challenge["independently_reconstructed_decisions"]
        == producer["known_answer_decisions"],
        "known answers disagree",
    )
    require(
        challenge["independently_verified_artifact_count"]
        == producer["artifact_count"]
        == 64,
        "artifact count disagrees",
    )
    attacks = challenge["authorization_attacks"]
    require(
        len(attacks) == challenge["authorization_attacks_rejected"] == 9
        and all(row["rejected"] is True for row in attacks),
        "authorization attack coverage incomplete",
    )
    require(
        challenge["h169_bypasses_rejected"] is True
        and producer["h169_bypasses_rejected"] is True,
        "H169 bypass remains",
    )
    require(
        challenge["disposition"] == "pass_with_scope"
        and challenge["reliance_gate_passed_for_synthetic_interface_logic"] is True,
        "challenge did not pass",
    )
    require(
        challenge["real_site_qualified"] is False
        and challenge["field_collection_authorized"] is False,
        "field scope widened",
    )


def main() -> None:
    challenge = json.loads(CHALLENGE_RESULT.read_text(encoding="utf-8"))
    producer = json.loads(PRODUCER.read_text(encoding="utf-8"))
    validate(challenge, producer)
    print(
        "OK: H171 independent Node challenge agrees with H170 "
        f"(source {sha256(CHALLENGE_SOURCE)})"
    )


if __name__ == "__main__":
    main()
