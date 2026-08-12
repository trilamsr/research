#!/usr/bin/env python3
"""Independent DuckDB challenge of the H202 first-state reconstruction."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

import duckdb


ROOT = Path(__file__).resolve().parents[2]
FAMILY = Path(__file__).resolve().parent
COHORT = FAMILY / "result-h187-phail-context-support-sanitized.csv"
INVENTORY = FAMILY / "projection-h190-phail-path-tree.json"
PROJECTION = FAMILY / "projection-h202-phail-initial-joint-state.csv"
SOURCE_MANIFEST = FAMILY / "sources-h202-phail-initial-joint-state.csv"
PRODUCER_RESULT = FAMILY / "result-h202-phail-initial-joint-state.json"
OUTPUT = FAMILY / "challenge-h202-phail-initial-joint-state.json"
CACHE = ROOT / "work" / "h202-initial-joint-state"
EXPECTED_EPISODES = 594
COHORT_SHA256 = "ad43fca1da065a1cb7fd84dfa9afc5691c72ebe12e7f165c68a0050e51e87ebe"
INVENTORY_SHA256 = "6350af0ce19ce1cea88c8f3c2613873c3e3624e47e0cfde5c02fbaa1506d98e1"
BASE = [0.0, -0.31, 0.0, -1.65, 0.0, 1.522, 0.0]
HALF_WIDTHS = [0.03, 0.05, 0.08, 0.08, 0.10, 0.10, 0.10]
SIGNALS = ("robot_state.q", "robot_state.error")
ABS_TOLERANCE = 1e-12


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def synthetic_controls(connection: duckdb.DuckDBPyConnection) -> dict[str, bool]:
    with tempfile.TemporaryDirectory(prefix="h202-duckdb-control-") as directory:
        path = Path(directory) / "sentinel.parquet"
        quoted = str(path).replace("'", "''")
        connection.execute(
            f"""
            COPY (
              SELECT * FROM (
                VALUES
                  (11::BIGINT, [0.1,0.2,0.3,0.4,0.5,0.6,0.7]::DOUBLE[]),
                  (22::BIGINT, [999,999,999,999,999,999,999]::DOUBLE[])
              ) AS t(timestamp, value)
            ) TO '{quoted}' (FORMAT PARQUET)
            """
        )
        first = connection.execute(
            "SELECT timestamp, value FROM read_parquet(?) LIMIT 1", [str(path)]
        ).fetchone()
    quantiles = connection.execute(
        """
        SELECT
          quantile_cont(x::DOUBLE, 0.05),
          quantile_cont(x::DOUBLE, 0.50),
          quantile_cont(x::DOUBLE, 0.95),
          stddev_pop(x::DOUBLE)
        FROM (VALUES (0.0), (10.0), (20.0), (30.0)) AS t(x)
        """
    ).fetchone()
    return {
        "first_row_not_later_sentinel": (
            first is not None
            and first[0] == 11
            and [float(value) for value in first[1]]
            == [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
        ),
        "linear_quantiles": (
            quantiles is not None
            and math.isclose(float(quantiles[0]), 1.5)
            and math.isclose(float(quantiles[1]), 15.0)
            and math.isclose(float(quantiles[2]), 28.5)
        ),
        "population_standard_deviation": (
            quantiles is not None
            and math.isclose(float(quantiles[3]), math.sqrt(125.0))
        ),
    }


def select_sources() -> list[dict[str, Any]]:
    require(sha256(COHORT) == COHORT_SHA256, "cohort hash")
    require(sha256(INVENTORY) == INVENTORY_SHA256, "inventory hash")
    cohort = read_csv(COHORT)
    inventory = json.loads(INVENTORY.read_text())
    require(len(cohort) == EXPECTED_EPISODES, "cohort count")
    require(inventory["content_opened"] is False, "safe inventory")
    by_key: dict[str, list[dict[str, Any]]] = {}
    for item in inventory["dataset_inventory"]:
        by_key.setdefault(item["key"], []).append(item)
    selected = []
    for episode in cohort:
        parent = PurePosixPath(episode["meta_source_path"]).parent
        require(parent.name == episode["episode_id"], "episode root")
        row: dict[str, Any] = {"episode_id": episode["episode_id"]}
        for signal in SIGNALS:
            key = str(parent / f"{signal}.parquet")
            candidates = by_key.get(key, [])
            require(len(candidates) == 1, f"{episode['episode_id']} {signal}")
            item = candidates[0]
            require(PurePosixPath(item["key"]).parent == parent, "source root")
            require(PurePosixPath(item["key"]).name == f"{signal}.parquet", "basename")
            require(item["size"] > 0 and len(item["etag"]) == 32, "source identity")
            row[signal] = item
        selected.append(row)
    require(
        len({row["episode_id"] for row in selected}) == EXPECTED_EPISODES,
        "selection identity",
    )
    return selected


def cache_path(key: str) -> Path:
    return CACHE / f"{hashlib.sha256(key.encode()).hexdigest()}.parquet"


def first_row(
    connection: duckdb.DuckDBPyConnection, path: Path
) -> tuple[int, Any, int]:
    require(path.is_file(), "cached source missing")
    row = connection.execute(
        "SELECT timestamp, value FROM read_parquet(?) LIMIT 1", [str(path)]
    ).fetchone()
    count = connection.execute(
        "SELECT count(*) FROM read_parquet(?)", [str(path)]
    ).fetchone()
    require(row is not None and count is not None, "parquet query")
    return int(row[0]), row[1], int(count[0])


def reconstruct(
    connection: duckdb.DuckDBPyConnection,
    selected: list[dict[str, Any]],
) -> tuple[list[tuple[Any, ...]], dict[str, Any]]:
    projection = {row["episode_id"]: row for row in read_csv(PROJECTION)}
    manifest = {
        (row["episode_id"], row["signal"]): row
        for row in read_csv(SOURCE_MANIFEST)
    }
    require(len(projection) == EXPECTED_EPISODES, "projection count")
    require(len(manifest) == 2 * EXPECTED_EPISODES, "manifest count")
    challenged: list[tuple[Any, ...]] = []
    object_hashes: set[str] = set()
    total_bytes = 0
    for index, item in enumerate(selected, start=1):
        episode_id = item["episode_id"]
        require(episode_id in projection, "projection identity")
        projected = projection[episode_id]
        values: dict[str, Any] = {}
        timestamps: dict[str, int] = {}
        for signal in SIGNALS:
            source = item[signal]
            path = cache_path(source["key"])
            digest = sha256(path)
            timestamp, value, row_count = first_row(connection, path)
            recorded = manifest[(episode_id, signal)]
            prefix = "q" if signal == "robot_state.q" else "error"
            require(path.stat().st_size == source["size"], "source size")
            require(recorded["path"] == source["key"], "manifest path")
            require(recorded["etag"] == source["etag"], "manifest etag")
            require(int(recorded["byte_count"]) == source["size"], "manifest size")
            require(recorded["sha256"] == digest, "manifest digest")
            require(int(recorded["row_count"]) == row_count, "manifest row count")
            require(projected[f"{prefix}_path"] == source["key"], "projection path")
            require(projected[f"{prefix}_sha256"] == digest, "projection digest")
            require(int(projected[f"{prefix}_row_count"]) == row_count, "projection rows")
            timestamps[signal] = timestamp
            values[signal] = value
            object_hashes.add(digest)
            total_bytes += source["size"]
        require(timestamps[SIGNALS[0]] == timestamps[SIGNALS[1]], "timestamp alignment")
        require(int(projected["timestamp_ns"]) == timestamps[SIGNALS[0]], "projected timestamp")
        q = values["robot_state.q"]
        error = values["robot_state.error"]
        require(isinstance(q, list) and len(q) == 7, "q shape")
        q = [float(value) for value in q]
        require(all(math.isfinite(value) for value in q), "finite q")
        require(int(error) in {0, 1}, "error value")
        require(int(projected["error"]) == int(error), "projected error")
        for joint, value in enumerate(q):
            require(
                math.isclose(
                    float(projected[f"q{joint}"]),
                    value,
                    rel_tol=0.0,
                    abs_tol=0.0,
                ),
                "projected q",
            )
        challenged.append(
            (
                episode_id,
                int(error),
                *[q[joint] - BASE[joint] for joint in range(7)],
            )
        )
        if index % 100 == 0:
            print(f"H202 DuckDB challenge: {index}/{EXPECTED_EPISODES}")
    return challenged, {
        "episode_count": len(challenged),
        "source_object_count": 2 * len(challenged),
        "unique_source_sha256_count": len(object_hashes),
        "total_source_bytes": total_bytes,
    }


def summarize(
    connection: duckdb.DuckDBPyConnection,
    rows: list[tuple[Any, ...]],
) -> dict[str, Any]:
    connection.execute(
        """
        CREATE TEMP TABLE challenged (
          episode_id VARCHAR,
          error INTEGER,
          d0 DOUBLE, d1 DOUBLE, d2 DOUBLE, d3 DOUBLE,
          d4 DOUBLE, d5 DOUBLE, d6 DOUBLE
        )
        """
    )
    connection.executemany(
        "INSERT INTO challenged VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", rows
    )
    coverage = connection.execute(
        """
        SELECT
          count(*),
          count(*) FILTER (WHERE error = 1),
          count(*) FILTER (WHERE error = 0)
        FROM challenged
        """
    ).fetchone()
    require(coverage is not None, "coverage summary")
    joints = []
    for index, half_width in enumerate(HALF_WIDTHS):
        row = connection.execute(
            f"""
            SELECT
              min(d{index}),
              quantile_cont(d{index}, 0.05),
              quantile_cont(d{index}, 0.50),
              avg(d{index}),
              stddev_pop(d{index}),
              quantile_cont(d{index}, 0.95),
              max(d{index}),
              avg(CASE WHEN d{index} BETWEEN ? AND ? THEN 1.0 ELSE 0.0 END)
            FROM challenged WHERE error = 0
            """,
            [-half_width, half_width],
        ).fetchone()
        require(row is not None and all(value is not None for value in row), "joint summary")
        joints.append(
            {
                "joint_index": index,
                "minimum_rad": float(row[0]),
                "q05_rad": float(row[1]),
                "median_rad": float(row[2]),
                "mean_rad": float(row[3]),
                "population_std_rad": float(row[4]),
                "q95_rad": float(row[5]),
                "maximum_rad": float(row[6]),
                "fraction_inside_configured_target_support": float(row[7]),
                "observed_std_to_uniform_target_std_ratio": (
                    float(row[4]) / (half_width / math.sqrt(3))
                ),
            }
        )
    squared = " + ".join(f"d{index} * d{index}" for index in range(7))
    norm = connection.execute(
        f"""
        WITH norms AS (
          SELECT sqrt({squared}) AS value
          FROM challenged WHERE error = 0
        )
        SELECT
          min(value),
          quantile_cont(value, 0.50),
          avg(value),
          sqrt(avg(value * value)),
          quantile_cont(value, 0.95),
          max(value)
        FROM norms
        """
    ).fetchone()
    require(norm is not None and all(value is not None for value in norm), "norm summary")
    return {
        "file_pair_count": int(coverage[0]),
        "first_error_count": int(coverage[1]),
        "valid_achieved_state_count": int(coverage[2]),
        "valid_achieved_state_fraction": int(coverage[2]) / EXPECTED_EPISODES,
        "joint_deviation_summary": joints,
        "euclidean_joint_deviation_summary": {
            "minimum_rad": float(norm[0]),
            "median_rad": float(norm[1]),
            "mean_rad": float(norm[2]),
            "rms_rad": float(norm[3]),
            "q95_rad": float(norm[4]),
            "maximum_rad": float(norm[5]),
        },
    }


def compare_numeric(actual: Any, expected: Any, path: str = "") -> float:
    maximum = 0.0
    if isinstance(expected, dict):
        require(set(actual) == set(expected), f"{path} keys")
        for key in expected:
            maximum = max(
                maximum,
                compare_numeric(actual[key], expected[key], f"{path}.{key}"),
            )
    elif isinstance(expected, list):
        require(len(actual) == len(expected), f"{path} length")
        for index, value in enumerate(expected):
            maximum = max(
                maximum,
                compare_numeric(actual[index], value, f"{path}[{index}]"),
            )
    elif isinstance(expected, float):
        difference = abs(float(actual) - expected)
        require(difference <= ABS_TOLERANCE, f"{path} difference {difference}")
        maximum = difference
    else:
        require(actual == expected, f"{path} value")
    return maximum


def build() -> dict[str, Any]:
    producer = json.loads(PRODUCER_RESULT.read_text())
    connection = duckdb.connect(":memory:")
    controls = synthetic_controls(connection)
    require(all(controls.values()), "synthetic controls")
    selection = select_sources()
    rows, integrity = reconstruct(connection, selection)
    challenged_summary = summarize(connection, rows)
    expected_summary = {
        key: producer["summary"][key]
        for key in (
            "file_pair_count",
            "first_error_count",
            "valid_achieved_state_count",
            "valid_achieved_state_fraction",
            "joint_deviation_summary",
            "euclidean_joint_deviation_summary",
        )
    }
    maximum_difference = compare_numeric(challenged_summary, expected_summary)
    require(producer["classification"] == "complete_initial_joint_state_reconstruction", "classification")
    require(challenged_summary["first_error_count"] == 0, "error count")
    return {
        "schema": "h202-duckdb-independent-challenge-v1",
        "duckdb_version": duckdb.__version__,
        "producer_result_sha256": sha256(PRODUCER_RESULT),
        "projection_sha256": sha256(PROJECTION),
        "source_manifest_sha256": sha256(SOURCE_MANIFEST),
        "method": (
            "independent exact-path selector, full local source hash verification, "
            "DuckDB first-row Parquet reads, and DuckDB SQL summaries"
        ),
        "synthetic_controls": controls,
        "integrity": integrity,
        "classification_confirmed": producer["classification"],
        "maximum_absolute_summary_difference": maximum_difference,
        "absolute_tolerance": ABS_TOLERANCE,
        "projection_exactly_confirmed": True,
        "fixed_summary_confirmed": True,
        "later_rows_summarized": False,
        "result": "pass",
    }


def validate(result: dict[str, Any]) -> None:
    require(result["schema"] == "h202-duckdb-independent-challenge-v1", "schema")
    require(result["producer_result_sha256"] == sha256(PRODUCER_RESULT), "producer")
    require(result["projection_sha256"] == sha256(PROJECTION), "projection")
    require(result["source_manifest_sha256"] == sha256(SOURCE_MANIFEST), "manifest")
    require(all(result["synthetic_controls"].values()), "controls")
    require(result["integrity"]["episode_count"] == EXPECTED_EPISODES, "episodes")
    require(result["integrity"]["source_object_count"] == 2 * EXPECTED_EPISODES, "objects")
    require(result["classification_confirmed"] == "complete_initial_joint_state_reconstruction", "classification")
    require(result["maximum_absolute_summary_difference"] <= ABS_TOLERANCE, "summary")
    require(result["projection_exactly_confirmed"] is True, "projection confirmation")
    require(result["fixed_summary_confirmed"] is True, "summary confirmation")
    require(result["later_rows_summarized"] is False, "later rows")
    require(result["result"] == "pass", "result")


def main() -> None:
    candidate = build()
    validate(candidate)
    OUTPUT.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n")
    print(json.dumps(candidate, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
