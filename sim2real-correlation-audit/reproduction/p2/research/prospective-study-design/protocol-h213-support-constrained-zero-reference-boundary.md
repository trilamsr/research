# Protocol: H213 support-constrained zero-reference boundary

Date fixed: 2026-07-28

Status: result-exposed exploratory decision-set audit. H212's closed-simplex
result is known. Before this protocol was fixed, inspection of H212's
exactly-one-zero optimizer and preliminary algebra exposed the possibility
that forbidding selection of zero-reference policies raises the minimax
value. The direction and candidate formula are therefore not confirmatory or
preregistered.

## Question and decision value

H212 allows an ex-ante lottery to select a policy even when its
opponent-reference weight is zero. What changes if zero reference weight also
means that the policy is outside the selectable action set?

This distinction is operationally material. A zero may mean “excluded from
the opponent population but still selectable” or “excluded from the decision
entirely.” If those meanings have different robust values, P2 must state
which decision set its theorem uses rather than treating zero weights as a
purely technical boundary.

## Fixed inputs

- H212 protocol, SHA-256
  `2204934e1e4729a0d1dff29b89e544c0da59b654d01a6270655265eda5b61e7c`.
- H212 producer result, SHA-256
  `60197dc7967bdb388d0707299c6652403e289c2fc58a010d7a121a17b78f839e`.
- H212 independent challenge, SHA-256
  `405b0d2fd7805d4d3e6b569635a1e13a5fb942bf4038344feebdc0a42dcd28d1`.
- H212 review, SHA-256
  `a41a7193a7c3adede901b9e0b4d135c056072d5ed1fb19453720fff056a0774d`.
- H212 implementation and tests, SHA-256
  `81f29991e0ba2cc343af9fe0c614705eed1d401a6076af2c38b1d1915de2f99a`
  and
  `08eb666e761e22285dd1718515e79d52f735c4fc96076dadbd4438b8d93da2b1`.

Require the retained H212 classification and review disposition exactly. Do
not modify H212 after H213 computation.

## Fixed model and estimand

Retain H212's \(K\geq3\), nonnegative normalized reference vector, compatible
full edge box, weighted-Borda values, and ex-ante expected regret:

\[
\mathcal R(p)=\frac14\max_w\left[
1-p_w+\sum_{i<j,\ i,j\ne w}|r_jp_i-r_ip_j|
\right].
\]

Change only the decision set:

\[
\mathcal P(r)=\left\{p:\ p_i\geq0,\ \sum_i p_i=1,\quad
r_i=0\Rightarrow p_i=0\right\}.
\]

Call this the support-constrained problem. H212 is the unrestricted
closed-simplex comparator.

## Fixed analyses

1. **Interior parity.** Require the support constraint to reproduce H188/H212
   whenever all \(r_i>0\).
2. **Boundary value and face.** For every nonempty zero set, determine the
   exact minimax value and complete optimizer set over \(\mathcal P(r)\).
3. **Zero-winner lower bound.** For a zero-reference winner \(z\), isolate
   \(F_z=1+D_r(p)\), where \(D_r(p)\) is dispersion within the positive
   support. Determine the exact equality conditions, including support size
   one.
4. **H212 comparison.** Report value and optimizer-set differences separately
   for exactly one zero, exactly two zeros, and at least three zeros. Do not
   call a face change a value change.
5. **Action-set limit.** For exactly-one-zero cases, use the exact interior
   sequence \(r_z=\epsilon\), \(r_i=(1-\epsilon)r_i^{(0)}\) with
   \(\epsilon\in\{1/10,1/100,1/1000,1/10000\}\), after rejecting values that
   alter the two-smallest order. Compare the unrestricted interior limit with
   the support-constrained boundary value.
6. **Exact census.** Reuse all 242 H212 canonical zero-pattern/positive-weight
   cases for \(K=3,\ldots,6\), all distinct label permutations, exact raw
   endpoint enumeration for \(K\leq5\), and denominator-eight simplex grids
   restricted to \(\mathcal P(r)\).
7. **Optimal-face reconstruction.** Use numerical linear programming only as
   a challenge. Retained value and completeness claims must be exact rational
   consequences of the zero-winner lower bound and equality conditions.

## Fixed classification

Classify exactly one:

- `support_constraint_creates_boundary_value_jump`;
- `support_constraint_changes_optimizer_face_only`;
- `no_support_constraint_effect`;
- `input_drift_or_integrity_failure`; or
- `compute_integrity_failure`.

## Staged validation and independent challenge

Before material computation:

1. verify all fixed hashes and exact H212 rebuild;
2. test support-mask enforcement, simplex validation, and label invariance on
   known answers;
3. verify reduced versus raw endpoint regret on singleton-support,
   two-support, and positive-interior controls;
4. verify an LP with explicit \(p_i=0\) bounds on zero-reference indices; and
5. exercise infeasible, unbounded, tolerance, and rational-reconstruction
   fail-closed controls.

Before manuscript reliance, independently derive the result and reconstruct
the fixed census with a distinct implementation that does not import or
execute the producer.

## Scope and stop rule

This is one hard support constraint for the same weighted-Borda full
compatible edge box and ex-ante regret. Stop after its exact boundary. Do not
vary edge widths, add soft exclusion penalties, choose empirical weights,
change target aggregation, inspect outcomes, or infer which meaning of zero a
real system intends without source evidence.
