import json

import audit_wm_nonlinear_calibration_sensitivity as nonlinear
import audit_wm_probability_calibration as h240


def test_pav_known_answer() -> None:
    rows = [
        {"predicted": 0.1, "real": 0.5},
        {"predicted": 0.2, "real": 0.1},
        {"predicted": 0.3, "real": 0.4},
    ]
    mapping = nonlinear.isotonic_level_map(rows)
    assert [row["isotonic_fitted_rate"] for row in mapping] == [0.3, 0.3, 0.4]


def test_murphy_identity() -> None:
    for panel in h240.load_panels().values():
        result = nonlinear.murphy(panel["rows"])
        assert abs(
            result["brier"]
            - result["reliability"]
            + result["resolution"]
            - result["uncertainty"]
        ) <= 1e-12


def test_canonical_irarsim_flip_is_in_sample_only() -> None:
    result = json.loads(nonlinear.OUTPUT.read_text(encoding="utf-8"))
    irasim = result["panels"]["IRASim"]
    assert irasim["original_winner"] == "Octo-Base"
    assert irasim["isotonic_winner"] == "OpenVLA"
    assert irasim["winner_changed"] is True
    assert "in-sample" in result["scope"]


def test_canonical_result_reproduces() -> None:
    assert json.loads(nonlinear.OUTPUT.read_text(encoding="utf-8")) == (
        nonlinear.build()
    )
