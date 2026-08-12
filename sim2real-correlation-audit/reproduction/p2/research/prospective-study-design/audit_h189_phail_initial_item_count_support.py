#!/usr/bin/env python3
"""Outcome-free PhAIL initial-item-count support audit."""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

import audit_h187_phail_context_support as h187


FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h189-phail-initial-item-count-support.md"
OUTPUT = FAMILY / "result-h189-phail-initial-item-count-support.json"
SANITIZED = FAMILY / "result-h189-phail-initial-item-count-support-sanitized.csv"
H187_RESULT = FAMILY / "result-h187-phail-context-support.json"
H187_SANITIZED = FAMILY / "result-h187-phail-context-support-sanitized.csv"
EXPECTED_H187_INVENTORY = (
    "8b69b6ad8c14b1f5d920dc7aa8c833c79536a8f3405205e9eb5d4f63e5353982"
)
EXPECTED_H187_SANITIZED = (
    "ad43fca1da065a1cb7fd84dfa9afc5691c72ebe12e7f165c68a0050e51e87ebe"
)
ALLOWED_FIELDS = h187.ALLOWED_FIELDS + ("initial_item_count",)
POLICIES = h187.POLICIES


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def inventory_manifest_sha256(inventory: list[dict[str, Any]]) -> str:
    content = "".join(
        f"{row['key']}\t{row['size']}\t{row['etag']}\t{row['last_modified']}\n"
        for row in sorted(inventory, key=lambda item: str(item["key"]))
    )
    return sha256_bytes(content.encode())


def parse_item_count(value: Any) -> int:
    require(not isinstance(value, bool), "Boolean item count")
    if isinstance(value, int):
        result = value
    elif isinstance(value, float) and value.is_integer():
        result = int(value)
    else:
        raise ValueError("item count is missing or nonintegral")
    require(result > 0, "item count must be positive")
    return result


def sanitize_episode(
    episode_id: str,
    _storage_partition: str,
    meta_key: str,
    static_key: str,
    fetch=h187.get_bytes,
) -> dict[str, Any]:
    meta_raw = fetch(f"{h187.ENDPOINT}/{meta_key}")
    static_raw = fetch(f"{h187.ENDPOINT}/{static_key}")
    meta = json.loads(meta_raw)
    static = json.loads(static_raw)
    created = meta.get("created_ts_ns")
    require(isinstance(created, int) and not isinstance(created, bool), "bad timestamp")
    row = {
        "episode_id": episode_id,
        "policy_model": static.get("model"),
        "checkpoint_variant": static.get("variant"),
        "task": static.get("task"),
        "object": static.get("eval.object"),
        "tote_placement": static.get("eval.tote_placement"),
        "external_camera": static.get("eval.external_camera"),
        "created_ts_ns": created,
        "utc_date": datetime.fromtimestamp(
            created / 1_000_000_000, tz=timezone.utc
        ).date().isoformat(),
        "session_id": None,
        "meta_source_path": meta_key,
        "meta_sha256": sha256_bytes(meta_raw),
        "static_source_path": static_key,
        "static_sha256": sha256_bytes(static_raw),
        "initial_item_count": parse_item_count(static.get("eval.total_items")),
    }
    require(tuple(row) == ALLOWED_FIELDS, "sanitized schema drift")
    return row


def render_sanitized(rows: list[dict[str, Any]]) -> bytes:
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=ALLOWED_FIELDS)
    writer.writeheader()
    writer.writerows(rows)
    return handle.getvalue().encode()


def load_sanitized() -> list[dict[str, Any]]:
    with SANITIZED.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        for field in ("created_ts_ns", "initial_item_count"):
            row[field] = int(row[field])
        if row["session_id"] == "":
            row["session_id"] = None
    return rows


def assert_exact_h187_projection(rows: list[dict[str, Any]]) -> None:
    h187_rows = h187.load_sanitized()
    projected = [
        {field: row[field] for field in h187.ALLOWED_FIELDS}
        for row in rows
    ]
    require(
        projected == h187_rows,
        "H189 rows do not project exactly to the fixed H187 manifest",
    )


def cell_summary(
    rows: list[dict[str, Any]], fields: tuple[str, ...]
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, ...], Counter[str]] = defaultdict(Counter)
    for row in rows:
        key = tuple(str(row[field]) for field in fields)
        grouped[key][str(row["policy_model"])] += 1
    result = []
    for key, counts in sorted(grouped.items()):
        policy_counts = {policy: counts.get(policy, 0) for policy in POLICIES}
        result.append(
            {
                **dict(zip(fields, key)),
                "policy_counts": policy_counts,
                "minimum_policy_count": min(policy_counts.values()),
            }
        )
    return result


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    require(len(rows) == h187.EXPECTED_EPISODES, "episode count changed")
    require(len({row["episode_id"] for row in rows}) == len(rows), "duplicate episode")
    require({row["policy_model"] for row in rows} == set(POLICIES), "policy roster")
    item_counts = Counter(int(row["initial_item_count"]) for row in rows)
    by_policy: dict[str, Counter[int]] = {
        policy: Counter(
            int(row["initial_item_count"])
            for row in rows
            if row["policy_model"] == policy
        )
        for policy in POLICIES
    }
    full_fields = (
        "task",
        "object",
        "tote_placement",
        "external_camera",
        "initial_item_count",
    )
    dated_fields = ("utc_date",) + full_fields
    h187_dated_fields = (
        "utc_date",
        "task",
        "object",
        "tote_placement",
        "external_camera",
    )
    full_cells = cell_summary(rows, full_fields)
    dated_cells = cell_summary(rows, dated_fields)
    h187_item_sets: dict[tuple[str, ...], set[int]] = defaultdict(set)
    for row in rows:
        key = tuple(str(row[field]) for field in h187_dated_fields)
        h187_item_sets[key].add(int(row["initial_item_count"]))
    multi_item_h187_cells = sorted(
        [
            {
                **dict(zip(h187_dated_fields, key)),
                "initial_item_counts": sorted(values),
            }
            for key, values in h187_item_sets.items()
            if len(values) > 1
        ],
        key=lambda row: tuple(str(row[field]) for field in h187_dated_fields),
    )
    target_cells = [cell for cell in dated_cells if cell["minimum_policy_count"] > 0]
    target_policy_counts = {
        policy: sum(cell["policy_counts"][policy] for cell in target_cells)
        for policy in POLICIES
    }
    target_episodes = sum(target_policy_counts.values())
    h187_result = json.loads(H187_RESULT.read_text())
    h187_target = h187_result["audit"]["narrow_target"]
    return {
        "episode_count": len(rows),
        "item_count_distribution": {
            str(key): value for key, value in sorted(item_counts.items())
        },
        "item_count_by_policy": {
            policy: {
                str(key): value for key, value in sorted(counts.items())
            }
            for policy, counts in by_policy.items()
        },
        "four_item_share_by_policy": {
            policy: {
                "numerator": by_policy[policy].get(4, 0),
                "denominator": sum(by_policy[policy].values()),
            }
            for policy in POLICIES
        },
        "full_window_cell_count": len(full_cells),
        "full_window_supported_cell_count": sum(
            cell["minimum_policy_count"] > 0 for cell in full_cells
        ),
        "full_window_cells": full_cells,
        "dated_cell_count": len(dated_cells),
        "dated_supported_cell_count": len(target_cells),
        "dated_cells": dated_cells,
        "h187_dated_cells_with_multiple_item_counts": multi_item_h187_cells,
        "initial_item_count_deterministic_within_h187_dated_cell": not bool(
            multi_item_h187_cells
        ),
        "h189_target": {
            "identified": bool(target_cells),
            "rule": (
                "retain every UTC-date × task × object × tote × camera × "
                "initial-item-count cell with all four policies; equal cell weights"
            ),
            "retained_cell_count": len(target_cells),
            "equal_cell_weight": (
                {"numerator": 1, "denominator": len(target_cells)}
                if target_cells
                else None
            ),
            "retained_episode_count": target_episodes,
            "excluded_episode_count": len(rows) - target_episodes,
            "policy_counts": target_policy_counts,
            "cells": target_cells,
        },
        "comparison_to_h187": {
            "h187_retained_cell_count": h187_target["retained_cell_count"],
            "h187_retained_episode_count": h187_target["retained_episode_count"],
            "cell_count_change": len(target_cells)
            - h187_target["retained_cell_count"],
            "episode_count_change": target_episodes
            - h187_target["retained_episode_count"],
            "retained_episode_fraction_of_h187": (
                {
                    "numerator": Fraction(
                        target_episodes, h187_target["retained_episode_count"]
                    ).numerator,
                    "denominator": Fraction(
                        target_episodes, h187_target["retained_episode_count"]
                    ).denominator,
                }
                if h187_target["retained_episode_count"]
                else None
            ),
        },
        "full_release_support_pass": (
            bool(full_cells)
            and all(cell["minimum_policy_count"] > 0 for cell in full_cells)
            and bool(dated_cells)
            and all(cell["minimum_policy_count"] > 0 for cell in dated_cells)
        ),
        "chronology_gate_status": "unresolved_inherited_from_h187",
        "metadata_gate_pass": False,
        "conditional_outcome_phase_authorized": False,
        "disposition": (
            "item_count_preserves_h187_target"
            if len(target_cells) == h187_target["retained_cell_count"]
            and target_episodes == h187_target["retained_episode_count"]
            else "item_count_narrows_h187_target"
            if target_cells
            else "item_count_eliminates_common_support_target"
        ),
    }


def validate(result: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    require(result.get("schema") == "h189-phail-item-count-support-v1", "schema")
    require(result.get("protocol_sha256") == sha256(PROTOCOL), "protocol hash")
    require(
        result["source"].get("fresh_inventory_manifest_sha256")
        == EXPECTED_H187_INVENTORY,
        "fresh inventory binding",
    )
    require(tuple(rows[0]) == ALLOWED_FIELDS, "row schema")
    require(all(tuple(row) == ALLOWED_FIELDS for row in rows), "row schema drift")
    assert_exact_h187_projection(rows)
    require(
        result["source"]["sanitized_csv_sha256"]
        == sha256_bytes(render_sanitized(rows)),
        "CSV hash",
    )
    require(result["audit"] == summarize(rows), "audit recomputation")
    require(result["audit"]["metadata_gate_pass"] is False, "overbroad gate")
    require(
        result["audit"]["conditional_outcome_phase_authorized"] is False,
        "outcome authorization",
    )


def assemble_result(
    rows: list[dict[str, Any]], fresh_inventory_hash: str
) -> dict[str, Any]:
    result = {
        "schema": "h189-phail-item-count-support-v1",
        "protocol_sha256": sha256(PROTOCOL),
        "source": {
            "endpoint": h187.ENDPOINT,
            "prefix": h187.PREFIX,
            "cohort": "official v1.0 594-rollout release cohort",
            "h187_inventory_manifest_sha256": EXPECTED_H187_INVENTORY,
            "fresh_inventory_manifest_sha256": fresh_inventory_hash,
            "h187_sanitized_csv_sha256": EXPECTED_H187_SANITIZED,
            "sanitized_csv_sha256": sha256_bytes(render_sanitized(rows)),
            "retained_sidecar_count": 2 * len(rows),
            "raw_sidecars_persisted": False,
        },
        "field_policy": {
            "new_allowed_source_field": "eval.total_items",
            "interpretation": "pre-assignment initial item count",
            "performance_fields_emitted": [],
        },
        "audit": summarize(rows),
    }
    validate(result, rows)
    return result


def fresh_inventory() -> tuple[list[dict[str, Any]], str]:
    inventory = h187.list_inventory()
    fresh_inventory_hash = inventory_manifest_sha256(inventory)
    require(
        fresh_inventory_hash == EXPECTED_H187_INVENTORY,
        "fresh public inventory drifted from H187",
    )
    return inventory, fresh_inventory_hash


def validate_fixed_h187_inputs() -> None:
    h187_result = json.loads(H187_RESULT.read_text())
    require(
        h187_result["source"]["inventory_manifest_sha256"]
        == EXPECTED_H187_INVENTORY,
        "H187 inventory binding",
    )
    require(sha256(H187_SANITIZED) == EXPECTED_H187_SANITIZED, "H187 CSV binding")


def build(workers: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    validate_fixed_h187_inputs()
    inventory, fresh_inventory_hash = fresh_inventory()
    pairs = h187.episode_pairs(inventory)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(lambda args: sanitize_episode(*args), pairs))
    rows.sort(key=lambda row: row["episode_id"])
    assert_exact_h187_projection(rows)
    return assemble_result(rows, fresh_inventory_hash), rows


def refresh_from_sanitized() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    validate_fixed_h187_inputs()
    _, fresh_inventory_hash = fresh_inventory()
    rows = load_sanitized()
    assert_exact_h187_projection(rows)
    return assemble_result(rows, fresh_inventory_hash), rows


def write_outputs(result: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    SANITIZED.write_bytes(render_sanitized(rows))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--refresh-from-sanitized", action="store_true")
    parser.add_argument("--workers", type=int, default=24)
    args = parser.parse_args()
    require(
        not (args.check and args.refresh_from_sanitized),
        "choose at most one execution mode",
    )
    if args.check:
        validate(json.loads(OUTPUT.read_text()), load_sanitized())
        return
    if args.refresh_from_sanitized:
        result, rows = refresh_from_sanitized()
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        return
    result, rows = build(args.workers)
    write_outputs(result, rows)


if __name__ == "__main__":
    main()
