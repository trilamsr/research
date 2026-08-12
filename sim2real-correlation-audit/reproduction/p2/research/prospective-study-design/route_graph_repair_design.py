#!/usr/bin/env python3
"""H234 minimum route-graph repair for contextwise identification."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "protocol-h234-route-graph-repair-design.md"
OUTPUT = HERE / "result-h234-route-graph-repair-design.json"

Edge = tuple[int, int]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_edge(i: int, j: int) -> Edge:
    if i == j:
        raise ValueError("self-edge")
    return (i, j) if i < j else (j, i)


def all_edges(k: int) -> tuple[Edge, ...]:
    return tuple(itertools.combinations(range(k), 2))


def components(k: int, edges: tuple[Edge, ...]) -> list[tuple[int, ...]]:
    adjacent = [set() for _ in range(k)]
    for i, j in edges:
        adjacent[i].add(j)
        adjacent[j].add(i)
    unseen = set(range(k))
    groups: list[tuple[int, ...]] = []
    while unseen:
        root = min(unseen)
        unseen.remove(root)
        stack = [root]
        group: list[int] = []
        while stack:
            node = stack.pop()
            group.append(node)
            for neighbor in sorted(adjacent[node] & unseen, reverse=True):
                unseen.remove(neighbor)
                stack.append(neighbor)
        groups.append(tuple(sorted(group)))
    return groups


def is_connected(k: int, edges: tuple[Edge, ...]) -> bool:
    return len(components(k, edges)) == 1


def repair(
    k: int,
    current: tuple[Edge, ...],
    allowable: tuple[Edge, ...] | None = None,
    costs: dict[Edge, int] | None = None,
) -> dict[str, object]:
    current_set = {canonical_edge(*edge) for edge in current}
    allowed_set = (
        set(all_edges(k)) - current_set
        if allowable is None
        else {canonical_edge(*edge) for edge in allowable} - current_set
    )
    groups = components(k, tuple(sorted(current_set)))
    if len(groups) == 1:
        return {
            "feasible": True,
            "components_before": 1,
            "minimum_new_pair_types": 0,
            "selected_edges": [],
            "total_cost": 0,
        }

    component_of = {
        policy: component
        for component, group in enumerate(groups)
        for policy in group
    }
    quotient_candidates: dict[tuple[int, int], tuple[int, Edge]] = {}
    for edge in sorted(allowed_set):
        left, right = component_of[edge[0]], component_of[edge[1]]
        if left == right:
            continue
        quotient = canonical_edge(left, right)
        cost = 1 if costs is None else costs[edge]
        candidate = (cost, edge)
        if quotient not in quotient_candidates or candidate < quotient_candidates[quotient]:
            quotient_candidates[quotient] = candidate

    parent = list(range(len(groups)))

    def find(node: int) -> int:
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    selected: list[Edge] = []
    total_cost = 0
    ordered = sorted(
        (cost, edge, quotient)
        for quotient, (cost, edge) in quotient_candidates.items()
    )
    for cost, edge, (left, right) in ordered:
        root_left, root_right = find(left), find(right)
        if root_left == root_right:
            continue
        parent[root_right] = root_left
        selected.append(edge)
        total_cost += cost

    feasible = len(selected) == len(groups) - 1
    if not feasible:
        selected = []
        total_cost = 0
    return {
        "feasible": feasible,
        "components_before": len(groups),
        "minimum_new_pair_types": len(groups) - 1 if feasible else None,
        "selected_edges": [list(edge) for edge in selected],
        "total_cost": total_cost if feasible else None,
    }


def brute_minimum_count(
    k: int, current: tuple[Edge, ...], allowable: tuple[Edge, ...]
) -> int | None:
    current_set = set(current)
    candidates = tuple(sorted(set(allowable) - current_set))
    for count in range(len(candidates) + 1):
        for chosen in itertools.combinations(candidates, count):
            if is_connected(k, tuple(sorted(current_set | set(chosen)))):
                return count
    return None


def brute_minimum_cost(
    k: int,
    current: tuple[Edge, ...],
    allowable: tuple[Edge, ...],
    costs: dict[Edge, int],
) -> int | None:
    current_set = set(current)
    candidates = tuple(sorted(set(allowable) - current_set))
    best: int | None = None
    for mask in range(1 << len(candidates)):
        chosen = tuple(
            edge for bit, edge in enumerate(candidates) if mask & (1 << bit)
        )
        cost = sum(costs[edge] for edge in chosen)
        if best is not None and cost >= best:
            continue
        if is_connected(k, tuple(sorted(current_set | set(chosen)))):
            best = cost
    return best


def exhaustive_unit_census() -> dict[str, int]:
    exact_graphs = 0
    sampled_k6_graphs = 0
    for k in range(2, 7):
        universe = all_edges(k)
        if k <= 5:
            masks = range(1 << len(universe))
        else:
            masks = sorted(
                {
                    0,
                    (1 << len(universe)) - 1,
                    *[
                        int.from_bytes(
                            hashlib.sha256(f"h234-{index}".encode()).digest()[:4],
                            "big",
                        )
                        % (1 << len(universe))
                        for index in range(512)
                    ],
                }
            )
        for mask in masks:
            current = tuple(
                edge
                for bit, edge in enumerate(universe)
                if mask & (1 << bit)
            )
            expected = len(components(k, current)) - 1
            proposed = repair(k, current)
            if proposed["minimum_new_pair_types"] != expected:
                raise AssertionError((k, current, proposed, expected))
            brute = brute_minimum_count(k, current, universe)
            if brute != expected:
                raise AssertionError((k, current, brute, expected))
            if k <= 5:
                exact_graphs += 1
            else:
                sampled_k6_graphs += 1
    return {
        "exhaustive_current_graphs_k2_to_k5": exact_graphs,
        "deterministic_sampled_current_graphs_k6": sampled_k6_graphs,
    }


def exhaustive_allowable_census() -> dict[str, int]:
    states = 0
    for k in range(2, 6):
        universe = all_edges(k)
        # Ternary state per edge: unavailable, currently present, or allowable.
        for labels in itertools.product(range(3), repeat=len(universe)):
            current = tuple(
                edge for edge, label in zip(universe, labels) if label == 1
            )
            allowable = tuple(
                edge for edge, label in zip(universe, labels) if label == 2
            )
            proposed = repair(k, current, allowable)
            brute = brute_minimum_count(k, current, allowable)
            if proposed["feasible"] != (brute is not None):
                raise AssertionError((k, current, allowable, proposed, brute))
            if brute is not None and proposed["minimum_new_pair_types"] != brute:
                raise AssertionError((k, current, allowable, proposed, brute))
            states += 1
    return {"exhaustive_current_allowable_states_k2_to_k5": states}


def cost_census() -> dict[str, int]:
    panels = 0
    for k in range(2, 7):
        universe = all_edges(k)
        masks = range(1 << len(universe)) if k <= 4 else range(128)
        for index, mask in enumerate(masks):
            current = tuple(
                edge
                for bit, edge in enumerate(universe)
                if mask & (1 << bit)
            )
            allowable = tuple(edge for edge in universe if edge not in current)
            costs = {
                edge: 1
                + int.from_bytes(
                    hashlib.sha256(f"{k}-{index}-{edge}".encode()).digest()[:2],
                    "big",
                )
                % 29
                for edge in allowable
            }
            proposed = repair(k, current, allowable, costs)
            brute = brute_minimum_cost(k, current, allowable, costs)
            if proposed["total_cost"] != brute:
                raise AssertionError((k, current, proposed, brute))
            panels += 1
    return {"deterministic_cost_panels_k2_to_k6": panels}


def build() -> dict[str, object]:
    unit = exhaustive_unit_census()
    allowable = exhaustive_allowable_census()
    costs = cost_census()

    h233_a = repair(3, ((0, 2), (1, 2)))
    h233_b = repair(3, ((0, 1),))
    h231_b = {str(k): repair(k, ()) for k in range(3, 9)}

    constrained_costs = {
        (0, 2): 7,
        (1, 2): 2,
        (2, 3): 3,
        (0, 3): 11,
    }
    constrained = repair(
        4,
        ((0, 1),),
        tuple(constrained_costs),
        constrained_costs,
    )
    if constrained["selected_edges"] != [[1, 2], [2, 3]]:
        raise AssertionError(constrained)
    if constrained["total_cost"] != 5:
        raise AssertionError(constrained)

    # Duplicate/repeated observations do not change the simple route graph.
    repeated_rank_invariant = (
        len(components(4, ((0, 1), (1, 2))))
        == len(components(4, ((0, 1), (0, 1), (1, 2), (1, 2))))
    )
    if not repeated_rank_invariant:
        raise AssertionError("duplicate edge changed graph components")

    return {
        "schema": "h234-route-graph-repair-design-v1",
        "status": "pass",
        "classification": "constructive_contextwise_identification_repair",
        "outcome_status": "post_h233_outcome_exposed_exploratory",
        "protocol_sha256": sha256(PROTOCOL),
        "verification": {**unit, **allowable, **costs},
        "theorem": {
            "minimum_new_pair_types_per_context": "components-1",
            "allowable_edge_feasibility": "connected component quotient graph",
            "minimum_cost_rule": "minimum spanning tree on component quotient graph",
            "multi_context_total": "sum(components_c-1) when every positive-weight context must be connected and each new pair type belongs to one context",
            "repeated_existing_edges_repair_identification": False,
        },
        "known_answers": {
            "h233_context_a": h233_a,
            "h233_context_b": h233_b,
            "h231_unobserved_context_b_k3_to_k8": h231_b,
            "constrained_cost_case": constrained,
        },
        "boundary": (
            "Minimum is for contextwise difference identification under H233; "
            "one boundary-specific winner or aggregate target may require fewer edges."
        ),
        "prior_art_boundary": (
            "Connectivity and well-connected comparison designs are established; "
            "this is an executable model-specific repair corollary."
        ),
    }


def validate(data: dict[str, object]) -> None:
    if data != build():
        raise AssertionError("stored H234 result is stale")


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(f"WROTE {OUTPUT}")
    else:
        validate(json.loads(OUTPUT.read_text()))
        print("OK: H234 route-graph repair result")


if __name__ == "__main__":
    main()
