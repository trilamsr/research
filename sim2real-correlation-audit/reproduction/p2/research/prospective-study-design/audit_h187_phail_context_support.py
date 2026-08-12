#!/usr/bin/env python3
"""Outcome-blind PhAIL v1.0 release-cohort context-support audit."""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import io
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h187-phail-context-support-audit.md"
OUTPUT = FAMILY / "result-h187-phail-context-support.json"
SANITIZED = FAMILY / "result-h187-phail-context-support-sanitized.csv"
ENDPOINT = "https://storage.eu-north1.nebius.cloud/positronic-public"
PREFIX = "phail/v1.0/dataset/"
ROLLOUT_PREFIX = PREFIX + "rollouts/"
EXPECTED_EPISODES = 594
POLICIES = ("act", "groot", "openpi", "smolvla")
ALLOWED_FIELDS = (
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


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def get_bytes(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "auspex-h187-outcome-blind-metadata/1.0"},
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def list_inventory() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    token = ""
    while True:
        query = {"list-type": "2", "prefix": PREFIX, "max-keys": "1000"}
        if token:
            query["continuation-token"] = token
        raw = get_bytes(ENDPOINT + "?" + urllib.parse.urlencode(query))
        root = ET.fromstring(raw)
        ns = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
        for node in root.findall("s3:Contents", ns):
            rows.append(
                {
                    "key": node.findtext("s3:Key", default="", namespaces=ns),
                    "size": int(
                        node.findtext("s3:Size", default="-1", namespaces=ns)
                    ),
                    "etag": node.findtext(
                        "s3:ETag", default="", namespaces=ns
                    ).strip('"'),
                    "last_modified": node.findtext(
                        "s3:LastModified", default="", namespaces=ns
                    ),
                }
            )
        truncated = (
            root.findtext("s3:IsTruncated", default="false", namespaces=ns)
            == "true"
        )
        if not truncated:
            break
        token = root.findtext(
            "s3:NextContinuationToken", default="", namespaces=ns
        )
        if not token:
            raise ValueError("truncated inventory page without continuation token")
    if len({row["key"] for row in rows}) != len(rows):
        raise ValueError("duplicate inventory key")
    return rows


def sanitize_episode(
    episode_id: str,
    _storage_partition: str,
    meta_key: str,
    static_key: str,
    fetch=get_bytes,
) -> dict[str, Any]:
    meta_raw, static_raw = (
        fetch(f"{ENDPOINT}/{meta_key}"),
        fetch(f"{ENDPOINT}/{static_key}"),
    )
    meta = json.loads(meta_raw)
    static = json.loads(static_raw)
    created = meta.get("created_ts_ns")
    utc_date = ""
    if isinstance(created, int):
        utc_date = datetime.fromtimestamp(
            created / 1_000_000_000, tz=timezone.utc
        ).date().isoformat()
    row = {
        "episode_id": episode_id,
        "policy_model": static.get("model"),
        "checkpoint_variant": static.get("variant"),
        "task": static.get("task"),
        # PhAIL static sidecars use literal dotted top-level keys; these are
        # not nested JSON objects.
        "object": static.get("eval.object"),
        "tote_placement": static.get("eval.tote_placement"),
        "external_camera": static.get("eval.external_camera"),
        "created_ts_ns": created,
        "utc_date": utc_date,
        # The parent directory is a constant storage partition, not a
        # source-recorded experimental session.
        "session_id": None,
        "meta_source_path": meta_key,
        "meta_sha256": sha256_bytes(meta_raw),
        "static_source_path": static_key,
        "static_sha256": sha256_bytes(static_raw),
    }
    if tuple(row) != ALLOWED_FIELDS:
        raise AssertionError("sanitized schema drift")
    return row


def episode_pairs(inventory: list[dict[str, Any]]) -> list[tuple[str, str, str, str]]:
    keys = {str(row["key"]) for row in inventory}
    pairs = []
    for key in sorted(keys):
        if not key.startswith(ROLLOUT_PREFIX) or not key.endswith("/static.json"):
            continue
        parts = key.removeprefix(ROLLOUT_PREFIX).split("/")
        if len(parts) != 3:
            raise ValueError(f"unexpected rollout path: {key}")
        session_id, episode_id, _ = parts
        meta_key = key.removesuffix("static.json") + "meta.json"
        if meta_key not in keys:
            raise ValueError(f"missing paired metadata: {meta_key}")
        pairs.append((episode_id, session_id, meta_key, key))
    if len(pairs) != EXPECTED_EPISODES:
        raise ValueError(f"expected {EXPECTED_EPISODES} episodes, got {len(pairs)}")
    if len({row[0] for row in pairs}) != len(pairs):
        raise ValueError("duplicate episode identity")
    return pairs


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    policy_counts = Counter(str(row["policy_model"]) for row in rows)
    task_counts = Counter(str(row["task"]) for row in rows)
    complete = [
        row
        for row in rows
        if all(
            row[field] not in (None, "")
            for field in ("task", "object", "tote_placement", "external_camera")
        )
    ]
    cells: dict[tuple[str, str, str, str], Counter[str]] = defaultdict(Counter)
    for row in complete:
        cell = (
            str(row["task"]),
            str(row["object"]),
            str(row["tote_placement"]),
            str(row["external_camera"]),
        )
        cells[cell][str(row["policy_model"])] += 1
    cell_rows = []
    for cell, counts in sorted(cells.items()):
        values = [counts.get(policy, 0) for policy in POLICIES]
        total = sum(values)
        shares = [value / total for value in values] if total else [0.0] * 4
        cell_rows.append(
            {
                "task": cell[0],
                "object": cell[1],
                "tote_placement": cell[2],
                "external_camera": cell[3],
                "policy_counts": {p: counts.get(p, 0) for p in POLICIES},
                "minimum_policy_count": min(values),
                "maximum_absolute_share_deviation_from_quarter": max(
                    abs(value - 0.25) for value in shares
                ),
            }
        )
    ordered = sorted(rows, key=lambda row: (int(row["created_ts_ns"]), row["episode_id"]))
    adjacent_repeats = sum(
        left["policy_model"] == right["policy_model"]
        for left, right in zip(ordered, ordered[1:])
    )
    longest_run = 0
    current_run = 0
    previous = object()
    for row in ordered:
        current = row["policy_model"]
        current_run = current_run + 1 if current == previous else 1
        longest_run = max(longest_run, current_run)
        previous = current
    date_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        date_counts[str(row["utc_date"])][str(row["policy_model"])] += 1
    complete_dates = [
        date
        for date, counts in date_counts.items()
        if all(counts.get(policy, 0) > 0 for policy in POLICIES)
    ]
    missing_by_field = {
        field: sum(row[field] in (None, "") for row in rows)
        for field in ("task", "object", "tote_placement", "external_camera")
    }
    full_release_gate_pass = (
        len(complete) == len(rows)
        and bool(cell_rows)
        and all(row["minimum_policy_count"] > 0 for row in cell_rows)
        and len(complete_dates) == len(date_counts)
    )
    date_contexts: dict[
        tuple[str, str, str, str, str], Counter[str]
    ] = defaultdict(Counter)
    for row in complete:
        key = (
            str(row["utc_date"]),
            str(row["task"]),
            str(row["object"]),
            str(row["tote_placement"]),
            str(row["external_camera"]),
        )
        date_contexts[key][str(row["policy_model"])] += 1
    date_context_rows = []
    retained_target_cells = []
    for key, counts in sorted(date_contexts.items()):
        values = [counts.get(policy, 0) for policy in POLICIES]
        cell = {
            "utc_date": key[0],
            "task": key[1],
            "object": key[2],
            "tote_placement": key[3],
            "external_camera": key[4],
            "policy_counts": {p: counts.get(p, 0) for p in POLICIES},
            "minimum_policy_count": min(values),
        }
        date_context_rows.append(cell)
        if min(values) > 0:
            retained_target_cells.append(cell)
    narrow_target_defined = bool(retained_target_cells)
    target_policy_counts = {
        policy: sum(
            int(cell["policy_counts"][policy]) for cell in retained_target_cells
        )
        for policy in POLICIES
    }
    target_episode_count = sum(target_policy_counts.values())
    adverse_reasons = []
    if len(complete) != len(rows):
        adverse_reasons.append("missing_declared_context_metadata")
    if cell_rows and any(row["minimum_policy_count"] == 0 for row in cell_rows):
        adverse_reasons.append("full_window_context_cell_missing_policy")
    if len(complete_dates) != len(date_counts):
        adverse_reasons.append("calendar_dates_missing_policy")
    if not narrow_target_defined:
        adverse_reasons.append("no_common_date_context_cell")
    return {
        "episode_count": len(rows),
        "policy_counts": dict(sorted(policy_counts.items())),
        "task_counts": dict(sorted(task_counts.items())),
        "context_missing_counts": missing_by_field,
        "complete_context_episode_count": len(complete),
        "complete_context_cell_count": len(cell_rows),
        "context_cells": cell_rows,
        "chronology": {
            "ordering": "created_ts_ns",
            "immediate_policy_repeats": adjacent_repeats,
            "longest_policy_run": longest_run,
            "first_created_ts_ns": ordered[0]["created_ts_ns"],
            "last_created_ts_ns": ordered[-1]["created_ts_ns"],
        },
        "utc_date_policy_counts": {
            date: {policy: counts.get(policy, 0) for policy in POLICIES}
            for date, counts in sorted(date_counts.items())
        },
        "utc_dates_with_all_policies": sorted(complete_dates),
        "date_context_cell_count": len(date_context_rows),
        "date_context_cells": date_context_rows,
        "full_release_metadata_gate_pass": full_release_gate_pass,
        "adverse_reasons": adverse_reasons,
        "narrow_target": {
            "identified": narrow_target_defined,
            "rule": (
                "retain every UTC-date × task × object × tote × camera cell "
                "with positive exposure for all four policies; weight "
                "retained cells equally"
            ),
            "retained_cell_count": len(retained_target_cells),
            "retained_episode_count": target_episode_count,
            "excluded_episode_count": len(rows) - target_episode_count,
            "policy_counts": target_policy_counts,
            "equal_cell_weight": (
                1 / len(retained_target_cells) if retained_target_cells else None
            ),
            "cells": retained_target_cells,
        },
        "chronology_gate": {
            "status": "unresolved",
            "basis": (
                "no source-recorded session identity; candidate availability "
                "is visibly batched over dates and chronology counts alone "
                "cannot exclude carryover or undocumented exclusions"
            ),
        },
        "metadata_gate_pass": False,
        "conditional_outcome_phase_authorized": False,
        "disposition": (
            "full_release_common_support_identified_chronology_unresolved"
            if full_release_gate_pass
            else "narrow_common_support_target_identified_chronology_unresolved"
            if narrow_target_defined
            else "adverse_no_common_support_target"
        ),
    }


def build(workers: int = 12) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    inventory = list_inventory()
    pairs = episode_pairs(inventory)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        rows = list(
            pool.map(lambda args: sanitize_episode(*args), pairs)
        )
    rows.sort(key=lambda row: row["episode_id"])
    manifest_text = "".join(
        f"{row['key']}\t{row['size']}\t{row['etag']}\t{row['last_modified']}\n"
        for row in sorted(inventory, key=lambda item: str(item["key"]))
    )
    sanitized_bytes = render_sanitized(rows)
    result = {
        "schema": "h187-phail-context-support-v1",
        "protocol_sha256": sha256(PROTOCOL),
        "source": {
            "endpoint": ENDPOINT,
            "prefix": PREFIX,
            "rollout_prefix": ROLLOUT_PREFIX,
            "cohort": "official v1.0 release-page cohort",
            "inventory_object_count": len(inventory),
            "inventory_total_bytes": sum(int(row["size"]) for row in inventory),
            "inventory_manifest_sha256": sha256_bytes(manifest_text.encode()),
            "retained_sidecar_count": 2 * len(rows),
            "retained_sidecar_content_hashes": "in sanitized CSV",
            "sanitized_csv_sha256": sha256_bytes(sanitized_bytes),
        },
        "outcome_field_policy": {
            "allowed_output_fields": list(ALLOWED_FIELDS),
            "performance_fields_emitted": [],
            "raw_sidecars_persisted": False,
        },
        "audit": summarize(rows),
    }
    validate(result, rows)
    return result, rows


def validate(result: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    if result.get("schema") != "h187-phail-context-support-v1":
        raise ValueError("schema mismatch")
    if result.get("protocol_sha256") != sha256(PROTOCOL):
        raise ValueError("protocol hash mismatch")
    if len(rows) != EXPECTED_EPISODES:
        raise ValueError("episode count mismatch")
    if any(tuple(row) != ALLOWED_FIELDS for row in rows):
        raise ValueError("prohibited or missing sanitized field")
    if {row["policy_model"] for row in rows} != set(POLICIES):
        raise ValueError("unexpected policy roster")
    if result["source"].get("sanitized_csv_sha256") != sha256_bytes(
        render_sanitized(rows)
    ):
        raise ValueError("sanitized CSV binding mismatch")
    if result.get("audit") != summarize(rows):
        raise ValueError("audit does not recompute from sanitized rows")
    if result["outcome_field_policy"]["performance_fields_emitted"]:
        raise ValueError("performance field emitted")


def render_sanitized(rows: list[dict[str, Any]]) -> bytes:
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=ALLOWED_FIELDS)
    writer.writeheader()
    writer.writerows(rows)
    return handle.getvalue().encode("utf-8")


def load_sanitized() -> list[dict[str, Any]]:
    with SANITIZED.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        value = row["created_ts_ns"]
        row["created_ts_ns"] = int(value) if value else None
        for field in ALLOWED_FIELDS:
            if row[field] == "":
                row[field] = None
    return rows


def write_outputs(result: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    SANITIZED.write_bytes(render_sanitized(rows))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--workers", type=int, default=12)
    args = parser.parse_args()
    if args.check:
        data = json.loads(OUTPUT.read_text())
        validate(data, load_sanitized())
        return
    result, rows = build(workers=args.workers)
    write_outputs(result, rows)


if __name__ == "__main__":
    main()
