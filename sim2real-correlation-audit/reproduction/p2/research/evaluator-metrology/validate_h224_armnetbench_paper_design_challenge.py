#!/usr/bin/env python3
"""Validate the saved independent H224 challenge without opening source payloads."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


FAMILY = Path(__file__).resolve().parent
PRODUCER = FAMILY / "result-h224-armnetbench-paper-design-audit.json"
CHALLENGE = (
    FAMILY / "result-h224-armnetbench-paper-design-independent-challenge.json"
)
PRODUCER_SHA256 = "b29dc62a06f2174d2c9a6971dd678b774d728edc33431cee7a2e4976487f000a"
PDF_SHA256 = "c1d0edbd163f6db2597da67c4afe03e8b63deb3c2eefbfca613db3ff5319951e"
SOURCE_SHA256 = "21e4d8b117878e4d42d810da6e8e2a711c11e146dc389d1fd4ba7da97cf12bf1"
MAIN_TEX_SHA256 = "8ceaa0e443e561c90b376a22e5c4d541243685d5cb3d42b04d905118907f6e20"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(data: dict[str, Any]) -> dict[str, Any]:
    if sha256(PRODUCER) != PRODUCER_SHA256:
        raise ValueError("producer hash mismatch")
    producer = json.loads(PRODUCER.read_text(encoding="utf-8"))
    if data["schema"] != "h224-armnetbench-paper-design-independent-challenge-v1":
        raise ValueError("challenge schema mismatch")
    if data["producer_result_sha256"] != PRODUCER_SHA256:
        raise ValueError("challenge producer binding mismatch")
    identities = data["source_identities"]
    if identities != {
        "arxiv_id": "2607.24481v1",
        "pdf_sha256": PDF_SHA256,
        "source_archive_sha256": SOURCE_SHA256,
        "main_tex_sha256": MAIN_TEX_SHA256,
    }:
        raise ValueError("challenge source identity mismatch")
    statuses = {str(row["unit_id"]): row["status"] for row in producer["evidence_units"]}
    if data["independent_unit_statuses"] != statuses:
        raise ValueError("independent unit statuses disagree")
    decisions = data["independent_decisions"]
    if (
        decisions["p2_classification"] != "adverse_mismatch_contrast"
        or decisions["p2_positive_design_contrast_eligible"] is not False
        or decisions["h022_status"] != "refused_unchanged"
        or decisions["h022_existing_blockers_all_closed"] is not False
    ):
        raise ValueError("independent decision mismatch")
    for key in (
        "all_unit_statuses_agree",
        "p2_decision_agrees",
        "h022_decision_agrees",
    ):
        if data[key] is not True:
            raise ValueError(f"challenge agreement false: {key}")
    boundary = data["outcome_boundary"]
    if (
        boundary["full_source_bytes_processed"] is not True
        or boundary["performance_values_extracted_or_retained"] is not False
        or boundary["performance_values_used_in_classification"] is not False
        or boundary["source_selection_revisited"] is not False
    ):
        raise ValueError("challenge outcome boundary mismatch")
    for key, value in data["scope_limits"].items():
        if value is not False:
            raise ValueError(f"challenge scope boundary violated: {key}")
    if (
        data["disposition"]
        != "pass_adverse_mismatch_and_h022_refusal_confirmed"
    ):
        raise ValueError("challenge disposition mismatch")
    return data


def main() -> None:
    validate(json.loads(CHALLENGE.read_text(encoding="utf-8")))
    print("OK: H224 independent challenge validates")


if __name__ == "__main__":
    main()
