#!/usr/bin/env python3
"""Validate the method-distinct WM missing-simulator challenge."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
INPUT = HERE.parent / "corpus-reporting-audit" / "sources" / "source-wm-policyeval.csv"
PROTOCOL = HERE / "protocol-wm-missing-simulator-evidence-sensitivity.md"
PRODUCER = HERE / "analyze_wm_missing_simulator_uncertainty.py"
PRODUCER_RESULT = HERE / "result-wm-missing-simulator-evidence-sensitivity.json"
CHALLENGE = HERE / "result-wm-missing-simulator-evidence-sensitivity-independent-challenge.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(data: dict[str, object]) -> None:
    assert data["schema"] == "wm-missing-simulator-evidence-independent-challenge-v1"
    assert data["status"] == "pass"
    assert data["draws_per_scenario"] >= 100_000
    assert data["comparisons_within_0_015"] == 6
    assert data["zero_evidence_analytic_checks"] == 2
    assert data["protocol_sha256"] == sha256(PROTOCOL)
    assert data["producer_sha256"] == sha256(PRODUCER)
    assert data["producer_result_sha256"] == sha256(PRODUCER_RESULT)
    assert data["input_sha256"] == sha256(INPUT)
    for panel in data["panels"].values():
        for scenario in panel["scenarios"]:
            assert scenario["absolute_difference"] <= 0.015


def main() -> None:
    validate(json.loads(CHALLENGE.read_text(encoding="utf-8")))
    print("OK: WM missing-simulator challenge evidence binding")


if __name__ == "__main__":
    main()
