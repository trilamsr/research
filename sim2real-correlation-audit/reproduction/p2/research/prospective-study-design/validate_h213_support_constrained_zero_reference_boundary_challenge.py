#!/usr/bin/env python3
"""Validate the retained independent H213 exact challenge."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h213-support-constrained-zero-reference-boundary.md"
PRODUCER = FAMILY / "result-h213-support-constrained-zero-reference-boundary.json"
CHALLENGE = (
    FAMILY
    / "result-h213-support-constrained-zero-reference-boundary-independent-challenge.json"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(data: dict[str, Any]) -> None:
    require(
        data.get("schema")
        == "h213-support-constrained-zero-reference-boundary-independent-challenge-v1",
        "schema",
    )
    require(data.get("protocol_sha256") == sha256(PROTOCOL), "protocol binding")
    require(data.get("producer_result_sha256") == sha256(PRODUCER), "producer binding")
    require(data.get("imports_or_executes_producer") is False, "independence")
    require(
        data.get("classification")
        == "support_constraint_creates_boundary_value_jump",
        "classification",
    )
    census = data["exact_case_census"]
    require(census["canonical_cases"] == 242, "case count")
    require(census["raw_endpoint_oracle_cases_k_le_5"] == 117, "raw count")
    require(census["distinct_label_permutations"] == 14056, "permutations")
    require(
        census["support_grid_lotteries_k_le_5_denominator_8"] == 7857,
        "grid count",
    )
    require(census["accepted_exactly_one_zero_limit_rows"] == 453, "limits")
    required_attacks = {
        "support_constrained_value_below_one_quarter": "rejected",
        "second_support_constrained_optimizer": "rejected",
        "exactly_one_zero_changes_face_only": "rejected",
        "exactly_two_zeros_raise_value": "rejected",
        "three_or_more_zeros_change_h212": "rejected",
        "raw_reduction_fails_under_support_constraint": "rejected",
        "label_dependence": "rejected",
    }
    attacks = {row["attack"]: row["disposition"] for row in data["attacks"]}
    require(attacks == required_attacks, "attack dispositions")
    require(len(data["exact_derivation"]) == 4, "derivation")
    require(all(data["producer_agreement"].values()), "producer agreement")


def main() -> None:
    validate(json.loads(CHALLENGE.read_text()))


if __name__ == "__main__":
    main()
