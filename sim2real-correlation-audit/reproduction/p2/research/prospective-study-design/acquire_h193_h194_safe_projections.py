#!/usr/bin/env python3
"""Reacquire H193/H194/H200 safe projections without retaining raw sidecars."""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import functools
import hashlib
import io
import json
from pathlib import Path
from typing import Any

import audit_h187_phail_context_support as h187
import audit_h193_phail_lifecycle_keys as h193
import audit_h194_phail_server_fields as h194
import audit_h200_phail_home_field_keys as h200


FAMILY = Path(__file__).resolve().parent
H193_OUTPUT = FAMILY / "projection-h193-phail-lifecycle-keys.csv"
H194_OUTPUT = FAMILY / "projection-h194-phail-server-fields.csv"
H200_OUTPUT = FAMILY / "projection-h200-phail-home-field-keys.csv"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def acquire_one(
    row: dict[str, str],
    cache_dir: Path | None,
) -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, str]]:
    projected_h193: list[dict[str, str]] = []
    projected_h200: list[dict[str, str]] = []
    static: dict[str, Any] | None = None
    for sidecar in ("meta", "static"):
        expected = row[f"{sidecar}_sha256"]
        cached = cache_dir / f"{expected}.json" if cache_dir is not None else None
        if cached is not None and cached.is_file():
            raw = cached.read_bytes()
            require(hashlib.sha256(raw).hexdigest() == expected, "cache hash")
        else:
            raw = h193.fetch_verified(
                f"{h187.ENDPOINT}/{row[f'{sidecar}_source_path']}",
                expected,
                h187.get_bytes,
                None,
                attempts=4,
            )
        projected_h193.extend(
            {"episode_id": row["episode_id"], **item}
            for item in h193.project_schema(raw, sidecar)
        )
        projected_h200.extend(
            {"episode_id": row["episode_id"], **item}
            for item in h200.project_schema(raw, sidecar)
        )
        if sidecar == "static":
            parsed = json.loads(raw)
            require(isinstance(parsed, dict), "static root is not an object")
            static = parsed
    require(static is not None, "static sidecar missing")
    values = {
        "episode_id": row["episode_id"],
        "created_ts_ns": row["created_ts_ns"],
        "utc_date": row["utc_date"],
        "policy_model": row["policy_model"],
        h194.FIELDS[0]: h194.literal_value(static, h194.FIELDS[0]),
        h194.FIELDS[1]: h194.literal_value(static, h194.FIELDS[1]),
    }
    return projected_h193, projected_h200, values


def render(
    rows: list[dict[str, str]],
    workers: int,
    cache_dir: Path | None,
) -> tuple[str, str, str]:
    h193_rows: list[dict[str, str]] = []
    h194_rows: list[dict[str, str]] = []
    h200_rows: list[dict[str, str]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        worker = functools.partial(acquire_one, cache_dir=cache_dir)
        for projected_h193, projected_h200, values in executor.map(worker, rows):
            h193_rows.extend(projected_h193)
            h200_rows.extend(projected_h200)
            h194_rows.append(values)
    h193_buffer = io.StringIO(newline="")
    h193_writer = csv.DictWriter(
        h193_buffer,
        fieldnames=("episode_id", "key_path", "category", "node_type"),
    )
    h193_writer.writeheader()
    h193_writer.writerows(
        sorted(
            h193_rows,
            key=lambda item: (
                item["episode_id"],
                item["key_path"],
                item["category"],
                item["node_type"],
            ),
        )
    )
    h194_buffer = io.StringIO(newline="")
    h194_writer = csv.DictWriter(
        h194_buffer,
        fieldnames=(
            "episode_id",
            "created_ts_ns",
            "utc_date",
            "policy_model",
            *h194.FIELDS,
        ),
    )
    h194_writer.writeheader()
    h194_writer.writerows(sorted(h194_rows, key=lambda item: item["episode_id"]))
    h200_text = h200.render_projection(
        sorted(
            h200_rows,
            key=lambda item: tuple(item[field] for field in h200.FIELDS),
        )
    )
    return h193_buffer.getvalue(), h194_buffer.getvalue(), h200_text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--cache-dir", type=Path)
    args = parser.parse_args()
    require(1 <= args.workers <= 32, "workers outside safe range")
    h193_text, h194_text, h200_text = render(
        h193.load_cohort(), args.workers, args.cache_dir
    )
    if args.check:
        require(H193_OUTPUT.read_bytes() == h193_text.encode(), "H193 drift")
        require(H194_OUTPUT.read_bytes() == h194_text.encode(), "H194 drift")
        require(H200_OUTPUT.read_bytes() == h200_text.encode(), "H200 drift")
        print("OK: H193/H194/H200 safe projections reacquire exactly")
        return
    H193_OUTPUT.write_text(h193_text, encoding="utf-8")
    H194_OUTPUT.write_text(h194_text, encoding="utf-8")
    H200_OUTPUT.write_text(h200_text, encoding="utf-8")
    print(
        "OK: wrote outcome-free H193/H194/H200 projections; "
        "no raw sidecar retained"
    )


if __name__ == "__main__":
    main()
