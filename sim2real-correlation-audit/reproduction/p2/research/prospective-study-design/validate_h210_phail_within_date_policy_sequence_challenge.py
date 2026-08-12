#!/usr/bin/env python3
"""Validate the independent H210 Node challenge."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

FAMILY = Path(__file__).resolve().parent
PRODUCER = FAMILY / "result-h210-phail-within-date-policy-sequence.json"
CHALLENGE = FAMILY / "result-h210-phail-within-date-policy-sequence-independent-challenge.json"
PRODUCER_SHA256 = "71bf7b49976b936c147cd021776dc3c5a32a401dff5824506a28b1ae5b77d112"
KEYS = ("pooled_within_date", "regime_1_dates", "regime_2_dates")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(producer: dict[str, Any], challenge: dict[str, Any]) -> None:
    require(sha256(PRODUCER) == PRODUCER_SHA256, "producer hash")
    require(challenge["target_producer_result_sha256"] == PRODUCER_SHA256, "target")
    require(challenge["episode_count"] == 594 and challenge["date_count"] == 13, "counts")
    require(all(challenge["challenge_controls"].values()), "controls")
    require(challenge["implementation"]["producer_imported_or_executed"] is False, "independence")
    for key in KEYS:
        produced = producer["analyses"][key]
        challenged = challenge["analyses"][key]
        for metric in ("observed_same_policy_adjacency_fraction", "analytic_exchangeability_expectation"):
            require(abs(challenged[metric] - produced[metric]) <= 1e-15, f"{key} {metric}")
        require(abs(challenged["permutation_median"] - produced["permutation_median"]) <= 0.02, f"{key} median")
        require(abs(challenged["two_sided_p"] - produced["two_sided_p"]) <= 0.03, f"{key} p")
    require(challenge["classification"] == producer["classification"], "classification")
    for key in (
        "permutation_reference_treated_as_assignment_law",
        "date_treated_as_physical_session_or_cause",
        "state_or_performance_opened",
        "outcome_analysis_authorized",
    ):
        require(challenge[key] is False, key)
    require(challenge["unresolved_material_concerns"] == [], "concerns")


def mutation_attacks(producer: dict[str, Any], challenge: dict[str, Any]) -> dict[str, bool]:
    mutations = {
        "observed": lambda x: x["analyses"]["pooled_within_date"].__setitem__("observed_same_policy_adjacency_fraction", 0.9),
        "expected": lambda x: x["analyses"]["regime_1_dates"].__setitem__("analytic_exchangeability_expectation", 0.1),
        "median": lambda x: x["analyses"]["regime_2_dates"].__setitem__("permutation_median", 0.8),
        "classification": lambda x: x.__setitem__("classification", "material_pooled_within_date_policy_sequence_structure"),
        "count": lambda x: x.__setitem__("date_count", 12),
        "scope": lambda x: x.__setitem__("date_treated_as_physical_session_or_cause", True),
    }
    output = {}
    for name, mutate in mutations.items():
        attacked = copy.deepcopy(challenge)
        mutate(attacked)
        try:
            validate(producer, attacked)
        except ValueError:
            output[name] = True
        else:
            output[name] = False
    return output


def main() -> None:
    producer = json.loads(PRODUCER.read_text())
    challenge = json.loads(CHALLENGE.read_text())
    validate(producer, challenge)
    attacks = mutation_attacks(producer, challenge)
    require(all(attacks.values()), "attacks")
    print(f"OK: H210 independent challenge agrees; {len(attacks)} attacks rejected")


if __name__ == "__main__":
    main()
