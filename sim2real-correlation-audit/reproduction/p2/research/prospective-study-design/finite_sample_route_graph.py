#!/usr/bin/env python3
"""Propagate simultaneous edge intervals through P2's route-graph model."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import scipy
from scipy.linalg import block_diag
from scipy.optimize import linprog


FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h250-finite-sample-route-graph.md"
OUTPUT = FAMILY / "result-h250-finite-sample-route-graph.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass(frozen=True)
class Context:
    weight: float
    edges: tuple[tuple[int, int], ...]
    lower: tuple[float, ...]
    upper: tuple[float, ...]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def incidence(k: int, edges: Iterable[tuple[int, int]]) -> np.ndarray:
    rows = []
    seen: set[tuple[int, int]] = set()
    for i, j in edges:
        require(0 <= i < k and 0 <= j < k and i != j, "invalid edge")
        require((i, j) not in seen, "duplicate oriented edge")
        seen.add((i, j))
        row = np.zeros(k)
        row[i] = 1.0
        row[j] = -1.0
        rows.append(row)
    return np.asarray(rows, dtype=float).reshape((-1, k))


def context_constraints(k: int, context: Context) -> tuple[np.ndarray, np.ndarray]:
    e = incidence(k, context.edges)
    lower = np.asarray(context.lower, dtype=float)
    upper = np.asarray(context.upper, dtype=float)
    require(len(lower) == len(context.edges), "lower-bound length mismatch")
    require(len(upper) == len(context.edges), "upper-bound length mismatch")
    require(np.all(np.isfinite(lower)) and np.all(np.isfinite(upper)), "nonfinite interval")
    require(np.all(lower >= -1) and np.all(upper <= 1), "difference outside [-1,1]")
    require(np.all(lower <= upper), "reversed interval")
    identity = np.eye(k)
    a = np.vstack((e, -e, identity, -identity))
    b = np.concatenate((upper, -lower, np.ones(k), np.zeros(k)))
    feasibility = linprog(
        np.zeros(k), A_ub=a, b_ub=b, bounds=[(None, None)] * k, method="highs"
    )
    require(feasibility.success, "infeasible context interval system")
    return a, b


def validate_contexts(k: int, contexts: tuple[Context, ...]) -> None:
    require(k >= 2, "at least two policies required")
    require(bool(contexts), "at least one context required")
    weights = np.asarray([context.weight for context in contexts], dtype=float)
    require(np.all(np.isfinite(weights)) and np.all(weights > 0), "invalid context weight")
    require(abs(float(weights.sum()) - 1.0) <= 1e-12, "context weights must sum to one")
    for context in contexts:
        context_constraints(k, context)


def global_constraints(k: int, contexts: tuple[Context, ...]) -> tuple[np.ndarray, np.ndarray]:
    blocks = [context_constraints(k, context) for context in contexts]
    return block_diag(*(item[0] for item in blocks)), np.concatenate(
        [item[1] for item in blocks]
    )


def target_contrast(k: int, contexts: tuple[Context, ...], i: int, j: int) -> np.ndarray:
    contrast = np.zeros(k * len(contexts))
    for c, context in enumerate(contexts):
        contrast[c * k + i] = context.weight
        contrast[c * k + j] = -context.weight
    return contrast


def solve_linear(
    objective: np.ndarray, a: np.ndarray, b: np.ndarray, maximize: bool = False
) -> float:
    result = linprog(
        -objective if maximize else objective,
        A_ub=a,
        b_ub=b,
        bounds=[(None, None)] * len(objective),
        method="highs",
    )
    require(result.success, "linear program failed")
    value = float(objective @ result.x)
    return 0.0 if abs(value) < 1e-12 else value


def analyze(k: int, contexts: tuple[Context, ...]) -> dict[str, Any]:
    validate_contexts(k, contexts)
    a, b = global_constraints(k, contexts)
    bounds: dict[str, dict[str, float]] = {}
    lower_matrix = np.zeros((k, k))
    upper_matrix = np.zeros((k, k))
    for i in range(k):
        for j in range(i + 1, k):
            contrast = target_contrast(k, contexts, i, j)
            lower = solve_linear(contrast, a, b)
            upper = solve_linear(contrast, a, b, maximize=True)
            require(lower <= upper + 1e-10, "invalid projected interval")
            lower_matrix[i, j], upper_matrix[i, j] = lower, upper
            lower_matrix[j, i], upper_matrix[j, i] = -upper, -lower
            bounds[f"{i}-{j}"] = {"lower": lower, "upper": upper}

    possible = []
    for winner in range(k):
        winner_rows = []
        for other in range(k):
            if other == winner:
                continue
            winner_rows.append(-target_contrast(k, contexts, winner, other))
        candidate_a = np.vstack((a, np.asarray(winner_rows)))
        candidate_b = np.concatenate((b, np.zeros(k - 1)))
        feasible = linprog(
            np.zeros(k * len(contexts)),
            A_ub=candidate_a,
            b_ub=candidate_b,
            bounds=[(None, None)] * (k * len(contexts)),
            method="highs",
        )
        if feasible.success:
            possible.append(winner)

    certified = [
        i
        for i in range(k)
        if all(i == j or lower_matrix[i, j] > 1e-10 for j in range(k))
    ]
    robust = minimax_lottery(k, contexts)
    return {
        "target_difference_bounds": bounds,
        "possible_winners": possible,
        "certified_unique_winners": certified,
        "minimax_lottery": robust["lottery"],
        "minimax_half_credit_regret": robust["regret"],
    }


def minimax_lottery(k: int, contexts: tuple[Context, ...]) -> dict[str, Any]:
    validate_contexts(k, contexts)
    systems = [context_constraints(k, context) for context in contexts]
    y_sizes = [len(b) for _, b in systems]
    p_start = 0
    t_index = k
    next_index = k + 1
    y_slices: dict[tuple[int, int], slice] = {}
    for winner in range(k):
        for c, size in enumerate(y_sizes):
            y_slices[(winner, c)] = slice(next_index, next_index + size)
            next_index += size

    objective = np.zeros(next_index)
    objective[t_index] = 1.0
    equalities = []
    equality_rhs = []
    simplex = np.zeros(next_index)
    simplex[p_start:k] = 1.0
    equalities.append(simplex)
    equality_rhs.append(1.0)

    for winner in range(k):
        for c, (a, _) in enumerate(systems):
            alpha = contexts[c].weight
            y_slice = y_slices[(winner, c)]
            for node in range(k):
                row = np.zeros(next_index)
                row[node] = alpha
                row[y_slice] = a[:, node]
                equalities.append(row)
                equality_rhs.append(alpha if node == winner else 0.0)

    inequalities = []
    inequality_rhs = []
    for winner in range(k):
        row = np.zeros(next_index)
        row[t_index] = -1.0
        for c, (_, b) in enumerate(systems):
            row[y_slices[(winner, c)]] = 0.5 * b
        inequalities.append(row)
        inequality_rhs.append(0.0)

    variable_bounds = [(0.0, 1.0)] * k + [(0.0, None)]
    variable_bounds += [(0.0, None)] * (next_index - k - 1)
    result = linprog(
        objective,
        A_ub=np.asarray(inequalities),
        b_ub=np.asarray(inequality_rhs),
        A_eq=np.asarray(equalities),
        b_eq=np.asarray(equality_rhs),
        bounds=variable_bounds,
        method="highs",
    )
    require(result.success, "minimax dual linear program failed")
    lottery = [0.0 if abs(value) < 1e-12 else float(value) for value in result.x[:k]]
    regret = float(result.x[t_index])
    return {"lottery": lottery, "regret": regret}


def hoeffding_difference_interval(
    mean_half_credit: float, n: int, edge_count: int, alpha: float
) -> tuple[float, float]:
    require(0 <= mean_half_credit <= 1, "mean outside [0,1]")
    require(n > 0 and edge_count > 0, "positive counts required")
    require(0 < alpha < 1, "alpha outside (0,1)")
    epsilon = math.sqrt(math.log(2 * edge_count / alpha) / (2 * n))
    lower_q = max(0.0, mean_half_credit - epsilon)
    upper_q = min(1.0, mean_half_credit + epsilon)
    return 2 * lower_q - 1, 2 * upper_q - 1


def known_answers() -> dict[str, Any]:
    h233 = (
        Context(0.5, ((0, 2), (1, 2)), (0.0, 0.0), (0.0, 0.0)),
        Context(0.5, ((0, 1),), (0.5,), (0.5,)),
    )
    connected = (
        Context(1.0, ((0, 1), (1, 2)), (0.3, 0.3), (0.3, 0.3)),
    )
    disconnected = (Context(1.0, ((0, 1),), (0.3,), (0.3,)),)
    wider = (
        Context(1.0, ((0, 1), (1, 2)), (0.2, 0.2), (0.4, 0.4)),
    )
    return {
        "h233_point_case": analyze(3, h233),
        "connected_point_case": analyze(3, connected),
        "disconnected_point_case": analyze(3, disconnected),
        "connected_wider_case": analyze(3, wider),
        "hoeffding_example": {
            "mean_half_credit": 0.65,
            "n": 100,
            "edge_count": 6,
            "alpha": 0.05,
            "difference_interval": list(
                hoeffding_difference_interval(0.65, 100, 6, 0.05)
            ),
        },
    }


def build_result() -> dict[str, Any]:
    result = {
        "schema": "h250-finite-sample-route-graph-v1",
        "protocol_sha256": sha256(PROTOCOL),
        "implementation_sha256": sha256(Path(__file__)),
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "known_answers": known_answers(),
        "coverage_scope": (
            "inherits only the joint coverage and sampling-unit validity of the supplied "
            "edge intervals; no public-system performance outcome analyzed"
        ),
    }
    validate_result(result)
    return result


def validate_result(result: dict[str, Any]) -> None:
    require(result.get("schema") == "h250-finite-sample-route-graph-v1", "schema mismatch")
    require(result.get("protocol_sha256") == sha256(PROTOCOL), "protocol hash mismatch")
    require(result.get("implementation_sha256") == sha256(Path(__file__)), "implementation hash mismatch")
    expected = known_answers()
    require(result.get("known_answers") == expected, "known-answer mismatch")
    h233 = expected["h233_point_case"]
    require(np.allclose(h233["minimax_lottery"], [2 / 3, 0, 1 / 3], atol=1e-9), "H233 lottery")
    require(abs(h233["minimax_half_credit_regret"] - 1 / 12) <= 1e-9, "H233 regret")
    require(expected["connected_point_case"]["certified_unique_winners"] == [0], "connected winner")
    require(expected["disconnected_point_case"]["certified_unique_winners"] == [], "disconnected certification")
    require(len(expected["disconnected_point_case"]["possible_winners"]) >= 2, "disconnected ambiguity")
    point = expected["connected_point_case"]["target_difference_bounds"]
    wide = expected["connected_wider_case"]["target_difference_bounds"]
    for key in point:
        require(wide[key]["lower"] <= point[key]["lower"] + 1e-10, "widening raised lower bound")
        require(wide[key]["upper"] >= point[key]["upper"] - 1e-10, "widening lowered upper bound")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        validate_result(json.loads(OUTPUT.read_text(encoding="utf-8")))
        return
    OUTPUT.write_text(json.dumps(build_result(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
