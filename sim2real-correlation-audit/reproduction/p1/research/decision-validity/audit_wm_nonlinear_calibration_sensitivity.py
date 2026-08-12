#!/usr/bin/env python3
"""Nonlinear calibration and Murphy-decomposition sensitivity for WM panels."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path

import numpy as np

import audit_wm_probability_calibration as h240


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "protocol-wm-nonlinear-calibration-sensitivity.md"
OUTPUT = HERE / "result-wm-nonlinear-calibration-sensitivity.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def isotonic_level_map(rows: list[dict[str, object]]) -> list[dict[str, float]]:
    grouped: dict[float, list[float]] = {}
    for row in rows:
        grouped.setdefault(float(row["predicted"]), []).append(float(row["real"]))
    blocks = [
        {
            "levels": [level],
            "weight": float(len(values)),
            "sum": float(sum(values)),
        }
        for level, values in sorted(grouped.items())
    ]
    index = 0
    while index < len(blocks) - 1:
        left = blocks[index]["sum"] / blocks[index]["weight"]
        right = blocks[index + 1]["sum"] / blocks[index + 1]["weight"]
        if left <= right + 1e-15:
            index += 1
            continue
        blocks[index : index + 2] = [
            {
                "levels": blocks[index]["levels"] + blocks[index + 1]["levels"],
                "weight": blocks[index]["weight"] + blocks[index + 1]["weight"],
                "sum": blocks[index]["sum"] + blocks[index + 1]["sum"],
            }
        ]
        index = max(0, index - 1)
    mapping = []
    for block_index, block in enumerate(blocks):
        fitted = block["sum"] / block["weight"]
        for level in block["levels"]:
            mapping.append(
                {
                    "predicted_level": float(level),
                    "isotonic_fitted_rate": float(fitted),
                    "block_index": block_index,
                }
            )
    mapping.sort(key=lambda row: row["predicted_level"])
    require(
        all(
            mapping[index]["isotonic_fitted_rate"]
            <= mapping[index + 1]["isotonic_fitted_rate"] + 1e-15
            for index in range(len(mapping) - 1)
        ),
        "isotonic map is not monotone",
    )
    return mapping


def murphy(rows: list[dict[str, object]]) -> dict[str, float]:
    prevalence = float(np.mean([row["real"] for row in rows]))
    groups: dict[float, list[float]] = {}
    for row in rows:
        groups.setdefault(float(row["predicted"]), []).append(float(row["real"]))
    total = len(rows)
    reliability = 0.0
    resolution = 0.0
    for predicted, real_values in groups.items():
        weight = len(real_values) / total
        observed = float(np.mean(real_values))
        reliability += weight * (predicted - observed) ** 2
        resolution += weight * (observed - prevalence) ** 2
    uncertainty = prevalence * (1 - prevalence)
    brier = float(
        np.mean(
            [
                row["predicted"] ** 2
                - 2 * row["predicted"] * row["real"]
                + row["real"]
                for row in rows
            ]
        )
    )
    require(
        abs(brier - (reliability - resolution + uncertainty)) <= 1e-12,
        "Murphy decomposition failed",
    )
    return {
        "reliability": reliability,
        "resolution": resolution,
        "uncertainty": uncertainty,
        "brier": brier,
        "brier_skill_vs_empirical_prevalence": 1 - brier / uncertainty,
    }


def panel_result(panel: dict[str, object]) -> dict[str, object]:
    rows = panel["rows"]
    mapping = isotonic_level_map(rows)
    fitted_by_level = {
        row["predicted_level"]: row["isotonic_fitted_rate"] for row in mapping
    }
    policies = panel["policies"]
    raw_means = {
        policy: float(
            np.mean([row["predicted"] for row in rows if row["policy"] == policy])
        )
        for policy in policies
    }
    fitted_means = {
        policy: float(
            np.mean(
                [
                    fitted_by_level[float(row["predicted"])]
                    for row in rows
                    if row["policy"] == policy
                ]
            )
        )
        for policy in policies
    }
    original_winner = max(raw_means, key=raw_means.__getitem__)
    isotonic_winner = max(fitted_means, key=fitted_means.__getitem__)
    raw_mse = float(
        np.mean([(row["predicted"] - row["real"]) ** 2 for row in rows])
    )
    isotonic_mse = float(
        np.mean(
            [
                (
                    fitted_by_level[float(row["predicted"])] - row["real"]
                )
                ** 2
                for row in rows
            ]
        )
    )
    return {
        "isotonic_level_map": mapping,
        "raw_policy_means": raw_means,
        "isotonic_policy_means": fitted_means,
        "original_winner": original_winner,
        "isotonic_winner": isotonic_winner,
        "winner_changed": original_winner != isotonic_winner,
        "raw_cell_rate_mse": raw_mse,
        "isotonic_in_sample_cell_rate_mse": isotonic_mse,
        "murphy_forecast_level_decomposition": murphy(rows),
    }


def stable(value):
    if isinstance(value, float):
        return round(value, 12)
    if isinstance(value, dict):
        return {key: stable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [stable(item) for item in value]
    return value


def build() -> dict[str, object]:
    panels = h240.load_panels()
    results = {model: panel_result(panel) for model, panel in panels.items()}
    require(
        results["Cosmos"]["winner_changed"] is False,
        "Cosmos isotonic sensitivity changed",
    )
    require(
        results["IRASim"]["winner_changed"] is True
        and results["IRASim"]["isotonic_winner"] == "OpenVLA",
        "IRASim isotonic winner flip did not reproduce",
    )
    return stable(
        {
            "schema": "wm-nonlinear-calibration-sensitivity-v1",
            "status": "pass",
            "classification": (
                "affine_selection_invariance_does_not_extend_to_nonlinear_monotone_maps"
            ),
            "outcome_status": "domain_review_triggered_outcome_exposed_exploratory",
            "protocol_sha256": sha256(PROTOCOL),
            "implementation_sha256": sha256(Path(__file__)),
            "input_sha256": sha256(h240.INPUT),
            "runtime": {
                "python": platform.python_version(),
                "numpy": np.__version__,
            },
            "panels": results,
            "scope": (
                "Full-panel in-sample equal-cell isotonic shape sensitivity and "
                "finite forecast-level Murphy decomposition; not prospective "
                "calibration, selection repair, or transport evidence."
            ),
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=OUTPUT)
    args = parser.parse_args()
    result = build()
    if args.write:
        args.out.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"WROTE {args.out}")
    else:
        require(
            json.loads(args.out.read_text(encoding="utf-8")) == result,
            "stored nonlinear calibration result differs",
        )
        print("OK: WM nonlinear calibration sensitivity")


if __name__ == "__main__":
    main()
