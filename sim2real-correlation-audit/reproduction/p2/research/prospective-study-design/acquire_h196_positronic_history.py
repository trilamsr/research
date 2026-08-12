#!/usr/bin/env python3
"""Acquire and verify the exact public Git history required by H196."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FAMILY = ROOT / "research" / "prospective-study-design"
TARGET = ROOT / "work" / "h196-positronic-history"
REMOTE = "https://github.com/Positronic-Robotics/positronic.git"
BASE = "e406176bc526babb06844a48e3627a5c0409eb74"
HEAD = "01b78e6f62ff5913490c360afdd2712eee070524"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(TARGET), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ).stdout


def verify_checkout() -> None:
    require(TARGET.is_dir(), f"H196 source checkout missing: {TARGET}")
    require(git("rev-parse", BASE).strip() == BASE, "H196 baseline commit mismatch")
    require(git("rev-parse", HEAD).strip() == HEAD, "H196 comparison commit mismatch")
    subprocess.run(
        ["git", "-C", str(TARGET), "merge-base", "--is-ancestor", BASE, HEAD],
        check=True,
    )
    require(not git("status", "--porcelain=v1").strip(), "H196 source checkout is dirty")


def fetch() -> None:
    require(not TARGET.exists(), f"refusing to replace existing H196 checkout: {TARGET}")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "clone", "--filter=blob:none", "--no-checkout", REMOTE, str(TARGET)],
        check=True,
    )
    subprocess.run(["git", "-C", str(TARGET), "checkout", "--detach", HEAD], check=True)
    verify_checkout()


def check() -> None:
    verify_checkout()
    subprocess.run(
        [
            sys.executable,
            str(FAMILY / "audit_h196_positronic_session_identity_history.py"),
            "--check",
            "--repository",
            str(TARGET),
        ],
        check=True,
        cwd=ROOT,
    )
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            str(FAMILY / "test_audit_h196_positronic_session_identity_history.py"),
        ],
        check=True,
        cwd=ROOT,
    )
    subprocess.run(
        [
            "node",
            str(FAMILY / "challenge_h196_positronic_session_identity_history.mjs"),
            "--check",
        ],
        check=True,
        cwd=ROOT,
    )
    subprocess.run(
        [
            sys.executable,
            str(FAMILY / "validate_h196_positronic_session_identity_history_challenge.py"),
        ],
        check=True,
        cwd=ROOT,
    )
    print("PASS: exact network-acquired H196 Git history and endpoint trace")


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--fetch", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.fetch:
        fetch()
    else:
        check()


if __name__ == "__main__":
    main()
