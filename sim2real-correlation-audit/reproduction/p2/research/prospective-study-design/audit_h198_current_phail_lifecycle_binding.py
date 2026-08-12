#!/usr/bin/env python3
"""Trace the pinned current PhAIL command into lifecycle mechanics and evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h198-current-phail-lifecycle-binding.md"
H196 = FAMILY / "result-h196-positronic-session-identity-history.json"
OUTPUT = FAMILY / "result-h198-current-phail-lifecycle-binding.json"
DEFAULT_REPOSITORY = ROOT / "work" / "h198-positronic-current"
COMMIT = "01b78e6f62ff5913490c360afdd2712eee070524"

BASE_PATHS = (
    "positronic/inference.py",
    "positronic/policy/harness.py",
    "positronic/data_collection.py",
    "positronic/dataset/ds_writer_agent.py",
    "positronic/dataset/episode.py",
    "positronic/dataset/local_dataset.py",
    "positronic/cfg/policy.py",
    "positronic/policy/base.py",
    "positronic/policy/remote.py",
    "positronic/offboard/client.py",
    "positronic/offboard/server.py",
    "positronic/cli/eval/run.py",
    "positronic/eval.py",
    "positronic/cfg/embodiment.py",
    "positronic/gui/eval.py",
)

EXPANSIONS = (
    {
        "path": "positronic/wire.py",
        "origin_path": "positronic/cli/eval/run.py",
        "origin_symbol": "wire.wire_embodiment",
        "target_symbol": "wire_embodiment",
        "reason": "resolve embodiment signals and serializers wired into the episode writer",
    },
    {
        "path": "positronic/dataset/serializers.py",
        "origin_path": "positronic/cfg/embodiment.py",
        "origin_symbol": "Serializers.robot_state",
        "target_symbol": "Serializers.robot_state",
        "reason": "resolve RESETTING/ERROR behavior on policy and record paths",
    },
    {
        "path": "positronic/cfg/hardware/roboarm/__init__.py",
        "origin_path": "positronic/cfg/embodiment.py",
        "origin_symbol": "positronic.cfg.hardware.roboarm.franka_droid",
        "target_symbol": "franka_droid / franka",
        "reason": "resolve the real DROID arm implementation selected by the embodiment",
    },
    {
        "path": "positronic/drivers/roboarm/__init__.py",
        "origin_path": "positronic/dataset/serializers.py",
        "origin_symbol": "RobotStatus",
        "target_symbol": "RobotStatus",
        "reason": "resolve robot reset/readiness status semantics",
    },
    {
        "path": "positronic/drivers/roboarm/command.py",
        "origin_path": "positronic/cfg/embodiment.py",
        "origin_symbol": "roboarm_command.Reset",
        "target_symbol": "Reset",
        "reason": "resolve the configured home command type",
    },
    {
        "path": "positronic/drivers/roboarm/franka.py",
        "origin_path": "positronic/cfg/hardware/roboarm/__init__.py",
        "origin_symbol": "franka.Robot",
        "target_symbol": "Robot._reset / Robot.run",
        "reason": "resolve execution and completion semantics of the real arm Reset command",
    },
)

EXPECTED_BLOBS = {
    "positronic/cfg/embodiment.py": "7bc708eece4ea12c443ddfea6156f4d68a51a1ea",
    "positronic/cfg/hardware/roboarm/__init__.py": "4d27c99f622f6d2be40577a57b2d076c94a8695b",
    "positronic/cfg/policy.py": "4c612e0f4e0ba7dfa1c0778e3e39c96f906a4256",
    "positronic/cli/eval/run.py": "38c7bd50185df7bcb72434148c6c901b8d4f465a",
    "positronic/data_collection.py": "e1a1bb59f4e5e8568a5dddc6e6e40e28fe99b45c",
    "positronic/dataset/ds_writer_agent.py": "765b811438d1a0e7db32698e24f9d21488495be0",
    "positronic/dataset/episode.py": "d15b7f6b5917b121d9526506039db903ecc390dc",
    "positronic/dataset/local_dataset.py": "b14883ea6d970a5b9b84fc7c8ee930bc7a889495",
    "positronic/dataset/serializers.py": "c7a1ccacb9f0a98f9eb7e93981126542bab1e836",
    "positronic/drivers/roboarm/__init__.py": "4fe401691d07289e2702fc9c04d7855541fe0436",
    "positronic/drivers/roboarm/command.py": "964457cff3f7b808d955cfed2da710b3d2657d17",
    "positronic/drivers/roboarm/franka.py": "fbe608d1bd4fdae61309c630a0efcc990653c0a3",
    "positronic/eval.py": "a8fb68d340b8c05c9b8332711d53ccfa15e6c652",
    "positronic/gui/eval.py": "8fe6c8fec55a3702d6ae6047e45472b090bf73c0",
    "positronic/inference.py": "57dd5e20829acb606b8faa45b40dde923128b3b7",
    "positronic/offboard/client.py": "2c1c1ff7f2f3694a11e399be354d1c45d745dbf3",
    "positronic/offboard/server.py": "53abf9904dad7b088f803c5ff2de170617d75a2d",
    "positronic/policy/base.py": "8e0f4012d387cf46591667c1a2dd0ea08599ddd4",
    "positronic/policy/harness.py": "62dd01974588785000285ef6c8cba4672386690a",
    "positronic/policy/remote.py": "4ddc38539ae6698ab73a310fe216814e16b69cd2",
    "positronic/wire.py": "026f94cfd740f80cf8c9d859aaf24a55e8c34214",
}

FACTS = {
    "phail_alias": (
        "positronic/inference.py",
        92,
        108,
        ("embodiment=positronic.cfg.embodiment.droid", "'phail': run_cfg.override", "driver=eval_ui"),
    ),
    "attended_task_none": (
        "positronic/cli/eval/run.py",
        119,
        160,
        ("if driver is not None:", "_run_world(policy, embodiment, None, None"),
    ),
    "harness_receives_task": (
        "positronic/cli/eval/run.py",
        63,
        81,
        ("task: Task | None", "Harness(policy, embodiment, task=task"),
    ),
    "droid_real_home": (
        "positronic/cfg/embodiment.py",
        25,
        44,
        ("roboarm_command.Reset()", "'target_grip':", "simulated=False"),
    ),
    "task_reset_contract": (
        "positronic/eval.py",
        70,
        102,
        ("``None`` on real embodiments", "self.reset = reset"),
    ),
    "context_and_home": (
        "positronic/policy/harness.py",
        130,
        153,
        ("meta.update(context)", "self._embodiment.home.items()", "self.commands[name].emit"),
    ),
    "begin_end_order": (
        "positronic/policy/harness.py",
        196,
        252,
        (
            "if self._task is not None and self._task.reset is not None:",
            "self.policy.new_session",
            "DsWriterCommand.START()",
            "DsWriterCommand.ABORT()",
            "self._home(clock)",
        ),
    ),
    "inference_readiness": (
        "positronic/policy/harness.py",
        268,
        282,
        ("while the arm is", "``RESETTING``", "return None"),
    ),
    "initial_home": (
        "positronic/policy/harness.py",
        366,
        382,
        ("self._home(clock)", "directive_msg.updated"),
    ),
    "record_window": (
        "positronic/dataset/ds_writer_agent.py",
        196,
        230,
        ("after_start =", "before_stop =", "value = serializer(value)"),
    ),
    "abort_discards": (
        "positronic/dataset/ds_writer_agent.py",
        260,
        288,
        ("case DsWriterCommandType.ABORT_EPISODE:", "ep_writer.abort()"),
    ),
    "robot_state_filter": (
        "positronic/dataset/serializers.py",
        111,
        117,
        ("RobotStatus.RESETTING", "RobotStatus.ERROR", "return None"),
    ),
    "episode_uuid": (
        "positronic/dataset/local_dataset.py",
        113,
        122,
        ("'uid': uid or uuid.uuid4().hex", "'created_ts_ns'"),
    ),
    "static_persistence": (
        "positronic/dataset/local_dataset.py",
        242,
        249,
        ("'static.json'", "'meta.json'", "json.dump"),
    ),
    "writer_wiring": (
        "positronic/wire.py",
        90,
        105,
        ("ds_agent.add_signal(name, obs.serializer)", "ds_agent.add_signal(name, TrajectoryOverrideSerializer"),
    ),
    "ui_context": (
        "positronic/gui/eval.py",
        397,
        448,
        (
            "context = {keys.TASK: task_name}",
            "context['eval.total_items']",
            "Directive.RUN(**context)",
            "Directive.ABORT()",
        ),
    ),
    "franka_config": (
        "positronic/cfg/hardware/roboarm/__init__.py",
        6,
        37,
        ("home_joints=", "return franka.Robot", "franka_droid ="),
    ),
    "franka_reset": (
        "positronic/drivers/roboarm/franka.py",
        215,
        228,
        ("_start_reset()", "asynchronous=False", "_finish_reset()"),
    ),
    "franka_reset_dispatch": (
        "positronic/drivers/roboarm/franka.py",
        296,
        300,
        ("case command.Reset():", "self._reset(robot, robot_state)"),
    ),
    "robot_meta_fields": (
        "positronic/drivers/roboarm/franka.py",
        148,
        181,
        ("'urdf'", "'joint_names'", "'control_frame'", "'gripper'"),
    ),
}

UNIT_NAMES = (
    "phail_real_hardware_binding",
    "phail_task_binding",
    "pre_session_scene_reset_call",
    "scene_reset_completion_gate",
    "inter_episode_home_command",
    "home_completion_gate",
    "post_reset_recording_boundary",
    "persistent_episode_identity",
    "persistent_operator_session_identity",
    "persistent_reset_carryover_evidence",
    "persistent_directive_context",
    "server_recording_join",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(repository: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repository), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ).stdout


def source_files(repository: Path) -> list[dict[str, Any]]:
    require(git(repository, "rev-parse", "HEAD").strip() == COMMIT, "commit")
    require(not git(repository, "status", "--porcelain=v1").strip(), "dirty checkout")
    rows = []
    for path, expected_blob in sorted(EXPECTED_BLOBS.items()):
        raw = (repository / path).read_bytes()
        blob = git(repository, "rev-parse", f"{COMMIT}:{path}").strip()
        require(blob == expected_blob, f"blob: {path}")
        rows.append(
            {
                "path": path,
                "git_blob": blob,
                "sha256": hashlib.sha256(raw).hexdigest(),
                "byte_count": len(raw),
                "line_count": len(raw.decode("utf-8").splitlines()),
            }
        )
    return rows


def evidence_facts(repository: Path) -> list[dict[str, Any]]:
    out = []
    for fact_id, (path, start, end, required) in FACTS.items():
        lines = (repository / path).read_text().splitlines()
        require(1 <= start <= end <= len(lines), f"span: {fact_id}")
        excerpt = "\n".join(lines[start - 1 : end])
        for token in required:
            require(token in excerpt, f"fact token {fact_id}: {token}")
        out.append(
            {
                "fact_id": fact_id,
                "path": path,
                "start_line": start,
                "end_line": end,
                "excerpt": excerpt,
                "excerpt_sha256": hashlib.sha256(excerpt.encode()).hexdigest(),
            }
        )
    return sorted(out, key=lambda row: row["fact_id"])


def units() -> list[dict[str, Any]]:
    return [
        {
            "unit": "phail_real_hardware_binding",
            "status": "supported",
            "facts": ["phail_alias", "droid_real_home"],
            "reason": "The phail alias retains the DROID embodiment, whose source marks it non-simulated.",
        },
        {
            "unit": "phail_task_binding",
            "status": "not_supported",
            "facts": ["phail_alias", "attended_task_none", "harness_receives_task"],
            "reason": "The attended driver branch passes task=None and trials=None into the Harness.",
        },
        {
            "unit": "pre_session_scene_reset_call",
            "status": "not_supported",
            "facts": ["attended_task_none", "begin_end_order", "task_reset_contract"],
            "reason": "The only scene-reset call is conditional on a non-null Task, but the phail driver path supplies none.",
        },
        {
            "unit": "scene_reset_completion_gate",
            "status": "not_supported",
            "facts": ["attended_task_none", "begin_end_order"],
            "reason": "No PhAIL scene-reset call is bound, so no scene-reset completion or acceptance gate precedes session creation.",
        },
        {
            "unit": "inter_episode_home_command",
            "status": "supported",
            "facts": ["droid_real_home", "context_and_home", "initial_home", "franka_reset", "franka_reset_dispatch"],
            "reason": "The real DROID embodiment supplies arm Reset and gripper home values; the Harness emits them initially and after episodes, and the Franka Reset executes synchronously inside the driver.",
        },
        {
            "unit": "home_completion_gate",
            "status": "not_supported",
            "facts": ["attended_task_none", "begin_end_order", "franka_reset", "inference_readiness", "robot_state_filter"],
            "reason": "The driver marks completion after a synchronous motion and later robot-state samples gate inference, but the operator path can issue RUN and open the episode without a Harness-side pre-open completion/acceptance check.",
        },
        {
            "unit": "post_reset_recording_boundary",
            "status": "not_supported",
            "facts": ["attended_task_none", "droid_real_home", "record_window", "robot_state_filter", "writer_wiring"],
            "reason": "The writer drops pre-START samples and RESETTING robot_state, but PhAIL has no task reset and its camera streams are not gated on arm reset completion after an early RUN.",
        },
        {
            "unit": "persistent_episode_identity",
            "status": "supported",
            "facts": ["episode_uuid", "static_persistence"],
            "reason": "A fresh UUID4 hex episode uid is written to meta.json.",
        },
        {
            "unit": "persistent_operator_session_identity",
            "status": "not_supported",
            "facts": ["ui_context", "context_and_home", "robot_meta_fields", "episode_uuid"],
            "reason": "The fixed UI, context, writer, and robot-meta path creates no stable operator/collection-session identifier; the UUID is per episode.",
        },
        {
            "unit": "persistent_reset_carryover_evidence",
            "status": "not_supported",
            "facts": ["begin_end_order", "record_window", "abort_discards", "robot_state_filter", "franka_reset"],
            "reason": "Home commands are kept outside completed episodes, RESETTING state is dropped, ABORT discards the episode, and no reset result, accepted state, prior-episode link, or carryover record is serialized.",
        },
        {
            "unit": "persistent_directive_context",
            "status": "supported",
            "facts": ["ui_context", "context_and_home", "static_persistence"],
            "reason": "The UI's fixed task/object/placement/count context reaches Harness metadata and static.json.",
        },
        {
            "unit": "server_recording_join",
            "status": "supported",
            "facts": [],
            "dependency": "H196",
            "reason": "The independently challenged H196 endpoint trace establishes inference.policy.server.recording.rrd in static.json.",
        },
    ]


def classify(unit_rows: list[dict[str, Any]]) -> str:
    status = {row["unit"]: row["status"] for row in unit_rows}
    if all(value == "supported" for value in status.values()):
        return "lifecycle_evidence_bound"
    if any(status[name] == "supported" for name in ("pre_session_scene_reset_call", "inter_episode_home_command", "post_reset_recording_boundary")):
        if any(status[name] != "supported" for name in ("scene_reset_completion_gate", "home_completion_gate", "persistent_operator_session_identity", "persistent_reset_carryover_evidence")):
            return "mechanics_bound_evidence_incomplete"
    if all(status[name] != "supported" for name in ("pre_session_scene_reset_call", "inter_episode_home_command")):
        return "generic_capability_not_bound_to_phail"
    return "trace_incomplete"


def build(repository: Path) -> dict[str, Any]:
    unit_rows = units()
    return {
        "schema": "h198-current-phail-lifecycle-binding-v1",
        "commit": COMMIT,
        "protocol_sha256": sha256(PROTOCOL),
        "h196_dependency_sha256": sha256(H196),
        "base_paths": list(BASE_PATHS),
        "expansions": list(EXPANSIONS),
        "source_files": source_files(repository),
        "facts": evidence_facts(repository),
        "units": unit_rows,
        "supported_count": sum(row["status"] == "supported" for row in unit_rows),
        "not_supported_count": sum(row["status"] == "not_supported" for row in unit_rows),
        "unresolved_count": sum(row["status"] == "unresolved" for row in unit_rows),
        "classification": classify(unit_rows),
        "dataset_object_opened": False,
        "server_recording_opened": False,
        "performance_field_opened": False,
        "physical_success_established": False,
        "exchangeability_established": False,
        "decision_consequence": (
            "Current PhAIL binds real inter-episode arm/gripper home commands, "
            "episode UUIDs, UI context persistence, and the server-recording join, "
            "but supplies no Task scene reset, pre-open home acceptance gate, "
            "operator-session identity, or persistent reset/carryover evidence. "
            "Keep the dependence gate closed and request those fields explicitly."
        ),
        "scope": (
            "pinned public source ordering and serialization only; not physical "
            "success, historical deployment, independence, exchangeability, or performance"
        ),
    }


def validate(result: dict[str, Any]) -> None:
    require(result.get("schema") == "h198-current-phail-lifecycle-binding-v1", "schema")
    require(result.get("commit") == COMMIT, "commit")
    require(result.get("protocol_sha256") == sha256(PROTOCOL), "protocol")
    require(result.get("h196_dependency_sha256") == sha256(H196), "H196 dependency")
    require(result.get("base_paths") == list(BASE_PATHS), "base paths")
    require(result.get("expansions") == list(EXPANSIONS), "expansions")
    files = result.get("source_files")
    require(isinstance(files, list) and len(files) == len(EXPECTED_BLOBS), "source files")
    require({row["path"]: row["git_blob"] for row in files} == EXPECTED_BLOBS, "blob roster")
    facts = {row["fact_id"]: row for row in result.get("facts", [])}
    require(set(facts) == set(FACTS), "fact roster")
    for fact_id, (path, start, end, required) in FACTS.items():
        row = facts[fact_id]
        require((row["path"], row["start_line"], row["end_line"]) == (path, start, end), f"fact span: {fact_id}")
        require(hashlib.sha256(row["excerpt"].encode()).hexdigest() == row["excerpt_sha256"], f"fact hash: {fact_id}")
        require(all(token in row["excerpt"] for token in required), f"fact semantics: {fact_id}")
    unit_rows = result.get("units")
    require([row["unit"] for row in unit_rows] == list(UNIT_NAMES), "unit roster/order")
    require(all(row["status"] in {"supported", "not_supported", "unresolved"} for row in unit_rows), "unit status")
    require(all(set(row.get("facts", [])) <= set(FACTS) for row in unit_rows), "unit fact reference")
    require(result.get("classification") == classify(unit_rows), "classification")
    require(result.get("supported_count") == 5, "supported count")
    require(result.get("not_supported_count") == 7, "not-supported count")
    require(result.get("unresolved_count") == 0, "unresolved count")
    for key in (
        "dataset_object_opened",
        "server_recording_opened",
        "performance_field_opened",
        "physical_success_established",
        "exchangeability_established",
    ):
        require(result.get(key) is False, key)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, default=DEFAULT_REPOSITORY)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check and not args.repository.exists():
        validate(json.loads(OUTPUT.read_text()))
        print("OK: H198 stored source projection and lifecycle result validate")
        return
    candidate = build(args.repository)
    if args.check:
        require(candidate == json.loads(OUTPUT.read_text()), "exact source rebuild")
        validate(candidate)
        print("OK: H198 pinned source trace reproduces exactly")
    else:
        OUTPUT.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n")
        validate(candidate)
        print(json.dumps(candidate, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
