from __future__ import annotations

import pytest

from compare_json_numeric import compare


def test_float_roundoff_is_tolerated() -> None:
    compare({"value": 1.0}, {"value": 1.0 + 5e-13}, atol=1e-12)


def test_integer_float_schema_change_is_rejected() -> None:
    with pytest.raises(AssertionError, match="type int != float"):
        compare({"count": 26}, {"count": 26.0}, atol=1e-12)


def test_categorical_change_is_rejected() -> None:
    with pytest.raises(AssertionError, match="False != True"):
        compare({"passed": False}, {"passed": True}, atol=1e-12)
