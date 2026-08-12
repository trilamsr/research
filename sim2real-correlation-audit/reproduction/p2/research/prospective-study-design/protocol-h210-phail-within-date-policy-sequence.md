# Protocol: H210 PhAIL within-date policy sequence

Date fixed: 2026-07-28

Status: result-exposed exploratory follow-up fixed after H209 exposed a
regime-1 same-policy adjacency signal, but before computing any policy
adjacency within UTC date. This preserves H209 unchanged and tests a new,
coarser-mechanism explanation using all 13 dates. It is not a preregistration
or confirmatory analysis.

## Question and decision value

Does H209's ordered policy-label structure persist after conditioning on UTC
date?

H208 proves clock regime is exactly date-aliased. H209 permutes labels within
regime and finds a secondary regime-1 signal, so that result could arise from
different policy mixtures across contiguous collection dates rather than
within-day scheduling. Repeating the same adjacency diagnostic while
preserving every date's policy multiset is the smallest direct discriminator.
A positive result would locate structure below the day level; a bounded null
would narrow H209 to coarser date composition/boundaries without identifying
a mechanism.

## Fixed inputs

- H187 sanitized cohort:
  `result-h187-phail-context-support-sanitized.csv`, SHA-256
  `ad43fca1da065a1cb7fd84dfa9afc5691c72ebe12e7f165c68a0050e51e87ebe`.
- H206 clock-regime projection:
  `projection-h206-phail-clock-offset-regimes.csv`, SHA-256
  `7b7af23688e230325ec69070c8e5cd5523224990d7bc44defbe5b30f12c65529`.
- H206 retained result and challenge, SHA-256
  `1b46e77400b15ecd886d165f13fca06b3f6834a0cc4f70082da4be4a39f51e19`
  and
  `6867989afb5a2c9938ee08126defa647b7a20b26f8c48f42a7d13cc5a4787268`.
- H208 retained result and challenge, SHA-256
  `df6c42066f26c7bbd69be25d01ef0d72517f2546c0a1d02d129b6fdc8b6981db`
  and
  `36c2853d9193cf5ba2e752aeb03e652c96955aed59d1b7c3b6dba7e5289a3fa9`.
- H209 retained result and challenge, SHA-256
  `2879b1c4b0ade1e4d1fd47e5a0db5312fce2d401c5f1580f7e2af2c211da7794`
  and
  `e6700b2ce631a7ca6e16669dad30cf00a4d922ff8444f3a2601a154e23ed767f`.

Require exact hashes, 594 unique one-to-one identities, H187/H206 policy/date/
creation-time equality, unique positive monotonic timestamps, the 13 fixed
H208 dates, the four fixed policies, H206 group sizes 250/344 and order
agreement, and H209's retained classification. Require every date to contain
at least three episodes. Stop on drift.

No raw Parquet, state, action, command, media, later state, success, reward,
score, duration, termination, annotation, or performance/outcome field may be
opened.

## Fixed statistic and analyses

Within every exact UTC date, order labels by `first_timestamp_ns`. Ties fail.
Compute same-policy adjacency exactly as H209.

1. **Primary pooled within-date:** pool all within-date same-policy adjacency
   counts with equal pair weight. With 594 episodes and 13 dates, require
   exactly 581 pairs.
2. **Regime-1 dates:** pool the seven regime-1 dates, requiring 243 pairs.
3. **Regime-2 dates:** pool the six regime-2 dates, requiring 338 pairs.

The latter two are fixed secondary summaries. Do not report individual-date,
policy-specific, transition-specific, run, sub-day, or alternative-order
statistics.

For every date, compute the exact conditional-exchangeability expectation
\(\sum_p n_{dp}(n_{dp}-1)/(n_d(n_d-1))\), then pool expected counts using the
same pair weights for the three analyses.

## Fixed permutation reference

Use exactly 49,999 repetitions. In each repetition, independently permute the
policy multiset within every date over fixed monotonic positions. Derive all
three statistics from the same set of date permutations.

Use NumPy `Generator(PCG64)` seeded by the first 16 bytes of
`SHA256("H210 PhAIL within-date policy sequence v1")`, big-endian. Report
observed value, analytic expectation, linear permutation median and
2.5th/97.5th percentiles, observed-minus-median, lower/upper Monte Carlo
p-values using `(b+1)/(B+1)`, and two-sided
`min(1,2*min(p_lower,p_upper))`.

## Fixed classification

A material primary deviation requires pooled p<=0.01 and absolute
observed-minus-median difference >=0.10. The two fixed regime-date secondary
tests use p<=0.005.

Classify exactly one:

- `material_pooled_within_date_policy_sequence_structure`;
- `regime_specific_or_small_within_date_policy_sequence_structure`;
- `no_detectable_within_date_policy_sequence_structure_at_fixed_resolution`;
- `input_drift_or_integrity_failure`; or
- `compute_integrity_failure`.

## Staged validation and independent challenge

Before material execution:

1. verify hashes, identity, field agreement, timestamps, fixed dates/policies,
   group/date nesting, and 243 + 338 = 581 pair accounting without computing
   material adjacency;
2. verify constant, alternating, and blocked sequences;
3. verify analytic expectations by exact enumeration of small date multisets;
4. verify date-restricted permutations preserve every date multiset and replay
   at 99 repetitions; and
5. complete a 999-repetition synthetic rehearsal at the production date-group
   sizes.

Before manuscript reliance, independently reconstruct all date groups,
observed/expected statistics, and a distributionally equivalent
date-restricted permutation classification without importing the producer.

## Scope

UTC date is not a physical session, assignment block, scheduler, or causal
unit. A positive within-date diagnostic does not identify its mechanism or
imply outcome dependence. A bounded null does not prove that H209 was caused
by date composition, nor validate assignment, exchangeability, independence,
or uncertainty units. H210 cannot authorize outcomes.
