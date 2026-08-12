#!/usr/bin/env python3
"""Fixed H203 achieved-first-state temporal-structure audit."""

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


ROOT = Path(__file__).resolve().parents[2]
FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h203-phail-first-state-temporal-structure.md"
COHORT = FAMILY / "result-h187-phail-context-support-sanitized.csv"
PROJECTION = FAMILY / "projection-h202-phail-initial-joint-state.csv"
H202_RESULT = FAMILY / "result-h202-phail-initial-joint-state.json"
OUTPUT = FAMILY / "result-h203-phail-first-state-temporal-structure.json"
COHORT_SHA256 = "ad43fca1da065a1cb7fd84dfa9afc5691c72ebe12e7f165c68a0050e51e87ebe"
PROJECTION_SHA256 = "44b7cd9729c691a610cc1fbbefffc5668d31030e013b92f2d4550f9869020370"
H202_SHA256 = "4e60b6c6cbc0eabcaf4ae7761119b5af89bbaf6707e53cce8f0ec3c227a96043"
EXPECTED_EPISODES = 594
PERMUTATIONS = 49_999
SEED_TEXT = "H203 PhAIL first-state temporal structure v1"
SEED = int.from_bytes(hashlib.sha256(SEED_TEXT.encode()).digest()[:16], "big")
BASE = np.array([0.0, -0.31, 0.0, -1.65, 0.0, 1.522, 0.0])
HALF_WIDTHS = np.array([0.03, 0.05, 0.08, 0.08, 0.10, 0.10, 0.10])
CLASSIFICATIONS = {
    "material_global_temporal_structure",
    "secondary_only_or_small_temporal_structure",
    "no_detectable_temporal_structure_at_fixed_resolution",
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
    require(sha256(H202_RESULT) == H202_SHA256, "H202 result hash")
    cohort = read_csv(COHORT)
    projection = read_csv(PROJECTION)
    require(len(cohort) == EXPECTED_EPISODES, "cohort count")
    require(len(projection) == EXPECTED_EPISODES, "projection count")
    require(
        len({row["episode_id"] for row in cohort}) == EXPECTED_EPISODES,
        "cohort identity",
    )
    require(
        len({row["episode_id"] for row in projection}) == EXPECTED_EPISODES,
        "projection identity",
    )
    projected = {row["episode_id"]: row for row in projection}
    require(set(projected) == {row["episode_id"] for row in cohort}, "join identity")
    joined = []
    for row in cohort:
        episode_id = row["episode_id"]
        state = projected[episode_id]
        q = np.array([float(state[f"q{index}"]) for index in range(7)])
        require(np.isfinite(q).all(), "finite state")
        require(int(state["error"]) == 0, "first error")
        timestamp = int(row["created_ts_ns"])
        require(timestamp > 0, "timestamp")
        require(row["policy_model"], "policy")
        require(row["utc_date"], "date")
        joined.append(
            {
                "episode_id": episode_id,
                "timestamp": timestamp,
                "policy": row["policy_model"],
                "date": row["utc_date"],
                "q": q,
            }
        )
    require(
        len({row["timestamp"] for row in joined}) == EXPECTED_EPISODES,
        "unique timestamps",
    )
    return joined


def group_indices(
    rows: list[dict[str, Any]], key: str | None
) -> list[np.ndarray]:
    grouped: dict[str, list[int]] = defaultdict(list)
    if key is None:
        grouped["all"] = list(range(len(rows)))
    else:
        for index, row in enumerate(rows):
            grouped[str(row[key])].append(index)
    result = []
    for label in sorted(grouped):
        indices = sorted(
            grouped[label],
            key=lambda index: (rows[index]["timestamp"], rows[index]["episode_id"]),
        )
        require(len(indices) >= 3, f"{key or 'global'} group size")
        result.append(np.array(indices, dtype=np.int64))
    return result


def pair_count(groups: list[np.ndarray]) -> int:
    return sum(len(group) - 1 for group in groups)


def mean_successive_squared_distance(
    states: np.ndarray, groups: list[np.ndarray]
) -> float:
    total = 0.0
    pairs = pair_count(groups)
    require(pairs > 0, "no pairs")
    for group in groups:
        differences = np.diff(states[group], axis=0)
        total += float(np.square(differences).sum())
    return total / pairs


def permutation_distribution(
    states: np.ndarray,
    groups: list[np.ndarray],
    permutations: int,
    rng: np.random.Generator,
) -> np.ndarray:
    require(permutations > 0, "permutation count")
    pairs = pair_count(groups)
    output = np.empty(permutations, dtype=np.float64)
    for repetition in range(permutations):
        total = 0.0
        for group in groups:
            permuted = rng.permutation(group)
            differences = np.diff(states[permuted], axis=0)
            total += float(np.square(differences).sum())
        output[repetition] = total / pairs
    require(np.isfinite(output).all(), "finite permutation distribution")
    return output


def linear_quantile(values: np.ndarray, probability: float) -> float:
    return float(np.quantile(values, probability, method="linear"))


def analyze(
    states: np.ndarray,
    groups: list[np.ndarray],
    permutations: int,
    rng: np.random.Generator,
) -> dict[str, Any]:
    observed = mean_successive_squared_distance(states, groups)
    null = permutation_distribution(states, groups, permutations, rng)
    median = linear_quantile(null, 0.50)
    lower_p = (int(np.count_nonzero(null <= observed)) + 1) / (permutations + 1)
    upper_p = (int(np.count_nonzero(null >= observed)) + 1) / (permutations + 1)
    return {
        "group_count": len(groups),
        "adjacent_pair_count": pair_count(groups),
        "observed_mean_successive_squared_distance": observed,
        "permutation_median": median,
        "permutation_q025": linear_quantile(null, 0.025),
        "permutation_q975": linear_quantile(null, 0.975),
        "observed_to_permutation_median_ratio": observed / median,
        "lower_tail_p": lower_p,
        "upper_tail_p": upper_p,
        "two_sided_p": min(1.0, 2 * min(lower_p, upper_p)),
        "permutations": permutations,
    }


def adjacent_correlations(states: np.ndarray, group: np.ndarray) -> list[float]:
    return [
        float(np.corrcoef(states[group[:-1], joint], states[group[1:], joint])[0, 1])
        for joint in range(7)
    ]


def classify(analyses: dict[str, dict[str, Any]]) -> str:
    primary = analyses["global"]
    ratio = primary["observed_to_permutation_median_ratio"]
    if primary["two_sided_p"] <= 0.01 and (ratio <= 0.90 or ratio >= 1.10):
        return "material_global_temporal_structure"
    if primary["two_sided_p"] <= 0.01 or any(
        analyses[key]["two_sided_p"] <= 0.01
        for key in ("within_policy", "within_utc_date")
    ):
        return "secondary_only_or_small_temporal_structure"
    return "no_detectable_temporal_structure_at_fixed_resolution"


def synthetic_controls() -> dict[str, bool]:
    simple = np.zeros((3, 7))
    simple[:, 0] = [0.0, 1.0, 3.0]
    one_group = [np.arange(3)]
    constant = np.zeros((20, 7))
    alternating = np.tile(np.array([[0.0] * 7, [2.0] * 7]), (10, 1))
    drift = np.repeat(np.arange(20, dtype=float)[:, None] / 20, 7, axis=1)
    iid = np.random.default_rng(203).normal(size=(5_000, 7))
    deterministic_a = permutation_distribution(
        iid[:20], [np.arange(20)], 99, np.random.Generator(np.random.PCG64(SEED))
    )
    deterministic_b = permutation_distribution(
        iid[:20], [np.arange(20)], 99, np.random.Generator(np.random.PCG64(SEED))
    )
    return {
        "known_distance": math.isclose(
            mean_successive_squared_distance(simple, one_group), 2.5
        ),
        "constant_zero": mean_successive_squared_distance(
            constant, [np.arange(20)]
        )
        == 0.0,
        "alternating_exceeds_drift": (
            mean_successive_squared_distance(alternating, [np.arange(20)])
            > mean_successive_squared_distance(drift, [np.arange(20)])
        ),
        "iid_near_nominal_14": abs(
            mean_successive_squared_distance(iid, [np.arange(len(iid))]) - 14
        )
        < 0.5,
        "deterministic_replay": np.array_equal(deterministic_a, deterministic_b),
    }


def staged_validation(rows: list[dict[str, Any]]) -> dict[str, Any]:
    controls = synthetic_controls()
    require(all(controls.values()), "synthetic controls")
    policy_groups = group_indices(rows, "policy")
    date_groups = group_indices(rows, "date")
    require(pair_count(policy_groups) >= 100, "policy pairs")
    require(pair_count(date_groups) >= 100, "date pairs")
    synthetic = np.random.default_rng(204).normal(size=(len(rows), 7))
    started = time.monotonic()
    rng = np.random.Generator(np.random.PCG64(SEED))
    permutation_distribution(synthetic, [np.arange(len(rows))], 999, rng)
    permutation_distribution(synthetic, policy_groups, 999, rng)
    permutation_distribution(synthetic, date_groups, 999, rng)
    elapsed = time.monotonic() - started
    return {
        "controls": controls,
        "episode_count": len(rows),
        "unique_timestamp_count": len({row["timestamp"] for row in rows}),
        "policy_group_count": len(policy_groups),
        "policy_pair_count": pair_count(policy_groups),
        "utc_date_group_count": len(date_groups),
        "utc_date_pair_count": pair_count(date_groups),
        "synthetic_999_per_analysis_elapsed_seconds": elapsed,
    }


def build() -> dict[str, Any]:
    rows = load_join()
    controls = synthetic_controls()
    require(all(controls.values()), "synthetic controls")
    states = np.vstack([row["q"] for row in rows])
    states = (states - BASE) / (HALF_WIDTHS / math.sqrt(3))
    global_groups = group_indices(rows, None)
    policy_groups = group_indices(rows, "policy")
    date_groups = group_indices(rows, "date")
    require(pair_count(policy_groups) >= 100, "policy pairs")
    require(pair_count(date_groups) >= 100, "date pairs")
    rng = np.random.Generator(np.random.PCG64(SEED))
    analyses = {
        "global": analyze(states, global_groups, PERMUTATIONS, rng),
        "within_policy": analyze(states, policy_groups, PERMUTATIONS, rng),
        "within_utc_date": analyze(states, date_groups, PERMUTATIONS, rng),
    }
    global_order = global_groups[0]
    diagnostics = {
        "primary_adjacent_per_joint_pearson": adjacent_correlations(
            states, global_order
        ),
        "exact_duplicate_vector_count": int(
            len(states) - len(np.unique(states, axis=0))
        ),
    }
    return {
        "schema": "h203-phail-first-state-temporal-structure-v1",
        "protocol_sha256": sha256(PROTOCOL),
        "cohort_sha256": sha256(COHORT),
        "h202_projection_sha256": sha256(PROJECTION),
        "h202_result_sha256": sha256(H202_RESULT),
        "episode_count": len(rows),
        "seed_text": SEED_TEXT,
        "pcg64_seed": str(SEED),
        "rng_stream_order": ["global", "within_policy", "within_utc_date"],
        "synthetic_controls": controls,
        "analyses": analyses,
        "diagnostics": diagnostics,
        "classification": classify(analyses),
        "later_state_or_outcome_opened": False,
        "recorded_chronology_treated_as_physical_order": False,
        "independence_established": False,
        "decision_consequence": (
            "The fixed diagnostic can strengthen the session/carryover evidence "
            "request if material structure is detected, or block a positive "
            "dependence claim at this resolution if it is not. It cannot prove "
            "independence or identify a physical mechanism."
        ),
    }


def validate(result: dict[str, Any]) -> None:
    require(result["schema"] == "h203-phail-first-state-temporal-structure-v1", "schema")
    require(result["protocol_sha256"] == sha256(PROTOCOL), "protocol")
    require(result["cohort_sha256"] == COHORT_SHA256, "cohort")
    require(result["h202_projection_sha256"] == PROJECTION_SHA256, "projection")
    require(result["h202_result_sha256"] == H202_SHA256, "H202")
    require(result["episode_count"] == EXPECTED_EPISODES, "episodes")
    require(result["pcg64_seed"] == str(SEED), "seed")
    require(all(result["synthetic_controls"].values()), "controls")
    analyses = result["analyses"]
    require(set(analyses) == {"global", "within_policy", "within_utc_date"}, "analyses")
    require(analyses["global"]["adjacent_pair_count"] == 593, "global pairs")
    for analysis in analyses.values():
        require(analysis["permutations"] == PERMUTATIONS, "permutations")
        require(0 < analysis["two_sided_p"] <= 1, "p value")
        require(analysis["observed_to_permutation_median_ratio"] > 0, "ratio")
    require(result["classification"] == classify(analyses), "classification")
    require(result["classification"] in CLASSIFICATIONS, "classification value")
    require(result["later_state_or_outcome_opened"] is False, "scope")
    require(
        result["recorded_chronology_treated_as_physical_order"] is False,
        "chronology scope",
    )
    require(result["independence_established"] is False, "independence scope")


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
        print("OK: H203 temporal-structure result reproduces exactly")
    else:
        OUTPUT.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n")
        print(json.dumps(candidate, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
