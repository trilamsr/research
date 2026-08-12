#!/usr/bin/env python3
"""H170 target-bound repair of the H164 site-feasibility interface."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any


FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h170-target-bound-site-feasibility-repair.md"
TARGET_SPEC_FILE = FAMILY / "input-h170-target-spec.json"
H164_SOURCE = FAMILY / "outcome_free_site_feasibility_interface.py"
H164_RESULT = FAMILY / "result-h164-outcome-free-site-feasibility-interface.json"
H169_CHALLENGE = (
    FAMILY / "result-h169-h164-not-applicable-authorization-challenge.json"
)
H169_REVIEW = FAMILY / "review-h169-h164-not-applicable-authorization.md"
OUTPUT = FAMILY / "result-h170-target-bound-site-feasibility-repair.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()


def load_h164():
    spec = importlib.util.spec_from_file_location("h164_v1_for_h170", H164_SOURCE)
    require(spec is not None and spec.loader is not None, "H164 import failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


H164 = load_h164()
TARGET_SPEC = json.loads(TARGET_SPEC_FILE.read_text(encoding="utf-8"))
TARGET_HASH = canonical_hash(TARGET_SPEC)


def validate_canonical_target() -> None:
    require(TARGET_SPEC["schema"] == "h170-target-spec-v1", "target schema changed")
    require(
        TARGET_SPEC["target_id"] == "p2-pair-session-context-v1"
        and TARGET_SPEC["target_version"] == "1",
        "target identity changed",
    )
    require(
        TARGET_SPEC["required_units"] == H164.UNIT_ORDER,
        "target required-unit roster changed",
    )
    require(
        TARGET_SPEC["not_applicable_authorizations"] == [],
        "current target unexpectedly authorizes not_applicable",
    )


def upgrade_dossier(dossier: dict[str, Any]) -> dict[str, Any]:
    upgraded = copy.deepcopy(dossier)
    upgraded["schema"] = "h170-site-feasibility-dossier-v2"
    upgraded["target_spec"] = copy.deepcopy(TARGET_SPEC)
    upgraded["study_spec_hash"] = TARGET_HASH
    upgraded["not_applicable_authorizations"] = copy.deepcopy(
        TARGET_SPEC["not_applicable_authorizations"]
    )
    return upgraded


def validate_target_binding(dossier: dict[str, Any]) -> None:
    require(
        dossier.get("schema") == "h170-site-feasibility-dossier-v2",
        "bad H170 dossier schema",
    )
    target_spec = dossier.get("target_spec")
    require(isinstance(target_spec, dict), "complete target_spec missing")
    require(target_spec == TARGET_SPEC, "target_spec differs from canonical target")
    require(
        dossier.get("study_spec_hash") == TARGET_HASH,
        "study_spec_hash differs from canonical target",
    )
    require(
        canonical_hash(target_spec) == dossier["study_spec_hash"],
        "target_spec hash mismatch",
    )
    authorizations = dossier.get("not_applicable_authorizations")
    require(
        isinstance(authorizations, list),
        "not_applicable_authorizations must be a list",
    )
    require(
        authorizations == TARGET_SPEC["not_applicable_authorizations"],
        "authorization roster differs from canonical target",
    )
    units = dossier.get("units")
    require(isinstance(units, list), "units missing")
    require(
        [row.get("unit") for row in units] == TARGET_SPEC["required_units"],
        "dossier units differ from canonical target",
    )
    declared_not_applicable = sorted(
        row["unit"] for row in units if row.get("status") == "not_applicable"
    )
    authorized_units = sorted(row["unit"] for row in authorizations)
    require(
        declared_not_applicable == authorized_units,
        "not_applicable unit lacks exact target authorization",
    )


def downgrade_for_h164(dossier: dict[str, Any]) -> dict[str, Any]:
    downgraded = copy.deepcopy(dossier)
    downgraded["schema"] = "h164-site-feasibility-dossier-v1"
    downgraded.pop("target_spec", None)
    downgraded.pop("not_applicable_authorizations", None)
    return downgraded


def classify_dossier(dossier: dict[str, Any]) -> dict[str, Any]:
    validate_target_binding(dossier)
    return H164.classify_dossier(downgrade_for_h164(dossier))


Mutation = tuple[str, Callable[[dict[str, Any]], None]]


def inherited_mutations() -> list[Mutation]:
    return list(H164.hostile_mutations())


def authorization_mutations() -> list[Mutation]:
    def set_not_applicable(dossier: dict[str, Any], unit_name: str) -> None:
        row = next(item for item in dossier["units"] if item["unit"] == unit_name)
        row["status"] = "not_applicable"
        row["missing_or_changed"] = (
            "claimed unnecessary without target-bound authorization"
        )

    def na_policy_observation(dossier: dict[str, Any]) -> None:
        set_not_applicable(dossier, "policy_observation_interface")

    def na_context_order(dossier: dict[str, Any]) -> None:
        set_not_applicable(dossier, "context_generation_and_assignment_order")

    def na_reset_carryover(dossier: dict[str, Any]) -> None:
        set_not_applicable(dossier, "reset_washout_and_carryover_control")

    def forged_authorization(dossier: dict[str, Any]) -> None:
        set_not_applicable(dossier, "policy_observation_interface")
        dossier["not_applicable_authorizations"].append(
            {
                "unit": "policy_observation_interface",
                "rationale": "forged",
                "target_spec_sha256": dossier["study_spec_hash"],
            }
        )

    def modified_target_old_hash(dossier: dict[str, Any]) -> None:
        dossier["target_spec"]["max_allowed_start_delay_ns"] += 1

    def modified_target_rehashed(dossier: dict[str, Any]) -> None:
        dossier["target_spec"]["max_allowed_start_delay_ns"] += 1
        dossier["study_spec_hash"] = canonical_hash(dossier["target_spec"])

    def replaced_hash(dossier: dict[str, Any]) -> None:
        dossier["study_spec_hash"] = "0" * 64

    def missing_target(dossier: dict[str, Any]) -> None:
        dossier.pop("target_spec")

    def malformed_authorizations(dossier: dict[str, Any]) -> None:
        dossier["not_applicable_authorizations"] = {}

    return [
        ("na_policy_observation_without_authorization", na_policy_observation),
        ("na_context_order_without_authorization", na_context_order),
        ("na_reset_carryover_without_authorization", na_reset_carryover),
        ("forged_not_applicable_authorization", forged_authorization),
        ("modified_target_with_old_hash", modified_target_old_hash),
        ("modified_target_with_recomputed_hash", modified_target_rehashed),
        ("replaced_study_spec_hash", replaced_hash),
        ("missing_complete_target_spec", missing_target),
        ("malformed_authorization_container", malformed_authorizations),
    ]


def run_controls(
    base: dict[str, Any],
    mutations: list[Mutation],
) -> list[dict[str, Any]]:
    controls: list[dict[str, Any]] = []
    for name, mutate in mutations:
        candidate = copy.deepcopy(base)
        mutate(candidate)
        try:
            outcome = classify_dossier(candidate)
            observed = outcome["decision"]
            rejected = observed != "eligible_for_outcome_hidden_rehearsal"
        except (KeyError, TypeError, ValueError) as error:
            observed = f"validation_error:{error}"
            rejected = True
        controls.append(
            {
                "mutation": name,
                "observed": observed,
                "rejected": rejected,
            }
        )
    return controls


def build_result() -> dict[str, Any]:
    validate_canonical_target()
    h169 = json.loads(H169_CHALLENGE.read_text(encoding="utf-8"))
    require(
        h169["disposition"] == "fail_repair_required"
        and h169["bypass_count"] == 3,
        "H169 failure record changed",
    )
    dossiers = [upgrade_dossier(row) for row in H164.build_known_answer_dossiers()]
    evaluated: list[dict[str, Any]] = []
    for dossier in dossiers:
        classification = classify_dossier(dossier)
        require(
            classification["decision"]
            == H164.EXPECTED_DECISIONS[dossier["dossier_name"]],
            f"known-answer decision changed: {dossier['dossier_name']}",
        )
        evaluated.append({"dossier": dossier, "classification": classification})

    legacy_controls = run_controls(dossiers[0], inherited_mutations())
    authorization_controls = run_controls(dossiers[0], authorization_mutations())
    require(
        len(legacy_controls) == 14 and all(row["rejected"] for row in legacy_controls),
        "legacy H164 control failed",
    )
    require(
        len(authorization_controls) == 9
        and all(row["rejected"] for row in authorization_controls),
        "H170 authorization control failed",
    )
    return {
        "schema": "h170-target-bound-site-feasibility-repair-v1",
        "protocol_sha256": sha256(PROTOCOL),
        "target_spec_file_sha256": sha256(TARGET_SPEC_FILE),
        "canonical_target_spec_hash": TARGET_HASH,
        "upstream_hashes": {
            "h164_source": sha256(H164_SOURCE),
            "h164_result": sha256(H164_RESULT),
            "h169_challenge": sha256(H169_CHALLENGE),
            "h169_review": sha256(H169_REVIEW),
        },
        "target_spec": TARGET_SPEC,
        "dossiers": evaluated,
        "dossier_count": len(evaluated),
        "dossier_unit_row_count": sum(
            len(item["dossier"]["units"]) for item in evaluated
        ),
        "artifact_count": sum(
            len(item["dossier"]["artifacts"]) for item in evaluated
        ),
        "known_answer_decisions": H164.EXPECTED_DECISIONS,
        "legacy_hostile_controls": legacy_controls,
        "legacy_hostile_control_count": len(legacy_controls),
        "legacy_hostile_controls_rejected": sum(
            row["rejected"] for row in legacy_controls
        ),
        "authorization_controls": authorization_controls,
        "authorization_control_count": len(authorization_controls),
        "authorization_controls_rejected": sum(
            row["rejected"] for row in authorization_controls
        ),
        "h169_bypasses_rejected": True,
        "interface_decision": "synthetic_gate_logic_repaired_pass",
        "supersedes_h164_for_reliance": True,
        "independent_challenge_required": True,
        "real_site_qualified": False,
        "field_collection_authorized": False,
        "scope": (
            "Target-bound synthetic interface repair only; not physical "
            "truth, tolerance adequacy, safety, real-site qualification, "
            "outcome validity, causal identification, or transport."
        ),
    }


def canonical_bytes(data: dict[str, Any]) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8")


def validate_result(data: dict[str, Any]) -> None:
    require(
        data.get("schema") == "h170-target-bound-site-feasibility-repair-v1",
        "unexpected schema",
    )
    require(data.get("protocol_sha256") == sha256(PROTOCOL), "protocol changed")
    require(
        data.get("canonical_target_spec_hash") == TARGET_HASH,
        "target hash changed",
    )
    require(
        data.get("dossier_count") == 4
        and data.get("dossier_unit_row_count") == 64
        and data.get("artifact_count") == 64,
        "known-answer counts changed",
    )
    require(
        data.get("legacy_hostile_controls_rejected") == 14
        and data.get("authorization_controls_rejected") == 9,
        "control rejection count changed",
    )
    require(data.get("h169_bypasses_rejected") is True, "H169 bypass remains")
    require(
        data.get("interface_decision") == "synthetic_gate_logic_repaired_pass",
        "repair did not pass",
    )
    require(
        data.get("independent_challenge_required") is True,
        "challenge gate removed",
    )
    require(
        data.get("real_site_qualified") is False
        and data.get("field_collection_authorized") is False,
        "field scope widened",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("choose exactly one")
    result = build_result()
    validate_result(result)
    rendered = canonical_bytes(result)
    if args.check:
        require(args.out.read_bytes() == rendered, "canonical result is stale")
        print("OK: H170 target-bound site-feasibility repair regenerates exactly")
        return
    args.out.write_bytes(rendered)
    print(
        json.dumps(
            {
                "status": result["interface_decision"],
                "legacy_attacks_rejected": result[
                    "legacy_hostile_controls_rejected"
                ],
                "authorization_attacks_rejected": result[
                    "authorization_controls_rejected"
                ],
                "real_site_qualified": result["real_site_qualified"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
