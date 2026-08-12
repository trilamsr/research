#!/usr/bin/env python3
"""Vertex-enumeration cross-check for H250; imports no producer implementation."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import linprog


FAMILY = Path(__file__).resolve().parent
PRODUCER = FAMILY / "finite_sample_route_graph.py"
PRODUCER_RESULT = FAMILY / "result-h250-finite-sample-route-graph.json"
PROTOCOL = FAMILY / "protocol-h250-finite-sample-route-graph.md"
OUTPUT = FAMILY / "result-h250-finite-sample-route-graph-vertex-challenge.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def constraint_system(
    k: int,
    edges: tuple[tuple[int, int], ...],
    lower: tuple[float, ...],
    upper: tuple[float, ...],
) -> tuple[np.ndarray, np.ndarray]:
    e = np.zeros((len(edges), k))
    for row, (i, j) in enumerate(edges):
        e[row, i] = 1
        e[row, j] = -1
    identity = np.eye(k)
    return (
        np.vstack((e, -e, identity, -identity)),
        np.concatenate((upper, -np.asarray(lower), np.ones(k), np.zeros(k))),
    )


def vertices(a: np.ndarray, b: np.ndarray) -> list[np.ndarray]:
    k = a.shape[1]
    found: dict[tuple[float, ...], np.ndarray] = {}
    for active in itertools.combinations(range(len(b)), k):
        matrix = a[list(active)]
        if np.linalg.matrix_rank(matrix) < k:
            continue
        candidate = np.linalg.solve(matrix, b[list(active)])
        if np.all(a @ candidate <= b + 1e-9):
            key = tuple(float(value) for value in np.round(candidate, 10))
            found[key] = candidate
    require(bool(found), "no feasible vertices")
    return list(found.values())


def enumerate_target_vertices(
    k: int,
    contexts: tuple[
        tuple[float, tuple[tuple[int, int], ...], tuple[float, ...], tuple[float, ...]],
        ...,
    ],
) -> list[np.ndarray]:
    per_context = [vertices(*constraint_system(k, edges, lower, upper)) for _, edges, lower, upper in contexts]
    targets = {}
    for combination in itertools.product(*per_context):
        mu = sum(contexts[c][0] * combination[c] for c in range(len(contexts)))
        targets[tuple(float(value) for value in np.round(mu, 10))] = mu
    return list(targets.values())


def direct_analysis(k: int, contexts: tuple[Any, ...]) -> dict[str, Any]:
    targets = enumerate_target_vertices(k, contexts)
    difference_bounds = {}
    for i in range(k):
        for j in range(i + 1, k):
            values = [float(mu[i] - mu[j]) for mu in targets]
            difference_bounds[f"{i}-{j}"] = {"lower": min(values), "upper": max(values)}
    possible = [
        winner
        for winner in range(k)
        if any(all(mu[winner] >= mu[other] - 1e-10 for other in range(k)) for mu in targets)
    ]
    certified = [
        winner
        for winner in range(k)
        if all(all(mu[winner] > mu[other] + 1e-10 for other in range(k) if other != winner) for mu in targets)
    ]

    variable_count = k + 1
    objective = np.zeros(variable_count)
    objective[-1] = 1
    inequalities = []
    rhs = []
    for mu in targets:
        row = np.zeros(variable_count)
        row[:k] = -0.5 * mu
        row[-1] = -1
        inequalities.append(row)
        rhs.append(-0.5 * float(np.max(mu)))
    equality = np.zeros((1, variable_count))
    equality[0, :k] = 1
    result = linprog(
        objective,
        A_ub=np.asarray(inequalities),
        b_ub=np.asarray(rhs),
        A_eq=equality,
        b_eq=np.asarray([1.0]),
        bounds=[(0, 1)] * k + [(0, None)],
        method="highs",
    )
    require(result.success, "direct finite-world minimax LP failed")
    return {
        "target_vertex_count": len(targets),
        "target_difference_bounds": difference_bounds,
        "possible_winners": possible,
        "certified_unique_winners": certified,
        "minimax_lottery": [0.0 if abs(value) < 1e-12 else float(value) for value in result.x[:k]],
        "minimax_half_credit_regret": float(result.x[-1]),
    }


def cases() -> dict[str, tuple[Any, ...]]:
    return {
        "h233_point_case": (
            (0.5, ((0, 2), (1, 2)), (0.0, 0.0), (0.0, 0.0)),
            (0.5, ((0, 1),), (0.5,), (0.5,)),
        ),
        "connected_point_case": ((1.0, ((0, 1), (1, 2)), (0.3, 0.3), (0.3, 0.3)),),
        "disconnected_point_case": ((1.0, ((0, 1),), (0.3,), (0.3,)),),
        "connected_wider_case": ((1.0, ((0, 1), (1, 2)), (0.2, 0.2), (0.4, 0.4)),),
    }


def compare(producer: dict[str, Any], challenge: dict[str, Any]) -> None:
    for name, direct in challenge["cases"].items():
        expected = producer["known_answers"][name]
        require(direct["possible_winners"] == expected["possible_winners"], f"{name} possible winners")
        require(direct["certified_unique_winners"] == expected["certified_unique_winners"], f"{name} certified winners")
        require(np.allclose(direct["minimax_lottery"], expected["minimax_lottery"], atol=1e-9), f"{name} lottery")
        require(abs(direct["minimax_half_credit_regret"] - expected["minimax_half_credit_regret"]) <= 1e-9, f"{name} regret")
        for edge, interval in direct["target_difference_bounds"].items():
            require(abs(interval["lower"] - expected["target_difference_bounds"][edge]["lower"]) <= 1e-9, f"{name} {edge} lower")
            require(abs(interval["upper"] - expected["target_difference_bounds"][edge]["upper"]) <= 1e-9, f"{name} {edge} upper")


def build() -> dict[str, Any]:
    producer = json.loads(PRODUCER_RESULT.read_text(encoding="utf-8"))
    result = {
        "schema": "h250-finite-sample-route-graph-vertex-challenge-v1",
        "protocol_sha256": sha256(PROTOCOL),
        "producer_implementation_sha256": sha256(PRODUCER),
        "producer_result_sha256": sha256(PRODUCER_RESULT),
        "challenge_implementation_sha256": sha256(Path(__file__)),
        "method": "enumerate polytope vertices, then solve the finite-world primal minimax LP",
        "cases": {name: direct_analysis(3, contexts) for name, contexts in cases().items()},
        "status": "pass",
    }
    compare(producer, result)
    return result


def validate(result: dict[str, Any]) -> None:
    require(result.get("schema") == "h250-finite-sample-route-graph-vertex-challenge-v1", "schema")
    require(result.get("protocol_sha256") == sha256(PROTOCOL), "protocol hash")
    require(result.get("producer_implementation_sha256") == sha256(PRODUCER), "producer hash")
    require(result.get("producer_result_sha256") == sha256(PRODUCER_RESULT), "producer result hash")
    require(result.get("challenge_implementation_sha256") == sha256(Path(__file__)), "challenge hash")
    require(result.get("status") == "pass", "status")
    compare(json.loads(PRODUCER_RESULT.read_text(encoding="utf-8")), result)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        validate(json.loads(OUTPUT.read_text(encoding="utf-8")))
        return
    OUTPUT.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
