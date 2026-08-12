#!/usr/bin/env python3
"""Validate the independent H207 Node/SplitMix64 challenge."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


FAMILY = Path(__file__).resolve().parent
PRODUCER = FAMILY / "result-h207-phail-clock-regime-temporal-structure.json"
CHALLENGE = (
    FAMILY
    / "result-h207-phail-clock-regime-temporal-structure-independent-challenge.json"
)
PRODUCER_SHA256 = (
    "31ef2b4162157769bf9f99ce47f50865076b99e114c7a67592319ce8df2b2252"
)
ANALYSIS_KEYS = ("pooled_within_regime", "regime_1", "regime_2")
MAX_OBSERVED_ABS_DIFFERENCE = 1e-12
MAX_MEDIAN_ABS_DIFFERENCE = 0.05
MAX_TWO_SIDED_P_ABS_DIFFERENCE = 0.02


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(producer: dict[str, Any], challenge: dict[str, Any]) -> None:
    require(sha256(PRODUCER) == PRODUCER_SHA256, "producer file hash")
    require(
        challenge["schema"]
        == "h207-phail-clock-regime-temporal-independent-challenge-v1",
        "schema",
    )
    require(
        challenge["target_producer_result_sha256"] == PRODUCER_SHA256,
        "target producer hash",
    )
    require(
        challenge["input_sha256"]["h202_projection"]
        == producer["input_sha256"]["h202_projection"],
        "H202 input hash",
    )
    require(
        challenge["input_sha256"]["h206_projection"]
        == producer["input_sha256"]["h206_projection"],
        "H206 input hash",
    )
    require(challenge["episode_count"] == 594, "episode count")
    require(challenge["group_sizes"] == {"1": 250, "2": 344}, "group sizes")
    require(challenge["pooled_pair_count"] == 592, "pooled pair count")
    require(all(challenge["challenge_controls"].values()), "challenge controls")
    require(
        challenge["implementation"]["producer_imported_or_executed"] is False,
        "implementation independence",
    )
    require(
        challenge["implementation"]["rng"]
        == "independent SplitMix64 and Fisher-Yates stream",
        "RNG independence",
    )
    require(set(challenge["analyses"]) == set(ANALYSIS_KEYS), "analysis keys")
    for key in ANALYSIS_KEYS:
        produced = producer["analyses"][key]
        challenged = challenge["analyses"][key]
        require(challenged["permutations"] == 49_999, f"{key} permutations")
        require(
            abs(
                challenged["observed_mean_successive_squared_distance"]
                - produced["observed_mean_successive_squared_distance"]
            )
            <= MAX_OBSERVED_ABS_DIFFERENCE,
            f"{key} observed statistic",
        )
        require(
            abs(challenged["permutation_median"] - produced["permutation_median"])
            <= MAX_MEDIAN_ABS_DIFFERENCE,
            f"{key} permutation median",
        )
        require(
            abs(challenged["two_sided_p"] - produced["two_sided_p"])
            <= MAX_TWO_SIDED_P_ABS_DIFFERENCE,
            f"{key} permutation p value",
        )
    require(
        challenge["classification"] == producer["classification"],
        "classification agreement",
    )
    require(
        challenge["producer_classification"] == producer["classification"],
        "producer classification trace",
    )
    require(
        challenge["later_state_or_performance_opened"] is False,
        "performance scope",
    )
    require(
        challenge["clock_regime_treated_as_session"] is False,
        "regime scope",
    )
    require(challenge["independence_established"] is False, "independence scope")
    require(
        challenge["unresolved_material_concerns"] == [],
        "unresolved material concerns",
    )


def mutation_attacks(
    producer: dict[str, Any], challenge: dict[str, Any]
) -> dict[str, bool]:
    attacks: dict[str, bool] = {}
    mutations = {
        "observed_statistic": lambda value: value["analyses"][
            "pooled_within_regime"
        ].__setitem__(
            "observed_mean_successive_squared_distance",
            value["analyses"]["pooled_within_regime"][
                "observed_mean_successive_squared_distance"
            ]
            + 0.1,
        ),
        "permutation_median": lambda value: value["analyses"]["regime_1"].__setitem__(
            "permutation_median",
            value["analyses"]["regime_1"]["permutation_median"] + 0.1,
        ),
        "permutation_p": lambda value: value["analyses"]["regime_2"].__setitem__(
            "two_sided_p",
            value["analyses"]["regime_2"]["two_sided_p"] + 0.1,
        ),
        "classification": lambda value: value.__setitem__(
            "classification", "material_pooled_clock_regime_temporal_structure"
        ),
        "group_size": lambda value: value["group_sizes"].__setitem__("2", 343),
        "scope": lambda value: value.__setitem__(
            "clock_regime_treated_as_session", True
        ),
    }
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
        "OK: H207 independent challenge agrees; "
        f"{len(attacks)} mutation attacks rejected"
    )


if __name__ == "__main__":
    main()
