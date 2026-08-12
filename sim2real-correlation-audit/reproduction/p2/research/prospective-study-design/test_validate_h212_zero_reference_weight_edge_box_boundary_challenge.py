import copy
import json

import pytest

import validate_h212_zero_reference_weight_edge_box_boundary_challenge as validator


def retained() -> dict:
    return json.loads(validator.CHALLENGE.read_text())


def test_retained_challenge_validates() -> None:
    validator.validate(retained())


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("classification", "value_extends_but_optimizer_face_changes"),
        ("imports_or_executes_producer", True),
        ("protocol_sha256", "0" * 64),
        ("producer_result_sha256", "0" * 64),
    ),
)
def test_top_level_tampering_fails(field: str, value: object) -> None:
    data = retained()
    data[field] = value
    with pytest.raises(ValueError):
        validator.validate(data)


def test_missing_attack_fails() -> None:
    data = retained()
    data["attacks"] = data["attacks"][:-1]
    with pytest.raises(ValueError):
        validator.validate(data)


def test_census_tampering_fails() -> None:
    data = copy.deepcopy(retained())
    data["exact_case_census"]["canonical_cases"] -= 1
    with pytest.raises(ValueError):
        validator.validate(data)


def test_disagreement_fails() -> None:
    data = copy.deepcopy(retained())
    data["producer_agreement"]["uniqueness"] = False
    with pytest.raises(ValueError):
        validator.validate(data)
