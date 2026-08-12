# Protocol: H231 shared-binary-success sensitivity

Date fixed: 2026-07-28

Status: review-triggered, result-exposed exploratory sensitivity fixed after
an external-model methods challenge and two preliminary algebraic
reconstructions, but before the canonical producer implementation, finite
case census, or independent implementation. This is not a preregistration or
confirmatory analysis.

## Question and decision value

Do P2's construction-bounded non-identification and minimax conclusions
survive when pairwise comparison scores are not primitive independent edge
responses, but are derived from shared binary policy-success outcomes with
half credit for ties?

The methods challenge correctly notes that a full independent edge box need
not be feasible under a shared per-policy outcome model. If the central
non-identification or robust randomized action disappears under this common
structured alternative, P2 must narrow materially. If those conclusions
survive with changed geometry, the paper should report the sensitivity rather
than imply that the unrestricted box is generic.

## Origin and outcome exposure

The first methods reviewer proposed the shared-binary-success model and
reported the candidate formulas:

- deterministic worst regret \(1/4\);
- unique uniform minimax lottery;
- uniform value \((K-1)/(4K)\); and
- cancellation of opponent-reference weights.

Before this protocol was written, the primary analyst independently derived
the same formulas and ran exact vertex checks for \(K=3,\ldots,8\). A separate
validation reviewer then independently derived the model and ran exact checks
through \(K=6\), with winner witnesses through \(K=8\). These outcomes are
therefore exposed. H231 is exploratory and may support a transparent
sensitivity result only after the fixed canonical computation and independent
challenge pass.

## Fixed model

Let \(K\geq3\) policies share two contexts \(C\in\{A,B\}\), with an
equal-weight common target population. Each policy has a binary success
outcome \(Y_i(C)\in\{0,1\}\). For a pair \(i,j\), score policy \(i\) as one
for a strict success win, zero for a strict loss, and one half for a tie:

\[
Z_{ij}(C)=
\mathbf 1\{Y_i(C)>Y_j(C)\}
+\tfrac12\mathbf 1\{Y_i(C)=Y_j(C)\}.
\]

Write \(s_i(C)=E[Y_i(C)]\). The pair score obeys

\[
E[Z_{ij}(C)]
=\tfrac12+\tfrac12\{s_i(C)-s_j(C)\},
\]

without requiring independence between the two binary outcomes.

Fix every observed pair route to shared context A and require
\(s_i(A)=s_A\) for all policies, so every observed routed pair score is one
half. Let \(x_i=s_i(B)\in[0,1]\). The equal-context target edge is then

\[
q_{ij}=\tfrac12+\tfrac14(x_i-x_j).
\]

For arbitrary fixed nonnegative opponent-reference weights \(r_i\) summing to
one, define

\[
V_i=\sum_j r_jq_{ij}.
\]

For an ex-ante policy lottery \(p\), retain P2's world-specific Borda regret

\[
\mathcal R(p)=
\sup_{x\in[0,1]^K}
\left\{\max_iV_i-\sum_i p_iV_i\right\}.
\]

## Fixed claims to test

1. **Geometry.** The compatible target edges form the gradient image
   \[
   q_{ij}=\tfrac12+\tfrac14(x_i-x_j),
   \]
   not the full independent box. In particular,
   \(\delta_{ik}=\delta_{ij}+\delta_{jk}\).
2. **Non-identification.** The same complete-support observed half-win law is
   compatible with opposite unique common-context Borda winners for every
   \(K\geq3\), using \(x=e_1\) and \(x=e_K\).
3. **Reference cancellation.**
   \[
   V_i=\tfrac12+\tfrac14(x_i-r^\top x)
   \]
   and therefore
   \[
   \mathcal R(p)=\tfrac14(1-\min_i p_i),
   \]
   independent of \(r\).
4. **Exact minimax.** Every deterministic policy has worst regret \(1/4\).
   The unique minimax lottery is uniform, with value
   \((K-1)/(4K)\).
5. **Comparison with the unrestricted edge box.** The structured model
   preserves the unrestricted model's uniform minimax value but reduces
   deterministic worst regret from \((K-1)/(2K)\) to \(1/4\).

## Fixed computation and validation

The producer must:

1. derive the binary half-tie identity exactly;
2. enumerate every \(x\in\{0,1\}^K\) for \(K=3,\ldots,8\);
3. test uniform, every singleton, unequal fixed lotteries, and an exact
   simplex grid for \(K=3,\ldots,6\);
4. cross at least uniform, unequal-positive, one-zero, two-zero, and
   singleton opponent-reference vectors;
5. verify opposite unique-winner witnesses for every \(K=3,\ldots,64\);
6. verify label-permutation invariance and the gradient cycle equalities; and
7. fail closed on invalid dimensions, negative or non-normalized weights,
   invalid binary-success means, and incomplete edge maps.

Before reliance, a distinct implementation in another language must:

- avoid importing or executing the producer;
- reconstruct the exact vertex census for \(K=3,\ldots,7\);
- verify all five fixed claims using exact integer or rational arithmetic; and
- bind its result to the producer protocol, implementation, and canonical
  output hashes.

## Fixed classification

Classify exactly one:

- `central_result_survives_with_gradient_geometry`;
- `nonidentification_survives_but_minimax_changes`;
- `central_nonidentification_fails_under_shared_success`;
- `input_or_model_integrity_failure`; or
- `compute_integrity_failure`.

## Scope and stop rule

This sensitivity concerns one equal-weight two-context construction, shared
binary success, half credit for ties, all routed comparisons in context A,
and an unrestricted vector of context-B marginal success probabilities.
It is not a theorem for continuous scores, random-utility comparisons,
context-dependent measurement error, empirical robot success, every
pair-first design, or every structured response model.

Stop after the fixed shared-binary-success analysis. Record other structured
response classes as hypotheses; do not add them to H231 after inspecting its
result.
