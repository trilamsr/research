#!/usr/bin/env python3
"""Validate the method-distinct H238 challenge and its evidence binding."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "protocol-h238-interior-route-law-nonidentification.md"
REPAIR_PROTOCOL = HERE / "protocol-h238-challenge-repair-2026-07-31.md"
PRODUCER = HERE / "interior_route_law_nonidentification.py"
PRODUCER_RESULT = HERE / "result-h238-interior-route-law-nonidentification.json"
CHALLENGE = (
    HERE
    / "result-h238-interior-route-law-nonidentification-independent-challenge.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(data: dict[str, object]) -> None:
    assert data["schema"] == "h238-interior-route-law-independent-challenge-v1"
    assert data["status"] == "pass"
    assert data["classification"] == (
        "relative_open_within_additive_shared_success_model"
    )
    assert data["protocol_sha256"] == sha256(PROTOCOL)
    assert data["repair_protocol_sha256"] == sha256(REPAIR_PROTOCOL)
    assert data["producer_sha256"] == sha256(PRODUCER)
    assert data["producer_result_sha256"] == sha256(PRODUCER_RESULT)
    assert data["denominator"] == 5
    assert data["total_profiles"] == 455
    assert data["interior_profiles"] == 246
    assert data["boundary_profiles"] == 209
    assert data["interior_unique_winner_checks"] == 1291
    assert data["boundary_minimum_policy_exclusions"] == 329
    assert data["regret_formula_vertex_checks"] == 1365
    assert data["pair_interval_known_answers"] == 5
    assert data["mutation_controls_rejected"] == 4
    assert data["mutation_controls_rejected_names"] == [
        "remove_p_dot_a_from_regret",
        "replace_D_lt_1_with_D_le_1",
        "replace_interval_width_half_with_two_fifths",
        "claim_boundary_minimum_is_unique_winner",
    ]
    assert data["runtime"]["node"] == "v26.5.0"
    assert data["runtime"]["platform"] == "darwin"
    assert data["runtime"]["architecture"] == "arm64"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--challenge", type=Path, default=CHALLENGE)
    args = parser.parse_args()
    validate(json.loads(args.challenge.read_text(encoding="utf-8")))
    print("OK: H238 independent challenge evidence binding")


if __name__ == "__main__":
    main()
