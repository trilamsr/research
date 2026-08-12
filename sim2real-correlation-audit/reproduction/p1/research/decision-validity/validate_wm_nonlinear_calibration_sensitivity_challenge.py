#!/usr/bin/env python3
"""Validate the nonlinear calibration independent challenge."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
INPUT = HERE.parent / "corpus-reporting-audit" / "sources" / "source-wm-policyeval.csv"
PROTOCOL = HERE / "protocol-wm-nonlinear-calibration-sensitivity.md"
PRODUCER = HERE / "audit_wm_nonlinear_calibration_sensitivity.py"
PRODUCER_RESULT = HERE / "result-wm-nonlinear-calibration-sensitivity.json"
CHALLENGE = HERE / "result-wm-nonlinear-calibration-sensitivity-independent-challenge.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(data: dict[str, object]) -> None:
    assert data["schema"] == (
        "wm-nonlinear-calibration-sensitivity-independent-challenge-v1"
    )
    assert data["status"] == "pass"
    assert data["tolerance"] <= 1e-10
    assert data["numeric_comparisons"] == 68
    assert data["protocol_sha256"] == sha256(PROTOCOL)
    assert data["producer_sha256"] == sha256(PRODUCER)
    assert data["producer_result_sha256"] == sha256(PRODUCER_RESULT)
    assert data["input_sha256"] == sha256(INPUT)
    assert data["panels"]["Cosmos"]["winner_changed"] is False
    assert data["panels"]["IRASim"]["original_winner"] == "Octo-Base"
    assert data["panels"]["IRASim"]["isotonic_winner"] == "OpenVLA"
    assert data["panels"]["IRASim"]["winner_changed"] is True
    for panel in data["panels"].values():
        murphy = panel["murphy_forecast_level_decomposition"]
        assert abs(
            murphy["brier"]
            - murphy["reliability"]
            + murphy["resolution"]
            - murphy["uncertainty"]
        ) <= 1e-12


def main() -> None:
    validate(json.loads(CHALLENGE.read_text(encoding="utf-8")))
    print("OK: WM nonlinear calibration challenge binding")


if __name__ == "__main__":
    main()
