#!/usr/bin/env python3
"""Compare PhAIL's randomized Franka home target at v0.2.1 and current."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h199-phail-randomized-home-target.md"
H198 = FAMILY / "result-h198-current-phail-lifecycle-binding.json"
OUTPUT = FAMILY / "result-h199-phail-randomized-home-target.json"
DEFAULT_REPOSITORY = ROOT / "work" / "h198-positronic-current"
BASE = "e406176bc526babb06844a48e3627a5c0409eb74"
CURRENT = "01b78e6f62ff5913490c360afdd2712eee070524"
PATHS = (
    "positronic/inference.py",
    "positronic/cfg/embodiment.py",
    "positronic/cfg/hardware/roboarm/__init__.py",
    "positronic/drivers/roboarm/__init__.py",
    "positronic/drivers/roboarm/command.py",
    "positronic/drivers/roboarm/franka.py",
    "positronic/policy/harness.py",
    "positronic/dataset/ds_writer_agent.py",
    "positronic/dataset/serializers.py",
    "positronic/dataset/local_dataset.py",
    "positronic/wire.py",
)
EXPECTED_BLOBS = {
    BASE: {
        "positronic/inference.py": "c9bc29b72f15763e17740537f08a73d58675217c",
        "positronic/cfg/embodiment.py": None,
        "positronic/cfg/hardware/roboarm/__init__.py": "4a6352084f0c937a71ec0131e6cfdd97329fd73a",
        "positronic/drivers/roboarm/__init__.py": "4fe401691d07289e2702fc9c04d7855541fe0436",
        "positronic/drivers/roboarm/command.py": "d588cf98d9070c2c18440c954a399f2ac704f88b",
        "positronic/drivers/roboarm/franka.py": "a7a5fafe3a1a2c18b24cc948526fc4465586d660",
        "positronic/policy/harness.py": "857b1fe313d67689345fc5fd5954605464fbca38",
        "positronic/dataset/ds_writer_agent.py": "8f0f06e31fabecce2d093d7768ede88397affcb2",
        "positronic/dataset/serializers.py": None,
        "positronic/dataset/local_dataset.py": "8e7d6001ebcbb0a58e39a07b2f58d400f45797fd",
        "positronic/wire.py": "1c52667d9cf089712c8e45ee90b7ceee9f1f8fa1",
    },
    CURRENT: {
        "positronic/inference.py": "57dd5e20829acb606b8faa45b40dde923128b3b7",
        "positronic/cfg/embodiment.py": "7bc708eece4ea12c443ddfea6156f4d68a51a1ea",
        "positronic/cfg/hardware/roboarm/__init__.py": "4d27c99f622f6d2be40577a57b2d076c94a8695b",
        "positronic/drivers/roboarm/__init__.py": "4fe401691d07289e2702fc9c04d7855541fe0436",
        "positronic/drivers/roboarm/command.py": "964457cff3f7b808d955cfed2da710b3d2657d17",
        "positronic/drivers/roboarm/franka.py": "fbe608d1bd4fdae61309c630a0efcc990653c0a3",
        "positronic/policy/harness.py": "62dd01974588785000285ef6c8cba4672386690a",
        "positronic/dataset/ds_writer_agent.py": "765b811438d1a0e7db32698e24f9d21488495be0",
        "positronic/dataset/serializers.py": "c7a1ccacb9f0a98f9eb7e93981126542bab1e836",
        "positronic/dataset/local_dataset.py": "b14883ea6d970a5b9b84fc7c8ee930bc7a889495",
        "positronic/wire.py": "026f94cfd740f80cf8c9d859aaf24a55e8c34214",
    },
}
CLASSIFICATIONS = {
    "historical_and_current_unrecorded_randomized_home",
    "current_only_unrecorded_randomized_home",
    "randomized_home_draw_recorded",
    "no_randomized_home_bound",
    "trace_incomplete",
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


def git_bytes(repository: Path, revision: str, source_path: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(repository), "show", f"{revision}:{source_path}"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout


def parse_list_after(label: str, text: str) -> list[float]:
    match = re.search(rf"{re.escape(label)}\s*=\s*(\[[^\]]+\])", text)
    require(match is not None, f"missing vector: {label}")
    value = ast.literal_eval(match.group(1))
    require(
        isinstance(value, list)
        and len(value) == 7
        and all(isinstance(x, int | float) for x in value),
        f"invalid vector: {label}",
    )
    return [float(x) for x in value]


def parse_default_variation(text: str) -> list[float]:
    match = re.search(
        r"home_joints_variation\s+if\s+home_joints_variation\s+is\s+not\s+None\s+else\s+(\[[^\]]+\])",
        text,
    )
    require(match is not None, "missing home variation default")
    value = ast.literal_eval(match.group(1))
    require(isinstance(value, list) and len(value) == 7, "variation vector")
    return [float(x) for x in value]


def source_roster(repository: Path) -> dict[str, list[dict[str, Any]]]:
    rows: dict[str, list[dict[str, Any]]] = {}
    for revision in (BASE, CURRENT):
        endpoint_rows = []
        for source_path in PATHS:
            expected = EXPECTED_BLOBS[revision][source_path]
            exists = (
                subprocess.run(
                    ["git", "-C", str(repository), "cat-file", "-e", f"{revision}:{source_path}"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                ).returncode
                == 0
            )
            require(exists == (expected is not None), f"existence: {revision}:{source_path}")
            if not exists:
                endpoint_rows.append({"path": source_path, "present": False, "git_blob": None})
                continue
            blob = git(repository, "rev-parse", f"{revision}:{source_path}").strip()
            require(blob == expected, f"blob: {revision}:{source_path}")
            raw = git_bytes(repository, revision, source_path)
            endpoint_rows.append(
                {
                    "path": source_path,
                    "present": True,
                    "git_blob": blob,
                    "sha256": hashlib.sha256(raw).hexdigest(),
                    "byte_count": len(raw),
                }
            )
        rows[revision] = endpoint_rows
    return rows


def endpoint_analysis(repository: Path, revision: str) -> dict[str, Any]:
    inference = git_bytes(repository, revision, "positronic/inference.py").decode()
    cfg = git_bytes(
        repository, revision, "positronic/cfg/hardware/roboarm/__init__.py"
    ).decode()
    driver = git_bytes(
        repository, revision, "positronic/drivers/roboarm/franka.py"
    ).decode()
    harness = git_bytes(repository, revision, "positronic/policy/harness.py").decode()
    writer = git_bytes(
        repository, revision, "positronic/dataset/ds_writer_agent.py"
    ).decode()
    local = git_bytes(
        repository, revision, "positronic/dataset/local_dataset.py"
    ).decode()

    if revision == BASE:
        phail_bound = all(
            token in inference
            for token in ("'phail':", "droid_setup.override(", "phail_multiple")
        )
    else:
        phail_bound = all(
            token in inference
            for token in (
                "'phail':",
                "embodiment=positronic.cfg.embodiment.droid",
                "phail_multiple",
            )
        )
    if EXPECTED_BLOBS[revision]["positronic/cfg/embodiment.py"] is not None:
        embodiment = git_bytes(
            repository, revision, "positronic/cfg/embodiment.py"
        ).decode()
        reset_source = "roboarm_command.Reset()" in embodiment
    else:
        reset_source = (
            "roboarm.command.Reset()" in harness
            or ("_home" in harness and "Reset()" in harness)
        )
    droid_reset_bound = (
        "franka_droid" in cfg and "home_joints" in cfg and reset_source
    )
    base_home = parse_list_after("home_joints", cfg)
    variation = parse_default_variation(driver)
    cfg_exposes_variation = "home_joints_variation" in cfg
    draw_bound = all(
        token in driver
        for token in (
            "np.random.uniform",
            "-np.asarray(self._home_joints_variation)",
            "np.asarray(self._home_joints_variation)",
            "target = target + variation",
        )
    )
    synchronous = "set_target_joints(target, asynchronous=False)" in driver
    realized_target_serialized = any(
        token in text
        for text in (inference, cfg, driver, harness, writer, local)
        for token in (
            "'home_target'",
            '"home_target"',
            "'reset_target'",
            '"reset_target"',
            "'home_joints_realized'",
            '"home_joints_realized"',
        )
    )
    seed_serialized = any(
        token in text
        for text in (inference, cfg, driver, harness, writer, local)
        for token in (
            "'reset_seed'",
            '"reset_seed"',
            "'home_seed'",
            '"home_seed"',
            "'rng_state'",
            '"rng_state"',
        )
    )
    rng_interface = (
        "numpy_global_random_state"
        if "np.random.uniform" in driver
        and "default_rng" not in driver
        and "np.random.seed" not in driver
        else "other_or_seeded"
    )
    if revision == BASE:
        reset_outside_window = all(
            token in harness
            for token in (
                "self.ds_command.emit(DsWriterCommand.STOP",
                "self.ds_command.emit(DsWriterCommand.ABORT())",
                "self._home()",
            )
        )
    else:
        reset_outside_window = all(
            token in harness
            for token in (
                "self.ds_command.emit(DsWriterCommand.STOP",
                "self.ds_command.emit(DsWriterCommand.ABORT())",
                "self._home(clock)",
            )
        )

    return {
        "revision": revision,
        "phail_droid_binding": phail_bound,
        "droid_arm_reset_binding": droid_reset_bound,
        "base_home_joints_rad": base_home,
        "configuration_exposes_home_joints_variation": cfg_exposes_variation,
        "effective_home_joints_variation_rad": variation,
        "random_draw_bound": draw_bound,
        "draw_distribution": "independent_uniform_per_joint_on_symmetric_half_widths",
        "rng_interface": rng_interface,
        "arm_target_execution_synchronous": synchronous,
        "realized_target_serialized": realized_target_serialized,
        "seed_or_rng_state_serialized": seed_serialized,
        "reset_command_ordered_outside_retained_episode": reset_outside_window,
        "source_bound_not_execution_fidelity": True,
    }


def quantitative_summary(variation: list[float]) -> dict[str, Any]:
    sum_squares = sum(x * x for x in variation)
    return {
        "half_widths_rad": variation,
        "ranges_rad": [[-x, x] for x in variation],
        "half_widths_deg": [x * 180.0 / math.pi for x in variation],
        "ranges_deg": [
            [-x * 180.0 / math.pi, x * 180.0 / math.pi] for x in variation
        ],
        "sum_squared_half_widths_rad2": sum_squares,
        "maximum_euclidean_joint_perturbation_rad": math.sqrt(sum_squares),
        "rms_euclidean_joint_perturbation_rad": math.sqrt(sum_squares / 3.0),
        "interpretation": "configuration-space support only; no end-effector or outcome inference",
    }


def classify(endpoints: list[dict[str, Any]]) -> str:
    by_revision = {row["revision"]: row for row in endpoints}

    def positive(row: dict[str, Any]) -> bool:
        return (
            row["phail_droid_binding"]
            and row["droid_arm_reset_binding"]
            and row["random_draw_bound"]
            and any(x > 0 for x in row["effective_home_joints_variation_rad"])
        )

    base_positive = positive(by_revision[BASE])
    current_positive = positive(by_revision[CURRENT])
    any_recorded = any(
        row["realized_target_serialized"] or row["seed_or_rng_state_serialized"]
        for row in endpoints
    )
    if any_recorded and (base_positive or current_positive):
        return "randomized_home_draw_recorded"
    if base_positive and current_positive:
        return "historical_and_current_unrecorded_randomized_home"
    if current_positive:
        return "current_only_unrecorded_randomized_home"
    if not base_positive and not current_positive:
        return "no_randomized_home_bound"
    return "trace_incomplete"


def build(repository: Path) -> dict[str, Any]:
    require(git(repository, "rev-parse", CURRENT).strip() == CURRENT, "current revision")
    require(git(repository, "rev-parse", BASE).strip() == BASE, "baseline revision")
    require(not git(repository, "status", "--porcelain=v1").strip(), "dirty checkout")
    endpoints = [
        endpoint_analysis(repository, BASE),
        endpoint_analysis(repository, CURRENT),
    ]
    require(
        endpoints[0]["effective_home_joints_variation_rad"]
        == endpoints[1]["effective_home_joints_variation_rad"],
        "endpoint variation mismatch",
    )
    summary = quantitative_summary(endpoints[0]["effective_home_joints_variation_rad"])
    return {
        "schema": "h199-phail-randomized-home-target-v1",
        "protocol_sha256": sha256(PROTOCOL),
        "h198_dependency_sha256": sha256(H198),
        "revisions": {"v0.2.1": BASE, "current": CURRENT},
        "fixed_paths": list(PATHS),
        "source_files": source_roster(repository),
        "endpoints": endpoints,
        "quantitative_summary": summary,
        "classification": classify(endpoints),
        "comparison_exposure": {
            "current": "result_exposed_by_h198",
            "v0.2.1": "prospective_before_endpoint_source_opening",
        },
        "dataset_content_opened": False,
        "performance_field_opened": False,
        "physical_reset_adequacy_established": False,
        "historical_execution_fidelity_established": False,
        "performance_effect_established": False,
        "decision_consequence": (
            "The source-bound v0.2.1 and pinned current PhAIL paths both inherit "
            "a nonzero per-reset uniform Franka home-joint perturbation without "
            "serializing the realized target or RNG identity. Request those "
            "fields as lifecycle context; do not infer reset inadequacy or a "
            "performance effect."
        ),
    }


def validate(result: dict[str, Any]) -> None:
    require(result.get("schema") == "h199-phail-randomized-home-target-v1", "schema")
    require(result.get("protocol_sha256") == sha256(PROTOCOL), "protocol")
    require(result.get("h198_dependency_sha256") == sha256(H198), "H198 dependency")
    require(result.get("revisions") == {"v0.2.1": BASE, "current": CURRENT}, "revisions")
    require(result.get("fixed_paths") == list(PATHS), "paths")
    source = result.get("source_files")
    require(set(source) == {BASE, CURRENT}, "source endpoints")
    for revision in (BASE, CURRENT):
        observed = {row["path"]: row["git_blob"] for row in source[revision]}
        require(observed == EXPECTED_BLOBS[revision], f"source blobs: {revision}")
    endpoints = result.get("endpoints")
    require(
        [row["revision"] for row in endpoints] == [BASE, CURRENT],
        "endpoint order",
    )
    expected_vector = [0.03, 0.05, 0.08, 0.08, 0.10, 0.10, 0.10]
    for row in endpoints:
        require(row["effective_home_joints_variation_rad"] == expected_vector, "variation")
        require(row["random_draw_bound"] is True, "draw")
        require(row["realized_target_serialized"] is False, "target serialization")
        require(row["seed_or_rng_state_serialized"] is False, "seed serialization")
        require(row["source_bound_not_execution_fidelity"] is True, "source scope")
    require(result.get("classification") == classify(endpoints), "classification")
    require(result.get("classification") in CLASSIFICATIONS, "classification value")
    q = result["quantitative_summary"]
    require(q["half_widths_rad"] == expected_vector, "quantitative vector")
    sum_squares = sum(x * x for x in expected_vector)
    require(math.isclose(q["sum_squared_half_widths_rad2"], sum_squares, rel_tol=0, abs_tol=1e-15), "sum squares")
    require(math.isclose(q["maximum_euclidean_joint_perturbation_rad"], math.sqrt(sum_squares), rel_tol=0, abs_tol=1e-15), "maximum")
    require(math.isclose(q["rms_euclidean_joint_perturbation_rad"], math.sqrt(sum_squares / 3), rel_tol=0, abs_tol=1e-15), "rms")
    for key in (
        "dataset_content_opened",
        "performance_field_opened",
        "physical_reset_adequacy_established",
        "historical_execution_fidelity_established",
        "performance_effect_established",
    ):
        require(result.get(key) is False, key)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, default=DEFAULT_REPOSITORY)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check and not args.repository.exists():
        validate(json.loads(OUTPUT.read_text()))
        print("OK: H199 stored source projection and arithmetic validate")
        return
    candidate = build(args.repository)
    if args.check:
        require(candidate == json.loads(OUTPUT.read_text()), "exact rebuild")
        validate(candidate)
        print("OK: H199 endpoint comparison reproduces exactly")
    else:
        OUTPUT.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n")
        validate(candidate)
        print(json.dumps(candidate, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
