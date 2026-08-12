import json

import pytest

import validate_wm_nonlinear_calibration_sensitivity_challenge as validator


def load() -> dict[str, object]:
    return json.loads(validator.CHALLENGE.read_text(encoding="utf-8"))


def test_canonical_challenge_validates() -> None:
    validator.validate(load())


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("status", "fail"),
        ("tolerance", 1),
        ("numeric_comparisons", 0),
        ("protocol_sha256", "0" * 64),
        ("producer_sha256", "0" * 64),
        ("producer_result_sha256", "0" * 64),
        ("input_sha256", "0" * 64),
    ],
)
def test_mutations_fail(field: str, value: object) -> None:
    data = load()
    data[field] = value
    with pytest.raises(AssertionError):
        validator.validate(data)


def test_winner_mutation_fails() -> None:
    data = load()
    data["panels"]["IRASim"]["isotonic_winner"] = "Octo-Base"
    with pytest.raises(AssertionError):
        validator.validate(data)
