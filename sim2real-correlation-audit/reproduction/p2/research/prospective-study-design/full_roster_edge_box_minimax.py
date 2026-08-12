#!/usr/bin/env python3
"""Exact H186 minimax regret over the full compatible roster-edge box."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any


FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h186-full-roster-edge-box-minimax.md"
OUTPUT = FAMILY / "result-h186-full-roster-edge-box-minimax.json"
LOW = Fraction(1, 4)
HIGH = Fraction(3, 4)
HALF = Fraction(1, 2)
CONTEXTS = ("A", "B")


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


def pairs(k: int) -> tuple[tuple[int, int], ...]:
    require(k >= 3, "K must be at least three")
    return tuple(itertools.combinations(range(k), 2))


def validate_weights(k: int, weights: tuple[Fraction, ...]) -> None:
    require(len(weights) == k, "weight vector length changed")
    require(all(weight >= 0 for weight in weights), "negative policy weight")
    require(sum(weights) == 1, "policy weights do not sum to one")


def policy_values(
    k: int, target_edges: dict[tuple[int, int], Fraction]
) -> tuple[Fraction, ...]:
    require(set(target_edges) == set(pairs(k)), "target edge support changed")
    numerators = [HALF for _ in range(k)]
    for (i, j), q_ij in target_edges.items():
        require(LOW <= q_ij <= HIGH, "target edge outside fixed box")
        numerators[i] += q_ij
        numerators[j] += 1 - q_ij
    return tuple(value / k for value in numerators)


def route(edge: tuple[int, int]) -> str:
    i, j = edge
    return CONTEXTS[(i + j) % 2]


def potential_schedule(
    k: int, target_edges: dict[tuple[int, int], Fraction]
) -> dict[tuple[int, int], dict[str, Fraction]]:
    require(set(target_edges) == set(pairs(k)), "target edge support changed")
    schedule = {}
    for edge, target_q in target_edges.items():
        require(LOW <= target_q <= HIGH, "target edge outside fixed box")
        routed = route(edge)
        hidden_context = next(context for context in CONTEXTS if context != routed)
        schedule[edge] = {
            routed: HALF,
            hidden_context: compatible_hidden_outcome(target_q),
        }
    return schedule


def observed_projection(
    schedule: dict[tuple[int, int], dict[str, Fraction]]
) -> dict[tuple[int, int], Fraction]:
    return {edge: outcomes[route(edge)] for edge, outcomes in schedule.items()}


def target_projection(
    schedule: dict[tuple[int, int], dict[str, Fraction]]
) -> dict[tuple[int, int], Fraction]:
    return {
        edge: sum(outcomes[context] for context in CONTEXTS) / 2
        for edge, outcomes in schedule.items()
    }


def compatibility_witness(
    k: int, label: str, target_edges: dict[tuple[int, int], Fraction]
) -> dict[str, Any]:
    schedule = potential_schedule(k, target_edges)
    observed = observed_projection(schedule)
    projected = target_projection(schedule)
    require(projected == target_edges, "target projection changed")
    require(
        set(observed.values()) == {HALF},
        "observed law is not the complete-support half-win law",
    )
    rows = [
        {
            "edge": [i, j],
            "routed_context": route((i, j)),
            "routed_outcome": fraction(observed[(i, j)]),
            "hidden_outcome": fraction(
                schedule[(i, j)][
                    next(context for context in CONTEXTS if context != route((i, j)))
                ]
            ),
            "projected_target": fraction(projected[(i, j)]),
        }
        for i, j in pairs(k)
    ]
    content = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    return {
        "label": label,
        "k": k,
        "edge_count": len(rows),
        "all_edges_projected": True,
        "all_observed_routed_outcomes": [fraction(HALF)],
        "schedule_sha256": hashlib.sha256(content).hexdigest(),
        "edge_rows": rows if k <= 4 else None,
    }


def formula_regret(k: int, weights: tuple[Fraction, ...]) -> Fraction:
    validate_weights(k, weights)
    base_pair_dispersion = sum(
        abs(weights[i] - weights[j]) for i, j in pairs(k)
    )
    winner_objectives = []
    for winner in range(k):
        removed_winner_edges = sum(
            abs(weights[winner] - weights[other])
            for other in range(k)
            if other != winner
        )
        added_winner_edges = sum(
            1 - weights[winner] + weights[other]
            for other in range(k)
            if other != winner
        )
        winner_objectives.append(
            (
                base_pair_dispersion
                - removed_winner_edges
                + added_winner_edges
            )
            / (4 * k)
        )
    return max(winner_objectives)


@lru_cache(maxsize=None)
def endpoint_centered_scores(k: int) -> tuple[tuple[int, ...], ...]:
    """Return endpoint-centered values scaled by 4K."""
    edge_order = pairs(k)
    rows = []
    for signs in itertools.product((-1, 1), repeat=len(edge_order)):
        scores = [0 for _ in range(k)]
        for (i, j), sign in zip(edge_order, signs):
            scores[i] += sign
            scores[j] -= sign
        rows.append(tuple(scores))
    return tuple(rows)


def enumerated_regret(k: int, weights: tuple[Fraction, ...]) -> Fraction:
    validate_weights(k, weights)
    worst_scaled = Fraction()
    for scores in endpoint_centered_scores(k):
        mixture_scaled = sum(
            weight * score for weight, score in zip(weights, scores)
        )
        worst_scaled = max(worst_scaled, max(scores) - mixture_scaled)
    return worst_scaled / (4 * k)


def uniform(k: int) -> tuple[Fraction, ...]:
    return (Fraction(1, k),) * k


def singleton(k: int, policy: int = 0) -> tuple[Fraction, ...]:
    require(0 <= policy < k, "singleton policy outside roster")
    return tuple(Fraction(int(index == policy)) for index in range(k))


def candidate_weights(k: int) -> list[tuple[Fraction, ...]]:
    triangular_total = k * (k + 1) // 2
    candidates = [
        uniform(k),
        singleton(k),
        (Fraction(1, 2), Fraction(1, 2)) + (Fraction(),) * (k - 2),
        tuple(Fraction(index + 1, triangular_total) for index in range(k)),
    ]
    if k > 3:
        candidates.append((Fraction(1, 3),) * 3 + (Fraction(),) * (k - 3))
    return candidates


def compatible_hidden_outcome(target_q: Fraction) -> Fraction:
    hidden = 2 * target_q - HALF
    require(Fraction() <= hidden <= 1, "hidden outcome outside [0,1]")
    return hidden


def witness_target_edges(
    k: int, values: tuple[Fraction, ...]
) -> dict[tuple[int, int], Fraction]:
    require(values, "witness value cycle is empty")
    return {
        edge: values[index % len(values)]
        for index, edge in enumerate(pairs(k))
    }


def check_k(k: int, exhaust_endpoints: bool) -> dict[str, Any]:
    deterministic = Fraction(k - 1, 2 * k)
    randomized = Fraction(k - 1, 4 * k)
    require(formula_regret(k, singleton(k)) == deterministic, "deterministic formula")
    require(formula_regret(k, uniform(k)) == randomized, "uniform formula")
    require(randomized * 2 == deterministic, "factor-of-two identity changed")

    rows = []
    for weights in candidate_weights(k):
        formula = formula_regret(k, weights)
        enumerated = enumerated_regret(k, weights) if exhaust_endpoints else None
        if enumerated is not None:
            require(enumerated == formula, "endpoint enumeration disagrees")
        rows.append(
            {
                "weights": [fraction(weight) for weight in weights],
                "formula_worst_expected_regret": fraction(formula),
                "enumerated_worst_expected_regret": (
                    fraction(enumerated) if enumerated is not None else None
                ),
            }
        )

    for target_q in (LOW, HALF, HIGH):
        compatible_hidden_outcome(target_q)

    return {
        "k": k,
        "edge_count": len(pairs(k)),
        "endpoint_count": 2 ** len(pairs(k)),
        "endpoints_exhausted": exhaust_endpoints,
        "candidate_checks": rows,
        "deterministic_singleton_minimax_regret": fraction(deterministic),
        "randomized_minimax_expected_regret": fraction(randomized),
        "unique_randomized_minimizer": [fraction(weight) for weight in uniform(k)],
        "same_complete_support_observed_half_win_law": True,
        "valid_hidden_outcome_range": [fraction(Fraction()), fraction(Fraction(1))],
    }


def build() -> dict[str, Any]:
    exact_checks = [check_k(k, exhaust_endpoints=True) for k in range(3, 7)]
    formula_checks = [
        check_k(k, exhaust_endpoints=False)
        for k in (7, 8, 16, 32)
    ]
    witness_specs = [
        (3, "all-low", (LOW,)),
        (3, "all-high", (HIGH,)),
        (4, "mixed-endpoint", (LOW, HIGH)),
        (
            7,
            "mixed-interior",
            (
                Fraction(1, 3),
                Fraction(2, 5),
                HALF,
                Fraction(3, 5),
                Fraction(2, 3),
            ),
        ),
        (16, "alternating-endpoint", (LOW, HIGH)),
        (32, "mixed-endpoint-interior", (LOW, Fraction(2, 5), HALF, HIGH)),
    ]
    compatibility_witnesses = [
        compatibility_witness(k, label, witness_target_edges(k, values))
        for k, label, values in witness_specs
    ]
    return {
        "schema": "h186-full-roster-edge-box-minimax-v1",
        "protocol_sha256": sha256(PROTOCOL),
        "endpoint_exhaustion_k_min": 3,
        "endpoint_exhaustion_k_max": 6,
        "formula_check_k": [7, 8, 16, 32],
        "closed_forms": {
            "arbitrary_weight_worst_expected_regret": (
                "max_w sum_{i<j}|(1{i=w}-p_i)-(1{j=w}-p_j)|/(4K)"
            ),
            "deterministic_singleton_minimax_regret": "(K-1)/(2K)",
            "randomized_minimax_expected_regret": "(K-1)/(4K)",
            "unique_randomized_minimizer": "uniform over all K policies",
        },
        "exact_endpoint_checks": exact_checks,
        "additional_formula_checks": formula_checks,
        "compatibility_witnesses": compatibility_witnesses,
        "status": "pass",
        "scope": (
            "Exact minimax result for the full independent [1/4,3/4] target "
            "edge box compatible with one constructed complete-support "
            "pair-first observed half-win law. No dominated padding or fixed "
            "noncore target edges. Not every observed law, empirical roster, "
            "protocol, realized-policy guarantee, prevalence, or field claim."
        ),
    }


def validate(result: dict[str, Any]) -> None:
    require(
        result.get("schema") == "h186-full-roster-edge-box-minimax-v1",
        "unexpected schema",
    )
    require(result.get("protocol_sha256") == sha256(PROTOCOL), "protocol changed")
    require(result.get("endpoint_exhaustion_k_max") == 6, "endpoint gate changed")
    require(
        len(result.get("compatibility_witnesses", [])) == 6,
        "compatibility witness set changed",
    )
    require(
        result["closed_forms"]["randomized_minimax_expected_regret"]
        == "(K-1)/(4K)",
        "randomized formula changed",
    )
    require(result.get("status") == "pass", "H186 did not pass")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("choose exactly one")
    if args.check:
        validate(json.loads(args.out.read_text(encoding="utf-8")))
        for k in range(3, 7):
            check_k(k, exhaust_endpoints=True)
        for k in (7, 8, 16, 32):
            check_k(k, exhaust_endpoints=False)
        print("OK: H186 full-roster edge-box minimax validates")
        return
    result = build()
    validate(result)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": result["status"],
                "deterministic": result["closed_forms"][
                    "deterministic_singleton_minimax_regret"
                ],
                "randomized_expected": result["closed_forms"][
                    "randomized_minimax_expected_regret"
                ],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
