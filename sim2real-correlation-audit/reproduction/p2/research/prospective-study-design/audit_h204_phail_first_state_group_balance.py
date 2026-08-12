#!/usr/bin/env python3
"""Fixed H204 achieved-first-state policy/date balance audit."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np


FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h204-phail-first-state-group-balance.md"
COHORT = FAMILY / "result-h187-phail-context-support-sanitized.csv"
PROJECTION = FAMILY / "projection-h202-phail-initial-joint-state.csv"
H202_RESULT = FAMILY / "result-h202-phail-initial-joint-state.json"
H203_RESULT = FAMILY / "result-h203-phail-first-state-temporal-structure.json"
OUTPUT = FAMILY / "result-h204-phail-first-state-group-balance.json"
COHORT_SHA256 = "ad43fca1da065a1cb7fd84dfa9afc5691c72ebe12e7f165c68a0050e51e87ebe"
PROJECTION_SHA256 = "44b7cd9729c691a610cc1fbbefffc5668d31030e013b92f2d4550f9869020370"
H202_SHA256 = "4e60b6c6cbc0eabcaf4ae7761119b5af89bbaf6707e53cce8f0ec3c227a96043"
H203_SHA256 = "5f30b36135feaf85fc32b2f3fe5f2ad2f5c5e8188ca777131b8154d3db111cda"
EXPECTED_EPISODES = 594
PERMUTATIONS = 49_999
BATCH_SIZE = 128
SEED_TEXT = "H204 PhAIL first-state group balance v1"
SEED = int.from_bytes(hashlib.sha256(SEED_TEXT.encode()).digest()[:16], "big")
BASE = np.array([0.0, -0.31, 0.0, -1.65, 0.0, 1.522, 0.0])
HALF_WIDTHS = np.array([0.03, 0.05, 0.08, 0.08, 0.10, 0.10, 0.10])
SCALES = HALF_WIDTHS / math.sqrt(3)
CLASSIFICATIONS = {
    "material_policy_initial_state_association",
    "material_date_initial_state_association_only",
    "small_or_diagnostic_only_group_association",
    "no_material_group_mean_association_at_fixed_resolution",
    "input_drift_or_integrity_failure",
    "compute_integrity_failure",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_join() -> list[dict[str, Any]]:
    require(sha256(COHORT) == COHORT_SHA256, "cohort hash")
    require(sha256(PROJECTION) == PROJECTION_SHA256, "projection hash")
    require(sha256(H202_RESULT) == H202_SHA256, "H202 hash")
    require(sha256(H203_RESULT) == H203_SHA256, "H203 hash")
    cohort = read_csv(COHORT)
    projection = read_csv(PROJECTION)
    require(len(cohort) == EXPECTED_EPISODES, "cohort count")
    require(len(projection) == EXPECTED_EPISODES, "projection count")
    by_episode = {row["episode_id"]: row for row in projection}
    require(len(by_episode) == EXPECTED_EPISODES, "projection identity")
    require(set(by_episode) == {row["episode_id"] for row in cohort}, "join")
    rows = []
    for row in cohort:
        projected = by_episode[row["episode_id"]]
        q = np.array([float(projected[f"q{joint}"]) for joint in range(7)])
        require(np.isfinite(q).all(), "finite state")
        require(int(projected["error"]) == 0, "first error")
        rows.append(
            {
                "episode_id": row["episode_id"],
                "policy": row["policy_model"],
                "date": row["utc_date"],
                "q": q,
            }
        )
    return rows


def treatment_matrix(labels: list[str]) -> tuple[np.ndarray, list[str]]:
    levels = sorted(set(labels))
    require(len(levels) >= 2, "factor levels")
    matrix = np.column_stack(
        [
            np.ones(len(labels)),
            *[
                np.array([float(label == level) for label in labels])
                for level in levels[1:]
            ],
        ]
    )
    require(np.linalg.matrix_rank(matrix) == matrix.shape[1], "factor rank")
    return matrix, levels


def combined_matrix(
    nuisance_labels: list[str] | None,
    factor_labels: list[str],
) -> tuple[np.ndarray, np.ndarray, int, int]:
    if nuisance_labels is None:
        nuisance = np.ones((len(factor_labels), 1))
        nuisance_rank = 1
    else:
        nuisance, _ = treatment_matrix(nuisance_labels)
        nuisance_rank = nuisance.shape[1]
    factor, _ = treatment_matrix(factor_labels)
    full = np.column_stack([nuisance, factor[:, 1:]])
    full_rank = np.linalg.matrix_rank(full)
    require(full_rank == full.shape[1], "full design rank")
    return nuisance, full, nuisance_rank, full_rank


def strata_indices(labels: list[str] | None, count: int) -> list[np.ndarray]:
    if labels is None:
        return [np.arange(count, dtype=np.int64)]
    grouped: dict[str, list[int]] = defaultdict(list)
    for index, label in enumerate(labels):
        grouped[label].append(index)
    return [
        np.array(grouped[label], dtype=np.int64)
        for label in sorted(grouped)
    ]


def fit(design: np.ndarray, outcomes: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    coefficients = np.linalg.lstsq(design, outcomes, rcond=None)[0]
    fitted = design @ coefficients
    residual = outcomes - fitted
    return fitted, residual, float(np.square(residual).sum())


def effect_basis(nuisance: np.ndarray, full: np.ndarray) -> np.ndarray:
    factor = full[:, nuisance.shape[1] :]
    nuisance_fit = nuisance @ np.linalg.lstsq(nuisance, factor, rcond=None)[0]
    residualized = factor - nuisance_fit
    rank = np.linalg.matrix_rank(residualized)
    require(rank == residualized.shape[1], "effect rank")
    q, _ = np.linalg.qr(residualized, mode="reduced")
    return q[:, :rank]


def observed_partial_r2(
    nuisance: np.ndarray, full: np.ndarray, outcomes: np.ndarray
) -> float:
    _, _, reduced_sse = fit(nuisance, outcomes)
    _, _, full_sse = fit(full, outcomes)
    require(reduced_sse > 0, "reduced SSE")
    value = (reduced_sse - full_sse) / reduced_sse
    require(-1e-12 <= value <= 1 + 1e-12, "partial R2")
    return max(0.0, value)


def permuted_partial_r2(
    outcomes: np.ndarray,
    nuisance: np.ndarray,
    full: np.ndarray,
    strata: list[np.ndarray],
    permutations: int,
    rng: np.random.Generator,
) -> tuple[float, np.ndarray]:
    _, residual, reduced_sse = fit(nuisance, outcomes)
    basis = effect_basis(nuisance, full)
    observed = float(np.square(basis.T @ residual).sum() / reduced_sse)
    output = np.empty(permutations, dtype=np.float64)
    count = len(outcomes)
    cursor = 0
    while cursor < permutations:
        batch = min(BATCH_SIZE, permutations - cursor)
        indices = np.empty((batch, count), dtype=np.int64)
        for repetition in range(batch):
            indices[repetition] = np.arange(count)
            for group in strata:
                indices[repetition, group] = rng.permutation(group)
        permuted = residual[indices]
        projected = np.einsum("nk,bnj->bkj", basis, permuted, optimize=True)
        output[cursor : cursor + batch] = (
            np.square(projected).sum(axis=(1, 2)) / reduced_sse
        )
        cursor += batch
    require(np.isfinite(output).all(), "finite permutations")
    return observed, output


def analyze(
    outcomes: np.ndarray,
    nuisance_labels: list[str] | None,
    factor_labels: list[str],
    stratum_labels: list[str] | None,
    permutations: int,
    rng: np.random.Generator,
) -> dict[str, Any]:
    nuisance, full, nuisance_rank, full_rank = combined_matrix(
        nuisance_labels, factor_labels
    )
    strata = strata_indices(stratum_labels, len(outcomes))
    observed, null = permuted_partial_r2(
        outcomes, nuisance, full, strata, permutations, rng
    )
    direct = observed_partial_r2(nuisance, full, outcomes)
    require(math.isclose(observed, direct, rel_tol=0, abs_tol=1e-12), "R2 paths")
    upper = (int(np.count_nonzero(null >= observed)) + 1) / (permutations + 1)
    return {
        "observed_partial_r2": observed,
        "permutation_median": float(np.quantile(null, 0.50, method="linear")),
        "permutation_q025": float(np.quantile(null, 0.025, method="linear")),
        "permutation_q975": float(np.quantile(null, 0.975, method="linear")),
        "upper_tail_p": upper,
        "nuisance_rank": int(nuisance_rank),
        "full_rank": int(full_rank),
        "factor_degrees_of_freedom": int(full_rank - nuisance_rank),
        "factor_group_count": len(set(factor_labels)),
        "stratum_count": len(strata),
        "permutations": permutations,
    }


def group_spans(
    rows: list[dict[str, Any]], states: np.ndarray, key: str
) -> dict[str, Any]:
    groups: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        groups[row[key]].append(index)
    means = np.vstack(
        [states[groups[label]].mean(axis=0) for label in sorted(groups)]
    )
    standardized = means.max(axis=0) - means.min(axis=0)
    return {
        "group_count": len(groups),
        "maximum_group_mean_span_standardized": standardized.tolist(),
        "maximum_group_mean_span_rad": (standardized * SCALES).tolist(),
    }


def classify(analyses: dict[str, dict[str, Any]]) -> str:
    policy = analyses["policy_conditional_on_date"]
    date = analyses["date_conditional_on_policy"]
    unadjusted = analyses["policy_unadjusted"]
    policy_material = policy["upper_tail_p"] <= 0.01 and policy["observed_partial_r2"] >= 0.02
    date_material = date["upper_tail_p"] <= 0.01 and date["observed_partial_r2"] >= 0.02
    if policy_material:
        return "material_policy_initial_state_association"
    if date_material:
        return "material_date_initial_state_association_only"
    if (
        policy["upper_tail_p"] <= 0.01
        or date["upper_tail_p"] <= 0.01
        or (
            unadjusted["upper_tail_p"] <= 0.01
            and unadjusted["observed_partial_r2"] >= 0.02
        )
    ):
        return "small_or_diagnostic_only_group_association"
    return "no_material_group_mean_association_at_fixed_resolution"


def synthetic_controls() -> dict[str, bool]:
    policy = ["a"] * 20 + ["b"] * 20
    date = ["x", "y"] * 20
    policy_code = np.array([label == "b" for label in policy], dtype=float)
    date_code = np.array([label == "y" for label in date], dtype=float)
    base_noise = np.random.default_rng(204).normal(scale=0.05, size=(40, 7))
    policy_shift = base_noise + policy_code[:, None]
    date_shift = base_noise + date_code[:, None]
    additive = base_noise + policy_code[:, None] + 2 * date_code[:, None]
    n_policy, f_policy, _, _ = combined_matrix(date, policy)
    n_date, f_date, _, _ = combined_matrix(policy, date)
    null_rng_a = np.random.Generator(np.random.PCG64(SEED))
    null_rng_b = np.random.Generator(np.random.PCG64(SEED))
    replay_a = permuted_partial_r2(
        base_noise, n_policy, f_policy, strata_indices(date, 40), 99, null_rng_a
    )[1]
    replay_b = permuted_partial_r2(
        base_noise, n_policy, f_policy, strata_indices(date, 40), 99, null_rng_b
    )[1]
    collinear_failed = False
    try:
        combined_matrix(policy, policy)
    except ValueError:
        collinear_failed = True
    return {
        "policy_shift_detected": observed_partial_r2(
            n_policy, f_policy, policy_shift
        )
        > 0.9,
        "date_shift_detected": observed_partial_r2(n_date, f_date, date_shift)
        > 0.9,
        "additive_both_detected": (
            observed_partial_r2(n_policy, f_policy, additive) > 0.15
            and observed_partial_r2(n_date, f_date, additive) > 0.6
        ),
        "balanced_null_small": observed_partial_r2(
            n_policy, f_policy, base_noise
        )
        < 0.1,
        "deterministic_replay": np.array_equal(replay_a, replay_b),
        "collinearity_rejected": collinear_failed,
    }


def staged_validation(rows: list[dict[str, Any]]) -> dict[str, Any]:
    controls = synthetic_controls()
    require(all(controls.values()), "synthetic controls")
    policy = [row["policy"] for row in rows]
    date = [row["date"] for row in rows]
    combined_matrix(date, policy)
    combined_matrix(policy, date)
    combined_matrix(None, policy)
    rng = np.random.Generator(np.random.PCG64(SEED))
    synthetic = np.random.default_rng(205).normal(size=(len(rows), 7))
    started = time.monotonic()
    analyze(synthetic, date, policy, date, 999, rng)
    analyze(synthetic, policy, date, policy, 999, rng)
    analyze(synthetic, None, policy, None, 999, rng)
    return {
        "controls": controls,
        "episode_count": len(rows),
        "policy_group_count": len(set(policy)),
        "utc_date_group_count": len(set(date)),
        "date_stratum_policy_level_counts": sorted(
            len({policy[i] for i, value in enumerate(date) if value == label})
            for label in set(date)
        ),
        "policy_stratum_date_level_counts": sorted(
            len({date[i] for i, value in enumerate(policy) if value == label})
            for label in set(policy)
        ),
        "synthetic_999_per_analysis_elapsed_seconds": time.monotonic() - started,
    }


def build() -> dict[str, Any]:
    rows = load_join()
    controls = synthetic_controls()
    require(all(controls.values()), "synthetic controls")
    outcomes = (np.vstack([row["q"] for row in rows]) - BASE) / SCALES
    policy = [row["policy"] for row in rows]
    date = [row["date"] for row in rows]
    rng = np.random.Generator(np.random.PCG64(SEED))
    analyses = {
        "policy_conditional_on_date": analyze(
            outcomes, date, policy, date, PERMUTATIONS, rng
        ),
        "date_conditional_on_policy": analyze(
            outcomes, policy, date, policy, PERMUTATIONS, rng
        ),
        "policy_unadjusted": analyze(
            outcomes, None, policy, None, PERMUTATIONS, rng
        ),
    }
    return {
        "schema": "h204-phail-first-state-group-balance-v1",
        "protocol_sha256": sha256(PROTOCOL),
        "cohort_sha256": sha256(COHORT),
        "h202_projection_sha256": sha256(PROJECTION),
        "h202_result_sha256": sha256(H202_RESULT),
        "h203_result_sha256": sha256(H203_RESULT),
        "episode_count": len(rows),
        "seed_text": SEED_TEXT,
        "pcg64_seed": str(SEED),
        "rng_stream_order": [
            "policy_conditional_on_date",
            "date_conditional_on_policy",
            "policy_unadjusted",
        ],
        "synthetic_controls": controls,
        "analyses": analyses,
        "diagnostics": {
            "policy_group_mean_spans": group_spans(rows, outcomes, "policy"),
            "utc_date_group_mean_spans": group_spans(rows, outcomes, "date"),
        },
        "classification": classify(analyses),
        "later_state_or_outcome_opened": False,
        "causal_or_assignment_effect_established": False,
        "full_physical_balance_established": False,
        "decision_consequence": (
            "The fixed audit can identify material policy-linked initial-arm "
            "imbalance or date-linked drift. A null supports only seven-joint "
            "mean balance at this resolution and cannot establish assignment, "
            "exchangeability, or full physical-context balance."
        ),
    }


def validate(result: dict[str, Any]) -> None:
    require(result["schema"] == "h204-phail-first-state-group-balance-v1", "schema")
    require(result["protocol_sha256"] == sha256(PROTOCOL), "protocol")
    require(result["cohort_sha256"] == COHORT_SHA256, "cohort")
    require(result["h202_projection_sha256"] == PROJECTION_SHA256, "projection")
    require(result["h202_result_sha256"] == H202_SHA256, "H202")
    require(result["h203_result_sha256"] == H203_SHA256, "H203")
    require(result["episode_count"] == EXPECTED_EPISODES, "episodes")
    require(result["pcg64_seed"] == str(SEED), "seed")
    require(all(result["synthetic_controls"].values()), "controls")
    analyses = result["analyses"]
    require(
        set(analyses)
        == {
            "policy_conditional_on_date",
            "date_conditional_on_policy",
            "policy_unadjusted",
        },
        "analyses",
    )
    for analysis in analyses.values():
        require(analysis["permutations"] == PERMUTATIONS, "permutations")
        require(0 < analysis["upper_tail_p"] <= 1, "p value")
        require(0 <= analysis["observed_partial_r2"] <= 1, "R2")
        require(analysis["full_rank"] > analysis["nuisance_rank"], "ranks")
    require(result["classification"] == classify(analyses), "classification")
    require(result["classification"] in CLASSIFICATIONS, "class value")
    require(result["later_state_or_outcome_opened"] is False, "scope")
    require(result["causal_or_assignment_effect_established"] is False, "causal scope")
    require(result["full_physical_balance_established"] is False, "balance scope")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    require(not (args.stage and args.check), "choose one mode")
    if args.stage:
        print(json.dumps(staged_validation(load_join()), indent=2, sort_keys=True))
        return
    candidate = build()
    validate(candidate)
    if args.check:
        require(candidate == json.loads(OUTPUT.read_text()), "exact rebuild")
        print("OK: H204 first-state group-balance result reproduces")
    else:
        OUTPUT.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n")
        print(json.dumps(candidate, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
