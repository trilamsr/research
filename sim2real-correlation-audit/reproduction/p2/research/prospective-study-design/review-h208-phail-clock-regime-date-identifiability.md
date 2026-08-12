# Review: H208 PhAIL clock-regime/date identifiability

Date: 2026-07-28

Status: independently challenged result-exposed exploratory result; suitable
for bounded manuscript reliance.

## Candidate and result

The candidate is
`result-h208-phail-clock-regime-date-identifiability.json`, SHA-256
`df6c42066f26c7bbd69be25d01ef0d72517f2546c0a1d02d129b6fdc8b6981db`.
H206's regime-specific date and policy counts were already exposed, so H208
is explicitly descriptive and exploratory. Its protocol was fixed before
computing exact indicator alias, design ranks, total variation, or Cramer's V.

All 13 UTC dates map to exactly one H206 regime. The regime-2 indicator is
exactly the sum of the six regime-2 date indicators; adding it to the 13
nonempty date columns leaves design rank unchanged at 13. A separate
clock-regime coefficient is therefore not identified after saturated UTC-date
adjustment on this release.

All eight policy-by-regime cells are positive, ranging from 18 to 146
episodes. The two empirical policy distributions have total-variation
distance 0.3857209302 and descriptive Cramer's V 0.4515395691. No sampling
p-value is reported because the analysis describes the complete fixed
release cohort and does not posit random superpopulation sampling.

The producer passes 12 tests and exact rebuild.

## Independent method

`challenge_h208_phail_clock_regime_date_identifiability.rb` uses Ruby standard
CSV parsing and exact integer/Rational arithmetic. It does not import or
execute the Python producer. It independently:

- joins all 594 H187/H206 episode identities and verifies policy, date, and
  creation-time equality;
- reconstructs every date-to-regime mapping and exact alias coefficient;
- rebuilds the full 2-by-4 policy table;
- derives total variation and Pearson chi-square as exact fractions before
  floating conversion; and
- applies the fixed classification.

The retained challenge is
`result-h208-phail-clock-regime-date-identifiability-independent-challenge.json`,
SHA-256
`36c2853d9193cf5ba2e752aeb03e652c96955aed59d1b7c3b6dba7e5289a3fa9`.
It agrees exactly on the join, alias, ranks, table, and classification. Its
exact total-variation fraction is `8293/21500`; its exact descriptive
chi-square fraction is `76201398095229/629194425500`. Floating metrics agree
within `1.5e-14`. Six mutations to alias, counts, magnitude, classification,
and scope fail closed.

The first validator pass rejected only the cross-language chi-square float:
its approximately `1.4e-14` conversion difference narrowly exceeded a
`1e-14` comparison tolerance. The validator tolerance was widened to
`1e-12`; the exact Rational value, producer, challenge output, classification,
and scientific interpretation were unchanged.

## Disposition and boundaries

The independent evidence supports:

> H206 clock regime is exactly aliased with UTC date in this release, while
> every policy appears in both regimes with materially uneven descriptive
> composition.

The result blocks interpreting a date-adjusted clock-regime coefficient as an
independently identified release effect. Complete coarse cells establish only
observed support; they do not establish randomization, exchangeability,
precision, transport, session identity, physical order, reset/carryover,
causality, or outcome validity. No later state or performance field was
opened, and no outcome analysis is authorized. No unresolved material concern
remains for this narrow reliance.
