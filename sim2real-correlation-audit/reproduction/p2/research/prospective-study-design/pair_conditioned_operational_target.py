#!/usr/bin/env python3
"""Exact H165 pair-conditioned operational-target boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h165-pair-conditioned-operational-target.md"
H151_RESULT = FAMILY / "result-h151-pair-first-common-context-identification.json"
H152_RESULT = (
    FAMILY / "result-h152-pair-first-identification-independent-challenge.json"
)
OUTPUT = FAMILY / "result-h165-pair-conditioned-operational-target.json"

PAIRS = ("01", "02", "12")
THETA = {
    "01": Fraction(3, 4),
    "02": Fraction(1, 4),
    "12": Fraction(3, 4),
}
PI = {pair: Fraction(1, 3) for pair in PAIRS}
OPTIMAL_ROUTE = {"01": 0, "02": 2, "12": 1}
LOWER_INDEX_ROUTE = {"01": 0, "02": 0, "12": 1}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact(value: Fraction) -> dict[str, Any]:
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "text": f"{value.numerator}/{value.denominator}",
        "decimal": float(value),
    }


def pair_members(pair: str) -> tuple[int, int]:
    require(pair in PAIRS, f"unsupported pair {pair}")
    return int(pair[0]), int(pair[1])


def route_value(
    rule: dict[str, int],
    theta: dict[str, Fraction] = THETA,
    weights: dict[str, Fraction] = PI,
) -> Fraction:
    require(sum(weights.values(), Fraction()) == 1, "weights must sum to one")
    require(
        all(weight >= 0 for weight in weights.values()),
        "weights must be nonnegative",
    )
    total = Fraction()
    for pair, weight in weights.items():
        require(pair in theta, f"positive-weight edge {pair} is not identified")
        require(pair in rule, f"positive-weight edge {pair} has no routing action")
        lower, upper = pair_members(pair)
        choice = rule[pair]
        require(choice in (lower, upper), f"route choice {choice} not in pair {pair}")
        edge = theta[pair]
        require(Fraction() <= edge <= 1, f"edge {pair} outside [0,1]")
        total += weight * (edge if choice == lower else 1 - edge)
    return total


def tournament_values(
    theta: dict[str, Fraction] = THETA,
) -> tuple[Fraction, Fraction, Fraction]:
    require(set(theta) == set(PAIRS), "all three edges are required")
    q01, q02, q12 = (theta[pair] for pair in PAIRS)
    return (
        (Fraction(1, 2) + q01 + q02) / 3,
        (Fraction(1, 2) + (1 - q01) + q12) / 3,
        (Fraction(1, 2) + (1 - q02) + (1 - q12)) / 3,
    )


def missing_edge_decision(
    theta: dict[str, Fraction],
    weights: dict[str, Fraction] = PI,
) -> dict[str, Any]:
    missing = sorted(
        pair for pair, weight in weights.items() if weight > 0 and pair not in theta
    )
    return {
        "positive_weight_edges_missing": missing,
        "routing_value_identified": not missing,
        "decision": "identified" if not missing else "not_identified",
    }


def support_matrix() -> list[dict[str, str]]:
    return [
        {
            "target": "same_route_pair_choice",
            "decision": "supported_conditionally",
            "condition": "future pair uses the same declared pair-specific context mechanism",
        },
        {
            "target": "pair_routing_rule",
            "decision": "supported_conditionally",
            "condition": "fixed outcome-independent pair weights and identified positive-weight edges",
        },
        {
            "target": "mechanism_specific_tournament_score",
            "decision": "supported_as_mechanism_specific",
            "condition": "the tournament score itself is the declared action target",
        },
        {
            "target": "common_context_single_policy_selection",
            "decision": "refused_without_transport",
            "condition": "requires common-context identification",
        },
        {
            "target": "per_policy_task_success",
            "decision": "refused_without_bridge",
            "condition": "comparative outcomes alone do not identify marginal success",
        },
        {
            "target": "evaluator_or_simulator_causal_effect",
            "decision": "refused_without_randomized_intervention",
            "condition": "pair-conditioned comparisons are not evaluator-effect interventions",
        },
        {
            "target": "new_policy_task_site_or_context_transport",
            "decision": "refused_without_transport",
            "condition": "new domains are outside the fixed mechanism-specific target",
        },
        {
            "target": "outcome_adaptive_pair_weights",
            "decision": "refused_without_new_analysis",
            "condition": "reported routing target fixes weights independently of outcomes",
        },
        {
            "target": "unmeasured_positive_weight_edge_decision",
            "decision": "refused_as_not_identified",
            "condition": "every positive-weight edge must be identified or honestly bounded",
        },
    ]


def upstream_boundary() -> dict[str, Any]:
    h151 = json.loads(H151_RESULT.read_text(encoding="utf-8"))
    h152 = json.loads(H152_RESULT.read_text(encoding="utf-8"))
    require(
        h151["pair_conditioned_policy_tie"] is True,
        "H151 pair-conditioned tie changed",
    )
    require(
        h151["world_low"]["unique_winner"] == 2
        and h151["world_high"]["unique_winner"] == 0,
        "H151 common-context winner reversal changed",
    )
    require(
        h151["endpoint_regret_census"]["every_singleton_floor"]["text"] == "1/3",
        "H151 singleton regret floor changed",
    )
    require(
        h151["complete_pair_support_identifies_common_context_target"] is False,
        "H151 identification boundary weakened",
    )
    require(
        h152["pair_conditioned_policy_values"] == ["1/2", "1/2", "1/2"]
        and h152["low_world"]["unique_winner"] == 2
        and h152["high_world"]["unique_winner"] == 0
        and h152["singleton_worst_regret"] == ["1/3", "1/3", "1/3"],
        "H152 independent challenge disagrees",
    )
    require(h152["disposition"] == "pass_with_scope", "H152 did not pass")
    return {
        "h151_result_sha256": sha256(H151_RESULT),
        "h152_result_sha256": sha256(H152_RESULT),
        "pair_conditioned_tie": True,
        "compatible_common_context_unique_winners": [2, 0],
        "every_singleton_common_context_regret_floor": exact(Fraction(1, 3)),
        "common_context_target_identified": False,
        "independent_challenge_agrees": True,
    }


def build() -> dict[str, Any]:
    optimal_value = route_value(OPTIMAL_ROUTE)
    lower_value = route_value(LOWER_INDEX_ROUTE)
    regret = optimal_value - lower_value
    values = tournament_values()
    require(optimal_value == Fraction(3, 4), "optimal routing value changed")
    require(lower_value == Fraction(7, 12), "lower-index value changed")
    require(regret == Fraction(1, 6), "routing regret changed")
    require(values == (Fraction(1, 2),) * 3, "tournament tie changed")
    preferences = [
        {"pair": "01", "preferred_policy": 0, "relation": "0>1"},
        {"pair": "02", "preferred_policy": 2, "relation": "2>0"},
        {"pair": "12", "preferred_policy": 1, "relation": "1>2"},
    ]
    require(
        [row["preferred_policy"] for row in preferences]
        == [OPTIMAL_ROUTE[pair] for pair in PAIRS],
        "cycle and optimal route disagree",
    )
    missing = missing_edge_decision({"01": THETA["01"], "12": THETA["12"]})
    require(
        missing["decision"] == "not_identified"
        and missing["positive_weight_edges_missing"] == ["02"],
        "missing-edge refusal changed",
    )
    matrix = support_matrix()
    require(
        len(matrix) == 9
        and sum(row["decision"].startswith("refused") for row in matrix) == 6,
        "support/refusal matrix changed",
    )
    return {
        "schema": "h165-pair-conditioned-operational-target-v1",
        "protocol_sha256": sha256(PROTOCOL),
        "upstream_boundary": upstream_boundary(),
        "known_answer": {
            "pairs": list(PAIRS),
            "pair_weights": {pair: exact(PI[pair]) for pair in PAIRS},
            "pair_conditioned_edges": {
                pair: exact(THETA[pair]) for pair in PAIRS
            },
            "cyclic_preferences": preferences,
            "edge_optimal_routing_rule": OPTIMAL_ROUTE,
            "edge_optimal_routing_value": exact(optimal_value),
            "always_lower_index_rule": LOWER_INDEX_ROUTE,
            "always_lower_index_value": exact(lower_value),
            "always_lower_index_regret": exact(regret),
            "uniform_reference_tournament_values": [
                exact(value) for value in values
            ],
            "uniform_reference_tournament_tie": True,
            "unique_global_policy_identified": False,
        },
        "support_and_refusal_matrix": matrix,
        "positive_weight_missing_edge_attack": missing,
        "reporting_gate": {
            "pair_routing_action_explicit": True,
            "pair_weights_fixed_outcome_independently": True,
            "positive_weight_edges_identified_or_bounded": True,
            "future_pair_context_mechanism_fixed": True,
            "orientation_and_tie_rule_fixed": True,
            "uncertainty_must_respect_assignment_and_clustering": True,
        },
        "advancement": "pass",
        "real_site_qualified": False,
        "field_collection_authorized": False,
        "standalone_paper_novelty_claimed": False,
        "scope": (
            "Exact identification-semantics boundary for a pair-conditioned "
            "routing action; not a confidence procedure, common-context "
            "deployment ranking, site qualification, or field result."
        ),
    }


def canonical_bytes(data: dict[str, Any]) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8")


def validate(data: dict[str, Any]) -> None:
    require(
        data.get("schema") == "h165-pair-conditioned-operational-target-v1",
        "unexpected schema",
    )
    require(data.get("protocol_sha256") == sha256(PROTOCOL), "protocol changed")
    known = data["known_answer"]
    require(
        known["edge_optimal_routing_value"]["text"] == "3/4"
        and known["always_lower_index_value"]["text"] == "7/12"
        and known["always_lower_index_regret"]["text"] == "1/6",
        "known routing values changed",
    )
    require(
        [value["text"] for value in known["uniform_reference_tournament_values"]]
        == ["1/2", "1/2", "1/2"]
        and known["unique_global_policy_identified"] is False,
        "global-action boundary changed",
    )
    require(
        data["positive_weight_missing_edge_attack"]["decision"] == "not_identified",
        "missing-edge attack was not refused",
    )
    require(
        data["upstream_boundary"]["h151_result_sha256"] == sha256(H151_RESULT)
        and data["upstream_boundary"]["h152_result_sha256"] == sha256(H152_RESULT),
        "upstream result changed",
    )
    require(data.get("advancement") == "pass", "H165 did not pass")
    require(data.get("field_collection_authorized") is False, "field use authorized")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("choose exactly one")
    result = build()
    validate(result)
    rendered = canonical_bytes(result)
    if args.check:
        require(args.out.read_bytes() == rendered, "canonical result is stale")
        print("OK: H165 pair-conditioned operational target regenerates exactly")
        return
    args.out.write_bytes(rendered)
    print(
        json.dumps(
            {
                "status": result["advancement"],
                "optimal_routing_value": result["known_answer"][
                    "edge_optimal_routing_value"
                ]["text"],
                "global_policy_identified": result["known_answer"][
                    "unique_global_policy_identified"
                ],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
