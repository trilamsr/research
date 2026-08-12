#!/usr/bin/env python3
"""Exact H232 comparison of four pairwise-lottery decision objects."""

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
PROTOCOL = FAMILY / "protocol-h232-edge-box-objective-comparison.md"
OUTPUT = FAMILY / "result-h232-edge-box-objective-comparison.json"
HALF = Fraction(1, 2)


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


def validate_lottery(values: tuple[Fraction, ...]) -> None:
    require(len(values) >= 3, "K must be at least three")
    require(all(value >= 0 for value in values), "negative lottery mass")
    require(sum(values) == 1, "lottery does not sum to one")


def pairs(k: int) -> tuple[tuple[int, int], ...]:
    require(k >= 3, "K must be at least three")
    return tuple(itertools.combinations(range(k), 2))


def endpoint_matrices(k: int) -> Iterable[dict[tuple[int, int], Fraction]]:
    edge_order = pairs(k)
    for signs in itertools.product((-1, 1), repeat=len(edge_order)):
        yield {
            edge: Fraction(sign, 2)
            for edge, sign in zip(edge_order, signs)
        }


def margin_entry(
    matrix: dict[tuple[int, int], Fraction], i: int, j: int
) -> Fraction:
    if i == j:
        return Fraction()
    if i < j:
        value = matrix[(i, j)]
    else:
        value = -matrix[(j, i)]
    require(-HALF <= value <= HALF, "margin outside fixed box")
    return value


def min_pure_opponent_margin(
    policy_lottery: tuple[Fraction, ...],
    matrix: dict[tuple[int, int], Fraction],
) -> Fraction:
    validate_lottery(policy_lottery)
    require(set(matrix) == set(pairs(len(policy_lottery))), "matrix support changed")
    column_values = [
        sum(
            policy_lottery[i] * margin_entry(matrix, i, j)
            for i in range(len(policy_lottery))
        )
        for j in range(len(policy_lottery))
    ]
    return min(column_values)


def enumerated_robust_margin(policy_lottery: tuple[Fraction, ...]) -> Fraction:
    return min(
        min_pure_opponent_margin(policy_lottery, matrix)
        for matrix in endpoint_matrices(len(policy_lottery))
    )


def formula_robust_margin(policy_lottery: tuple[Fraction, ...]) -> Fraction:
    validate_lottery(policy_lottery)
    return -HALF * (1 - min(policy_lottery))


def compositions(total: int, parts: int) -> Iterable[tuple[int, ...]]:
    require(total >= 0, "composition total must be nonnegative")
    require(parts >= 1, "composition dimension must be positive")
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


def candidate_lotteries(k: int) -> tuple[tuple[Fraction, ...], ...]:
    total = k * (k + 1) // 2
    return (
        tuple(Fraction(1, k) for _ in range(k)),
        (Fraction(1),) + (Fraction(0),) * (k - 1),
        (Fraction(1, 2), Fraction(1, 2)) + (Fraction(0),) * (k - 2),
        tuple(Fraction(i + 1, total) for i in range(k)),
    )


def zero_matrix(k: int) -> dict[tuple[int, int], Fraction]:
    return {edge: Fraction() for edge in pairs(k)}


def condorcet_completion(k: int, winner: int) -> dict[tuple[int, int], Fraction]:
    require(0 <= winner < k, "winner outside roster")
    matrix = {}
    for i, j in pairs(k):
        if i == winner:
            matrix[(i, j)] = HALF
        elif j == winner:
            matrix[(i, j)] = -HALF
        else:
            matrix[(i, j)] = HALF if (i + j) % 2 == 0 else -HALF
    return matrix


def verify_unique_condorcet_action(
    matrix: dict[tuple[int, int], Fraction], winner: int, k: int
) -> None:
    winner_worst = min(margin_entry(matrix, winner, j) for j in range(k))
    require(winner_worst == 0, "winner maximin value changed")
    for selected in range(k):
        if selected == winner:
            continue
        pure = tuple(Fraction(int(i == selected)) for i in range(k))
        require(
            min_pure_opponent_margin(pure, matrix) < 0,
            "nonwinner pure action reaches maximin value",
        )
    # Any mixed action with mass away from the Condorcet winner loses to it.
    for lottery in candidate_lotteries(k):
        if lottery[winner] < 1:
            column = sum(
                lottery[i] * margin_entry(matrix, i, winner)
                for i in range(k)
            )
            require(column < 0, "mixed nonwinner action reaches maximin value")


def borda_uniform_regret(k: int) -> Fraction:
    require(k >= 3, "K must be at least three")
    # Independent derivation: only K-1 winner-incident edges contribute;
    # each q-edge half-width is 1/4 and normalized Borda divides by K.
    return Fraction(k - 1, 4 * k)


def verify_k(k: int, grid_denominator: int) -> dict[str, Any]:
    candidates = candidate_lotteries(k)
    for lottery in candidates:
        require(
            enumerated_robust_margin(lottery)
            == formula_robust_margin(lottery),
            "endpoint robust-margin oracle disagrees",
        )

    grid = simplex_grid(k, grid_denominator)
    grid_values = []
    for lottery in grid:
        enumerated = enumerated_robust_margin(lottery)
        formula = formula_robust_margin(lottery)
        require(enumerated == formula, "grid endpoint oracle disagrees")
        grid_values.append(formula)
    optimum = max(grid_values)
    minimizers = [grid[i] for i, value in enumerate(grid_values) if value == optimum]
    if grid_denominator % k == 0:
        uniform = tuple(Fraction(1, k) for _ in range(k))
        require(minimizers == [uniform], "uniform grid optimum is not unique")
        require(optimum == Fraction(-(k - 1), 2 * k), "uniform value changed")

    observed = zero_matrix(k)
    require(
        all(
            min_pure_opponent_margin(lottery, observed) == 0
            for lottery in candidates
        ),
        "zero-matrix maximal-lottery set changed",
    )

    for excluded in range(k):
        winner = (excluded + 1) % k
        matrix = condorcet_completion(k, winner)
        verify_unique_condorcet_action(matrix, winner, k)

    return {
        "k": k,
        "edge_count": len(pairs(k)),
        "endpoint_count": 2 ** len(pairs(k)),
        "grid_denominator": grid_denominator,
        "grid_size": len(grid),
        "candidate_lotteries_checked": len(candidates),
        "robust_uniform_margin": fraction(Fraction(-(k - 1), 2 * k)),
        "robust_uniform_worst_win_probability": fraction(Fraction(k + 1, 4 * k)),
        "p2_uniform_borda_regret": fraction(borda_uniform_regret(k)),
        "all_lotteries_maximal_on_observed_zero_matrix": True,
        "every_action_possible_equilibrium_action": True,
        "no_action_necessary_equilibrium_action": True,
    }


def build() -> dict[str, Any]:
    rows = [
        verify_k(3, 12),
        verify_k(4, 8),
        verify_k(5, 5),
    ]
    return {
        "schema": "h232-edge-box-objective-comparison-v1",
        "status": "pass",
        "classification": "same_uniform_action_different_objectives",
        "protocol_sha256": sha256(PROTOCOL),
        "implementation_sha256": sha256(Path(__file__)),
        "runtime": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
        },
        "margin_box": "M_ij in [-1/2,1/2] independently for i<j",
        "closed_forms": {
            "observed_zero_matrix_maximal_lotteries": "entire simplex",
            "possible_equilibrium_actions": "all actions",
            "necessary_equilibrium_actions": "none",
            "robust_margin_for_p": "-(1-min_i p_i)/2",
            "robust_unique_lottery": "uniform",
            "robust_margin_value": "-(K-1)/(2K)",
            "robust_worst_win_probability": "(K+1)/(4K)",
            "p2_borda_regret_unique_lottery": "uniform",
            "p2_borda_regret_value": "(K-1)/(4K)",
        },
        "exact_endpoint_rows": rows,
        "scope": (
            "Review-triggered comparison on P2's symmetric full independent "
            "margin box. Same selected action does not equate the objectives, "
            "losses, values, or interpretations."
        ),
    }


def validate(data: dict[str, Any]) -> None:
    require(
        data.get("schema") == "h232-edge-box-objective-comparison-v1",
        "unexpected schema",
    )
    require(data.get("protocol_sha256") == sha256(PROTOCOL), "protocol changed")
    require(
        data.get("implementation_sha256") == sha256(Path(__file__)),
        "implementation changed",
    )
    require(data.get("status") == "pass", "H232 did not pass")
    require(
        data.get("classification") == "same_uniform_action_different_objectives",
        "classification changed",
    )
    require(len(data.get("exact_endpoint_rows", [])) == 3, "K census changed")


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
        stored = json.loads(args.out.read_text())
        validate(stored)
        require(stored == build(), "stored H232 result is stale")
        print("OK: H232 edge-box objective comparison")


if __name__ == "__main__":
    main()
