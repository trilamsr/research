import json

import pytest

import analyze_wm_heterogeneous_simulator_evidence as hetero
import analyze_wm_missing_simulator_uncertainty as h239


def test_invalid_evidence_fails_closed() -> None:
    panel = h239.load_panels()["IRASim"]
    with pytest.raises(ValueError):
        hetero.evaluate(panel, (1, 2), 100, 1)
    with pytest.raises(ValueError):
        hetero.evaluate(panel, (1, -1, 2), 100, 1)
    with pytest.raises(ValueError):
        hetero.evaluate(panel, (1, 2, 3), 0, 1)


def test_common_positive_evidence_preserves_displayed_posterior_mean_action() -> None:
    panel = h239.load_panels()["IRASim"]
    row = hetero.evaluate(panel, (10, 10, 10), 10_000, 11)
    assert row["posterior_mean_sim_winner_set"] == ["Octo-Base"]


def test_canonical_result_reverses_common_evidence_direction() -> None:
    result = json.loads(hetero.OUTPUT.read_text(encoding="utf-8"))
    assert result["status"] == "pass"
    assert result["panels"]["IRASim"]["scenarios"]["common_10"][
        "latent_winner_concordance"
    ] < 0.5
    assert result["panels"]["IRASim"]["scenarios"]["openvla_10"][
        "latent_winner_concordance"
    ] > 0.5
    assert result["panels"]["IRASim"]["scenarios"]["openvla_0"][
        "latent_winner_concordance"
    ] > 0.5


def test_canonical_result_reproduces() -> None:
    assert json.loads(hetero.OUTPUT.read_text(encoding="utf-8")) == hetero.build()
