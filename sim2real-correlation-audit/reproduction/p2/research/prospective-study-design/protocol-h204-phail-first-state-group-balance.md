# Protocol: H204 PhAIL achieved-first-state group balance

Date fixed: 2026-07-28

Status: prospective secondary-analysis rules fixed after H202 aggregate
exposure and H203's bounded temporal null, but before computing any policy or
date group mean, fitted model, variance share, or label-permutation result.
After outcome-free stratum counts passed, but still before any state group
mean or model fit, the permutation implementation was amended from repeated
label-design rebuilding to nuisance-residual row permutation within the same
fixed strata. This preserves each seven-joint vector, the fixed factor labels,
and the intended conditional null while making the material computation
tractable. This is not a preregistration.

## Question and decision value

Does achieved first arm state show a material mean association with policy
after conditioning on UTC date, or with UTC date after conditioning on policy?

H199 shows the same configured randomized-home mechanism for all fixed PhAIL
policy paths, but neither commanded draws nor RNG identity are recorded. H202
recovers achieved first state and H203 finds no material successive-distance
structure. A policy-associated achieved-state shift could identify a concrete
initial-condition imbalance that must be handled before outcome comparison.
A date-associated shift could identify operational drift or batching. A
bounded null would support only mean balance on the seven observed arm joints,
not full physical-context balance, random assignment, exchangeability, or
outcome validity.

## Fixed inputs and scope

Use exactly the H203 fixed inputs:

- H187 sanitized cohort SHA-256
  `ad43fca1da065a1cb7fd84dfa9afc5691c72ebe12e7f165c68a0050e51e87ebe`;
- H202 first-state projection SHA-256
  `44b7cd9729c691a610cc1fbbefffc5668d31030e013b92f2d4550f9869020370`;
- H202 result SHA-256
  `4e60b6c6cbc0eabcaf4ae7761119b5af89bbaf6707e53cce8f0ec3c227a96043`;
  and
- H203 result SHA-256
  `5f30b36135feaf85fc32b2f3fe5f2ad2f5c5e8188ca777131b8154d3db111cda`.

Require the exact 594 one-to-one episode join, finite first seven-vectors,
zero first error flags, four nonempty policy groups, 13 nonempty UTC-date
groups, and at least two policy labels within each retained date and two date
labels within each retained policy. If a stratum has only one label for the
tested factor, retain it for nuisance fitting but it contributes no label
permutation.

Use only `episode_id`, `policy_model`, `utc_date`, and H202's first seven
joint values/error flag. Do not open later state, action, command, camera,
media, success, reward, score, rank, duration, termination, annotation, or
other outcome fields.

## Fixed transform and model statistic

Standardize the seven joint deviations by the source-configured uniform
target standard deviations, exactly as H203:

```text
base = [0.0, -0.31, 0.0, -1.65, 0.0, 1.522, 0.0]
a    = [0.03, 0.05, 0.08, 0.08, 0.10, 0.10, 0.10]
z_j  = (q_j - base_j) / (a_j / sqrt(3))
```

Fit multivariate ordinary least squares separately to all seven standardized
joint columns. Use full-rank treatment-coded design matrices with an
intercept. Define partial multivariate variance share for adding factor \(A\)
to nuisance model \(N\) as

\[
R^2_{\mathrm{partial}} =
\frac{\mathrm{SSE}(N)-\mathrm{SSE}(N+A)}{\mathrm{SSE}(N)},
\]

where SSE is the sum of squared residuals over all episodes and seven joints.
Use a pseudoinverse only as the deterministic OLS implementation; require the
constructed design rank to equal its declared rank.

## Fixed analyses

1. **Primary policy conditional on UTC date:** nuisance model is date; full
   model is date plus policy. Permute nuisance-model residual seven-vectors
   independently within each UTC date, add the fixed nuisance fitted values,
   and recompute the partial variance share against the fixed labels.
2. **Secondary date conditional on policy:** nuisance model is policy; full
   model is policy plus date. Permute nuisance-model residual seven-vectors
   independently within each policy, add the fixed nuisance fitted values,
   and recompute against the fixed labels.
3. **Diagnostic unadjusted policy:** intercept-only nuisance and policy full
   model; globally permute intercept-model residual seven-vectors.

For each analysis report observed partial \(R^2\), permutation median and
2.5th/97.5th percentiles, upper-tail Monte Carlo p-value `(b + 1)/(B + 1)`,
factor/nuisance ranks, group count, and stratum count. Use exactly 49,999
permutations.

Use NumPy `Generator(PCG64)` with the integer formed from the first 16 bytes
of `SHA256("H204 PhAIL first-state group balance v1")`, big-endian, and the
stream order primary policy, secondary date, diagnostic unadjusted policy.
Use deterministic linear empirical quantiles.

Report as diagnostics only:

- each joint's maximum absolute policy mean difference on the standardized
  scale;
- each joint's maximum absolute UTC-date mean difference on the standardized
  scale; and
- the corresponding raw-radian spans.

Do not select individual joints or pairwise group contrasts for inference
after exposure.

## Classification

A material association requires both upper-tail p-value at most 0.01 and
partial \(R^2\) at least 0.02.

Classify exactly one:

- `material_policy_initial_state_association`: the primary rule passes;
- `material_date_initial_state_association_only`: the primary rule fails and
  the secondary date rule passes;
- `small_or_diagnostic_only_group_association`: either fixed policy/date
  p-value is at most 0.01 but its partial \(R^2\) is below 0.02, or only the
  unadjusted policy diagnostic passes both thresholds;
- `no_material_group_mean_association_at_fixed_resolution`: none of the
  above;
- `input_drift_or_integrity_failure`; or
- `compute_integrity_failure`.

Retain continuous results regardless of classification. Do not relax the
0.01 or 0.02 rules.

## Staged validation and independent challenge

Before the material run:

1. verify hashes, joins, group/stratum counts, and design ranks without
   computing group means or model fits on the H202 values;
2. verify OLS SSE and partial \(R^2\) against hand-computed scalar and
   multivariate examples;
3. verify synthetic policy shift, date shift, additive policy/date shift,
   balanced null, and collinearity failure cases;
4. verify that every permutation preserves its exact stratum-specific
   residual-vector multiset and deterministic replay at 99 permutations; and
5. benchmark 999 synthetic permutations before running 49,999.

Before manuscript reliance, independently reconstruct the joined data,
observed variance shares, and classifications with a distinct implementation
or permutation stream.

## Scope

Policy/date association is descriptive and does not establish assignment,
causality, RNG failure, physical session identity, carryover mechanism, or
performance bias. The UTC date is not an authenticated session. Mean balance
on seven achieved arm joints does not establish balance in commanded target,
scene, object, tote, gripper, camera, calibration, robot health, operator
state, or unmeasured context. A null does not prove exchangeability or
authorize outcomes.
