#!/usr/bin/env python3
"""Fixed H205 achieved-first-state uniformity/independence audit."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import time
from pathlib import Path
from typing import Any

import numpy as np


FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h205-phail-first-state-uniform-independence.md"
PROJECTION = FAMILY / "projection-h202-phail-initial-joint-state.csv"
H202 = FAMILY / "result-h202-phail-initial-joint-state.json"
H203 = FAMILY / "result-h203-phail-first-state-temporal-structure.json"
H204 = FAMILY / "result-h204-phail-first-state-group-balance.json"
OUTPUT = FAMILY / "result-h205-phail-first-state-uniform-independence.json"
PROJECTION_SHA256 = "44b7cd9729c691a610cc1fbbefffc5668d31030e013b92f2d4550f9869020370"
H202_SHA256 = "4e60b6c6cbc0eabcaf4ae7761119b5af89bbaf6707e53cce8f0ec3c227a96043"
H203_SHA256 = "5f30b36135feaf85fc32b2f3fe5f2ad2f5c5e8188ca777131b8154d3db111cda"
H204_SHA256 = "d03aba1badedfe0c64bdd03be74c6e1134c331fc496a012f38ec35a048a812aa"
EXPECTED_EPISODES = 594
PERMUTATIONS = 49_999
BATCH_SIZE = 64
SEED_TEXT = "H205 PhAIL first-state uniform independence v1"
SEED = int.from_bytes(hashlib.sha256(SEED_TEXT.encode()).digest()[:16], "big")
BASE = np.array([0.0, -0.31, 0.0, -1.65, 0.0, 1.522, 0.0])
HALF_WIDTHS = np.array([0.03, 0.05, 0.08, 0.08, 0.10, 0.10, 0.10])
CLASSIFICATIONS = {
    "material_marginal_and_joint_departure",
    "material_marginal_departure_only",
    "material_joint_dependence_only",
    "small_or_diagnostic_only_departure",
    "no_material_uniform_independence_departure_at_fixed_resolution",
    "input_drift_or_integrity_failure",
    "compute_integrity_failure",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_states() -> np.ndarray:
    require(sha256(PROJECTION) == PROJECTION_SHA256, "projection hash")
    require(sha256(H202) == H202_SHA256, "H202 hash")
    require(sha256(H203) == H203_SHA256, "H203 hash")
    require(sha256(H204) == H204_SHA256, "H204 hash")
    with PROJECTION.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    require(len(rows) == EXPECTED_EPISODES, "episode count")
    require(len({row["episode_id"] for row in rows}) == len(rows), "identity")
    states = []
    for row in rows:
        require(int(row["error"]) == 0, "first error")
        q = np.array([float(row[f"q{joint}"]) for joint in range(7)])
        require(np.isfinite(q).all(), "finite")
        states.append((q - BASE) / HALF_WIDTHS)
    return np.vstack(states)


def ks_per_joint(states: np.ndarray) -> np.ndarray:
    require(states.ndim == 2 and states.shape[1] == 7, "state shape")
    ordered = np.sort(states, axis=0)
    cdf = np.clip((ordered + 1.0) / 2.0, 0.0, 1.0)
    count = len(states)
    upper_empirical = np.arange(1, count + 1)[:, None] / count
    lower_empirical = np.arange(count)[:, None] / count
    d_plus = np.max(upper_empirical - cdf, axis=0)
    d_minus = np.max(cdf - lower_empirical, axis=0)
    return np.maximum(d_plus, d_minus)


def correlation_diagnostics(states: np.ndarray) -> tuple[np.ndarray, float]:
    correlation = np.corrcoef(states, rowvar=False)
    require(np.isfinite(correlation).all(), "finite correlation")
    pairs = correlation[np.triu_indices(7, 1)]
    return pairs, float(np.max(np.abs(pairs)))


def simulated_omnibus(
    simulations: int, rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray]:
    ks_values = np.empty(simulations)
    correlation_values = np.empty(simulations)
    completed = 0
    upper_empirical = (
        np.arange(1, EXPECTED_EPISODES + 1)[None, :, None]
        / EXPECTED_EPISODES
    )
    lower_empirical = (
        np.arange(EXPECTED_EPISODES)[None, :, None]
        / EXPECTED_EPISODES
    )
    off_diagonal = ~np.eye(7, dtype=bool)
    while completed < simulations:
        batch = min(BATCH_SIZE, simulations - completed)
        samples = rng.uniform(
            -1.0, 1.0, size=(batch, EXPECTED_EPISODES, 7)
        )
        ordered = np.sort(samples, axis=1)
        cdf = np.clip((ordered + 1.0) / 2.0, 0.0, 1.0)
        d_plus = np.max(upper_empirical - cdf, axis=1)
        d_minus = np.max(cdf - lower_empirical, axis=1)
        ks_values[completed : completed + batch] = np.max(
            np.maximum(d_plus, d_minus), axis=1
        )
        centered = samples - samples.mean(axis=1, keepdims=True)
        cross = np.einsum("bnj,bnk->bjk", centered, centered, optimize=True)
        diagonal = np.diagonal(cross, axis1=1, axis2=2)
        denominator = np.sqrt(diagonal[:, :, None] * diagonal[:, None, :])
        correlations = cross / denominator
        correlation_values[completed : completed + batch] = np.max(
            np.abs(correlations[:, off_diagonal]), axis=1
        )
        completed += batch
    return ks_values, correlation_values


def summarize_reference(observed: float, reference: np.ndarray) -> dict[str, Any]:
    return {
        "observed": observed,
        "reference_median": float(np.quantile(reference, 0.50, method="linear")),
        "reference_q025": float(np.quantile(reference, 0.025, method="linear")),
        "reference_q975": float(np.quantile(reference, 0.975, method="linear")),
        "upper_tail_p": (
            int(np.count_nonzero(reference >= observed)) + 1
        )
        / (len(reference) + 1),
        "reference_simulations": len(reference),
    }


def support_diagnostics(states: np.ndarray) -> dict[str, Any]:
    outside = np.abs(states) > 1.0
    excess = np.maximum(np.abs(states) - 1.0, 0.0)
    return {
        "per_joint_outside_count": outside.sum(axis=0).astype(int).tolist(),
        "total_outside_count": int(outside.sum()),
        "per_joint_maximum_absolute_exceedance": excess.max(axis=0).tolist(),
        "maximum_absolute_exceedance": float(excess.max()),
    }


def classify(marginal: dict[str, Any], dependence: dict[str, Any]) -> str:
    marginal_significant = marginal["upper_tail_p"] <= 0.01
    dependence_significant = dependence["upper_tail_p"] <= 0.01
    marginal_material = marginal_significant and marginal["observed"] >= 0.08
    dependence_material = dependence_significant and dependence["observed"] >= 0.15
    if marginal_material and dependence_material:
        return "material_marginal_and_joint_departure"
    if marginal_material:
        return "material_marginal_departure_only"
    if dependence_material:
        return "material_joint_dependence_only"
    if marginal_significant or dependence_significant:
        return "small_or_diagnostic_only_departure"
    return "no_material_uniform_independence_departure_at_fixed_resolution"


def synthetic_controls() -> dict[str, bool]:
    known = np.tile(np.linspace(-1, 1, 5)[:, None], (1, 7))
    uniform = np.random.default_rng(205).uniform(-1, 1, size=(5_000, 7))
    shifted = np.random.default_rng(206).uniform(-0.5, 0.5, size=(1_000, 7))
    correlated = uniform.copy()
    correlated[:, 1] = correlated[:, 0]
    first = simulated_omnibus(99, np.random.Generator(np.random.PCG64(SEED)))
    second = simulated_omnibus(99, np.random.Generator(np.random.PCG64(SEED)))
    support = support_diagnostics(
        np.array([[0.0] * 7, [1.01] + [0.0] * 6, [-1.02] + [0.0] * 6])
    )
    return {
        "known_ks": np.allclose(ks_per_joint(known), 0.2),
        "uniform_small_ks": float(np.max(ks_per_joint(uniform))) < 0.03,
        "shifted_detected": float(np.max(ks_per_joint(shifted))) > 0.20,
        "correlation_detected": correlation_diagnostics(correlated)[1] > 0.99,
        "support_accounting": (
            support["total_outside_count"] == 2
            and math.isclose(support["maximum_absolute_exceedance"], 0.02)
        ),
        "deterministic_replay": (
            np.array_equal(first[0], second[0])
            and np.array_equal(first[1], second[1])
        ),
    }


def staged_validation() -> dict[str, Any]:
    states = load_states()
    controls = synthetic_controls()
    require(all(controls.values()), "synthetic controls")
    started = time.monotonic()
    simulated_omnibus(999, np.random.Generator(np.random.PCG64(SEED)))
    return {
        "controls": controls,
        "episode_count": len(states),
        "state_shape": list(states.shape),
        "synthetic_999_elapsed_seconds": time.monotonic() - started,
    }


def build() -> dict[str, Any]:
    states = load_states()
    controls = synthetic_controls()
    require(all(controls.values()), "synthetic controls")
    per_joint_ks = ks_per_joint(states)
    correlation_pairs, maximum_correlation = correlation_diagnostics(states)
    reference_ks, reference_correlation = simulated_omnibus(
        PERMUTATIONS, np.random.Generator(np.random.PCG64(SEED))
    )
    marginal = summarize_reference(float(np.max(per_joint_ks)), reference_ks)
    dependence = summarize_reference(maximum_correlation, reference_correlation)
    return {
        "schema": "h205-phail-first-state-uniform-independence-v1",
        "protocol_sha256": sha256(PROTOCOL),
        "projection_sha256": sha256(PROJECTION),
        "h202_sha256": sha256(H202),
        "h203_sha256": sha256(H203),
        "h204_sha256": sha256(H204),
        "episode_count": len(states),
        "seed_text": SEED_TEXT,
        "pcg64_seed": str(SEED),
        "synthetic_controls": controls,
        "marginal_uniformity": {
            **marginal,
            "per_joint_ks_distance": per_joint_ks.tolist(),
        },
        "joint_dependence": {
            **dependence,
            "pairwise_correlations": correlation_pairs.tolist(),
        },
        "support_diagnostic": support_diagnostics(states),
        "classification": classify(marginal, dependence),
        "commanded_draw_or_rng_validity_established": False,
        "later_state_or_outcome_opened": False,
        "full_physical_balance_established": False,
    }


def validate(result: dict[str, Any]) -> None:
    require(result["schema"] == "h205-phail-first-state-uniform-independence-v1", "schema")
    require(result["protocol_sha256"] == sha256(PROTOCOL), "protocol")
    require(result["projection_sha256"] == PROJECTION_SHA256, "projection")
    require(result["h202_sha256"] == H202_SHA256, "H202")
    require(result["h203_sha256"] == H203_SHA256, "H203")
    require(result["h204_sha256"] == H204_SHA256, "H204")
    require(result["episode_count"] == EXPECTED_EPISODES, "episodes")
    require(all(result["synthetic_controls"].values()), "controls")
    marginal = result["marginal_uniformity"]
    dependence = result["joint_dependence"]
    require(marginal["reference_simulations"] == PERMUTATIONS, "marginal simulations")
    require(dependence["reference_simulations"] == PERMUTATIONS, "dependence simulations")
    require(len(marginal["per_joint_ks_distance"]) == 7, "joint KS")
    require(len(dependence["pairwise_correlations"]) == 21, "correlations")
    require(result["classification"] == classify(marginal, dependence), "classification")
    require(result["classification"] in CLASSIFICATIONS, "class value")
    for key in (
        "commanded_draw_or_rng_validity_established",
        "later_state_or_outcome_opened",
        "full_physical_balance_established",
    ):
        require(result[key] is False, key)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    require(not (args.stage and args.check), "choose one mode")
    if args.stage:
        print(json.dumps(staged_validation(), indent=2, sort_keys=True))
        return
    candidate = build()
    validate(candidate)
    if args.check:
        require(candidate == json.loads(OUTPUT.read_text()), "exact rebuild")
        print("OK: H205 uniform-independence result reproduces")
    else:
        OUTPUT.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n")
        print(json.dumps(candidate, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
