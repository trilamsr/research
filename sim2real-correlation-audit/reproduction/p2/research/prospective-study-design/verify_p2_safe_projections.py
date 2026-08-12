#!/usr/bin/env python3
"""Verify safe outcome-free projections and vendored source in the P2 package."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FAMILY = ROOT / "research" / "prospective-study-design"
sys.path.insert(0, str(FAMILY))

import audit_h193_phail_lifecycle_keys as h193  # noqa: E402
import audit_h194_phail_server_fields as h194  # noqa: E402
import audit_h195_phail_session_identity_recording_trace as h195  # noqa: E402
import audit_h196_positronic_session_identity_history as h196  # noqa: E402
import audit_h198_current_phail_lifecycle_binding as h198  # noqa: E402
import audit_h199_phail_randomized_home_target as h199  # noqa: E402
import audit_h200_phail_home_field_keys as h200  # noqa: E402
import audit_h201_phail_home_field_semantics as h201  # noqa: E402
import audit_h190_phail_session_artifact_paths as h190  # noqa: E402


H190_PROJECTION = FAMILY / "projection-h190-phail-path-tree.json"
H190_RESULT = FAMILY / "result-h190-phail-session-artifact-path-audit.json"
H193_PROJECTION = FAMILY / "projection-h193-phail-lifecycle-keys.csv"
H194_PROJECTION = FAMILY / "projection-h194-phail-server-fields.csv"
H193_RESULT = FAMILY / "result-h193-phail-lifecycle-key-inventory.json"
H194_RESULT = FAMILY / "result-h194-phail-server-field-semantics.json"
H200_PROJECTION = FAMILY / "projection-h200-phail-home-field-keys.csv"
H200_RESULT = FAMILY / "result-h200-phail-home-field-key-inventory.json"
VENDOR = ROOT / "vendor" / "positronic-v0.2.1"
REVISION = VENDOR / "SOURCE-REVISION.json"
H196_PACKAGE_VENDOR = ROOT / "vendor" / "positronic-main-h196"
H196_SOURCE = (
    H196_PACKAGE_VENDOR
    if H196_PACKAGE_VENDOR.is_dir()
    else ROOT / "work" / "h196-positronic-history"
)
H196_REVISION = H196_PACKAGE_VENDOR / "SOURCE-REVISION.json"
H196_RESULT = FAMILY / "result-h196-positronic-session-identity-history.json"
H198_RESULT = FAMILY / "result-h198-current-phail-lifecycle-binding.json"
H199_RESULT = FAMILY / "result-h199-phail-randomized-home-target.json"
H201_RESULT = FAMILY / "result-h201-phail-home-field-semantics.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def verify_h190() -> None:
    projection = json.loads(H190_PROJECTION.read_text(encoding="utf-8"))
    require(
        projection["schema"] == "h190-phail-safe-path-tree-projection-v1",
        "H190 projection schema",
    )
    require(projection["content_opened"] is False, "H190 content opened")
    require(
        projection["performance_field_opened"] is False,
        "H190 performance field opened",
    )
    inventory_result = h190.project_inventory(projection["dataset_inventory"])
    stored = json.loads(H190_RESULT.read_text(encoding="utf-8"))
    require(
        inventory_result == stored["dataset_inventory"],
        "H190 dataset projection mismatch",
    )
    projected_trees = []
    for source in projection["source_trees"]:
        raw = json.dumps(
            {
                "sha": source["resolved_tree_sha"],
                "truncated": False,
                "tree": source["tree"],
            },
            separators=(",", ":"),
        ).encode()
        rebuilt = h190.project_tree(source["name"], source["url"], raw)
        rebuilt["raw_sha256"] = source["raw_response_sha256"]
        projected_trees.append(rebuilt)
    require(projected_trees == stored["source_trees"], "H190 tree projection mismatch")


def verify_h193() -> None:
    rows = load_csv(H193_PROJECTION)
    require(bool(rows), "empty H193 projection")
    require(
        set(rows[0]) == {"episode_id", "key_path", "category", "node_type"},
        "H193 projection schema",
    )
    episodes_by_key: dict[tuple[str, str], set[str]] = defaultdict(set)
    types_by_key: dict[tuple[str, str], dict[str, int]] = defaultdict(
        lambda: defaultdict(int)
    )
    episode_ids: set[str] = set()
    seen: set[tuple[str, str, str]] = set()
    for row in rows:
        require(
            row["category"] in {"lifecycle_candidate", "identity_time_control"},
            "H193 unsafe category",
        )
        identity = (row["episode_id"], row["key_path"], row["category"])
        require(identity not in seen, "duplicate H193 projection row")
        seen.add(identity)
        episode_ids.add(row["episode_id"])
        key = (row["key_path"], row["category"])
        episodes_by_key[key].add(row["episode_id"])
        types_by_key[key][row["node_type"]] += 1
    require(len(episode_ids) == h193.EXPECTED_EPISODES, "H193 episode coverage")
    rebuilt = []
    for key in sorted(episodes_by_key):
        ids = episodes_by_key[key]
        rebuilt.append(
            {
                "key_path": key[0],
                "category": key[1],
                "episode_count": len(ids),
                "episode_set_sha256": h193.episode_set_hash(ids),
                "node_type_counts": dict(sorted(types_by_key[key].items())),
            }
        )
    stored = json.loads(H193_RESULT.read_text(encoding="utf-8"))
    h193.validate(stored)
    require(stored["key_rows"] == rebuilt, "H193 projection aggregate mismatch")


def verify_vendor() -> None:
    revision = json.loads(REVISION.read_text(encoding="utf-8"))
    require(revision["commit"] == h194.SOURCE_COMMIT, "source revision drift")
    require(revision["tag"] == "v0.2.1", "source tag drift")
    require(
        revision["upstream"] == "https://github.com/Positronic-Robotics/positronic",
        "source upstream drift",
    )
    for relative, record in h194.SOURCE_FILES.items():
        source = VENDOR / relative
        require(source.is_file(), f"vendored source missing: {relative}")
        require(sha256(source) == record["sha256"], f"source drift: {relative}")
    for relative, record in h195.SOURCE_FILES.items():
        source = VENDOR / relative
        require(source.is_file(), f"vendored H195 source missing: {relative}")
        require(sha256(source) == record["sha256"], f"H195 source drift: {relative}")
    counterexample = h195.DREAMZERO_COUNTEREXAMPLE
    source = VENDOR / counterexample["path"]
    require(source.is_file(), "vendored DreamZero counterexample missing")
    require(
        sha256(source) == counterexample["sha256"],
        "DreamZero counterexample drift",
    )


def verify_h194() -> None:
    projection = load_csv(H194_PROJECTION)
    require(len(projection) == h193.EXPECTED_EPISODES, "H194 row count")
    require(
        set(projection[0])
        == {
            "episode_id",
            "created_ts_ns",
            "utc_date",
            "policy_model",
            "inference.policy.server.host",
            "inference.policy.server.device",
        },
        "H194 projection schema",
    )
    cohort = h193.load_cohort()
    cohort_by_id = {row["episode_id"]: row for row in cohort}
    require(
        {row["episode_id"] for row in projection} == set(cohort_by_id),
        "H194 episode identity",
    )
    allowed = {
        "inference.policy.server.host": {"string:0.0.0.0"},
        "inference.policy.server.device": {"string:cuda", h194.MISSING},
    }
    values_by_field = {field: {} for field in h194.FIELDS}
    for row in projection:
        source = cohort_by_id[row["episode_id"]]
        require(row["created_ts_ns"] == source["created_ts_ns"], "timestamp drift")
        require(row["utc_date"] == source["utc_date"], "date drift")
        require(row["policy_model"] == source["policy_model"], "policy drift")
        for field in h194.FIELDS:
            value = row[field]
            require(value in allowed[field], f"unexpected projected value: {field}")
            values_by_field[field][row["episode_id"]] = value
    rebuilt = [
        h194.summarize_field(field, cohort, values_by_field[field])
        for field in h194.FIELDS
    ]
    stored = json.loads(H194_RESULT.read_text(encoding="utf-8"))
    require(stored["field_results"] == rebuilt, "H194 projection aggregate mismatch")
    require(
        stored["disposition"]
        == "infrastructure_configuration_not_session_identity",
        "H194 disposition drift",
    )
    require(stored["performance_field_opened"] is False, "performance field opened")
    verify_vendor()


def verify_h195() -> None:
    rebuilt = h195.build(source_root=VENDOR)
    h195.validate(rebuilt, source_root=VENDOR)
    stored = json.loads(h195.OUTPUT.read_text(encoding="utf-8"))
    require(rebuilt == stored, "H195 source trace mismatch")


def verify_h196_endpoint_projection() -> None:
    stored = json.loads(H196_RESULT.read_text(encoding="utf-8"))
    h196.validate(stored)
    if H196_REVISION.is_file():
        revision = json.loads(H196_REVISION.read_text(encoding="utf-8"))
        require(revision["commit"] == h196.HEAD, "H196 source revision drift")
        require(revision["baseline_commit"] == h196.BASE, "H196 baseline revision drift")
        require(revision["upstream"] == h196.REMOTE, "H196 source upstream drift")
    else:
        require(
            H196_SOURCE == ROOT / "work" / "h196-positronic-history",
            "H196 source revision record missing",
        )
    records = {row["path"]: row for row in stored["source_records"]}
    present = 0
    for relative in h196.PATHS:
        comparison = records[relative]["comparison"]
        source = H196_SOURCE / relative
        if comparison["present"]:
            require(source.is_file(), f"vendored H196 source missing: {relative}")
            require(
                sha256(source) == comparison["sha256"],
                f"vendored H196 source drift: {relative}",
            )
            present += 1
        else:
            require(not source.exists(), f"unexpected absent H196 source: {relative}")
    require(present == 18, "H196 vendored endpoint source count")
    challenge = json.loads(
        (
            FAMILY
            / "result-h196-positronic-session-identity-history-independent-challenge.json"
        ).read_text(encoding="utf-8")
    )
    require(
        challenge["producer_result_sha256"] == sha256(H196_RESULT),
        "H196 challenge/result binding drift",
    )
    require(
        challenge["independently_reconstructed_final_static_rrd_key"]
        == stored["trace"]["final_static_rrd_key"]
        == "inference.policy.server.recording.rrd",
        "H196 endpoint key drift",
    )
    require(
        challenge["episode_uid_is_shared_server_session_id"] is False,
        "H196 episode UID scope drift",
    )
    require(
        challenge["rrd_path_is_episode_to_server_recording_join"] is True,
        "H196 RRD join drift",
    )


def verify_h198_endpoint_projection() -> None:
    stored = json.loads(H198_RESULT.read_text(encoding="utf-8"))
    h198.validate(stored)
    require(stored["commit"] == h196.HEAD, "H198/H196 endpoint mismatch")
    for row in stored["source_files"]:
        source = H196_SOURCE / row["path"]
        require(source.is_file(), f"vendored H198 source missing: {row['path']}")
        require(
            sha256(source) == row["sha256"],
            f"vendored H198 source drift: {row['path']}",
        )
        require(
            git_blob(source) == row["git_blob"],
            f"vendored H198 blob drift: {row['path']}",
        )


def verify_h199_endpoint_projections() -> None:
    stored = json.loads(H199_RESULT.read_text(encoding="utf-8"))
    h199.validate(stored)
    roots = {h199.BASE: VENDOR, h199.CURRENT: H196_SOURCE}
    for revision, rows in stored["source_files"].items():
        root = roots[revision]
        for row in rows:
            source = root / row["path"]
            if row["present"]:
                require(
                    source.is_file(),
                    f"vendored H199 source missing: {revision}:{row['path']}",
                )
                require(
                    sha256(source) == row["sha256"],
                    f"vendored H199 source drift: {revision}:{row['path']}",
                )
                require(
                    git_blob(source) == row["git_blob"],
                    f"vendored H199 blob drift: {revision}:{row['path']}",
                )
            else:
                require(
                    not source.exists(),
                    f"unexpected H199 absent source: {revision}:{row['path']}",
                )


def verify_h200_projection() -> None:
    stored = json.loads(H200_RESULT.read_text(encoding="utf-8"))
    h200.validate(stored)
    projection = load_csv(H200_PROJECTION)
    require(
        h200.aggregate(projection) == stored["key_rows"],
        "H200 projection aggregate mismatch",
    )
    require(stored["candidate_count"] == 3, "H200 candidate count")
    require(
        stored["performance_or_trajectory_values_opened"] is False,
        "H200 value seal",
    )


def verify_h201_source_projection() -> None:
    stored = json.loads(H201_RESULT.read_text(encoding="utf-8"))
    h201.validate(stored)
    require(stored["revision"] == h199.BASE, "H201/H199 baseline mismatch")
    for relative, expected_blob in stored["source_blobs"].items():
        source = VENDOR / relative
        require(source.is_file(), f"vendored H201 source missing: {relative}")
        require(
            git_blob(source) == expected_blob,
            f"vendored H201 blob drift: {relative}",
        )
    require(
        stored["classification"] == "generic_signal_schema_not_home_draw",
        "H201 classification drift",
    )


def main() -> None:
    verify_h190()
    verify_h193()
    verify_h194()
    verify_h195()
    verify_h196_endpoint_projection()
    verify_h198_endpoint_projection()
    verify_h199_endpoint_projections()
    verify_h200_projection()
    verify_h201_source_projection()
    print(
        "OK: outcome-free H190/H193/H194/H200 projections, H195 trace, and "
        "H196/H198/H199/H201 vendored source projections reproduce retained "
        "results"
    )


if __name__ == "__main__":
    main()
