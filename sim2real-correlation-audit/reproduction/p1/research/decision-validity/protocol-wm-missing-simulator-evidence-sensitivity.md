# Protocol: WM-PolicyEval missing-simulator-evidence sensitivity

Date fixed: 2026-07-31

Status: review-triggered, outcome-exposed exploratory analysis. P1A disclosed
approximate effective-size examples before this protocol. The analysis
quantifies a missing-data consequence; it cannot recover the true simulator
rollout count or dependence structure.

## Question and decision value

How much do WM-PolicyEval's sampled winner-match probability and selected-
policy regret depend on the unknown effective simulator evidence per
policy-task cell?

Removing fixed-simulator probabilities from the main paper prevents
overstatement but does not answer this question. If conclusions or magnitudes
change across the declared evidence grid, the simulator-side probability is
not identified by the released record. If the qualitative decision remains
stable throughout, that is useful bounded robustness evidence under the
declared model.

## Inputs and estimand

Use the 12 extracted cells for each of Cosmos and IRASim in
`source-wm-policyeval.csv`.

- Real success rates are exact multiples of 1/20 and are modeled as 20
  Bernoulli trials per cell.
- Simulator displayed rates have no released denominator. For sensitivity
  only, treat a declared effective evidence size \(n_s\) as fractional
  Bernoulli-equivalent counts \(n_s\hat p\) and
  \(n_s(1-\hat p)\).
- Average four task-cell draws within each policy. In each joint draw, select
  the sampled simulator-best policy and compare it with the sampled
  real-best policy.

Primary outputs per scenario are:

1. probability sampled simulator winner equals sampled real winner;
2. probability the displayed simulator winner remains simulator-best;
3. expected sampled-real regret of the sampled simulator selection; and
4. probability of positive sampled-real regret.

These are finite-panel model sensitivities, not deployment probabilities.

## Fixed sensitivity grid

- Symmetric Beta prior scale: \(0.5,1,2\).
- Effective simulator Bernoulli equivalents per policy-task:
  \(0,1,2,5,10,20,50,100,500,\infty\).
- \(n_s=0\) is the exchangeable-prior limit. Its winner-match probability is
  analytically \(1/K=1/3\) when simulator draws are continuous and
  exchangeable across the three policies.
- \(n_s=\infty\) fixes simulator rates at their displayed values and samples
  only the real side.
- Equal task weighting; independent cells and candidates.
- 300,000 draws per finite scenario with deterministic per-scenario seeds.

The grid is a sensitivity design, not a prior over the missing denominator.
No value is labeled plausible or selected as the answer.

## Staged validation

### Stage 0

- Recover the exact 3-policy by 4-task arrays.
- Confirm integer real counts out of 20 and displayed simulator winners.
- With 20,000 draws, require the \(n_s=0\) winner-match estimate for both
  panels and all priors to lie within six Monte Carlo standard errors of
  \(1/3\).
- Require the \(\infty\) scenario to match the existing fixed-simulator
  selection calculation within Monte Carlo tolerance.
- Reject invalid evidence sizes, priors, rates, and array shapes.

### Stage 1

Run the fixed 300,000-draw grid. Record Monte Carlo standard errors, the
minimum/maximum over the grid, whether every scenario lies on one side of
one half, and the first listed finite evidence size crossing one half for each
prior when one exists. A grid crossing is descriptive, not a universal
threshold.

### Method-distinct challenge

A Node implementation using its own deterministic random generator and
gamma/Beta sampler must not import or execute the producer. For both panels,
recompute prior-1 scenarios at \(n_s=0,10,\infty\) with at least 100,000
draws. Require agreement on:

- the displayed winners;
- the direction relative to one half;
- the \(n_s=0\) analytic \(1/3\) limit within sampling tolerance; and
- each selected scenario probability within 0.015 of the producer.

The challenge must bind protocol, producer, input, and producer-result hashes.

## Interpretation and stop conditions

If IRASim remains below one half throughout, that supports only a
model-conditional mismatch direction over this declared grid. If Cosmos
crosses one half as evidence grows, its fixed-score confidence magnitude is
not identified without the denominator. If either conclusion depends on an
implementation error, fails the method-distinct challenge, or has Monte Carlo
error large enough to span the decision boundary, retain it as unresolved.

No result may be used to infer the actual simulator evidence size, independence
of rollouts, field prevalence, or transport to new tasks or policies.
