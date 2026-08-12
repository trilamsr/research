#!/usr/bin/env python3
"""Independent SciPy/Philox challenge of H205 uniform independence."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import scipy
import scipy.stats


FAMILY = Path(__file__).resolve().parent
PROJECTION = FAMILY / "projection-h202-phail-initial-joint-state.csv"
PRODUCER = FAMILY / "result-h205-phail-first-state-uniform-independence.json"
OUTPUT = (
    FAMILY
    / "result-h205-phail-first-state-uniform-independence-independent-challenge.json"
)
PROJECTION_SHA256 = "44b7cd9729c691a610cc1fbbefffc5668d31030e013b92f2d4550f9869020370"
PRODUCER_SHA256 = "9bbdc9415f8d76717a08911852861579d54b75c4a7f9e50b26e3f893a1fbedf7"
EXPECTED_EPISODES = 594
SIMULATIONS = 49_999
BATCH_SIZE = 64
SEED_TEXT = "H205 independent SciPy Philox challenge v1"
SEED = int.from_bytes(hashlib.sha256(SEED_TEXT.encode()).digest()[:16], "big")
BASE = np.array([0.0, -0.31, 0.0, -1.65, 0.0, 1.522, 0.0])
HALF_WIDTHS = np.array([0.03, 0.05, 0.08, 0.08, 0.10, 0.10, 0.10])


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load() -> np.ndarray:
    require(sha256(PROJECTION) == PROJECTION_SHA256, "projection hash")
    with PROJECTION.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    require(len(rows) == EXPECTED_EPISODES, "episode count")
    require(len({row["episode_id"] for row in rows}) == len(rows), "identity")
    states = []
    for row in rows:
        require(row["error"] == "0", "error")
        q = np.array([float(row[f"q{joint}"]) for joint in range(7)])
        require(np.isfinite(q).all(), "finite")
        states.append((q - BASE) / HALF_WIDTHS)
    return np.vstack(states)


def observed_statistics(states: np.ndarray) -> tuple[list[float], float, list[float], float]:
    ks = [
        float(
            scipy.stats.kstest(
                states[:, joint], "uniform", args=(-1.0, 2.0), method="exact"
            ).statistic
        )
        for joint in range(7)
    ]
    correlations = [
        float(scipy.stats.pearsonr(states[:, first], states[:, second]).statistic)
        for first in range(7)
        for second in range(first + 1, 7)
    ]
    return ks, max(ks), correlations, max(abs(value) for value in correlations)


def independent_reference(
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    maximum_ks = np.empty(SIMULATIONS)
    maximum_correlation = np.empty(SIMULATIONS)
    completed = 0
    empirical_upper = np.arange(1, EXPECTED_EPISODES + 1) / EXPECTED_EPISODES
    empirical_lower = np.arange(EXPECTED_EPISODES) / EXPECTED_EPISODES
    upper_triangle = np.triu_indices(7, 1)
    while completed < SIMULATIONS:
        batch = min(BATCH_SIZE, SIMULATIONS - completed)
        samples = rng.uniform(-1.0, 1.0, size=(batch, EXPECTED_EPISODES, 7))
        ordered_cdf = (np.sort(samples, axis=1) + 1.0) / 2.0
        d_positive = np.max(
            empirical_upper[None, :, None] - ordered_cdf, axis=1
        )
        d_negative = np.max(
            ordered_cdf - empirical_lower[None, :, None], axis=1
        )
        maximum_ks[completed : completed + batch] = np.max(
            np.maximum(d_positive, d_negative), axis=1
        )

        centered = samples - np.mean(samples, axis=1, keepdims=True)
        covariance_numerator = np.swapaxes(centered, 1, 2) @ centered
        sum_squares = np.diagonal(
            covariance_numerator, axis1=1, axis2=2
        )
        correlation = covariance_numerator / np.sqrt(
            sum_squares[:, :, None] * sum_squares[:, None, :]
        )
        maximum_correlation[completed : completed + batch] = np.max(
            np.abs(correlation[:, upper_triangle[0], upper_triangle[1]]), axis=1
        )
        completed += batch
    return maximum_ks, maximum_correlation


def upper_tail_p(observed: float, reference: np.ndarray) -> float:
    return (int(np.count_nonzero(reference >= observed)) + 1) / (
        len(reference) + 1
    )


def classify(
    marginal_observed: float,
    marginal_p: float,
    dependence_observed: float,
    dependence_p: float,
) -> str:
    marginal_significant = marginal_p <= 0.01
    dependence_significant = dependence_p <= 0.01
    marginal_material = marginal_significant and marginal_observed >= 0.08
    dependence_material = (
        dependence_significant and dependence_observed >= 0.15
    )
    if marginal_material and dependence_material:
        return "material_marginal_and_joint_departure"
    if marginal_material:
        return "material_marginal_departure_only"
    if dependence_material:
        return "material_joint_dependence_only"
    if marginal_significant or dependence_significant:
        return "small_or_diagnostic_only_departure"
    return "no_material_uniform_independence_departure_at_fixed_resolution"


def build() -> dict[str, Any]:
    require(sha256(PRODUCER) == PRODUCER_SHA256, "producer hash")
    producer = json.loads(PRODUCER.read_text())
    states = load()
    ks, maximum_ks, correlations, maximum_correlation = observed_statistics(
        states
    )
    reference_ks, reference_correlation = independent_reference(
        np.random.Generator(np.random.Philox(SEED))
    )
    marginal_p = upper_tail_p(maximum_ks, reference_ks)
    dependence_p = upper_tail_p(maximum_correlation, reference_correlation)
    classification = classify(
        maximum_ks, marginal_p, maximum_correlation, dependence_p
    )
    producer_ks = producer["marginal_uniformity"]["observed"]
    producer_correlation = producer["joint_dependence"]["observed"]
    maximum_observed_difference = max(
        abs(maximum_ks - producer_ks),
        abs(maximum_correlation - producer_correlation),
    )
    producer_support = producer["support_diagnostic"]
    outside = np.abs(states) > 1.0
    maximum_exceedance = float(
        np.maximum(np.abs(states) - 1.0, 0.0).max()
    )
    require(maximum_observed_difference <= 1e-12, "observed difference")
    require(
        int(outside.sum()) == producer_support["total_outside_count"],
        "support count",
    )
    require(
        abs(
            maximum_exceedance
            - producer_support["maximum_absolute_exceedance"]
        )
        <= 1e-15,
        "support exceedance",
    )
    require(classification == producer["classification"], "classification")
    return {
        "schema": "h205-scipy-philox-independent-challenge-v1",
        "scipy_version": scipy.__version__,
        "producer_result_sha256": sha256(PRODUCER),
        "projection_sha256": sha256(PROJECTION),
        "method": (
            "independent SciPy exact one-sample KS and Pearson statistics "
            "with a separate Philox complete-reference stream"
        ),
        "seed_text": SEED_TEXT,
        "simulations": SIMULATIONS,
        "per_joint_ks_distance": ks,
        "maximum_ks_distance": maximum_ks,
        "marginal_upper_tail_p": marginal_p,
        "pairwise_correlations": correlations,
        "maximum_absolute_correlation": maximum_correlation,
        "dependence_upper_tail_p": dependence_p,
        "support_total_outside_count": int(outside.sum()),
        "support_maximum_absolute_exceedance": maximum_exceedance,
        "maximum_observed_statistic_difference": maximum_observed_difference,
        "producer_classification": producer["classification"],
        "independent_classification": classification,
        "commanded_draw_or_rng_validity_established": False,
        "later_state_or_outcome_opened": False,
        "result": "pass",
    }


def validate(result: dict[str, Any]) -> None:
    producer = json.loads(PRODUCER.read_text())
    require(
        result["schema"] == "h205-scipy-philox-independent-challenge-v1",
        "schema",
    )
    require(result["producer_result_sha256"] == sha256(PRODUCER), "producer")
    require(result["projection_sha256"] == PROJECTION_SHA256, "projection")
    require(result["simulations"] == SIMULATIONS, "simulations")
    require(
        result["maximum_observed_statistic_difference"] <= 1e-12,
        "difference",
    )
    require(
        result["producer_classification"] == producer["classification"],
        "producer class",
    )
    require(
        result["independent_classification"] == producer["classification"],
        "challenge class",
    )
    require(
        result["commanded_draw_or_rng_validity_established"] is False,
        "commanded scope",
    )
    require(result["later_state_or_outcome_opened"] is False, "later scope")
    require(result["result"] == "pass", "result")


def main() -> None:
    candidate = build()
    validate(candidate)
    OUTPUT.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n")
    print(json.dumps(candidate, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
