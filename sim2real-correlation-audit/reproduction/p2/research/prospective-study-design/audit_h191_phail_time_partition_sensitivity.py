#!/usr/bin/env python3
"""Outcome-free sensitivity surface for H187 time partitions."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h191-phail-time-partition-sensitivity.md"
INPUT = FAMILY / "result-h187-phail-context-support-sanitized.csv"
OUTPUT = FAMILY / "result-h191-phail-time-partition-sensitivity.json"
EXPECTED_INPUT_SHA256 = (
    "ad43fca1da065a1cb7fd84dfa9afc5691c72ebe12e7f165c68a0050e51e87ebe"
)
POLICIES = ("act", "groot", "openpi", "smolvla")
CONTEXT_FIELDS = ("task", "object", "tote_placement", "external_camera")
ALLOWED_INPUT_FIELDS = (
    "episode_id",
    "policy_model",
    "checkpoint_variant",
    "task",
    "object",
    "tote_placement",
    "external_camera",
    "created_ts_ns",
    "utc_date",
    "session_id",
    "meta_source_path",
    "meta_sha256",
    "static_source_path",
    "static_sha256",
)
WIDTHS_HOURS = (12, 24, 48, 72, 96, 120, 144, 168)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_rows() -> list[dict[str, str]]:
    require(sha256(INPUT) == EXPECTED_INPUT_SHA256, "H187 input hash drift")
    with INPUT.open(newline="") as handle:
        reader = csv.DictReader(handle)
        require(tuple(reader.fieldnames or ()) == ALLOWED_INPUT_FIELDS, "input schema")
        rows = list(reader)
    require(len(rows) == 594, "episode count")
    require({row["policy_model"] for row in rows} == set(POLICIES), "policy roster")
    require(
        all(row[field] for row in rows for field in (*CONTEXT_FIELDS, "created_ts_ns")),
        "missing required field",
    )
    return rows


def summarize(
    rows: list[dict[str, str]], width_hours: int | None, phase_hours: int = 0
) -> dict[str, Any]:
    cells: dict[tuple[Any, ...], Counter[str]] = defaultdict(Counter)
    members: dict[tuple[Any, ...], int] = defaultdict(int)
    width_ns = width_hours * 3_600_000_000_000 if width_hours else None
    phase_ns = phase_hours * 3_600_000_000_000
    for row in rows:
        base = tuple(row[field] for field in CONTEXT_FIELDS)
        time_key: tuple[Any, ...] = ()
        if width_ns is not None:
            time_key = ((int(row["created_ts_ns"]) + phase_ns) // width_ns,)
        key = time_key + base
        cells[key][row["policy_model"]] += 1
        members[key] += 1
    supported = []
    for key, counts in cells.items():
        minimum = min(counts.get(policy, 0) for policy in POLICIES)
        if minimum > 0:
            supported.append((key, counts, members[key], minimum))
    policy_counts = {
        policy: sum(counts.get(policy, 0) for _, counts, _, _ in supported)
        for policy in POLICIES
    }
    retained = sum(size for _, _, size, _ in supported)
    minimum_distribution = Counter(minimum for _, _, _, minimum in supported)
    return {
        "width_hours": width_hours,
        "phase_hours": phase_hours if width_hours is not None else None,
        "cell_count": len(cells),
        "supported_cell_count": len(supported),
        "retained_episode_count": retained,
        "excluded_episode_count": len(rows) - retained,
        "policy_counts": policy_counts,
        "minimum_policy_count_distribution": {
            str(key): value for key, value in sorted(minimum_distribution.items())
        },
    }


def build() -> dict[str, Any]:
    rows = load_rows()
    grid = [
        summarize(rows, width, phase)
        for width in WIDTHS_HOURS
        for phase in range(width)
    ]
    width_ranges = []
    for width in WIDTHS_HOURS:
        matches = [row for row in grid if row["width_hours"] == width]
        phase_zero = next(row for row in matches if row["phase_hours"] == 0)
        width_ranges.append(
            {
                "width_hours": width,
                "phase_count": len(matches),
                "phase_zero_supported_cell_count": phase_zero[
                    "supported_cell_count"
                ],
                "phase_zero_retained_episode_count": phase_zero[
                    "retained_episode_count"
                ],
                "supported_cell_count_min": min(
                    row["supported_cell_count"] for row in matches
                ),
                "supported_cell_count_max": max(
                    row["supported_cell_count"] for row in matches
                ),
                "retained_episode_count_min": min(
                    row["retained_episode_count"] for row in matches
                ),
                "retained_episode_count_max": max(
                    row["retained_episode_count"] for row in matches
                ),
            }
        )
    return {
        "schema": "h191-phail-time-partition-sensitivity-v1",
        "protocol_sha256": sha256(PROTOCOL),
        "input_sha256": sha256(INPUT),
        "input_episode_count": len(rows),
        "performance_fields_opened": False,
        "interpretation": (
            "deterministic partition sensitivity only; bins are not "
            "source-recorded sessions and do not authorize outcomes"
        ),
        "full_window": summarize(rows, None),
        "h187_utc_24h_phase_zero": summarize(rows, 24, 0),
        "width_ranges": width_ranges,
        "grid": grid,
    }


def validate(result: dict[str, Any]) -> None:
    require(
        result.get("schema") == "h191-phail-time-partition-sensitivity-v1",
        "schema",
    )
    require(result.get("protocol_sha256") == sha256(PROTOCOL), "protocol hash")
    require(result.get("input_sha256") == EXPECTED_INPUT_SHA256, "input hash")
    require(result.get("input_episode_count") == 594, "episode count")
    require(result.get("performance_fields_opened") is False, "performance seal")
    require(len(result.get("grid", [])) == sum(WIDTHS_HOURS), "grid completeness")
    utc = result["h187_utc_24h_phase_zero"]
    require(utc["cell_count"] == 126, "H187 UTC cell count")
    require(utc["supported_cell_count"] == 18, "H187 supported cells")
    require(utc["retained_episode_count"] == 194, "H187 retained episodes")
    require(
        utc["minimum_policy_count_distribution"] == {"1": 11, "2": 7},
        "H187 support minima",
    )
    require(result == build(), "stored result does not exactly recompute")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        validate(json.loads(OUTPUT.read_text()))
        return
    result = build()
    validate(result)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
