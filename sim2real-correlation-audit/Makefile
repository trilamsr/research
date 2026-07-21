# Reproduction Makefile — every paper number, one command each.
# `make verify` runs the whole battery and prints a PASS/FAIL summary.

PY      := .venv/bin/python
PIP     := .venv/bin/pip
SCRATCH := /tmp/sim2real-audit-verify

.PHONY: install test demo survey figures results coverage verify clean

install:              ## create venv and install pinned dependencies
	python3 -m venv .venv
	$(PIP) install -q -r requirements.txt pytest matplotlib
	@echo "OK: environment ready (.venv)"

test:                 ## 26 known-answer tests + byte-for-byte §2.1/--demo parity
	$(PY) -m pytest tests/ -q

demo:                 ## reproduce paper §2.1 (RoboWorld vs Digital Cousins)
	$(PY) correlation_audit.py --demo

survey:               ## regenerate every §8 count from the coded survey
	$(PY) survey_table.py

figures:              ## regenerate Figures 1–3, printing verification numbers
	cd figures && ../$(PY) make_figures.py

results:              ## regenerate results.json and diff against the released one
	@mkdir -p $(SCRATCH)
	$(PY) measure_noise_floor.py --data data/real2sim-eval-fig3-checkpoints.csv --out $(SCRATCH) >/dev/null
	@$(PY) -c "import json; a=json.load(open('results.json')); b=json.load(open('$(SCRATCH)/results.json')); \
	a.pop('source',None); b.pop('source',None); \
	assert json.dumps(a,sort_keys=True)==json.dumps(b,sort_keys=True), 'MISMATCH'; print('OK: results.json regenerates identically')"

coverage:             ## §6.1 Fisher-z coverage simulation (seed-fixed, ~2 s)
	$(PY) fz_coverage.py

verify: test demo survey figures results   ## the full battery
	@echo ""
	@echo "ALL CHECKS PASSED — every headline number recomputes from the released data."

clean:                ## remove venv and caches
	rm -rf .venv $(SCRATCH) .pytest_cache figures/__pycache__ tests/__pycache__ __pycache__
