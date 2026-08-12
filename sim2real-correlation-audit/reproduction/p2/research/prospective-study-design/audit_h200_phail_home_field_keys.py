#!/usr/bin/env python3
"""Outcome-free key-only inventory for PhAIL home/randomization fields."""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

import audit_h187_phail_context_support as h187
import audit_h193_phail_lifecycle_keys as h193


FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h200-phail-home-field-key-inventory.md"
H199 = FAMILY / "result-h199-phail-randomized-home-target.json"
H193 = FAMILY / "result-h193-phail-lifecycle-key-inventory.json"
OUTPUT = FAMILY / "result-h200-phail-home-field-key-inventory.json"
PROJECTION = FAMILY / "projection-h200-phail-home-field-keys.csv"
TOKENS = (
    "home",
    "homing",
    "joint",
    "joints",
    "initial",
    "initialize",
    "initialization",
    "start",
    "starting",
    "pose",
    "rng",
    "random",
    "randomized",
    "randomization",
    "variation",
    "perturbation",
    "target",
    "origin",
)
PROHIBITED = (
    "success",
    "successful",
    "outcome",
    "result",
    "reward",
    "score",
    "rank",
    "duration",
    "termination",
    "terminated",
    "completion",
    "completed",
    "safety",
    "hrt",
    "annotation",
    "event",
    "note",
    "media",
    "video",
    "telemetry",
    "item",
    "items",
    "action",
    "actions",
    "command",
    "commands",
    "observation",
    "observations",
)
TOKEN_RE = re.compile(r"[A-Za-z0-9]+")
FIELDS = ("episode_id", "key_path", "category", "node_type")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def key_tokens(key: str) -> tuple[str, ...]:
    return tuple(token.lower() for token in TOKEN_RE.findall(key))


def node_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    if isinstance(value, str):
        return "string"
    if isinstance(value, (int, float)):
        return "number"
    raise ValueError("unsupported JSON node")


def classify_path(parts: tuple[str, ...]) -> str | None:
    tokens = {
        token for part in parts for token in key_tokens(part)
    }
    if tokens & set(PROHIBITED):
        return None
    if tokens & set(TOKENS):
        return "home_field_candidate"
    return None


def project_schema(raw: bytes, sidecar: str) -> list[dict[str, str]]:
    data = json.loads(raw)
    require(isinstance(data, dict), "sidecar root is not an object")
    projected: set[tuple[str, str, str]] = set()

    def visit(value: Any, parts: tuple[str, ...]) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                require(isinstance(key, str), "non-string JSON key")
                child_parts = parts + (key,)
                category = classify_path(child_parts)
                if category is not None:
                    projected.add(
                        (
                            ".".join((sidecar,) + child_parts),
                            category,
                            node_type(child),
                        )
                    )
                visit(child, child_parts)
        elif isinstance(value, list):
            for child in value:
                if isinstance(child, (dict, list)):
                    visit(child, parts + ("[]",))
                else:
                    node_type(child)
        else:
            node_type(value)

    visit(data, ())
    return [
        {"key_path": path, "category": category, "node_type": kind}
        for path, category, kind in sorted(projected)
    ]


def inspect_one(
    row: dict[str, str],
    fetch: Callable[[str], bytes] = h187.get_bytes,
    cache_dir: Path | None = h193.CACHE,
) -> tuple[str, list[dict[str, str]]]:
    episode_id = row["episode_id"]
    projected: list[dict[str, str]] = []
    for sidecar in ("meta", "static"):
        expected = row[f"{sidecar}_sha256"]
        cache_path = cache_dir / f"{expected}.json" if cache_dir else None
        raw = h193.fetch_verified(
            f"{h187.ENDPOINT}/{row[f'{sidecar}_source_path']}",
            expected,
            fetch,
            cache_path,
            attempts=4 if cache_path else 1,
        )
        projected.extend(project_schema(raw, sidecar))
    return episode_id, projected


def aggregate(projection: list[dict[str, str]]) -> list[dict[str, Any]]:
    episodes: dict[tuple[str, str], set[str]] = defaultdict(set)
    types: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    seen: set[tuple[str, str, str, str]] = set()
    for row in projection:
        require(set(row) == set(FIELDS), "projection schema")
        require(row["category"] == "home_field_candidate", "category")
        marker = tuple(row[field] for field in FIELDS)
        if marker in seen:
            continue
        seen.add(marker)
        key = (row["key_path"], row["category"])
        episodes[key].add(row["episode_id"])
        types[key][row["node_type"]] += 1
    rows = []
    for key in sorted(episodes):
        ids = episodes[key]
        rows.append(
            {
                "key_path": key[0],
                "category": key[1],
                "episode_count": len(ids),
                "episode_set_sha256": h193.episode_set_hash(ids),
                "node_type_counts": dict(sorted(types[key].items())),
            }
        )
    return rows


def prior_h193_reset_seed_count() -> int:
    result = json.loads(H193.read_text())
    h193.validate(result)
    return sum(
        any(token in {"reset", "seed"} for token in key_tokens(row["key_path"]))
        for row in result["key_rows"]
    )


def build(
    fetch: Callable[[str], bytes] = h187.get_bytes,
    max_workers: int = 16,
    cache_dir: Path | None = h193.CACHE,
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    cohort = h193.load_cohort()
    projected: list[dict[str, str]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [
            pool.submit(inspect_one, row, fetch, cache_dir) for row in cohort
        ]
        for future in concurrent.futures.as_completed(futures):
            episode_id, rows = future.result()
            projected.extend({"episode_id": episode_id, **row} for row in rows)
    projected.sort(key=lambda row: tuple(row[field] for field in FIELDS))
    key_rows = aggregate(projected)
    result = {
        "schema": "h200-phail-home-field-key-inventory-v1",
        "protocol_sha256": sha256(PROTOCOL),
        "h199_sha256": sha256(H199),
        "h193_sha256": sha256(H193),
        "input_sha256": sha256(h193.INPUT),
        "episode_count": len(cohort),
        "sidecar_object_count": 2 * len(cohort),
        "fixed_tokens": list(TOKENS),
        "prohibited_tokens": list(PROHIBITED),
        "prior_h193_reset_seed_key_count": prior_h193_reset_seed_count(),
        "primitive_values_retained": False,
        "source_content_emitted": False,
        "performance_or_trajectory_values_opened": False,
        "key_rows": key_rows,
        "candidate_count": len(key_rows),
        "disposition": (
            "candidate_home_field_key_found"
            if key_rows
            else "no_fixed_vocabulary_home_field_key_found"
        ),
        "scope": (
            "key names and node types only over the exact 1,188 H187-hash-bound "
            "sidecars; no primitive values, trajectories, media, telemetry, or "
            "performance content"
        ),
    }
    return result, projected


def validate(result: dict[str, Any]) -> None:
    require(
        result.get("schema") == "h200-phail-home-field-key-inventory-v1",
        "schema",
    )
    require(result.get("protocol_sha256") == sha256(PROTOCOL), "protocol")
    require(result.get("h199_sha256") == sha256(H199), "H199")
    require(result.get("h193_sha256") == sha256(H193), "H193")
    require(result.get("input_sha256") == h193.INPUT_SHA256, "input")
    require(result.get("episode_count") == h193.EXPECTED_EPISODES, "episodes")
    require(result.get("sidecar_object_count") == 1188, "sidecars")
    require(result.get("fixed_tokens") == list(TOKENS), "tokens")
    require(result.get("prohibited_tokens") == list(PROHIBITED), "prohibited")
    require(result.get("prior_h193_reset_seed_key_count") == 0, "H193 controls")
    for key in (
        "primitive_values_retained",
        "source_content_emitted",
        "performance_or_trajectory_values_opened",
    ):
        require(result.get(key) is False, key)
    rows = result.get("key_rows")
    require(isinstance(rows, list), "rows")
    require(
        len({(row["key_path"], row["category"]) for row in rows}) == len(rows),
        "duplicate rows",
    )
    for row in rows:
        require(row["category"] == "home_field_candidate", "row category")
        require(0 < row["episode_count"] <= h193.EXPECTED_EPISODES, "row count")
        require(len(row["episode_set_sha256"]) == 64, "row hash")
        require(bool(row["node_type_counts"]), "row types")
        path_components = set(key_tokens(row["key_path"]))
        require(bool(path_components & set(TOKENS)), "unmatched row")
        require(not path_components & set(PROHIBITED), "prohibited row")
    require(result.get("candidate_count") == len(rows), "candidate count")
    expected = (
        "candidate_home_field_key_found"
        if rows
        else "no_fixed_vocabulary_home_field_key_found"
    )
    require(result.get("disposition") == expected, "disposition")


def render_projection(rows: list[dict[str, str]]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def load_projection() -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(PROJECTION.read_text())))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--offline-projection-check", action="store_true")
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    require(1 <= args.workers <= 32, "workers outside safe range")
    stored = json.loads(OUTPUT.read_text()) if OUTPUT.exists() else None
    if args.offline_projection_check:
        require(stored is not None, "stored result missing")
        validate(stored)
        require(aggregate(load_projection()) == stored["key_rows"], "projection")
        print("OK: H200 safe projection reproduces stored key aggregates")
        return
    result, projection = build(max_workers=args.workers)
    validate(result)
    if args.check:
        require(stored == result, "stored result differs from exact rebuild")
        require(PROJECTION.read_text() == render_projection(projection), "projection drift")
        print("OK: H200 exact key-only inventory reproduces")
        return
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    PROJECTION.write_text(render_projection(projection))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
