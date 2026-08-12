#!/usr/bin/env python3
"""Audit probability-level calibration in the retained WM-PolicyEval panels."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
INPUT = HERE.parent / "corpus-reporting-audit" / "sources" / "source-wm-policyeval.csv"
PROTOCOL = HERE / "protocol-wm-probability-calibration-audit.md"
OUTPUT = HERE / "result-wm-probability-calibration-audit.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows() -> list[dict[str, str]]:
    with INPUT.open(encoding="utf-8") as handle:
        return list(
            csv.DictReader(
                line
                for line in handle
                if line.strip() and not line.startswith("#")
            )
        )


def load_panels() -> dict[str, dict[str, object]]:
    rows = read_rows()
    panels: dict[str, dict[str, object]] = {}
    for model in sorted({row["world_model"] for row in rows}):
        selected = [row for row in rows if row["world_model"] == model]
        policies = sorted({row["policy"] for row in selected})
        tasks = sorted({row["task"] for row in selected})
        require(len(selected) == 12, f"{model}: expected 12 cells")
        require(len(policies) == 3 and len(tasks) == 4, f"{model}: roster changed")
        panels[model] = {
            "policies": policies,
            "tasks": tasks,
            "rows": [
                {
                    "policy": row["policy"],
                    "task": row["task"],
                    "real": float(row["actual_success_rate"]),
                    "predicted": float(row["predicted_success_rate"]),
                }
                for row in selected
            ],
        }
    require(set(panels) == {"Cosmos", "IRASim"}, "unexpected evaluator roster")
    return panels


def ols(real: np.ndarray, predicted: np.ndarray) -> tuple[float, float]:
    require(real.shape == predicted.shape, "OLS arrays differ in shape")
    require(real.ndim == 1 and real.size >= 3, "OLS needs at least three cells")
    centered_predicted = predicted - np.mean(predicted)
    denominator = float(np.dot(centered_predicted, centered_predicted))
    require(denominator > 0, "predicted values have zero variance")
    slope = float(
        np.dot(centered_predicted, real - np.mean(real)) / denominator
    )
    intercept = float(np.mean(real) - slope * np.mean(predicted))
    return intercept, slope


def metrics(rows: list[dict[str, object]]) -> dict[str, float]:
    require(len(rows) >= 3, "at least three cells required")
    real = np.array([float(row["real"]) for row in rows], dtype=float)
    predicted = np.array([float(row["predicted"]) for row in rows], dtype=float)
    require(np.all((real >= 0) & (real <= 1)), "real rate outside [0,1]")
    require(
        np.all((predicted >= 0) & (predicted <= 1)),
        "predicted rate outside [0,1]",
    )
    rate_mse = float(np.mean((predicted - real) ** 2))
    empirical_brier = float(np.mean(predicted**2 - 2 * predicted * real + real))
    empirical_outcome_variance = float(np.mean(real * (1 - real)))
    require(
        abs(empirical_brier - rate_mse - empirical_outcome_variance) <= 1e-15,
        "Brier decomposition failed",
    )
    intercept, slope = ols(real, predicted)
    return {
        "cell_rate_mse": rate_mse,
        "empirical_individual_outcome_brier": empirical_brier,
        "empirical_outcome_variance_component": empirical_outcome_variance,
        "calibration_in_the_large_predicted_minus_real": float(
            np.mean(predicted) - np.mean(real)
        ),
        "ols_intercept_real_on_predicted": intercept,
        "ols_slope_real_on_predicted": slope,
        "pearson_r": float(np.corrcoef(predicted, real)[0, 1]),
    }


def selection(rows: list[dict[str, object]], policies: list[str]) -> dict[str, object]:
    real_means = {
        policy: float(
            np.mean([row["real"] for row in rows if row["policy"] == policy])
        )
        for policy in policies
    }
    predicted_means = {
        policy: float(
            np.mean([row["predicted"] for row in rows if row["policy"] == policy])
        )
        for policy in policies
    }
    real_winner = max(real_means, key=real_means.__getitem__)
    predicted_winner = max(predicted_means, key=predicted_means.__getitem__)
    return {
        "real_policy_means": real_means,
        "predicted_policy_means": predicted_means,
        "real_winner": real_winner,
        "predicted_winner": predicted_winner,
        "displayed_real_regret": (
            real_means[real_winner] - real_means[predicted_winner]
        ),
    }


def task_deletions(
    rows: list[dict[str, object]], tasks: list[str]
) -> dict[str, object]:
    records = []
    for omitted in tasks:
        retained = [row for row in rows if row["task"] != omitted]
        records.append({"omitted_task": omitted, **metrics(retained)})
    fields = (
        "cell_rate_mse",
        "empirical_individual_outcome_brier",
        "calibration_in_the_large_predicted_minus_real",
        "ols_intercept_real_on_predicted",
        "ols_slope_real_on_predicted",
    )
    ranges = {
        field: {
            "minimum": min(row[field] for row in records),
            "maximum": max(row[field] for row in records),
        }
        for field in fields
    }
    return {"rows": records, "ranges": ranges}


def heldout_affine_recalibration(
    rows: list[dict[str, object]], tasks: list[str]
) -> dict[str, object]:
    folds = []
    uncalibrated_errors: list[float] = []
    calibrated_errors: list[float] = []
    crossfitted_rows: list[dict[str, object]] = []
    for omitted in tasks:
        training = [row for row in rows if row["task"] != omitted]
        heldout = [row for row in rows if row["task"] == omitted]
        training_real = np.array([row["real"] for row in training], dtype=float)
        training_predicted = np.array(
            [row["predicted"] for row in training], dtype=float
        )
        intercept, slope = ols(training_real, training_predicted)
        heldout_real = np.array([row["real"] for row in heldout], dtype=float)
        heldout_predicted = np.array(
            [row["predicted"] for row in heldout], dtype=float
        )
        recalibrated = intercept + slope * heldout_predicted
        raw_error = (heldout_predicted - heldout_real) ** 2
        calibrated_error = (recalibrated - heldout_real) ** 2
        uncalibrated_errors.extend(raw_error.tolist())
        calibrated_errors.extend(calibrated_error.tolist())
        for row, value in zip(heldout, recalibrated, strict=True):
            crossfitted_rows.append(
                {
                    "policy": row["policy"],
                    "task": row["task"],
                    "recalibrated": float(value),
                }
            )
        folds.append(
            {
                "heldout_task": omitted,
                "training_intercept": intercept,
                "training_slope": slope,
                "heldout_uncalibrated_rate_mse": float(np.mean(raw_error)),
                "heldout_recalibrated_rate_mse": float(
                    np.mean(calibrated_error)
                ),
            }
        )
    policies = sorted({str(row["policy"]) for row in rows})
    policy_means = {
        policy: float(
            np.mean(
                [
                    row["recalibrated"]
                    for row in crossfitted_rows
                    if row["policy"] == policy
                ]
            )
        )
        for policy in policies
    }
    ordered = sorted(policy_means.items(), key=lambda item: item[1], reverse=True)
    return {
        "folds": folds,
        "pooled_uncalibrated_rate_mse": float(np.mean(uncalibrated_errors)),
        "pooled_recalibrated_rate_mse": float(np.mean(calibrated_errors)),
        "recalibration_reduces_pooled_rate_mse": bool(
            np.mean(calibrated_errors) < np.mean(uncalibrated_errors)
        ),
        "heldout_tasks_improved": sum(
            fold["heldout_recalibrated_rate_mse"]
            < fold["heldout_uncalibrated_rate_mse"]
            for fold in folds
        ),
        "crossfitted_policy_means": policy_means,
        "crossfitted_winner": ordered[0][0],
        "crossfitted_winner_margin": ordered[0][1] - ordered[1][1],
    }


def panel_result(panel: dict[str, object]) -> dict[str, object]:
    rows = panel["rows"]
    policies = panel["policies"]
    tasks = panel["tasks"]
    full_metrics = metrics(rows)
    selection_result = selection(rows, policies)
    intercept = full_metrics["ols_intercept_real_on_predicted"]
    slope = full_metrics["ols_slope_real_on_predicted"]
    require(slope > 0, "full-panel affine slope is not positive")
    transformed_policy_means = {
        policy: intercept + slope * value
        for policy, value in selection_result["predicted_policy_means"].items()
    }
    transformed_winner = max(
        transformed_policy_means, key=transformed_policy_means.__getitem__
    )
    require(
        transformed_winner == selection_result["predicted_winner"],
        "positive affine recalibration changed aggregate policy winner",
    )
    return {
        "metrics": full_metrics,
        "selection": selection_result,
        "task_deletion": task_deletions(rows, tasks),
        "task_heldout_affine_recalibration": heldout_affine_recalibration(
            rows, tasks
        ),
        "full_panel_affine_selection_check": {
            "slope_positive": True,
            "transformed_policy_means": transformed_policy_means,
            "transformed_winner": transformed_winner,
            "winner_preserved": True,
        },
        "score_name_diagnosis": {
            "cell_rate_mse_is_brier": False,
            "difference_equals_empirical_outcome_variance": True,
        },
    }


def validate_stage_zero() -> dict[str, object]:
    panels = load_panels()
    rows = []
    for model, panel in panels.items():
        counts = np.array([20 * row["real"] for row in panel["rows"]])
        require(
            np.allclose(counts, np.round(counts), atol=1e-12),
            f"{model}: noninteger real count",
        )
        result = metrics(panel["rows"])
        expected_r = 0.7193 if model == "Cosmos" else 0.2772
        require(
            abs(result["pearson_r"] - expected_r) < 0.0001,
            f"{model}: plotted Pearson changed",
        )
        require(
            result["cell_rate_mse"]
            != result["empirical_individual_outcome_brier"],
            f"{model}: rate MSE mislabeled as Brier",
        )
        rows.append(
            {
                "model": model,
                "cells": len(panel["rows"]),
                "policies": len(panel["policies"]),
                "tasks": len(panel["tasks"]),
                "pearson_r": result["pearson_r"],
                "brier_identity_residual": (
                    result["empirical_individual_outcome_brier"]
                    - result["cell_rate_mse"]
                    - result["empirical_outcome_variance_component"]
                ),
            }
        )
    return {"rows": rows}


def build() -> dict[str, object]:
    stage_zero = validate_stage_zero()
    panels = load_panels()
    results = {model: panel_result(panel) for model, panel in panels.items()}
    return {
        "schema": "wm-probability-calibration-audit-v1",
        "status": "pass",
        "classification": "orthogonal_level_error_with_selection_invariance",
        "outcome_status": "review_triggered_outcome_exposed_exploratory",
        "protocol_sha256": sha256(PROTOCOL),
        "implementation_sha256": sha256(Path(__file__)),
        "input_sha256": sha256(INPUT),
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "stage_zero": stage_zero,
        "panels": results,
        "interpretation": (
            "Probability-level fit adds an orthogonal descriptive axis on these "
            "retained panels. Positive affine recalibration preserves the aggregate "
            "selection, so it neither repairs nor creates the argmax result."
        ),
        "boundary": (
            "Twelve outcome-exposed cells per evaluator, four task deletion folds, "
            "unknown simulator denominator, and no task/policy sampling frame."
        ),
    }


def stable(value):
    if isinstance(value, float):
        return round(value, 12)
    if isinstance(value, dict):
        return {key: stable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [stable(item) for item in value]
    return value


def validate(data: dict[str, object]) -> None:
    require(data == stable(build()), "stored calibration audit differs")


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=OUTPUT)
    args = parser.parse_args()
    result = stable(build())
    if args.write:
        args.out.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"WROTE {args.out}")
    else:
        validate(json.loads(args.out.read_text(encoding="utf-8")))
        print("OK: WM probability-calibration audit")


if __name__ == "__main__":
    main()
