# Protocol: H209 PhAIL within-regime policy sequence

Date fixed: 2026-07-28

Status: result-exposed exploratory protocol fixed after H206--H208, but before
ordering policy labels by the source-primary monotonic timestamp or computing
any within-regime policy-adjacency statistic. H206's regime/date/policy counts,
H207's state-vector temporal null, and H208's date alias are known. This is not
a preregistration and cannot support a confirmatory claim on this release.

## Question and decision value

Are policy labels temporally structured inside the two source-qualified H206
clock regimes?

H207 finds no material successive-distance structure in achieved first arm
state, but that does not test how policies were scheduled. H208 shows all
policy-regime cells are present while aggregate composition is uneven and
regime is date-aliased. Detectable same-policy adjacency or alternation inside
regime would show that policy allocation is not well represented by an
exchangeable label sequence along the recovered chronology. This would
strengthen the need for explicit assignment/block metadata before outcome
comparison. A bounded null would close this one label-order diagnostic without
validating an assignment mechanism.

## Fixed inputs

- H187 sanitized cohort:
  `result-h187-phail-context-support-sanitized.csv`, SHA-256
  `ad43fca1da065a1cb7fd84dfa9afc5691c72ebe12e7f165c68a0050e51e87ebe`.
- H206 clock-regime projection:
  `projection-h206-phail-clock-offset-regimes.csv`, SHA-256
  `7b7af23688e230325ec69070c8e5cd5523224990d7bc44defbe5b30f12c65529`.
- H206 retained result and independent challenge, SHA-256
  `1b46e77400b15ecd886d165f13fca06b3f6834a0cc4f70082da4be4a39f51e19`
  and
  `6867989afb5a2c9938ee08126defa647b7a20b26f8c48f42a7d13cc5a4787268`.
- H208 retained result and independent challenge, SHA-256
  `df6c42066f26c7bbd69be25d01ef0d72517f2546c0a1d02d129b6fdc8b6981db`
  and
  `36c2853d9193cf5ba2e752aeb03e652c96955aed59d1b7c3b6dba7e5289a3fa9`.

Require exactly 594 unique episode IDs and an exact one-to-one H187/H206
join. Require exact equality of policy, UTC date, and creation timestamp.
Require unique positive `first_timestamp_ns`, group sizes 250/344, the four
fixed policy labels from H208, all eight policy-regime cells positive, and
H206's retained classification and zero order discordances. Stop on drift.

No raw Parquet, state vector, later state, action, command, camera, media,
success, reward, score, duration, termination, annotation, or other
performance/outcome field may be opened.

## Fixed statistic

Within each exact H206 regime, sort episodes by `first_timestamp_ns`. Ties
fail integrity. For group \(g\), let

\[
A_g=\frac{1}{n_g-1}\sum_{t=1}^{n_g-1}
    1\{\mathrm{policy}_{t+1}=\mathrm{policy}_t\}.
\]

The primary statistic \(A_P\) pools the same-policy adjacency counts across
the 249 + 343 = 592 within-regime adjacent pairs with equal pair weight.
Report \(A_1\) and \(A_2\) as fixed secondary statistics.

Also report the exact conditional-exchangeability expectation

\[
E[A_g]=\frac{\sum_p n_{gp}(n_{gp}-1)}{n_g(n_g-1)}
\]

and its pair-weighted pooled value. Do not report selected policy-specific
adjacencies, individual transitions, dates, sub-regimes, runs, or alternative
orders.

## Fixed permutation reference

Use exactly 49,999 repetitions. In each repetition, independently permute the
fixed policy multiset over timestamp positions within each regime. From the
same pair of permutations, calculate pooled, regime-1, and regime-2
same-policy adjacency fractions.

Use NumPy `Generator(PCG64)` seeded by the first 16 bytes of
`SHA256("H209 PhAIL within-regime policy sequence v1")`, interpreted big-endian.
Use linear empirical quantiles.

For all three statistics report observed value, analytic expectation,
permutation median and 2.5th/97.5th percentiles, observed-minus-median
difference, lower/upper Monte Carlo p-values with `(b+1)/(B+1)`, and two-sided
`min(1, 2*min(p_lower,p_upper))`.

## Fixed classification

A material pooled deviation requires both:

- pooled two-sided p-value at most 0.01; and
- absolute observed-minus-median difference at least 0.10.

The two fixed regime-specific tests use a Bonferroni two-sided p-value of
0.005 and remain secondary.

Classify exactly one:

- `material_pooled_policy_sequence_structure`: the material pooled rule
  passes;
- `regime_specific_or_small_policy_sequence_structure`: pooled p<=0.01
  without the 0.10 effect threshold, or either regime-specific p<=0.005;
- `no_detectable_policy_sequence_structure_at_fixed_resolution`;
- `input_drift_or_integrity_failure`; or
- `compute_integrity_failure`.

Direction is descriptive: positive difference is same-policy batching;
negative difference is systematic alternation. Neither identifies a scheduler
or cause.

## Staged validation and challenge

Before material execution:

1. verify hashes, identity, field agreement, timestamps, regimes, policy
   labels, cell support, and 592-pair accounting without computing ordered
   label adjacency;
2. verify adjacency arithmetic on constant, alternating, and block synthetic
   sequences;
3. verify the analytic expectation against complete enumeration of small
   policy multisets;
4. verify restricted permutations preserve each regime's policy multiset and
   replay exactly at 99 repetitions; and
5. complete a 999-repetition rehearsal on synthetic labels with production
   group sizes before authorizing 49,999 repetitions.

Before manuscript reliance, independently reconstruct the join and chronology,
all observed adjacency statistics, analytic expectations, and a
distributionally equivalent restricted-permutation classification without
importing the producer.

## Scope

The permutation distribution is a fixed diagnostic exchangeability reference,
not evidence that labels were randomly assigned. Policy sequence structure is
not outcome dependence, physical session identity, a scheduler mechanism,
causality, or a performance effect. A null cannot validate assignment,
exchangeability, independence, or uncertainty units. H209 cannot authorize
opening outcomes.
