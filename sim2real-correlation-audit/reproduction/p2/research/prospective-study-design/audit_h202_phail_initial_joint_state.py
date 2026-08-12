#!/usr/bin/env python3
"""Audit the fixed H202 first retained PhAIL joint-state projection."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any

import acquire_h202_phail_initial_joint_state as acquire


ROOT = Path(__file__).resolve().parents[2]
FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h202-phail-initial-joint-state-reconstruction.md"
H199 = FAMILY / "result-h199-phail-randomized-home-target.json"
H201 = FAMILY / "result-h201-phail-home-field-semantics.json"
OUTPUT = FAMILY / "result-h202-phail-initial-joint-state.json"
DEFAULT_REPOSITORY = ROOT / "work" / "h198-positronic-current"
REVISION = "e406176bc526babb06844a48e3627a5c0409eb74"
SOURCE_BLOBS = {
    "positronic/dataset/ds_writer_agent.py": "8f0f06e31fabecce2d093d7768ede88397affcb2",
    "positronic/dataset/local_dataset.py": "8e7d6001ebcbb0a58e39a07b2f58d400f45797fd",
    "positronic/dataset/vector.py": "9a08005cd301df2d54f7be3b57261b6079e0e04a",
    "positronic/drivers/roboarm/__init__.py": "4fe401691d07289e2702fc9c04d7855541fe0436",
    "positronic/drivers/roboarm/franka.py": "a7a5fafe3a1a2c18b24cc948526fc4465586d660",
    "positronic/policy/harness.py": "857b1fe313d67689345fc5fd5954605464fbca38",
    "positronic/wire.py": "1c52667d9cf089712c8e45ee90b7ceee9f1f8fa1",
}
BASE = [0.0, -0.31, 0.0, -1.65, 0.0, 1.522, 0.0]
HALF_WIDTHS = [0.03, 0.05, 0.08, 0.08, 0.10, 0.10, 0.10]
CLASSIFICATIONS = {
    "complete_initial_joint_state_reconstruction",
    "partial_initial_joint_state_reconstruction",
    "insufficient_initial_joint_state_coverage",
    "semantic_trace_incomplete",
    "input_drift_or_integrity_failure",
}


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


def git_blob_sha1(raw: bytes) -> str:
    header = f"blob {len(raw)}\0".encode()
    return hashlib.sha1(header + raw).hexdigest()


def source_trace(repository: Path) -> dict[str, Any]:
    if (repository / ".git").exists():
        require(git(repository, "rev-parse", REVISION).strip() == REVISION, "revision")
        blobs = {
            relative: git(repository, "rev-parse", f"{REVISION}:{relative}").strip()
            for relative in SOURCE_BLOBS
        }
        texts = {
            relative: git(repository, "show", f"{REVISION}:{relative}")
            for relative in SOURCE_BLOBS
        }
    else:
        raw_files = {
            relative: (repository / relative).read_bytes()
            for relative in SOURCE_BLOBS
        }
        blobs = {
            relative: git_blob_sha1(raw)
            for relative, raw in raw_files.items()
        }
        texts = {
            relative: raw.decode("utf-8")
            for relative, raw in raw_files.items()
        }
    require(blobs == SOURCE_BLOBS, "source blobs")
    writer = texts["positronic/dataset/ds_writer_agent.py"]
    vector = texts["positronic/dataset/vector.py"]
    franka = texts["positronic/drivers/roboarm/franka.py"]
    wire = texts["positronic/wire.py"]
    controls = {
        "exact_signal_binding": all(
            token in wire
            for token in (
                "ds_agent.add_signal('robot_state', Serializers.robot_state)",
                "world.connect(robot_arm.state, ds_agent.inputs['robot_state'])",
                "'joint_signal': 'robot_state.q'",
            )
        ),
        "resetting_dropped_error_retained": all(
            token in writer
            for token in (
                "if state.status == RobotStatus.RESETTING:",
                "return None",
                "'.q': state.q",
                "'.error': int(state.status == RobotStatus.ERROR)",
            )
        ),
        "suffix_to_signal_files": all(
            token in writer
            for token in (
                "items = ((name + suffix, v) for suffix, v in value.items())",
                "ep_writer.append(full_name, v, ts_ns, extra_ts)",
            )
        ),
        "parquet_schema": all(
            token in vector
            for token in (
                "column_names = ['timestamp', 'value']",
                "pa.array(self._timestamps, type=pa.int64())",
                "SimpleSignalWriter",
            )
        ),
        "first_nonreset_is_observation_not_target": all(
            token in franka
            for token in (
                "target = target + variation",
                "robot.set_target_joints(target, asynchronous=False)",
                "robot_state._finish_reset()",
                "self.state.emit(robot_state)",
                "self.array[FrankaState.Q_OFFSET : FrankaState.Q_OFFSET + 7] = state.q",
            )
        ),
    }
    return {
        "revision": REVISION,
        "source_mode": "git-blob-bound source projection",
        "source_blobs": blobs,
        "controls": controls,
        "semantic_trace_complete": all(controls.values()),
        "first_q_semantics": (
            "first retained seven-joint observation after RESETTING samples are "
            "dropped; ERROR observations are retained and separately flagged"
        ),
        "not_commanded_target": True,
    }


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate_projection() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    cohort = acquire.load_cohort()
    inventory = acquire.load_inventory()
    selected = acquire.select_sources(cohort, inventory)
    require(len(selected) == acquire.EXPECTED_EPISODES, "selection coverage")
    selected_by_id = {row["episode_id"]: row for row in selected}
    rows = read_csv(acquire.PROJECTION)
    manifest = read_csv(acquire.SOURCE_MANIFEST)
    require(len(rows) == acquire.EXPECTED_EPISODES, "projection rows")
    require(len(manifest) == 2 * acquire.EXPECTED_EPISODES, "manifest rows")
    require(set(rows[0]) == set(acquire.PROJECTION_FIELDS), "projection schema")
    require(set(manifest[0]) == set(acquire.MANIFEST_FIELDS), "manifest schema")
    require(len({row["episode_id"] for row in rows}) == len(rows), "duplicate projection")
    require(
        {(row["episode_id"], row["signal"]) for row in manifest}
        == {
            (episode_id, signal)
            for episode_id in selected_by_id
            for signal in acquire.SIGNALS
        },
        "manifest identity",
    )
    manifest_by_key = {
        (row["episode_id"], row["signal"]): row for row in manifest
    }
    parsed = []
    total_bytes = 0
    for row in rows:
        episode_id = row["episode_id"]
        require(episode_id in selected_by_id, "episode identity")
        item = selected_by_id[episode_id]
        q = [float(row[f"q{i}"]) for i in range(7)]
        require(all(math.isfinite(value) for value in q), "finite q")
        error = int(row["error"])
        require(error in {0, 1}, "error")
        timestamp = int(row["timestamp_ns"])
        require(timestamp > 0, "timestamp")
        for signal, prefix in (
            ("robot_state.q", "q"),
            ("robot_state.error", "error"),
        ):
            expected = item[signal]
            require(row[f"{prefix}_path"] == expected["key"], "path")
            require(row[f"{prefix}_etag"] == expected["etag"], "etag")
            require(int(row[f"{prefix}_size"]) == expected["size"], "size")
            require(len(row[f"{prefix}_sha256"]) == 64, "source sha")
            require(int(row[f"{prefix}_row_count"]) > 0, "row count")
            source = manifest_by_key[(episode_id, signal)]
            require(source["path"] == expected["key"], "manifest path")
            require(source["etag"] == expected["etag"], "manifest etag")
            require(int(source["advertised_size"]) == expected["size"], "manifest size")
            require(int(source["byte_count"]) == expected["size"], "manifest bytes")
            require(source["sha256"] == row[f"{prefix}_sha256"], "manifest sha")
            require(int(source["row_count"]) == int(row[f"{prefix}_row_count"]), "manifest rows")
            require(len(source["schema_sha256"]) == 64, "schema sha")
            total_bytes += expected["size"]
        require(
            PurePosixPath(row["q_path"]).parent
            == PurePosixPath(row["error_path"]).parent,
            "source pair root",
        )
        parsed.append(
            {
                "episode_id": episode_id,
                "timestamp_ns": timestamp,
                "error": error,
                "q": q,
            }
        )
    parsed.sort(key=lambda row: row["episode_id"])
    return parsed, {
        "selected_episode_count": len(selected),
        "source_object_count": len(manifest),
        "total_source_bytes": total_bytes,
        "unique_source_sha256_count": len({row["sha256"] for row in manifest}),
        "projection_sha256": sha256(acquire.PROJECTION),
        "source_manifest_sha256": sha256(acquire.SOURCE_MANIFEST),
    }


def quantile_linear(values: list[float], probability: float) -> float:
    require(bool(values), "empty quantile")
    require(0 <= probability <= 1, "quantile probability")
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def population_std(values: list[float]) -> float:
    mean = sum(values) / len(values)
    return math.sqrt(sum((value - mean) ** 2 for value in values) / len(values))


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    valid = [row for row in rows if row["error"] == 0]
    errors = [row for row in rows if row["error"] == 1]
    require(bool(valid), "no valid achieved states")
    deviations = [
        [value - base for value, base in zip(row["q"], BASE, strict=True)]
        for row in valid
    ]
    joint_rows = []
    for index, half_width in enumerate(HALF_WIDTHS):
        values = [row[index] for row in deviations]
        mean = sum(values) / len(values)
        observed_std = population_std(values)
        joint_rows.append(
            {
                "joint_index": index,
                "minimum_rad": min(values),
                "q05_rad": quantile_linear(values, 0.05),
                "median_rad": quantile_linear(values, 0.50),
                "mean_rad": mean,
                "population_std_rad": observed_std,
                "q95_rad": quantile_linear(values, 0.95),
                "maximum_rad": max(values),
                "fraction_inside_configured_target_support": (
                    sum(-half_width <= value <= half_width for value in values)
                    / len(values)
                ),
                "observed_std_to_uniform_target_std_ratio": (
                    observed_std / (half_width / math.sqrt(3))
                ),
            }
        )
    norms = [math.sqrt(sum(value * value for value in row)) for row in deviations]
    norm_summary = {
        "minimum_rad": min(norms),
        "median_rad": quantile_linear(norms, 0.50),
        "mean_rad": sum(norms) / len(norms),
        "rms_rad": math.sqrt(sum(value * value for value in norms) / len(norms)),
        "q95_rad": quantile_linear(norms, 0.95),
        "maximum_rad": max(norms),
    }
    return {
        "file_pair_count": len(rows),
        "schema_valid_timestamp_aligned_count": len(rows),
        "first_error_count": len(errors),
        "valid_achieved_state_count": len(valid),
        "valid_achieved_state_fraction": len(valid) / acquire.EXPECTED_EPISODES,
        "joint_deviation_summary": joint_rows,
        "euclidean_joint_deviation_summary": norm_summary,
        "configured_base_home_joints_rad": BASE,
        "configured_target_half_widths_rad": HALF_WIDTHS,
    }


def classify(summary: dict[str, Any], semantic_trace_complete: bool) -> str:
    if not semantic_trace_complete:
        return "semantic_trace_incomplete"
    count = summary["valid_achieved_state_count"]
    if count == acquire.EXPECTED_EPISODES:
        return "complete_initial_joint_state_reconstruction"
    if count / acquire.EXPECTED_EPISODES >= 0.90:
        return "partial_initial_joint_state_reconstruction"
    return "insufficient_initial_joint_state_coverage"


def build(repository: Path) -> dict[str, Any]:
    rows, integrity = validate_projection()
    trace = source_trace(repository)
    summary = summarize(rows)
    return {
        "schema": "h202-phail-initial-joint-state-v1",
        "protocol_sha256": sha256(PROTOCOL),
        "h199_sha256": sha256(H199),
        "h201_sha256": sha256(H201),
        "cohort_sha256": sha256(acquire.COHORT),
        "inventory_sha256": sha256(acquire.INVENTORY),
        "integrity": integrity,
        "source_trace": trace,
        "summary": summary,
        "classification": classify(summary, trace["semantic_trace_complete"]),
        "decoded_signal_values": ["first robot_state.q", "first robot_state.error"],
        "later_joint_values_retained_or_summarized": False,
        "action_command_camera_media_or_performance_opened": False,
        "target_draw_recovered": False,
        "reset_acceptance_established": False,
        "historical_execution_fidelity_established": False,
        "decision_consequence": (
            "The release permits a bounded achieved-first-joint-state "
            "reconstruction if coverage passes. This can describe initial arm "
            "variation but cannot recover the commanded draw, certify reset "
            "acceptance, or resolve scene/carryover/session dependence."
        ),
    }


def validate(result: dict[str, Any]) -> None:
    require(result.get("schema") == "h202-phail-initial-joint-state-v1", "schema")
    require(result.get("protocol_sha256") == sha256(PROTOCOL), "protocol")
    require(result.get("h199_sha256") == sha256(H199), "H199")
    require(result.get("h201_sha256") == sha256(H201), "H201")
    require(result.get("cohort_sha256") == acquire.COHORT_SHA256, "cohort")
    require(result.get("inventory_sha256") == acquire.INVENTORY_SHA256, "inventory")
    integrity = result["integrity"]
    require(integrity["selected_episode_count"] == acquire.EXPECTED_EPISODES, "selected")
    require(integrity["source_object_count"] == 2 * acquire.EXPECTED_EPISODES, "objects")
    require(
        1 <= integrity["unique_source_sha256_count"]
        <= integrity["source_object_count"],
        "unique source count",
    )
    trace = result["source_trace"]
    require(trace["source_blobs"] == SOURCE_BLOBS, "source blobs")
    require(trace["semantic_trace_complete"] is True, "semantic trace")
    summary = result["summary"]
    require(summary["file_pair_count"] == acquire.EXPECTED_EPISODES, "file pairs")
    require(
        summary["valid_achieved_state_count"] + summary["first_error_count"]
        == acquire.EXPECTED_EPISODES,
        "coverage partition",
    )
    require(len(summary["joint_deviation_summary"]) == 7, "joint rows")
    require(
        result.get("classification")
        == classify(summary, trace["semantic_trace_complete"]),
        "classification",
    )
    require(result.get("classification") in CLASSIFICATIONS, "classification value")
    for key in (
        "later_joint_values_retained_or_summarized",
        "action_command_camera_media_or_performance_opened",
        "target_draw_recovered",
        "reset_acceptance_established",
        "historical_execution_fidelity_established",
    ):
        require(result.get(key) is False, key)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, default=DEFAULT_REPOSITORY)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    candidate = build(args.repository)
    validate(candidate)
    if args.check:
        require(candidate == json.loads(OUTPUT.read_text()), "exact rebuild")
        print("OK: H202 exact first-state result reproduces")
    else:
        OUTPUT.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n")
        print(json.dumps(candidate, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
