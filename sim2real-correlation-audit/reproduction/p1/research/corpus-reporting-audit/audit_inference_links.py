#!/usr/bin/env python3
"""Validate the broadened paper-level inference-link recoding."""

from __future__ import annotations

import csv
from pathlib import Path


HERE = Path(__file__).resolve().parent
RECORD = HERE / "result-inference-link-recoding.csv"
ESTIMANDS = HERE / "result-estimand-grid.csv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate() -> dict[str, int]:
    rows = read(RECORD)
    roster = {(row["paper"], row["arxiv_version"]) for row in read(ESTIMANDS)}
    recoded = {(row["paper"], row["pinned_version"]) for row in rows}
    if len(rows) != 26 or len(recoded) != 26:
        raise ValueError("inference-link recoding must contain 26 unique papers")
    if recoded != roster:
        raise ValueError("inference-link roster/version mismatch")
    if any(row["formal_population_prediction"] != "no" for row in rows):
        raise ValueError("formal population-prediction coding changed")
    held_out = sum(
        "held_out" in row["inferential_link"] for row in rows
    )
    fixed = sum("fixed_benchmark" in row["target_scope"] for row in rows)
    if held_out < 1 or fixed < 1:
        raise ValueError("broadened schema collapsed non-sampling evidence")
    for row in rows:
        for field in (
            "target_scope",
            "inferential_link",
            "uncertainty_type",
            "claim_type",
            "primary_source_basis",
            "status",
        ):
            if not row[field].strip():
                raise ValueError(f"missing {field} for {row['paper']}")
    return {
        "papers": len(rows),
        "held_out_predictive": held_out,
        "fixed_benchmark": fixed,
        "formal_population_prediction": 0,
    }


def main() -> None:
    counts = validate()
    print(
        "inference-link recoding schema/roster consistent: "
        f"{counts['papers']} papers, "
        f"{counts['held_out_predictive']} with held-out links, "
        f"{counts['fixed_benchmark']} with fixed-benchmark scope, "
        "0 formal population predictions"
    )


if __name__ == "__main__":
    main()
