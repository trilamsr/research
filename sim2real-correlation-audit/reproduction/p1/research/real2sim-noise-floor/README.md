# Real2Sim noise-floor and metric forensics

## Purpose

This family owns the Real2Sim-specific noise-floor calculation, MMRV convention
audit, model-conditional Bayesian sensitivity, source-artifact review, and the
retained historical preregistration record.

`record-noise-floor-preregistration.md` preserves the identity and amendment
history of the earlier local preregistration. It is an audit record, not a
repository freeze mechanism or a default workflow requirement.

## Inputs and provenance

The analysis tracks the current canonical Real2Sim and REALM source records in
`../corpus-reporting-audit/sources/`. `source-published-summary.csv`,
`input-fig3-digitized-reference.csv` and
`input-eyeballed-real-reference.csv` retain the additional source-transcribed
and historical comparison-arm inputs owned by this family. Their headers and
the historical record document provenance and limitations.

## Reproduction

From the project root:

```bash
.venv/bin/python research/real2sim-noise-floor/audit_mmrv_conventions.py
.venv/bin/python research/real2sim-noise-floor/analyze_bayesian_interval.py
.venv/bin/python research/real2sim-noise-floor/measure_noise_floor.py \
  --data research/corpus-reporting-audit/sources/source-real2sim-eval-fig3-checkpoints.csv \
  --out research/real2sim-noise-floor
.venv/bin/python -m pytest research/real2sim-noise-floor -q
```

The canonical computational output is `result-noise-floor.json`. The
historical record can be checked with the `make historical-prereg-audit`
target.

## Dependencies and access

This family tracks the current corpus-family source records. The declared
computations require no network access. Re-running upstream source experiments
requires the external assets and access boundaries listed in
`review-source-artifacts.md`. Release-critical use must fix the upstream
project revision before release.
