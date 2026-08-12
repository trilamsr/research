# Protocol: H205 PhAIL achieved-first-state uniformity and joint independence

Date fixed: 2026-07-28

Status: prospective secondary-analysis rules fixed after H202's aggregate
distribution, H203's temporal null, and H204's policy/date mean-balance null,
but before computing any goodness-of-fit statistic, joint correlation, or
simulated reference. This is not a preregistration.

## Question and decision value

Are the 594 achieved first arm states distributionally consistent, at a fixed
resolution, with the source-implied independent uniform perturbations?

H199 source-defines independent per-joint uniform target draws. H202 shows
achieved-state marginal spread close to the configured scale but does not test
distributional shape or cross-joint independence. H203--H204 find no material
chronological or group-mean structure. A material shape or dependence
departure could reveal a new operational/RNG/control signature. A bounded
null would support only consistency of achieved observations with this simple
reference, not recovery of commanded draws or proof of RNG correctness.

## Fixed inputs and transform

Use exactly H202's 594-row first-state projection, SHA-256
`44b7cd9729c691a610cc1fbbefffc5668d31030e013b92f2d4550f9869020370`,
and require H202/H203/H204 result SHA-256 values
`4e60b6c6cbc0eabcaf4ae7761119b5af89bbaf6707e53cce8f0ec3c227a96043`,
`5f30b36135feaf85fc32b2f3fe5f2ad2f5c5e8188ca777131b8154d3db111cda`,
and `d03aba1badedfe0c64bdd03be74c6e1134c331fc496a012f38ec35a048a812aa`.

Require 594 unique episodes, finite seven-vectors, and zero first error flags.
Transform joint \(j\) to

\[
u_j=(q_j-\mathrm{base}_j)/a_j
\]

with the H199 base and half-width vectors. Do not clip support exceedances,
recenter, rescale, group, or remove observations.

No raw source, later state, action, command, media, performance, or outcome
field may be opened.

## Fixed estimands

1. **Marginal shape:** compute the one-sample Kolmogorov--Smirnov distance
   from Uniform[-1,1] for each joint and use the maximum across seven joints
   as the omnibus statistic.
2. **Cross-joint dependence:** compute all 21 Pearson correlations and use
   the maximum absolute value as the omnibus statistic.
3. **Support diagnostic:** report per-joint and total counts outside [-1,1],
   plus maximum absolute exceedance. This is descriptive only because achieved
   observations are not commanded draws.

Generate exactly 49,999 reference datasets of 594 independent seven-vectors
from Uniform[-1,1]. Use NumPy `Generator(PCG64)` seeded by the first 16 bytes
of `SHA256("H205 PhAIL first-state uniform independence v1")`, big-endian.
For each reference dataset compute both omnibus statistics. Report observed
values, reference median and 2.5th/97.5th percentiles, and upper-tail Monte
Carlo p-values `(b+1)/(B+1)`. Use deterministic linear quantiles.

## Classification

A material marginal departure requires p<=0.01 and maximum KS distance at
least 0.08. A material dependence departure requires p<=0.01 and maximum
absolute correlation at least 0.15.

Classify exactly one:

- `material_marginal_and_joint_departure`;
- `material_marginal_departure_only`;
- `material_joint_dependence_only`;
- `small_or_diagnostic_only_departure` when either p<=0.01 without its effect
  threshold;
- `no_material_uniform_independence_departure_at_fixed_resolution`;
- `input_drift_or_integrity_failure`; or
- `compute_integrity_failure`.

Do not revise thresholds or select individual joints/pairs after exposure.

## Staged validation and challenge

Before the material run, verify hashes/schema, exact KS arithmetic on
hand-computed samples, correlation arithmetic, support accounting, synthetic
uniform/shifted/truncated/correlated alternatives, deterministic replay at 99
simulations, and a 999-simulation runtime rehearsal. Before manuscript
reliance, independently reconstruct both observed omnibus statistics and the
classification with a distinct implementation or RNG stream.

## Scope

Achieved-state consistency with an independent-uniform reference is not proof
that commanded draws were independent or uniform, that tagged source was the
historical deployment, that RNG state was valid, or that resets succeeded.
Departures cannot identify whether their cause is target generation, control,
measurement, calibration, robot state, or another mechanism. Neither result
establishes scene/gripper balance, exchangeability, carryover absence, or
performance validity.
