#!/usr/bin/env python3
"""Build the repository-owned standalone P1 and P2 packages."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "reproduction"


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--p1-only", action="store_true")
    parser.add_argument("--p2-only", action="store_true")
    args = parser.parse_args()
    if args.p1_only and args.p2_only:
        raise SystemExit("choose at most one of --p1-only and --p2-only")

    if not args.p2_only:
        run(
            [
                sys.executable,
                str(HERE / "build_p1_package.py"),
                "--output",
                str(HERE / "p1"),
            ]
        )
    if not args.p1_only:
        run(
            [
                sys.executable,
                str(
                    ROOT
                    / "research"
                    / "prospective-study-design"
                    / "build_p2_reproduction_package.py"
                ),
                "--output",
                str(HERE / "p2"),
            ]
        )


if __name__ == "__main__":
    main()
