#!/usr/bin/env python3
"""Validate independent H168 public-applicability challenge."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h167-public-pair-routing-applicability.md"
PRODUCER = FAMILY / "result-h167-public-pair-routing-applicability.json"
CHALLENGE_SOURCE = FAMILY / "challenge_h168_public_pair_routing_applicability.mjs"
CHALLENGE_RESULT = (
    FAMILY
    / "result-h168-public-pair-routing-applicability-independent-challenge.json"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(challenge: dict[str, Any], producer: dict[str, Any]) -> None:
    require(
        challenge.get("schema")
        == "h168-public-pair-routing-applicability-independent-challenge-v1",
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
        challenge.get("h167_result_sha256") == sha256(PRODUCER),
        "H167 result changed",
    )
    require(
        challenge["independently_reconstructed_status_vector"]
        == [row["status"] for row in producer["units"]],
        "unit statuses disagree",
    )
    require(
        challenge["failed_required_unit_ids"]
        == [row["unit_id"] for row in producer["failed_required_units"]]
        and challenge["failed_required_unit_count"]
        == producer["failed_required_unit_count"]
        == 11,
        "failed conjunction disagrees",
    )
    require(
        challenge["decision"]
        == producer["decision"]
        == "not_qualified_for_public_pair_routing_application",
        "decision disagrees",
    )
    require(
        challenge["public_action_mismatch"] is True
        and producer["public_action_mismatch"] is True,
        "action mismatch disagrees",
    )
    attacks = challenge["semantic_attacks"]
    require(
        len(attacks) == challenge["attacks_rejected"] == 7
        and all(row["rejected"] is True for row in attacks),
        "attack coverage incomplete",
    )
    require(
        challenge["outcome_fields_accessed_or_used"] is False,
        "challenge used outcomes",
    )
    require(challenge["disposition"] == "pass_with_scope", "challenge did not pass")


def main() -> None:
    challenge = json.loads(CHALLENGE_RESULT.read_text(encoding="utf-8"))
    producer = json.loads(PRODUCER.read_text(encoding="utf-8"))
    validate(challenge, producer)
    print(
        "OK: H168 independent Node challenge agrees with H167 "
        f"(source {sha256(CHALLENGE_SOURCE)})"
    )


if __name__ == "__main__":
    main()
