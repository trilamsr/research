# Protocol: H203 PhAIL achieved-first-state temporal structure

Date fixed: 2026-07-28

Status: prospective secondary-analysis rules fixed after H202 exposed and
summarized the achieved first-state projection, but before ordering those
states, joining policy/time fields to them, or computing any temporal,
policy-stratified, or calendar-stratified statistic. This is not a
preregistration and is explicitly result-exposed to H202's aggregate
distribution.

## Question and decision value

Do the 594 public achieved first arm states show material structure along the
release-record chronology that would strengthen the request for
session/carryover-aware evaluation evidence?

The source uses a fresh `numpy.random.uniform` draw at each reset, but records
neither RNG identity nor the commanded draw. H202 recovers the achieved first
joint observation for every episode. Detectable chronological persistence,
alternation, or batching would be evidence against treating these achieved
states as an unstructured exchangeable sequence. A bounded null would not
prove independence or absence of carryover, but would prevent an unsupported
positive dependence claim.

## Fixed inputs

- H187 sanitized 594-episode cohort:
  `result-h187-phail-context-support-sanitized.csv`, SHA-256
  `ad43fca1da065a1cb7fd84dfa9afc5691c72ebe12e7f165c68a0050e51e87ebe`.
- H202 first-state projection:
  `projection-h202-phail-initial-joint-state.csv`, SHA-256
  `44b7cd9729c691a610cc1fbbefffc5668d31030e013b92f2d4550f9869020370`.
- H202 result:
  `result-h202-phail-initial-joint-state.json`, SHA-256
  `4e60b6c6cbc0eabcaf4ae7761119b5af89bbaf6707e53cce8f0ec3c227a96043`.

Use all 594 episodes. Require one-to-one episode identity, all H202 first error
flags equal to zero, finite seven-vectors, unique positive H187
`created_ts_ns`, and exact H187/H202 input hashes. Stop on any drift.

No raw Parquet, later state, action, command, camera, media, success, reward,
score, duration, termination, annotation, or other outcome field may be
opened. `policy_model`, `created_ts_ns`, and `utc_date` are the only H187
fields authorized for this analysis.

## Fixed transform

Subtract the H199 configured base vector and standardize joint \(j\) by the
theoretical uniform-target standard deviation \(a_j/\sqrt{3}\), using

```text
base = [0.0, -0.31, 0.0, -1.65, 0.0, 1.522, 0.0]
a    = [0.03, 0.05, 0.08, 0.08, 0.10, 0.10, 0.10]
```

Do not recenter or rescale by observed group moments.

For an ordered sequence of \(n\) standardized seven-vectors, define the mean
successive squared distance

\[
M = \frac{1}{n-1}\sum_{t=1}^{n-1}\sum_{j=1}^{7}
    (z_{t+1,j}-z_{t,j})^2 .
\]

Under independent draws with the configured marginal variances, the nominal
reference is 14, but all decisions below use permutation references rather
than that approximation.

## Fixed analyses

Sort by `created_ts_ns`, breaking ties by episode ID only as an integrity
fallback (ties themselves fail the unique-timestamp requirement).

1. **Primary global chronology:** compute \(M_G\) across the complete ordered
   594-episode sequence. Compare it with global permutations of the 594 state
   vectors over the fixed timestamps.
2. **Policy-stratified chronology:** within each exact `policy_model`, order
   episodes by timestamp and pool all within-policy adjacent-pair squared
   distances with equal pair weight. Compare with independent permutations
   of state vectors within each policy.
3. **UTC-date-stratified chronology:** within each exact `utc_date`, order
   episodes by timestamp and pool all within-date adjacent-pair squared
   distances with equal pair weight. Compare with independent permutations
   within each date.

Require every included group to contain at least three episodes and each
pooled secondary analysis to contain at least 100 adjacent pairs. Do not merge,
drop, or rename groups after exposure.

For each analysis report:

- observed \(M\);
- permutation median and 2.5th/97.5th percentiles;
- observed-to-permutation-median ratio;
- lower-tail and upper-tail Monte Carlo p-values using `(b + 1)/(B + 1)`;
- two-sided p-value `min(1, 2 * min(p_lower, p_upper))`; and
- pair and group counts.

Use exactly 49,999 permutations and NumPy `Generator(PCG64)` with the integer
formed from the first 16 bytes of
`SHA256("H203 PhAIL first-state temporal structure v1")`, interpreted
big-endian. Use deterministic linear empirical quantiles.

As diagnostics only, report per-joint Pearson correlations across the primary
adjacent pairs and the number of exact duplicate seven-vectors. Do not use
these diagnostics for classification and do not add proximity thresholds
after exposure.

## Classification

Let a material primary deviation require both:

- two-sided permutation p-value at most 0.01; and
- primary observed/median ratio at most 0.90 or at least 1.10.

Classify exactly one:

- `material_global_temporal_structure`: the material primary rule passes;
- `secondary_only_or_small_temporal_structure`: the primary p-value is at
  most 0.01 without the 10% effect threshold, or either fixed secondary
  p-value is at most 0.01;
- `no_detectable_temporal_structure_at_fixed_resolution`: neither rule above
  passes;
- `input_drift_or_integrity_failure`; or
- `compute_integrity_failure`.

The `no_detectable` class is a bounded null at this statistic, sample size,
timestamp surrogate, and permutation design. It is not evidence of
independence, correct RNG operation, carryover absence, or valid uncertainty
units.

## Staged validation and independent challenge

Before the material permutation run:

1. verify input joins, unique timestamps, and group/pair accounting without
   computing state-order statistics;
2. verify the transform and successive-distance arithmetic on hand-computed
   vectors;
3. verify that constant, alternating, linear-drift, policy-shift, and IID
   synthetic sequences produce the expected qualitative behavior;
4. verify deterministic permutation replay at 99 permutations, including
   separate global, policy, and date permutation scopes; and
5. estimate runtime at 999 permutations before authorizing the 49,999-run
   computation.

Before manuscript reliance, independently recompute the joined sequence,
observed statistics, and permutation classification with a distinct
implementation or RNG stream. Resolve any material disagreement before
reliance.

## Scope

`created_ts_ns` is a release-record chronology field, not authenticated
physical execution order or operator-session identity. Temporal structure in
achieved arm state cannot by itself identify RNG state, commanded targets,
scene/gripper state, resets, carryover mechanisms, sessions, causal effects,
exchangeability of outcomes, or performance bias. A null cannot validate
independence. This study may refine an evidence request; it may not authorize
opening outcomes.
