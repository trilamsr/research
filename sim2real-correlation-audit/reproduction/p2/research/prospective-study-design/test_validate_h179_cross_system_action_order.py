import copy

import pytest

import validate_h179_cross_system_action_order as h179


def load_pair():
    return h179.load_pair() if hasattr(h179, "load_pair") else (
        __import__("json").loads(h179.CHALLENGE.read_text()),
        __import__("json").loads(h179.PRODUCER.read_text()),
    )


def test_canonical_h179_challenge_passes():
    challenge, producer = load_pair()
    h179.validate(challenge, producer)


@pytest.mark.parametrize(
    "field,value",
    [
        ("decision", "no_second_instantiation_in_bounded_frame"),
        ("positive_contrast_strength", "artifact_reproduced"),
        ("outcome_fields_accessed_or_used", True),
        ("disposition", "fail"),
    ],
)
def test_material_challenge_mutations_fail(field, value):
    challenge, producer = load_pair()
    attacked = copy.deepcopy(challenge)
    attacked[field] = value
    with pytest.raises(ValueError):
        h179.validate(attacked, producer)
