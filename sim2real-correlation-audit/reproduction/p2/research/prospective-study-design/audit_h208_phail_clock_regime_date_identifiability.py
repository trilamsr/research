#!/usr/bin/env python3
"""Fixed H208 clock-regime/date identifiability audit."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np


FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h208-phail-clock-regime-date-identifiability.md"
COHORT = FAMILY / "result-h187-phail-context-support-sanitized.csv"
H206_PROJECTION = FAMILY / "projection-h206-phail-clock-offset-regimes.csv"
H206_RESULT = FAMILY / "result-h206-phail-monotonic-wall-clock-bridge.json"
H206_CHALLENGE = (
    FAMILY / "result-h206-phail-monotonic-wall-clock-bridge-independent-challenge.json"
)
H207_RESULT = FAMILY / "result-h207-phail-clock-regime-temporal-structure.json"
H207_CHALLENGE = (
    FAMILY
    / "result-h207-phail-clock-regime-temporal-structure-independent-challenge.json"
)
OUTPUT = FAMILY / "result-h208-phail-clock-regime-date-identifiability.json"

EXPECTED_HASHES = {
    COHORT: "ad43fca1da065a1cb7fd84dfa9afc5691c72ebe12e7f165c68a0050e51e87ebe",
    H206_PROJECTION: "7b7af23688e230325ec69070c8e5cd5523224990d7bc44defbe5b30f12c65529",
    H206_RESULT: "1b46e77400b15ecd886d165f13fca06b3f6834a0cc4f70082da4be4a39f51e19",
    H206_CHALLENGE: "6867989afb5a2c9938ee08126defa647b7a20b26f8c48f42a7d13cc5a4787268",
    H207_RESULT: "31ef2b4162157769bf9f99ce47f50865076b99e114c7a67592319ce8df2b2252",
    H207_CHALLENGE: "39839285b7a84acf2fb3a5b74afe18a3fb32d51e2491358d6b42ad24b80032e2",
}
EXPECTED_EPISODES = 594
EXPECTED_GROUP_SIZES = {1: 250, 2: 344}
CLASSIFICATIONS = {
    "date_aliased_with_complete_policy_regime_support",
    "date_aliased_with_policy_regime_support_gap",
    "date_separable_at_utc_day_resolution",
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


def verify_h206() -> None:
    result = json.loads(H206_RESULT.read_text())
    require(
        result["classification"] == "scale_separated_clock_offset_regimes",
        "H206 classification",
    )
    require(result["episode_count"] == EXPECTED_EPISODES, "H206 episode count")
    groups = {int(row["group_1h"]): row for row in result["one_hour_groups"]}
    require(set(groups) == {1, 2}, "H206 groups")
    for label, size in EXPECTED_GROUP_SIZES.items():
        require(groups[label]["episode_count"] == size, f"H206 group {label} size")
        require(
            groups[label]["wall_monotonic_discordant_pairs"] == 0,
            f"H206 group {label} order",
        )


def load_join() -> list[dict[str, Any]]:
    verify_hashes()
    verify_h206()
    cohort = read_csv(COHORT)
    projection = read_csv(H206_PROJECTION)
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
    cohort_by_id = {row["episode_id"]: row for row in cohort}
    require(set(cohort_by_id) == {row["episode_id"] for row in projection}, "join")
    joined: list[dict[str, Any]] = []
    counts: dict[int, int] = defaultdict(int)
    for projected in projection:
        source = cohort_by_id[projected["episode_id"]]
        for field in ("policy_model", "utc_date", "created_ts_ns"):
            require(source[field] == projected[field], f"{field} agreement")
        group = int(projected["group_1h"])
        require(group in EXPECTED_GROUP_SIZES, "group label")
        counts[group] += 1
        joined.append(
            {
                "episode_id": projected["episode_id"],
                "policy": projected["policy_model"],
                "date": projected["utc_date"],
                "group": group,
            }
        )
    require(dict(counts) == EXPECTED_GROUP_SIZES, "group sizes")
    return joined


def date_alias(rows: list[dict[str, Any]]) -> dict[str, Any]:
    dates = sorted({row["date"] for row in rows})
    date_regimes = {
        date: sorted({row["group"] for row in rows if row["date"] == date})
        for date in dates
    }
    exact_single_regime_per_date = all(
        len(regimes) == 1 for regimes in date_regimes.values()
    )
    regime_two_dates = [
        date for date, regimes in date_regimes.items() if regimes == [2]
    ]
    regime_vector = np.array([int(row["group"] == 2) for row in rows], dtype=int)
    reconstructed = np.array(
        [int(row["date"] in regime_two_dates) for row in rows], dtype=int
    )
    exact_indicator_reconstruction = bool(np.array_equal(regime_vector, reconstructed))
    date_matrix = np.column_stack(
        [
            np.array([int(row["date"] == date) for row in rows], dtype=float)
            for date in dates
        ]
    )
    date_rank = int(np.linalg.matrix_rank(date_matrix))
    augmented_rank = int(
        np.linalg.matrix_rank(np.column_stack([date_matrix, regime_vector]))
    )
    return {
        "date_count": len(dates),
        "date_regimes": date_regimes,
        "regime_2_alias_dates": regime_two_dates,
        "exact_single_regime_per_date": exact_single_regime_per_date,
        "exact_indicator_reconstruction": exact_indicator_reconstruction,
        "date_only_design_rank": date_rank,
        "date_plus_regime_design_rank": augmented_rank,
        "rank_increment": augmented_rank - date_rank,
    }


def policy_regime_table(rows: list[dict[str, Any]]) -> dict[str, Any]:
    policies = sorted({row["policy"] for row in rows})
    counts = {
        policy: {
            str(group): sum(
                row["policy"] == policy and row["group"] == group for row in rows
            )
            for group in (1, 2)
        }
        for policy in policies
    }
    cells = [counts[policy][str(group)] for policy in policies for group in (1, 2)]
    return {
        "policies": policies,
        "counts": counts,
        "all_policy_regime_cells_positive": all(cell > 0 for cell in cells),
        "minimum_cell_count": min(cells),
        "maximum_cell_count": max(cells),
    }


def composition_metrics(table: dict[str, Any]) -> dict[str, float]:
    policies = table["policies"]
    matrix = np.array(
        [
            [table["counts"][policy][str(group)] for policy in policies]
            for group in (1, 2)
        ],
        dtype=float,
    )
    require(np.all(matrix >= 0), "nonnegative table")
    require(np.all(matrix.sum(axis=1) > 0), "positive row totals")
    distributions = matrix / matrix.sum(axis=1, keepdims=True)
    total_variation = 0.5 * float(np.abs(distributions[0] - distributions[1]).sum())
    total = float(matrix.sum())
    expected = np.outer(matrix.sum(axis=1), matrix.sum(axis=0)) / total
    require(np.all(expected > 0), "positive expected counts")
    chi_square = float((np.square(matrix - expected) / expected).sum())
    cramers_v = math.sqrt(chi_square / total)
    return {
        "policy_distribution_total_variation": total_variation,
        "pearson_chi_square_descriptive": chi_square,
        "cramers_v": cramers_v,
    }


def classify(alias: dict[str, Any], table: dict[str, Any]) -> str:
    exact_alias = (
        alias["exact_single_regime_per_date"]
        and alias["exact_indicator_reconstruction"]
    )
    if exact_alias and table["all_policy_regime_cells_positive"]:
        return "date_aliased_with_complete_policy_regime_support"
    if exact_alias:
        return "date_aliased_with_policy_regime_support_gap"
    return "date_separable_at_utc_day_resolution"


def synthetic_controls() -> dict[str, bool]:
    nested = [
        {"date": "a", "group": 1, "policy": "p"},
        {"date": "a", "group": 1, "policy": "q"},
        {"date": "b", "group": 2, "policy": "p"},
        {"date": "b", "group": 2, "policy": "q"},
    ]
    crossed = [
        {"date": "a", "group": 1, "policy": "p"},
        {"date": "a", "group": 2, "policy": "p"},
        {"date": "b", "group": 2, "policy": "q"},
    ]
    gap = [
        {"date": "a", "group": 1, "policy": "p"},
        {"date": "b", "group": 2, "policy": "p"},
        {"date": "b", "group": 2, "policy": "q"},
    ]
    disjoint_table = {
        "policies": ["p", "q"],
        "counts": {"p": {"1": 1, "2": 0}, "q": {"1": 0, "2": 1}},
    }
    metrics = composition_metrics(disjoint_table)
    return {
        "nested_alias": (
            date_alias(nested)["exact_indicator_reconstruction"]
            and date_alias(nested)["rank_increment"] == 0
        ),
        "crossed_date_not_alias": (
            not date_alias(crossed)["exact_single_regime_per_date"]
            and not date_alias(crossed)["exact_indicator_reconstruction"]
        ),
        "complete_support": policy_regime_table(nested)[
            "all_policy_regime_cells_positive"
        ],
        "support_gap": not policy_regime_table(gap)[
            "all_policy_regime_cells_positive"
        ],
        "known_total_variation": math.isclose(
            metrics["policy_distribution_total_variation"], 1.0
        ),
        "known_cramers_v": math.isclose(metrics["cramers_v"], 1.0),
    }


def staged_validation(rows: list[dict[str, Any]]) -> dict[str, Any]:
    controls = synthetic_controls()
    require(all(controls.values()), "synthetic controls")
    return {
        "schema": "h208-phail-clock-regime-date-identifiability-stage-v1",
        "input_hashes_verified": True,
        "episode_count": len(rows),
        "group_sizes": {
            str(group): sum(row["group"] == group for row in rows)
            for group in (1, 2)
        },
        "synthetic_controls": controls,
        "material_date_alias_or_composition_metric_computed": False,
    }


def build() -> dict[str, Any]:
    rows = load_join()
    controls = synthetic_controls()
    require(all(controls.values()), "synthetic controls")
    alias = date_alias(rows)
    table = policy_regime_table(rows)
    metrics = composition_metrics(table)
    return {
        "schema": "h208-phail-clock-regime-date-identifiability-v1",
        "status": "result_exposed_exploratory",
        "protocol_sha256": sha256(PROTOCOL),
        "input_sha256": {
            path.name: sha256(path) for path in EXPECTED_HASHES
        },
        "episode_count": len(rows),
        "synthetic_controls": controls,
        "date_alias": alias,
        "policy_regime_support": table,
        "composition_metrics": metrics,
        "classification": classify(alias, table),
        "sampling_p_value_reported": False,
        "performance_or_later_state_opened": False,
        "clock_regime_treated_as_session_or_cause": False,
        "outcome_analysis_authorized": False,
        "decision_consequence": (
            "Exact date alias blocks separate clock-regime effect "
            "identification after saturated UTC-date adjustment on this "
            "release. Complete policy-regime cells establish only coarse "
            "structural overlap, not validity or precision."
        ),
    }


def validate(result: dict[str, Any]) -> None:
    require(
        result["schema"] == "h208-phail-clock-regime-date-identifiability-v1",
        "schema",
    )
    require(result["status"] == "result_exposed_exploratory", "status")
    require(result["protocol_sha256"] == sha256(PROTOCOL), "protocol")
    require(
        result["input_sha256"]
        == {path.name: expected for path, expected in EXPECTED_HASHES.items()},
        "input hashes",
    )
    require(result["episode_count"] == EXPECTED_EPISODES, "episode count")
    require(all(result["synthetic_controls"].values()), "synthetic controls")
    alias = result["date_alias"]
    table = result["policy_regime_support"]
    require(alias["date_count"] > 1, "date count")
    require(
        alias["date_plus_regime_design_rank"] >= alias["date_only_design_rank"],
        "rank order",
    )
    require(
        alias["rank_increment"]
        == alias["date_plus_regime_design_rank"] - alias["date_only_design_rank"],
        "rank increment",
    )
    require(table["minimum_cell_count"] >= 0, "minimum cell")
    require(table["maximum_cell_count"] >= table["minimum_cell_count"], "maximum cell")
    require(
        sum(
            table["counts"][policy][str(group)]
            for policy in table["policies"]
            for group in (1, 2)
        )
        == EXPECTED_EPISODES,
        "table total",
    )
    metrics = result["composition_metrics"]
    require(
        0 <= metrics["policy_distribution_total_variation"] <= 1,
        "total variation",
    )
    require(0 <= metrics["cramers_v"] <= 1, "Cramer's V")
    require(result["classification"] == classify(alias, table), "classification")
    require(result["classification"] in CLASSIFICATIONS, "classification value")
    require(result["sampling_p_value_reported"] is False, "sampling p value")
    require(
        result["performance_or_later_state_opened"] is False,
        "performance scope",
    )
    require(
        result["clock_regime_treated_as_session_or_cause"] is False,
        "regime scope",
    )
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
        print("OK: H208 clock-regime/date identifiability result reproduces")
    else:
        OUTPUT.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n")
        print(json.dumps(candidate, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
