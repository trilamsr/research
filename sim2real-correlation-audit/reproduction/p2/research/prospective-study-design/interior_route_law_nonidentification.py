#!/usr/bin/env python3
"""H238 exact interior routed-law non-identification checks."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
from fractions import Fraction
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "protocol-h238-interior-route-law-nonidentification.md"
OUTPUT = HERE / "result-h238-interior-route-law-nonidentification.json"
HALF = Fraction(1, 2)
QUARTER = Fraction(1, 4)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_profile(profile: tuple[Fraction, ...]) -> None:
    require(len(profile) >= 3, "K must be at least three")
    require(all(0 <= value <= 1 for value in profile), "profile outside [0,1]")


def validate_lottery(lottery: tuple[Fraction, ...], k: int) -> None:
    require(len(lottery) == k, "lottery dimension changed")
    require(all(value >= 0 for value in lottery), "negative lottery weight")
    require(sum(lottery) == 1, "lottery does not sum to one")


def observed_score(
    profile: tuple[Fraction, ...], i: int, j: int
) -> Fraction:
    validate_profile(profile)
    require(i != j, "pair endpoints must differ")
    require(0 <= i < len(profile) and 0 <= j < len(profile), "invalid endpoint")
    score = HALF + HALF * (profile[i] - profile[j])
    require(0 <= score <= 1, "observed score outside [0,1]")
    return score


def pair_target_interval(observed: Fraction) -> tuple[Fraction, Fraction]:
    require(0 <= observed <= 1, "observed score outside [0,1]")
    return observed / 2, (observed + 1) / 2


def profile_range(profile: tuple[Fraction, ...]) -> Fraction:
    validate_profile(profile)
    return max(profile) - min(profile)


def target_order_values(
    profile: tuple[Fraction, ...], missing: tuple[Fraction, ...]
) -> tuple[Fraction, ...]:
    validate_profile(profile)
    require(len(missing) == len(profile), "missing-context dimension changed")
    require(all(0 <= value <= 1 for value in missing), "missing mean outside [0,1]")
    return tuple(a + x for a, x in zip(profile, missing))


def winner_set(values: tuple[Fraction, ...]) -> tuple[int, ...]:
    require(bool(values), "empty value vector")
    maximum = max(values)
    return tuple(index for index, value in enumerate(values) if value == maximum)


def unit_witness(k: int, winner: int) -> tuple[Fraction, ...]:
    require(k >= 3, "K must be at least three")
    require(0 <= winner < k, "invalid winner")
    return tuple(Fraction(index == winner) for index in range(k))


def can_be_unique_winner(
    profile: tuple[Fraction, ...], winner: int
) -> bool:
    validate_profile(profile)
    require(0 <= winner < len(profile), "invalid winner")
    return profile[winner] + 1 > max(
        profile[index] for index in range(len(profile)) if index != winner
    )


def unique_winner_witnesses(
    profile: tuple[Fraction, ...],
) -> dict[int, tuple[Fraction, ...]]:
    validate_profile(profile)
    witnesses: dict[int, tuple[Fraction, ...]] = {}
    for winner in range(len(profile)):
        witness = unit_witness(len(profile), winner)
        if winner_set(target_order_values(profile, witness)) == (winner,):
            witnesses[winner] = witness
        require(
            (winner in witnesses) == can_be_unique_winner(profile, winner),
            "analytic and explicit winner witnesses disagree",
        )
    return witnesses


def candidate_lotteries(k: int) -> tuple[tuple[Fraction, ...], ...]:
    require(k >= 3, "K must be at least three")
    triangular = k * (k + 1) // 2
    return (
        tuple(Fraction(1, k) for _ in range(k)),
        (Fraction(1),) + (Fraction(0),) * (k - 1),
        tuple(Fraction(index + 1, triangular) for index in range(k)),
    )


def vertex_regret(
    profile: tuple[Fraction, ...],
    lottery: tuple[Fraction, ...],
    missing: tuple[Fraction, ...],
) -> Fraction:
    validate_profile(profile)
    validate_lottery(lottery, len(profile))
    values = target_order_values(profile, missing)
    return QUARTER * (
        max(values) - sum(weight * value for weight, value in zip(lottery, values))
    )


def enumerated_worst_regret(
    profile: tuple[Fraction, ...], lottery: tuple[Fraction, ...]
) -> Fraction:
    validate_profile(profile)
    validate_lottery(lottery, len(profile))
    return max(
        vertex_regret(
            profile,
            lottery,
            tuple(Fraction(value) for value in vertex),
        )
        for vertex in itertools.product((0, 1), repeat=len(profile))
    )


def formula_worst_regret(
    profile: tuple[Fraction, ...], lottery: tuple[Fraction, ...]
) -> Fraction:
    validate_profile(profile)
    validate_lottery(lottery, len(profile))
    weighted_observed = sum(
        weight * value for weight, value in zip(lottery, profile)
    )
    support = max(
        value - weight for value, weight in zip(profile, lottery)
    )
    return QUARTER * (1 - weighted_observed + support)


def normalized_profiles(k: int, denominator: int) -> Iterable[tuple[Fraction, ...]]:
    require(k >= 3, "K must be at least three")
    require(denominator >= 1, "denominator must be positive")
    for tail in itertools.combinations_with_replacement(
        range(denominator + 1), k - 1
    ):
        row = (0,) + tail
        yield tuple(Fraction(value, denominator) for value in row)


def verify_stage_zero() -> dict[str, object]:
    interval_rows = []
    for observed in (
        Fraction(0),
        Fraction(1, 4),
        Fraction(1, 2),
        Fraction(3, 4),
        Fraction(1),
    ):
        low, high = pair_target_interval(observed)
        require(high - low == HALF, "pair interval width changed")
        require(
            (low < HALF < high) == (0 < observed < 1),
            "pair interval straddle rule changed",
        )
        interval_rows.append(
            {
                "observed": str(observed),
                "target_interval": [str(low), str(high)],
                "strictly_straddles_half": low < HALF < high,
            }
        )

    interior_profiles = (
        (Fraction(0), Fraction(1, 4), Fraction(1, 2)),
        (Fraction(0), Fraction(1, 3), Fraction(2, 3), Fraction(5, 6)),
    )
    interior_rows = []
    regret_checks = 0
    for profile in interior_profiles:
        witnesses = unique_winner_witnesses(profile)
        require(len(witnesses) == len(profile), "interior known answer lost a winner")
        for lottery in candidate_lotteries(len(profile)):
            require(
                enumerated_worst_regret(profile, lottery)
                == formula_worst_regret(profile, lottery),
                "stage-zero regret formula mismatch",
            )
            regret_checks += 1
        interior_rows.append(
            {
                "profile": [str(value) for value in profile],
                "range": str(profile_range(profile)),
                "compatible_unique_winners": [
                    winner + 1 for winner in sorted(witnesses)
                ],
            }
        )

    boundary = (Fraction(0), Fraction(1, 2), Fraction(1))
    boundary_winners = unique_winner_witnesses(boundary)
    require(0 not in boundary_winners, "minimum boundary policy became unique")
    require(set(boundary_winners) == {1, 2}, "boundary known answer changed")
    return {
        "pair_interval_rows": interval_rows,
        "interior_profiles": interior_rows,
        "boundary_profile": {
            "profile": [str(value) for value in boundary],
            "compatible_unique_winners": [
                winner + 1 for winner in sorted(boundary_winners)
            ],
            "minimum_policy_excluded": True,
        },
        "regret_formula_checks": regret_checks,
    }


def exhaustive_census(denominator: int = 6) -> dict[str, object]:
    rows = []
    total_profiles = 0
    interior_profiles = 0
    boundary_profiles = 0
    winner_checks = 0
    boundary_exclusions = 0
    regret_checks = 0
    offset_checks = 0
    for k in range(3, 7):
        k_profiles = 0
        k_interior = 0
        k_boundary = 0
        for profile in normalized_profiles(k, denominator):
            k_profiles += 1
            total_profiles += 1
            witnesses = unique_winner_witnesses(profile)
            width = profile_range(profile)
            if width < 1:
                require(
                    len(witnesses) == k,
                    "interior profile did not admit every unique winner",
                )
                interior_profiles += 1
                k_interior += 1
                winner_checks += k
            else:
                require(width == 1, "normalized grid range exceeded one")
                minima = {
                    index
                    for index, value in enumerate(profile)
                    if value == min(profile)
                }
                require(
                    minima.isdisjoint(witnesses),
                    "minimum boundary policy became a unique winner",
                )
                boundary_profiles += 1
                k_boundary += 1
                boundary_exclusions += len(minima)

            for lottery in candidate_lotteries(k):
                require(
                    enumerated_worst_regret(profile, lottery)
                    == formula_worst_regret(profile, lottery),
                    "census regret formula mismatch",
                )
                regret_checks += 1

            if max(profile) <= Fraction(denominator - 1, denominator):
                shifted = tuple(
                    value + Fraction(1, denominator) for value in profile
                )
                for lottery in candidate_lotteries(k):
                    require(
                        formula_worst_regret(profile, lottery)
                        == formula_worst_regret(shifted, lottery),
                        "common-offset invariance failed",
                    )
                    offset_checks += 1
        rows.append(
            {
                "k": k,
                "profiles": k_profiles,
                "interior_profiles": k_interior,
                "boundary_profiles": k_boundary,
            }
        )
    return {
        "denominator": denominator,
        "rows": rows,
        "total_profiles": total_profiles,
        "interior_profiles": interior_profiles,
        "boundary_profiles": boundary_profiles,
        "interior_unique_winner_checks": winner_checks,
        "boundary_minimum_policy_exclusions": boundary_exclusions,
        "regret_formula_vertex_checks": regret_checks,
        "offset_invariance_checks": offset_checks,
    }


def build() -> dict[str, object]:
    stage_zero = verify_stage_zero()
    census = exhaustive_census()
    return {
        "schema": "h238-interior-route-law-nonidentification-v1",
        "status": "pass",
        "classification": (
            "relative_open_within_additive_shared_success_model"
        ),
        "outcome_status": "review_triggered_outcome_exposed_exploratory",
        "protocol_sha256": sha256(PROTOCOL),
        "implementation_sha256": sha256(Path(__file__)),
        "runtime": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
        },
        "propositions": {
            "pair_target_interval": "[o_ij/2,(o_ij+1)/2]",
            "pair_interval_width": "1/2",
            "interior_condition": "max(a)-min(a)<1",
            "interior_consequence": (
                "every policy is a compatible unique target winner via x=e_w"
            ),
            "boundary_consequence": (
                "a minimum-a policy cannot be a compatible unique winner at range 1"
            ),
            "worst_regret": (
                "R(p;a)=[1-p_dot_a+max_w(a_w-p_w)]/4"
            ),
            "constant_profile_reduction": "R(p)=(1-min_i p_i)/4",
            "opponent_reference_cancels": True,
            "common_offset_cancels": True,
        },
        "stage_zero": stage_zero,
        "exhaustive_census": census,
        "scope": (
            "Constant-route, equal-target-weight, two-context exact additive "
            "shared-binary-success "
            "model with exact observed laws. No sampling or empirical transport claim."
        ),
    }


def validate(data: dict[str, object]) -> None:
    require(data == build(), "stored H238 result differs from recomputation")


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=OUTPUT)
    args = parser.parse_args()
    result = build()
    if args.write:
        args.out.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"WROTE {args.out}")
    else:
        validate(json.loads(args.out.read_text(encoding="utf-8")))
        print("OK: H238 interior routed-law result")


if __name__ == "__main__":
    main()
