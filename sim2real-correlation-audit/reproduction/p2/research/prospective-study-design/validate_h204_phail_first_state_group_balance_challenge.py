#!/usr/bin/env python3
"""Validate H204's retained independent challenge and scope."""

from __future__ import annotations

import copy
import json

import challenge_h204_phail_first_state_group_balance as challenge


def main() -> None:
    result = json.loads(challenge.OUTPUT.read_text())
    challenge.validate(result)
    attacks = 0
    for key in ("later_state_or_outcome_opened", "full_physical_balance_established"):
        attacked = copy.deepcopy(result)
        attacked[key] = True
        try:
            challenge.validate(attacked)
        except ValueError:
            attacks += 1
    attacked = copy.deepcopy(result)
    attacked["independent_classification"] = "material_policy_initial_state_association"
    try:
        challenge.validate(attacked)
    except ValueError:
        attacks += 1
    attacked = copy.deepcopy(result)
    attacked["maximum_observed_r2_difference"] = 1e-6
    try:
        challenge.validate(attacked)
    except ValueError:
        attacks += 1
    if attacks != 4:
        raise ValueError("attack coverage")
    print(f"OK: H204 independent challenge passes with {attacks} rejected attacks")


if __name__ == "__main__":
    main()
