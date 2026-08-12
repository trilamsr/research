#!/usr/bin/env python3
"""Compare JSON structures exactly except for negligible float roundoff."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


def compare(a: Any, b: Any, path: str = "$", atol: float = 1e-12) -> None:
    if isinstance(a, bool) or isinstance(b, bool):
        if a is not b:
            raise AssertionError(f"{path}: {a!r} != {b!r}")
        return
    if isinstance(a, float) and isinstance(b, float):
        if not math.isclose(float(a), float(b), rel_tol=0.0, abs_tol=atol):
            raise AssertionError(f"{path}: {a!r} != {b!r} (atol={atol})")
        return
    if type(a) is not type(b):
        raise AssertionError(f"{path}: type {type(a).__name__} != {type(b).__name__}")
    if isinstance(a, dict):
        if a.keys() != b.keys():
            raise AssertionError(f"{path}: keys differ")
        for key in a:
            compare(a[key], b[key], f"{path}.{key}", atol)
        return
    if isinstance(a, list):
        if len(a) != len(b):
            raise AssertionError(f"{path}: lengths {len(a)} != {len(b)}")
        for index, (left, right) in enumerate(zip(a, b)):
            compare(left, right, f"{path}[{index}]", atol)
        return
    if a != b:
        raise AssertionError(f"{path}: {a!r} != {b!r}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("reference", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--atol", type=float, default=1e-12)
    args = parser.parse_args()
    left = json.loads(args.reference.read_text(encoding="utf-8"))
    right = json.loads(args.candidate.read_text(encoding="utf-8"))
    compare(left, right, atol=args.atol)
    print(f"OK: {args.reference.name} matches numerically within {args.atol:g}")


if __name__ == "__main__":
    main()
