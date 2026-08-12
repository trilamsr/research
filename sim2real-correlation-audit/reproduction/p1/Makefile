PYTHON ?= python3.12
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
