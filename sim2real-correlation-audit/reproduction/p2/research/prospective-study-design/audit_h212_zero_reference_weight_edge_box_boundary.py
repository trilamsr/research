#!/usr/bin/env python3
"""Exact H212 audit of the H188 theorem on the closed reference simplex."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
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


FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h212-zero-reference-weight-edge-box-boundary.md"
OUTPUT = FAMILY / "result-h212-zero-reference-weight-edge-box-boundary.json"
H188_PROTOCOL = FAMILY / "protocol-h188-weighted-edge-box-minimax.md"
H188_RESULT = FAMILY / "result-h188-weighted-edge-box-minimax.json"
H188_REVIEW = FAMILY / "review-h188-weighted-edge-box-minimax.md"
H188_CODE = FAMILY / "weighted_edge_box_minimax.py"
H188_TESTS = FAMILY / "test_weighted_edge_box_minimax.py"

FIXED_HASHES = {
    H188_PROTOCOL.name: "0391adc2b80152b136bee5b470f2b4f3bfbec64b39b811af54d6ff65a1bd459e",
    H188_RESULT.name: "e5721a0918c8f97f1a076b6d00b9a9f9e323261f71d9e6093b1cec307709800a",
    H188_REVIEW.name: "14323db710ef389de390bfee220eb87379468eda1cce14b1545b566687be67eb",
    H188_CODE.name: "4ce70305dcba09d317880bbedd134d762c7018915d7405469953cf8cfb1a766f",
    H188_TESTS.name: "383d16e41cf833822791233ad854d3c03f91459e44d482a3dacb3d9613697ddb",
}
HALF = Fraction(1, 2)
QUARTER = Fraction(1, 4)


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


def normalize_nonnegative(
    raw: tuple[Fraction, ...],
) -> tuple[Fraction, ...]:
    require(len(raw) >= 3, "at least three policies required")
    require(all(value >= 0 for value in raw), "reference weights must be nonnegative")
    total = sum(raw)
    require(total > 0, "reference weights cannot all be zero")
    return tuple(value / total for value in raw)


def validate_lottery(p: tuple[Fraction, ...], k: int) -> None:
    require(len(p) == k, "lottery length changed")
    require(all(value >= 0 for value in p), "negative lottery mass")
    require(sum(p) == 1, "lottery does not sum to one")


def reduced_regret(
    raw_reference: tuple[Fraction, ...], p: tuple[Fraction, ...]
) -> Fraction:
    r = normalize_nonnegative(raw_reference)
    validate_lottery(p, len(r))
    objectives = []
    for winner in range(len(r)):
        dispersion = sum(
            abs(r[j] * p[i] - r[i] * p[j])
            for i, j in itertools.combinations(range(len(r)), 2)
            if i != winner and j != winner
        )
        objectives.append(1 - p[winner] + dispersion)
    return max(objectives) / 4


def endpoint_policy_values(
    r: tuple[Fraction, ...], signs: tuple[int, ...]
) -> tuple[Fraction, ...]:
    k = len(r)
    edges = tuple(itertools.combinations(range(k), 2))
    require(len(signs) == len(edges), "endpoint sign count changed")
    q = [[HALF for _ in range(k)] for _ in range(k)]
    for (i, j), sign in zip(edges, signs):
        q[i][j] = HALF + sign * QUARTER
        q[j][i] = 1 - q[i][j]
    return tuple(sum(r[j] * q[i][j] for j in range(k)) for i in range(k))


def raw_endpoint_regret(
    raw_reference: tuple[Fraction, ...], p: tuple[Fraction, ...]
) -> Fraction:
    r = normalize_nonnegative(raw_reference)
    validate_lottery(p, len(r))
    edges = tuple(itertools.combinations(range(len(r)), 2))
    worst = Fraction()
    for signs in itertools.product((-1, 1), repeat=len(edges)):
        values = endpoint_policy_values(r, signs)
        regret = max(values) - sum(prob * value for prob, value in zip(p, values))
        worst = max(worst, regret)
    return worst


def segment_info(raw_reference: tuple[Fraction, ...]) -> dict[str, Any]:
    r = normalize_nonnegative(raw_reference)
    order = sorted(range(len(r)), key=lambda index: (r[index], index))
    first, second, third = order[:3]
    a, b, g = r[first], r[second], r[third]
    return {
        "reference": r,
        "order": tuple(order),
        "first": first,
        "second": second,
        "third": third,
        "a": a,
        "b": b,
        "g": g,
        "h_min": Fraction(),
        "h_max": (g - b) / 2,
        "value": (2 - a - b) / 8,
    }


def segment_lottery(
    raw_reference: tuple[Fraction, ...], h: Fraction
) -> tuple[Fraction, ...]:
    info = segment_info(raw_reference)
    require(info["h_min"] <= h <= info["h_max"], "h outside minimizer segment")
    r = info["reference"]
    first, second = info["first"], info["second"]
    a, b = info["a"], info["b"]
    complement = 1 - a - b
    require(complement > 0, "two smallest weights exhaust the simplex")
    p = [Fraction() for _ in r]
    p[first] = (a + b) / 2 + h
    p[second] = b * (2 - a - b) / (2 * (1 - a))
    p[second] += (1 - b) * h / (1 - a)
    multiplier = (2 - a - b) / (1 - a) * (HALF - h / complement)
    for index in range(len(r)):
        if index not in (first, second):
            p[index] = r[index] * multiplier
    result = tuple(p)
    validate_lottery(result, len(r))
    return result


def canonical_cases() -> tuple[tuple[Fraction, ...], ...]:
    rows: list[tuple[Fraction, ...]] = []
    for k in range(3, 7):
        for support_size in range(1, k):
            zero_count = k - support_size
            for positive in itertools.combinations_with_replacement(
                (Fraction(1), Fraction(2), Fraction(3), Fraction(4)),
                support_size,
            ):
                rows.append((Fraction(),) * zero_count + positive)
    return tuple(rows)


def distinct_permutations(values: tuple[Fraction, ...]) -> Iterable[tuple[Fraction, ...]]:
    return set(itertools.permutations(values))


def permute_vector(
    vector: tuple[Fraction, ...], permutation: tuple[int, ...]
) -> tuple[Fraction, ...]:
    return tuple(vector[index] for index in permutation)


def segment_probes(raw: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    info = segment_info(raw)
    return tuple(
        sorted(
            {
                info["h_min"],
                (info["h_min"] + info["h_max"]) / 2,
                info["h_max"],
            }
        )
    )


def reconstruct_fraction(
    value: float, *, max_denominator: int = 10000, tolerance: float = 1e-10
) -> Fraction:
    candidate = Fraction(value).limit_denominator(max_denominator)
    require(
        abs(float(candidate) - value) <= tolerance,
        "floating value has no accepted rational reconstruction",
    )
    return candidate


def deduplicate_vectors(
    vectors: Iterable[tuple[Fraction, ...]],
) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(sorted(set(vectors)))


def lp_problem(
    raw_reference: tuple[Fraction, ...],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, list[tuple[float, None]]]:
    r = normalize_nonnegative(raw_reference)
    k = len(r)
    tail_edges = {
        winner: tuple(
            (i, j)
            for i, j in itertools.combinations(range(k), 2)
            if i != winner and j != winner
        )
        for winner in range(k)
    }
    z_keys = tuple(
        (winner, i, j)
        for winner in range(k)
        for i, j in tail_edges[winner]
    )
    z_index = {key: k + 1 + offset for offset, key in enumerate(z_keys)}
    n_vars = k + 1 + len(z_keys)
    t_index = k
    a_ub: list[list[float]] = []
    b_ub: list[float] = []
    for winner in range(k):
        row = [0.0] * n_vars
        row[winner] = -1.0
        row[t_index] = -4.0
        for i, j in tail_edges[winner]:
            row[z_index[(winner, i, j)]] = 1.0
        a_ub.append(row)
        b_ub.append(-1.0)
        for i, j in tail_edges[winner]:
            z = z_index[(winner, i, j)]
            positive = [0.0] * n_vars
            positive[i] = float(r[j])
            positive[j] = -float(r[i])
            positive[z] = -1.0
            a_ub.append(positive)
            b_ub.append(0.0)
            negative = [-value for value in positive]
            negative[z] = -1.0
            a_ub.append(negative)
            b_ub.append(0.0)
    a_eq = np.zeros((1, n_vars))
    a_eq[0, :k] = 1.0
    b_eq = np.array([1.0])
    return (
        np.asarray(a_ub),
        np.asarray(b_ub),
        a_eq,
        b_eq,
        [(0.0, None)] * n_vars,
    )


def solve_lp(
    raw_reference: tuple[Fraction, ...],
    direction: tuple[Fraction, ...] | None = None,
    *,
    maximize: bool = False,
    value_cap: Fraction | None = None,
) -> tuple[float, tuple[float, ...]]:
    r = normalize_nonnegative(raw_reference)
    k = len(r)
    a_ub, b_ub, a_eq, b_eq, bounds = lp_problem(raw_reference)
    n_vars = len(bounds)
    objective = np.zeros(n_vars)
    if direction is None:
        objective[k] = 1.0
    else:
        require(len(direction) == k, "LP direction length changed")
        objective[:k] = np.asarray([float(value) for value in direction])
        if maximize:
            objective *= -1
    if value_cap is not None:
        cap = np.zeros(n_vars)
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
    require(solution.status == 0, f"LP failed with status {solution.status}")
    value = -solution.fun if maximize else solution.fun
    return float(value), tuple(float(item) for item in solution.x[:k])


def exact_direction_range(
    raw: tuple[Fraction, ...], direction: tuple[Fraction, ...]
) -> tuple[Fraction, Fraction]:
    info = segment_info(raw)
    endpoints = (
        segment_lottery(raw, info["h_min"]),
        segment_lottery(raw, info["h_max"]),
    )
    values = tuple(
        sum(coefficient * probability for coefficient, probability in zip(direction, p))
        for p in endpoints
    )
    return min(values), max(values)


def stage_validation() -> dict[str, Any]:
    observed_hashes = {
        path.name: sha256(path)
        for path in (H188_PROTOCOL, H188_RESULT, H188_REVIEW, H188_CODE, H188_TESTS)
    }
    require(observed_hashes == FIXED_HASHES, "fixed H188 input drift")
    subprocess.run(
        [sys.executable, str(H188_CODE), "--check"],
        cwd=FAMILY,
        check=True,
        capture_output=True,
        text=True,
    )

    for bad in (
        (Fraction(1), Fraction(2)),
        (Fraction(-1), Fraction(1), Fraction(1)),
        (Fraction(), Fraction(), Fraction()),
    ):
        try:
            normalize_nonnegative(bad)
        except ValueError:
            pass
        else:
            raise ValueError("nonnegative normalization failed closed")
    require(
        normalize_nonnegative((Fraction(), Fraction(2), Fraction(2)))
        == (Fraction(), Fraction(1, 2), Fraction(1, 2)),
        "zero-weight normalization known answer",
    )

    controls = (
        ((Fraction(1), Fraction(1), Fraction(1)), (Fraction(1, 3),) * 3),
        ((Fraction(), Fraction(), Fraction(1)), (Fraction(), Fraction(), Fraction(1))),
        ((Fraction(), Fraction(1), Fraction(1)), (Fraction(), Fraction(1, 2), Fraction(1, 2))),
    )
    for raw, p in controls:
        require(reduced_regret(raw, p) == raw_endpoint_regret(raw, p), "raw control")
    require(
        reduced_regret(
            (Fraction(), Fraction(), Fraction(1)),
            (Fraction(1), Fraction(), Fraction()),
        )
        == Fraction(1, 2),
        "singleton-lottery control changed",
    )

    spec = importlib.util.spec_from_file_location("h188_fixed", H188_CODE)
    require(spec is not None and spec.loader is not None, "cannot load fixed H188")
    h188 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h188)
    for raw in h188.cases():
        ours = segment_info(raw)
        theirs = h188.minimax_segment(raw)
        require(ours["value"] == theirs["value"], "positive H188 value changed")
        require(ours["h_max"] == theirs["h_max"], "positive H188 face changed")
        for h in segment_probes(raw):
            require(
                segment_lottery(raw, h) == h188.segment_lottery(raw, h),
                "positive H188 optimizer changed",
            )

    feasible, _ = solve_lp((Fraction(1), Fraction(1), Fraction(1)))
    require(abs(feasible - 1 / 6) < 1e-10, "LP known answer changed")
    infeasible = linprog(
        np.array([0.0]),
        A_ub=np.array([[1.0], [-1.0]]),
        b_ub=np.array([0.0, -1.0]),
        bounds=[(None, None)],
        method="highs",
    )
    require(infeasible.status == 2, "LP infeasible status not detected")
    unbounded = linprog(
        np.array([-1.0]), bounds=[(None, None)], method="highs"
    )
    require(unbounded.status == 3, "LP unbounded status not detected")
    require(reconstruct_fraction(1 / 3) == Fraction(1, 3), "rational reconstruction")
    try:
        reconstruct_fraction(0.123456789, max_denominator=7, tolerance=1e-12)
    except ValueError:
        pass
    else:
        raise ValueError("rational reconstruction failed open")
    require(
        deduplicate_vectors(
            (
                (Fraction(), Fraction(1)),
                (Fraction(), Fraction(1)),
                (Fraction(1), Fraction()),
            )
        )
        == ((Fraction(), Fraction(1)), (Fraction(1), Fraction())),
        "exact duplicate-vector control",
    )
    return {
        "fixed_h188_hashes": observed_hashes,
        "h188_exact_rebuild": "pass",
        "nonnegative_normalization_controls": "pass",
        "raw_endpoint_known_answers": len(controls),
        "positive_h188_cases_reproduced": len(h188.cases()),
        "lp_fail_closed_controls": {
            "known_answer": "pass",
            "infeasible": "pass",
            "unbounded": "pass",
            "rational_reconstruction": "pass",
            "duplicate_vectors": "pass",
        },
    }


def build() -> dict[str, Any]:
    cases = canonical_cases()
    count_by_k = Counter(len(raw) for raw in cases)
    count_by_support = Counter(sum(value > 0 for value in raw) for raw in cases)
    raw_oracle_probes = 0
    permutation_checks = 0
    segment_probes_checked = 0
    lp_value_error = 0.0
    lp_face_error = 0.0
    limit_checks = 0
    final_limit_error = Fraction()
    representatives: list[dict[str, Any]] = []

    for raw in cases:
        info = segment_info(raw)
        probes = segment_probes(raw)
        for h in probes:
            p = segment_lottery(raw, h)
            require(reduced_regret(raw, p) == info["value"], "segment value changed")
            segment_probes_checked += 1
            if len(raw) <= 5:
                require(
                    raw_endpoint_regret(raw, p) == info["value"],
                    "raw endpoint oracle disagrees",
                )
                raw_oracle_probes += 1

        reference = normalize_nonnegative(raw)
        for permuted in distinct_permutations(raw):
            perm_info = segment_info(permuted)
            require(perm_info["value"] == info["value"], "value label dependence")
            for h in segment_probes(permuted):
                require(
                    reduced_regret(permuted, segment_lottery(permuted, h))
                    == info["value"],
                    "optimizer label dependence",
                )
            require(
                tuple(sorted(perm_info["reference"])) == tuple(sorted(reference)),
                "reference orbit changed",
            )
            permutation_checks += 1

        lp_value, _ = solve_lp(raw)
        lp_value_error = max(lp_value_error, abs(lp_value - float(info["value"])))
        require(lp_value_error < 2e-8, "LP value disagrees with exact theorem")
        directions = [
            tuple(Fraction(index == coordinate) for index in range(len(raw)))
            for coordinate in range(len(raw))
        ]
        directions.extend(
            (
                tuple(Fraction(index + 1) for index in range(len(raw))),
                tuple(Fraction((-1) ** index * (index + 1)) for index in range(len(raw))),
                tuple(Fraction((index + 1) ** 2) for index in range(len(raw))),
            )
        )
        for direction in directions:
            exact_min, exact_max = exact_direction_range(raw, direction)
            observed_min, _ = solve_lp(raw, direction, value_cap=info["value"])
            observed_max, _ = solve_lp(
                raw, direction, maximize=True, value_cap=info["value"]
            )
            lp_face_error = max(
                lp_face_error,
                abs(observed_min - float(exact_min)),
                abs(observed_max - float(exact_max)),
            )
        require(lp_face_error < 2e-7, "LP face direction escapes exact segment")

        zero_count = sum(value == 0 for value in raw)
        for denominator in (10, 100, 1000):
            epsilon = Fraction(1, denominator)
            interior = tuple(epsilon if value == 0 else value for value in raw)
            boundary_endpoints = (
                segment_lottery(raw, info["h_min"]),
                segment_lottery(raw, info["h_max"]),
            )
            interior_info = segment_info(interior)
            interior_endpoints = (
                segment_lottery(interior, interior_info["h_min"]),
                segment_lottery(interior, interior_info["h_max"]),
            )
            error = max(
                sum(abs(left - right) for left, right in zip(boundary, positive))
                for boundary, positive in zip(boundary_endpoints, interior_endpoints)
            )
            if denominator == 1000:
                final_limit_error = max(final_limit_error, error)
            limit_checks += 1
        if len(representatives) < 8 and (
            len(raw), sum(value > 0 for value in raw)
        ) in {
            (3, 1),
            (3, 2),
            (4, 1),
            (4, 2),
            (4, 3),
            (5, 2),
            (5, 4),
            (6, 5),
        }:
            p_min = segment_lottery(raw, info["h_min"])
            p_max = segment_lottery(raw, info["h_max"])
            representatives.append(
                {
                    "reference": [fraction(value) for value in reference],
                    "support_size": sum(value > 0 for value in raw),
                    "value": fraction(info["value"]),
                    "h_interval": [
                        fraction(info["h_min"]),
                        fraction(info["h_max"]),
                    ],
                    "unique": info["h_min"] == info["h_max"],
                    "endpoint_lotteries": [
                        [fraction(value) for value in p_min],
                        [fraction(value) for value in p_max],
                    ],
                }
            )

    require(len(cases) == 242, "case census count changed")
    require(raw_oracle_probes == 247, "raw endpoint probe count changed")
    require(final_limit_error <= Fraction(1, 50), "positive-limit convergence too slow")
    classification = "value_and_optimizer_extend_without_change"
    return {
        "schema": "h212-zero-reference-weight-edge-box-boundary-v1",
        "protocol_sha256": sha256(PROTOCOL),
        "fixed_h188_hashes": FIXED_HASHES,
        "classification": classification,
        "closed_simplex_theorem": {
            "reference_domain": "r_i >= 0, sum_i r_i = 1, K >= 3",
            "value": "(2-r_(1)-r_(2))/8",
            "complete_minimizer_set": "the same closed h-segment as H188",
            "h_interval": "0 <= h <= (r_(3)-r_(2))/2",
            "uniqueness_condition": "r_(2)=r_(3)",
            "zero_support_consequences": {
                "exactly_two_zero_weights": (
                    "the two zero-reference policies receive equal h mass; "
                    "0 <= h <= min_positive_weight/2"
                ),
                "at_least_three_zero_weights": (
                    "h=0 and the unique optimizer is p=r"
                ),
                "one_zero_weight": "the H188 segment applies without a new face",
            },
        },
        "exact_case_census": {
            "canonical_cases": len(cases),
            "by_k": {str(key): value for key, value in sorted(count_by_k.items())},
            "by_positive_support_size": {
                str(key): value for key, value in sorted(count_by_support.items())
            },
            "segment_probes": segment_probes_checked,
            "raw_endpoint_oracle_probes_k_le_5": raw_oracle_probes,
            "distinct_label_permutations": permutation_checks,
            "positive_limit_checks": limit_checks,
            "largest_l1_endpoint_error_at_raw_epsilon_1_over_1000": fraction(
                final_limit_error
            ),
        },
        "numerical_face_challenge": {
            "solver": "scipy.optimize.linprog(method='highs')",
            "cases": len(cases),
            "directions_per_case": "K coordinate directions plus three fixed contrasts",
            "maximum_value_absolute_error": lp_value_error,
            "maximum_face_support_absolute_error": lp_face_error,
            "role": "candidate-face challenge only; exact proof is canonical",
        },
        "exact_proof_ledger": [
            {
                "step": "lower_bound",
                "claim": (
                    "For indices of the two smallest weights a,b, "
                    "F_1+F_2 >= 2-p_1-p_2+|p_1+p_2-a-b| >= 2-a-b."
                ),
            },
            {
                "step": "equality_tail",
                "claim": (
                    "Equality makes all tail cross-products r_j p_i-r_i p_j "
                    "zero. Because the tail contains positive total weight, "
                    "p_i=lambda r_i for every tail index, including p_i=0 "
                    "at any zero-weight tail index."
                ),
            },
            {
                "step": "solve_equalizers",
                "claim": (
                    "F_1=F_2=(2-a-b)/2 gives exactly H188's h-parameterized "
                    "lottery; all denominators remain positive on the closed "
                    "simplex for K>=3."
                ),
            },
            {
                "step": "complete_face",
                "claim": (
                    "For each tail j, F_j-(2-a-b)/2=2h-(r_j-b); therefore "
                    "all winner constraints hold exactly for "
                    "0<=h<=(r_(3)-r_(2))/2, with no additional optimizer."
                ),
            },
        ],
        "representative_boundary_cases": representatives,
        "scope": (
            "one weighted-Borda full compatible edge box and ex-ante expected "
            "regret; no empirical reference choice, outcome use, or extension "
            "to other target laws"
        ),
    }


def validate(data: dict[str, Any]) -> None:
    require(
        data.get("schema") == "h212-zero-reference-weight-edge-box-boundary-v1",
        "schema",
    )
    require(data.get("protocol_sha256") == sha256(PROTOCOL), "protocol hash")
    require(data.get("fixed_h188_hashes") == FIXED_HASHES, "H188 hash binding")
    require(
        data.get("classification") == "value_and_optimizer_extend_without_change",
        "classification",
    )
    census = data["exact_case_census"]
    require(census["canonical_cases"] == 242, "case count")
    require(census["raw_endpoint_oracle_probes_k_le_5"] == 247, "raw oracle count")
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
