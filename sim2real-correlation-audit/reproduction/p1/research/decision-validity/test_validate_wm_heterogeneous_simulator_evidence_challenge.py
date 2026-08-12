import json

import pytest

import validate_wm_heterogeneous_simulator_evidence_challenge as validator


def load() -> dict[str, object]:
    return json.loads(validator.CHALLENGE.read_text(encoding="utf-8"))


def test_canonical_challenge_validates() -> None:
    validator.validate(load())


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("status", "fail"),
        ("draws_per_scenario", 1),
        ("tolerance", 1.0),
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
