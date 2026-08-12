from __future__ import annotations
import subprocess
import sys
from pathlib import Path


def test_manifest_rejects_a_mutated_file(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parent
    (tmp_path / "verify_manifest.py").write_bytes((root / "verify_manifest.py").read_bytes())
    (tmp_path / "payload.txt").write_text("mutated", encoding="utf-8")
    (tmp_path / "SOURCE-MANIFEST.sha256").write_text(
        "0" * 64 + "  ./payload.txt\n", encoding="utf-8"
    )
    result = subprocess.run(
        [sys.executable, "verify_manifest.py"], cwd=tmp_path, capture_output=True
    )
    assert result.returncode != 0
    assert b"hash mismatch" in result.stderr
