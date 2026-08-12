#!/usr/bin/env python3
"""Validate H205's retained independent challenge and scope."""

from __future__ import annotations

import copy
import json

import challenge_h205_phail_first_state_uniform_independence as challenge


def main() -> None:
    result = json.loads(challenge.OUTPUT.read_text())
    challenge.validate(result)
    attacks = 0
    for key in (
        "commanded_draw_or_rng_validity_established",
        "later_state_or_outcome_opened",
    ):
        attacked = copy.deepcopy(result)
        attacked[key] = True
        try:
            challenge.validate(attacked)
        except ValueError:
            attacks += 1
    attacked = copy.deepcopy(result)
    attacked["independent_classification"] = "material_joint_dependence_only"
    try:
        challenge.validate(attacked)
    except ValueError:
        attacks += 1
    attacked = copy.deepcopy(result)
    attacked["maximum_observed_statistic_difference"] = 1e-6
    try:
        challenge.validate(attacked)
    except ValueError:
        attacks += 1
    attacked = copy.deepcopy(result)
    attacked["simulations"] -= 1
    try:
        challenge.validate(attacked)
    except ValueError:
        attacks += 1
    if attacks != 5:
        raise ValueError("attack coverage")
    print(f"OK: H205 independent challenge passes with {attacks} rejected attacks")


if __name__ == "__main__":
    main()
