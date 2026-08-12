from __future__ import annotations

import csv
import io
import math

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

import acquire_h202_phail_initial_joint_state as h202


def cohort_row(episode_id: str) -> dict[str, str]:
    parent = f"phail/v1.0/dataset/rollouts/000000000000/{episode_id}"
    return {
        "episode_id": episode_id,
        "meta_source_path": f"{parent}/meta.json",
    }


def inventory_rows(episode_id: str) -> list[dict[str, object]]:
    parent = f"phail/v1.0/dataset/rollouts/000000000000/{episode_id}"
    return [
        {
            "key": f"{parent}/{signal}.parquet",
            "etag": str(index) * 32,
            "size": index,
        }
        for index, signal in enumerate(h202.SIGNALS, 1)
    ]


def test_selector_requires_exact_pair_and_root() -> None:
    cohort = [cohort_row("000000000001")]
    inventory = inventory_rows("000000000001")
    assert h202.select_sources(cohort, inventory)[0]["episode_id"] == "000000000001"
    with pytest.raises(ValueError, match="count"):
        h202.select_sources(cohort, inventory[:-1])
    with pytest.raises(ValueError, match="count"):
        h202.select_sources(cohort, inventory + [inventory[0]])


def write_signal(path, values, timestamps=None, reversed_columns=False) -> None:
    timestamps = timestamps or list(range(100, 100 + len(values)))
    arrays = {
        "timestamp": pa.array(timestamps, type=pa.int64()),
        "value": pa.array(values),
    }
    names = ["value", "timestamp"] if reversed_columns else ["timestamp", "value"]
    pq.write_table(pa.table({name: arrays[name] for name in names}), path)


def test_first_q_and_error_sample_only(tmp_path) -> None:
    q_path = tmp_path / "q.parquet"
    error_path = tmp_path / "error.parquet"
    first = [0.1 * i for i in range(7)]
    sentinel = [999.0] * 7
    write_signal(q_path, [first, sentinel])
    write_signal(error_path, [0, 1])
    q = h202.first_sample(q_path, "robot_state.q")
    error = h202.first_sample(error_path, "robot_state.error")
    assert q["value"] == first
    assert 999.0 not in q["value"]
    assert q["row_count"] == 2
    assert error["value"] == 0


def test_reordered_columns_are_addressed_by_name(tmp_path) -> None:
    path = tmp_path / "q.parquet"
    write_signal(path, [[0.0] * 7], reversed_columns=True)
    assert h202.first_sample(path, "robot_state.q")["value"] == [0.0] * 7


@pytest.mark.parametrize(
    "values,match",
    [
        ([[0.0] * 6], "dimension"),
        ([[0.0] * 6 + [math.nan]], "finite"),
        ([[0.0] * 6 + [math.inf]], "finite"),
    ],
)
def test_bad_q_fails(tmp_path, values, match) -> None:
    path = tmp_path / "q.parquet"
    write_signal(path, values)
    with pytest.raises(ValueError, match=match):
        h202.first_sample(path, "robot_state.q")


@pytest.mark.parametrize("value", [-1, 2, True, 0.5])
def test_bad_error_fails(tmp_path, value) -> None:
    path = tmp_path / "error.parquet"
    write_signal(path, [value])
    with pytest.raises(ValueError, match="error"):
        h202.first_sample(path, "robot_state.error")


def test_empty_file_fails(tmp_path) -> None:
    path = tmp_path / "empty.parquet"
    pq.write_table(
        pa.table(
            {
                "timestamp": pa.array([], type=pa.int64()),
                "value": pa.array([], type=pa.float64()),
            }
        ),
        path,
    )
    with pytest.raises(ValueError, match="empty"):
        h202.first_sample(path, "robot_state.q")


def test_timestamp_mismatch_fails() -> None:
    with pytest.raises(ValueError, match="timestamp mismatch"):
        h202.require_aligned(
            "episode",
            {"timestamp_ns": 1},
            {"timestamp_ns": 2},
        )


def test_render_is_stable_lf_csv() -> None:
    row = {field: "" for field in h202.PROJECTION_FIELDS}
    text = h202.render([row], h202.PROJECTION_FIELDS)
    assert "\r" not in text
    parsed = list(csv.DictReader(io.StringIO(text)))
    assert parsed == [row]
