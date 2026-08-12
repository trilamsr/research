#!/usr/bin/env python3
"""Exploratory H206 monotonic/wall-clock bridge audit."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h206-phail-monotonic-wall-clock-bridge.md"
EXPOSURE = FAMILY / "exploration-h206-phail-clock-offset-exposure.md"
COHORT = FAMILY / "result-h187-phail-context-support-sanitized.csv"
H202_PROJECTION = FAMILY / "projection-h202-phail-initial-joint-state.csv"
H202_RESULT = FAMILY / "result-h202-phail-initial-joint-state.json"
PROJECTION = FAMILY / "projection-h206-phail-clock-offset-regimes.csv"
OUTPUT = FAMILY / "result-h206-phail-monotonic-wall-clock-bridge.json"
DEFAULT_REPOSITORY = ROOT / "work" / "h198-positronic-current"
COHORT_SHA256 = "ad43fca1da065a1cb7fd84dfa9afc5691c72ebe12e7f165c68a0050e51e87ebe"
H202_PROJECTION_SHA256 = (
    "44b7cd9729c691a610cc1fbbefffc5668d31030e013b92f2d4550f9869020370"
)
H202_RESULT_SHA256 = (
    "4e60b6c6cbc0eabcaf4ae7761119b5af89bbaf6707e53cce8f0ec3c227a96043"
)
REVISION = "e406176bc526babb06844a48e3627a5c0409eb74"
EXPECTED_EPISODES = 594
SOURCE_SHA256 = {
    "pimm/world.py": "cca1fbe28cd69adef15dac7c7c8a7b30386bcf9cf06d8c943b8c2d1736c5560f",
    "positronic/inference.py": "f0d9565b501b70ea15421d86b0e742a8c57d5c22446f57f36f9bd7cf79d43080",
    "positronic/dataset/ds_writer_agent.py": (
        "40435c6a11cb8f75bb1dc79933da1ea8b47586cffa2988c3bf44756fb1fbe483"
    ),
    "positronic/dataset/local_dataset.py": (
        "e0308688d7daa43c4c27b00a5f199ed8ffc86caaf3b6b1b2cf9177adec82e493"
    ),
    "positronic/wire.py": "586baf9bd736a623fc4b19027ea05158757f4e7e474a9f73081090a992329763",
}
THRESHOLDS_SECONDS = (0.001, 0.01, 0.1, 1, 10, 60, 600, 3_600, 21_600, 86_400)
CANONICAL_THRESHOLD_NS = 3_600_000_000_000
PROJECTION_FIELDS = (
    "offset_rank",
    "episode_id",
    "policy_model",
    "utc_date",
    "created_ts_ns",
    "first_timestamp_ns",
    "offset_ns",
    "gap_from_previous_ns",
    "group_1h",
)
CLASSIFICATIONS = {
    "scale_separated_clock_offset_regimes",
    "clock_offset_structure_without_scale_separation",
    "no_clock_offset_structure_at_fixed_resolution",
    "clock_semantic_trace_incomplete",
    "input_drift_or_integrity_failure",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git_bytes(repository: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(repository), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout


def source_trace(repository: Path) -> dict[str, Any]:
    if (repository / ".git").exists():
        revision = git_bytes(repository, "rev-parse", REVISION).decode().strip()
        require(revision == REVISION, "source revision")
        files = {
            relative: git_bytes(repository, "show", f"{REVISION}:{relative}")
            for relative in SOURCE_SHA256
        }
    else:
        files = {
            relative: (repository / relative).read_bytes()
            for relative in SOURCE_SHA256
        }
    hashes = {relative: sha256_bytes(raw) for relative, raw in files.items()}
    require(hashes == SOURCE_SHA256, "source hashes")
    texts = {relative: raw.decode("utf-8") for relative, raw in files.items()}
    world = texts["pimm/world.py"]
    inference = texts["positronic/inference.py"]
    writer = texts["positronic/dataset/ds_writer_agent.py"]
    local = texts["positronic/dataset/local_dataset.py"]
    wire = texts["positronic/wire.py"]
    controls = {
        "real_inference_uses_default_world": (
            "with writer_cm as dataset_writer, pimm.World() as world:" in inference
        ),
        "world_defaults_to_system_clock": (
            "self._clock = clock or SystemClock()" in world
        ),
        "system_clock_is_monotonic_ns": (
            "class SystemClock(Clock):" in world
            and "return time.monotonic_ns()" in world
        ),
        "real_inference_uses_clock_mode": (
            "wire.wire(world, harness, dataset_writer, camera_emitters, "
            "robot_arm, gripper, gui, TimeMode.CLOCK)"
            in inference
        ),
        "writer_primary_time_is_world_clock": all(
            token in writer
            for token in (
                "world_time_ns, message_time_ns = clock.now_ns(), msg.ts",
                "primary_ts = world_time_ns if self._time_mode == "
                "TimeMode.CLOCK else message_time_ns",
                "_append(ep_writer, name, value, primary_ts, extra_ts)",
            )
        ),
        "episode_creation_is_wall_time_ns": (
            "'created_ts_ns': created_ts_ns or time.time_ns()" in local
        ),
        "robot_state_signal_binding": all(
            token in wire
            for token in (
                "ds_agent.add_signal('robot_state', Serializers.robot_state)",
                "world.connect(robot_arm.state, ds_agent.inputs['robot_state'])",
            )
        ),
    }
    require(all(controls.values()), "clock semantic trace")
    return {
        "revision": REVISION,
        "source_mode": "hash-bound v0.2.1 source projection",
        "source_sha256": hashes,
        "controls": controls,
        "semantic_trace_complete": True,
    }


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_rows() -> list[dict[str, Any]]:
    require(sha256(COHORT) == COHORT_SHA256, "cohort hash")
    require(sha256(H202_PROJECTION) == H202_PROJECTION_SHA256, "H202 projection hash")
    require(sha256(H202_RESULT) == H202_RESULT_SHA256, "H202 result hash")
    cohort = read_csv(COHORT)
    projection = read_csv(H202_PROJECTION)
    require(len(cohort) == len(projection) == EXPECTED_EPISODES, "episode count")
    cohort_by_id = {row["episode_id"]: row for row in cohort}
    projection_by_id = {row["episode_id"]: row for row in projection}
    require(len(cohort_by_id) == len(cohort), "cohort identity")
    require(len(projection_by_id) == len(projection), "projection identity")
    require(set(cohort_by_id) == set(projection_by_id), "join identity")
    rows = []
    for episode_id in sorted(cohort_by_id):
        context = cohort_by_id[episode_id]
        first = projection_by_id[episode_id]
        created = int(context["created_ts_ns"])
        monotonic = int(first["timestamp_ns"])
        require(created > 0 and monotonic > 0, "positive timestamps")
        require(context["policy_model"] and context["utc_date"], "context fields")
        rows.append(
            {
                "episode_id": episode_id,
                "policy_model": context["policy_model"],
                "utc_date": context["utc_date"],
                "created_ts_ns": created,
                "first_timestamp_ns": monotonic,
                "offset_ns": created - monotonic,
            }
        )
    require(len({row["created_ts_ns"] for row in rows}) == len(rows), "wall timestamp identity")
    require(
        len({row["first_timestamp_ns"] for row in rows}) == len(rows),
        "monotonic timestamp identity",
    )
    return rows


def labels_for_threshold(sorted_rows: list[dict[str, Any]], threshold_ns: int) -> list[int]:
    labels = [0]
    for previous, current in zip(sorted_rows, sorted_rows[1:]):
        labels.append(
            labels[-1] + int(current["offset_ns"] - previous["offset_ns"] > threshold_ns)
        )
    return labels


def group_sizes(labels: list[int]) -> list[int]:
    return sorted(Counter(labels).values())


def positions_contiguous(labels: list[int], group: int) -> bool:
    positions = [index for index, label in enumerate(labels) if label == group]
    return max(positions) - min(positions) + 1 == len(positions)


def discordant_pairs(rows: list[dict[str, Any]]) -> tuple[int, float]:
    ordered = sorted(rows, key=lambda row: (row["created_ts_ns"], row["episode_id"]))
    discordant = 0
    for first_index, first in enumerate(ordered):
        for second in ordered[first_index + 1 :]:
            discordant += int(
                first["first_timestamp_ns"] > second["first_timestamp_ns"]
            )
    total = math.comb(len(rows), 2)
    tau_a = 1.0 if total == 0 else 1.0 - 2.0 * discordant / total
    return discordant, tau_a


def threshold_key(seconds: float) -> str:
    return f"{seconds:g}s"


def synthetic_controls() -> dict[str, bool]:
    rows = [
        {"created_ts_ns": 110, "first_timestamp_ns": 10},
        {"created_ts_ns": 221, "first_timestamp_ns": 20},
        {"created_ts_ns": 333, "first_timestamp_ns": 30},
    ]
    offsets = [
        row["created_ts_ns"] - row["first_timestamp_ns"] for row in rows
    ]
    sorted_rows = [
        {"offset_ns": offset, "episode_id": str(index)}
        for index, offset in enumerate(offsets)
    ]
    threshold_boundary = labels_for_threshold(sorted_rows, 101) == [0, 0, 1]
    threshold_strict = labels_for_threshold(sorted_rows, 102) == [0, 0, 0]
    kendall_rows = [
        {"episode_id": "a", "created_ts_ns": 1, "first_timestamp_ns": 1},
        {"episode_id": "b", "created_ts_ns": 2, "first_timestamp_ns": 3},
        {"episode_id": "c", "created_ts_ns": 3, "first_timestamp_ns": 2},
    ]
    discordant, tau = discordant_pairs(kendall_rows)
    contiguous = (
        positions_contiguous([0, 0, 1, 1], 0)
        and positions_contiguous([0, 0, 1, 1], 1)
        and not positions_contiguous([0, 1, 0], 0)
    )
    return {
        "integer_offsets": offsets == [100, 201, 303],
        "strict_threshold_boundary": threshold_boundary and threshold_strict,
        "kendall_known_answer": discordant == 1 and math.isclose(tau, 1 / 3),
        "contiguity_known_answer": contiguous,
        "stable_sort": [
            row["episode_id"]
            for row in sorted(
                [
                    {"offset_ns": 1, "episode_id": "b"},
                    {"offset_ns": 1, "episode_id": "a"},
                ],
                key=lambda row: (row["offset_ns"], row["episode_id"]),
            )
        ]
        == ["a", "b"],
    }


def build_projection(
    sorted_rows: list[dict[str, Any]], labels: list[int]
) -> tuple[list[dict[str, str]], bytes]:
    projected = []
    previous_offset: int | None = None
    for rank, (row, label) in enumerate(zip(sorted_rows, labels), start=1):
        gap = "" if previous_offset is None else str(row["offset_ns"] - previous_offset)
        projected.append(
            {
                "offset_rank": str(rank),
                "episode_id": row["episode_id"],
                "policy_model": row["policy_model"],
                "utc_date": row["utc_date"],
                "created_ts_ns": str(row["created_ts_ns"]),
                "first_timestamp_ns": str(row["first_timestamp_ns"]),
                "offset_ns": str(row["offset_ns"]),
                "gap_from_previous_ns": gap,
                "group_1h": str(label + 1),
            }
        )
        previous_offset = row["offset_ns"]
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(
        handle, fieldnames=PROJECTION_FIELDS, lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows(projected)
    return projected, handle.getvalue().encode()


def summarize_group(
    group_rows: list[dict[str, Any]],
    all_rows: list[dict[str, Any]],
    group_by_episode: dict[str, int],
    group: int,
) -> dict[str, Any]:
    ordered_wall = sorted(
        group_rows, key=lambda row: (row["created_ts_ns"], row["episode_id"])
    )
    baseline = ordered_wall[0]
    discordant, tau = discordant_pairs(group_rows)
    wall_labels = [
        group_by_episode[row["episode_id"]]
        for row in sorted(
            all_rows, key=lambda row: (row["created_ts_ns"], row["episode_id"])
        )
    ]
    episode_labels = [
        group_by_episode[row["episode_id"]]
        for row in sorted(all_rows, key=lambda row: row["episode_id"])
    ]
    return {
        "group_1h": group + 1,
        "episode_count": len(group_rows),
        "offset_min_ns": min(row["offset_ns"] for row in group_rows),
        "offset_max_ns": max(row["offset_ns"] for row in group_rows),
        "offset_span_ns": (
            max(row["offset_ns"] for row in group_rows)
            - min(row["offset_ns"] for row in group_rows)
        ),
        "created_ts_min_ns": min(row["created_ts_ns"] for row in group_rows),
        "created_ts_max_ns": max(row["created_ts_ns"] for row in group_rows),
        "monotonic_ts_min_ns": min(
            row["first_timestamp_ns"] for row in group_rows
        ),
        "monotonic_ts_max_ns": max(
            row["first_timestamp_ns"] for row in group_rows
        ),
        "utc_date_counts": dict(sorted(Counter(row["utc_date"] for row in group_rows).items())),
        "policy_counts": dict(
            sorted(Counter(row["policy_model"] for row in group_rows).items())
        ),
        "wall_monotonic_discordant_pairs": discordant,
        "wall_monotonic_kendall_tau_a": tau,
        "maximum_elapsed_time_discrepancy_ns": max(
            abs(
                (row["created_ts_ns"] - baseline["created_ts_ns"])
                - (
                    row["first_timestamp_ns"]
                    - baseline["first_timestamp_ns"]
                )
            )
            for row in group_rows
        ),
        "contiguous_in_wall_clock_order": positions_contiguous(wall_labels, group),
        "contiguous_in_episode_id_order": positions_contiguous(
            episode_labels, group
        ),
    }


def classify(gaps: list[int], memberships: dict[int, list[int]]) -> str:
    if not gaps:
        return "no_clock_offset_structure_at_fixed_resolution"
    largest = max(gaps)
    second = sorted(gaps)[-2] if len(gaps) >= 2 else 0
    stable = all(
        memberships[threshold] == memberships[1_000_000_000]
        for threshold in (
            1_000_000_000,
            10_000_000_000,
            60_000_000_000,
            600_000_000_000,
            3_600_000_000_000,
            21_600_000_000_000,
        )
    )
    if (
        largest >= 86_400_000_000_000
        and second > 0
        and largest / second >= 1_000
        and stable
    ):
        return "scale_separated_clock_offset_regimes"
    if largest > 1_000_000_000:
        return "clock_offset_structure_without_scale_separation"
    return "no_clock_offset_structure_at_fixed_resolution"


def build(repository: Path) -> tuple[dict[str, Any], bytes]:
    controls = synthetic_controls()
    require(all(controls.values()), "synthetic controls")
    source = source_trace(repository)
    rows = load_rows()
    sorted_rows = sorted(
        rows, key=lambda row: (row["offset_ns"], row["episode_id"])
    )
    gaps = [
        current["offset_ns"] - previous["offset_ns"]
        for previous, current in zip(sorted_rows, sorted_rows[1:])
    ]
    memberships: dict[int, list[int]] = {}
    threshold_surface = {}
    for seconds in THRESHOLDS_SECONDS:
        threshold_ns = int(seconds * 1_000_000_000)
        labels = labels_for_threshold(sorted_rows, threshold_ns)
        memberships[threshold_ns] = labels
        sizes = group_sizes(labels)
        threshold_surface[threshold_key(seconds)] = {
            "threshold_ns": threshold_ns,
            "group_count": len(sizes),
            "sorted_group_sizes": sizes,
        }
    labels = memberships[CANONICAL_THRESHOLD_NS]
    projected, projection_bytes = build_projection(sorted_rows, labels)
    group_by_episode = {
        row["episode_id"]: label for row, label in zip(sorted_rows, labels)
    }
    groups = [
        summarize_group(
            [row for row in rows if group_by_episode[row["episode_id"]] == group],
            rows,
            group_by_episode,
            group,
        )
        for group in sorted(set(labels))
    ]
    ordered_gaps = sorted(gaps, reverse=True)
    result = {
        "schema": "h206-phail-monotonic-wall-clock-bridge-v1",
        "status": "result_exposed_exploratory",
        "protocol_sha256": sha256(PROTOCOL),
        "exposure_record_sha256": sha256(EXPOSURE),
        "cohort_sha256": sha256(COHORT),
        "h202_projection_sha256": sha256(H202_PROJECTION),
        "h202_result_sha256": sha256(H202_RESULT),
        "source_trace": source,
        "synthetic_controls": controls,
        "episode_count": len(rows),
        "monotonic_timestamp": {
            "unique_count": len({row["first_timestamp_ns"] for row in rows}),
            "minimum_ns": min(row["first_timestamp_ns"] for row in rows),
            "maximum_ns": max(row["first_timestamp_ns"] for row in rows),
            "span_ns": (
                max(row["first_timestamp_ns"] for row in rows)
                - min(row["first_timestamp_ns"] for row in rows)
            ),
        },
        "clock_offset": {
            "minimum_ns": min(row["offset_ns"] for row in rows),
            "maximum_ns": max(row["offset_ns"] for row in rows),
            "span_ns": (
                max(row["offset_ns"] for row in rows)
                - min(row["offset_ns"] for row in rows)
            ),
            "largest_adjacent_gap_ns": ordered_gaps[0],
            "second_largest_adjacent_gap_ns": ordered_gaps[1],
            "largest_to_second_gap_ratio": ordered_gaps[0] / ordered_gaps[1],
        },
        "threshold_sensitivity": threshold_surface,
        "one_hour_groups": groups,
        "projection_sha256": sha256_bytes(projection_bytes),
        "projection_rows": len(projected),
        "classification": classify(gaps, memberships),
        "performance_or_later_state_opened": False,
        "host_or_session_identity_established": False,
        "dependence_cluster_established": False,
        "confirmatory_claim_authorized": False,
    }
    return result, projection_bytes


def validate(result: dict[str, Any]) -> None:
    require(result["schema"] == "h206-phail-monotonic-wall-clock-bridge-v1", "schema")
    require(result["status"] == "result_exposed_exploratory", "status")
    require(result["protocol_sha256"] == sha256(PROTOCOL), "protocol")
    require(result["exposure_record_sha256"] == sha256(EXPOSURE), "exposure")
    require(result["cohort_sha256"] == COHORT_SHA256, "cohort")
    require(result["h202_projection_sha256"] == H202_PROJECTION_SHA256, "H202 projection")
    require(result["h202_result_sha256"] == H202_RESULT_SHA256, "H202 result")
    require(result["episode_count"] == EXPECTED_EPISODES, "episodes")
    require(result["projection_rows"] == EXPECTED_EPISODES, "projection rows")
    require(all(result["synthetic_controls"].values()), "controls")
    require(result["source_trace"]["semantic_trace_complete"] is True, "source trace")
    require(result["classification"] in CLASSIFICATIONS, "classification value")
    for key in (
        "performance_or_later_state_opened",
        "host_or_session_identity_established",
        "dependence_cluster_established",
        "confirmatory_claim_authorized",
    ):
        require(result[key] is False, key)


def staged_validation(repository: Path) -> dict[str, Any]:
    controls = synthetic_controls()
    require(all(controls.values()), "synthetic controls")
    source = source_trace(repository)
    rows = load_rows()
    return {
        "controls": controls,
        "source_controls": source["controls"],
        "episode_count": len(rows),
        "joined_unique_count": len({row["episode_id"] for row in rows}),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, default=DEFAULT_REPOSITORY)
    parser.add_argument("--stage", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    require(not (args.stage and args.check), "choose one mode")
    repository = args.repository.resolve()
    if args.stage:
        print(json.dumps(staged_validation(repository), indent=2, sort_keys=True))
        return
    candidate, projection_bytes = build(repository)
    validate(candidate)
    if args.check:
        require(PROJECTION.read_bytes() == projection_bytes, "projection exact rebuild")
        require(candidate == json.loads(OUTPUT.read_text()), "result exact rebuild")
        print("OK: H206 monotonic/wall-clock bridge reproduces")
        return
    PROJECTION.write_bytes(projection_bytes)
    OUTPUT.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n")
    print(json.dumps(candidate, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
