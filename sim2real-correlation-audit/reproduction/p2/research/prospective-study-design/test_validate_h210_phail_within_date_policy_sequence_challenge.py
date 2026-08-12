from __future__ import annotations

import json

import validate_h210_phail_within_date_policy_sequence_challenge as validator


def test_challenge_validates() -> None:
    validator.validate(
        json.loads(validator.PRODUCER.read_text()),
        json.loads(validator.CHALLENGE.read_text()),
    )


def test_mutation_attacks_fail_closed() -> None:
    producer = json.loads(validator.PRODUCER.read_text())
    challenge = json.loads(validator.CHALLENGE.read_text())
    assert all(validator.mutation_attacks(producer, challenge).values())
