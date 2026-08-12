#!/usr/bin/env python3
"""Exact H213 audit when zero-reference policies are not selectable."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import subprocess
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from scipy.optimize import linprog

import audit_h212_zero_reference_weight_edge_box_boundary as h212


FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h213-support-constrained-zero-reference-boundary.md"
OUTPUT = FAMILY / "result-h213-support-constrained-zero-reference-boundary.json"
H212_PROTOCOL = FAMILY / "protocol-h212-zero-reference-weight-edge-box-boundary.md"
H212_RESULT = FAMILY / "result-h212-zero-reference-weight-edge-box-boundary.json"
H212_CHALLENGE = (
    FAMILY
    / "result-h212-zero-reference-weight-edge-box-boundary-independent-challenge.json"
)
H212_REVIEW = FAMILY / "review-h212-zero-reference-weight-edge-box-boundary.md"
H212_CODE = FAMILY / "audit_h212_zero_reference_weight_edge_box_boundary.py"
H212_TESTS = FAMILY / "test_audit_h212_zero_reference_weight_edge_box_boundary.py"
FIXED_HASHES = {
    H212_PROTOCOL.name: "2204934e1e4729a0d1dff29b89e544c0da59b654d01a6270655265eda5b61e7c",
    H212_RESULT.name: "60197dc7967bdb388d0707299c6652403e289c2fc58a010d7a121a17b78f839e",
    H212_CHALLENGE.name: "405b0d2fd7805d4d3e6b569635a1e13a5fb942bf4038344feebdc0a42dcd28d1",
    H212_REVIEW.name: "a41a7193a7c3adede901b9e0b4d135c056072d5ed1fb19453720fff056a0774d",
    H212_CODE.name: "81f29991e0ba2cc343af9fe0c614705eed1d401a6076af2c38b1d1915de2f99a",
    H212_TESTS.name: "08eb666e761e22285dd1718515e79d52f735c4fc96076dadbd4438b8d93da2b1",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fraction(value: Fraction) -> dict[str, Any]:
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "text": f"{value.numerator}/{value.denominator}",
        "decimal": float(value),
    }


def validate_support_constraint(
    raw_reference: tuple[Fraction, ...], p: tuple[Fraction, ...]
) -> None:
    r = h212.normalize_nonnegative(raw_reference)
    h212.validate_lottery(p, len(r))
    require(
        all(r[index] > 0 or p[index] == 0 for index in range(len(r))),
        "zero-reference policy received lottery mass",
    )


def constrained_regret(
    raw_reference: tuple[Fraction, ...], p: tuple[Fraction, ...]
) -> Fraction:
    validate_support_constraint(raw_reference, p)
    return h212.reduced_regret(raw_reference, p)


def constrained_solution(
    raw_reference: tuple[Fraction, ...],
) -> dict[str, Any]:
    r = h212.normalize_nonnegative(raw_reference)
    zero_count = sum(value == 0 for value in r)
    if zero_count == 0:
        info = h212.segment_info(raw_reference)
        return {
            "reference": r,
            "value": info["value"],
            "unique": info["h_min"] == info["h_max"],
            "optimizer": None,
            "interior_segment": info,
        }
    return {
        "reference": r,
        "value": Fraction(1, 4),
        "unique": True,
        "optimizer": r,
        "interior_segment": None,
    }


def support_dispersion(
    raw_reference: tuple[Fraction, ...], p: tuple[Fraction, ...]
) -> Fraction:
    r = h212.normalize_nonnegative(raw_reference)
    validate_support_constraint(raw_reference, p)
    support = [index for index, value in enumerate(r) if value > 0]
    return sum(
        abs(r[j] * p[i] - r[i] * p[j])
        for i, j in itertools.combinations(support, 2)
    )


def compositions(total: int, parts: int) -> Iterable[tuple[int, ...]]:
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for tail in compositions(total - first, parts - 1):
            yield (first,) + tail


def support_grid(
    raw_reference: tuple[Fraction, ...], denominator: int
) -> Iterable[tuple[Fraction, ...]]:
    r = h212.normalize_nonnegative(raw_reference)
    support = [index for index, value in enumerate(r) if value > 0]
    for composition in compositions(denominator, len(support)):
        p = [Fraction() for _ in r]
        for index, numerator in zip(support, composition):
            p[index] = Fraction(numerator, denominator)
        yield tuple(p)


def solve_support_lp(
    raw_reference: tuple[Fraction, ...],
    coordinate: int | None = None,
    *,
    maximize: bool = False,
    value_cap: Fraction | None = None,
) -> tuple[float, tuple[float, ...]]:
    r = h212.normalize_nonnegative(raw_reference)
    k = len(r)
    a_ub, b_ub, a_eq, b_eq, bounds = h212.lp_problem(raw_reference)
    bounds = list(bounds)
    for index, value in enumerate(r):
        if value == 0:
            bounds[index] = (0.0, 0.0)
    objective = np.zeros(len(bounds))
    if coordinate is None:
        objective[k] = 1.0
    else:
        require(0 <= coordinate < k, "coordinate outside lottery")
        objective[coordinate] = -1.0 if maximize else 1.0
    if value_cap is not None:
        cap = np.zeros(len(bounds))
        cap[k] = 1.0
        a_ub = np.vstack([a_ub, cap])
        b_ub = np.concatenate([b_ub, [float(value_cap) + 1e-10]])
    solution = linprog(
        objective,
        A_ub=a_ub,
        b_ub=b_ub,
        A_eq=a_eq,
        b_eq=b_eq,
        bounds=bounds,
        method="highs",
    )
    require(solution.status == 0, f"support LP failed with status {solution.status}")
    value = -solution.fun if maximize else solution.fun
    return float(value), tuple(float(item) for item in solution.x[:k])


def stage_validation() -> dict[str, Any]:
    paths = (
        H212_PROTOCOL,
        H212_RESULT,
        H212_CHALLENGE,
        H212_REVIEW,
        H212_CODE,
        H212_TESTS,
    )
    observed = {path.name: sha256(path) for path in paths}
    require(observed == FIXED_HASHES, "fixed H212 input drift")
    subprocess.run(
        [sys.executable, str(H212_CODE), "--check"],
        cwd=FAMILY,
        check=True,
        capture_output=True,
        text=True,
    )

    raw = (Fraction(), Fraction(1), Fraction(2))
    reference = h212.normalize_nonnegative(raw)
    validate_support_constraint(raw, reference)
    try:
        validate_support_constraint(
            raw, (Fraction(1, 10), Fraction(3, 10), Fraction(3, 5))
        )
    except ValueError:
        pass
    else:
        raise ValueError("support constraint failed open")

    controls = (
        (Fraction(), Fraction(), Fraction(1)),
        (Fraction(), Fraction(1), Fraction(1)),
        (Fraction(), Fraction(1), Fraction(2), Fraction(4)),
    )
    for case in controls:
        p = h212.normalize_nonnegative(case)
        require(constrained_regret(case, p) == Fraction(1, 4), "known value")
        require(
            constrained_regret(case, p) == h212.raw_endpoint_regret(case, p),
            "raw endpoint control",
        )
    positive = (Fraction(1), Fraction(2), Fraction(3), Fraction(4))
    info = h212.segment_info(positive)
    require(
        constrained_solution(positive)["value"] == info["value"],
        "positive interior value changed",
    )
    for h in h212.segment_probes(positive):
        p = h212.segment_lottery(positive, h)
        validate_support_constraint(positive, p)

    lp_value, _ = solve_support_lp(raw)
    require(abs(lp_value - 0.25) < 1e-10, "support LP known answer")
    infeasible = linprog(
        np.array([0.0]),
        A_ub=np.array([[1.0], [-1.0]]),
        b_ub=np.array([0.0, -1.0]),
        bounds=[(None, None)],
        method="highs",
    )
    require(infeasible.status == 2, "infeasible LP status")
    unbounded = linprog(np.array([-1.0]), bounds=[(None, None)], method="highs")
    require(unbounded.status == 3, "unbounded LP status")
    require(h212.reconstruct_fraction(0.25) == Fraction(1, 4), "reconstruction")
    try:
        h212.reconstruct_fraction(
            0.123456789, max_denominator=7, tolerance=1e-12
        )
    except ValueError:
        pass
    else:
        raise ValueError("rational reconstruction failed open")
    return {
        "fixed_h212_hashes": observed,
        "h212_exact_rebuild": "pass",
        "support_mask_controls": "pass",
        "raw_endpoint_known_answers": len(controls),
        "positive_interior_parity": "pass",
        "lp_fail_closed_controls": "pass",
    }


def build() -> dict[str, Any]:
    cases = h212.canonical_cases()
    require(len(cases) == 242, "H212 case census changed")
    by_zero_count = Counter()
    by_support = Counter()
    raw_oracles = 0
    permutations = 0
    grid_lotteries = 0
    grid_equalities = 0
    lp_value_error = 0.0
    lp_face_error = 0.0
    limit_rows = 0
    exactly_one_gap_min: Fraction | None = None
    exactly_one_gap_max = Fraction()
    representatives: dict[str, Any] = {}

    for raw in cases:
        r = h212.normalize_nonnegative(raw)
        zero_count = sum(value == 0 for value in r)
        support_size = len(r) - zero_count
        by_zero_count[zero_count] += 1
        by_support[support_size] += 1
        solution = constrained_solution(raw)
        p = solution["optimizer"]
        require(p is not None, "boundary optimizer missing")
        require(p == r, "boundary optimizer is not reference lottery")
        require(constrained_regret(raw, p) == Fraction(1, 4), "boundary value")
        zero = next(index for index, value in enumerate(r) if value == 0)
        objectives = []
        for winner in range(len(r)):
            dispersion = sum(
                abs(r[j] * p[i] - r[i] * p[j])
                for i, j in itertools.combinations(range(len(r)), 2)
                if i != winner and j != winner
            )
            objectives.append(1 - p[winner] + dispersion)
        require(objectives[zero] == 1 + support_dispersion(raw, p), "zero winner")
        require(support_dispersion(raw, p) == 0, "equality dispersion")

        if len(raw) <= 5:
            require(
                h212.raw_endpoint_regret(raw, p) == Fraction(1, 4),
                "raw endpoint oracle",
            )
            raw_oracles += 1

        for permuted in h212.distinct_permutations(raw):
            permuted_r = h212.normalize_nonnegative(permuted)
            require(
                constrained_regret(permuted, permuted_r) == Fraction(1, 4),
                "label dependence",
            )
            permutations += 1

        if len(raw) <= 5:
            for grid_p in support_grid(raw, 8):
                regret = constrained_regret(raw, grid_p)
                require(regret >= Fraction(1, 4), "grid found lower value")
                if regret == Fraction(1, 4):
                    require(grid_p == r, "grid found second optimizer")
                    grid_equalities += 1
                grid_lotteries += 1

        lp_value, _ = solve_support_lp(raw)
        lp_value_error = max(lp_value_error, abs(lp_value - 0.25))
        for coordinate in range(len(raw)):
            observed_min, _ = solve_support_lp(
                raw, coordinate, value_cap=Fraction(1, 4)
            )
            observed_max, _ = solve_support_lp(
                raw, coordinate, maximize=True, value_cap=Fraction(1, 4)
            )
            lp_face_error = max(
                lp_face_error,
                abs(observed_min - float(r[coordinate])),
                abs(observed_max - float(r[coordinate])),
            )
        require(lp_value_error < 2e-8, "LP value disagrees")
        require(lp_face_error < 2e-7, "LP face is not unique")

        h212_info = h212.segment_info(raw)
        if zero_count == 1:
            b = sorted(r)[1]
            gap = Fraction(1, 4) - h212_info["value"]
            require(gap == b / 8 and gap > 0, "exactly-one-zero gap")
            exactly_one_gap_min = (
                gap if exactly_one_gap_min is None else min(exactly_one_gap_min, gap)
            )
            exactly_one_gap_max = max(exactly_one_gap_max, gap)
            positive = tuple(value for value in r if value > 0)
            for epsilon in (
                Fraction(1, 10),
                Fraction(1, 100),
                Fraction(1, 1000),
                Fraction(1, 10000),
            ):
                interior = (epsilon,) + tuple((1 - epsilon) * value for value in positive)
                if epsilon > min(interior[1:]):
                    continue
                interior_value = h212.segment_info(interior)["value"]
                limit_value = (2 - b) / 8
                require(
                    abs(interior_value - limit_value) <= epsilon / 4,
                    "interior limit identity",
                )
                limit_rows += 1
            representatives.setdefault(
                "exactly_one_zero",
                {
                    "reference": [fraction(value) for value in r],
                    "h212_unrestricted_value": fraction(h212_info["value"]),
                    "support_constrained_value": fraction(Fraction(1, 4)),
                    "value_gap": fraction(gap),
                    "support_constrained_optimizer": [fraction(value) for value in p],
                },
            )
        elif zero_count == 2:
            require(h212_info["value"] == Fraction(1, 4), "two-zero value")
            require(h212_info["h_max"] > 0, "two-zero H212 face")
            representatives.setdefault(
                "exactly_two_zeros",
                {
                    "reference": [fraction(value) for value in r],
                    "value": fraction(Fraction(1, 4)),
                    "h212_h_interval": [
                        fraction(h212_info["h_min"]),
                        fraction(h212_info["h_max"]),
                    ],
                    "support_constrained_optimizer": [fraction(value) for value in p],
                },
            )
        else:
            require(h212_info["value"] == Fraction(1, 4), "many-zero value")
            require(h212_info["h_max"] == 0, "many-zero H212 uniqueness")
            representatives.setdefault(
                "at_least_three_zeros",
                {
                    "reference": [fraction(value) for value in r],
                    "value": fraction(Fraction(1, 4)),
                    "support_constrained_optimizer": [fraction(value) for value in p],
                },
            )

    require(raw_oracles == 117, "raw oracle count")
    require(permutations == 14056, "permutation count")
    require(exactly_one_gap_min is not None, "missing exactly-one-zero cases")
    return {
        "schema": "h213-support-constrained-zero-reference-boundary-v1",
        "protocol_sha256": sha256(PROTOCOL),
        "fixed_h212_hashes": FIXED_HASHES,
        "classification": "support_constraint_creates_boundary_value_jump",
        "theorem": {
            "positive_interior": "H188/H212 applies unchanged",
            "any_nonempty_zero_set": {
                "value": "1/4",
                "complete_optimizer": "p=r",
                "unique": True,
            },
            "h212_comparison": {
                "exactly_one_zero": (
                    "value increases by r_(2)/8; no H212 optimizer is "
                    "support-constrained"
                ),
                "exactly_two_zeros": (
                    "value remains 1/4; H212 segment collapses to its h=0 "
                    "endpoint p=r"
                ),
                "at_least_three_zeros": "no value or optimizer change",
            },
        },
        "exact_proof_ledger": [
            {
                "step": "zero_winner",
                "claim": (
                    "For any zero-reference index z and support-constrained p, "
                    "F_z=1+D_r(p)>=1."
                ),
            },
            {
                "step": "attainment",
                "claim": (
                    "p=r is support-constrained, has D_r(p)=0, and makes all "
                    "winner objectives at most one."
                ),
            },
            {
                "step": "uniqueness",
                "claim": (
                    "Equality forces zero support dispersion; on positive "
                    "support this gives p_i=lambda r_i, and the simplex gives "
                    "lambda=1. Support size one is immediate."
                ),
            },
            {
                "step": "one_zero_gap",
                "claim": (
                    "With exactly one zero, H212 has value (2-r_(2))/8, "
                    "so hard support exclusion raises value by r_(2)/8."
                ),
            },
        ],
        "exact_case_census": {
            "canonical_cases": len(cases),
            "by_zero_count": {
                str(key): value for key, value in sorted(by_zero_count.items())
            },
            "by_positive_support_size": {
                str(key): value for key, value in sorted(by_support.items())
            },
            "raw_endpoint_oracle_cases_k_le_5": raw_oracles,
            "distinct_label_permutations": permutations,
            "support_grid_lotteries_k_le_5_denominator_8": grid_lotteries,
            "grid_equalities_at_unique_optimizer": grid_equalities,
            "accepted_exactly_one_zero_limit_rows": limit_rows,
            "exactly_one_zero_gap_range": [
                fraction(exactly_one_gap_min),
                fraction(exactly_one_gap_max),
            ],
        },
        "numerical_face_challenge": {
            "solver": "scipy.optimize.linprog(method='highs')",
            "cases": len(cases),
            "maximum_value_absolute_error": lp_value_error,
            "maximum_unique_face_coordinate_error": lp_face_error,
            "role": "challenge only; exact zero-winner proof is canonical",
        },
        "representative_cases": representatives,
        "scope": (
            "hard p_i=0 whenever r_i=0 constraint only, for the same "
            "weighted-Borda full compatible edge box and ex-ante regret"
        ),
    }


def validate(data: dict[str, Any]) -> None:
    require(
        data.get("schema")
        == "h213-support-constrained-zero-reference-boundary-v1",
        "schema",
    )
    require(data.get("protocol_sha256") == sha256(PROTOCOL), "protocol hash")
    require(data.get("fixed_h212_hashes") == FIXED_HASHES, "H212 binding")
    require(
        data.get("classification")
        == "support_constraint_creates_boundary_value_jump",
        "classification",
    )
    census = data["exact_case_census"]
    require(census["canonical_cases"] == 242, "case count")
    require(census["raw_endpoint_oracle_cases_k_le_5"] == 117, "raw count")
    require(census["distinct_label_permutations"] == 14056, "permutation count")
    require(len(data["exact_proof_ledger"]) == 4, "proof ledger")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    require(
        sum((args.stage, args.write, args.check)) == 1,
        "choose exactly one of --stage/--write/--check",
    )
    if args.stage:
        print(json.dumps(stage_validation(), indent=2, sort_keys=True))
        return
    stage_validation()
    result = build()
    validate(result)
    if args.check:
        require(json.loads(OUTPUT.read_text()) == result, "result drift")
        return
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
