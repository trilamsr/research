# Protocol: H186 full-roster compatible-edge-box minimax

Date fixed: 2026-07-27

Status: fixed before implementing or evaluating the full roster edge box.

## Research question and impact

H183--H185 establish identification and minimax consequences by embedding a
three-policy core, padding it with dominated policies, and holding noncore
target edges fixed. The most important formal scope attack is therefore that
the arbitrary-\(K\) result is inherited from a small core rather than arising
over the full compatible \(K\)-policy comparison structure.

For every \(K\geq3\), consider a pair-first observed law in which every pair is
observed with win probability \(1/2\) on its routed context. Let every
common-context pairwise win probability vary independently over
\([1/4,3/4]\), with complementary reverse outcomes. This is the full
\(\binom K2\)-edge compatible box for that observed law.

The question is whether exact minimax regret over this full box is:

- \((K-1)/(2K)\) for deterministic singleton selection; and
- \((K-1)/(4K)\) for ex-ante randomized selection, uniquely attained by the
  uniform lottery over all \(K\) policies.

If true, this removes dominated padding and fixed noncore target edges from
the minimax result. It would still be a constructed observed law, not a claim
about every empirical roster or protocol.

## Fixed estimand and compatible class

For unordered pair \(\{i,j\}\), let the target-context probability that
\(i\) beats \(j\) be

\[
q_{ij}=\tfrac12+\delta_{ij},\qquad
\delta_{ij}\in[-1/4,1/4],
\]

with \(\delta_{ji}=-\delta_{ij}\). Define the normalized target value

\[
V_i=\frac{\tfrac12+\sum_{j\ne i}q_{ij}}{K}.
\]

For an ex-ante probability vector \(p\in\Delta^{K-1}\), fixed independently
of the compatible world and realized policy draw, define worst-case expected
regret

\[
\mathcal R(p)=
\sup_{\delta}
\left\{\max_w V_w-\sum_i p_iV_i\right\}.
\]

For a fixed candidate winner \(w\), set \(c_i=\mathbf 1\{i=w\}-p_i\).
Independent edge extrema imply the proposed exact formula

\[
\mathcal R(p)=
\frac1{4K}\max_w\sum_{i<j}|c_i-c_j|.
\]

At uniform \(p\), the sum is \(K-1\). Averaging the sum over \(w\) gives

\[
\frac1K\sum_w\sum_{i<j}|c_i-c_j|
=K-1+\frac{K-2}{K}\sum_{i<j}|p_i-p_j|,
\]

so the proposed randomized minimizer is uniquely uniform.

## Smallest informative test

1. Derive the formula symbolically from independent edge extrema.
2. Compare it with exact enumeration of all \(2^{\binom K2}\) endpoints for
   every fixed candidate mixture at \(K=3,\ldots,6\).
3. Check the closed form for symmetric and asymmetric rational mixtures
   through \(K=32\).
4. Construct compatible potential outcomes and verify identical observed laws
   for representative endpoint worlds.

## Passing claims

The hypothesis passes only if exact arithmetic shows:

1. every deterministic singleton has worst compatible regret
   \((K-1)/(2K)\);
2. the unique randomized minimizer is uniform on all \(K\) policies;
3. its worst compatible expected regret is \((K-1)/(4K)\);
4. the randomized value is exactly half the deterministic value;
5. endpoint enumeration agrees with the arbitrary-weight formula; and
6. all constructed worlds preserve the same complete-support observed
   half-win law with valid hidden-context probabilities.

## Stop and scope rules

- Preserve any counterexample to the formula, uniqueness, or factor-of-two
  claim.
- Do not shrink the edge box, reintroduce fixed noncore schedules, or select a
  different observed law after seeing results.
- Do not call this a theorem about every pair-first observed distribution,
  empirical roster, evaluation system, or target action.
- Do not equate expected regret of an ex-ante lottery with realized-policy
  worst regret.
- Do not use public outcomes.

## Advancement gate

A producer pass remains provisional. Before P2 manuscript reliance, require a
separately implemented or symbolic challenge of the arbitrary-weight formula,
the minimax uniqueness proof, the compatibility construction, and the stated
scope.
