import json

import numpy as np
import pytest

import audit_wm_probability_calibration as calibration


def test_stage_zero_inputs_and_score_identity() -> None:
    stage = calibration.validate_stage_zero()
    assert len(stage["rows"]) == 2
    assert all(row["cells"] == 12 for row in stage["rows"])
    assert all(abs(row["brier_identity_residual"]) <= 1e-15 for row in stage["rows"])


def test_rate_mse_is_not_individual_outcome_brier() -> None:
    for panel in calibration.load_panels().values():
        result = calibration.metrics(panel["rows"])
        assert result["cell_rate_mse"] != result[
            "empirical_individual_outcome_brier"
        ]
        assert np.isclose(
            result["empirical_individual_outcome_brier"],
            result["cell_rate_mse"]
            + result["empirical_outcome_variance_component"],
            atol=1e-15,
        )


def test_positive_affine_map_preserves_aggregate_winner() -> None:
    result = calibration.build()
    for panel in result["panels"].values():
        check = panel["full_panel_affine_selection_check"]
        assert check["slope_positive"]
        assert check["winner_preserved"]
        assert check["transformed_winner"] == panel["selection"]["predicted_winner"]


def test_task_deletion_has_four_fixed_folds() -> None:
    result = calibration.build()
    for panel in result["panels"].values():
        assert len(panel["task_deletion"]["rows"]) == 4
        assert len(panel["task_heldout_affine_recalibration"]["folds"]) == 4


def test_invalid_ols_and_metrics_fail_closed() -> None:
    with pytest.raises(ValueError):
        calibration.ols(np.array([0.0, 1.0]), np.array([0.0]))
    with pytest.raises(ValueError):
        calibration.ols(np.array([0.0, 0.5, 1.0]), np.ones(3))
    with pytest.raises(ValueError):
        calibration.metrics(
            [
                {"real": 0.0, "predicted": 0.0},
                {"real": 0.5, "predicted": 0.5},
            ]
        )


def test_canonical_artifact_parity() -> None:
    expected = json.loads(calibration.OUTPUT.read_text(encoding="utf-8"))
    calibration.validate(expected)
