#!/usr/bin/env python3
"""Validate the independent H179 reconstruction against H178."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h178-cross-system-action-order-source-audit.md"
PRODUCER = FAMILY / "result-h178-cross-system-action-order-source-audit.json"
CHALLENGE_SOURCE = FAMILY / "challenge_h179_cross_system_action_order.mjs"
CHALLENGE = (
    FAMILY / "result-h179-cross-system-action-order-independent-challenge.json"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(challenge: dict[str, Any], producer: dict[str, Any]) -> None:
    require(
        challenge.get("schema")
        == "h179-cross-system-action-order-independent-challenge-v1",
        "unexpected challenge schema",
    )
    require(challenge.get("producer_modules_imported") is False, "producer imported")
    require(challenge.get("protocol_sha256") == sha256(PROTOCOL), "protocol changed")
    require(
        challenge["upstream_hashes"]["h178_result_sha256"] == sha256(PRODUCER),
        "producer result changed",
    )
    require(
        challenge["independently_reconstructed_row_count"]
        == producer["row_count"]
        == 70,
        "row count disagrees",
    )
    require(
        challenge["independently_reconstructed_positive_contrasts"]
        == producer["positive_contrast_systems"]
        == ["umi_bench", "robodojo"],
        "positive contrasts disagree",
    )
    require(
        challenge["independently_reconstructed_second_mismatches"]
        == producer["second_mismatch_systems"]
        == [],
        "second mismatch decision disagrees",
    )
    require(
        challenge["decision"] == producer["decision"] == "positive_contrast_found",
        "decision disagrees",
    )
    require(
        challenge["positive_contrast_strength"]
        == producer["positive_contrast_strength"]
        == "source_described",
        "contrast strength disagrees",
    )
    require(
        challenge["semantic_attacks_rejected"]
        == len(challenge["semantic_attacks"])
        == 22
        and all(row["rejected"] is True for row in challenge["semantic_attacks"]),
        "semantic attack coverage incomplete",
    )
    require(challenge.get("outcome_fields_accessed_or_used") is False, "outcomes used")
    require(challenge.get("agrees_with_h178") is True, "challenge disagrees")
    require(challenge.get("disposition") == "pass_with_scope", "challenge did not pass")


def main() -> None:
    challenge = json.loads(CHALLENGE.read_text(encoding="utf-8"))
    producer = json.loads(PRODUCER.read_text(encoding="utf-8"))
    validate(challenge, producer)
    print(
        "OK: H179 independent Node challenge agrees with H178 "
        f"(source {sha256(CHALLENGE_SOURCE)})"
    )


if __name__ == "__main__":
    main()
