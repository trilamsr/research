#!/usr/bin/env python3
"""Derive the fixed H178 cross-system action/order audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h178-cross-system-action-order-source-audit.md"
ROSTER = FAMILY / "result-h177-cross-system-action-order-roster.json"
CODING = FAMILY / "input-h178-source-coding.json"
OUTPUT = FAMILY / "result-h178-cross-system-action-order-source-audit.json"

SYSTEM_ORDER = [
    "autoeval",
    "roboarena",
    "gesim_2",
    "practical_recipe",
    "umi_bench",
    "gigaworld_wmbench",
    "robodojo",
]
UNIT_ORDER = [
    "declared_operational_action",
    "candidate_pair_or_roster_fixed_before_context",
    "context_fixed_before_candidate_assignment",
    "stable_assignment_law_public",
    "stable_context_law_public",
    "declared_target_support_complete_or_bounded",
    "reset_carryover_rule_public",
    "cluster_or_session_identity_public",
    "public_action_matches_identified_estimand",
    "target_compatible_positive_contrast",
]
EVIDENCE_STATUSES = {
    "available",
    "partial",
    "paper_described_only",
    "absent_from_fixed_sources",
    "unresolved",
}
ACTION_LABELS = {
    "global_policy_ranking",
    "fixed_task_policy_score_or_ranking",
    "simulator_or_world_model_evaluation",
    "policy_development_or_improvement",
    "unresolved_action",
}
SEMANTIC_VALUES = {"satisfied", "not_satisfied", "unresolved"}
CONJUNCTION_EVIDENCE = {"available", "paper_described_only"}
POSITIVE_UNITS = [
    "context_fixed_before_candidate_assignment",
    "stable_assignment_law_public",
    "stable_context_law_public",
    "declared_target_support_complete_or_bounded",
    "reset_carryover_rule_public",
    "cluster_or_session_identity_public",
    "public_action_matches_identified_estimand",
    "target_compatible_positive_contrast",
]
RANKING_ACTIONS = {
    "global_policy_ranking",
    "fixed_task_policy_score_or_ranking",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def index_units(system: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["unit"]: row for row in system["units"]}


def positive_contrast(system: dict[str, Any]) -> bool:
    rows = index_units(system)
    action = rows["declared_operational_action"]
    return (
        action["status"] in CONJUNCTION_EVIDENCE
        and action["value"] in RANKING_ACTIONS
        and all(
            rows[unit]["status"] in CONJUNCTION_EVIDENCE
            and rows[unit]["value"] == "satisfied"
            for unit in POSITIVE_UNITS
        )
    )


def second_mismatch(system: dict[str, Any]) -> bool:
    rows = index_units(system)
    return (
        system["system"] != "roboarena"
        and rows["declared_operational_action"]["value"] == "global_policy_ranking"
        and rows["candidate_pair_or_roster_fixed_before_context"]["status"]
        in CONJUNCTION_EVIDENCE
        and rows["candidate_pair_or_roster_fixed_before_context"]["value"]
        == "satisfied"
        and rows["context_fixed_before_candidate_assignment"]["status"]
        in CONJUNCTION_EVIDENCE
        and rows["context_fixed_before_candidate_assignment"]["value"]
        == "not_satisfied"
        and rows["stable_context_law_public"]["status"] in CONJUNCTION_EVIDENCE
        and rows["stable_context_law_public"]["value"] == "not_satisfied"
        and rows["public_action_matches_identified_estimand"]["status"]
        in CONJUNCTION_EVIDENCE
        and rows["public_action_matches_identified_estimand"]["value"]
        == "not_satisfied"
    )


def validate_inputs(
    roster: dict[str, Any], coding: dict[str, Any]
) -> list[dict[str, Any]]:
    require(
        coding.get("schema") == "h178-cross-system-source-coding-v1",
        "unexpected coding schema",
    )
    require(
        coding.get("fixed_roster_sha256") == sha256(ROSTER),
        "coding is not bound to the current H177 roster",
    )
    roster_ids = [
        row["arxiv_id"] for row in roster["frozen_source_screening_roster"]
    ]
    systems = coding.get("systems", [])
    require(
        [row.get("system") for row in systems] == SYSTEM_ORDER,
        "system roster or order changed",
    )
    require(
        [row.get("arxiv_id") for row in systems] == roster_ids,
        "coded identities disagree with frozen roster",
    )
    require(len(coding.get("source_bindings", [])) == 9, "source binding count changed")
    source_keys: set[str] = set()
    for binding in coding["source_bindings"]:
        key = binding["source_key"]
        require(key not in source_keys, f"duplicate source key: {key}")
        source_keys.add(key)
        path = FAMILY / binding["path"]
        require(path.is_file(), f"source missing: {path}")
        require(sha256(path) == binding["sha256"], f"source hash changed: {key}")

    for system in systems:
        units = system.get("units", [])
        require(
            [row.get("unit") for row in units] == UNIT_ORDER,
            f"unit roster or order changed for {system['system']}",
        )
        for index, row in enumerate(units):
            require(row.get("status") in EVIDENCE_STATUSES, "invalid evidence status")
            if index == 0:
                require(row.get("value") in ACTION_LABELS, "invalid action label")
            else:
                require(row.get("value") in SEMANTIC_VALUES, "invalid semantic value")
            require(bool(row.get("finding")), "missing bounded finding")
            require(bool(row.get("locator")), "missing source locator")
            require(bool(row.get("limit")), "missing limitation")
            keys = row.get("source_keys", [])
            require(bool(keys), "row without source binding")
            require(set(keys) <= source_keys, "unknown row source binding")
    require(sum(len(row["units"]) for row in systems) == 70, "row count changed")
    return systems


def build_result() -> dict[str, Any]:
    roster = load(ROSTER)
    coding = load(CODING)
    systems = validate_inputs(roster, coding)
    positives = [
        row["system"]
        for row in systems
        if row["system"] != "roboarena" and positive_contrast(row)
    ]
    mismatches = [row["system"] for row in systems if second_mismatch(row)]
    status_counts = Counter(
        unit["status"] for system in systems for unit in system["units"]
    )
    semantic_counts = Counter(
        unit["value"]
        for system in systems
        for unit in system["units"]
        if unit["unit"] != "declared_operational_action"
    )
    if mismatches:
        decision = "second_mismatch_found"
    elif positives:
        decision = "positive_contrast_found"
    else:
        decision = "no_second_instantiation_in_bounded_frame"
    return {
        "schema": "h178-cross-system-action-order-source-audit-v1",
        "protocol": PROTOCOL.name,
        "protocol_sha256": sha256(PROTOCOL),
        "upstream_hashes": {
            "h177_roster_sha256": sha256(ROSTER),
            "h178_source_coding_sha256": sha256(CODING),
        },
        "source_bindings": coding["source_bindings"],
        "row_count": 70,
        "system_count": 7,
        "evidence_status_counts": dict(sorted(status_counts.items())),
        "semantic_value_counts": dict(sorted(semantic_counts.items())),
        "systems": systems,
        "second_mismatch_systems": mismatches,
        "positive_contrast_systems": positives,
        "positive_contrast_strength": (
            "source_described" if positives else "not_applicable"
        ),
        "decision": decision,
        "bounded_interpretation": (
            "No second RoboArena-like action/identification mismatch was found "
            "in the fixed seven-system frame. UMI-Bench and RoboDojo are "
            "source-described positive protocol contrasts: each fixes a common "
            "finite evaluation frame, execution rule, reset handling, and "
            "episode/trial identity before candidate execution."
        ),
        "limitations": [
            "The purposive seven-system frame does not estimate field prevalence.",
            "The positive contrasts are supported by fixed paper descriptions, "
            "not independently reproduced execution artifacts.",
            "No performance direction, magnitude, significance, or leaderboard "
            "standing was extracted or used.",
        ],
        "outcome_fields_retained": [],
        "roster_expansion_authorized": False,
        "paper_status_change_authorized_before_independent_challenge": False,
        "next_stage": "h179_independent_challenge",
    }


def serialized(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build_result()
    rendered = serialized(result)
    if args.check:
        require(OUTPUT.is_file(), "result file is missing")
        require(OUTPUT.read_text(encoding="utf-8") == rendered, "result is stale")
        print("OK: H178 source audit is current")
        return
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(
        f"Wrote {OUTPUT.name}: {result['decision']} "
        f"({', '.join(result['positive_contrast_systems'])})"
    )


if __name__ == "__main__":
    main()
