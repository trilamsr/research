#!/usr/bin/env python3
"""Compare OSCAR's joined 63-session real panel with printed Figure 1 bars."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import spearmanr


def winners(values: dict[str, float]) -> list[str]:
    maximum = max(values.values())
    return sorted(
        policy
        for policy, value in values.items()
        if np.isclose(value, maximum, atol=1e-12, rtol=0)
    )


def portable_path(path: Path) -> str:
    parts = path.parts
    if "research" in parts:
        last_research = max(
            index for index, part in enumerate(parts) if part == "research"
        )
        return str(Path(*parts[last_research:]))
    return path.name


def analyze(join_path: Path, printed_path: Path) -> dict[str, Any]:
    join = json.loads(join_path.read_text(encoding="utf-8"))
    joined_records = join["real_outcomes_for_released_sessions"]
    joined_real = {
        record["printed_name"]: record["real_binary_success_rate_pct"]
        for record in joined_records.values()
    }

    printed_real = {}
    printed_wm = {}
    with printed_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(
            line for line in handle if not line.startswith("#")
        ):
            policy = row["policy"]
            printed_real[policy] = float(row["real_sr_pct"])
            printed_wm[policy] = float(row["wm_sr_pct"])

    if set(joined_real) != set(printed_real):
        raise ValueError("joined and printed policy rosters differ")
    order = sorted(joined_real)
    joined_vector = np.array([joined_real[p] for p in order])
    printed_real_vector = np.array([printed_real[p] for p in order])
    printed_wm_vector = np.array([printed_wm[p] for p in order])
    wm_winners = winners(printed_wm)
    joined_real_best = max(joined_real.values())

    absolute_differences = {
        policy: abs(joined_real[policy] - printed_real[policy])
        for policy in order
    }
    return {
        "inputs": {
            "joined_panel": portable_path(join_path),
            "printed_bars": portable_path(printed_path),
            "joined_real_denominator_per_policy": 63,
            "printed_wm_inferred_denominator_per_policy": 65,
        },
        "decision": {
            "joined_release_real_winners": winners(joined_real),
            "printed_real_winners": winners(printed_real),
            "printed_wm_winners": wm_winners,
            "joined_release_real_regret_of_printed_wm_winner_pp": (
                joined_real_best
                - max(joined_real[policy] for policy in wm_winners)
            ),
        },
        "comparison": {
            "pearson_joined_real_vs_printed_wm": float(
                np.corrcoef(joined_vector, printed_wm_vector)[0, 1]
            ),
            "spearman_joined_real_vs_printed_wm": float(
                spearmanr(joined_vector, printed_wm_vector).statistic
            ),
            "pearson_joined_real_vs_printed_real": float(
                np.corrcoef(joined_vector, printed_real_vector)[0, 1]
            ),
            "maximum_absolute_joined_vs_printed_real_difference_pp": max(
                absolute_differences.values()
            ),
            "policy_with_maximum_absolute_difference": sorted(
                policy
                for policy, difference in absolute_differences.items()
                if np.isclose(
                    difference,
                    max(absolute_differences.values()),
                    atol=1e-12,
                    rtol=0,
                )
            ),
        },
        "scope": (
            "Source-discrepancy diagnostic only. The joined real outcomes cover "
            "the 63 released session IDs, while the printed world-model bars "
            "imply 65 sessions and the printed real bars use another unstated "
            "RoboArena aggregation. The cross-vector correlation and regret "
            "are not an exact matched-session evaluator estimate."
        ),
    }


def main() -> None:
    family = Path(__file__).resolve().parent
    project = family.parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--join",
        type=Path,
        default=family / "result-oscar-roboarena-join.json",
    )
    parser.add_argument(
        "--printed",
        type=Path,
        default=(
            project
            / "research/corpus-reporting-audit/sources/source-oscar.csv"
        ),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=family / "result-oscar-joined-panel.json",
    )
    args = parser.parse_args()
    result = analyze(args.join, args.printed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
