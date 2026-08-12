#!/usr/bin/env python3
"""Validate the retained independent H212 challenge and required attacks."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h212-zero-reference-weight-edge-box-boundary.md"
PRODUCER = FAMILY / "result-h212-zero-reference-weight-edge-box-boundary.json"
CHALLENGE = (
    FAMILY
    / "result-h212-zero-reference-weight-edge-box-boundary-independent-challenge.json"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(data: dict[str, Any]) -> None:
    require(
        data.get("schema")
        == "h212-zero-reference-weight-edge-box-boundary-independent-challenge-v1",
        "schema",
    )
    require(data.get("protocol_sha256") == sha256(PROTOCOL), "protocol binding")
    require(data.get("producer_result_sha256") == sha256(PRODUCER), "producer binding")
    require(data.get("imports_or_executes_producer") is False, "independence declaration")
    require(
        data.get("classification") == "value_and_optimizer_extend_without_change",
        "classification",
    )
    census = data["exact_case_census"]
    require(census["canonical_cases"] == 242, "case count")
    require(census["raw_endpoint_oracle_probes_k_le_5"] == 247, "raw endpoint count")
    require(census["distinct_label_permutations"] == 14056, "permutation count")
    require(census["just_outside_segment_attacks"] == 238, "outside attacks")
    require(len(data["exact_derivation"]) == 4, "derivation")
    attacks = {row["attack"]: row["disposition"] for row in data["attacks"]}
    required = {
        "value_formula_boundary_failure": "rejected",
        "new_optimizer_direction_on_boundary": "rejected",
        "raw_reduction_invalid_at_zero_weight": "rejected",
        "label_or_tie_dependence": "rejected",
        "segment_endpoint_is_not_complete": "rejected",
        "zero_weight_implies_zero_lottery_mass": "confirmed_as_false",
        "three_or_more_zero_weights_create_a_larger_face": "rejected",
    }
    require(attacks == required, "attack dispositions")
    require(all(data["producer_agreement"].values()), "producer agreement")


def main() -> None:
    data = json.loads(CHALLENGE.read_text())
    validate(data)


if __name__ == "__main__":
    main()
