#!/usr/bin/env python3
"""Result-exposed, outcome-free census of two fixed PhAIL server fields."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import audit_h193_phail_lifecycle_keys as h193


FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h194-phail-server-field-semantics.md"
H193_RESULT = FAMILY / "result-h193-phail-lifecycle-key-inventory.json"
OUTPUT = FAMILY / "result-h194-phail-server-field-semantics.json"
SOURCE_ROOT = FAMILY.parent.parent / "work" / "h194-positronic-v0.2.1"
H193_RESULT_SHA256 = "3c9eec888c77e425349ffb9997f0eb249c99b73eb9b24bf94278ee8a2e25f429"
SOURCE_COMMIT = "e406176bc526babb06844a48e3627a5c0409eb74"
FIELDS = (
    "inference.policy.server.host",
    "inference.policy.server.device",
)
MISSING = "<missing>"
SOURCE_FILES = {
    "positronic/policy/remote.py": {
        "sha256": "787bff2df4b06a26441106ddc78ab73951d0bdd02fb34601f994b531d3809199",
        "lines": "97-99",
        "supports": "server metadata is flattened into recorded policy metadata",
    },
    "positronic/offboard/vendor_server.py": {
        "sha256": "82d1d136f7e263b9e7b96f124ff5743ea2bafaacc1f79ae5c9d88a99055d0894",
        "lines": "116-118, 213",
        "supports": "host configures the inference server bind address",
    },
    "positronic/vendors/lerobot/server.py": {
        "sha256": "6fe568b46b314f5313b547ef33c93b62631d190ae225275b58a3b4464a70e6a9",
        "lines": "32-45",
        "supports": "host and selected device are copied into server metadata",
    },
    "positronic/vendors/lerobot/policy.py": {
        "sha256": "c0e3b02de5f2428d1bdb0256a6d030f51c4305b6241abe12175e3ca108ab6039",
        "lines": "10-23",
        "supports": "device is a generic accelerator backend selected by availability",
    },
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def verify_sources(
    source_root: Path = SOURCE_ROOT,
    source_files: dict[str, dict[str, str]] = SOURCE_FILES,
) -> list[dict[str, str]]:
    require(source_root.is_dir(), "pinned Positronic source checkout missing")
    head = (source_root / ".git" / "HEAD").read_text().strip()
    require(
        head == SOURCE_COMMIT or head == f"ref: refs/tags/v0.2.1",
        "source checkout identity changed",
    )
    rows = []
    for relative, record in source_files.items():
        source = source_root / relative
        require(source.is_file(), f"source file missing: {relative}")
        require(sha256(source) == record["sha256"], f"source drift: {relative}")
        rows.append(
            {
                "path": relative,
                "sha256": record["sha256"],
                "lines": record["lines"],
                "supports": record["supports"],
            }
        )
    return rows


def literal_value(data: dict[str, Any], field: str) -> str:
    if field not in data:
        return MISSING
    value = data[field]
    require(
        value is None or isinstance(value, (str, int, float, bool)),
        "candidate value is not literal",
    )
    if value is None:
        return "<null>"
    if isinstance(value, bool):
        return f"boolean:{str(value).lower()}"
    if isinstance(value, str):
        return f"string:{value}"
    if isinstance(value, int):
        return f"number:{value}"
    return f"number:{value!r}"


def episode_set_hash(values: set[str]) -> str:
    return sha256_bytes(
        "".join(f"{value}\n" for value in sorted(values)).encode()
    )


def run_summary(labels: list[str]) -> dict[str, Any]:
    require(bool(labels), "empty chronology")
    lengths: dict[str, list[int]] = defaultdict(list)
    previous = labels[0]
    current = 1
    for label in labels[1:]:
        if label == previous:
            current += 1
        else:
            lengths[previous].append(current)
            previous = label
            current = 1
    lengths[previous].append(current)
    return {
        label: {
            "run_count": len(values),
            "run_lengths": values,
            "minimum_run_length": min(values),
            "maximum_run_length": max(values),
        }
        for label, values in sorted(lengths.items())
    }


def summarize_field(
    field: str,
    rows: list[dict[str, str]],
    values: dict[str, str],
) -> dict[str, Any]:
    require(set(values) == {row["episode_id"] for row in rows}, "value coverage")
    counts = Counter(values.values())
    by_policy: dict[str, Counter[str]] = defaultdict(Counter)
    by_date: dict[str, Counter[str]] = defaultdict(Counter)
    episodes_by_value: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        label = values[row["episode_id"]]
        by_policy[row["policy_model"]][label] += 1
        by_date[row["utc_date"]][label] += 1
        episodes_by_value[label].add(row["episode_id"])
    ordered = sorted(
        rows, key=lambda row: (int(row["created_ts_ns"]), row["episode_id"])
    )
    states_by_policy = {
        policy: set(policy_counts)
        for policy, policy_counts in by_policy.items()
    }
    nonmissing = {label for label in counts if label != MISSING}
    source_identity = False
    conditions = {
        "source_defines_execution_or_physical_instance_identity": source_identity,
        "at_least_two_nonmissing_values": len(nonmissing) >= 2,
        "not_deterministic_function_of_policy": any(
            len(states) > 1 for states in states_by_policy.values()
        ),
        "populated_for_every_episode": counts.get(MISSING, 0) == 0,
        "source_supports_cluster_equality_semantics": source_identity,
    }
    return {
        "field": field,
        "missing_count": counts.get(MISSING, 0),
        "nonmissing_count": len(rows) - counts.get(MISSING, 0),
        "literal_value_counts": dict(sorted(counts.items())),
        "episode_set_sha256_by_value": {
            label: episode_set_hash(episode_ids)
            for label, episode_ids in sorted(episodes_by_value.items())
        },
        "by_policy": {
            policy: dict(sorted(policy_counts.items()))
            for policy, policy_counts in sorted(by_policy.items())
        },
        "by_utc_date": {
            date: dict(sorted(date_counts.items()))
            for date, date_counts in sorted(by_date.items())
        },
        "chronological_runs": run_summary(
            [values[row["episode_id"]] for row in ordered]
        ),
        "qualification_conditions": conditions,
        "qualifies_as_operational_cluster": all(conditions.values()),
    }


def build() -> dict[str, Any]:
    require(sha256(H193_RESULT) == H193_RESULT_SHA256, "H193 result drifted")
    rows = h193.load_cohort()
    values_by_field = {field: {} for field in FIELDS}
    for row in rows:
        static_hash = row["static_sha256"]
        source = h193.CACHE / f"{static_hash}.json"
        require(source.is_file(), "verified static cache entry missing")
        raw = source.read_bytes()
        require(sha256_bytes(raw) == static_hash, "static cache hash mismatch")
        data = json.loads(raw)
        require(isinstance(data, dict), "static root is not an object")
        for field in FIELDS:
            values_by_field[field][row["episode_id"]] = literal_value(data, field)
    field_rows = [
        summarize_field(field, rows, values_by_field[field]) for field in FIELDS
    ]
    any_qualified = any(row["qualifies_as_operational_cluster"] for row in field_rows)
    return {
        "schema": "h194-phail-server-field-semantics-v1",
        "protocol_sha256": sha256(PROTOCOL),
        "h193_result_sha256": sha256(H193_RESULT),
        "h187_input_sha256": sha256(h193.INPUT),
        "source_commit": SOURCE_COMMIT,
        "source_records": verify_sources(),
        "fixed_fields": list(FIELDS),
        "episode_count": len(rows),
        "result_exposed": True,
        "performance_field_opened": False,
        "field_results": field_rows,
        "disposition": (
            "operational_cluster_candidate_found"
            if any_qualified
            else "infrastructure_configuration_not_session_identity"
        ),
        "scope": (
            "exhaustive result-exposed census of two fixed nonperformance "
            "server configuration fields; no session or exchangeability "
            "inference without the fixed qualification rule"
        ),
    }


def validate(result: dict[str, Any]) -> None:
    require(
        set(result)
        == {
            "schema",
            "protocol_sha256",
            "h193_result_sha256",
            "h187_input_sha256",
            "source_commit",
            "source_records",
            "fixed_fields",
            "episode_count",
            "result_exposed",
            "performance_field_opened",
            "field_results",
            "disposition",
            "scope",
        },
        "top-level output schema",
    )
    require(result.get("schema") == "h194-phail-server-field-semantics-v1", "schema")
    require(result.get("protocol_sha256") == sha256(PROTOCOL), "protocol hash")
    require(result.get("h193_result_sha256") == H193_RESULT_SHA256, "H193 hash")
    require(result.get("h187_input_sha256") == h193.INPUT_SHA256, "H187 hash")
    require(result.get("source_commit") == SOURCE_COMMIT, "source commit")
    require(result.get("fixed_fields") == list(FIELDS), "field drift")
    require(result.get("episode_count") == h193.EXPECTED_EPISODES, "episodes")
    require(result.get("result_exposed") is True, "exposure status")
    require(result.get("performance_field_opened") is False, "performance field")
    source_records = result.get("source_records")
    require(
        isinstance(source_records, list)
        and len(source_records) == len(SOURCE_FILES)
        and all(
            set(row) == {"path", "sha256", "lines", "supports"}
            for row in source_records
        ),
        "source record schema",
    )
    require(source_records == verify_sources(), "source records changed")
    rows = result.get("field_results")
    require(isinstance(rows, list) and len(rows) == 2, "field rows")
    require([row["field"] for row in rows] == list(FIELDS), "field order")
    field_keys = {
        "field",
        "missing_count",
        "nonmissing_count",
        "literal_value_counts",
        "episode_set_sha256_by_value",
        "by_policy",
        "by_utc_date",
        "chronological_runs",
        "qualification_conditions",
        "qualifies_as_operational_cluster",
    }
    qualification_keys = {
        "source_defines_execution_or_physical_instance_identity",
        "at_least_two_nonmissing_values",
        "not_deterministic_function_of_policy",
        "populated_for_every_episode",
        "source_supports_cluster_equality_semantics",
    }
    run_keys = {
        "run_count",
        "run_lengths",
        "minimum_run_length",
        "maximum_run_length",
    }
    cohort_rows = h193.load_cohort()
    expected_policies = {row["policy_model"] for row in cohort_rows}
    expected_dates = {row["utc_date"] for row in cohort_rows}
    require(
        all(
            set(row) == field_keys
            and set(row["qualification_conditions"]) == qualification_keys
            and set(row["by_policy"]) == expected_policies
            and set(row["by_utc_date"]) == expected_dates
            and set(row["episode_set_sha256_by_value"])
            == set(row["literal_value_counts"])
            and set(row["chronological_runs"])
            == set(row["literal_value_counts"])
            and all(
                set(counts).issubset(row["literal_value_counts"])
                and sum(counts.values())
                == sum(
                    1
                    for cohort_row in cohort_rows
                    if cohort_row["policy_model"] == policy
                )
                for policy, counts in row["by_policy"].items()
            )
            and all(
                set(counts).issubset(row["literal_value_counts"])
                and sum(counts.values())
                == sum(
                    1
                    for cohort_row in cohort_rows
                    if cohort_row["utc_date"] == date
                )
                for date, counts in row["by_utc_date"].items()
            )
            and all(
                set(run_record) == run_keys
                and run_record["run_count"] == len(run_record["run_lengths"])
                and sum(run_record["run_lengths"]) > 0
                and min(run_record["run_lengths"]) == run_record["minimum_run_length"]
                and max(run_record["run_lengths"]) == run_record["maximum_run_length"]
                for run_record in row["chronological_runs"].values()
            )
            and sum(
                sum(run_record["run_lengths"])
                for run_record in row["chronological_runs"].values()
            )
            == h193.EXPECTED_EPISODES
            and row["missing_count"] + row["nonmissing_count"] == h193.EXPECTED_EPISODES
            and sum(row["literal_value_counts"].values()) == h193.EXPECTED_EPISODES
            and row["qualifies_as_operational_cluster"]
            == all(row["qualification_conditions"].values())
            for row in rows
        ),
        "field summary integrity",
    )
    expected = (
        "operational_cluster_candidate_found"
        if any(row["qualifies_as_operational_cluster"] for row in rows)
        else "infrastructure_configuration_not_session_identity"
    )
    require(result.get("disposition") == expected, "disposition")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rebuilt = build()
    validate(rebuilt)
    if args.check:
        stored = json.loads(OUTPUT.read_text())
        validate(stored)
        require(stored == rebuilt, "stored result differs from exact rebuild")
        return
    OUTPUT.write_text(json.dumps(rebuilt, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
