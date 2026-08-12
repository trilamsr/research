#!/usr/bin/env python3
"""Acquire the six exact arXiv PDFs required by the P2 H178 source audit."""

from __future__ import annotations

import argparse
import hashlib
import urllib.request
from pathlib import Path


FAMILY = Path(__file__).resolve().parent
SOURCES = (
    {
        "identity": "AutoEval",
        "version": "2503.24278v2",
        "path": "sources/h162/autoeval-2503.24278v2.pdf",
        "sha256": "734840964f233f46ce2c1b8e64427a9cb65ca140b4152a0c4fd339677fd7e45f",
        "license_uri": "https://arxiv.org/licenses/nonexclusive-distrib/1.0/",
    },
    {
        "identity": "GE-Sim 2.0",
        "version": "2605.27491v1",
        "path": "sources/h178/2605.27491v1.pdf",
        "sha256": "af875445ebe487962e308bbff5e76e19fdcfc57620a50ec6ec9070989cbfe641",
        "license_uri": "https://arxiv.org/licenses/nonexclusive-distrib/1.0/",
    },
    {
        "identity": "A Practical Recipe",
        "version": "2606.10366v1",
        "path": "sources/h178/2606.10366v1.pdf",
        "sha256": "0196e433f9523815aeb0e3151e069a466c614e838bc681883bac52a2d9160ab2",
        "license_uri": "https://arxiv.org/licenses/nonexclusive-distrib/1.0/",
    },
    {
        "identity": "UMI-Bench 1.0",
        "version": "2606.10382v1",
        "path": "sources/h162/umi-bench-2606.10382v1.pdf",
        "sha256": "cd279ae9758460c2b1142b721ce2e0184b8adba755b21dc5319d03918ec90e2b",
        "license_uri": "https://creativecommons.org/licenses/by/4.0/",
    },
    {
        "identity": "GigaWorld-1",
        "version": "2607.02642v1",
        "path": "sources/h178/2607.02642v1.pdf",
        "sha256": "15c685a1cfcd9b88635328b29d62f5cb7c8c55b7e1d12799a5a7a6c33a092a0f",
        "license_uri": "https://creativecommons.org/licenses/by/4.0/",
    },
    {
        "identity": "RoboDojo",
        "version": "2607.04434v3",
        "path": "sources/h162/robodojo-2607.04434v3.pdf",
        "sha256": "e07c215f30169dde6a792c34b046b1f54818d09331763988732dcf9ead89a9d4",
        "license_uri": "https://arxiv.org/licenses/nonexclusive-distrib/1.0/",
    },
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(record: dict[str, str]) -> None:
    destination = FAMILY / record["path"]
    if destination.is_file():
        require(
            sha256_bytes(destination.read_bytes()) == record["sha256"],
            f"existing source drift: {record['path']}",
        )
        return
    request = urllib.request.Request(
        f"https://arxiv.org/pdf/{record['version']}",
        headers={
            "User-Agent": "sim2real-research-audit/1.0 (exact-source acquisition)",
            "Accept": "application/pdf",
        },
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        require(response.status == 200, f"HTTP {response.status}")
        body = response.read()
    require(body.startswith(b"%PDF-"), f"non-PDF response: {record['version']}")
    require(
        sha256_bytes(body) == record["sha256"],
        f"source hash changed: {record['version']}",
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(body)


def validate() -> None:
    require(len(SOURCES) == 6, "source roster")
    require(len({record["path"] for record in SOURCES}) == 6, "duplicate path")
    for record in SOURCES:
        source = FAMILY / record["path"]
        require(source.is_file(), f"source missing: {record['path']}")
        body = source.read_bytes()
        require(body.startswith(b"%PDF-"), f"non-PDF: {record['path']}")
        require(sha256_bytes(body) == record["sha256"], f"hash: {record['path']}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    require(args.fetch != args.check, "choose exactly one of --fetch or --check")
    if args.fetch:
        for record in SOURCES:
            fetch(record)
    validate()
    print("OK: six exact H178 arXiv source PDFs are present and hash-bound")


if __name__ == "__main__":
    main()
