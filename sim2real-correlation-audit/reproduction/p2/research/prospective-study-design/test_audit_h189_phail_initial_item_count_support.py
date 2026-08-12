import json
from fractions import Fraction

import pytest

import audit_h189_phail_initial_item_count_support as h189


def test_sanitizer_retains_only_baseline_item_count() -> None:
    meta = {"created_ts_ns": 1_700_000_000_000_000_000, "duration_ns": 999}
    static = {
        "model": "act",
        "variant": "checkpoint",
        "task": "task",
        "eval.object": "object",
        "eval.tote_placement": "left",
        "eval.external_camera": "right",
        "eval.total_items": 8,
        "eval.successful_items": 7,
        "eval.outcome": "forbidden",
        "eval.duration": 12,
        "eval.notes": "forbidden",
    }
    payloads = {
        f"{h189.h187.ENDPOINT}/meta": json.dumps(meta).encode(),
        f"{h189.h187.ENDPOINT}/static": json.dumps(static).encode(),
    }
    row = h189.sanitize_episode(
        "episode", "partition", "meta", "static", fetch=payloads.__getitem__
    )
    assert tuple(row) == h189.ALLOWED_FIELDS
    assert row["initial_item_count"] == 8
    assert not {
        "eval.successful_items",
        "eval.outcome",
        "eval.duration",
        "eval.notes",
        "duration_ns",
    } & set(row)


@pytest.mark.parametrize("value", [None, True, False, 0, -1, 1.5, "8"])
def test_invalid_item_count_fails(value) -> None:
    with pytest.raises(ValueError):
        h189.parse_item_count(value)


def test_integral_float_is_canonicalized() -> None:
    assert h189.parse_item_count(8.0) == 8


def test_cell_summary_and_narrowing_known_answer(monkeypatch) -> None:
    rows = []
    for policy in h189.POLICIES:
        rows.append(
            {
                **{field: "x" for field in h189.ALLOWED_FIELDS},
                "policy_model": policy,
                "initial_item_count": 4,
                "utc_date": "2026-01-01",
            }
        )
    rows.append(
        {
            **{field: "x" for field in h189.ALLOWED_FIELDS},
            "policy_model": "act",
            "initial_item_count": 8,
            "utc_date": "2026-01-01",
        }
    )
    cells = h189.cell_summary(
        rows, ("utc_date", "initial_item_count")
    )
    assert len(cells) == 2
    assert cells[0]["minimum_policy_count"] == 1
    assert cells[1]["minimum_policy_count"] == 0


def test_fraction_reduction_for_comparison() -> None:
    value = Fraction(6, 8)
    assert (value.numerator, value.denominator) == (3, 4)


def test_h187_projection_mismatch_fails(monkeypatch) -> None:
    row = {field: None for field in h189.ALLOWED_FIELDS}
    row["episode_id"] = "one"
    monkeypatch.setattr(
        h189.h187,
        "load_sanitized",
        lambda: [{field: ("different" if field == "episode_id" else None)
                  for field in h189.h187.ALLOWED_FIELDS}],
    )
    with pytest.raises(ValueError):
        h189.assert_exact_h187_projection([row])


def test_inventory_manifest_algorithm_known_answer() -> None:
    inventory = [
        {"key": "b", "size": 2, "etag": "y", "last_modified": "t2"},
        {"key": "a", "size": 1, "etag": "x", "last_modified": "t1"},
    ]
    expected = h189.sha256_bytes(b"a\t1\tx\tt1\nb\t2\ty\tt2\n")
    assert h189.inventory_manifest_sha256(inventory) == expected
