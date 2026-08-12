#!/usr/bin/env python3
"""Build and verify the standalone P1 reproduction package."""

from __future__ import annotations

import argparse
from datetime import date
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP = (
    ROOT
    / "research"
    / "claim-evidence-synthesis"
    / "result-p1-package-content-map.json"
)
DEFAULT_OUTPUT = ROOT / "reproduction" / "p1"


README = """# P1 reproduction package

This standalone package reproduces the paper-facing results for **What Does a
Sim-to-Real Correlation Support?** from the retained audit records and derived
coordinates.

The package has three evidence boundaries:

1. It regenerates the manuscript's selected audit facts, decision results,
   tables, figures, sensitivities, and PDFs from retained inputs.
2. Figure-derived CSVs are retained derived inputs. Exact extraction can be
   rerun only where the corresponding extractor and public source asset are
   included.
3. It does not rerun the surveyed robot experiments, simulator training, or
   upstream policy evaluations.

## Reproduce

Python 3.12 is required. Node and Ruby are used by method-distinct challenge
implementations. Pandoc 3.10, Tectonic 0.16.9, and Poppler's `pdfunite` are
required to rebuild the PDFs.

```bash
make install
make verify
```

`SOURCE-MANIFEST.sha256` binds every distributed file. The complete-package
reader is `output/pdf/PAPER-with-supplement.pdf`.
"""


MAKEFILE = r"""PYTHON ?= python3.12
PY := .venv/bin/python
PIP := .venv/bin/pip
WORK := work/verification
CORPUS := research/corpus-reporting-audit
DECISION := research/decision-validity
SYNTHESIS := research/claim-evidence-synthesis
NOISE := research/real2sim-noise-floor

.PHONY: install manifest paths test paper-results paper-figures decisions pdf verify clean

install:
	$(PYTHON) -m venv .venv
	$(PIP) install -q -r requirements-lock.txt

manifest:
	$(PYTHON) verify_manifest.py

paths:
	$(PY) verify_package_paths.py

test:
	$(PY) -m pytest -q research test_verify_manifest.py

paper-results:
	mkdir -p $(WORK)
	$(PY) $(SYNTHESIS)/synthesize_paper_evidence.py \
		--out $(WORK)/result-paper-evidence.json \
		--supplement $(WORK)/result-quantitative-supplement.md \
		--main-tables $(WORK)/result-main-tables.md
	$(PY) $(NOISE)/compare_json_numeric.py \
		$(SYNTHESIS)/result-paper-evidence.json \
		$(WORK)/result-paper-evidence.json --atol 1e-12
	cmp $(SYNTHESIS)/result-quantitative-supplement.md \
		$(WORK)/result-quantitative-supplement.md
	cmp $(SYNTHESIS)/result-main-tables.md $(WORK)/result-main-tables.md

paper-figures:
	mkdir -p $(WORK)/figures
	$(PY) $(SYNTHESIS)/generate_paper_figures.py --out-dir $(WORK)/figures
	for stem in figure-worldgym-axis-validity figure-decision-atlas figure-decision-robustness; do \
		$(PY) $(SYNTHESIS)/compare_rendered_png.py \
			$(SYNTHESIS)/$$stem.png $(WORK)/figures/$$stem.png; \
	done

decisions:
	mkdir -p $(WORK)
	$(PY) $(DECISION)/audit_reversal_evidence.py \
		--out $(WORK)/result-reversal-evidence.json
	cmp $(DECISION)/result-reversal-evidence.json \
		$(WORK)/result-reversal-evidence.json
	$(PY) $(DECISION)/analyze_decision_confidence.py \
		--out $(WORK)/result-decision-confidence.json
	cmp $(DECISION)/result-decision-confidence.json \
		$(WORK)/result-decision-confidence.json
	$(PY) $(DECISION)/independent_decision_audit.py \
		--out $(WORK)/result-independent-decision-audit.json
	cmp $(DECISION)/result-independent-decision-audit.json \
		$(WORK)/result-independent-decision-audit.json
	$(PY) $(DECISION)/analyze_cosmos_two_sided.py \
		--out $(WORK)/result-cosmos-two-sided.json
	cmp $(DECISION)/result-cosmos-two-sided.json \
		$(WORK)/result-cosmos-two-sided.json
	$(PY) $(DECISION)/analyze_real2sim_two_sided.py \
		--out $(WORK)/result-real2sim-two-sided.json
	cmp $(DECISION)/result-real2sim-two-sided.json \
		$(WORK)/result-real2sim-two-sided.json
	$(PY) $(DECISION)/analyze_wm_missing_simulator_uncertainty.py --check
	node $(DECISION)/challenge_wm_missing_simulator_uncertainty.mjs --check
	$(PY) $(DECISION)/validate_wm_missing_simulator_uncertainty_challenge.py
	$(PY) $(DECISION)/audit_wm_probability_calibration.py --check
	node $(DECISION)/challenge_wm_probability_calibration.mjs --check
	$(PY) $(DECISION)/validate_wm_probability_calibration_challenge.py
	$(PY) $(DECISION)/analyze_wm_heterogeneous_simulator_evidence.py --check
	node $(DECISION)/challenge_wm_heterogeneous_simulator_evidence.mjs --check
	$(PY) $(DECISION)/validate_wm_heterogeneous_simulator_evidence_challenge.py
	$(PY) $(DECISION)/audit_wm_nonlinear_calibration_sensitivity.py --check
	node $(DECISION)/challenge_wm_nonlinear_calibration_sensitivity.mjs --check
	$(PY) $(DECISION)/validate_wm_nonlinear_calibration_sensitivity_challenge.py
	$(PY) $(NOISE)/audit_mmrv_conventions.py

pdf:
	test "$$(pandoc --version | head -1)" = "pandoc 3.10"
	test "$$(tectonic --version)" = "Tectonic 0.16.9"
	test "$$(pdfunite -v 2>&1 | head -1)" = "pdfunite version 26.07.0"
	mkdir -p $(WORK)/pdf
	$(PY) $(SYNTHESIS)/preprocess_paper_pdf.py \
		< PAPER.md | \
		pandoc -f markdown -o $(WORK)/pdf/PAPER.pdf \
			--pdf-engine=tectonic -V geometry:margin=1in -V fontsize=11pt \
			-V header-includes='\usepackage{array,longtable,graphicx}' \
			-V colorlinks=true \
			-V title-meta="What Does a Sim-to-Real Correlation Support?"
	$(PY) $(SYNTHESIS)/preprocess_paper_pdf.py \
		< $(SYNTHESIS)/result-quantitative-supplement.md | \
		pandoc -f markdown -o $(WORK)/pdf/SUPPLEMENT.pdf \
			--pdf-engine=tectonic -V geometry:landscape -V geometry:margin=0.65in \
			-V fontsize=9pt \
			-V header-includes='\usepackage{array,longtable,graphicx}' \
			-V colorlinks=true
	pdfunite \
		$(WORK)/pdf/PAPER.pdf \
		$(WORK)/pdf/SUPPLEMENT.pdf \
		$(WORK)/pdf/PAPER-with-supplement.pdf
	for name in PAPER; do \
		pdftotext $$name.pdf $(WORK)/pdf/$$name.canonical.txt; \
		pdftotext $(WORK)/pdf/$$name.pdf $(WORK)/pdf/$$name.rebuilt.txt; \
		cmp $(WORK)/pdf/$$name.canonical.txt $(WORK)/pdf/$$name.rebuilt.txt; \
	done
	for name in SUPPLEMENT PAPER-with-supplement; do \
		pdftotext output/pdf/$$name.pdf $(WORK)/pdf/$$name.canonical.txt; \
		pdftotext $(WORK)/pdf/$$name.pdf $(WORK)/pdf/$$name.rebuilt.txt; \
		cmp $(WORK)/pdf/$$name.canonical.txt $(WORK)/pdf/$$name.rebuilt.txt; \
	done

verify: manifest paths test paper-results paper-figures decisions pdf
	@echo "ALL P1 PACKAGE CHECKS PASSED."

clean:
	rm -rf .venv .pytest_cache work
	find research -type d -name __pycache__ -prune -exec rm -rf {} +
"""


MANIFEST_VERIFIER = """#!/usr/bin/env python3
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
"""


PATH_VERIFIER = """#!/usr/bin/env python3
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
    for relative in re.findall(r"\\\\includegraphics(?:\\[[^]]*\\])?\\{([^}]+)\\}", text):
        if not (root / relative).is_file():
            missing.append(f"{source.relative_to(root)} -> {relative}")
if missing:
    raise SystemExit("missing manuscript dependencies:\\n- " + "\\n- ".join(missing))
print("OK: manuscript-local file references resolve inside the package")
"""


MANIFEST_TEST = """from __future__ import annotations
import subprocess
import sys
from pathlib import Path


def test_manifest_rejects_a_mutated_file(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parent
    (tmp_path / "verify_manifest.py").write_bytes((root / "verify_manifest.py").read_bytes())
    (tmp_path / "payload.txt").write_text("mutated", encoding="utf-8")
    (tmp_path / "SOURCE-MANIFEST.sha256").write_text(
        "0" * 64 + "  ./payload.txt\\n", encoding="utf-8"
    )
    result = subprocess.run(
        [sys.executable, "verify_manifest.py"], cwd=tmp_path, capture_output=True
    )
    assert result.returncode != 0
    assert b"hash mismatch" in result.stderr
"""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def copy(source: Path, destination: Path) -> None:
    require(source.is_file(), f"required source missing: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def selected_repository_files() -> list[Path]:
    payload = json.loads(MAP.read_text(encoding="utf-8"))
    selected = []
    for entry in payload["entries"]:
        relative = entry.get("repository_path")
        relative = {
            "PAPER-sim2real-correlation-audit.md": "PAPER.md",
            "PAPER-sim2real-correlation-audit.pdf": "PAPER.pdf",
            "output/pdf/SUPPLEMENT-sim2real-correlation-audit.pdf": (
                "output/pdf/SUPPLEMENT.pdf"
            ),
            "output/pdf/PAPER-sim2real-correlation-audit-with-supplement.pdf": (
                "output/pdf/PAPER-with-supplement.pdf"
            ),
        }.get(relative, relative)
        if relative:
            selected.append(ROOT / relative)
    required = {
        ROOT / "PAPER.md",
        ROOT / "PAPER.pdf",
        ROOT / "output/pdf/SUPPLEMENT.pdf",
        ROOT / "output/pdf/PAPER-with-supplement.pdf",
    }
    require(required <= set(selected), "P1 package map omits a required reader artifact")
    return sorted(set(selected))


def write_controls(destination: Path) -> None:
    (destination / "README.md").write_text(README, encoding="utf-8")
    (destination / "Makefile").write_text(MAKEFILE, encoding="utf-8")
    (destination / "requirements-lock.txt").write_bytes(
        (ROOT / "requirements.txt").read_bytes()
    )
    (destination / "verify_manifest.py").write_text(
        MANIFEST_VERIFIER, encoding="utf-8"
    )
    (destination / "verify_package_paths.py").write_text(
        PATH_VERIFIER, encoding="utf-8"
    )
    (destination / "test_verify_manifest.py").write_text(
        MANIFEST_TEST, encoding="utf-8"
    )
    (destination / "UPSTREAM-SOURCES.csv").write_text(
        "scope,location,boundary\n"
        "paper_source_headers,research/corpus-reporting-audit/sources/,"
        "public source identity and extraction notes are recorded in each header\n"
        "real2sim_artifacts,research/real2sim-noise-floor/review-source-artifacts.md,"
        "unreleased upstream experimental inputs are not reproduced\n",
        encoding="utf-8",
    )
    copy(ROOT.parent / "LICENSE", destination / "LICENSE")


def write_manifest(destination: Path) -> None:
    script = ROOT / "research/claim-evidence-synthesis/write_p1_package_manifest.py"
    subprocess.run([sys.executable, str(script), str(destination)], check=True)


def build(destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=".p1-staging-", dir=destination.parent
    ) as temporary:
        staging = Path(temporary) / destination.name
        staging.mkdir()
        for source in selected_repository_files():
            copy(source, staging / source.relative_to(ROOT))
        write_controls(staging)
        (staging / "CLEAN-ROOM-RESULT.md").write_text(
            "# Clean-room package result\n\nStatus: verification in progress.\n",
            encoding="utf-8",
        )
        write_manifest(staging)
        subprocess.run([sys.executable, "verify_manifest.py"], cwd=staging, check=True)
        subprocess.run(
            ["make", f"PYTHON={sys.executable}", "install", "verify"],
            cwd=staging,
            check=True,
        )
        (staging / "CLEAN-ROOM-RESULT.md").write_text(
            "# Clean-room package result\n\n"
            f"Status: PASS on {date.today().isoformat()}.\n\n"
            "The staged standalone package passed its closed SHA-256 inventory, "
            "package-path check, focused Python tests, paper-result and figure "
            "regeneration, decision analyses and method-distinct challenges, and "
            "extracted-text PDF reconstruction. Generated environments, caches, "
            "and work products were removed before the final manifest was written.\n",
            encoding="utf-8",
        )
        shutil.rmtree(staging / ".venv", ignore_errors=True)
        shutil.rmtree(staging / ".pytest_cache", ignore_errors=True)
        shutil.rmtree(staging / "work", ignore_errors=True)
        for cache in staging.rglob("__pycache__"):
            shutil.rmtree(cache)
        require(not any(staging.rglob("*.pyc")), "compiled cache survived cleanup")
        write_manifest(staging)
        subprocess.run([sys.executable, "verify_manifest.py"], cwd=staging, check=True)
        previous = Path(temporary) / "previous"
        if destination.exists():
            destination.rename(previous)
        try:
            staging.rename(destination)
        except BaseException:
            if previous.exists() and not destination.exists():
                previous.rename(destination)
            raise

    content_map = ROOT / "research/claim-evidence-synthesis/audit_p1_package_content_map.py"
    subprocess.run(
        [sys.executable, str(content_map), "--package-root", str(destination), "--write"],
        cwd=ROOT,
        check=True,
    )
    subprocess.run([sys.executable, "verify_manifest.py"], cwd=destination, check=True)
    print(f"OK: built P1 reproduction package at {destination}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    build(args.output.resolve())


if __name__ == "__main__":
    main()
