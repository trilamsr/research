#!/usr/bin/env python3
"""Exact H188 minimax theorem for arbitrary positive reference weights."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


FAMILY = Path(__file__).resolve().parent
PROTOCOL = FAMILY / "protocol-h188-weighted-edge-box-minimax.md"
OUTPUT = FAMILY / "result-h188-weighted-edge-box-minimax.json"
HALF = Fraction(1, 2)
QUARTER = Fraction(1, 4)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fraction(value: Fraction) -> dict[str, Any]:
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "text": f"{value.numerator}/{value.denominator}",
        "decimal": float(value),
    }


def normalize(raw: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    require(len(raw) >= 3, "at least three policies required")
    require(all(value > 0 for value in raw), "reference weights must be positive")
    total = sum(raw)
    return tuple(value / total for value in raw)


def validate_lottery(p: tuple[Fraction, ...], k: int) -> None:
    require(len(p) == k, "lottery length changed")
    require(all(value >= 0 for value in p), "negative lottery mass")
    require(sum(p) == 1, "lottery does not sum to one")


def weighted_formula_regret(
    raw_reference: tuple[Fraction, ...], p: tuple[Fraction, ...]
) -> Fraction:
    r = normalize(raw_reference)
    validate_lottery(p, len(r))
    objectives = []
    for winner in range(len(r)):
        dispersion = sum(
            abs(r[j] * p[i] - r[i] * p[j])
            for i, j in itertools.combinations(range(len(r)), 2)
            if i != winner and j != winner
        )
        objectives.append(1 - p[winner] + dispersion)
    return max(objectives) / 4


def minimax_segment(raw_reference: tuple[Fraction, ...]) -> dict[str, Any]:
    r = normalize(raw_reference)
    order = sorted(range(len(r)), key=lambda index: (r[index], index))
    first, second, third = order[:3]
    a, b, g = r[first], r[second], r[third]
    return {
        "reference": r,
        "order": tuple(order),
        "first": first,
        "second": second,
        "a": a,
        "b": b,
        "g": g,
        "h_min": Fraction(),
        "h_max": (g - b) / 2,
        "value": (2 - a - b) / 8,
    }


def segment_lottery(
    raw_reference: tuple[Fraction, ...], h: Fraction
) -> tuple[Fraction, ...]:
    info = minimax_segment(raw_reference)
    require(info["h_min"] <= h <= info["h_max"], "h outside minimizer segment")
    r = info["reference"]
    first, second = info["first"], info["second"]
    a, b = info["a"], info["b"]
    complement = 1 - a - b
    p = [Fraction() for _ in r]
    p[first] = (a + b) / 2 + h
    p[second] = b * (2 - a - b) / (2 * (1 - a))
    p[second] += (1 - b) * h / (1 - a)
    multiplier = (2 - a - b) / (1 - a) * (HALF - h / complement)
    for index in range(len(r)):
        if index not in (first, second):
            p[index] = r[index] * multiplier
    result = tuple(p)
    validate_lottery(result, len(r))
    return result


def endpoint_policy_values(
    r: tuple[Fraction, ...], signs: tuple[int, ...]
) -> tuple[Fraction, ...]:
    k = len(r)
    edges = tuple(itertools.combinations(range(k), 2))
    require(len(signs) == len(edges), "endpoint sign count changed")
    q = [[HALF for _ in range(k)] for _ in range(k)]
    for (i, j), sign in zip(edges, signs):
        q[i][j] = HALF + sign * QUARTER
        q[j][i] = 1 - q[i][j]
    return tuple(sum(r[j] * q[i][j] for j in range(k)) for i in range(k))


def enumerated_weighted_regret(
    raw_reference: tuple[Fraction, ...], p: tuple[Fraction, ...]
) -> Fraction:
    r = normalize(raw_reference)
    validate_lottery(p, len(r))
    edges = tuple(itertools.combinations(range(len(r)), 2))
    worst = Fraction()
    for signs in itertools.product((-1, 1), repeat=len(edges)):
        values = endpoint_policy_values(r, signs)
        regret = max(values) - sum(prob * value for prob, value in zip(p, values))
        worst = max(worst, regret)
    return worst


def cases() -> tuple[tuple[Fraction, ...], ...]:
    return (
        (Fraction(1), Fraction(1), Fraction(1)),
        (Fraction(1), Fraction(2), Fraction(3)),
        (Fraction(1), Fraction(2), Fraction(3), Fraction(4)),
        (Fraction(1), Fraction(3), Fraction(3), Fraction(3)),
        (Fraction(1), Fraction(1), Fraction(2), Fraction(4)),
        (Fraction(1), Fraction(2), Fraction(2), Fraction(5), Fraction(7)),
    )


def build() -> dict[str, Any]:
    rows = []
    for raw in cases():
        info = minimax_segment(raw)
        probes = sorted({info["h_min"], info["h_max"], (info["h_min"] + info["h_max"]) / 2})
        probe_rows = []
        for h in probes:
            p = segment_lottery(raw, h)
            formula = weighted_formula_regret(raw, p)
            require(formula == info["value"], "segment formula value changed")
            enumerated = (
                enumerated_weighted_regret(raw, p) if len(raw) <= 5 else None
            )
            if enumerated is not None:
                require(enumerated == formula, "raw endpoint oracle disagrees")
            probe_rows.append(
                {
                    "h": fraction(h),
                    "lottery": [fraction(value) for value in p],
                    "formula_regret": fraction(formula),
                    "endpoint_regret": (
                        fraction(enumerated) if enumerated is not None else None
                    ),
                }
            )
        rows.append(
            {
                "reference": [fraction(value) for value in normalize(raw)],
                "value": fraction(info["value"]),
                "h_interval": [fraction(info["h_min"]), fraction(info["h_max"])],
                "unique": info["h_min"] == info["h_max"],
                "probes": probe_rows,
            }
        )
    counterexample_raw = (
        Fraction(1, 10),
        Fraction(1, 5),
        Fraction(3, 10),
        Fraction(2, 5),
    )
    counterexample_h = Fraction(1, 40)
    counterexample_p = segment_lottery(counterexample_raw, counterexample_h)
    return {
        "schema": "h188-weighted-edge-box-minimax-v1",
        "protocol_sha256": sha256(PROTOCOL),
        "closed_form": {
            "value": "(2-r_(1)-r_(2))/8",
            "minimizer_set": "closed h-segment in protocol",
            "water_filling_endpoint": "h=0",
            "uniqueness_condition": "r_(2)=r_(3)",
            "uniform_reduction": "(K-1)/(4K), uniquely uniform",
        },
        "cases": rows,
        "nonuniqueness_counterexample": {
            "reference": [fraction(value) for value in counterexample_raw],
            "h": fraction(counterexample_h),
            "lottery": [fraction(value) for value in counterexample_p],
            "regret": fraction(
                weighted_formula_regret(counterexample_raw, counterexample_p)
            ),
            "strong_water_filling_uniqueness_conjecture": "rejected",
        },
        "scope": (
            "one weighted-Borda full compatible edge box; not every observed "
            "law, empirical roster, or realized-policy guarantee"
        ),
    }


def validate(data: dict[str, Any]) -> None:
    require(data.get("schema") == "h188-weighted-edge-box-minimax-v1", "schema")
    require(data.get("protocol_sha256") == sha256(PROTOCOL), "protocol hash")
    require(
        data["nonuniqueness_counterexample"][
            "strong_water_filling_uniqueness_conjecture"
        ]
        == "rejected",
        "counterexample disposition",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    require(args.write != args.check, "choose exactly one of --write/--check")
    if args.check:
        validate(json.loads(OUTPUT.read_text()))
        require(json.loads(OUTPUT.read_text()) == build(), "result drift")
        return
    result = build()
    validate(result)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
