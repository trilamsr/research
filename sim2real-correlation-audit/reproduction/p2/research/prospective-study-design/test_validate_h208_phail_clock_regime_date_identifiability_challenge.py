from __future__ import annotations

import json

import validate_h208_phail_clock_regime_date_identifiability_challenge as validator


def test_independent_challenge_validates() -> None:
    producer = json.loads(validator.PRODUCER.read_text())
    challenge = json.loads(validator.CHALLENGE.read_text())
    validator.validate(producer, challenge)


def test_all_mutation_attacks_fail_closed() -> None:
    producer = json.loads(validator.PRODUCER.read_text())
    challenge = json.loads(validator.CHALLENGE.read_text())
    assert all(validator.mutation_attacks(producer, challenge).values())
