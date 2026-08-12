# H213 support-constrained zero-reference boundary challenge

Date: 2026-07-28

Status: pass; hard exclusion of zero-reference policies creates an exact
boundary value jump. No critical or material concern remains.

## Independent derivation

Let

\[
\mathcal P(r)=\{p:\ p_i\geq0,\ \sum_i p_i=1,\ r_i=0\Rightarrow p_i=0\}.
\]

For any zero-reference index \(z\) and \(p\in\mathcal P(r)\), its
candidate-winner objective is

\[
F_z=1+D_r(p),
\qquad
D_r(p)=
\sum_{\substack{i<j\\r_i>0,\ r_j>0}}
|r_jp_i-r_ip_j|.
\]

Thus the robust regret is at least \(1/4\). The reference lottery \(p=r\) is
feasible, has \(D_r(p)=0\), and makes every candidate-winner objective at
most one, so it attains \(1/4\).

Equality requires \(D_r(p)=0\). On positive support this makes every
\(p_i/r_i\) equal; the simplex constraint then gives \(p=r\). With
positive-support size one, feasibility and normalization give the same result
immediately. Therefore, for every nonempty zero set,

\[
\mathcal R^\star_{\mathrm{support}}=\frac14,
\qquad
\arg\min_{p\in\mathcal P(r)}\mathcal R(p)=\{r\}.
\]

If exactly one weight is zero, H212's unrestricted value is
\((2-r_{(2)})/8\), so hard exclusion raises regret by exactly
\(r_{(2)}/8>0\). If exactly two weights are zero, the value remains \(1/4\)
but H212's nonunique segment collapses to its \(h=0\) endpoint \(p=r\). With
at least three zeros, H212 already has that value and unique optimizer.

## Independent exact computation

A separate Ruby implementation using native exact `Rational` arithmetic,
without importing or executing the producer, reconstructed:

- all 242 fixed boundary cases and 242 zero-winner proof identities;
- 117 exact raw target-box endpoint comparisons for \(K\leq5\);
- 14,056 distinct label permutations;
- 7,857 denominator-eight support-constrained simplex lotteries, with all 42
  exact equalities occurring only at \(p=r\);
- 453 accepted exactly-one-zero interior-limit rows; and
- nine positive-interior H188/H212 endpoint checks.

It independently confirms 121 exactly-one-zero value jumps, 69
exactly-two-zero face collapses without value change, and 52 cases with three
or more zeros where H212 is unchanged. The producer's 242 support-constrained
LP values agree exactly at displayed precision, and its optimal-face
coordinate error is at most \(5.21\times10^{-9}\). The LP is diagnostic; the
zero-winner equality proof establishes completeness.

## Attack disposition

The challenge rejects a support-constrained value below \(1/4\), a second
optimizer, a face-only interpretation for exactly one zero, a value increase
for exactly two zeros, an H212 change with at least three zeros, raw/reduced
objective disagreement, and label dependence.

## Disposition, paper placement, and boundary

H213 supports `support_constraint_creates_boundary_value_jump`. The result is
a direct operational boundary of H212 and should be stated as a corollary or
decision-set caveat in P2, not promoted to a separate paper on the present
evidence. Its scientific coherence and proof both depend on H212's model; a
standalone narrative would add packaging, not a distinct research object.

P2 must distinguish:

1. zero opponent-reference weight while the policy remains selectable
   (H212); and
2. zero reference weight plus hard removal from the selectable action set
   (H213).

The result does not determine which meaning a real system intends, select
empirical weights, justify hard exclusion, extend to a soft penalty, or change
the edge-box uncertainty law.

Canonical artifacts:

- [protocol](protocol-h213-support-constrained-zero-reference-boundary.md);
- [producer result](result-h213-support-constrained-zero-reference-boundary.json);
- [independent challenge](result-h213-support-constrained-zero-reference-boundary-independent-challenge.json).
