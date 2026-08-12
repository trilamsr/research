#!/usr/bin/env python3
"""Validate the retained independent H203 Node challenge and scope."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


FAMILY = Path(__file__).resolve().parent
PRODUCER = FAMILY / "result-h203-phail-first-state-temporal-structure.json"
CHALLENGE = (
    FAMILY
    / "result-h203-phail-first-state-temporal-structure-independent-challenge.json"
)
EXPECTED_CLASS = "no_detectable_temporal_structure_at_fixed_resolution"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(result: dict[str, Any]) -> None:
    require(result["schema"] == "h203-node-independent-challenge-v1", "schema")
    require(result["producer_result_sha256"] == sha256(PRODUCER), "producer hash")
    require(all(result["synthetic_controls"].values()), "controls")
    require(result["maximum_observed_statistic_difference"] <= 1e-12, "difference")
    require(result["producer_classification"] == EXPECTED_CLASS, "producer class")
    require(result["independent_classification"] == EXPECTED_CLASS, "challenge class")
    require(result["producer_classification"] == result["independent_classification"], "agreement")
    require(result["later_state_or_outcome_opened"] is False, "scope")
    require(result["independence_established"] is False, "independence")
    require(result["result"] == "pass", "result")


def attack_checks(result: dict[str, Any]) -> int:
    attacks = 0
    for key in ("later_state_or_outcome_opened", "independence_established"):
        attacked = copy.deepcopy(result)
        attacked[key] = True
        try:
            validate(attacked)
        except ValueError:
            attacks += 1
    attacked = copy.deepcopy(result)
    attacked["independent_classification"] = "material_global_temporal_structure"
    try:
        validate(attacked)
    except ValueError:
        attacks += 1
    attacked = copy.deepcopy(result)
    attacked["maximum_observed_statistic_difference"] = 1e-6
    try:
        validate(attacked)
    except ValueError:
        attacks += 1
    return attacks


def main() -> None:
    result = json.loads(CHALLENGE.read_text())
    validate(result)
    attacks = attack_checks(result)
    require(attacks == 4, "attack coverage")
    print(f"OK: H203 independent challenge passes with {attacks} rejected attacks")


if __name__ == "__main__":
    main()
