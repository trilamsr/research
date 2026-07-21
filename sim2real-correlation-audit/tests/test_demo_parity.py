"""Parity test: `python correlation_audit.py --demo` reproduces PAPER.md section 2.1.

Section 10's artifact table claims --demo reproduces the two fenced audit
blocks in section 2.1. This test extracts those blocks from PAPER.md and
asserts each appears in the demo stdout byte-for-byte (title line included --
the demo prints the same titles).
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PAPER = ROOT / "PAPER.md"
SCRIPT = ROOT / "correlation_audit.py"


def _paper_2_1_blocks():
    text = PAPER.read_text()
    header = re.search(r"^#{2,}\s.*2\.1\b.*$", text, re.M)
    assert header, "PAPER.md has no section 2.1 header"
    start = header.end()
    nxt = re.search(r"^#{2,}\s", text[start:], re.M)
    section = text[start : start + nxt.start()] if nxt else text[start:]
    blocks = re.findall(r"^```[^\n]*\n(.*?)^```\s*$", section, re.M | re.S)
    assert len(blocks) == 2, f"expected 2 fenced blocks in section 2.1, found {len(blocks)}"
    return [b.rstrip("\n") for b in blocks]


@pytest.fixture(scope="module")
def demo_stdout():
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--demo"],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert proc.returncode == 0, f"--demo exited {proc.returncode}: {proc.stderr}"
    return proc.stdout


def _demo_audit_chunks(stdout):
    # The demo separates its audit reports with full-width rule lines.
    chunks = re.split(r"^─+$", stdout, flags=re.M)
    # First two chunks are the RoboWorld and Digital Cousins reports;
    # the last is the closing commentary.
    assert len(chunks) >= 3, "demo output does not contain two rule-separated reports"
    return [c.strip("\n") for c in chunks[:2]]


def test_demo_reproduces_paper_2_1_byte_for_byte(demo_stdout):
    paper_blocks = _paper_2_1_blocks()
    demo_chunks = _demo_audit_chunks(demo_stdout)
    for i, (paper, demo) in enumerate(zip(paper_blocks, demo_chunks)):
        assert demo == paper, (
            f"block {i} differs between --demo output and PAPER.md section 2.1\n"
            f"--- demo ---\n{demo}\n--- paper ---\n{paper}"
        )


def test_paper_blocks_appear_verbatim_in_demo(demo_stdout):
    # Stronger form: each fenced block is a literal substring of the raw stdout.
    for i, block in enumerate(_paper_2_1_blocks()):
        assert block in demo_stdout, f"paper block {i} not found verbatim in demo stdout"
