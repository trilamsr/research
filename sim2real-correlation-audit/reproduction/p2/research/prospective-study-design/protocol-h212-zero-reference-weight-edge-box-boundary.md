# Protocol: H212 zero-reference-weight edge-box boundary

Date fixed: 2026-07-28

Status: result-exposed exploratory theorem-boundary audit fixed after H188,
but before computing or optimizing any reference vector containing a zero.
This is not a preregistration or confirmatory analysis.

## Question and decision value

Does H188's weighted full-edge-box minimax value and complete optimizer
segment extend from strictly positive opponent-reference weights to the
closed probability simplex, where one or more policies can receive zero
reference weight?

Zero weights are operationally plausible when a decision target excludes
opponents. If the value extends but the optimizer face changes, the paper
should say so. If the value formula fails, H188's positive-weight boundary
must remain explicit. This audit concerns theorem scope, not a choice of
empirical weights.

## Fixed inputs

- H188 protocol, SHA-256
  `0391adc2b80152b136bee5b470f2b4f3bfbec64b39b811af54d6ff65a1bd459e`.
- H188 result, SHA-256
  `e5721a0918c8f97f1a076b6d00b9a9f9e323261f71d9e6093b1cec307709800a`.
- H188 independent review, SHA-256
  `14323db710ef389de390bfee220eb87379468eda1cce14b1545b566687be67eb`.
- H188 implementation and tests, SHA-256
  `4ce70305dcba09d317880bbedd134d762c7018915d7405469953cf8cfb1a766f`
  and
  `383d16e41cf833822791233ad854d3c03f91459e44d482a3dacb3d9613697ddb`.

Require the retained H188 result and review disposition exactly. Do not
modify H188 after seeing H212.

## Fixed model and estimand

For \(K\ge3\), let \(r_i\ge0\), \(\sum_i r_i=1\), and

\[
V_i=\sum_j r_jq_{ij},\qquad q_{ii}=1/2,\quad
q_{ij}\in[1/4,3/4],\quad q_{ji}=1-q_{ij}.
\]

For an ex-ante lottery \(p\), retain H188's exact reduced objective

\[
\mathcal R(p)=\frac14\max_w\left[
1-p_w+\sum_{i<j,\ i,j\ne w}|r_jp_i-r_ip_j|
\right].
\]

Determine the minimax value and complete optimizer set for nonnegative
reference weights. Treat support sizes one, two, and at least three
separately if required.

## Fixed analyses

1. **Formula continuation.** For every case, test the continuous H188 value
   candidate \((2-r_{(1)}-r_{(2)})/8\), where order statistics include zeros.
2. **Optimizer continuation.** Test whether limits of H188's positive-weight
   segment exhaust the boundary optimizer set or whether new optimal
   directions/faces appear.
3. **Support reduction.** Test whether zero-reference policies can or must
   receive ex-ante lottery mass and whether the problem reduces to the
   positive support.
4. **Exact cases.** Use all zero-pattern orbits for \(K=3,\ldots,6\) crossed
   with positive integer support weights from \(\{1,2,3,4\}\), normalized
   exactly. Include support sizes one through \(K-1\), all label
   permutations needed to test invariance, and explicit limits approaching
   each zero pattern from positive weights.
5. **Raw endpoint oracle.** For \(K\le5\), independently enumerate all
   \(2^{K(K-1)/2}\) target-edge endpoints and require exact agreement with the
   reduced objective at every retained rational lottery probe.
6. **Optimal-face reconstruction.** Use linear programming only to discover
   candidate vertices/directions. Convert every retained claim to exact
   rational equalities/inequalities and test complete optimal faces, not only
   one solver-returned point.

Do not select one optimizer as preferred when the complete face is
non-unique.

## Fixed classification

Classify exactly one:

- `value_and_optimizer_extend_without_change`;
- `value_extends_but_optimizer_face_changes`;
- `value_formula_fails_on_boundary`;
- `input_drift_or_integrity_failure`; or
- `compute_integrity_failure`.

## Staged validation and independent challenge

Before material boundary optimization:

1. verify every fixed hash and exact H188 rebuild;
2. test nonnegative normalization, simplex, tie, label-permutation, and
   zero-pattern enumeration on synthetic known answers;
3. verify the reduced objective against raw endpoint enumeration on constant,
   singleton-lottery, and uniform-reference controls;
4. verify that the positive interior cases still reproduce H188 exactly; and
5. exercise LP infeasibility, unboundedness, tolerance, duplicate-vertex, and
   rational-reconstruction fail-closed paths on synthetic cases.

Before manuscript reliance, independently derive the boundary result and
reconstruct the exact case census with a distinct implementation that does
not import or execute the producer.

## Scope and stop rule

This is one weighted-Borda full compatible edge box and ex-ante expected
regret. It is not an empirical reference distribution, pair-sampling design,
deployment lottery, realized-policy guarantee, or theorem for every observed
law.

Stop after the fixed closed-simplex boundary. Do not vary edge widths, target
aggregation, observed law, loss, or empirical roster; do not use outcomes or
select a reference vector for the paper.
