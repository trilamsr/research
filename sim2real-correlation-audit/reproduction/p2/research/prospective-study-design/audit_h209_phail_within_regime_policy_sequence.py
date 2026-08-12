#!/usr/bin/env python3
"""Fixed H209 within-clock-regime policy-sequence audit."""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np


FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h209-phail-within-regime-policy-sequence.md"
COHORT = FAMILY / "result-h187-phail-context-support-sanitized.csv"
H206_PROJECTION = FAMILY / "projection-h206-phail-clock-offset-regimes.csv"
H206_RESULT = FAMILY / "result-h206-phail-monotonic-wall-clock-bridge.json"
H206_CHALLENGE = (
    FAMILY / "result-h206-phail-monotonic-wall-clock-bridge-independent-challenge.json"
)
H208_RESULT = FAMILY / "result-h208-phail-clock-regime-date-identifiability.json"
H208_CHALLENGE = (
    FAMILY
    / "result-h208-phail-clock-regime-date-identifiability-independent-challenge.json"
)
OUTPUT = FAMILY / "result-h209-phail-within-regime-policy-sequence.json"

EXPECTED_HASHES = {
    COHORT: "ad43fca1da065a1cb7fd84dfa9afc5691c72ebe12e7f165c68a0050e51e87ebe",
    H206_PROJECTION: "7b7af23688e230325ec69070c8e5cd5523224990d7bc44defbe5b30f12c65529",
    H206_RESULT: "1b46e77400b15ecd886d165f13fca06b3f6834a0cc4f70082da4be4a39f51e19",
    H206_CHALLENGE: "6867989afb5a2c9938ee08126defa647b7a20b26f8c48f42a7d13cc5a4787268",
    H208_RESULT: "df6c42066f26c7bbd69be25d01ef0d72517f2546c0a1d02d129b6fdc8b6981db",
    H208_CHALLENGE: "36c2853d9193cf5ba2e752aeb03e652c96955aed59d1b7c3b6dba7e5289a3fa9",
}
EXPECTED_EPISODES = 594
EXPECTED_GROUP_SIZES = {1: 250, 2: 344}
EXPECTED_PAIR_COUNTS = {1: 249, 2: 343}
EXPECTED_POLICIES = ("act", "groot", "openpi", "smolvla")
EXPECTED_POOLED_PAIRS = 592
PERMUTATIONS = 49_999
SEED_TEXT = "H209 PhAIL within-regime policy sequence v1"
SEED = int.from_bytes(hashlib.sha256(SEED_TEXT.encode()).digest()[:16], "big")
ANALYSIS_KEYS = ("pooled_within_regime", "regime_1", "regime_2")
CLASSIFICATIONS = {
    "material_pooled_policy_sequence_structure",
    "regime_specific_or_small_policy_sequence_structure",
    "no_detectable_policy_sequence_structure_at_fixed_resolution",
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
    for path, expected in EXPECTED_HASHES.items():
        require(sha256(path) == expected, f"input hash: {path.name}")


def verify_upstream_results() -> None:
    h206 = json.loads(H206_RESULT.read_text())
    require(
        h206["classification"] == "scale_separated_clock_offset_regimes",
        "H206 classification",
    )
    require(h206["episode_count"] == EXPECTED_EPISODES, "H206 episode count")
    for group in h206["one_hour_groups"]:
        label = int(group["group_1h"])
        require(
            group["episode_count"] == EXPECTED_GROUP_SIZES[label],
            f"H206 group {label} size",
        )
        require(
            group["wall_monotonic_discordant_pairs"] == 0,
            f"H206 group {label} order",
        )
    h208 = json.loads(H208_RESULT.read_text())
    require(
        h208["classification"]
        == "date_aliased_with_complete_policy_regime_support",
        "H208 classification",
    )
    require(
        tuple(h208["policy_regime_support"]["policies"]) == EXPECTED_POLICIES,
        "H208 policies",
    )
    require(
        h208["policy_regime_support"]["all_policy_regime_cells_positive"],
        "H208 support",
    )


def load_join() -> list[dict[str, Any]]:
    verify_hashes()
    verify_upstream_results()
    cohort = read_csv(COHORT)
    clocks = read_csv(H206_PROJECTION)
    require(len(cohort) == EXPECTED_EPISODES, "cohort count")
    require(len(clocks) == EXPECTED_EPISODES, "clock count")
    cohort_by_id = {row["episode_id"]: row for row in cohort}
    require(len(cohort_by_id) == EXPECTED_EPISODES, "cohort identity")
    require(
        len({row["episode_id"] for row in clocks}) == EXPECTED_EPISODES,
        "clock identity",
    )
    require(set(cohort_by_id) == {row["episode_id"] for row in clocks}, "join")
    rows: list[dict[str, Any]] = []
    counts: dict[int, int] = defaultdict(int)
    for clock in clocks:
        source = cohort_by_id[clock["episode_id"]]
        for field in ("policy_model", "utc_date", "created_ts_ns"):
            require(source[field] == clock[field], f"{field} agreement")
        group = int(clock["group_1h"])
        timestamp = int(clock["first_timestamp_ns"])
        require(group in EXPECTED_GROUP_SIZES, "group label")
        require(timestamp > 0, "timestamp")
        require(clock["policy_model"] in EXPECTED_POLICIES, "policy label")
        counts[group] += 1
        rows.append(
            {
                "episode_id": clock["episode_id"],
                "group": group,
                "timestamp": timestamp,
                "policy": clock["policy_model"],
            }
        )
    require(dict(counts) == EXPECTED_GROUP_SIZES, "group sizes")
    require(
        len({row["timestamp"] for row in rows}) == EXPECTED_EPISODES,
        "unique timestamps",
    )
    for group in (1, 2):
        for policy in EXPECTED_POLICIES:
            require(
                any(row["group"] == group and row["policy"] == policy for row in rows),
                "policy-regime support",
            )
    return rows


def ordered_group_indices(rows: list[dict[str, Any]]) -> dict[int, np.ndarray]:
    groups: dict[int, list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        groups[row["group"]].append(index)
    require(set(groups) == {1, 2}, "group identities")
    result = {
        group: np.array(
            sorted(groups[group], key=lambda index: rows[index]["timestamp"]),
            dtype=np.int64,
        )
        for group in (1, 2)
    }
    require(
        {group: len(result[group]) for group in result} == EXPECTED_GROUP_SIZES,
        "ordered group sizes",
    )
    return result


def adjacency_counts(
    labels: np.ndarray, groups: dict[int, np.ndarray]
) -> dict[int, int]:
    return {
        group: int(np.count_nonzero(labels[indices[:-1]] == labels[indices[1:]]))
        for group, indices in groups.items()
    }


def three_statistics(
    labels: np.ndarray, groups: dict[int, np.ndarray]
) -> dict[str, float]:
    counts = adjacency_counts(labels, groups)
    pairs = {group: len(groups[group]) - 1 for group in groups}
    return {
        "pooled_within_regime": sum(counts.values()) / sum(pairs.values()),
        "regime_1": counts[1] / pairs[1],
        "regime_2": counts[2] / pairs[2],
    }


def analytic_expectations(
    labels: np.ndarray, groups: dict[int, np.ndarray]
) -> dict[str, float]:
    expected_counts: dict[int, float] = {}
    for group, indices in groups.items():
        counts = Counter(labels[indices])
        n = len(indices)
        expected_fraction = sum(
            count * (count - 1) for count in counts.values()
        ) / (n * (n - 1))
        expected_counts[group] = expected_fraction * (n - 1)
    return {
        "pooled_within_regime": sum(expected_counts.values())
        / sum(len(indices) - 1 for indices in groups.values()),
        "regime_1": expected_counts[1] / (len(groups[1]) - 1),
        "regime_2": expected_counts[2] / (len(groups[2]) - 1),
    }


def draw_restricted_permutations(
    groups: dict[int, np.ndarray], rng: np.random.Generator
) -> dict[int, np.ndarray]:
    return {group: rng.permutation(groups[group]) for group in (1, 2)}


def permutation_distributions(
    labels: np.ndarray,
    groups: dict[int, np.ndarray],
    permutations: int,
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
    require(permutations > 0, "permutations")
    output = {
        key: np.empty(permutations, dtype=float) for key in ANALYSIS_KEYS
    }
    for repetition in range(permutations):
        permuted_indices = draw_restricted_permutations(groups, rng)
        permuted_labels = labels.copy()
        for group in (1, 2):
            target = groups[group]
            permuted_labels[target] = labels[permuted_indices[group]]
        values = three_statistics(permuted_labels, groups)
        for key in ANALYSIS_KEYS:
            output[key][repetition] = values[key]
    return output


def summarize(
    observed: float, expected: float, null: np.ndarray
) -> dict[str, Any]:
    repetitions = len(null)
    median = float(np.quantile(null, 0.5, method="linear"))
    lower_p = (int(np.count_nonzero(null <= observed)) + 1) / (repetitions + 1)
    upper_p = (int(np.count_nonzero(null >= observed)) + 1) / (repetitions + 1)
    return {
        "observed_same_policy_adjacency_fraction": observed,
        "analytic_exchangeability_expectation": expected,
        "permutation_median": median,
        "permutation_q025": float(np.quantile(null, 0.025, method="linear")),
        "permutation_q975": float(np.quantile(null, 0.975, method="linear")),
        "observed_minus_permutation_median": observed - median,
        "lower_tail_p": lower_p,
        "upper_tail_p": upper_p,
        "two_sided_p": min(1.0, 2 * min(lower_p, upper_p)),
        "permutations": repetitions,
    }


def classify(analyses: dict[str, dict[str, Any]]) -> str:
    pooled = analyses["pooled_within_regime"]
    effect = abs(pooled["observed_minus_permutation_median"])
    if pooled["two_sided_p"] <= 0.01 and effect >= 0.10:
        return "material_pooled_policy_sequence_structure"
    if pooled["two_sided_p"] <= 0.01 or any(
        analyses[f"regime_{group}"]["two_sided_p"] <= 0.005 for group in (1, 2)
    ):
        return "regime_specific_or_small_policy_sequence_structure"
    return "no_detectable_policy_sequence_structure_at_fixed_resolution"


def synthetic_controls() -> dict[str, bool]:
    groups = {1: np.arange(4), 2: np.arange(4, 8)}
    constant = np.array(["a"] * 8)
    alternating = np.array(["a", "b"] * 4)
    blocked = np.array(["a", "a", "b", "b", "a", "a", "b", "b"])
    small = np.array(["a", "a", "b"])
    unique_permutations = sorted(set(itertools.permutations(small.tolist())))
    enumerated_mean = np.mean(
        [
            np.count_nonzero(np.array(order[:-1]) == np.array(order[1:]))
            / (len(order) - 1)
            for order in unique_permutations
        ]
    )
    formula = sum(count * (count - 1) for count in Counter(small).values()) / (
        len(small) * (len(small) - 1)
    )
    replay_labels = np.array(["a", "b", "c", "d"] * 5)
    replay_groups = {1: np.arange(8), 2: np.arange(8, 20)}
    first = permutation_distributions(
        replay_labels,
        replay_groups,
        99,
        np.random.Generator(np.random.PCG64(SEED)),
    )
    second = permutation_distributions(
        replay_labels,
        replay_groups,
        99,
        np.random.Generator(np.random.PCG64(SEED)),
    )
    draw = draw_restricted_permutations(replay_groups, np.random.default_rng(209))
    return {
        "constant_one": all(value == 1 for value in three_statistics(constant, groups).values()),
        "alternating_zero": all(
            value == 0 for value in three_statistics(alternating, groups).values()
        ),
        "blocked_exceeds_alternating": (
            three_statistics(blocked, groups)["pooled_within_regime"]
            > three_statistics(alternating, groups)["pooled_within_regime"]
        ),
        "analytic_matches_enumeration": bool(
            np.isclose(enumerated_mean, formula)
        ),
        "restricted_membership": all(
            set(draw[group]) == set(replay_groups[group]) for group in (1, 2)
        ),
        "deterministic_replay": all(
            np.array_equal(first[key], second[key]) for key in ANALYSIS_KEYS
        ),
    }


def staged_validation(rows: list[dict[str, Any]]) -> dict[str, Any]:
    controls = synthetic_controls()
    require(all(controls.values()), "synthetic controls")
    groups = ordered_group_indices(rows)
    labels = np.array(
        [EXPECTED_POLICIES[index % len(EXPECTED_POLICIES)] for index in range(len(rows))]
    )
    rehearsal = permutation_distributions(
        labels,
        groups,
        999,
        np.random.Generator(np.random.PCG64(SEED)),
    )
    return {
        "schema": "h209-phail-within-regime-policy-sequence-stage-v1",
        "input_hashes_verified": True,
        "episode_count": len(rows),
        "group_sizes": {str(group): len(groups[group]) for group in (1, 2)},
        "pooled_pair_count": sum(len(groups[group]) - 1 for group in (1, 2)),
        "synthetic_controls": controls,
        "synthetic_rehearsal_permutations": 999,
        "synthetic_rehearsal_complete": all(
            len(rehearsal[key]) == 999 for key in ANALYSIS_KEYS
        ),
        "material_ordered_policy_adjacency_computed": False,
    }


def build() -> dict[str, Any]:
    rows = load_join()
    controls = synthetic_controls()
    require(all(controls.values()), "synthetic controls")
    groups = ordered_group_indices(rows)
    labels = np.array([row["policy"] for row in rows])
    observed = three_statistics(labels, groups)
    expected = analytic_expectations(labels, groups)
    nulls = permutation_distributions(
        labels,
        groups,
        PERMUTATIONS,
        np.random.Generator(np.random.PCG64(SEED)),
    )
    analyses = {
        key: summarize(observed[key], expected[key], nulls[key])
        for key in ANALYSIS_KEYS
    }
    analyses["pooled_within_regime"]["adjacent_pair_count"] = EXPECTED_POOLED_PAIRS
    for group in (1, 2):
        analyses[f"regime_{group}"]["episode_count"] = EXPECTED_GROUP_SIZES[group]
        analyses[f"regime_{group}"]["adjacent_pair_count"] = EXPECTED_PAIR_COUNTS[
            group
        ]
    return {
        "schema": "h209-phail-within-regime-policy-sequence-v1",
        "status": "result_exposed_exploratory",
        "protocol_sha256": sha256(PROTOCOL),
        "input_sha256": {path.name: sha256(path) for path in EXPECTED_HASHES},
        "episode_count": len(rows),
        "seed_text": SEED_TEXT,
        "pcg64_seed": str(SEED),
        "permutations": PERMUTATIONS,
        "synthetic_controls": controls,
        "analyses": analyses,
        "classification": classify(analyses),
        "permutation_reference_treated_as_assignment_law": False,
        "state_or_performance_opened": False,
        "scheduler_or_cause_identified": False,
        "outcome_analysis_authorized": False,
        "decision_consequence": (
            "Material ordered-label structure would require explicit "
            "assignment/block metadata before treating policy observations "
            "as exchangeable along chronology. A bounded null would close "
            "only this fixed adjacency diagnostic."
        ),
    }


def validate(result: dict[str, Any]) -> None:
    require(
        result["schema"] == "h209-phail-within-regime-policy-sequence-v1",
        "schema",
    )
    require(result["status"] == "result_exposed_exploratory", "status")
    require(result["protocol_sha256"] == sha256(PROTOCOL), "protocol")
    require(
        result["input_sha256"]
        == {path.name: expected for path, expected in EXPECTED_HASHES.items()},
        "input hashes",
    )
    require(result["episode_count"] == EXPECTED_EPISODES, "episodes")
    require(result["pcg64_seed"] == str(SEED), "seed")
    require(result["permutations"] == PERMUTATIONS, "permutations")
    require(all(result["synthetic_controls"].values()), "controls")
    require(set(result["analyses"]) == set(ANALYSIS_KEYS), "analyses")
    for key in ANALYSIS_KEYS:
        analysis = result["analyses"][key]
        require(analysis["permutations"] == PERMUTATIONS, f"{key} permutations")
        require(0 <= analysis["observed_same_policy_adjacency_fraction"] <= 1, f"{key} observed")
        require(0 <= analysis["analytic_exchangeability_expectation"] <= 1, f"{key} expected")
        require(0 < analysis["two_sided_p"] <= 1, f"{key} p value")
    require(
        result["analyses"]["pooled_within_regime"]["adjacent_pair_count"]
        == EXPECTED_POOLED_PAIRS,
        "pooled pairs",
    )
    require(result["classification"] == classify(result["analyses"]), "classification")
    require(result["classification"] in CLASSIFICATIONS, "classification value")
    require(
        result["permutation_reference_treated_as_assignment_law"] is False,
        "assignment scope",
    )
    require(result["state_or_performance_opened"] is False, "data scope")
    require(result["scheduler_or_cause_identified"] is False, "cause scope")
    require(result["outcome_analysis_authorized"] is False, "outcome scope")


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
        print("OK: H209 within-regime policy-sequence result reproduces")
    else:
        OUTPUT.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n")
        print(json.dumps(candidate, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
