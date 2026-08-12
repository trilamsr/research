#!/usr/bin/env python3
"""Exact H151 pair-first/common-context identification counterexample."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h151-pair-first-common-context-identification.md"
OUTPUT = FAMILY / "result-h151-pair-first-common-context-identification.json"
PAIRS = ("01", "02", "12")
CONTEXTS = ("A", "B")
ROUTES = {"01": "A", "02": "B", "12": "A"}
OBSERVED_OUTCOME = Fraction(1, 2)
TARGET_LOWER = Fraction(1, 4)
TARGET_UPPER = Fraction(3, 4)


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


def policy_values(
    edge_values: tuple[Fraction, Fraction, Fraction],
) -> tuple[Fraction, Fraction, Fraction]:
    q01, q02, q12 = edge_values
    require(
        all(Fraction() <= value <= 1 for value in edge_values),
        "edge value outside [0,1]",
    )
    return (
        (Fraction(1, 2) + q01 + q02) / 3,
        (Fraction(1, 2) + (1 - q01) + q12) / 3,
        (Fraction(1, 2) + (1 - q02) + (1 - q12)) / 3,
    )


def potential_schedule(target_edge: Fraction) -> dict[str, dict[str, Fraction]]:
    require(
        TARGET_LOWER <= target_edge <= TARGET_UPPER,
        "target edge outside compatible interval",
    )
    unobserved = 2 * target_edge - OBSERVED_OUTCOME
    require(Fraction() <= unobserved <= 1, "unobserved outcome outside [0,1]")
    schedule: dict[str, dict[str, Fraction]] = {}
    for pair in PAIRS:
        observed_context = ROUTES[pair]
        other_context = next(
            context for context in CONTEXTS if context != observed_context
        )
        schedule[pair] = {
            observed_context: OBSERVED_OUTCOME,
            other_context: unobserved,
        }
    return schedule


def observed_projection(
    schedule: dict[str, dict[str, Fraction]],
) -> tuple[tuple[str, str, Fraction], ...]:
    rows = tuple(
        (pair, ROUTES[pair], schedule[pair][ROUTES[pair]]) for pair in PAIRS
    )
    require(
        all(row[2] == OBSERVED_OUTCOME for row in rows),
        "observed outcome changed",
    )
    return rows


def common_target_edges(
    schedule: dict[str, dict[str, Fraction]],
) -> tuple[Fraction, Fraction, Fraction]:
    return tuple(
        sum((schedule[pair][context] for context in CONTEXTS), Fraction()) / 2
        for pair in PAIRS
    )  # type: ignore[return-value]


def world(target_edge: Fraction) -> dict[str, Any]:
    schedule = potential_schedule(target_edge)
    observed = observed_projection(schedule)
    edges = common_target_edges(schedule)
    values = policy_values(edges)
    winner = max(range(3), key=lambda policy: values[policy])
    require(values.count(values[winner]) == 1, "winner is not unique")
    return {
        "target_edge": fraction(target_edge),
        "potential_schedule": {
            pair: {
                context: fraction(value)
                for context, value in sorted(contexts.items())
            }
            for pair, contexts in sorted(schedule.items())
        },
        "observed_projection": [
            {"pair": pair, "context": context, "outcome": fraction(outcome)}
            for pair, context, outcome in observed
        ],
        "common_target_edges": [fraction(value) for value in edges],
        "common_target_policy_values": [fraction(value) for value in values],
        "unique_winner": winner,
    }


def endpoint_regret_census() -> dict[str, Any]:
    rows = []
    worst = [Fraction(), Fraction(), Fraction()]
    witnesses: list[list[str]] = [[], [], []]
    for edge_values in itertools.product(
        (TARGET_LOWER, TARGET_UPPER), repeat=len(PAIRS)
    ):
        values = policy_values(edge_values)
        best = max(values)
        row_regrets = tuple(best - value for value in values)
        label = ",".join(f"{value.numerator}/{value.denominator}" for value in edge_values)
        rows.append(
            {
                "edge_values": [fraction(value) for value in edge_values],
                "policy_values": [fraction(value) for value in values],
                "singleton_regrets": [fraction(value) for value in row_regrets],
            }
        )
        for policy, regret in enumerate(row_regrets):
            if regret > worst[policy]:
                worst[policy] = regret
                witnesses[policy] = [label]
            elif regret == worst[policy]:
                witnesses[policy].append(label)
    require(len(rows) == 8, "endpoint census size changed")
    require(
        worst == [Fraction(1, 3)] * 3,
        "singleton worst-regret floor changed",
    )
    return {
        "endpoint_completions_exhausted": len(rows),
        "rows": rows,
        "singleton_worst_regret": [fraction(value) for value in worst],
        "singleton_witnesses": witnesses,
        "every_singleton_floor": fraction(Fraction(1, 3)),
    }


def build() -> dict[str, Any]:
    low = world(TARGET_LOWER)
    high = world(TARGET_UPPER)
    require(
        low["observed_projection"] == high["observed_projection"],
        "worlds are not observationally equivalent",
    )
    require(
        low["unique_winner"] == 2 and high["unique_winner"] == 0,
        "winner reversal changed",
    )
    pair_conditioned = policy_values(
        (OBSERVED_OUTCOME, OBSERVED_OUTCOME, OBSERVED_OUTCOME)
    )
    require(
        pair_conditioned == (Fraction(1, 2),) * 3,
        "pair-conditioned values do not tie",
    )
    cross_world_regret = (
        Fraction(2, 3) - Fraction(1, 3)
    )
    return {
        "schema": "h151-pair-first-common-context-identification-v1",
        "protocol_sha256": sha256(PROTOCOL),
        "design": {
            "policies": 3,
            "pairs": list(PAIRS),
            "contexts": list(CONTEXTS),
            "pair_assignment_probability": fraction(Fraction(1, 3)),
            "pair_conditioned_routes": ROUTES,
            "observed_outcome_on_every_route": fraction(OBSERVED_OUTCOME),
            "common_target_context_weights": {
                "A": fraction(Fraction(1, 2)),
                "B": fraction(Fraction(1, 2)),
            },
        },
        "pair_conditioned_edge_values": [
            fraction(OBSERVED_OUTCOME) for _ in PAIRS
        ],
        "pair_conditioned_policy_values": [
            fraction(value) for value in pair_conditioned
        ],
        "pair_conditioned_policy_tie": True,
        "compatible_common_target_edge_interval": {
            "lower": fraction(TARGET_LOWER),
            "upper": fraction(TARGET_UPPER),
            "construction": "unobserved outcome = 2*target_edge - 1/2",
        },
        "world_low": low,
        "world_high": high,
        "same_observed_pair_context_outcome_law": True,
        "opposite_unique_common_context_winners": True,
        "extreme_policy_cross_world_regret": fraction(cross_world_regret),
        "endpoint_regret_census": endpoint_regret_census(),
        "complete_pair_support_identifies_common_context_target": False,
        "unlimited_same_route_repetition_resolves_target": False,
        "pair_conditioned_estimand_is_well_defined": True,
        "additional_identifying_condition_required": True,
        "status": "pass",
        "scope": (
            "Exact target-identification counterexample for pair-first, "
            "pair-conditioned context construction; not a claim that the "
            "pair-conditioned estimand or public benchmark is invalid."
        ),
    }


def validate(data: dict[str, Any]) -> None:
    require(
        data.get("schema")
        == "h151-pair-first-common-context-identification-v1",
        "unexpected schema",
    )
    require(data.get("protocol_sha256") == sha256(PROTOCOL), "protocol changed")
    require(data.get("same_observed_pair_context_outcome_law") is True, "law changed")
    require(
        data.get("opposite_unique_common_context_winners") is True,
        "winner reversal missing",
    )
    require(
        data["world_low"]["unique_winner"] == 2
        and data["world_high"]["unique_winner"] == 0,
        "winner identities changed",
    )
    require(
        data["endpoint_regret_census"]["endpoint_completions_exhausted"] == 8,
        "endpoint census incomplete",
    )
    require(
        all(
            value["text"] == "1/3"
            for value in data["endpoint_regret_census"][
                "singleton_worst_regret"
            ]
        ),
        "singleton floor changed",
    )
    require(
        data.get("complete_pair_support_identifies_common_context_target")
        is False
        and data.get("additional_identifying_condition_required") is True,
        "identification boundary weakened",
    )
    require(data.get("status") == "pass", "H151 did not pass")


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
        print("OK: H151 pair-first/common-context counterexample validates")
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
                "pair_conditioned_tie": result["pair_conditioned_policy_tie"],
                "world_low_winner": result["world_low"]["unique_winner"],
                "world_high_winner": result["world_high"]["unique_winner"],
                "singleton_floor": result["endpoint_regret_census"][
                    "every_singleton_floor"
                ]["text"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
