#!/usr/bin/env python3
"""Outcome-free key-only inventory of pinned PhAIL v1.0 sidecars."""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import io
import json
import re
import time
import urllib.error
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

import audit_h187_phail_context_support as h187


FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h193-phail-lifecycle-key-inventory.md"
INPUT = FAMILY / "result-h187-phail-context-support-sanitized.csv"
OUTPUT = FAMILY / "result-h193-phail-lifecycle-key-inventory.json"
CACHE = FAMILY.parent.parent / "work" / "h193-sidecars"
INPUT_SHA256 = "ad43fca1da065a1cb7fd84dfa9afc5691c72ebe12e7f165c68a0050e51e87ebe"
EXPECTED_EPISODES = 594
LIFECYCLE_TOKENS = (
    "session",
    "run",
    "batch",
    "block",
    "sequence",
    "seq",
    "trial",
    "shift",
    "operator",
    "worker",
    "user",
    "robot",
    "device",
    "host",
    "machine",
    "reset",
    "restart",
    "sampler",
    "seed",
    "assignment",
    "availability",
    "candidate",
    "roster",
    "pool",
    "retry",
    "abort",
    "deviation",
    "carryover",
    "parent",
    "previous",
    "group",
    "cluster",
)
CONTROL_KEYS = ("episode_id", "created_ts_ns", "id")
PROHIBITED_TOKENS = (
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
)
TOKEN_RE = re.compile(r"[A-Za-z0-9]+")
REQUIRED_COLUMNS = (
    "episode_id",
    "meta_source_path",
    "meta_sha256",
    "static_source_path",
    "static_sha256",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


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
    all_tokens = tuple(
        token for part in parts for token in key_tokens(part)
    )
    if set(all_tokens) & set(PROHIBITED_TOKENS):
        return None
    final = parts[-1].lower()
    if final in CONTROL_KEYS:
        return "identity_time_control"
    if set(all_tokens) & set(LIFECYCLE_TOKENS):
        return "lifecycle_candidate"
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


def validate_cohort_rows(rows: list[dict[str, str]]) -> None:
    require(len(rows) == EXPECTED_EPISODES, "episode count changed")
    require(
        all(column in rows[0] for column in REQUIRED_COLUMNS),
        "required column missing",
    )
    episode_ids = [row["episode_id"] for row in rows]
    require(len(set(episode_ids)) == len(episode_ids), "duplicate episode")
    for row in rows:
        require(all(row[column] for column in REQUIRED_COLUMNS), "blank identity")
        require(
            row["meta_source_path"].endswith("/meta.json"),
            "meta path changed",
        )
        require(
            row["static_source_path"].endswith("/static.json"),
            "static path changed",
        )
        require(
            len(row["meta_sha256"]) == 64 and len(row["static_sha256"]) == 64,
            "source hash malformed",
        )


def load_cohort() -> list[dict[str, str]]:
    require(sha256(INPUT) == INPUT_SHA256, "H187 sanitized input drifted")
    rows = list(csv.DictReader(io.StringIO(INPUT.read_text())))
    validate_cohort_rows(rows)
    return rows


def inspect_one(
    row: dict[str, str],
    fetch: Callable[[str], bytes] = h187.get_bytes,
    cache_dir: Path | None = None,
) -> tuple[str, list[dict[str, str]]]:
    episode_id = row["episode_id"]
    projected: list[dict[str, str]] = []
    for sidecar in ("meta", "static"):
        path = row[f"{sidecar}_source_path"]
        expected_hash = row[f"{sidecar}_sha256"]
        cache_path = (
            cache_dir / f"{expected_hash}.json"
            if cache_dir is not None
            else None
        )
        raw = fetch_verified(
            f"{h187.ENDPOINT}/{path}",
            expected_hash,
            fetch,
            cache_path,
            attempts=4 if cache_path is not None else 1,
        )
        projected.extend(project_schema(raw, sidecar))
    return episode_id, projected


def fetch_verified(
    url: str,
    expected_hash: str,
    fetch: Callable[[str], bytes],
    cache_path: Path | None,
    attempts: int,
) -> bytes:
    if cache_path is not None and cache_path.exists():
        raw = cache_path.read_bytes()
        require(sha256_bytes(raw) == expected_hash, "cached source hash mismatch")
        return raw
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            raw = fetch(url)
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            last_error = error
            if attempt + 1 < attempts:
                time.sleep(0.25 * (2**attempt))
            continue
        require(sha256_bytes(raw) == expected_hash, "source hash mismatch")
        if cache_path is not None:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            temporary = cache_path.with_suffix(".tmp")
            temporary.write_bytes(raw)
            temporary.replace(cache_path)
        return raw
    raise ValueError(f"source unavailable after {attempts} attempts: {last_error}")


def episode_set_hash(episode_ids: set[str]) -> str:
    payload = "".join(f"{value}\n" for value in sorted(episode_ids)).encode()
    return sha256_bytes(payload)


def build(
    fetch: Callable[[str], bytes] = h187.get_bytes,
    max_workers: int = 16,
    cache_dir: Path | None = CACHE,
) -> dict[str, Any]:
    rows = load_cohort()
    episodes_by_key: dict[
        tuple[str, str], set[str]
    ] = defaultdict(set)
    types_by_key: dict[
        tuple[str, str], Counter[str]
    ] = defaultdict(Counter)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [
            pool.submit(inspect_one, row, fetch, cache_dir) for row in rows
        ]
        for future in concurrent.futures.as_completed(futures):
            episode_id, projected = future.result()
            seen: set[tuple[str, str, str]] = set()
            for item in projected:
                key = (item["key_path"], item["category"])
                marker = (item["key_path"], item["category"], item["node_type"])
                if marker in seen:
                    continue
                seen.add(marker)
                episodes_by_key[key].add(episode_id)
                types_by_key[key][item["node_type"]] += 1
    key_rows = []
    for key in sorted(episodes_by_key):
        episode_ids = episodes_by_key[key]
        key_rows.append(
            {
                "key_path": key[0],
                "category": key[1],
                "episode_count": len(episode_ids),
                "episode_set_sha256": episode_set_hash(episode_ids),
                "node_type_counts": dict(sorted(types_by_key[key].items())),
            }
        )
    candidates = [
        row for row in key_rows if row["category"] == "lifecycle_candidate"
    ]
    return {
        "schema": "h193-phail-lifecycle-key-inventory-v1",
        "protocol_sha256": sha256(PROTOCOL),
        "input_sha256": sha256(INPUT),
        "episode_count": len(rows),
        "sidecar_object_count": len(rows) * 2,
        "fixed_lifecycle_tokens": list(LIFECYCLE_TOKENS),
        "identity_time_controls": list(CONTROL_KEYS),
        "primitive_values_retained": False,
        "source_content_emitted": False,
        "performance_field_values_opened": False,
        "key_rows": key_rows,
        "lifecycle_candidate_count": len(candidates),
        "disposition": (
            "candidate_lifecycle_key_found"
            if candidates
            else "no_fixed_vocabulary_lifecycle_key_found"
        ),
        "scope": (
            "key names and node types only over the exact hash-bound H187 "
            "sidecars; candidates require separate semantics and safe-value "
            "review"
        ),
    }


def validate(result: dict[str, Any]) -> None:
    require(
        result.get("schema") == "h193-phail-lifecycle-key-inventory-v1",
        "schema",
    )
    require(result.get("protocol_sha256") == sha256(PROTOCOL), "protocol hash")
    require(result.get("input_sha256") == INPUT_SHA256, "input hash")
    require(result.get("episode_count") == EXPECTED_EPISODES, "episodes")
    require(result.get("sidecar_object_count") == 1188, "sidecar count")
    require(result.get("fixed_lifecycle_tokens") == list(LIFECYCLE_TOKENS), "tokens")
    require(result.get("primitive_values_retained") is False, "values retained")
    require(result.get("source_content_emitted") is False, "content emitted")
    require(
        result.get("performance_field_values_opened") is False,
        "performance values",
    )
    rows = result.get("key_rows")
    require(isinstance(rows, list), "key rows")
    require(
        len({(row["key_path"], row["category"]) for row in rows}) == len(rows),
        "duplicate key row",
    )
    require(
        all(
            row["category"] in {"lifecycle_candidate", "identity_time_control"}
            and 0 < row["episode_count"] <= EXPECTED_EPISODES
            and len(row["episode_set_sha256"]) == 64
            and bool(row["node_type_counts"])
            for row in rows
        ),
        "invalid projected row",
    )
    candidate_count = sum(
        row["category"] == "lifecycle_candidate" for row in rows
    )
    require(result.get("lifecycle_candidate_count") == candidate_count, "count")
    expected = (
        "candidate_lifecycle_key_found"
        if candidate_count
        else "no_fixed_vocabulary_lifecycle_key_found"
    )
    require(result.get("disposition") == expected, "disposition")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    require(1 <= args.workers <= 32, "workers outside safe range")
    if args.check:
        stored = json.loads(OUTPUT.read_text())
        validate(stored)
        rebuilt = build(max_workers=args.workers)
        require(stored == rebuilt, "stored result differs from exact rebuild")
        return
    result = build(max_workers=args.workers)
    validate(result)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
