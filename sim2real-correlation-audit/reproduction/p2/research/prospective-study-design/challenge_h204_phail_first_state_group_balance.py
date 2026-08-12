#!/usr/bin/env python3
"""Independent SciPy/Philox challenge of H204 group balance."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import scipy
import scipy.linalg


FAMILY = Path(__file__).resolve().parent
COHORT = FAMILY / "result-h187-phail-context-support-sanitized.csv"
PROJECTION = FAMILY / "projection-h202-phail-initial-joint-state.csv"
PRODUCER = FAMILY / "result-h204-phail-first-state-group-balance.json"
OUTPUT = FAMILY / "result-h204-phail-first-state-group-balance-independent-challenge.json"
COHORT_SHA256 = "ad43fca1da065a1cb7fd84dfa9afc5691c72ebe12e7f165c68a0050e51e87ebe"
PROJECTION_SHA256 = "44b7cd9729c691a610cc1fbbefffc5668d31030e013b92f2d4550f9869020370"
PERMUTATIONS = 9_999
SEED_TEXT = "H204 independent SciPy Philox challenge v1"
SEED = int.from_bytes(hashlib.sha256(SEED_TEXT.encode()).digest()[:8], "big")
BASE = np.array([0.0, -0.31, 0.0, -1.65, 0.0, 1.522, 0.0])
SCALES = np.array([0.03, 0.05, 0.08, 0.08, 0.10, 0.10, 0.10]) / math.sqrt(3)
EXPECTED_CLASS = "no_material_group_mean_association_at_fixed_resolution"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load() -> tuple[np.ndarray, list[str], list[str]]:
    require(sha256(COHORT) == COHORT_SHA256, "cohort hash")
    require(sha256(PROJECTION) == PROJECTION_SHA256, "projection hash")
    cohort = read_csv(COHORT)
    projection = {row["episode_id"]: row for row in read_csv(PROJECTION)}
    require(len(cohort) == len(projection) == 594, "counts")
    states = []
    policy = []
    date = []
    for row in cohort:
        projected = projection[row["episode_id"]]
        require(projected["error"] == "0", "error")
        q = np.array([float(projected[f"q{joint}"]) for joint in range(7)])
        require(np.isfinite(q).all(), "finite")
        states.append((q - BASE) / SCALES)
        policy.append(row["policy_model"])
        date.append(row["utc_date"])
    return np.vstack(states), policy, date


def treatment(labels: list[str]) -> np.ndarray:
    levels = sorted(set(labels))
    return np.column_stack(
        [
            np.ones(len(labels)),
            *[
                np.array([float(label == level) for label in labels])
                for level in levels[1:]
            ],
        ]
    )


def designs(
    nuisance_labels: list[str] | None, factor_labels: list[str]
) -> tuple[np.ndarray, np.ndarray]:
    nuisance = (
        np.ones((len(factor_labels), 1))
        if nuisance_labels is None
        else treatment(nuisance_labels)
    )
    factor = treatment(factor_labels)
    full = np.column_stack([nuisance, factor[:, 1:]])
    require(
        np.linalg.matrix_rank(nuisance) == nuisance.shape[1]
        and np.linalg.matrix_rank(full) == full.shape[1],
        "rank",
    )
    return nuisance, full


def groups(labels: list[str] | None, count: int) -> list[np.ndarray]:
    if labels is None:
        return [np.arange(count)]
    grouped: dict[str, list[int]] = defaultdict(list)
    for index, label in enumerate(labels):
        grouped[label].append(index)
    return [np.array(grouped[label]) for label in sorted(grouped)]


def solve(design: np.ndarray, outcomes: np.ndarray) -> tuple[np.ndarray, float]:
    coefficients = scipy.linalg.lstsq(
        design, outcomes, lapack_driver="gelsy"
    )[0]
    residual = outcomes - design @ coefficients
    return residual, float(np.square(residual).sum())


def analyze(
    outcomes: np.ndarray,
    nuisance_labels: list[str] | None,
    factor_labels: list[str],
    stratum_labels: list[str] | None,
    rng: np.random.Generator,
) -> dict[str, Any]:
    nuisance, full = designs(nuisance_labels, factor_labels)
    reduced_residual, reduced_sse = solve(nuisance, outcomes)
    _, full_sse = solve(full, outcomes)
    observed = (reduced_sse - full_sse) / reduced_sse
    added = full[:, nuisance.shape[1] :]
    nuisance_coefficients = scipy.linalg.lstsq(
        nuisance, added, lapack_driver="gelsy"
    )[0]
    residualized_added = added - nuisance @ nuisance_coefficients
    basis, _, pivot = scipy.linalg.qr(
        residualized_added, mode="economic", pivoting=True
    )
    rank = np.linalg.matrix_rank(residualized_added)
    require(rank == residualized_added.shape[1], "effect rank")
    basis = basis[:, :rank]
    direct = float(np.square(basis.T @ reduced_residual).sum() / reduced_sse)
    require(math.isclose(observed, direct, abs_tol=1e-12), "observed paths")
    strata = groups(stratum_labels, len(outcomes))
    null = np.empty(PERMUTATIONS)
    for repetition in range(PERMUTATIONS):
        order = np.arange(len(outcomes))
        for group in strata:
            order[group] = rng.permutation(group)
        projected = basis.T @ reduced_residual[order]
        null[repetition] = float(np.square(projected).sum() / reduced_sse)
    upper = (int(np.count_nonzero(null >= observed)) + 1) / (PERMUTATIONS + 1)
    return {
        "observed_partial_r2": observed,
        "permutation_median": float(np.quantile(null, 0.5)),
        "permutation_q025": float(np.quantile(null, 0.025)),
        "permutation_q975": float(np.quantile(null, 0.975)),
        "upper_tail_p": upper,
        "permutations": PERMUTATIONS,
        "factor_degrees_of_freedom": int(rank),
        "stratum_count": len(strata),
    }


def classify(analyses: dict[str, dict[str, Any]]) -> str:
    policy = analyses["policy_conditional_on_date"]
    date = analyses["date_conditional_on_policy"]
    unadjusted = analyses["policy_unadjusted"]
    if policy["upper_tail_p"] <= 0.01 and policy["observed_partial_r2"] >= 0.02:
        return "material_policy_initial_state_association"
    if date["upper_tail_p"] <= 0.01 and date["observed_partial_r2"] >= 0.02:
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
    return EXPECTED_CLASS


def build() -> dict[str, Any]:
    outcomes, policy, date = load()
    rng = np.random.Generator(np.random.Philox(SEED))
    analyses = {
        "policy_conditional_on_date": analyze(
            outcomes, date, policy, date, rng
        ),
        "date_conditional_on_policy": analyze(
            outcomes, policy, date, policy, rng
        ),
        "policy_unadjusted": analyze(
            outcomes, None, policy, None, rng
        ),
    }
    producer = json.loads(PRODUCER.read_text())
    maximum_difference = max(
        abs(
            analyses[key]["observed_partial_r2"]
            - producer["analyses"][key]["observed_partial_r2"]
        )
        for key in analyses
    )
    classification = classify(analyses)
    require(maximum_difference <= 1e-12, "observed difference")
    require(classification == producer["classification"], "classification")
    return {
        "schema": "h204-scipy-philox-independent-challenge-v1",
        "scipy_version": scipy.__version__,
        "producer_result_sha256": sha256(PRODUCER),
        "cohort_sha256": sha256(COHORT),
        "projection_sha256": sha256(PROJECTION),
        "method": (
            "independent SciPy GELSY/QR-with-pivoting solver and Philox "
            "stratum-residual permutation stream"
        ),
        "seed_text": SEED_TEXT,
        "analyses": analyses,
        "maximum_observed_r2_difference": maximum_difference,
        "producer_classification": producer["classification"],
        "independent_classification": classification,
        "later_state_or_outcome_opened": False,
        "full_physical_balance_established": False,
        "result": "pass",
    }


def validate(result: dict[str, Any]) -> None:
    require(result["schema"] == "h204-scipy-philox-independent-challenge-v1", "schema")
    require(result["producer_result_sha256"] == sha256(PRODUCER), "producer")
    require(result["cohort_sha256"] == COHORT_SHA256, "cohort")
    require(result["projection_sha256"] == PROJECTION_SHA256, "projection")
    require(result["maximum_observed_r2_difference"] <= 1e-12, "difference")
    require(result["producer_classification"] == EXPECTED_CLASS, "producer class")
    require(result["independent_classification"] == EXPECTED_CLASS, "challenge class")
    require(result["later_state_or_outcome_opened"] is False, "scope")
    require(result["full_physical_balance_established"] is False, "balance")
    require(result["result"] == "pass", "result")


def main() -> None:
    candidate = build()
    validate(candidate)
    OUTPUT.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n")
    print(json.dumps(candidate, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
