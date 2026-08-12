# Protocol: WM-PolicyEval probability-calibration audit

Date fixed: 2026-07-31

Status: review-triggered, outcome-exposed exploratory analysis. P1B proposed a
“Brier” value and affine calibration slope before this protocol. The audit
must first determine whether that score name and calculation are valid.

## Question and decision value

Do the retained WM-PolicyEval panels contain defensible probability-level
information that correlation and argmax omit, and would adding calibration
analysis materially change P1's scientific conclusion or recommended
measurement bundle?

The analysis is useful only if it distinguishes probability calibration from
rate fit and from selection. It must not use a favorable relabeling of one
metric as another.

## Inputs and units

Use the 12 policy-task cells per evaluator in
`source-wm-policyeval.csv`. Each real rate represents 20 binary robot outcomes.
Simulator predictions are displayed rates with an unknown rollout denominator.

The primary descriptive unit is the policy-task cell. Tasks are the only
declared deletion clusters. No population of tasks or policies is defined.

## Fixed calculations

For each of Cosmos and IRASim:

1. **Cell-rate MSE**
   \[
   \frac1{12}\sum_c(\hat p_c-\hat r_c)^2.
   \]
   This measures displayed rate fit. It is not the individual-outcome Brier
   score.
2. **Empirical individual-outcome Brier score**, reconstructed exactly from
   the 20 real binary outcomes per cell:
   \[
   \frac1{12}\sum_c
   \{\hat p_c^2-2\hat p_c\hat r_c+\hat r_c\}.
   \]
   Verify the identity
   \[
   \text{Brier}=\text{cell-rate MSE}
   +\frac1{12}\sum_c\hat r_c(1-\hat r_c).
   \]
3. Calibration-in-the-large:
   \(\overline{\hat p}-\overline{\hat r}\).
4. Equal-cell OLS calibration:
   \(\hat r=\beta_0+\beta_1\hat p\), plus Pearson correlation.
5. Displayed policy means, winners, and real regret of the displayed
   simulator winner.
6. Exact leave-one-task-out ranges for cell-rate MSE, Brier,
   calibration-in-the-large, slope, and intercept.
7. Four-fold task-held-out affine recalibration: fit
   \((\beta_0,\beta_1)\) on three tasks, apply it to the omitted task, and
   report pooled held-out rate MSE. This is an exploratory internal
   cross-check, not generalization evidence.
8. Determine mechanically whether the full-panel affine slope is positive.
   A common positive affine map preserves every cell ordering and aggregate
   policy argmax, so it cannot repair or create P1's selection disagreement.

Do not bin the 12 cells into an expected-calibration error; the binning choice
would dominate this sample. Do not report asymptotic standard errors that
treat the 12 cells as independent draws from a population.

## Staged validation

### Stage 0

- Confirm 12 complete cells, four tasks, three policies, and integer real
  counts out of 20 per evaluator.
- Confirm the empirical Brier identity exactly to \(10^{-15}\).
- Reproduce the source-record Pearson coefficients from plotted points.
- Reject a test fixture that labels cell-rate MSE as Brier.

### Stage 1

Run all fixed calculations, exact task deletions, and held-out recalibration.
Retain unfavorable or null calibration results. Classify the result as one of:

- `orthogonal_level_error_with_selection_invariance`;
- `calibration_adds_no_material_information`;
- `score_interpretation_invalid`; or
- `compute_integrity_failure`.

### Method-distinct challenge

A separate implementation must reconstruct the two score definitions from
the CSV without importing or executing the producer. It must verify the Brier
identity, OLS coefficients, task-deletion extrema, policy winners, and affine
selection invariance to \(10^{-10}\), while binding protocol, input, producer,
and result hashes.

## Interpretation and stop conditions

A positive level-error finding would support adding probability-level
diagnostics only where evaluator outputs are intended as success
probabilities. It would not strengthen the claim that correlation fails to
identify argmax, estimate calibration transport, or validate a universal
threshold.

If the review's proposed Brier value is actually cell-rate MSE, correct the
scientific record explicitly. If positive affine calibration preserves the
winner, treat calibration as an orthogonal validity axis rather than a repair
of the decision result. Stop after the fixed panel calculations; new
prospective calibration requires new tasks or policies and a target sampling
design.
