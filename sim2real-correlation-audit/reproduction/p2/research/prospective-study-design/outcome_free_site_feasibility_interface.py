#!/usr/bin/env python3
"""Deterministic H164 outcome-free site-feasibility interface."""

from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any


FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h164-outcome-free-site-feasibility-interface.md"
H160 = FAMILY / "result-h160-prospective-physical-evidence-packet.json"
H162 = FAMILY / "result-h162-object-level-reset-tolerance-source-audit.json"
H163 = (
    FAMILY
    / "result-h163-object-level-reset-tolerance-source-independent-challenge.json"
)
OUTPUT = FAMILY / "result-h164-outcome-free-site-feasibility-interface.json"

UNIT_ORDER = [
    "target_population_and_decision",
    "policy_observation_interface",
    "policy_action_and_control_interface",
    "scene_geometry_and_dynamics",
    "context_generation_and_assignment_order",
    "object_state_representation",
    "sensor_identity_and_calibration",
    "measurement_error_bound",
    "numeric_reset_tolerance",
    "tolerance_adequacy_rationale",
    "preassignment_baseline_capture",
    "preexecution_capture_and_comparison",
    "acceptance_to_controller_start_link",
    "reset_washout_and_carryover_control",
    "abort_retry_deviation_and_assignment_lifecycle",
    "capacity_safety_privacy_and_access",
]
ALLOWED_STATUSES = {
    "available",
    "partial",
    "target_altering",
    "absent",
    "not_applicable",
}
N_A_FORBIDDEN = {
    "object_state_representation",
    "sensor_identity_and_calibration",
    "measurement_error_bound",
    "numeric_reset_tolerance",
    "tolerance_adequacy_rationale",
    "preassignment_baseline_capture",
    "preexecution_capture_and_comparison",
    "acceptance_to_controller_start_link",
    "abort_retry_deviation_and_assignment_lifecycle",
    "capacity_safety_privacy_and_access",
}
FEATURES = [
    "red_container_x_um",
    "steel_bowl_x_um",
]
EXPECTED_DECISIONS = {
    "target_preserving_complete": "eligible_for_outcome_hidden_rehearsal",
    "visible_fiducial_complete": "target_altering_only",
    "grid_scale_as_tolerance": "not_evidenced",
    "unlinked_human_overlay": "not_evidenced",
}
UNIT_FIELDS = {
    "status",
    "artifact_ids",
    "owner",
    "claim",
    "missing_or_changed",
    "target_effect",
    "verification_method",
    "access",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_hash(value: Any) -> str:
    return sha256_bytes(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    )


def artifact(artifact_id: str, content: str) -> dict[str, Any]:
    raw = content.encode("utf-8")
    return {
        "artifact_id": artifact_id,
        "media_type": "application/x-h164-known-answer",
        "size_bytes": len(raw),
        "sha256": sha256_bytes(raw),
        "content_b64": base64.b64encode(raw).decode("ascii"),
        "access": "synthetic_public_fixture",
    }


def unit(
    dossier_name: str,
    name: str,
    status: str = "available",
    *,
    missing_or_changed: str = "",
    target_effect: str = "none",
) -> tuple[dict[str, Any], dict[str, Any]]:
    require(name in UNIT_ORDER, f"unknown unit {name}")
    require(status in ALLOWED_STATUSES, f"invalid unit status {status}")
    artifact_id = f"{dossier_name}:{name}"
    content = (
        f"H164 known-answer evidence; dossier={dossier_name}; unit={name}; "
        f"status={status}; target_effect={target_effect}"
    )
    record = {
        "unit": name,
        "status": status,
        "artifact_ids": [artifact_id],
        "owner": "synthetic-site-owner",
        "claim": f"Known-answer evidence for {name}",
        "missing_or_changed": missing_or_changed,
        "target_effect": target_effect,
        "verification_method": "content hash plus deterministic gate",
        "access": "synthetic_public_fixture",
    }
    return record, artifact(artifact_id, content)


def build_dossier(
    name: str,
    unit_overrides: dict[str, dict[str, str]] | None = None,
    **field_overrides: Any,
) -> dict[str, Any]:
    unit_overrides = unit_overrides or {}
    units: list[dict[str, Any]] = []
    artifacts: list[dict[str, Any]] = []
    for unit_name in UNIT_ORDER:
        override = unit_overrides.get(unit_name, {})
        row, retained = unit(
            name,
            unit_name,
            status=override.get("status", "available"),
            missing_or_changed=override.get("missing_or_changed", ""),
            target_effect=override.get("target_effect", "none"),
        )
        units.append(row)
        artifacts.append(retained)
    target_spec = {
        "target_id": "p2-pair-session-context-v1",
        "policy_observation_interface": "native_rgb_and_proprio",
        "policy_action_interface": "native_end_effector_delta",
        "scene_geometry": "native_site_scene",
        "context_law": "locked_before_pair_assignment",
        "max_allowed_start_delay_ns": 5_000_000_000,
    }
    dossier = {
        "schema": "h164-site-feasibility-dossier-v1",
        "dossier_name": name,
        "site_id": "synthetic-site-01",
        "target_id": target_spec["target_id"],
        "target_version": "1",
        "study_spec_hash": canonical_hash(target_spec),
        "prepared_before_outcomes": True,
        "outcome_fields_present": False,
        "proposed_rehearsal_mode": "outcome_hidden_synthetic_replay",
        "policy_visible_instrumentation": False,
        "contact_or_dynamics_altering_instrumentation": False,
        "preexecution_capture_time_ns": 1_000_000_000,
        "controller_start_time_ns": 2_000_000_000,
        "controller_start_delay_ns": 1_000_000_000,
        "max_allowed_start_delay_ns": target_spec[
            "max_allowed_start_delay_ns"
        ],
        "measurement_error_by_feature": {
            "red_container_x_um": 1_000,
            "steel_bowl_x_um": 1_500,
        },
        "tolerance_by_feature": {
            "red_container_x_um": 3_000,
            "steel_bowl_x_um": 4_000,
        },
        "tolerance_rationale_kind": "site_owned_task_sensitivity_bound",
        "preexecution_comparison_recorded": True,
        "acceptance_linked_to_controller_start": True,
        "human_override_used": False,
        "human_override_documented": True,
        "assigned_slots": 2,
        "closed_slots": 2,
        "declared_retries": 0,
        "observed_retries": 0,
        "capacity_safety_privacy_resolved": True,
        "units": units,
        "artifacts": artifacts,
    }
    dossier.update(field_overrides)
    return dossier


def build_known_answer_dossiers() -> list[dict[str, Any]]:
    complete = build_dossier("target_preserving_complete")
    visible = build_dossier(
        "visible_fiducial_complete",
        unit_overrides={
            "policy_observation_interface": {
                "status": "target_altering",
                "missing_or_changed": "new fiducial appears in native policy RGB",
                "target_effect": "changes policy observation distribution",
            }
        },
        policy_visible_instrumentation=True,
    )
    grid = build_dossier(
        "grid_scale_as_tolerance",
        unit_overrides={
            "tolerance_adequacy_rationale": {
                "status": "partial",
                "missing_or_changed": "grid scale copied without task sensitivity or error rationale",
            }
        },
        tolerance_by_feature={
            "red_container_x_um": 50_000,
            "steel_bowl_x_um": 50_000,
        },
        tolerance_rationale_kind="borrowed_grid_cell_size",
    )
    overlay = build_dossier(
        "unlinked_human_overlay",
        unit_overrides={
            "preexecution_capture_and_comparison": {
                "status": "partial",
                "missing_or_changed": "visual comparison not retained",
            },
            "acceptance_to_controller_start_link": {
                "status": "absent",
                "missing_or_changed": "no timestamped acceptance/start link",
            },
        },
        preexecution_comparison_recorded=False,
        acceptance_linked_to_controller_start=False,
        human_override_used=True,
        human_override_documented=False,
    )
    return [complete, visible, grid, overlay]


def decoded_artifact(item: dict[str, Any]) -> bytes:
    try:
        return base64.b64decode(item["content_b64"], validate=True)
    except Exception as error:
        raise ValueError("artifact base64 invalid") from error


def validate_dossier_structure(dossier: dict[str, Any]) -> None:
    require(
        dossier.get("schema") == "h164-site-feasibility-dossier-v1",
        "bad dossier schema",
    )
    units = dossier.get("units")
    require(isinstance(units, list), "units missing")
    require([row.get("unit") for row in units] == UNIT_ORDER, "unit roster changed")
    for row in units:
        require(
            set(row) == UNIT_FIELDS | {"unit"},
            f"unit fields changed: {row.get('unit')}",
        )
        require(row.get("status") in ALLOWED_STATUSES, "invalid unit status")
        require(isinstance(row.get("artifact_ids"), list), "artifact ids missing")
        require(bool(row.get("owner")), "unit owner missing")
        require(bool(row.get("claim")), "unit claim missing")
        require(bool(row.get("verification_method")), "verification missing")
        require(bool(row.get("access")), "unit access missing")
        if row["status"] == "not_applicable":
            require(
                row["unit"] not in N_A_FORBIDDEN,
                f"not_applicable forbidden for {row['unit']}",
            )
            require(
                bool(row["missing_or_changed"]),
                "not_applicable reason missing",
            )

    artifacts = dossier.get("artifacts")
    require(isinstance(artifacts, list), "artifacts missing")
    artifact_by_id: dict[str, dict[str, Any]] = {}
    for item in artifacts:
        artifact_id = item.get("artifact_id")
        require(isinstance(artifact_id, str), "artifact id missing")
        require(artifact_id not in artifact_by_id, "duplicate artifact id")
        raw = decoded_artifact(item)
        require(item.get("size_bytes") == len(raw), "artifact size mismatch")
        require(item.get("sha256") == sha256_bytes(raw), "artifact hash mismatch")
        artifact_by_id[artifact_id] = item
    for row in units:
        require(bool(row["artifact_ids"]), f"no artifact for {row['unit']}")
        for artifact_id in row["artifact_ids"]:
            require(artifact_id in artifact_by_id, "referenced artifact missing")

    errors = dossier.get("measurement_error_by_feature")
    tolerances = dossier.get("tolerance_by_feature")
    require(isinstance(errors, dict), "measurement errors missing")
    require(isinstance(tolerances, dict), "tolerances missing")
    require(sorted(errors) == FEATURES, "measurement feature roster changed")
    require(sorted(tolerances) == FEATURES, "tolerance feature roster changed")
    for feature in FEATURES:
        require(
            isinstance(errors[feature], int) and errors[feature] >= 0,
            "invalid measurement error",
        )
        require(
            isinstance(tolerances[feature], int) and tolerances[feature] > 0,
            "invalid tolerance",
        )


def classify_dossier(dossier: dict[str, Any]) -> dict[str, Any]:
    validate_dossier_structure(dossier)
    unit_status = {row["unit"]: row["status"] for row in dossier["units"]}
    evidence_issues: list[str] = []
    target_changes: list[str] = []

    if dossier.get("prepared_before_outcomes") is not True:
        evidence_issues.append("not_prepared_before_outcomes")
    if dossier.get("outcome_fields_present") is not False:
        evidence_issues.append("outcome_fields_present")
    if dossier.get("preexecution_comparison_recorded") is not True:
        evidence_issues.append("preexecution_comparison_not_recorded")
    if dossier.get("acceptance_linked_to_controller_start") is not True:
        evidence_issues.append("acceptance_not_linked_to_controller_start")
    if (
        dossier.get("preexecution_capture_time_ns")
        > dossier.get("controller_start_time_ns")
    ):
        evidence_issues.append("capture_after_controller_start")
    expected_delay = (
        dossier["controller_start_time_ns"]
        - dossier["preexecution_capture_time_ns"]
    )
    if dossier.get("controller_start_delay_ns") != expected_delay:
        evidence_issues.append("controller_start_delay_inconsistent")
    if dossier.get("human_override_used") and not dossier.get(
        "human_override_documented"
    ):
        evidence_issues.append("undocumented_human_override")
    if dossier.get("assigned_slots") != dossier.get("closed_slots"):
        evidence_issues.append("assigned_slot_lifecycle_incomplete")
    if dossier.get("declared_retries") != dossier.get("observed_retries"):
        evidence_issues.append("retry_lifecycle_incomplete")
    if dossier.get("capacity_safety_privacy_resolved") is not True:
        evidence_issues.append("capacity_safety_privacy_unresolved")
    if dossier.get("tolerance_rationale_kind") != (
        "site_owned_task_sensitivity_bound"
    ):
        evidence_issues.append("tolerance_rationale_not_site_owned")
    for feature in FEATURES:
        if dossier["measurement_error_by_feature"][feature] >= dossier[
            "tolerance_by_feature"
        ][feature]:
            evidence_issues.append(f"measurement_error_not_below_tolerance:{feature}")

    incomplete_statuses = [
        name
        for name, status in unit_status.items()
        if status in {"partial", "absent"}
    ]
    evidence_issues.extend(f"unit_incomplete:{name}" for name in incomplete_statuses)

    if dossier.get("policy_visible_instrumentation"):
        target_changes.append("policy_observation_interface")
    if dossier.get("contact_or_dynamics_altering_instrumentation"):
        target_changes.append("scene_geometry_and_dynamics")
    if dossier["controller_start_delay_ns"] > dossier["max_allowed_start_delay_ns"]:
        target_changes.append("controller_start_timing")
    target_changes.extend(
        row["unit"]
        for row in dossier["units"]
        if row["status"] == "target_altering"
    )
    target_changes = sorted(set(target_changes))

    mechanically_complete = all(
        status in {"available", "not_applicable", "target_altering"}
        for status in unit_status.values()
    )
    if evidence_issues:
        decision = "not_evidenced"
    elif target_changes and mechanically_complete:
        decision = "target_altering_only"
    elif not target_changes and mechanically_complete:
        decision = "eligible_for_outcome_hidden_rehearsal"
    else:
        decision = "not_evidenced"
    return {
        "decision": decision,
        "evidence_issues": sorted(set(evidence_issues)),
        "target_changes": target_changes,
        "mechanically_complete": mechanically_complete,
    }


Mutation = tuple[str, Callable[[dict[str, Any]], None]]


def hostile_mutations() -> list[Mutation]:
    def status(dossier: dict[str, Any], name: str, value: str) -> None:
        row = next(item for item in dossier["units"] if item["unit"] == name)
        row["status"] = value

    def insert_outcome(dossier: dict[str, Any]) -> None:
        dossier["outcome_fields_present"] = True
        dossier["policy_success_rate"] = 0.9

    def prepared_late(dossier: dict[str, Any]) -> None:
        dossier["prepared_before_outcomes"] = False

    def missing_artifact(dossier: dict[str, Any]) -> None:
        dossier["artifacts"].pop()

    def changed_artifact(dossier: dict[str, Any]) -> None:
        dossier["artifacts"][0]["content_b64"] = base64.b64encode(
            b"changed bytes"
        ).decode("ascii")

    def error_equals_tolerance(dossier: dict[str, Any]) -> None:
        dossier["measurement_error_by_feature"]["red_container_x_um"] = (
            dossier["tolerance_by_feature"]["red_container_x_um"]
        )

    def unexplained_tolerance(dossier: dict[str, Any]) -> None:
        dossier["tolerance_rationale_kind"] = "coarse_image_similarity"

    def visible_marker_relabel(dossier: dict[str, Any]) -> None:
        dossier["policy_visible_instrumentation"] = True
        status(dossier, "policy_observation_interface", "available")

    def dynamics_relabel(dossier: dict[str, Any]) -> None:
        dossier["contact_or_dynamics_altering_instrumentation"] = True
        status(dossier, "scene_geometry_and_dynamics", "available")

    def capture_after_start(dossier: dict[str, Any]) -> None:
        dossier["preexecution_capture_time_ns"] = 3_000_000_000

    def excessive_delay(dossier: dict[str, Any]) -> None:
        dossier["controller_start_time_ns"] = 8_000_000_001
        dossier["controller_start_delay_ns"] = 7_000_000_001

    def undocumented_override(dossier: dict[str, Any]) -> None:
        dossier["human_override_used"] = True
        dossier["human_override_documented"] = False

    def omitted_slot_or_retry(dossier: dict[str, Any]) -> None:
        dossier["closed_slots"] = 1
        dossier["observed_retries"] = 1

    def unresolved_safety_relabel(dossier: dict[str, Any]) -> None:
        dossier["capacity_safety_privacy_resolved"] = False
        status(dossier, "capacity_safety_privacy_and_access", "available")

    def invalid_not_applicable(dossier: dict[str, Any]) -> None:
        status(dossier, "numeric_reset_tolerance", "not_applicable")
        row = next(
            item
            for item in dossier["units"]
            if item["unit"] == "numeric_reset_tolerance"
        )
        row["missing_or_changed"] = "incorrectly declared unnecessary"

    return [
        ("outcome_field_inserted", insert_outcome),
        ("prepared_after_outcomes", prepared_late),
        ("artifact_missing", missing_artifact),
        ("artifact_bytes_changed", changed_artifact),
        ("measurement_error_equals_tolerance", error_equals_tolerance),
        ("tolerance_unexplained", unexplained_tolerance),
        ("visible_marker_relabelled", visible_marker_relabel),
        ("dynamics_change_relabelled", dynamics_relabel),
        ("capture_after_controller_start", capture_after_start),
        ("capture_to_start_delay_excessive", excessive_delay),
        ("human_override_undocumented", undocumented_override),
        ("assigned_slot_or_retry_omitted", omitted_slot_or_retry),
        ("safety_privacy_access_unresolved_relabelled", unresolved_safety_relabel),
        ("invalid_not_applicable", invalid_not_applicable),
    ]


def run_hostile_controls(base: dict[str, Any]) -> list[dict[str, Any]]:
    controls: list[dict[str, Any]] = []
    for name, mutate in hostile_mutations():
        candidate = copy.deepcopy(base)
        mutate(candidate)
        try:
            outcome = classify_dossier(candidate)
            rejected = (
                outcome["decision"] != "eligible_for_outcome_hidden_rehearsal"
            )
            observed = outcome["decision"]
        except ValueError as error:
            rejected = True
            observed = f"validation_error:{error}"
        controls.append(
            {
                "mutation": name,
                "rejected": rejected,
                "observed": observed,
            }
        )
    return controls


def build_result() -> dict[str, Any]:
    require(H160.is_file() and H162.is_file() and H163.is_file(), "upstream missing")
    dossiers = build_known_answer_dossiers()
    evaluated: list[dict[str, Any]] = []
    for dossier in dossiers:
        classification = classify_dossier(dossier)
        require(
            classification["decision"]
            == EXPECTED_DECISIONS[dossier["dossier_name"]],
            f"known-answer decision failed: {dossier['dossier_name']}",
        )
        evaluated.append(
            {
                "dossier": dossier,
                "classification": classification,
            }
        )
    controls = run_hostile_controls(dossiers[0])
    require(all(row["rejected"] for row in controls), "hostile mutation survived")
    result = {
        "schema": "h164-outcome-free-site-feasibility-interface-v1",
        "protocol_sha256": sha256(PROTOCOL),
        "upstream_hashes": {
            "h160_packet": sha256(H160),
            "h162_source_audit": sha256(H162),
            "h163_independent_challenge": sha256(H163),
        },
        "unit_order": UNIT_ORDER,
        "allowed_statuses": sorted(ALLOWED_STATUSES),
        "known_answer_decisions": EXPECTED_DECISIONS,
        "dossiers": evaluated,
        "dossier_count": len(evaluated),
        "dossier_unit_row_count": sum(
            len(item["dossier"]["units"]) for item in evaluated
        ),
        "artifact_count": sum(
            len(item["dossier"]["artifacts"]) for item in evaluated
        ),
        "hostile_controls": controls,
        "hostile_control_count": len(controls),
        "hostile_controls_rejected": sum(row["rejected"] for row in controls),
        "interface_decision": "synthetic_gate_logic_pass",
        "real_site_qualified": False,
        "field_collection_authorized": False,
        "next_action": (
            "Prepare a public-data-only site request packet and outcome-hidden "
            "replay using this interface; in parallel define the explicit "
            "pair-conditioned operational estimand."
        ),
        "claim_boundary": (
            "The result validates deterministic target-preservation and "
            "evidence-completeness logic on synthetic dossiers only. It does "
            "not establish a real site's feasibility, tolerance adequacy, "
            "safety, outcome validity, causal identification, or transport."
        ),
    }
    validate_result(result)
    return result


def validate_result(data: dict[str, Any]) -> None:
    require(
        data.get("schema") == "h164-outcome-free-site-feasibility-interface-v1",
        "bad result schema",
    )
    require(data.get("unit_order") == UNIT_ORDER, "result unit order changed")
    require(
        data.get("allowed_statuses") == sorted(ALLOWED_STATUSES),
        "status roster changed",
    )
    dossiers = data.get("dossiers")
    require(isinstance(dossiers, list) and len(dossiers) == 4, "dossier roster")
    names = [item["dossier"]["dossier_name"] for item in dossiers]
    require(names == list(EXPECTED_DECISIONS), "dossier order changed")
    for item in dossiers:
        dossier = item["dossier"]
        observed = classify_dossier(dossier)
        require(item["classification"] == observed, "classification changed")
        require(
            observed["decision"] == EXPECTED_DECISIONS[dossier["dossier_name"]],
            "known-answer mismatch",
        )
    require(data.get("dossier_unit_row_count") == 64, "unit row count")
    require(data.get("artifact_count") == 64, "artifact count")
    controls = data.get("hostile_controls")
    require(isinstance(controls, list) and len(controls) == 14, "hostile controls")
    require(all(row.get("rejected") is True for row in controls), "attack survived")
    require(data.get("hostile_controls_rejected") == 14, "rejection count")
    require(data.get("interface_decision") == "synthetic_gate_logic_pass", "gate")
    require(data.get("real_site_qualified") is False, "real site qualified")
    require(
        data.get("field_collection_authorized") is False,
        "field collection authorized",
    )


def serialized(data: dict[str, Any]) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build_result()
    content = serialized(result)
    if args.check:
        require(OUTPUT.is_file(), f"missing canonical result: {OUTPUT}")
        require(OUTPUT.read_bytes() == content, "canonical H164 result differs")
        print("OK: H164 outcome-free site-feasibility interface validates")
        return
    OUTPUT.write_bytes(content)
    print(OUTPUT)


if __name__ == "__main__":
    main()
