# Claim-evidence synthesis

## Purpose

This family combines canonical results from the project’s scientific families
into the machine-readable paper evidence, generated main tables, quantitative
supplement, and publication figures. It also owns the paper protocol and the
claim-boundary, knowledge-gap, and confidence-closure reviews.

## Inputs and provenance

`synthesize_paper_evidence.py` reads the current canonical corpus sources and
outputs, Real2Sim forensic results, and their documented provenance. It does
not rerun the surveyed papers’ robot experiments. `generate_paper_figures.py`
uses the same in-memory evidence object so plotted annotations do not create a
second factual source.

## Reproduction

From the project root:

```bash
.venv/bin/python research/claim-evidence-synthesis/synthesize_paper_evidence.py
.venv/bin/python research/claim-evidence-synthesis/generate_paper_figures.py
.venv/bin/python -m pytest research/claim-evidence-synthesis -q
```

Canonical outputs are `result-paper-evidence.json`,
`result-main-tables.md`, `result-quantitative-supplement.md`, and the matching
`figure-*.pdf`/`figure-*.png` pairs.

JSON regeneration requires exact structure, types, counts, and categorical
values while allowing absolute float drift up to `1e-12`. This covers
platform-level correlation roundoff; the generated Markdown tables remain
byte-identical. It is not a tolerance for Monte Carlo or scientific
disagreement.

`review-confidence-closure.md` ranks residual risks and records their closure
conditions. It is operational review control rather than an external-fact
source.

For external review, start with `EXTERNAL-REVIEW-GUIDE.md` at the project root.
`SIM2REAL-DECISION-AUDIT-CHECKLIST.md` is the reusable method extracted from
the manuscript. The current technical-readiness evidence and the remaining
human-review gate are recorded in
`review-p1-external-readiness-2026-07-27.md`.

The external package is a deliberately scoped projection rather than a raw
directory copy. `audit_p1_package_content_map.py` produces
`result-p1-package-content-map.json`, which maps every distributed file to its
repository owner or gives the package-only/package-variant reason. Recheck a
candidate package with:

```bash
.venv/bin/python research/claim-evidence-synthesis/audit_p1_package_content_map.py \
  --package-root /path/to/P1-reproduction-package --check
```

## Dependencies and access

This family tracks the current canonical artifacts in
`../corpus-reporting-audit/` and `../real2sim-noise-floor/`; paper text also
uses the current decision-validity outputs documented in the manuscript and
reviews. No network access is required for generation. All release-critical
upstream dependencies must be fixed before paper release.
