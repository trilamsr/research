# Protocol: H208 PhAIL clock-regime/date identifiability

Date fixed: 2026-07-28

Status: result-exposed exploratory protocol fixed after H206 exposed the two
clock-regime date and policy counts and after H207 retained a bounded temporal
null, but before computing the exact date-alias relation, policy-regime support
classification, Cramer's V, or total-variation distance. This is not a
preregistration and cannot support a confirmatory claim on this release.

## Question and decision value

Does the H206 clock-regime indicator add an identifiable dimension beyond UTC
collection date, and does every released policy appear in both clock regimes?

H206 source-qualifies two clock-origin regimes and within-regime order. H207
finds no material achieved-state temporal structure within them. A later
outcome analysis might nevertheless be tempted to treat clock regime as a
session-like adjustment or explanatory variable. If regime is exactly aliased
with UTC date, its effect cannot be separated from date on this release. If
policy-by-regime cells are missing, even coarse policy comparisons across
regime would additionally require extrapolation. Complete cells would show
structural overlap only, not randomization, precision, or exchangeability.

## Fixed inputs

- H187 sanitized 594-episode cohort:
  `result-h187-phail-context-support-sanitized.csv`, SHA-256
  `ad43fca1da065a1cb7fd84dfa9afc5691c72ebe12e7f165c68a0050e51e87ebe`.
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
- Known H207 result context:
  `result-h207-phail-clock-regime-temporal-structure.json`, SHA-256
  `31ef2b4162157769bf9f99ce47f50865076b99e114c7a67592319ce8df2b2252`.
- H207 independent challenge:
  `result-h207-phail-clock-regime-temporal-structure-independent-challenge.json`,
  SHA-256
  `39839285b7a84acf2fb3a5b74afe18a3fb32d51e2491358d6b42ad24b80032e2`.

Require exactly 594 unique episode IDs and an exact one-to-one H187/H206
join. Require exact equality of `policy_model`, `utc_date`, and
`created_ts_ns` across the two projections. Require H206's retained
classification, group sizes 250/344, and zero within-group wall/monotonic
discordant pairs. Stop on any drift.

No raw Parquet, later state, action, command, camera, media, success, reward,
score, duration, termination, annotation, or performance/outcome field may be
opened.

## Fixed exact analyses

1. **Date alias.** Construct one exact indicator column for each observed UTC
   date and the binary indicator `group_1h == 2`. For every date, report the
   set of observed regimes. The regime indicator is exactly date-aliased if
   every date has one regime and the regime-2 vector equals the sum of the
   one-hot columns for its dates. Report the date-only design rank and the
   date-plus-regime rank as diagnostics; the exact indicator equality, not a
   floating tolerance, governs classification.
2. **Policy-regime support.** Cross-tabulate exact `policy_model` by
   `group_1h`. Report all cells, the minimum and maximum cell counts, and
   whether every policy appears in both regimes. Do not merge or rename
   policies.
3. **Descriptive composition magnitude.** Report the total-variation distance
   between the two empirical policy distributions and Cramer's V for the
   fixed 2-by-policy table. These describe this complete release cohort; do
   not attach a sampling p-value or interpret the release as a random sample
   from a superpopulation.

Do not open outcomes or add sub-day bins, clock sub-regimes, selected policy
contrasts, odds ratios, weighting targets, or outcome models after exposure.

## Fixed classification

Classify exactly one:

- `date_aliased_with_complete_policy_regime_support`: exact date alias holds
  and every policy appears in both regimes;
- `date_aliased_with_policy_regime_support_gap`: exact date alias holds and
  at least one policy-regime cell is zero;
- `date_separable_at_utc_day_resolution`: at least one UTC date contains both
  regimes and the regime indicator is not exactly reconstructed by the
  date-only indicators;
- `input_drift_or_integrity_failure`; or
- `compute_integrity_failure`.

The first class means a clock-regime coefficient cannot be separately
identified after saturated UTC-date adjustment on this release, while coarse
policy-by-regime cells are all observed. It does not mean those cells are
exchangeable, sufficiently precise, randomly assigned, causally comparable,
or valid for outcomes.

## Staged validation and challenge

Before material computation:

1. verify hashes, one-to-one identity, field equality, H206 status, and group
   counts;
2. verify exact alias detection on a synthetic date-nested table;
3. verify non-alias detection when one synthetic date spans regimes;
4. verify complete and missing policy-regime support controls;
5. verify total-variation and Cramer's-V arithmetic on hand-computed tables.

Before manuscript reliance, independently reconstruct the join, date-regime
map, exact alias coefficients, full policy-regime table, and both composition
metrics without importing the producer. Resolve any material disagreement.

## Scope

UTC date is a coarse release-record field, not an authenticated physical
execution session. Clock regime is an outcome-exposed clock-origin partition,
not a machine, reboot, operator session, reset/carryover unit, cause, or valid
uncertainty cluster. Exact alias proves non-separability only for these
recorded columns in this release. Complete coarse cells do not authorize
outcome access or inference.
