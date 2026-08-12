#!/usr/bin/env python3
"""Exact H183 arbitrary-roster embedding of the H151 counterexample."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h183-arbitrary-roster-pair-first-identification.md"
OUTPUT = FAMILY / "result-h183-arbitrary-roster-pair-first-identification.json"
CORE = (0, 1, 2)
LOW = Fraction(1, 4)
HALF = Fraction(1, 2)
HIGH = Fraction(3, 4)
CORE_ROUTES = {(0, 1): "A", (0, 2): "B", (1, 2): "A"}
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
    return tuple((i, j) for i in range(k) for j in range(i + 1, k))


def fixed_noncore_edge(i: int, j: int) -> Fraction:
    require(i < j, "edges must use increasing orientation")
    if i in CORE and j not in CORE:
        return Fraction(1)
    require(i not in CORE and j not in CORE, "unexpected edge class")
    return HALF


def edge_map(k: int, core_edge: Fraction | None) -> dict[tuple[int, int], Fraction]:
    result: dict[tuple[int, int], Fraction] = {}
    for i, j in pairs(k):
        if i in CORE and j in CORE:
            result[(i, j)] = HALF if core_edge is None else core_edge
        else:
            result[(i, j)] = fixed_noncore_edge(i, j)
    return result


def policy_values(
    k: int, edges: dict[tuple[int, int], Fraction]
) -> tuple[Fraction, ...]:
    require(set(edges) == set(pairs(k)), "edge support is incomplete")
    values = []
    for policy in range(k):
        numerator = HALF
        for opponent in range(k):
            if opponent == policy:
                continue
            if policy < opponent:
                numerator += edges[(policy, opponent)]
            else:
                numerator += 1 - edges[(opponent, policy)]
        values.append(numerator / k)
    return tuple(values)


def route(edge: tuple[int, int]) -> str:
    return CORE_ROUTES.get(edge, "A")


def potential_schedule(
    k: int, core_target_edge: Fraction
) -> dict[tuple[int, int], dict[str, Fraction]]:
    require(
        core_target_edge in (LOW, HIGH),
        "this fixed construction has only low and high core worlds",
    )
    unobserved = 2 * core_target_edge - HALF
    result: dict[tuple[int, int], dict[str, Fraction]] = {}
    for edge in pairs(k):
        i, j = edge
        if i in CORE and j in CORE:
            observed_context = route(edge)
            other_context = next(c for c in CONTEXTS if c != observed_context)
            result[edge] = {
                observed_context: HALF,
                other_context: unobserved,
            }
        else:
            fixed = fixed_noncore_edge(i, j)
            result[edge] = {context: fixed for context in CONTEXTS}
    return result


def common_target_edges(
    schedule: dict[tuple[int, int], dict[str, Fraction]]
) -> dict[tuple[int, int], Fraction]:
    return {
        edge: sum(contexts.values(), Fraction()) / len(CONTEXTS)
        for edge, contexts in schedule.items()
    }


def observed_projection(
    k: int, schedule: dict[tuple[int, int], dict[str, Fraction]]
) -> tuple[tuple[int, int, str, Fraction], ...]:
    rows = []
    for i, j in pairs(k):
        edge = (i, j)
        observed_context = route(edge)
        rows.append((i, j, observed_context, schedule[edge][observed_context]))
    return tuple(rows)


def winner_set(values: tuple[Fraction, ...]) -> tuple[int, ...]:
    maximum = max(values)
    return tuple(i for i, value in enumerate(values) if value == maximum)


def expected_values(k: int, world: str) -> tuple[Fraction, ...]:
    added = k - 3
    if world == "pair_conditioned":
        core_numerators = (
            Fraction(3, 2) + added,
            Fraction(3, 2) + added,
            Fraction(3, 2) + added,
        )
    elif world == "low":
        core_numerators = (
            Fraction(1) + added,
            Fraction(3, 2) + added,
            Fraction(2) + added,
        )
    elif world == "high":
        core_numerators = (
            Fraction(2) + added,
            Fraction(3, 2) + added,
            Fraction(1) + added,
        )
    else:
        raise ValueError(f"unexpected world {world!r}")
    extra_value = Fraction(k - 3, 2 * k)
    return tuple(value / k for value in core_numerators) + (extra_value,) * added


def check_k(k: int) -> dict[str, Any]:
    low_schedule = potential_schedule(k, LOW)
    high_schedule = potential_schedule(k, HIGH)
    low_observed = observed_projection(k, low_schedule)
    high_observed = observed_projection(k, high_schedule)
    require(low_observed == high_observed, "observed laws differ")

    observed_edges = edge_map(k, None)
    low_edges = common_target_edges(low_schedule)
    high_edges = common_target_edges(high_schedule)
    pair_values = policy_values(k, observed_edges)
    low_values = policy_values(k, low_edges)
    high_values = policy_values(k, high_edges)
    require(
        pair_values == expected_values(k, "pair_conditioned"),
        "pair-conditioned closed form failed",
    )
    require(low_values == expected_values(k, "low"), "low closed form failed")
    require(high_values == expected_values(k, "high"), "high closed form failed")
    require(winner_set(pair_values) == CORE, "pair-conditioned winner set changed")
    require(winner_set(low_values) == (2,), "low unique winner changed")
    require(winner_set(high_values) == (0,), "high unique winner changed")

    if k > 3:
        require(
            min(low_values[:3]) > max(low_values[3:])
            and min(high_values[:3]) > max(high_values[3:]),
            "an added policy reaches the core",
        )
    regret = low_values[2] - low_values[0]
    require(regret == high_values[0] - high_values[2], "regret is asymmetric")
    require(regret == Fraction(1, k), "regret identity changed")
    require(len(low_observed) == k * (k - 1) // 2, "pair support is incomplete")

    return {
        "k": k,
        "pair_count": len(low_observed),
        "pair_assignment_probability": fraction(Fraction(1, len(low_observed))),
        "pair_conditioned_winner_set": list(winner_set(pair_values)),
        "low_unique_winner": 2,
        "high_unique_winner": 0,
        "pair_conditioned_values": [fraction(value) for value in pair_values],
        "low_values": [fraction(value) for value in low_values],
        "high_values": [fraction(value) for value in high_values],
        "cross_world_extreme_regret": fraction(regret),
    }


def build() -> dict[str, Any]:
    checked = [check_k(k) for k in range(3, 33)]
    samples = {str(row["k"]): row for row in checked if row["k"] in (3, 4, 7, 32)}
    return {
        "schema": "h183-arbitrary-roster-pair-first-identification-v1",
        "protocol_sha256": sha256(PROTOCOL),
        "construction": {
            "core_policies": list(CORE),
            "added_policy_rule": "core always beats added; added pairs tie",
            "core_observed_edge": fraction(HALF),
            "core_low_common_edge": fraction(LOW),
            "core_high_common_edge": fraction(HIGH),
            "complete_pair_support": True,
        },
        "closed_forms": {
            "pair_conditioned_core_value": "(K-3/2)/K",
            "low_core_values": ["(K-2)/K", "(K-3/2)/K", "(K-1)/K"],
            "high_core_values": ["(K-1)/K", "(K-3/2)/K", "(K-2)/K"],
            "added_policy_value": "(K-3)/(2K)",
            "cross_world_extreme_regret": "1/K",
            "weakest_core_minus_added": "(K-1)/(2K)",
        },
        "checked_k_min": 3,
        "checked_k_max": 32,
        "checked_k_count": len(checked),
        "sample_checks": samples,
        "same_observed_law_for_all_pairs": True,
        "pair_conditioned_winner_set": [0, 1, 2],
        "for_every_integer_k_ge_3_there_exists_this_construction": True,
        "opposite_unique_common_context_winners_for_every_finite_k_ge_3": True,
        "complete_pair_support_identifies_common_context_winner": False,
        "status": "pass",
        "scope": (
            "For every integer K>=3 there exists this dominated-padding "
            "embedding of the exact H151 witness. It is not a statement about "
            "every roster or pair-first design, a minimax-regret floor over the "
            "two selected worlds, field prevalence, benchmark validity, or "
            "current execution."
        ),
    }


def validate(data: dict[str, Any]) -> None:
    require(
        data.get("schema")
        == "h183-arbitrary-roster-pair-first-identification-v1",
        "unexpected schema",
    )
    require(data.get("protocol_sha256") == sha256(PROTOCOL), "protocol changed")
    require(data.get("checked_k_count") == 30, "finite check count changed")
    require(
        data.get("opposite_unique_common_context_winners_for_every_finite_k_ge_3")
        is True,
        "arbitrary-roster conclusion missing",
    )
    require(
        data["closed_forms"]["cross_world_extreme_regret"] == "1/K",
        "regret closed form changed",
    )
    require(data.get("status") == "pass", "H183 did not pass")


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
        for k in range(3, 33):
            check_k(k)
        print("OK: H183 arbitrary-roster identification validates")
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
                "checked_k": [result["checked_k_min"], result["checked_k_max"]],
                "regret": result["closed_forms"]["cross_world_extreme_regret"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
