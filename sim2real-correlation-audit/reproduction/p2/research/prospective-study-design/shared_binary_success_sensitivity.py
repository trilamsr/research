#!/usr/bin/env python3
"""Exact H231 shared-binary-success sensitivity calculation."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h231-shared-binary-success-sensitivity.md"
OUTPUT = FAMILY / "result-h231-shared-binary-success-sensitivity.json"
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


def validate_distribution(values: tuple[Fraction, ...], label: str) -> None:
    require(values, f"{label} is empty")
    require(all(value >= 0 for value in values), f"{label} has a negative value")
    require(sum(values) == 1, f"{label} does not sum to one")


def binary_half_tie_score(
    p00: Fraction, p01: Fraction, p10: Fraction, p11: Fraction
) -> Fraction:
    cells = (p00, p01, p10, p11)
    validate_distribution(cells, "binary joint law")
    score = p10 + HALF * (p00 + p11)
    mean_i = p10 + p11
    mean_j = p01 + p11
    require(score == HALF + HALF * (mean_i - mean_j), "binary identity failed")
    return score


def gradient_edges(x: tuple[Fraction, ...]) -> dict[tuple[int, int], Fraction]:
    require(len(x) >= 3, "K must be at least three")
    require(all(0 <= value <= 1 for value in x), "success mean outside [0,1]")
    return {
        (i, j): HALF + QUARTER * (x[i] - x[j])
        for i in range(len(x))
        for j in range(i + 1, len(x))
    }


def policy_values(
    x: tuple[Fraction, ...], reference: tuple[Fraction, ...]
) -> tuple[Fraction, ...]:
    require(len(x) == len(reference), "reference dimension changed")
    validate_distribution(reference, "opponent reference")
    require(all(0 <= value <= 1 for value in x), "success mean outside [0,1]")
    reference_mean = sum(reference[i] * x[i] for i in range(len(x)))
    return tuple(HALF + QUARTER * (value - reference_mean) for value in x)


def regret(
    x: tuple[Fraction, ...],
    policy_lottery: tuple[Fraction, ...],
    reference: tuple[Fraction, ...],
) -> Fraction:
    require(len(x) == len(policy_lottery), "policy-lottery dimension changed")
    validate_distribution(policy_lottery, "policy lottery")
    values = policy_values(x, reference)
    return max(values) - sum(
        policy_lottery[i] * values[i] for i in range(len(values))
    )


def formula_regret(policy_lottery: tuple[Fraction, ...]) -> Fraction:
    validate_distribution(policy_lottery, "policy lottery")
    return QUARTER * (1 - min(policy_lottery))


def enumerated_regret(
    policy_lottery: tuple[Fraction, ...],
    reference: tuple[Fraction, ...],
) -> Fraction:
    require(len(policy_lottery) == len(reference), "reference dimension changed")
    return max(
        regret(
            tuple(Fraction(value) for value in vertex),
            policy_lottery,
            reference,
        )
        for vertex in itertools.product((0, 1), repeat=len(policy_lottery))
    )


def compositions(total: int, parts: int) -> Iterable[tuple[int, ...]]:
    require(total >= 0, "composition total must be nonnegative")
    require(parts >= 1, "grid dimension must be positive")
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for tail in compositions(total - first, parts - 1):
            yield (first,) + tail


def simplex_grid(k: int, denominator: int) -> tuple[tuple[Fraction, ...], ...]:
    require(denominator >= 1, "grid denominator must be positive")
    return tuple(
        tuple(Fraction(value, denominator) for value in row)
        for row in compositions(denominator, k)
    )


def reference_vectors(k: int) -> tuple[tuple[Fraction, ...], ...]:
    triangular = k * (k + 1) // 2
    vectors = [
        tuple(Fraction(1, k) for _ in range(k)),
        tuple(Fraction(i + 1, triangular) for i in range(k)),
        (Fraction(1),) + (Fraction(0),) * (k - 1),
        (Fraction(0),) + tuple(Fraction(1, k - 1) for _ in range(k - 1)),
    ]
    if k >= 4:
        vectors.append(
            (Fraction(0), Fraction(0))
            + tuple(Fraction(1, k - 2) for _ in range(k - 2))
        )
    return tuple(vectors)


def candidate_lotteries(k: int) -> tuple[tuple[Fraction, ...], ...]:
    triangular = k * (k + 1) // 2
    return (
        tuple(Fraction(1, k) for _ in range(k)),
        (Fraction(1),) + (Fraction(0),) * (k - 1),
        (Fraction(1, 2), Fraction(1, 2)) + (Fraction(0),) * (k - 2),
        tuple(Fraction(i + 1, triangular) for i in range(k)),
    )


def winner_set(values: tuple[Fraction, ...]) -> tuple[int, ...]:
    maximum = max(values)
    return tuple(i for i, value in enumerate(values) if value == maximum)


def verify_binary_identity() -> int:
    checked = 0
    denominator = 8
    for counts in compositions(denominator, 4):
        binary_half_tie_score(*(Fraction(value, denominator) for value in counts))
        checked += 1
    return checked


def verify_gradient_cycles(k: int) -> int:
    checked = 0
    for vertex in itertools.product((Fraction(0), Fraction(1)), repeat=k):
        edges = gradient_edges(vertex)
        deltas = {edge: value - HALF for edge, value in edges.items()}
        for i in range(k):
            for j in range(i + 1, k):
                for m in range(j + 1, k):
                    require(
                        deltas[(i, m)] == deltas[(i, j)] + deltas[(j, m)],
                        "gradient cycle identity failed",
                    )
                    checked += 1
    return checked


def verify_known_answers(k: int) -> dict[str, Any]:
    references = reference_vectors(k)
    lotteries = candidate_lotteries(k)
    enumerated = 0
    for reference in references:
        for lottery in lotteries:
            require(
                enumerated_regret(lottery, reference) == formula_regret(lottery),
                "vertex oracle disagrees with formula",
            )
            enumerated += 1

    uniform = lotteries[0]
    singleton = lotteries[1]
    require(
        formula_regret(uniform) == Fraction(k - 1, 4 * k),
        "uniform value changed",
    )
    require(formula_regret(singleton) == QUARTER, "singleton value changed")

    unrestricted_singleton = Fraction(k - 1, 2 * k)
    require(
        unrestricted_singleton - formula_regret(singleton)
        == Fraction(k - 2, 4 * k),
        "unrestricted comparison changed",
    )

    return {
        "k": k,
        "vertex_count": 2**k,
        "reference_count": len(references),
        "lottery_count": len(lotteries),
        "enumerated_reference_lottery_pairs": enumerated,
        "uniform_minimax_regret": fraction(formula_regret(uniform)),
        "deterministic_worst_regret": fraction(formula_regret(singleton)),
        "unrestricted_edge_box_deterministic_regret": fraction(
            unrestricted_singleton
        ),
    }


def verify_simplex_grids() -> dict[str, Any]:
    rows = []
    for k, denominator in ((3, 12), (4, 8), (5, 6), (6, 5)):
        grid = simplex_grid(k, denominator)
        reference = reference_vectors(k)[1]
        values = [enumerated_regret(lottery, reference) for lottery in grid]
        minimum = min(values)
        expected = Fraction(k - 1, 4 * k)
        if denominator % k == 0:
            require(minimum == expected, "grid optimum changed")
            minimizers = [grid[i] for i, value in enumerate(values) if value == minimum]
            require(
                minimizers == [tuple(Fraction(1, k) for _ in range(k))],
                "uniform grid minimizer is not unique",
            )
        else:
            require(minimum > expected, "off-grid optimum unexpectedly attained")
        rows.append(
            {
                "k": k,
                "denominator": denominator,
                "grid_size": len(grid),
                "minimum": fraction(minimum),
                "uniform_on_grid": denominator % k == 0,
            }
        )
    return {"rows": rows, "total_grid_points": sum(row["grid_size"] for row in rows)}


def verify_winner_witnesses() -> int:
    checked = 0
    for k in range(3, 65):
        reference = reference_vectors(k)[0]
        first = (Fraction(1),) + (Fraction(0),) * (k - 1)
        last = (Fraction(0),) * (k - 1) + (Fraction(1),)
        require(winner_set(policy_values(first, reference)) == (0,), "first witness")
        require(winner_set(policy_values(last, reference)) == (k - 1,), "last witness")
        checked += 1
    return checked


def build() -> dict[str, Any]:
    identity_count = verify_binary_identity()
    exact_rows = [verify_known_answers(k) for k in range(3, 9)]
    cycle_checks = sum(verify_gradient_cycles(k) for k in range(3, 7))
    grid = verify_simplex_grids()
    witness_count = verify_winner_witnesses()
    return {
        "schema": "h231-shared-binary-success-sensitivity-v1",
        "status": "pass",
        "classification": "central_result_survives_with_gradient_geometry",
        "protocol_sha256": sha256(PROTOCOL),
        "implementation_sha256": sha256(Path(__file__)),
        "runtime": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
        },
        "model": {
            "contexts": ["A", "B"],
            "target_context_weights": ["1/2", "1/2"],
            "observed_context": "A for every pair",
            "observed_pair_score": "1/2 for every pair",
            "pair_score": "binary success comparison with half credit for ties",
            "context_b_success_means": "x in [0,1]^K",
            "compatible_target_geometry": (
                "q_ij=1/2+(x_i-x_j)/4; "
                "delta_ik=delta_ij+delta_jk"
            ),
        },
        "closed_forms": {
            "policy_value": "V_i=1/2+(x_i-r_dot_x)/4",
            "worst_regret": "R(p)=(1-min_i p_i)/4",
            "deterministic_worst_regret": "1/4",
            "unique_minimax_lottery": "uniform over all K policies",
            "minimax_value": "(K-1)/(4K)",
            "opponent_reference_cancels": True,
        },
        "binary_joint_laws_checked": identity_count,
        "exact_vertex_rows": exact_rows,
        "gradient_cycle_equalities_checked": cycle_checks,
        "simplex_grid": grid,
        "opposite_unique_winner_roster_sizes_checked": witness_count,
        "checked_k_min": 3,
        "checked_k_max": 64,
        "scope": (
            "Exploratory sensitivity for one equal-weight two-context, "
            "all-routes-in-A shared-binary-success construction. It is not "
            "a theorem for every structured response model or robot outcome."
        ),
    }


def validate(data: dict[str, Any]) -> None:
    require(
        data.get("schema") == "h231-shared-binary-success-sensitivity-v1",
        "unexpected schema",
    )
    require(data.get("protocol_sha256") == sha256(PROTOCOL), "protocol changed")
    require(
        data.get("implementation_sha256") == sha256(Path(__file__)),
        "implementation changed",
    )
    require(data.get("status") == "pass", "H231 did not pass")
    require(
        data.get("classification")
        == "central_result_survives_with_gradient_geometry",
        "H231 classification changed",
    )
    require(data.get("binary_joint_laws_checked") == 165, "joint-law census changed")
    require(len(data.get("exact_vertex_rows", [])) == 6, "exact K census changed")
    require(
        data.get("opposite_unique_winner_roster_sizes_checked") == 62,
        "winner-witness census changed",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("choose exactly one of --write or --check")
    if args.write:
        result = build()
        validate(result)
        args.out.write_text(json.dumps(result, indent=2) + "\n")
        print(f"WROTE {args.out}")
    else:
        require(args.out.exists(), f"missing result: {args.out}")
        data = json.loads(args.out.read_text())
        validate(data)
        require(data == build(), "stored H231 result is stale")
        print("OK: H231 shared-binary-success sensitivity")


if __name__ == "__main__":
    main()
