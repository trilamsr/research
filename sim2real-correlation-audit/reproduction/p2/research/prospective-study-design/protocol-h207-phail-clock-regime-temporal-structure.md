# Protocol: H207 PhAIL clock-regime temporal structure

Date fixed: 2026-07-28

Status: result-exposed exploratory protocol fixed after H203 and H206, but
before computing any achieved-state distance in an H206 clock-offset regime.
H203's aggregate temporal null and H206's two-regime clock result are known.
This is not a preregistration and cannot support a confirmatory claim on this
release.

## Question and decision value

Does the H203 bounded temporal null remain when successive achieved first arm
states are compared only within the two source-qualified H206 clock-offset
regimes and ordered by the source-primary monotonic timestamp?

H203 used release-record wall-clock chronology and included one pair across
the large clock-origin discontinuity. H206 later established two
scale-separated clock-offset regimes of 250 and 344 episodes, with identical
wall-clock and monotonic ordering inside each regime. Repeating the fixed
successive-distance diagnostic within those regimes is the smallest direct
test of whether the prior null concealed regime-conditioned structure. A
positive result would strengthen the request for authenticated execution
sessions and carryover-aware evaluation. A bounded null would close this
specific clock-regime refinement without proving independence.

## Fixed inputs and integrity requirements

- H202 first-state projection:
  `projection-h202-phail-initial-joint-state.csv`, SHA-256
  `44b7cd9729c691a610cc1fbbefffc5668d31030e013b92f2d4550f9869020370`.
- H203 producer implementation:
  `audit_h203_phail_first_state_temporal_structure.py`, SHA-256
  `2a93bd3188681c5fc06312395f06fc3e899b405ed55547018b0e82ca3f271873`.
- H203 retained result:
  `result-h203-phail-first-state-temporal-structure.json`, SHA-256
  `5f30b36135feaf85fc32b2f3fe5f2ad2f5c5e8188ca777131b8154d3db111cda`.
- H206 clock-regime projection:
  `projection-h206-phail-clock-offset-regimes.csv`, SHA-256
  `7b7af23688e230325ec69070c8e5cd5523224990d7bc44defbe5b30f12c65529`.
- H206 retained result:
  `result-h206-phail-monotonic-wall-clock-bridge.json`, SHA-256
  `1b46e77400b15ecd886d165f13fca06b3f6834a0cc4f70082da4be4a39f51e19`.
- H206 independent challenge:
  `result-h206-phail-monotonic-wall-clock-bridge-independent-challenge.json`,
  SHA-256
  `6867989afb5a2c9938ee08126defa647b7a20b26f8c48f42a7d13cc5a4787268`.

Require exactly 594 unique episode IDs and an exact one-to-one H202/H206
join. Require every H202 error flag to equal zero, every seven-vector to be
finite, every H206 `first_timestamp_ns` to be positive and unique, and the
only `group_1h` values to be 1 and 2 with respective sizes 250 and 344.
Require the H206 result to retain
`scale_separated_clock_offset_regimes`, zero within-group wall/monotonic
discordant pairs, and the same group sizes. Stop on any drift.

No raw Parquet, later state, action, command, camera, media, success, reward,
score, duration, termination, annotation, or other performance/outcome field
may be opened.

## Fixed transform and statistic

Use the H203 transform without observed-data recentering or rescaling:

```text
base = [0.0, -0.31, 0.0, -1.65, 0.0, 1.522, 0.0]
a    = [0.03, 0.05, 0.08, 0.08, 0.10, 0.10, 0.10]
z_j  = (q_j - base_j) / (a_j / sqrt(3))
```

Within each exact H206 regime, order episodes by `first_timestamp_ns`.
Timestamp ties fail integrity rather than invoking a substantive tie rule.
For an ordered group \(g\), define

\[
M_g = \frac{1}{n_g-1}\sum_{t=1}^{n_g-1}\sum_{j=1}^{7}
      (z_{t+1,j}-z_{t,j})^2 .
\]

The primary statistic \(M_P\) pools the sums of squared distance across all
within-regime adjacent pairs with equal pair weight. It therefore contains
592 pairs: 249 in regime 1 and 343 in regime 2. Report \(M_1\) and \(M_2\) as
fixed secondary statistics. Do not calculate or select individual joints,
pairs, dates, policies, sub-regimes, proximity thresholds, or alternative
orders.

## Fixed permutation reference

Use exactly 49,999 repetitions. In every repetition, independently permute
the state vectors over the fixed timestamp positions within each of the two
regimes. From the same pair of regime permutations, calculate the pooled,
regime-1, and regime-2 statistics. This preserves regime membership and uses
no across-regime pair.

Use NumPy `Generator(PCG64)` with the integer formed from the first 16 bytes
of `SHA256("H207 PhAIL clock-regime temporal structure v1")`, interpreted
big-endian. Use deterministic linear empirical quantiles.

For all three statistics report:

- observed mean successive squared distance;
- permutation median and 2.5th/97.5th percentiles;
- observed-to-permutation-median ratio;
- lower-tail and upper-tail Monte Carlo p-values using
  `(b + 1)/(B + 1)`; and
- two-sided p-value `min(1, 2 * min(p_lower, p_upper))`.

## Fixed classification

Let a material pooled deviation require both:

- pooled two-sided p-value at most 0.01; and
- pooled observed/median ratio at most 0.90 or at least 1.10.

The two fixed regime-specific tests use a Bonferroni-adjusted two-sided
threshold of 0.005. They are secondary and cannot be relabeled as the primary
result after exposure.

Classify exactly one:

- `material_pooled_clock_regime_temporal_structure`: the material pooled rule
  passes;
- `regime_specific_or_small_clock_regime_temporal_structure`: the pooled
  p-value is at most 0.01 without its 10% effect threshold, or either
  regime-specific p-value is at most 0.005;
- `no_detectable_clock_regime_temporal_structure_at_fixed_resolution`: neither
  rule above passes;
- `input_drift_or_integrity_failure`; or
- `compute_integrity_failure`.

The `no_detectable` class is a bounded null for these achieved first arm
states, two outcome-exposed clock regimes, this statistic, and this
permutation design. It is not evidence of independence, valid RNG operation,
carryover absence, authenticated physical order, or valid uncertainty units.

## Staged validation

Before the material permutation run:

1. verify all hashes, exact one-to-one identity, unique monotonic timestamps,
   regime sizes, H206 classifications, and the 249 + 343 = 592 pair
   accounting without computing achieved-state order statistics;
2. verify the transform and successive-distance arithmetic on hand-computed
   vectors;
3. verify constant, alternating, linear-drift, and IID synthetic controls;
4. verify that restricted permutations never cross regime membership and
   replay exactly at 99 repetitions; and
5. run a 999-repetition rehearsal on synthetic seven-vectors with group sizes
   250 and 344, recording runtime and completeness before authorizing the
   49,999-repetition material computation.

Technical success is exact input identity, complete finite output, the fixed
repetition count, deterministic rebuild, and passed controls. A favorable,
unfavorable, or null scientific result is not an execution failure.

## Independent challenge and scope

Before manuscript reliance, independently reconstruct the H202/H206 join,
within-regime monotonic order, all three observed statistics, and a
distributionally equivalent restricted-permutation classification using an
implementation and random stream that do not import the producer. Resolve
material disagreements before reliance.

H206's regimes are clock-origin regimes, not identified hosts, reboots,
operator sessions, physical reset blocks, carryover units, exchangeability
clusters, or causal mechanisms. H207 may refine the evidence request and the
scope of H203's bounded null. It may not authorize opening outcomes or support
a performance, policy-comparison, independence, or causal claim.
