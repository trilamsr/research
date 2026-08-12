import json

import pytest

import validate_h238_interior_route_law_nonidentification_challenge as validator


def load() -> dict[str, object]:
    return json.loads(validator.CHALLENGE.read_text(encoding="utf-8"))


def test_canonical_challenge_validates() -> None:
    validator.validate(load())


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("status", "fail"),
        ("classification", "knife_edge_only"),
        ("protocol_sha256", "0" * 64),
        ("repair_protocol_sha256", "0" * 64),
        ("producer_sha256", "0" * 64),
        ("producer_result_sha256", "0" * 64),
        ("mutation_controls_rejected", 3),
    ],
)
def test_mutated_challenge_fails(field: str, value: object) -> None:
    data = load()
    data[field] = value
    with pytest.raises(AssertionError):
        validator.validate(data)


def test_named_mutation_roster_is_required() -> None:
    data = load()
    data["mutation_controls_rejected_names"] = data[
        "mutation_controls_rejected_names"
    ][:-1]
    with pytest.raises(AssertionError):
        validator.validate(data)


def test_exact_census_is_required() -> None:
    data = load()
    data["regret_formula_vertex_checks"] += 1
    with pytest.raises(AssertionError):
        validator.validate(data)
