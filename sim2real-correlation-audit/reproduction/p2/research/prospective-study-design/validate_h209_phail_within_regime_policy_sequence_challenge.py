#!/usr/bin/env python3
"""Validate the independent H209 Node/SplitMix64 challenge."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


FAMILY = Path(__file__).resolve().parent
PRODUCER = FAMILY / "result-h209-phail-within-regime-policy-sequence.json"
CHALLENGE = (
    FAMILY
    / "result-h209-phail-within-regime-policy-sequence-independent-challenge.json"
)
PRODUCER_SHA256 = (
    "2879b1c4b0ade1e4d1fd47e5a0db5312fce2d401c5f1580f7e2af2c211da7794"
)
KEYS = ("pooled_within_regime", "regime_1", "regime_2")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(producer: dict[str, Any], challenge: dict[str, Any]) -> None:
    require(sha256(PRODUCER) == PRODUCER_SHA256, "producer hash")
    require(
        challenge["schema"]
        == "h209-phail-within-regime-policy-sequence-independent-challenge-v1",
        "schema",
    )
    require(
        challenge["target_producer_result_sha256"] == PRODUCER_SHA256,
        "target hash",
    )
    require(challenge["episode_count"] == 594, "episode count")
    require(challenge["group_sizes"] == {"1": 250, "2": 344}, "group sizes")
    require(all(challenge["challenge_controls"].values()), "controls")
    require(
        challenge["implementation"]["producer_imported_or_executed"] is False,
        "independence",
    )
    for key in KEYS:
        produced = producer["analyses"][key]
        challenged = challenge["analyses"][key]
        require(challenged["permutations"] == 49_999, f"{key} permutations")
        for metric in (
            "observed_same_policy_adjacency_fraction",
            "analytic_exchangeability_expectation",
        ):
            require(
                abs(challenged[metric] - produced[metric]) <= 1e-15,
                f"{key} {metric}",
            )
        require(
            abs(challenged["permutation_median"] - produced["permutation_median"])
            <= 0.02,
            f"{key} median",
        )
        require(
            abs(challenged["two_sided_p"] - produced["two_sided_p"]) <= 0.02,
            f"{key} p value",
        )
    require(
        challenge["classification"] == producer["classification"],
        "classification",
    )
    for key, message in (
        ("permutation_reference_treated_as_assignment_law", "assignment scope"),
        ("state_or_performance_opened", "data scope"),
        ("scheduler_or_cause_identified", "cause scope"),
        ("outcome_analysis_authorized", "outcome scope"),
    ):
        require(challenge[key] is False, message)
    require(
        challenge["unresolved_material_concerns"] == [],
        "unresolved concerns",
    )


def mutation_attacks(
    producer: dict[str, Any], challenge: dict[str, Any]
) -> dict[str, bool]:
    mutations = {
        "observed": lambda value: value["analyses"][
            "pooled_within_regime"
        ].__setitem__(
            "observed_same_policy_adjacency_fraction",
            value["analyses"]["pooled_within_regime"][
                "observed_same_policy_adjacency_fraction"
            ]
            + 0.1,
        ),
        "expectation": lambda value: value["analyses"]["regime_1"].__setitem__(
            "analytic_exchangeability_expectation", 0.1
        ),
        "median": lambda value: value["analyses"]["regime_2"].__setitem__(
            "permutation_median", 0.5
        ),
        "classification": lambda value: value.__setitem__(
            "classification", "material_pooled_policy_sequence_structure"
        ),
        "group_size": lambda value: value["group_sizes"].__setitem__("1", 249),
        "scope": lambda value: value.__setitem__(
            "permutation_reference_treated_as_assignment_law", True
        ),
    }
    attacks: dict[str, bool] = {}
    for name, mutate in mutations.items():
        attacked = copy.deepcopy(challenge)
        mutate(attacked)
        try:
            validate(producer, attacked)
        except ValueError:
            attacks[name] = True
        else:
            attacks[name] = False
    return attacks


def main() -> None:
    producer = json.loads(PRODUCER.read_text())
    challenge = json.loads(CHALLENGE.read_text())
    validate(producer, challenge)
    attacks = mutation_attacks(producer, challenge)
    require(all(attacks.values()), "mutation attacks")
    print(
        "OK: H209 independent challenge agrees; "
        f"{len(attacks)} mutation attacks rejected"
    )


if __name__ == "__main__":
    main()
