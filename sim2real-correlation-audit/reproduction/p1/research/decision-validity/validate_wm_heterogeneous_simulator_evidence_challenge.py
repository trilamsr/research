#!/usr/bin/env python3
"""Validate the heterogeneous simulator-evidence independent challenge."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
INPUT = HERE.parent / "corpus-reporting-audit" / "sources" / "source-wm-policyeval.csv"
PROTOCOL = HERE / "protocol-wm-heterogeneous-simulator-evidence-sensitivity.md"
PRODUCER = HERE / "analyze_wm_heterogeneous_simulator_evidence.py"
PRODUCER_RESULT = HERE / "result-wm-heterogeneous-simulator-evidence-sensitivity.json"
CHALLENGE = HERE / "result-wm-heterogeneous-simulator-evidence-independent-challenge.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(data: dict[str, object]) -> None:
    assert data["schema"] == (
        "wm-heterogeneous-simulator-evidence-independent-challenge-v1"
    )
    assert data["status"] == "pass"
    assert data["draws_per_scenario"] == 150_000
    assert data["tolerance"] == 0.015
    assert data["protocol_sha256"] == sha256(PROTOCOL)
    assert data["producer_sha256"] == sha256(PRODUCER)
    assert data["producer_result_sha256"] == sha256(PRODUCER_RESULT)
    assert data["input_sha256"] == sha256(INPUT)
    assert [row["name"] for row in data["scenarios"]] == [
        "common_10",
        "openvla_10",
        "openvla_0",
    ]
    assert data["scenarios"][0]["latent_winner_concordance"] < 0.5
    assert all(
        row["latent_winner_concordance"] > 0.5
        for row in data["scenarios"][1:]
    )
    assert all(row["absolute_difference"] <= 0.015 for row in data["scenarios"])


def main() -> None:
    validate(json.loads(CHALLENGE.read_text(encoding="utf-8")))
    print("OK: WM heterogeneous-evidence challenge binding")


if __name__ == "__main__":
    main()
