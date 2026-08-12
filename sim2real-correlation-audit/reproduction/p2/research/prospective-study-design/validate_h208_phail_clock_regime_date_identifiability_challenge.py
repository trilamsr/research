#!/usr/bin/env python3
"""Validate the independent H208 Ruby/Rational challenge."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


FAMILY = Path(__file__).resolve().parent
PRODUCER = FAMILY / "result-h208-phail-clock-regime-date-identifiability.json"
CHALLENGE = (
    FAMILY
    / "result-h208-phail-clock-regime-date-identifiability-independent-challenge.json"
)
PRODUCER_SHA256 = (
    "df6c42066f26c7bbd69be25d01ef0d72517f2546c0a1d02d129b6fdc8b6981db"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(producer: dict[str, Any], challenge: dict[str, Any]) -> None:
    require(sha256(PRODUCER) == PRODUCER_SHA256, "producer file hash")
    require(
        challenge["schema"]
        == "h208-phail-clock-regime-date-identifiability-independent-challenge-v1",
        "schema",
    )
    require(
        challenge["target_producer_result_sha256"] == PRODUCER_SHA256,
        "target producer hash",
    )
    require(challenge["episode_count"] == 594, "episode count")
    require(all(challenge["challenge_controls"].values()), "challenge controls")
    require(
        challenge["implementation"]["producer_imported_or_executed"] is False,
        "implementation independence",
    )
    require(
        challenge["date_alias"] == producer["date_alias"],
        "date alias agreement",
    )
    require(
        challenge["policy_regime_support"] == producer["policy_regime_support"],
        "policy-regime table agreement",
    )
    for key in (
        "policy_distribution_total_variation",
        "pearson_chi_square_descriptive",
        "cramers_v",
    ):
        require(
            abs(
                challenge["composition_metrics"][key]
                - producer["composition_metrics"][key]
            )
            <= 1e-12,
            f"{key} agreement",
        )
    require(
        challenge["classification"] == producer["classification"],
        "classification agreement",
    )
    require(challenge["sampling_p_value_reported"] is False, "sampling p value")
    require(
        challenge["later_state_or_performance_opened"] is False,
        "performance scope",
    )
    require(
        challenge["clock_regime_treated_as_session_or_cause"] is False,
        "regime scope",
    )
    require(challenge["outcome_analysis_authorized"] is False, "outcome scope")
    require(
        challenge["unresolved_material_concerns"] == [],
        "unresolved material concerns",
    )


def mutation_attacks(
    producer: dict[str, Any], challenge: dict[str, Any]
) -> dict[str, bool]:
    mutations = {
        "date_alias": lambda value: value["date_alias"].__setitem__(
            "rank_increment", 1
        ),
        "policy_cell": lambda value: value["policy_regime_support"]["counts"][
            "act"
        ].__setitem__("1", 106),
        "total_variation": lambda value: value["composition_metrics"].__setitem__(
            "policy_distribution_total_variation", 0.1
        ),
        "classification": lambda value: value.__setitem__(
            "classification", "date_separable_at_utc_day_resolution"
        ),
        "sampling_p": lambda value: value.__setitem__(
            "sampling_p_value_reported", True
        ),
        "scope": lambda value: value.__setitem__(
            "clock_regime_treated_as_session_or_cause", True
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
        "OK: H208 independent Ruby challenge agrees; "
        f"{len(attacks)} mutation attacks rejected"
    )


if __name__ == "__main__":
    main()
