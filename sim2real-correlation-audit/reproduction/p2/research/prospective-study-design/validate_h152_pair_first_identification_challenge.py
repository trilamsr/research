#!/usr/bin/env python3
"""Validate the independent Node H152 result against H151."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h151-pair-first-common-context-identification.md"
PRODUCER = FAMILY / "result-h151-pair-first-common-context-identification.json"
CHALLENGE_SOURCE = FAMILY / "challenge_h152_pair_first_identification.mjs"
CHALLENGE_RESULT = (
    FAMILY / "result-h152-pair-first-identification-independent-challenge.json"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(data: dict[str, Any]) -> None:
    producer = json.loads(PRODUCER.read_text(encoding="utf-8"))
    require(
        data.get("schema")
        == "h152-pair-first-identification-independent-challenge-v1",
        "unexpected schema",
    )
    require(data.get("producer_modules_imported") is False, "producer imported")
    require(data.get("protocol_sha256") == sha256(PROTOCOL), "protocol changed")
    require(
        data["low_world"]["observed_projection"]
        == data["high_world"]["observed_projection"],
        "independent worlds are not observationally equivalent",
    )
    require(
        data["low_world"]["unique_winner"]
        == producer["world_low"]["unique_winner"]
        == 2
        and data["high_world"]["unique_winner"]
        == producer["world_high"]["unique_winner"]
        == 0,
        "winner reversal disagrees",
    )
    require(
        data["pair_conditioned_policy_values"] == ["1/2", "1/2", "1/2"],
        "pair-conditioned tie disagrees",
    )
    require(
        data["endpoint_completions_exhausted"]
        == producer["endpoint_regret_census"]["endpoint_completions_exhausted"]
        == 8,
        "endpoint census disagrees",
    )
    require(
        data["singleton_worst_regret"] == ["1/3", "1/3", "1/3"],
        "singleton regret floor disagrees",
    )
    require(
        data.get("complete_pair_support_identifies_common_context_target")
        is False,
        "identification boundary weakened",
    )
    require(data.get("disposition") == "pass_with_scope", "challenge did not pass")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", type=Path, default=CHALLENGE_RESULT)
    args = parser.parse_args()
    validate(json.loads(args.result.read_text(encoding="utf-8")))
    print(
        "OK: H152 independent Node reconstruction agrees with H151 "
        f"(source {sha256(CHALLENGE_SOURCE)})"
    )


if __name__ == "__main__":
    main()
