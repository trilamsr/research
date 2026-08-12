# Protocol: H232 full-edge-box objective comparison

Date fixed: 2026-07-28

Status: review-triggered, result-exposed exploratory comparison fixed after
two literature reviewers identified maximal lotteries, incomplete
zero-sum games, and robust lotteries as close antecedents. Candidate formulas
were visible before this protocol. This is not a preregistration, novelty
proof, or confirmatory analysis.

## Question and decision value

Are P2's minimax-regret Borda lottery, a maximal lottery, an incomplete-game
equilibrium action, and a robust maximal lottery the same decision object on
P2's complete independent edge box?

If the objectives and outputs coincide generally, P2's mathematical
positioning should narrow or merge. If they differ despite selecting the same
lottery on the symmetric box, the manuscript should show the exact
relationship rather than relying on prose.

## Fixed sources and source boundary

- Brandl, Brandt, and Seedig (2016), *Consistent Probabilistic Social Choice*,
  <https://doi.org/10.3982/ECTA13337>.
- Brill, Freeman, and Conitzer (2016), *Computing Possible and Necessary
  Equilibrium Actions (and Bipartisan Set Winners)*,
  <https://doi.org/10.1609/aaai.v30i1.10052>.
- Khalaf et al. (2026), *Robust AI Evaluation through Maximal Lotteries*,
  arXiv:2602.21297v1, <https://arxiv.org/abs/2602.21297>.
- P2 H186/H188 exact Borda-regret results and H192 literature boundary.

The comparison accepts each paper's published objective as a trusted
mathematical input and independently evaluates it on P2's fixed box. It does
not reproduce those papers or establish exhaustive novelty.

## Fixed model

Let \(M\) be a skew-symmetric pairwise margin matrix with

\[
M_{ij}=2q_{ij}-1,\qquad M_{ij}\in[-1/2,1/2]
\]

independently for every \(i<j\). The observed routed half-win matrix is
\(M^0=0\).

Compare:

1. **Observed maximal lottery**
   \[
   \max_p\min_q p^\top M^0q.
   \]
2. **Possible/necessary equilibrium action under incomplete \(M\):** whether
   an action belongs to an equilibrium support for at least one or every
   completion of the box.
3. **Robust maximal lottery**
   \[
   \max_p\min_{M}\min_q p^\top Mq.
   \]
4. **P2 Borda-regret lottery:** minimize worst compatible regret relative to
   the Borda-best policy in the same compatible world.

## Fixed claims to test

1. Every lottery is maximal for the observed zero matrix.
2. Every action is a possible equilibrium action because \(M=0\) is a
   completion.
3. No action is a necessary equilibrium action because, for each action, a
   completion exists with another action as the unique Condorcet winner and
   unique maximin action.
4. For fixed \(p\), the robust maximal-lottery value is
   \[
   -\tfrac12(1-\min_i p_i).
   \]
5. The unique robust maximal lottery is uniform, with margin value
   \[
   -\frac{K-1}{2K},
   \]
   equivalently worst win probability
   \[
   \frac{K+1}{4K}.
   \]
6. P2's Borda-regret objective also uniquely selects the uniform lottery on
   this symmetric box, but its value is regret
   \((K-1)/(4K)\), not a worst head-to-head margin or win probability.

## Fixed computation and challenge

The producer must:

- use exact rational arithmetic;
- exhaust every margin-box endpoint for \(K=3,\ldots,5\);
- cross the endpoint oracle with every pure opponent and exact lottery grids;
- verify the closed form for uniform, every singleton, unequal lotteries, and
  all grid points;
- construct and verify a unique-Condorcet completion excluding each queried
  action;
- reproduce the retained H186 uniform Borda-regret value without importing
  its implementation; and
- fail closed on non-skew matrices, invalid margins, and invalid lotteries.

A distinct implementation in another language must independently reconstruct
the objective values for \(K=3,\ldots,5\), bind exact producer inputs and
outputs, and avoid importing or executing the producer.

## Fixed classification

Classify exactly one:

- `same_uniform_action_different_objectives`;
- `p2_objective_subsumed_by_robust_maximal_lottery`;
- `objectives_select_different_actions_on_symmetric_box`;
- `source_or_model_integrity_failure`; or
- `compute_integrity_failure`.

## Scope and stop rule

This is an exact comparison on P2's symmetric full independent margin box.
It does not characterize arbitrary ambiguity sets, weighted-reference boxes,
asymmetric margins, or every robust social-choice loss. Record those as
separate hypotheses rather than expanding H232 after observing its result.
