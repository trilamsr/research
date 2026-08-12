#!/usr/bin/env python3
"""H233 route-colored shared-success identification and minimax checks."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import linprog


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "protocol-h233-route-colored-shared-success.md"
OUTPUT = HERE / "result-h233-route-colored-shared-success.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def components(k: int, edges: tuple[tuple[int, int], ...]) -> list[list[int]]:
    adjacent = [set() for _ in range(k)]
    for i, j in edges:
        adjacent[i].add(j)
        adjacent[j].add(i)
    unseen = set(range(k))
    out: list[list[int]] = []
    while unseen:
        root = min(unseen)
        stack = [root]
        unseen.remove(root)
        group: list[int] = []
        while stack:
            node = stack.pop()
            group.append(node)
            for neighbor in sorted(adjacent[node] & unseen, reverse=True):
                unseen.remove(neighbor)
                stack.append(neighbor)
        out.append(sorted(group))
    return out


def incidence(k: int, edges: tuple[tuple[int, int], ...]) -> np.ndarray:
    matrix = np.zeros((len(edges), k), dtype=float)
    for row, (i, j) in enumerate(edges):
        matrix[row, i] = 1
        matrix[row, j] = -1
    return matrix


def graph_census() -> dict[str, int]:
    exhaustive_graphs = 0
    sampled_graphs = 0
    for k in range(3, 9):
        all_edges = tuple(itertools.combinations(range(k), 2))
        if k <= 6:
            masks = range(1 << len(all_edges))
        else:
            seed = np.random.default_rng(20260728 + k)
            masks = sorted(
                set(
                    [0, (1 << len(all_edges)) - 1]
                    + [
                        int(seed.integers(0, 1 << len(all_edges)))
                        for _ in range(2048)
                    ]
                )
            )
        for mask in masks:
            edges = tuple(
                edge for bit, edge in enumerate(all_edges) if mask & (1 << bit)
            )
            rank = int(np.linalg.matrix_rank(incidence(k, edges), tol=1e-10))
            expected = k - len(components(k, edges))
            if rank != expected:
                raise AssertionError((k, edges, rank, expected))
            if k <= 6:
                exhaustive_graphs += 1
            else:
                sampled_graphs += 1
    return {
        "exhaustive_graphs_k3_to_k6": exhaustive_graphs,
        "deterministic_sampled_graphs_k7_to_k8": sampled_graphs,
    }


def known_answer_vertices() -> list[tuple[Fraction, Fraction, Fraction]]:
    # B identifies x1-x2=1/2; x2 is in [0,1/2], while x3 is unconstrained.
    return [
        (b2 + Fraction(1, 2), b2, b3)
        for b2 in (Fraction(0), Fraction(1, 2))
        for b3 in (Fraction(0), Fraction(1))
    ]


def target_mu(b: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    # A has equal policy means, so its common offset cancels from regret.
    return tuple(Fraction(1, 2) * value for value in b)


def exact_regret(p: tuple[Fraction, ...]) -> Fraction:
    worst = Fraction(0)
    for b in known_answer_vertices():
        mu = target_mu(b)
        mixture = sum(pi * value for pi, value in zip(p, mu))
        for winner in range(3):
            worst = max(worst, Fraction(1, 2) * (mu[winner] - mixture))
    return worst


def numerical_minimax() -> tuple[np.ndarray, float]:
    # Variables p1,p2,p3,t. Each compatible vertex/winner supplies one row.
    a_ub: list[list[float]] = []
    b_ub: list[float] = []
    for b in known_answer_vertices():
        mu = np.array([float(value) for value in target_mu(b)])
        for winner in range(3):
            # .5 * (mu_w - p'mu) <= t
            a_ub.append(list(-0.5 * mu) + [-1.0])
            b_ub.append(-0.5 * mu[winner])
    result = linprog(
        c=[0.0, 0.0, 0.0, 1.0],
        A_ub=np.array(a_ub),
        b_ub=np.array(b_ub),
        A_eq=[[1.0, 1.0, 1.0, 0.0]],
        b_eq=[1.0],
        bounds=[(0.0, 1.0)] * 3 + [(0.0, None)],
        method="highs",
    )
    if not result.success:
        raise AssertionError(result.message)
    return result.x[:3], float(result.x[3])


def numerical_dual_minimax() -> tuple[np.ndarray, float]:
    """Solve protocol equation S4.8 for the H233 known-answer route graphs."""
    k = 3
    contexts = [
        (Fraction(1, 2), ((0, 2), (1, 2)), (Fraction(0), Fraction(0))),
        (Fraction(1, 2), ((0, 1),), (Fraction(1, 2),)),
    ]
    # p[0:3], t[3], then for every (winner, context): free lambdas and u>=0.
    cursor = 4
    blocks: dict[tuple[int, int], tuple[slice, slice]] = {}
    bounds: list[tuple[float | None, float | None]] = [(0, 1)] * k + [(0, None)]
    for winner in range(k):
        for context_index, (_, edges, _) in enumerate(contexts):
            lambda_slice = slice(cursor, cursor + len(edges))
            cursor += len(edges)
            bounds.extend([(None, None)] * len(edges))
            u_slice = slice(cursor, cursor + k)
            cursor += k
            bounds.extend([(0, None)] * k)
            blocks[(winner, context_index)] = (lambda_slice, u_slice)

    a_ub: list[np.ndarray] = []
    b_ub: list[float] = []
    for winner in range(k):
        regret_row = np.zeros(cursor)
        regret_row[3] = -1.0
        for context_index, (_, _, d) in enumerate(contexts):
            lambda_slice, u_slice = blocks[(winner, context_index)]
            regret_row[lambda_slice] = 0.5 * np.array([float(value) for value in d])
            regret_row[u_slice] = 0.5
        a_ub.append(regret_row)
        b_ub.append(0.0)

        for context_index, (alpha, edges, _) in enumerate(contexts):
            matrix = incidence(k, edges)
            lambda_slice, u_slice = blocks[(winner, context_index)]
            for policy in range(k):
                # -(E'lambda+u-alpha(e_w-p)) <= 0.
                row = np.zeros(cursor)
                row[policy] = -float(alpha)
                row[lambda_slice] = -matrix[:, policy]
                row[u_slice.start + policy] = -1.0
                rhs = -float(alpha) if policy == winner else 0.0
                a_ub.append(row)
                b_ub.append(rhs)

    objective = np.zeros(cursor)
    objective[3] = 1.0
    equality = np.zeros((1, cursor))
    equality[0, :k] = 1.0
    result = linprog(
        c=objective,
        A_ub=np.array(a_ub),
        b_ub=np.array(b_ub),
        A_eq=equality,
        b_eq=[1.0],
        bounds=bounds,
        method="highs",
    )
    if not result.success:
        raise AssertionError(result.message)
    return result.x[:k], float(result.x[3])


def build() -> dict[str, object]:
    census = graph_census()
    vertices = known_answer_vertices()
    proposed = (Fraction(2, 3), Fraction(0), Fraction(1, 3))
    exact_value = exact_regret(proposed)
    numeric_p, numeric_value = numerical_minimax()
    dual_p, dual_value = numerical_dual_minimax()
    if max(abs(numeric_p - np.array([2 / 3, 0, 1 / 3]))) > 1e-9:
        raise AssertionError(numeric_p)
    if abs(numeric_value - 1 / 12) > 1e-9:
        raise AssertionError(numeric_value)
    if max(abs(dual_p - numeric_p)) > 1e-9 or abs(dual_value - numeric_value) > 1e-9:
        raise AssertionError((dual_p, dual_value))

    low = target_mu((Fraction(1, 2), Fraction(0), Fraction(0)))
    high = target_mu((Fraction(1, 2), Fraction(0), Fraction(1)))
    if max(range(3), key=low.__getitem__) != 0:
        raise AssertionError("low endpoint winner changed")
    if max(range(3), key=high.__getitem__) != 2:
        raise AssertionError("high endpoint winner changed")

    return {
        "schema": "h233-route-colored-shared-success-v1",
        "status": "pass",
        "classification": "candidate_dependent_routing_can_leave_target_unidentified",
        "outcome_status": "review_triggered_outcome_exposed_exploratory",
        "protocol_sha256": sha256(PROTOCOL),
        "graph_rank_census": census,
        "theorem_boundary": {
            "connected_positive_weight_route_graphs": (
                "identify every within-context policy difference"
            ),
            "disconnected_route_graphs": (
                "retain component offsets when compatible bounds leave slack"
            ),
            "exact_test": (
                "all compatible target pair-difference widths equal zero"
            ),
        },
        "known_answer": {
            "k": 3,
            "target_weights": ["1/2", "1/2"],
            "routes": {"A": ["1-3", "2-3"], "B": ["1-2"]},
            "identified_differences": {"A": ["0", "0"], "B": ["1/2"]},
            "compatible_b_vertices": [
                [str(value) for value in vertex] for vertex in vertices
            ],
            "opposite_unique_winners": [1, 3],
            "exact_minimax_lottery": ["2/3", "0", "1/3"],
            "exact_minimax_regret": str(exact_value),
            "exact_regret_formula": (
                "max(1-p1, p1+2*p2, 2-2*p1-p2, p2)/8"
            ),
            "uniqueness_proof": (
                "max(p1+2*p2,2-2*p1-p2) is at least "
                "(2+p2)/3; equality requires p1+p2=2/3, "
                "and the bound is uniquely minimized at p2=0,p1=2/3"
            ),
            "numerical_minimax_lottery": [float(value) for value in numeric_p],
            "numerical_minimax_regret": numeric_value,
            "dual_lp_minimax_lottery": [float(value) for value in dual_p],
            "dual_lp_minimax_regret": dual_value,
        },
        "reference_distribution_cancels_from_regret": True,
        "dual_lp_recorded_in_protocol": True,
    }


def validate(data: dict[str, object]) -> None:
    if data != build():
        raise AssertionError("stored H233 result is stale")


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
        print("OK: H233 route-colored shared-success result")


if __name__ == "__main__":
    main()
