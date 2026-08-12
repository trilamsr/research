# Review: H205 PhAIL achieved-first-state uniform independence

Date: 2026-07-28

## Disposition

**Pass as
`no_material_uniform_independence_departure_at_fixed_resolution`.**

The maximum of seven marginal one-sample KS distances is 0.04071, below the
49,999-dataset independent-uniform reference median of 0.05044 (upper-tail
p=0.891). The largest absolute cross-joint correlation is 0.13117, compared
with a reference median of 0.08764 and 97.5th percentile of 0.13252
(upper-tail p=0.0282). It passes neither the fixed p<=0.01 rule nor the
0.15 material-effect threshold. No individual joint or pair is promoted
post hoc.

Ten of 4,158 achieved joint values lie slightly outside their configured
target support. The maximum normalized exceedance is 0.01139, equivalent to
less than 0.001 rad for every joint. This descriptive diagnostic is compatible
with achieved state differing slightly from a commanded target; it does not
identify control, measurement, calibration, or RNG behavior.

## Independent challenge

A separate implementation imports no producer module. It uses SciPy's exact
one-sample KS and Pearson implementations for the observed statistics and a
separate Philox stream for 49,999 complete reference datasets. It reproduces
the observed omnibus statistics within `2.78e-17`; its marginal and
dependence p-values are 0.8912 and 0.02894, yielding the same classification.
Five result, simulation-count, and scope attacks are rejected.

Producer result SHA-256 is
`9bbdc9415f8d76717a08911852861579d54b75c4a7f9e50b26e3f893a1fbedf7`;
challenge result SHA-256 is
`e6d071de1ed781d503a0a3b3e66c8a19749d4ea05942a3c9ae5ff44013203909`.

## Consequence and scope

P2 may state that the achieved first arm states show no material marginal-
uniformity or cross-joint-dependence departure at the fixed resolution. This
is consistency of achieved observations with a simple source-implied
reference, not recovery or validation of commanded draws, RNG state, reset
acceptance, historical source fidelity, or physical-context balance. A
departure would not by itself identify its mechanism.

No new public object was opened. H205 used only H202's fixed first-state
projection; later state and all performance fields remained sealed.
