#!/usr/bin/env python3
"""Fixed H207 clock-regime achieved-state temporal-structure audit."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np


FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h207-phail-clock-regime-temporal-structure.md"
H202_PROJECTION = FAMILY / "projection-h202-phail-initial-joint-state.csv"
H203_SCRIPT = FAMILY / "audit_h203_phail_first_state_temporal_structure.py"
H203_RESULT = FAMILY / "result-h203-phail-first-state-temporal-structure.json"
H206_PROJECTION = FAMILY / "projection-h206-phail-clock-offset-regimes.csv"
H206_RESULT = FAMILY / "result-h206-phail-monotonic-wall-clock-bridge.json"
H206_CHALLENGE = (
    FAMILY / "result-h206-phail-monotonic-wall-clock-bridge-independent-challenge.json"
)
OUTPUT = FAMILY / "result-h207-phail-clock-regime-temporal-structure.json"

H202_PROJECTION_SHA256 = (
    "44b7cd9729c691a610cc1fbbefffc5668d31030e013b92f2d4550f9869020370"
)
H203_SCRIPT_SHA256 = (
    "2a93bd3188681c5fc06312395f06fc3e899b405ed55547018b0e82ca3f271873"
)
H203_RESULT_SHA256 = (
    "5f30b36135feaf85fc32b2f3fe5f2ad2f5c5e8188ca777131b8154d3db111cda"
)
H206_PROJECTION_SHA256 = (
    "7b7af23688e230325ec69070c8e5cd5523224990d7bc44defbe5b30f12c65529"
)
H206_RESULT_SHA256 = (
    "1b46e77400b15ecd886d165f13fca06b3f6834a0cc4f70082da4be4a39f51e19"
)
H206_CHALLENGE_SHA256 = (
    "6867989afb5a2c9938ee08126defa647b7a20b26f8c48f42a7d13cc5a4787268"
)

EXPECTED_EPISODES = 594
EXPECTED_GROUP_SIZES = {1: 250, 2: 344}
EXPECTED_PAIR_COUNTS = {1: 249, 2: 343}
EXPECTED_POOLED_PAIRS = 592
PERMUTATIONS = 49_999
SEED_TEXT = "H207 PhAIL clock-regime temporal structure v1"
SEED = int.from_bytes(hashlib.sha256(SEED_TEXT.encode()).digest()[:16], "big")
BASE = np.array([0.0, -0.31, 0.0, -1.65, 0.0, 1.522, 0.0])
HALF_WIDTHS = np.array([0.03, 0.05, 0.08, 0.08, 0.10, 0.10, 0.10])
ANALYSIS_KEYS = ("pooled_within_regime", "regime_1", "regime_2")
CLASSIFICATIONS = {
    "material_pooled_clock_regime_temporal_structure",
    "regime_specific_or_small_clock_regime_temporal_structure",
    "no_detectable_clock_regime_temporal_structure_at_fixed_resolution",
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


def verify_hashes() -> None:
    expected = {
        H202_PROJECTION: H202_PROJECTION_SHA256,
        H203_SCRIPT: H203_SCRIPT_SHA256,
        H203_RESULT: H203_RESULT_SHA256,
        H206_PROJECTION: H206_PROJECTION_SHA256,
        H206_RESULT: H206_RESULT_SHA256,
        H206_CHALLENGE: H206_CHALLENGE_SHA256,
    }
    for path, digest in expected.items():
        require(sha256(path) == digest, f"input hash: {path.name}")


def verify_h206_result() -> dict[str, Any]:
    result = json.loads(H206_RESULT.read_text())
    require(
        result["classification"] == "scale_separated_clock_offset_regimes",
        "H206 classification",
    )
    require(result["episode_count"] == EXPECTED_EPISODES, "H206 episode count")
    groups = {int(group["group_1h"]): group for group in result["one_hour_groups"]}
    require(set(groups) == set(EXPECTED_GROUP_SIZES), "H206 groups")
    for label, expected_size in EXPECTED_GROUP_SIZES.items():
        require(
            groups[label]["episode_count"] == expected_size,
            f"H206 group {label} size",
        )
        require(
            groups[label]["wall_monotonic_discordant_pairs"] == 0,
            f"H206 group {label} order",
        )
    return result


def load_join() -> list[dict[str, Any]]:
    verify_hashes()
    verify_h206_result()
    states = read_csv(H202_PROJECTION)
    clocks = read_csv(H206_PROJECTION)
    require(len(states) == EXPECTED_EPISODES, "H202 row count")
    require(len(clocks) == EXPECTED_EPISODES, "H206 projection row count")
    require(
        len({row["episode_id"] for row in states}) == EXPECTED_EPISODES,
        "H202 unique identity",
    )
    require(
        len({row["episode_id"] for row in clocks}) == EXPECTED_EPISODES,
        "H206 unique identity",
    )
    state_by_id = {row["episode_id"]: row for row in states}
    require(set(state_by_id) == {row["episode_id"] for row in clocks}, "join identity")

    joined: list[dict[str, Any]] = []
    for clock in clocks:
        episode_id = clock["episode_id"]
        state = state_by_id[episode_id]
        q = np.array([float(state[f"q{joint}"]) for joint in range(7)])
        require(np.isfinite(q).all(), "finite achieved state")
        require(int(state["error"]) == 0, "first-state error flag")
        first_timestamp_ns = int(clock["first_timestamp_ns"])
        require(first_timestamp_ns > 0, "positive monotonic timestamp")
        require(
            int(state["timestamp_ns"]) == first_timestamp_ns,
            "H202/H206 timestamp agreement",
        )
        group = int(clock["group_1h"])
        require(group in EXPECTED_GROUP_SIZES, "clock regime label")
        joined.append(
            {
                "episode_id": episode_id,
                "group": group,
                "first_timestamp_ns": first_timestamp_ns,
                "q": q,
            }
        )

    require(
        len({row["first_timestamp_ns"] for row in joined}) == EXPECTED_EPISODES,
        "unique monotonic timestamps",
    )
    counts: dict[int, int] = defaultdict(int)
    for row in joined:
        counts[row["group"]] += 1
    require(dict(counts) == EXPECTED_GROUP_SIZES, "clock regime sizes")
    return joined


def ordered_group_indices(rows: list[dict[str, Any]]) -> dict[int, np.ndarray]:
    groups: dict[int, list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        groups[int(row["group"])].append(index)
    require(set(groups) == set(EXPECTED_GROUP_SIZES), "group identities")
    ordered: dict[int, np.ndarray] = {}
    for label in sorted(groups):
        indices = sorted(
            groups[label],
            key=lambda index: rows[index]["first_timestamp_ns"],
        )
        require(len(indices) == EXPECTED_GROUP_SIZES[label], f"group {label} size")
        timestamps = [rows[index]["first_timestamp_ns"] for index in indices]
        require(len(set(timestamps)) == len(timestamps), f"group {label} timestamps")
        ordered[label] = np.array(indices, dtype=np.int64)
    return ordered


def transform(states: np.ndarray) -> np.ndarray:
    require(states.ndim == 2 and states.shape[1] == 7, "state shape")
    output = (states - BASE) / (HALF_WIDTHS / math.sqrt(3))
    require(np.isfinite(output).all(), "finite transformed states")
    return output


def distance_sums(
    states: np.ndarray, groups: dict[int, np.ndarray]
) -> dict[int, float]:
    output: dict[int, float] = {}
    for label in sorted(groups):
        indices = groups[label]
        require(len(indices) >= 2, f"group {label} pairs")
        differences = np.diff(states[indices], axis=0)
        output[label] = float(np.square(differences).sum())
    return output


def three_statistics(
    states: np.ndarray, groups: dict[int, np.ndarray]
) -> dict[str, float]:
    sums = distance_sums(states, groups)
    pair_counts = {label: len(groups[label]) - 1 for label in groups}
    pooled_pairs = sum(pair_counts.values())
    require(pooled_pairs > 0, "pooled pairs")
    return {
        "pooled_within_regime": sum(sums.values()) / pooled_pairs,
        "regime_1": sums[1] / pair_counts[1],
        "regime_2": sums[2] / pair_counts[2],
    }


def draw_restricted_permutations(
    groups: dict[int, np.ndarray], rng: np.random.Generator
) -> dict[int, np.ndarray]:
    return {label: rng.permutation(groups[label]) for label in sorted(groups)}


def permutation_distributions(
    states: np.ndarray,
    groups: dict[int, np.ndarray],
    permutations: int,
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
    require(permutations > 0, "permutation count")
    output = {
        key: np.empty(permutations, dtype=np.float64) for key in ANALYSIS_KEYS
    }
    for repetition in range(permutations):
        permuted = draw_restricted_permutations(groups, rng)
        statistics = three_statistics(states, permuted)
        for key in ANALYSIS_KEYS:
            output[key][repetition] = statistics[key]
    for values in output.values():
        require(np.isfinite(values).all(), "finite permutation distribution")
    return output


def summarize(observed: float, null: np.ndarray) -> dict[str, Any]:
    repetitions = len(null)
    require(repetitions > 0, "empty permutation distribution")
    median = float(np.quantile(null, 0.50, method="linear"))
    lower_p = (int(np.count_nonzero(null <= observed)) + 1) / (repetitions + 1)
    upper_p = (int(np.count_nonzero(null >= observed)) + 1) / (repetitions + 1)
    return {
        "observed_mean_successive_squared_distance": observed,
        "permutation_median": median,
        "permutation_q025": float(np.quantile(null, 0.025, method="linear")),
        "permutation_q975": float(np.quantile(null, 0.975, method="linear")),
        "observed_to_permutation_median_ratio": observed / median,
        "lower_tail_p": lower_p,
        "upper_tail_p": upper_p,
        "two_sided_p": min(1.0, 2 * min(lower_p, upper_p)),
        "permutations": repetitions,
    }


def classify(analyses: dict[str, dict[str, Any]]) -> str:
    pooled = analyses["pooled_within_regime"]
    ratio = pooled["observed_to_permutation_median_ratio"]
    if pooled["two_sided_p"] <= 0.01 and (ratio <= 0.90 or ratio >= 1.10):
        return "material_pooled_clock_regime_temporal_structure"
    if pooled["two_sided_p"] <= 0.01 or any(
        analyses[f"regime_{label}"]["two_sided_p"] <= 0.005 for label in (1, 2)
    ):
        return "regime_specific_or_small_clock_regime_temporal_structure"
    return "no_detectable_clock_regime_temporal_structure_at_fixed_resolution"


def synthetic_controls() -> dict[str, bool]:
    simple = np.zeros((3, 7))
    simple[:, 0] = [0.0, 1.0, 3.0]
    simple_groups = {1: np.arange(3), 2: np.arange(3, 6)}
    simple_two = np.vstack([simple, simple])
    constant = np.zeros((40, 7))
    alternating = np.tile(np.array([[0.0] * 7, [2.0] * 7]), (20, 1))
    drift = np.repeat(np.arange(40, dtype=float)[:, None] / 40, 7, axis=1)
    iid = np.random.default_rng(207).normal(size=(5_000, 7))
    replay_states = np.random.default_rng(208).normal(size=(20, 7))
    replay_groups = {1: np.arange(8), 2: np.arange(8, 20)}
    replay_a = permutation_distributions(
        replay_states,
        replay_groups,
        99,
        np.random.Generator(np.random.PCG64(SEED)),
    )
    replay_b = permutation_distributions(
        replay_states,
        replay_groups,
        99,
        np.random.Generator(np.random.PCG64(SEED)),
    )
    membership_rng = np.random.default_rng(209)
    membership_draw = draw_restricted_permutations(replay_groups, membership_rng)
    return {
        "known_distance": math.isclose(
            three_statistics(simple_two, simple_groups)["pooled_within_regime"],
            2.5,
        ),
        "constant_zero": (
            float(np.square(np.diff(constant, axis=0)).sum()) == 0.0
        ),
        "alternating_exceeds_drift": (
            float(np.square(np.diff(alternating, axis=0)).sum())
            > float(np.square(np.diff(drift, axis=0)).sum())
        ),
        "iid_near_nominal_14": abs(
            float(np.square(np.diff(iid, axis=0)).sum()) / (len(iid) - 1) - 14
        )
        < 0.5,
        "restricted_membership": all(
            set(membership_draw[label]) == set(replay_groups[label])
            for label in replay_groups
        ),
        "deterministic_replay": all(
            np.array_equal(replay_a[key], replay_b[key]) for key in ANALYSIS_KEYS
        ),
    }


def staged_validation(rows: list[dict[str, Any]]) -> dict[str, Any]:
    controls = synthetic_controls()
    require(all(controls.values()), "synthetic controls")
    groups = ordered_group_indices(rows)
    require(
        {label: len(indices) - 1 for label, indices in groups.items()}
        == EXPECTED_PAIR_COUNTS,
        "pair accounting",
    )
    synthetic_states = np.random.default_rng(210).normal(
        size=(EXPECTED_EPISODES, 7)
    )
    started = time.monotonic()
    rehearsal = permutation_distributions(
        synthetic_states,
        groups,
        999,
        np.random.Generator(np.random.PCG64(SEED)),
    )
    elapsed = time.monotonic() - started
    return {
        "schema": "h207-phail-clock-regime-temporal-structure-stage-v1",
        "input_hashes_verified": True,
        "episode_count": len(rows),
        "unique_monotonic_timestamp_count": len(
            {row["first_timestamp_ns"] for row in rows}
        ),
        "group_sizes": {
            str(label): len(indices) for label, indices in groups.items()
        },
        "group_pair_counts": {
            str(label): len(indices) - 1 for label, indices in groups.items()
        },
        "pooled_pair_count": sum(len(indices) - 1 for indices in groups.values()),
        "synthetic_controls": controls,
        "synthetic_rehearsal_permutations": 999,
        "synthetic_rehearsal_complete": all(
            len(rehearsal[key]) == 999 for key in ANALYSIS_KEYS
        ),
        "synthetic_rehearsal_elapsed_seconds": elapsed,
        "achieved_state_order_statistic_computed": False,
    }


def build() -> dict[str, Any]:
    rows = load_join()
    controls = synthetic_controls()
    require(all(controls.values()), "synthetic controls")
    groups = ordered_group_indices(rows)
    raw_states = np.vstack([row["q"] for row in rows])
    states = transform(raw_states)
    observed = three_statistics(states, groups)
    nulls = permutation_distributions(
        states,
        groups,
        PERMUTATIONS,
        np.random.Generator(np.random.PCG64(SEED)),
    )
    analyses = {
        key: summarize(observed[key], nulls[key]) for key in ANALYSIS_KEYS
    }
    analyses["pooled_within_regime"]["group_count"] = 2
    analyses["pooled_within_regime"]["adjacent_pair_count"] = EXPECTED_POOLED_PAIRS
    for label in (1, 2):
        analyses[f"regime_{label}"]["group_count"] = 1
        analyses[f"regime_{label}"]["episode_count"] = EXPECTED_GROUP_SIZES[label]
        analyses[f"regime_{label}"]["adjacent_pair_count"] = EXPECTED_PAIR_COUNTS[
            label
        ]

    prior_h203 = json.loads(H203_RESULT.read_text())
    result = {
        "schema": "h207-phail-clock-regime-temporal-structure-v1",
        "status": "result_exposed_exploratory",
        "protocol_sha256": sha256(PROTOCOL),
        "input_sha256": {
            "h202_projection": sha256(H202_PROJECTION),
            "h203_script": sha256(H203_SCRIPT),
            "h203_result": sha256(H203_RESULT),
            "h206_projection": sha256(H206_PROJECTION),
            "h206_result": sha256(H206_RESULT),
            "h206_independent_challenge": sha256(H206_CHALLENGE),
        },
        "run_identity": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "platform": platform.platform(),
            "seed_text": SEED_TEXT,
            "pcg64_seed": str(SEED),
            "permutations": PERMUTATIONS,
            "rng_stream_scope": (
                "one stream; each repetition independently permutes regime 1 "
                "then regime 2 and derives all three statistics"
            ),
        },
        "episode_count": len(rows),
        "group_sizes": {str(key): value for key, value in EXPECTED_GROUP_SIZES.items()},
        "group_pair_counts": {
            str(key): value for key, value in EXPECTED_PAIR_COUNTS.items()
        },
        "pooled_pair_count": EXPECTED_POOLED_PAIRS,
        "synthetic_controls": controls,
        "analyses": analyses,
        "classification": classify(analyses),
        "known_prior_h203": {
            "classification": prior_h203["classification"],
            "global_ratio": prior_h203["analyses"]["global"][
                "observed_to_permutation_median_ratio"
            ],
            "global_two_sided_p": prior_h203["analyses"]["global"]["two_sided_p"],
        },
        "performance_or_later_state_opened": False,
        "clock_regime_treated_as_session": False,
        "independence_established": False,
        "confirmatory_claim_authorized": False,
        "decision_consequence": (
            "This exploratory diagnostic can strengthen the request for "
            "authenticated execution-session and carryover units if temporal "
            "structure is detected, or close this clock-regime refinement if "
            "it is not. It cannot establish independence or a mechanism."
        ),
    }
    return result


def validate(result: dict[str, Any]) -> None:
    require(
        result["schema"] == "h207-phail-clock-regime-temporal-structure-v1",
        "schema",
    )
    require(result["status"] == "result_exposed_exploratory", "status")
    require(result["protocol_sha256"] == sha256(PROTOCOL), "protocol")
    expected_inputs = {
        "h202_projection": H202_PROJECTION_SHA256,
        "h203_script": H203_SCRIPT_SHA256,
        "h203_result": H203_RESULT_SHA256,
        "h206_projection": H206_PROJECTION_SHA256,
        "h206_result": H206_RESULT_SHA256,
        "h206_independent_challenge": H206_CHALLENGE_SHA256,
    }
    require(result["input_sha256"] == expected_inputs, "input hashes")
    require(result["episode_count"] == EXPECTED_EPISODES, "episode count")
    require(
        result["group_sizes"]
        == {str(key): value for key, value in EXPECTED_GROUP_SIZES.items()},
        "group sizes",
    )
    require(
        result["group_pair_counts"]
        == {str(key): value for key, value in EXPECTED_PAIR_COUNTS.items()},
        "group pair counts",
    )
    require(result["pooled_pair_count"] == EXPECTED_POOLED_PAIRS, "pooled pairs")
    require(all(result["synthetic_controls"].values()), "synthetic controls")
    require(set(result["analyses"]) == set(ANALYSIS_KEYS), "analysis keys")
    for key in ANALYSIS_KEYS:
        analysis = result["analyses"][key]
        require(analysis["permutations"] == PERMUTATIONS, f"{key} permutations")
        require(
            0 < analysis["two_sided_p"] <= 1,
            f"{key} p value",
        )
        require(
            analysis["observed_to_permutation_median_ratio"] > 0,
            f"{key} ratio",
        )
    require(
        result["analyses"]["pooled_within_regime"]["adjacent_pair_count"]
        == EXPECTED_POOLED_PAIRS,
        "analysis pooled pairs",
    )
    require(
        result["analyses"]["regime_1"]["adjacent_pair_count"]
        == EXPECTED_PAIR_COUNTS[1],
        "analysis regime 1 pairs",
    )
    require(
        result["analyses"]["regime_2"]["adjacent_pair_count"]
        == EXPECTED_PAIR_COUNTS[2],
        "analysis regime 2 pairs",
    )
    require(result["classification"] == classify(result["analyses"]), "classification")
    require(result["classification"] in CLASSIFICATIONS, "classification value")
    require(
        result["performance_or_later_state_opened"] is False,
        "performance scope",
    )
    require(
        result["clock_regime_treated_as_session"] is False,
        "regime scope",
    )
    require(result["independence_established"] is False, "independence scope")
    require(
        result["confirmatory_claim_authorized"] is False,
        "confirmatory scope",
    )


def rebuild_equivalent(candidate: dict[str, Any], retained: dict[str, Any]) -> bool:
    """Compare all retained content except the non-scientific OS build label."""
    validate(candidate)
    validate(retained)
    candidate_bound = json.loads(json.dumps(candidate))
    retained_bound = json.loads(json.dumps(retained))
    candidate_bound["run_identity"].pop("platform")
    retained_bound["run_identity"].pop("platform")
    return candidate_bound == retained_bound


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
        retained = json.loads(OUTPUT.read_text())
        require(rebuild_equivalent(candidate, retained), "scientific rebuild")
        print(
            "OK: H207 scientific result reproduces exactly "
            "(OS build label excluded)"
        )
    else:
        OUTPUT.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n")
        print(json.dumps(candidate, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
