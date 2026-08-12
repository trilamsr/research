#!/usr/bin/env python3
from __future__ import annotations
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parent
manifest = root / "SOURCE-MANIFEST.sha256"
listed = []
for line in manifest.read_text(encoding="utf-8").splitlines():
    digest, relative = line.split("  ", 1)
    path = root / relative
    if not path.is_file():
        raise SystemExit(f"missing: {relative}")
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise SystemExit(f"hash mismatch: {relative}")
    listed.append(relative.removeprefix("./"))
if len(listed) != len(set(listed)):
    raise SystemExit("duplicate manifest path")
ignored = {".venv", ".pytest_cache", "work"}
actual = set()
for path in root.rglob("*"):
    if not path.is_file() or path.name == manifest.name:
        continue
    relative = path.relative_to(root)
    if relative.parts[0] in ignored or "__pycache__" in relative.parts:
        continue
    if relative.suffix == ".pyc":
        continue
    actual.add(relative.as_posix())
if actual != set(listed):
    raise SystemExit(
        f"inventory mismatch; missing={sorted(set(listed)-actual)}; "
        f"unexpected={sorted(actual-set(listed))}"
    )
print(f"OK: {len(listed)} package files match SOURCE-MANIFEST.sha256")
