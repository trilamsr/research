#!/usr/bin/env python3
"""Validate the independent H166 Node reconstruction against H165."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h165-pair-conditioned-operational-target.md"
PRODUCER = FAMILY / "result-h165-pair-conditioned-operational-target.json"
CHALLENGE_SOURCE = FAMILY / "challenge_h166_pair_conditioned_operational_target.mjs"
CHALLENGE_RESULT = (
    FAMILY
    / "result-h166-pair-conditioned-operational-target-independent-challenge.json"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(challenge: dict[str, Any], producer: dict[str, Any]) -> None:
    require(
        challenge.get("schema")
        == "h166-pair-conditioned-operational-target-independent-challenge-v1",
        "unexpected challenge schema",
    )
    require(
        challenge.get("producer_modules_imported") is False,
        "producer module imported",
    )
    require(
        challenge.get("protocol_sha256") == sha256(PROTOCOL),
        "protocol changed",
    )
    independent = challenge["independent_known_answer"]
    known = producer["known_answer"]
    require(
        independent["edge_optimal_value"]
        == known["edge_optimal_routing_value"]["text"]
        == "3/4",
        "optimal routing value disagrees",
    )
    require(
        independent["lower_index_value"]
        == known["always_lower_index_value"]["text"]
        == "7/12",
        "lower-index value disagrees",
    )
    require(
        independent["lower_index_regret"]
        == known["always_lower_index_regret"]["text"]
        == "1/6",
        "routing regret disagrees",
    )
    require(
        independent["tournament_values"] == ["1/2", "1/2", "1/2"]
        and independent["unique_global_policy_identified"] is False,
        "global-policy boundary disagrees",
    )
    require(
        challenge["upstream_common_context_boundary"][
            "opposite_unique_winners"
        ]
        == [2, 0]
        and challenge["upstream_common_context_boundary"][
            "singleton_worst_regret_floor"
        ]
        == "1/3"
        and challenge["upstream_common_context_boundary"][
            "common_context_target_identified"
        ]
        is False,
        "H151--H152 boundary not retained",
    )
    attacks = challenge["semantic_attacks"]
    require(
        len(attacks) == challenge["attacks_rejected"] == 8
        and all(row["rejected"] is True for row in attacks),
        "semantic attack coverage incomplete",
    )
    require(
        challenge["upstream_hashes"]["h165_result_sha256"] == sha256(PRODUCER),
        "H165 result changed",
    )
    require(
        challenge.get("disposition") == "pass_with_scope",
        "challenge did not pass",
    )


def main() -> None:
    challenge = json.loads(CHALLENGE_RESULT.read_text(encoding="utf-8"))
    producer = json.loads(PRODUCER.read_text(encoding="utf-8"))
    validate(challenge, producer)
    print(
        "OK: H166 independent Node reconstruction agrees with H165 "
        f"(source {sha256(CHALLENGE_SOURCE)})"
    )


if __name__ == "__main__":
    main()
