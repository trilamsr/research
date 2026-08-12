#!/usr/bin/env python3
"""Fixed H210 within-UTC-date policy-sequence audit."""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np


FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h210-phail-within-date-policy-sequence.md"
COHORT = FAMILY / "result-h187-phail-context-support-sanitized.csv"
H206_PROJECTION = FAMILY / "projection-h206-phail-clock-offset-regimes.csv"
H206_RESULT = FAMILY / "result-h206-phail-monotonic-wall-clock-bridge.json"
H206_CHALLENGE = FAMILY / "result-h206-phail-monotonic-wall-clock-bridge-independent-challenge.json"
H208_RESULT = FAMILY / "result-h208-phail-clock-regime-date-identifiability.json"
H208_CHALLENGE = FAMILY / "result-h208-phail-clock-regime-date-identifiability-independent-challenge.json"
H209_RESULT = FAMILY / "result-h209-phail-within-regime-policy-sequence.json"
H209_CHALLENGE = FAMILY / "result-h209-phail-within-regime-policy-sequence-independent-challenge.json"
OUTPUT = FAMILY / "result-h210-phail-within-date-policy-sequence.json"

EXPECTED_HASHES = {
    COHORT: "ad43fca1da065a1cb7fd84dfa9afc5691c72ebe12e7f165c68a0050e51e87ebe",
    H206_PROJECTION: "7b7af23688e230325ec69070c8e5cd5523224990d7bc44defbe5b30f12c65529",
    H206_RESULT: "1b46e77400b15ecd886d165f13fca06b3f6834a0cc4f70082da4be4a39f51e19",
    H206_CHALLENGE: "6867989afb5a2c9938ee08126defa647b7a20b26f8c48f42a7d13cc5a4787268",
    H208_RESULT: "df6c42066f26c7bbd69be25d01ef0d72517f2546c0a1d02d129b6fdc8b6981db",
    H208_CHALLENGE: "36c2853d9193cf5ba2e752aeb03e652c96955aed59d1b7c3b6dba7e5289a3fa9",
    H209_RESULT: "2879b1c4b0ade1e4d1fd47e5a0db5312fce2d401c5f1580f7e2af2c211da7794",
    H209_CHALLENGE: "e6700b2ce631a7ca6e16669dad30cf00a4d922ff8444f3a2601a154e23ed767f",
}
EXPECTED_EPISODES = 594
EXPECTED_DATES = 13
EXPECTED_GROUP_SIZES = {1: 250, 2: 344}
EXPECTED_PAIR_COUNTS = {"pooled_within_date": 581, "regime_1_dates": 243, "regime_2_dates": 338}
EXPECTED_POLICIES = ("act", "groot", "openpi", "smolvla")
KEYS = tuple(EXPECTED_PAIR_COUNTS)
PERMUTATIONS = 49_999
SEED_TEXT = "H210 PhAIL within-date policy sequence v1"
SEED = int.from_bytes(hashlib.sha256(SEED_TEXT.encode()).digest()[:16], "big")
CLASSIFICATIONS = {
    "material_pooled_within_date_policy_sequence_structure",
    "regime_specific_or_small_within_date_policy_sequence_structure",
    "no_detectable_within_date_policy_sequence_structure_at_fixed_resolution",
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
    for path, expected in EXPECTED_HASHES.items():
        require(sha256(path) == expected, f"input hash: {path.name}")
    h206 = json.loads(H206_RESULT.read_text())
    require(h206["classification"] == "scale_separated_clock_offset_regimes", "H206")
    h208 = json.loads(H208_RESULT.read_text())
    require(h208["classification"] == "date_aliased_with_complete_policy_regime_support", "H208")
    h209 = json.loads(H209_RESULT.read_text())
    require(h209["classification"] == "regime_specific_or_small_policy_sequence_structure", "H209")
    cohort = read_csv(COHORT)
    clocks = read_csv(H206_PROJECTION)
    require(len(cohort) == len(clocks) == EXPECTED_EPISODES, "counts")
    cohort_by_id = {row["episode_id"]: row for row in cohort}
    require(len(cohort_by_id) == EXPECTED_EPISODES, "cohort identity")
    require(len({row["episode_id"] for row in clocks}) == EXPECTED_EPISODES, "clock identity")
    require(set(cohort_by_id) == {row["episode_id"] for row in clocks}, "join")
    rows = []
    for clock in clocks:
        source = cohort_by_id[clock["episode_id"]]
        for field in ("policy_model", "utc_date", "created_ts_ns"):
            require(source[field] == clock[field], f"{field} agreement")
        timestamp = int(clock["first_timestamp_ns"])
        group = int(clock["group_1h"])
        require(timestamp > 0, "timestamp")
        require(group in (1, 2), "group")
        require(clock["policy_model"] in EXPECTED_POLICIES, "policy")
        rows.append({
            "episode_id": clock["episode_id"],
            "date": clock["utc_date"],
            "group": group,
            "timestamp": timestamp,
            "policy": clock["policy_model"],
        })
    require(len({row["timestamp"] for row in rows}) == EXPECTED_EPISODES, "timestamps")
    require(len({row["date"] for row in rows}) == EXPECTED_DATES, "dates")
    require(
        {group: sum(row["group"] == group for row in rows) for group in (1, 2)}
        == EXPECTED_GROUP_SIZES,
        "group sizes",
    )
    return rows


def date_groups(rows: list[dict[str, Any]]) -> tuple[dict[str, np.ndarray], dict[str, int]]:
    dates = sorted({row["date"] for row in rows})
    groups: dict[str, np.ndarray] = {}
    regimes: dict[str, int] = {}
    for date in dates:
        indices = [index for index, row in enumerate(rows) if row["date"] == date]
        require(len(indices) >= 3, "date size")
        ordered = sorted(indices, key=lambda index: rows[index]["timestamp"])
        groups[date] = np.array(ordered, dtype=np.int64)
        values = {rows[index]["group"] for index in ordered}
        require(len(values) == 1, "date regime nesting")
        regimes[date] = values.pop()
    return groups, regimes


def same_counts(labels: np.ndarray, groups: dict[str, np.ndarray]) -> dict[str, int]:
    return {
        date: int(np.count_nonzero(labels[idx[:-1]] == labels[idx[1:]]))
        for date, idx in groups.items()
    }


def statistics(
    labels: np.ndarray, groups: dict[str, np.ndarray], regimes: dict[str, int]
) -> dict[str, float]:
    counts = same_counts(labels, groups)
    pairs = {date: len(indices) - 1 for date, indices in groups.items()}
    selected = {
        "pooled_within_date": list(groups),
        "regime_1_dates": [date for date in groups if regimes[date] == 1],
        "regime_2_dates": [date for date in groups if regimes[date] == 2],
    }
    return {
        key: sum(counts[date] for date in dates) / sum(pairs[date] for date in dates)
        for key, dates in selected.items()
    }


def expectations(
    labels: np.ndarray, groups: dict[str, np.ndarray], regimes: dict[str, int]
) -> dict[str, float]:
    expected_counts = {}
    pairs = {}
    for date, indices in groups.items():
        counts = Counter(labels[indices])
        n = len(indices)
        fraction = sum(count * (count - 1) for count in counts.values()) / (n * (n - 1))
        pairs[date] = n - 1
        expected_counts[date] = fraction * pairs[date]
    selected = {
        "pooled_within_date": list(groups),
        "regime_1_dates": [date for date in groups if regimes[date] == 1],
        "regime_2_dates": [date for date in groups if regimes[date] == 2],
    }
    return {
        key: sum(expected_counts[date] for date in dates) / sum(pairs[date] for date in dates)
        for key, dates in selected.items()
    }


def permutation_distributions(
    labels: np.ndarray,
    groups: dict[str, np.ndarray],
    regimes: dict[str, int],
    repetitions: int,
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
    output = {key: np.empty(repetitions) for key in KEYS}
    for repetition in range(repetitions):
        permuted = labels.copy()
        for indices in groups.values():
            permuted[indices] = labels[rng.permutation(indices)]
        values = statistics(permuted, groups, regimes)
        for key in KEYS:
            output[key][repetition] = values[key]
    return output


def summarize(observed: float, expected: float, null: np.ndarray) -> dict[str, Any]:
    repetitions = len(null)
    median = float(np.quantile(null, 0.5, method="linear"))
    lower = (int(np.count_nonzero(null <= observed)) + 1) / (repetitions + 1)
    upper = (int(np.count_nonzero(null >= observed)) + 1) / (repetitions + 1)
    return {
        "observed_same_policy_adjacency_fraction": observed,
        "analytic_exchangeability_expectation": expected,
        "permutation_median": median,
        "permutation_q025": float(np.quantile(null, 0.025, method="linear")),
        "permutation_q975": float(np.quantile(null, 0.975, method="linear")),
        "observed_minus_permutation_median": observed - median,
        "lower_tail_p": lower,
        "upper_tail_p": upper,
        "two_sided_p": min(1.0, 2 * min(lower, upper)),
        "permutations": repetitions,
    }


def classify(analyses: dict[str, dict[str, Any]]) -> str:
    pooled = analyses["pooled_within_date"]
    if pooled["two_sided_p"] <= 0.01 and abs(pooled["observed_minus_permutation_median"]) >= 0.10:
        return "material_pooled_within_date_policy_sequence_structure"
    if pooled["two_sided_p"] <= 0.01 or any(
        analyses[key]["two_sided_p"] <= 0.005 for key in ("regime_1_dates", "regime_2_dates")
    ):
        return "regime_specific_or_small_within_date_policy_sequence_structure"
    return "no_detectable_within_date_policy_sequence_structure_at_fixed_resolution"


def synthetic_controls() -> dict[str, bool]:
    rows = [
        {"date": "a", "group": 1, "timestamp": 1},
        {"date": "a", "group": 1, "timestamp": 2},
        {"date": "a", "group": 1, "timestamp": 3},
        {"date": "b", "group": 2, "timestamp": 4},
        {"date": "b", "group": 2, "timestamp": 5},
        {"date": "b", "group": 2, "timestamp": 6},
    ]
    groups, regimes = date_groups(rows)
    constant = np.array(["x"] * 6)
    alternating = np.array(["x", "y", "x", "y", "x", "y"])
    small = np.array(["a", "a", "b"])
    orders = set(itertools.permutations(small.tolist()))
    enum_mean = np.mean([
        np.count_nonzero(np.array(order[:-1]) == np.array(order[1:])) / 2
        for order in orders
    ])
    formula = sum(n * (n - 1) for n in Counter(small).values()) / 6
    first = permutation_distributions(
        alternating, groups, regimes, 99, np.random.Generator(np.random.PCG64(SEED))
    )
    second = permutation_distributions(
        alternating, groups, regimes, 99, np.random.Generator(np.random.PCG64(SEED))
    )
    return {
        "constant_one": all(value == 1 for value in statistics(constant, groups, regimes).values()),
        "alternating_zero": all(value == 0 for value in statistics(alternating, groups, regimes).values()),
        "analytic_matches_enumeration": bool(np.isclose(enum_mean, formula)),
        "deterministic_replay": all(np.array_equal(first[key], second[key]) for key in KEYS),
    }


def staged_validation(rows: list[dict[str, Any]]) -> dict[str, Any]:
    controls = synthetic_controls()
    require(all(controls.values()), "controls")
    groups, regimes = date_groups(rows)
    require(len(groups) == EXPECTED_DATES, "date group count")
    pairs = {
        key: sum(
            len(groups[date]) - 1
            for date in groups
            if key == "pooled_within_date"
            or regimes[date] == (1 if key == "regime_1_dates" else 2)
        )
        for key in KEYS
    }
    require(pairs == EXPECTED_PAIR_COUNTS, "pair accounting")
    labels = np.array([EXPECTED_POLICIES[index % 4] for index in range(len(rows))])
    rehearsal = permutation_distributions(
        labels, groups, regimes, 999, np.random.Generator(np.random.PCG64(SEED))
    )
    return {
        "schema": "h210-phail-within-date-policy-sequence-stage-v1",
        "episode_count": len(rows),
        "date_count": len(groups),
        "pair_counts": pairs,
        "synthetic_controls": controls,
        "synthetic_rehearsal_complete": all(len(rehearsal[key]) == 999 for key in KEYS),
        "material_within_date_adjacency_computed": False,
    }


def build() -> dict[str, Any]:
    rows = load_join()
    controls = synthetic_controls()
    require(all(controls.values()), "controls")
    groups, regimes = date_groups(rows)
    require(len(groups) == EXPECTED_DATES, "date group count")
    labels = np.array([row["policy"] for row in rows])
    observed = statistics(labels, groups, regimes)
    expected = expectations(labels, groups, regimes)
    nulls = permutation_distributions(
        labels, groups, regimes, PERMUTATIONS, np.random.Generator(np.random.PCG64(SEED))
    )
    analyses = {
        key: summarize(observed[key], expected[key], nulls[key]) for key in KEYS
    }
    for key, pairs in EXPECTED_PAIR_COUNTS.items():
        analyses[key]["adjacent_pair_count"] = pairs
    result = {
        "schema": "h210-phail-within-date-policy-sequence-v1",
        "status": "result_exposed_exploratory",
        "protocol_sha256": sha256(PROTOCOL),
        "input_sha256": {path.name: sha256(path) for path in EXPECTED_HASHES},
        "episode_count": len(rows),
        "date_count": len(groups),
        "date_counts_by_regime": {
            str(regime): sum(value == regime for value in regimes.values()) for regime in (1, 2)
        },
        "seed_text": SEED_TEXT,
        "pcg64_seed": str(SEED),
        "permutations": PERMUTATIONS,
        "synthetic_controls": controls,
        "analyses": analyses,
        "classification": classify(analyses),
        "permutation_reference_treated_as_assignment_law": False,
        "date_treated_as_physical_session_or_cause": False,
        "state_or_performance_opened": False,
        "outcome_analysis_authorized": False,
    }
    return result


def validate(result: dict[str, Any]) -> None:
    require(result["schema"] == "h210-phail-within-date-policy-sequence-v1", "schema")
    require(result["status"] == "result_exposed_exploratory", "status")
    require(result["protocol_sha256"] == sha256(PROTOCOL), "protocol")
    require(
        result["input_sha256"] == {path.name: expected for path, expected in EXPECTED_HASHES.items()},
        "input hashes",
    )
    require(result["episode_count"] == EXPECTED_EPISODES, "episodes")
    require(result["date_count"] == EXPECTED_DATES, "dates")
    require(result["date_counts_by_regime"] == {"1": 7, "2": 6}, "date regimes")
    require(result["pcg64_seed"] == str(SEED), "seed")
    require(all(result["synthetic_controls"].values()), "controls")
    require(set(result["analyses"]) == set(KEYS), "analyses")
    for key, pairs in EXPECTED_PAIR_COUNTS.items():
        analysis = result["analyses"][key]
        require(analysis["adjacent_pair_count"] == pairs, f"{key} pairs")
        require(analysis["permutations"] == PERMUTATIONS, f"{key} permutations")
        require(0 <= analysis["observed_same_policy_adjacency_fraction"] <= 1, f"{key} observed")
        require(0 < analysis["two_sided_p"] <= 1, f"{key} p")
    require(result["classification"] == classify(result["analyses"]), "classification")
    require(result["classification"] in CLASSIFICATIONS, "classification value")
    require(result["permutation_reference_treated_as_assignment_law"] is False, "assignment scope")
    require(result["date_treated_as_physical_session_or_cause"] is False, "date scope")
    require(result["state_or_performance_opened"] is False, "data scope")
    require(result["outcome_analysis_authorized"] is False, "outcome scope")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    require(not (args.stage and args.check), "choose one")
    if args.stage:
        print(json.dumps(staged_validation(load_join()), indent=2, sort_keys=True))
        return
    candidate = build()
    validate(candidate)
    if args.check:
        require(candidate == json.loads(OUTPUT.read_text()), "exact rebuild")
        print("OK: H210 within-date policy-sequence result reproduces")
    else:
        OUTPUT.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n")
        print(json.dumps(candidate, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
