#!/usr/bin/env python3
"""Validate H206's retained Node BigInt challenge and scope."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


FAMILY = Path(__file__).resolve().parent
PRODUCER = FAMILY / "result-h206-phail-monotonic-wall-clock-bridge.json"
PROJECTION = FAMILY / "projection-h206-phail-clock-offset-regimes.csv"
CHALLENGE = (
    FAMILY
    / "result-h206-phail-monotonic-wall-clock-bridge-independent-challenge.json"
)
EXPECTED_CLASS = "scale_separated_clock_offset_regimes"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(result: dict) -> None:
    require(
        result["schema"] == "h206-node-bigint-independent-challenge-v1",
        "schema",
    )
    require(result["producer_result_sha256"] == sha256(PRODUCER), "producer")
    require(
        result["producer_projection_sha256"] == sha256(PROJECTION),
        "projection",
    )
    require(result["episode_count"] == 594, "episodes")
    require(
        result["largest_adjacent_gap_ns"] == "1556979984990940",
        "largest gap",
    )
    require(
        result["second_largest_adjacent_gap_ns"] == "509323503",
        "second gap",
    )
    require(result["independent_classification"] == EXPECTED_CLASS, "class")
    require(result["exact_projection_reconstruction"] is True, "exact projection")
    require(
        [group["episode_count"] for group in result["one_hour_groups"]]
        == [250, 344],
        "group counts",
    )
    require(
        all(
            group["wall_monotonic_discordant_pairs"] == 0
            for group in result["one_hour_groups"]
        ),
        "discordance",
    )
    for key in (
        "performance_or_later_state_opened",
        "host_or_session_identity_established",
        "dependence_cluster_established",
    ):
        require(result[key] is False, key)
    require(result["result"] == "pass", "result")


def main() -> None:
    result = json.loads(CHALLENGE.read_text())
    validate(result)
    attacks = 0
    for key in (
        "performance_or_later_state_opened",
        "host_or_session_identity_established",
        "dependence_cluster_established",
    ):
        attacked = copy.deepcopy(result)
        attacked[key] = True
        try:
            validate(attacked)
        except ValueError:
            attacks += 1
    attacked = copy.deepcopy(result)
    attacked["independent_classification"] = "clock_offset_structure_without_scale_separation"
    try:
        validate(attacked)
    except ValueError:
        attacks += 1
    attacked = copy.deepcopy(result)
    attacked["exact_projection_reconstruction"] = False
    try:
        validate(attacked)
    except ValueError:
        attacks += 1
    attacked = copy.deepcopy(result)
    attacked["one_hour_groups"][0]["wall_monotonic_discordant_pairs"] = 1
    try:
        validate(attacked)
    except ValueError:
        attacks += 1
    if attacks != 6:
        raise ValueError("attack coverage")
    print(f"OK: H206 independent challenge passes with {attacks} rejected attacks")


if __name__ == "__main__":
    main()
