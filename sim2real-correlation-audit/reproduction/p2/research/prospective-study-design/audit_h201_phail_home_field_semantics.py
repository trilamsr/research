#!/usr/bin/env python3
"""Trace H200 candidate key semantics in pinned Positronic v0.2.1 source."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h201-phail-home-field-semantics.md"
H200 = FAMILY / "result-h200-phail-home-field-key-inventory.json"
H199 = FAMILY / "result-h199-phail-randomized-home-target.json"
OUTPUT = FAMILY / "result-h201-phail-home-field-semantics.json"
DEFAULT_REPOSITORY = ROOT / "work" / "h198-positronic-current"
REVISION = "e406176bc526babb06844a48e3627a5c0409eb74"
CANDIDATES = ("joint_names", "joint_signal", "pose_signals")
MATCHED_PATH_BLOBS = {
    "positronic/cfg/ds/internal.py": "c5e85de27ef4b2269d72a0c296d5a2e4a72e874b",
    "positronic/drivers/roboarm/franka.py": "a7a5fafe3a1a2c18b24cc948526fc4465586d660",
    "positronic/drivers/roboarm/ik.py": "73a9593c6a60ab6a482d0688653511fb6d4feda0",
    "positronic/drivers/roboarm/kinematics.py": "5587768fc6d54a9b8bc05e43804cf829f1da6f21",
    "positronic/drivers/roboarm/so101/driver.py": "d87467e8af3ecc88c5a8d541737df8065ecbafc7",
    "positronic/drivers/roboarm/tests/test_ik.py": "e05f60e9e81b3caf63b28e76872b3f9ec3b0c960",
    "positronic/policy/tests/test_harness.py": "8a2686081d47c22dbf317e0505c7dc9e685fe63b",
    "positronic/server/dataset_utils.py": "244e4e38fc2f4ae7b07bfa56640391d6a30a1298",
    "positronic/simulator/mujoco/sim.py": "23df42e7c614a46f0cc273d3b39edaa12083c091",
    "positronic/wire.py": "1c52667d9cf089712c8e45ee90b7ceee9f1f8fa1",
}
EXPANSION_BLOBS = {
    "positronic/inference.py": "c9bc29b72f15763e17740537f08a73d58675217c",
    "positronic/policy/harness.py": "857b1fe313d67689345fc5fd5954605464fbca38",
    "positronic/dataset/ds_writer_agent.py": "8f0f06e31fabecce2d093d7768ede88397affcb2",
    "positronic/dataset/local_dataset.py": "8e7d6001ebcbb0a58e39a07b2f58d400f45797fd",
}
CLASSIFICATIONS = {
    "realized_home_or_rng_evidence_source_defined",
    "generic_signal_schema_not_home_draw",
    "mixed_or_ambiguous_candidate_semantics",
    "source_trace_incomplete",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(repository: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", "-C", str(repository), *args],
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout


def source(repository: Path, relative: str) -> str:
    return git(repository, "show", f"{REVISION}:{relative}")


def function_slice(text: str, start: str, end: str) -> str:
    begin = text.index(start)
    finish = text.index(end, begin + len(start))
    return text[begin:finish]


def exact_search(repository: Path) -> list[dict[str, Any]]:
    hits = []
    for candidate in CANDIDATES:
        raw = git(
            repository,
            "grep",
            "-n",
            "-F",
            candidate,
            REVISION,
            "--",
            ".",
        )
        require(raw.strip(), f"no search hit: {candidate}")
        for line in raw.splitlines():
            prefix = f"{REVISION}:"
            require(line.startswith(prefix), "grep revision prefix")
            relative, number, text = line[len(prefix) :].split(":", 2)
            hits.append(
                {
                    "candidate": candidate,
                    "path": relative,
                    "line": int(number),
                    "text": text,
                }
            )
    hits.sort(key=lambda row: (row["candidate"], row["path"], row["line"]))
    observed_paths = {row["path"] for row in hits}
    require(observed_paths == set(MATCHED_PATH_BLOBS), "matched path roster")
    return hits


def blob_roster(repository: Path) -> dict[str, str]:
    expected = MATCHED_PATH_BLOBS | EXPANSION_BLOBS
    observed = {
        relative: git(repository, "rev-parse", f"{REVISION}:{relative}").strip()
        for relative in expected
    }
    require(observed == expected, "source blob drift")
    return observed


def analyze(repository: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    wire = source(repository, "positronic/wire.py")
    franka = source(repository, "positronic/drivers/roboarm/franka.py")
    inference = source(repository, "positronic/inference.py")
    harness = source(repository, "positronic/policy/harness.py")
    writer = source(repository, "positronic/dataset/ds_writer_agent.py")
    local = source(repository, "positronic/dataset/local_dataset.py")
    server = source(repository, "positronic/server/dataset_utils.py")

    robot_meta = function_slice(
        franka, "    def _build_robot_meta(", "\n    def _ensure_robot("
    )
    reset = function_slice(franka, "    def _reset(", "\n    def run(")
    build_meta = function_slice(
        harness, "    def _build_episode_meta(", "\n    def _home("
    )
    handle = function_slice(
        writer, "    def _handle_command(", "\n        return ep_writer"
    )
    candidates = [
        {
            "key": "joint_names",
            "producer_path": "positronic/drivers/roboarm/franka.py",
            "producer_symbol": "Robot._build_robot_meta",
            "value_class": "array_of_revolute_joint_name_strings_from_robot_urdf",
            "behavior": "static_robot_model_metadata_emitted_at_driver_start",
            "semantic_class": "schema_descriptor",
            "configured_base_home_present": False,
            "realized_home_target_present": False,
            "rng_identity_present": False,
        },
        {
            "key": "joint_signal",
            "producer_path": "positronic/wire.py",
            "producer_symbol": "ROBOT_STATIC_META",
            "value_class": "constant_signal_name_string",
            "behavior": "fixed_static_visualization_role",
            "semantic_class": "schema_descriptor",
            "configured_base_home_present": False,
            "realized_home_target_present": False,
            "rng_identity_present": False,
        },
        {
            "key": "pose_signals",
            "producer_path": "positronic/wire.py",
            "producer_symbol": "ROBOT_STATIC_META",
            "value_class": "constant_array_of_pose_signal_name_strings",
            "behavior": "fixed_static_visualization_roles",
            "semantic_class": "schema_descriptor",
            "configured_base_home_present": False,
            "realized_home_target_present": False,
            "rng_identity_present": False,
        },
    ]
    controls = {
        "wire_constants_bound": all(
            token in wire
            for token in (
                "'joint_signal': 'robot_state.q'",
                "'pose_signals': ['robot_state.ee_pose', 'robot_commands.pose']",
            )
        ),
        "joint_names_bound_to_urdf_names": all(
            token in robot_meta
            for token in (
                "'joint_names': _revolute_joint_names(urdf_xml)",
                "'control_frame': 'end_effector'",
            )
        ),
        "randomized_target_separate_from_robot_meta": all(
            token in reset
            for token in (
                "np.random.uniform(",
                "target = target + variation",
                "set_target_joints(target, asynchronous=False)",
            )
        )
        and "target" not in robot_meta
        and "variation" not in robot_meta,
        "phail_harness_receives_static_meta": (
            "Harness(policy, static_meta=wire.ROBOT_STATIC_META)" in inference
        ),
        "robot_meta_connected_to_harness": (
            "world.connect(robot_arm.robot_meta, harness.robot_meta_in)" in wire
        ),
        "static_and_robot_meta_merged": (
            "meta = dict(self._static_meta)" in build_meta
            and "meta.update(self.robot_meta_in.value)" in build_meta
        ),
        "episode_start_persists_static_data": (
            "DsWriterCommandType.START_EPISODE" in handle
            and "for k, v in cmd.static_data.items()" in handle
            and "ep_writer.set_static(k, v)" in handle
        ),
        "static_json_sink": (
            "episode_json = self._path / 'static.json'" in local
            and "json.dump(self._static_items" in local
        ),
        "server_consumes_as_visualization_schema": all(
            token in server
            for token in (
                "3D visualization roles (pose_signals, joint_signal)",
                "joint_signal = ep.static.get('joint_signal')",
                "joint_names = ep.static.get('joint_names')",
                "pose_set = set(ep.static.get('pose_signals', []))",
            )
        ),
    }
    require(all(controls.values()), "semantic trace control")
    return candidates, controls


def classify(candidates: list[dict[str, Any]], controls: dict[str, Any]) -> str:
    if not all(controls.values()) or len(candidates) != 3:
        return "source_trace_incomplete"
    if any(
        row["realized_home_target_present"] or row["rng_identity_present"]
        for row in candidates
    ):
        return "realized_home_or_rng_evidence_source_defined"
    if all(row["semantic_class"] == "schema_descriptor" for row in candidates):
        return "generic_signal_schema_not_home_draw"
    return "mixed_or_ambiguous_candidate_semantics"


def build(repository: Path) -> dict[str, Any]:
    require(git(repository, "rev-parse", REVISION).strip() == REVISION, "revision")
    require(not git(repository, "status", "--porcelain=v1").strip(), "dirty checkout")
    candidates, controls = analyze(repository)
    hits = exact_search(repository)
    return {
        "schema": "h201-phail-home-field-semantics-v1",
        "protocol_sha256": sha256(PROTOCOL),
        "h200_sha256": sha256(H200),
        "h199_sha256": sha256(H199),
        "revision": REVISION,
        "search_terms": list(CANDIDATES),
        "search_hits": hits,
        "source_blobs": blob_roster(repository),
        "matched_path_count": len(MATCHED_PATH_BLOBS),
        "direct_expansions": [
            {
                "path": relative,
                "reason": reason,
            }
            for relative, reason in (
                (
                    "positronic/inference.py",
                    "bind wire static metadata to the exact real-hardware harness",
                ),
                (
                    "positronic/policy/harness.py",
                    "trace static and robot metadata merge",
                ),
                (
                    "positronic/dataset/ds_writer_agent.py",
                    "trace START payload to static item writes",
                ),
                (
                    "positronic/dataset/local_dataset.py",
                    "trace static items to static.json",
                ),
            )
        ],
        "candidates": candidates,
        "controls": controls,
        "classification": classify(candidates, controls),
        "sidecar_values_opened": False,
        "trajectory_or_performance_content_opened": False,
        "historical_execution_fidelity_established": False,
        "decision_consequence": (
            "H200's three public key candidates are robot/signal schema "
            "descriptors, not the configured or realized randomized home target "
            "and not RNG evidence. Do not open their sidecar values; retain "
            "H199's request to serialize the realized target and RNG identity."
        ),
    }


def validate(result: dict[str, Any]) -> None:
    require(result.get("schema") == "h201-phail-home-field-semantics-v1", "schema")
    require(result.get("protocol_sha256") == sha256(PROTOCOL), "protocol")
    require(result.get("h200_sha256") == sha256(H200), "H200")
    require(result.get("h199_sha256") == sha256(H199), "H199")
    require(result.get("revision") == REVISION, "revision")
    require(result.get("search_terms") == list(CANDIDATES), "terms")
    require(result.get("matched_path_count") == len(MATCHED_PATH_BLOBS), "paths")
    require(result.get("source_blobs") == MATCHED_PATH_BLOBS | EXPANSION_BLOBS, "blobs")
    require(len(result.get("direct_expansions", [])) == 4, "expansions")
    candidates = result.get("candidates")
    require([row["key"] for row in candidates] == list(CANDIDATES), "candidates")
    for row in candidates:
        require(row["semantic_class"] == "schema_descriptor", "semantic class")
        require(row["configured_base_home_present"] is False, "base home")
        require(row["realized_home_target_present"] is False, "realized home")
        require(row["rng_identity_present"] is False, "RNG")
    require(result.get("classification") == classify(candidates, result["controls"]), "classification")
    require(result.get("classification") in CLASSIFICATIONS, "classification value")
    for key in (
        "sidecar_values_opened",
        "trajectory_or_performance_content_opened",
        "historical_execution_fidelity_established",
    ):
        require(result.get(key) is False, key)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, default=DEFAULT_REPOSITORY)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check and not args.repository.exists():
        validate(json.loads(OUTPUT.read_text()))
        print("OK: H201 stored source trace validates")
        return
    candidate = build(args.repository)
    validate(candidate)
    if args.check:
        require(candidate == json.loads(OUTPUT.read_text()), "exact rebuild")
        print("OK: H201 exact source trace reproduces")
    else:
        OUTPUT.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n")
        print(json.dumps(candidate, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
