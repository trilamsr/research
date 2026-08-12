#!/usr/bin/env python3
"""Outcome-free H167 public pair-routing applicability audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h167-public-pair-routing-applicability.md"
OUTPUT = FAMILY / "result-h167-public-pair-routing-applicability.json"
SOURCES = {
    "paper_protocol": FAMILY / "source-h122-roboarena-paper-protocol.json",
    "ranking_semantics": (
        FAMILY / "result-h106-roboarena-ranking-algorithm-and-exclusion.json"
    ),
    "assignment_context": (
        FAMILY / "result-h114-roboarena-authored-text-assignment-context.json"
    ),
    "dataset_card_recall": (
        FAMILY / "result-h116-roboarena-dataset-card-assignment-recall.json"
    ),
    "release_challenge": (
        FAMILY / "result-h122-release-sequence-independent-challenge.json"
    ),
    "assignment_regimes": FAMILY / "result-roboarena-assignment-regimes.json",
    "h165_target": FAMILY / "result-h165-pair-conditioned-operational-target.json",
    "h166_challenge": (
        FAMILY
        / "result-h166-pair-conditioned-operational-target-independent-challenge.json"
    ),
}
ALLOWED_STATUSES = {
    "available",
    "paper_described_only",
    "partial",
    "absent",
    "contradicted_by_public_record",
}
REQUIRED_UNIT_IDS = (1, 3, 5, 6, 7, 8, 10, 11, 13, 14, 15)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_sources() -> dict[str, dict[str, Any]]:
    return {
        name: json.loads(path.read_text(encoding="utf-8"))
        for name, path in SOURCES.items()
    }


def verify_sources(data: dict[str, dict[str, Any]]) -> None:
    expected_schemas = {
        "paper_protocol": "h122-roboarena-paper-protocol-source-v1",
        "ranking_semantics": "h106-roboarena-ranking-algorithm-and-exclusion-v1",
        "assignment_context": "h114-roboarena-authored-text-assignment-context-v1",
        "dataset_card_recall": "h116-roboarena-dataset-card-assignment-recall-v1",
        "release_challenge": "h122-release-sequence-independent-challenge-v1",
        "assignment_regimes": "roboarena-assignment-regime-diagnostic-v1",
        "h165_target": "h165-pair-conditioned-operational-target-v1",
        "h166_challenge": (
            "h166-pair-conditioned-operational-target-independent-challenge-v1"
        ),
    }
    for name, schema in expected_schemas.items():
        require(data[name].get("schema") == schema, f"{name} schema changed")
    require(
        data["ranking_semantics"]["outcome_values_accessed"] is False,
        "ranking audit used outcomes",
    )
    require(
        data["assignment_context"]["outcome_values_accessed"] is False,
        "assignment-context audit used outcomes",
    )
    require(
        data["dataset_card_recall"]["performance_values_retained_or_interpreted"]
        is False,
        "dataset-card audit used performance",
    )
    require(
        data["release_challenge"]["outcome_or_judgment_fields_referenced_or_used"]
        is False,
        "release challenge used outcomes",
    )
    require(
        data["assignment_regimes"]["input"]["outcome_fields_referenced_or_used"]
        is False,
        "assignment-regime audit used outcomes",
    )
    require(
        data["h165_target"]["field_collection_authorized"] is False
        and data["h166_challenge"]["disposition"] == "pass_with_scope",
        "H165--H166 boundary changed",
    )


def unit(
    unit_id: int,
    name: str,
    status: str,
    evidence: str,
    source_keys: list[str],
) -> dict[str, Any]:
    require(status in ALLOWED_STATUSES, f"invalid unit status {status}")
    return {
        "unit_id": unit_id,
        "name": name,
        "status": status,
        "evidence": evidence,
        "source_keys": source_keys,
    }


def build_units(data: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    paper = data["paper_protocol"]
    ranking = data["ranking_semantics"]
    assignment = data["assignment_context"]
    cards = data["dataset_card_recall"]
    release = data["release_challenge"]
    regimes = data["assignment_regimes"]
    require(
        paper["source_findings"][0]["finding"].startswith(
            "The stated evaluation protocol has the central server sample two policies"
        ),
        "paper pair-sampling finding changed",
    )
    require(
        "pair inclusion probabilities or deterministic assignment weights"
        in paper["not_established_by_source"],
        "paper assignment boundary changed",
    )
    require(
        ranking["algorithm_name"] == "Bradley-Terry Davidson"
        and ranking["algorithm_name_only_in_ui_prose"] is True,
        "public ranking semantics changed",
    )
    require(
        assignment["server_assignment_law_established"] is False
        and assignment["realized_assignment_probabilities_established"] is False,
        "deployed assignment law unexpectedly established",
    )
    require(
        cards["candidate_window_count"] == 0,
        "dataset cards now contain assignment candidates",
    )
    require(
        release["fixed_panel_support"][1]["supported_pair_count"] == 21
        and release["fixed_panel_support"][2]["supported_pair_count"] == 15,
        "historical/newest support distinction changed",
    )
    require(
        regimes["status"] == "exploratory_topology_exposed"
        and "segment or explicitly bridge" in regimes["decision_consequence"],
        "assignment-epoch boundary changed",
    )
    return [
        unit(
            1,
            "declared_within_pair_routing_action",
            "absent",
            "No audited public record declares policy routing within a presented pair as the downstream action.",
            ["ranking_semantics", "paper_protocol"],
        ),
        unit(
            2,
            "declared_global_leaderboard_or_ranking",
            "available",
            "The pinned public UI declares a Policy Leaderboard and names Bradley-Terry Davidson in UI prose.",
            ["ranking_semantics"],
        ),
        unit(
            3,
            "h165_action_aligned_with_public_action",
            "absent",
            "The H165 within-pair routing action is not the public global-ranking action.",
            ["h165_target", "ranking_semantics"],
        ),
        unit(
            4,
            "paper_pair_first_random_sampling",
            "paper_described_only",
            "The paper describes random pair sampling before evaluator task/scene construction; deployed execution is unaudited.",
            ["paper_protocol"],
        ),
        unit(
            5,
            "current_deployed_pair_assignment_law",
            "absent",
            "The audited authored public source does not establish the server assignment law.",
            ["assignment_context", "paper_protocol"],
        ),
        unit(
            6,
            "fixed_outcome_independent_pair_weights",
            "absent",
            "Neither pair inclusion probabilities nor deterministic assignment weights are public in the audited record.",
            ["paper_protocol", "assignment_context"],
        ),
        unit(
            7,
            "active_pool_effective_intervals",
            "absent",
            "The paper anticipates a changing pool but does not establish active-pool intervals for a public dump.",
            ["paper_protocol", "release_challenge"],
        ),
        unit(
            8,
            "session_level_assignment_export",
            "absent",
            "The paper source record explicitly leaves a session-level assignment export unestablished.",
            ["paper_protocol"],
        ),
        unit(
            9,
            "matched_within_pair_conditions",
            "paper_described_only",
            "The paper requires closely matched initial conditions inside each A/B comparison.",
            ["paper_protocol"],
        ),
        unit(
            10,
            "stable_future_pair_specific_context_law",
            "absent",
            "No audited source identifies a stable future distribution G_ab for evaluator-constructed tasks and scenes.",
            ["paper_protocol"],
        ),
        unit(
            11,
            "historical_to_future_context_bridge",
            "absent",
            "No overlap, invariance, or transport bridge links historical realized contexts to a future G_ab.",
            ["paper_protocol", "h165_target"],
        ),
        unit(
            12,
            "cumulative_february_panel_all_21_edges",
            "available",
            "The independently reconstructed February public panel has 1,816 exact-two sessions and all 21 fixed-policy pairs.",
            ["release_challenge"],
        ),
        unit(
            13,
            "newest_nonoverlapping_increment_all_21_edges",
            "partial",
            "The newest increment has 278 exact-two sessions, 15 of 21 pairs, and one isolated fixed policy.",
            ["release_challenge"],
        ),
        unit(
            14,
            "stable_roster_assignment_epoch_for_pooling",
            "contradicted_by_public_record",
            "Public topology and vocabulary shift require segmentation or an explicit bridge before pooling.",
            ["release_challenge", "assignment_regimes"],
        ),
        unit(
            15,
            "future_cluster_lifecycle_structure",
            "partial",
            "Public metadata support session-level descriptive counts, but the relied-on challenge retained neither assignment rows nor session identifiers.",
            ["release_challenge", "assignment_regimes"],
        ),
    ]


def build() -> dict[str, Any]:
    data = load_sources()
    verify_sources(data)
    units = build_units(data)
    require(
        [row["unit_id"] for row in units] == list(range(1, 16)),
        "unit order changed",
    )
    by_id = {row["unit_id"]: row for row in units}
    failed = [
        {
            "unit_id": unit_id,
            "name": by_id[unit_id]["name"],
            "status": by_id[unit_id]["status"],
        }
        for unit_id in REQUIRED_UNIT_IDS
        if by_id[unit_id]["status"] != "available"
    ]
    action_mismatch = (
        by_id[1]["status"] == "absent" and by_id[2]["status"] == "available"
    )
    require(action_mismatch, "public action mismatch changed")
    require(len(failed) == len(REQUIRED_UNIT_IDS), "required blocker count changed")
    return {
        "schema": "h167-public-pair-routing-applicability-v1",
        "protocol_sha256": sha256(PROTOCOL),
        "source_hashes": {
            name: sha256(path) for name, path in sorted(SOURCES.items())
        },
        "outcome_fields_accessed_or_used": False,
        "unit_count": len(units),
        "units": units,
        "required_unit_ids": list(REQUIRED_UNIT_IDS),
        "failed_required_units": failed,
        "failed_required_unit_count": len(failed),
        "public_action_mismatch": action_mismatch,
        "cumulative_support_does_not_establish_current_applicability": True,
        "decision": "not_qualified_for_public_pair_routing_application",
        "advancement": "pass",
        "prospective_adoption_possible": True,
        "field_collection_authorized": False,
        "scope": (
            "Outcome-free applicability audit of existing public RoboArena "
            "records for the H165 routing action; not a benchmark-validity, "
            "outcome, assignment-intent, causal, or field claim."
        ),
    }


def canonical_bytes(data: dict[str, Any]) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8")


def validate(data: dict[str, Any]) -> None:
    require(
        data.get("schema") == "h167-public-pair-routing-applicability-v1",
        "unexpected schema",
    )
    require(data.get("protocol_sha256") == sha256(PROTOCOL), "protocol changed")
    require(data.get("unit_count") == 15, "unit count changed")
    require(
        data.get("outcome_fields_accessed_or_used") is False,
        "outcome scope violated",
    )
    require(
        data.get("decision")
        == "not_qualified_for_public_pair_routing_application",
        "applicability decision changed",
    )
    require(data.get("public_action_mismatch") is True, "action mismatch missing")
    require(
        data.get("cumulative_support_does_not_establish_current_applicability")
        is True,
        "cumulative-support boundary weakened",
    )
    require(data.get("advancement") == "pass", "H167 did not pass")
    require(data.get("field_collection_authorized") is False, "field use authorized")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("choose exactly one")
    result = build()
    validate(result)
    rendered = canonical_bytes(result)
    if args.check:
        require(args.out.read_bytes() == rendered, "canonical result is stale")
        print("OK: H167 public pair-routing applicability regenerates exactly")
        return
    args.out.write_bytes(rendered)
    print(
        json.dumps(
            {
                "status": result["advancement"],
                "decision": result["decision"],
                "failed_required_units": result["failed_required_unit_count"],
                "public_action_mismatch": result["public_action_mismatch"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
