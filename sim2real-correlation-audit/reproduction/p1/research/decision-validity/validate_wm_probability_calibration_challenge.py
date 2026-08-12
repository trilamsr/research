#!/usr/bin/env python3
"""Validate the method-distinct WM calibration challenge."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
INPUT = HERE.parent / "corpus-reporting-audit" / "sources" / "source-wm-policyeval.csv"
PROTOCOL = HERE / "protocol-wm-probability-calibration-audit.md"
PRODUCER = HERE / "audit_wm_probability_calibration.py"
PRODUCER_RESULT = HERE / "result-wm-probability-calibration-audit.json"
CHALLENGE = HERE / "result-wm-probability-calibration-audit-independent-challenge.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(data: dict[str, object]) -> None:
    assert data["schema"] == "wm-probability-calibration-independent-challenge-v1"
    assert data["status"] == "pass"
    assert data["tolerance"] <= 1e-10
    assert data["numeric_comparisons"] == 78
    assert data["protocol_sha256"] == sha256(PROTOCOL)
    assert data["input_sha256"] == sha256(INPUT)
    assert data["producer_sha256"] == sha256(PRODUCER)
    assert data["producer_result_sha256"] == sha256(PRODUCER_RESULT)
    for panel in data["panels"].values():
        assert panel["positive_affine_winner_preserved"] is True
        assert panel["rate_mse_is_brier"] is False
        heldout = panel["task_heldout_affine_recalibration"]
        assert heldout["heldout_tasks_improved"] == 2
        assert heldout["crossfitted_winner_margin"] > 0


def main() -> None:
    validate(json.loads(CHALLENGE.read_text(encoding="utf-8")))
    print("OK: WM calibration challenge evidence binding")


if __name__ == "__main__":
    main()
