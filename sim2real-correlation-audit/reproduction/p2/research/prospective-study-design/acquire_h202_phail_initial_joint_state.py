#!/usr/bin/env python3
"""Acquire only the first PhAIL joint-state/error sample per fixed episode."""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import io
import json
import math
import time
import urllib.error
import urllib.request
from pathlib import Path, PurePosixPath
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[2]
FAMILY = Path(__file__).resolve().parent
COHORT = FAMILY / "result-h187-phail-context-support-sanitized.csv"
INVENTORY = FAMILY / "projection-h190-phail-path-tree.json"
PROJECTION = FAMILY / "projection-h202-phail-initial-joint-state.csv"
SOURCE_MANIFEST = FAMILY / "sources-h202-phail-initial-joint-state.csv"
CACHE = ROOT / "work" / "h202-initial-joint-state"
ENDPOINT = "https://storage.eu-north1.nebius.cloud/positronic-public"
COHORT_SHA256 = "ad43fca1da065a1cb7fd84dfa9afc5691c72ebe12e7f165c68a0050e51e87ebe"
INVENTORY_SHA256 = "6350af0ce19ce1cea88c8f3c2613873c3e3624e47e0cfde5c02fbaa1506d98e1"
EXPECTED_EPISODES = 594
SIGNALS = ("robot_state.q", "robot_state.error")
PROJECTION_FIELDS = (
    "episode_id",
    "timestamp_ns",
    "error",
    "q0",
    "q1",
    "q2",
    "q3",
    "q4",
    "q5",
    "q6",
    "q_path",
    "q_etag",
    "q_size",
    "q_sha256",
    "q_row_count",
    "error_path",
    "error_etag",
    "error_size",
    "error_sha256",
    "error_row_count",
)
MANIFEST_FIELDS = (
    "episode_id",
    "signal",
    "path",
    "etag",
    "advertised_size",
    "byte_count",
    "sha256",
    "row_count",
    "schema_sha256",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_cohort() -> list[dict[str, str]]:
    require(sha256(COHORT) == COHORT_SHA256, "cohort hash")
    with COHORT.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    require(len(rows) == EXPECTED_EPISODES, "cohort count")
    require(len({row["episode_id"] for row in rows}) == len(rows), "duplicate cohort")
    return rows


def load_inventory() -> list[dict[str, Any]]:
    require(sha256(INVENTORY) == INVENTORY_SHA256, "inventory hash")
    payload = json.loads(INVENTORY.read_text())
    require(payload["schema"] == "h190-phail-safe-path-tree-projection-v1", "inventory schema")
    require(payload["content_opened"] is False, "inventory content flag")
    return payload["dataset_inventory"]


def select_sources(
    cohort: list[dict[str, str]],
    inventory: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_key: dict[str, list[dict[str, Any]]] = {}
    for row in inventory:
        by_key.setdefault(row["key"], []).append(row)
    selected = []
    for row in cohort:
        parent = PurePosixPath(row["meta_source_path"]).parent
        item: dict[str, Any] = {"episode_id": row["episode_id"]}
        require(parent.name == row["episode_id"], "episode directory identity")
        for signal in SIGNALS:
            key = str(parent / f"{signal}.parquet")
            matches = by_key.get(key, [])
            require(len(matches) == 1, f"{row['episode_id']}:{signal} count")
            record = matches[0]
            require(PurePosixPath(record["key"]).parent == parent, "path root")
            require(PurePosixPath(record["key"]).name == f"{signal}.parquet", "basename")
            require(
                isinstance(record["size"], int)
                and record["size"] > 0
                and isinstance(record["etag"], str)
                and len(record["etag"]) == 32,
                "inventory identity",
            )
            item[signal] = record
        selected.append(item)
    return selected


def fetch(record: dict[str, Any], cache_dir: Path, attempts: int = 4) -> Path:
    etag = record["etag"]
    cache_key = hashlib.sha256(record["key"].encode()).hexdigest()
    destination = cache_dir / f"{cache_key}.parquet"
    metadata_path = cache_dir / f"{cache_key}.json"
    if destination.is_file():
        require(metadata_path.is_file(), "cached metadata missing")
        metadata = json.loads(metadata_path.read_text())
        require(
            set(metadata) == {"etag", "key", "sha256", "size"},
            "cached metadata schema",
        )
        require(
            metadata["etag"] == etag
            and metadata["key"] == record["key"]
            and metadata["size"] == record["size"]
            and isinstance(metadata["sha256"], str)
            and len(metadata["sha256"]) == 64,
            "cached metadata",
        )
        raw = destination.read_bytes()
        require(len(raw) == record["size"], "cached size")
        require(hashlib.sha256(raw).hexdigest() == metadata["sha256"], "cached SHA-256")
        return destination
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(
                f"{ENDPOINT}/{record['key']}",
                headers={"User-Agent": "sim2real-h202/1.0"},
            )
            with urllib.request.urlopen(request, timeout=90) as response:
                response_etag = response.headers.get("ETag", "").strip('"')
                response_length = response.headers.get("Content-Length")
                raw = response.read()
            require(response_etag == etag, "response ETag")
            require(
                response_length is not None
                and int(response_length) == record["size"],
                "response length",
            )
            require(len(raw) == record["size"], "download size")
            digest = hashlib.sha256(raw).hexdigest()
            cache_dir.mkdir(parents=True, exist_ok=True)
            temporary = cache_dir / f".{cache_key}.tmp"
            temporary.write_bytes(raw)
            temporary.replace(destination)
            metadata_path.write_text(
                json.dumps(
                    {
                        "etag": etag,
                        "key": record["key"],
                        "sha256": digest,
                        "size": record["size"],
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n"
            )
            return destination
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            last_error = error
            if attempt + 1 < attempts:
                time.sleep(0.5 * (2**attempt))
    raise ValueError(f"source unavailable after {attempts} attempts: {last_error}")


def schema_hash(schema: pa.Schema) -> str:
    return hashlib.sha256(schema.serialize().to_pybytes()).hexdigest()


def first_sample(path: Path, signal: str) -> dict[str, Any]:
    parquet = pq.ParquetFile(path)
    metadata = parquet.metadata
    require(metadata is not None and metadata.num_rows > 0, f"{signal} empty")
    require("timestamp" in parquet.schema_arrow.names, f"{signal} timestamp")
    require("value" in parquet.schema_arrow.names, f"{signal} value")
    batches = parquet.iter_batches(
        batch_size=1,
        row_groups=[0],
        columns=["timestamp", "value"],
    )
    try:
        batch = next(batches)
    except StopIteration as error:
        raise ValueError(f"{signal} missing first batch") from error
    require(batch.num_rows == 1, f"{signal} first batch size")
    timestamp = batch.column(batch.schema.get_field_index("timestamp"))[0].as_py()
    value = batch.column(batch.schema.get_field_index("value"))[0].as_py()
    require(isinstance(timestamp, int), f"{signal} timestamp type")
    if signal == "robot_state.q":
        require(isinstance(value, list) and len(value) == 7, "q dimension")
        require(
            all(isinstance(x, int | float) and math.isfinite(float(x)) for x in value),
            "q finite",
        )
        value = [float(x) for x in value]
    else:
        require(isinstance(value, int) and not isinstance(value, bool), "error type")
        require(value in {0, 1}, "error value")
    return {
        "timestamp_ns": timestamp,
        "value": value,
        "row_count": metadata.num_rows,
        "schema_sha256": schema_hash(parquet.schema_arrow),
    }


def require_aligned(
    episode_id: str,
    q_sample: dict[str, Any],
    error_sample: dict[str, Any],
) -> None:
    require(
        q_sample["timestamp_ns"] == error_sample["timestamp_ns"],
        f"{episode_id}: first timestamp mismatch",
    )


def acquire_one(item: dict[str, Any], cache_dir: Path) -> tuple[dict[str, str], list[dict[str, str]]]:
    episode_id = item["episode_id"]
    observations = {}
    manifest = []
    for signal in SIGNALS:
        record = item[signal]
        path = fetch(record, cache_dir)
        sample = first_sample(path, signal)
        raw_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
        observations[signal] = (record, sample, raw_sha256)
        manifest.append(
            {
                "episode_id": episode_id,
                "signal": signal,
                "path": record["key"],
                "etag": record["etag"],
                "advertised_size": str(record["size"]),
                "byte_count": str(path.stat().st_size),
                "sha256": raw_sha256,
                "row_count": str(sample["row_count"]),
                "schema_sha256": sample["schema_sha256"],
            }
        )
    q_record, q_sample, q_sha = observations["robot_state.q"]
    e_record, e_sample, e_sha = observations["robot_state.error"]
    require_aligned(episode_id, q_sample, e_sample)
    row = {
        "episode_id": episode_id,
        "timestamp_ns": str(q_sample["timestamp_ns"]),
        "error": str(e_sample["value"]),
        **{f"q{i}": repr(value) for i, value in enumerate(q_sample["value"])},
        "q_path": q_record["key"],
        "q_etag": q_record["etag"],
        "q_size": str(q_record["size"]),
        "q_sha256": q_sha,
        "q_row_count": str(q_sample["row_count"]),
        "error_path": e_record["key"],
        "error_etag": e_record["etag"],
        "error_size": str(e_record["size"]),
        "error_sha256": e_sha,
        "error_row_count": str(e_sample["row_count"]),
    }
    return row, manifest


def render(rows: list[dict[str, str]], fields: tuple[str, ...]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def run(
    selection: list[dict[str, Any]],
    cache_dir: Path,
    workers: int,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    rows = []
    manifest = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(acquire_one, item, cache_dir): item["episode_id"]
            for item in selection
        }
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            row, records = future.result()
            rows.append(row)
            manifest.extend(records)
            completed += 1
            if completed % 50 == 0 or completed == len(selection):
                print(f"H202 acquisition: {completed}/{len(selection)} episodes validated")
    rows.sort(key=lambda row: row["episode_id"])
    manifest.sort(key=lambda row: (row["episode_id"], row["signal"]))
    return rows, manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rehearsal", action="store_true")
    parser.add_argument("--fetch", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--cache-dir", type=Path, default=CACHE)
    args = parser.parse_args()
    require(sum((args.rehearsal, args.fetch, args.check)) == 1, "choose one mode")
    require(1 <= args.workers <= 24, "workers")
    selected = select_sources(load_cohort(), load_inventory())
    require(len(selected) == EXPECTED_EPISODES, "selection count")
    if args.rehearsal:
        selected = [selected[0], selected[-1]]
    rows, manifest = run(selected, args.cache_dir, args.workers)
    if args.rehearsal:
        require(len(rows) == 2 and len(manifest) == 4, "rehearsal coverage")
        print("OK: H202 two-episode transport/schema rehearsal passed; values not printed")
        return
    projection_text = render(rows, PROJECTION_FIELDS)
    manifest_text = render(manifest, MANIFEST_FIELDS)
    if args.check:
        require(PROJECTION.read_bytes() == projection_text.encode(), "projection drift")
        require(SOURCE_MANIFEST.read_bytes() == manifest_text.encode(), "manifest drift")
        print("OK: H202 full first-state projection reacquires exactly")
        return
    PROJECTION.write_text(projection_text, encoding="utf-8")
    SOURCE_MANIFEST.write_text(manifest_text, encoding="utf-8")
    print(
        "OK: H202 wrote first-state projection and source manifest; "
        "no values printed"
    )


if __name__ == "__main__":
    main()
