import json

import numpy as np
import pytest

import analyze_wm_missing_simulator_uncertainty as wm


def test_panel_shapes_counts_and_displayed_winners() -> None:
    panels = wm.load_panels()
    assert set(panels) == {"Cosmos", "IRASim"}
    for panel in panels.values():
        assert np.asarray(panel["real_successes"]).shape == (3, 4)
        assert np.asarray(panel["sim_rates"]).shape == (3, 4)
        assert np.all(np.asarray(panel["real_successes"]) == np.round(
            np.asarray(panel["real_successes"])
        ))
    cosmos = panels["Cosmos"]
    irasim = panels["IRASim"]
    assert cosmos["candidates"][cosmos["displayed_sim_winner_index"]] == "OpenVLA"
    assert irasim["candidates"][irasim["displayed_sim_winner_index"]] == "Octo-Base"
    assert cosmos["candidates"][cosmos["displayed_real_winner_index"]] == "OpenVLA"
    assert irasim["candidates"][irasim["displayed_real_winner_index"]] == "OpenVLA"


def test_stage_zero_exchangeable_and_fixed_limits() -> None:
    stage = wm.validate_stage_zero()
    assert stage["zero_limit_checks"] == 6
    assert stage["fixed_display_checks"] == 2


def test_evaluate_rejects_invalid_inputs() -> None:
    panel = wm.load_panels()["Cosmos"]
    with pytest.raises(ValueError):
        wm.evaluate(panel, 0.0, 10.0, 100, 1)
    with pytest.raises(ValueError):
        wm.evaluate(panel, 1.0, -1.0, 100, 1)
    with pytest.raises(ValueError):
        wm.evaluate(panel, 1.0, 1.0, 0, 1)
    broken = dict(panel)
    broken["sim_rates"] = np.zeros((2, 4))
    with pytest.raises(ValueError):
        wm.evaluate(broken, 1.0, 1.0, 100, 1)


def test_canonical_result_contract() -> None:
    result = json.loads(wm.OUTPUT.read_text(encoding="utf-8"))
    assert result["status"] == "pass"
    assert result["panels"]["IRASim"]["stress_envelope"][
        "all_scenarios_below_one_half"
    ]
    assert not result["panels"]["Cosmos"]["stress_envelope"][
        "all_scenarios_above_one_half"
    ]
    assert any(
        value is not None
        for value in result["panels"]["Cosmos"]["stress_envelope"][
            "first_listed_evidence_size_above_one_half_by_prior"
        ].values()
    )


def test_canonical_artifact_parity() -> None:
    expected = json.loads(wm.OUTPUT.read_text(encoding="utf-8"))
    wm.validate(expected)
