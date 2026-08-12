#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path

root = Path(__file__).resolve().parent
sources = [
    root / "PAPER.md",
    root / "research/claim-evidence-synthesis/result-quantitative-supplement.md",
]
missing = []
for source in sources:
    text = source.read_text(encoding="utf-8")
    for relative in re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", text):
        if not (root / relative).is_file():
            missing.append(f"{source.relative_to(root)} -> {relative}")
if missing:
    raise SystemExit("missing manuscript dependencies:\n- " + "\n- ".join(missing))
print("OK: manuscript-local file references resolve inside the package")
