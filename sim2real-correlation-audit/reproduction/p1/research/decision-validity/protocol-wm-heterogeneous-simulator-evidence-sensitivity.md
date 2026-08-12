# Protocol: WM heterogeneous simulator-evidence sensitivity

Date fixed: 2026-07-31

Status: domain-review-triggered, outcome-exposed exploratory extension of
H239. The reviewer exposed the qualitative IRASim reversal for two
heterogeneous-evidence examples before this protocol. This is not
confirmatory evidence.

## Question

H239 assigns one common effective simulator evidence size to every
policy-task cell. Does its IRASim below-one-half latent winner-concordance
result survive when effective evidence differs by policy?

## Fixed data and model

- Use the retained WM-PolicyEval 3-policy by 4-task Cosmos and IRASim panels.
- Real cells use their exact successes out of 20 with independent
  Beta(1,1) posteriors.
- Simulator cells use the displayed rate \(s_{jt}\) and independent
  \[
  \theta_{jt}\sim
  \operatorname{Beta}(1+n_j s_{jt},1+n_j(1-s_{jt})),
  \]
  where one effective evidence value \(n_j\) applies to all four tasks for
  policy \(j\).
- This is a sensitivity parameter, not an estimate of a nominal rollout
  count or dependence-adjusted sample size.
- The estimand is posterior latent-rank concordance:
  the probability that independently sampled simulator-best and real-best
  policies agree. It is not the reliability of a fixed operational selection
  rule.

## Fixed scenarios and compute

For candidate order `Octo-Base`, `Octo-Small`, `OpenVLA`, evaluate:

- common evidence: `(10,10,10)` and `(500,500,500)`;
- each policy at evidence 10 while the other two are 500; and
- each policy at evidence 0 while the other two are 500.

Use 500,000 seeded draws per panel/scenario. Record:

- latent winner-concordance probability and binomial Monte Carlo SE;
- simulator and real latent winner probabilities;
- posterior-mean simulator policy scores, winner set, and winner margin.

## Gates

- The common-evidence scenarios must agree with H239 within four combined
  Monte Carlo SEs.
- At least one IRASim heterogeneous scenario must exceed one-half, disproving
  extension of H239's common-evidence direction to heterogeneous evidence.
- A method-distinct Node implementation with a custom PRNG and Gamma/Beta
  sampler must reproduce IRASim `(10,10,10)`, `(500,500,10)`, and
  `(500,500,0)` within 0.015 and preserve their below/above-half directions.
- Tests must reject negative evidence, wrong evidence-vector length, and a
  changed panel roster.

## Interpretation

Passing shows that H239's IRASim direction depends on its common-effective-
evidence restriction. It does not identify the actual cell evidence,
dependence, simulator ranking, or real-world selection reliability. No source
experiment, new outcome, population, or operational decision is inferred.
