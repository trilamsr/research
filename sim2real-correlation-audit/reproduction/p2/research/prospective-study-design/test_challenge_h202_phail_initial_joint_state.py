from __future__ import annotations

import copy
import json

import pytest

import challenge_h202_phail_initial_joint_state as challenge


def canonical() -> dict:
    return json.loads(challenge.OUTPUT.read_text())


def test_canonical_challenge_validates() -> None:
    challenge.validate(canonical())


@pytest.mark.parametrize(
    ("path", "value", "message"),
    [
        (("projection_exactly_confirmed",), False, "projection confirmation"),
        (("fixed_summary_confirmed",), False, "summary confirmation"),
        (("later_rows_summarized",), True, "later rows"),
        (("result",), "fail", "result"),
        (
            ("classification_confirmed",),
            "partial_initial_joint_state_reconstruction",
            "classification",
        ),
    ],
)
def test_scope_and_result_attacks_fail(
    path: tuple[str, ...], value: object, message: str
) -> None:
    result = copy.deepcopy(canonical())
    result[path[0]] = value
    with pytest.raises(ValueError, match=message):
        challenge.validate(result)


def test_numeric_tolerance_attack_fails() -> None:
    result = copy.deepcopy(canonical())
    result["maximum_absolute_summary_difference"] = (
        result["absolute_tolerance"] * 2
    )
    with pytest.raises(ValueError, match="summary"):
        challenge.validate(result)


def test_source_count_attack_fails() -> None:
    result = copy.deepcopy(canonical())
    result["integrity"]["source_object_count"] -= 1
    with pytest.raises(ValueError, match="objects"):
        challenge.validate(result)
