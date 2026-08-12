#!/usr/bin/env python3
from __future__ import annotations
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parent
manifest = root / "SOURCE-MANIFEST.sha256"
rows = []
for line in manifest.read_text(encoding="utf-8").splitlines():
    digest, relative = line.split("  ", 1)
    path = root / relative
    if not path.is_file():
        raise SystemExit(f"missing: {relative}")
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != digest:
        raise SystemExit(f"hash mismatch: {relative}")
    rows.append(relative)
if len(rows) != len(set(rows)):
    raise SystemExit("duplicate manifest path")
allowed_roots = {".venv", ".pytest_cache", "work"}
generated_source_paths = {
    "research/prospective-study-design/sources/h162/autoeval-2503.24278v2.pdf",
    "research/prospective-study-design/sources/h162/umi-bench-2606.10382v1.pdf",
    "research/prospective-study-design/sources/h162/robodojo-2607.04434v3.pdf",
    "research/prospective-study-design/sources/h178/2605.27491v1.pdf",
    "research/prospective-study-design/sources/h178/2606.10366v1.pdf",
    "research/prospective-study-design/sources/h178/2607.02642v1.pdf",
}
actual = set()
for path in root.rglob("*"):
    if not path.is_file():
        continue
    relative = path.relative_to(root)
    if relative.name == "SOURCE-MANIFEST.sha256":
        continue
    if relative.parts[0] in allowed_roots:
        continue
    if relative.as_posix() in generated_source_paths:
        continue
    if "__pycache__" in relative.parts or relative.suffix == ".pyc":
        continue
    actual.add(relative.as_posix())
listed = set(rows)
if actual != listed:
    missing = sorted(listed - actual)
    unexpected = sorted(actual - listed)
    raise SystemExit(f"inventory mismatch; missing={missing}; unexpected={unexpected}")
print(f"OK: {len(rows)} package files match SOURCE-MANIFEST.sha256")
