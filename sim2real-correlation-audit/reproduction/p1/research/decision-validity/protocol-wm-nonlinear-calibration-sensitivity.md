# Protocol: WM nonlinear calibration and score-decomposition sensitivity

Date fixed: 2026-07-31

Status: domain-review-triggered and outcome-exposed exploratory extension of
H240. The reviewer exposed an IRASim in-sample isotonic winner flip before
this protocol. This is not confirmatory or prospective calibration evidence.

## Questions

1. Does H240's selection-invariance result extend beyond one common positive
   affine calibration map?
2. What are the exact forecast-level Murphy Brier components for the retained
   12-cell panels?

## Fixed analyses

For Cosmos and IRASim separately:

- retain equal weight for each of the 12 policy-task cells;
- group identical displayed simulator probabilities before fitting;
- fit one nondecreasing full-panel isotonic map with the pooled-adjacent-
  violators algorithm and squared-error loss;
- apply the fitted level map to the same 12 cells and recompute policy means
  and the aggregate winner;
- report this only as an in-sample shape sensitivity, not a validated
  calibration procedure; and
- compute the exact forecast-level Murphy decomposition
  \[
  \mathrm{BS}=\mathrm{reliability}-\mathrm{resolution}+\mathrm{uncertainty}
  \]
  by grouping identical displayed forecast values, plus Brier skill relative
  to the empirical-prevalence forecast.

## Gates

- The isotonic level map must be nondecreasing and minimize cell-rate squared
  error over the fixed order-constrained level problem.
- The exact Brier identity must hold to \(10^{-12}\).
- The original winner and isotonic winner must be recorded. A winner flip is
  a sensitivity result, not evidence of improved operational selection.
- A separate Node implementation must parse the retained CSV, implement PAV
  and the Murphy decomposition directly, and match every numeric result to
  \(10^{-10}\).
- Tests must reject an altered level map, winner, or decomposition component.

## Interpretation

A positive common affine map preserves all cell and aggregate orderings.
A common monotone nonlinear map preserves cell ordering but need not preserve
averages across different score distributions, so aggregate policy ordering
can change. Full-panel isotonic fitting uses the evaluation outcomes twice and
cannot establish prospective calibration or repair. The Murphy components are
descriptive for these finite forecast groups and are not population estimates.
