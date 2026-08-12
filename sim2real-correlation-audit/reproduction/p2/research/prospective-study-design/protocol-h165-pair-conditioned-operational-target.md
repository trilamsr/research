# Protocol: H165 pair-conditioned operational target

Date fixed: 2026-07-27

Status: fixed after H151--H152 established the common-context
non-identification result and H162--H164 clarified the public mechanical and
site-feasibility boundaries, before executing the exact known-answer checks
below.

## Question

When a context is constructed after a policy pair is known and no
common-context physical target is justified, which operational decisions can
pair-conditioned edge estimates support, and which interpretations must the
program refuse?

For each unordered pair \(a<b\), define the mechanism-specific estimand

\[
\theta^{pc}_{ab}=E_{C\sim G_{ab}}[Z_{ab}(C)],
\qquad
\theta^{pc}_{ba}=1-\theta^{pc}_{ab},
\]

where \(G_{ab}\) is the context-generation mechanism used for that pair.
This is a pair-conditioned comparison edge. It is not, without another
identification argument, a single policy's task-success rate or its value in
a common deployment population.

## Supported operational targets

### Same-route pair choice

For a future choice between the same pair under the same \(G_{ab}\), choose
\(a\) when \(\theta^{pc}_{ab}>1/2\), choose \(b\) when it is below \(1/2\),
and apply a declared tie or abstention rule when it equals \(1/2\).

### Pair-routing rule

Suppose a future unordered pair is drawn from a fixed, outcome-independent
distribution \(\pi\), after which the same pair-specific context mechanism
\(G_{ab}\) is used. A routing rule \(\delta(a,b)\in\{a,b\}\) has value

\[
V^{pc}(\delta)=
\sum_{a<b}\pi_{ab}\left[
1\{\delta(a,b)=a\}\theta^{pc}_{ab}
+1\{\delta(a,b)=b\}(1-\theta^{pc}_{ab})
\right].
\]

Because the objective is separable by edge, choosing the locally preferred
member of every positive-weight pair is optimal for this routing action.

### Mechanism-specific tournament score

A score such as

\[
v_i^{pc}=\sum_j w_j q_{ij}^{pc},\qquad q_{ii}^{pc}=1/2,
\]

is also well-defined. It is operational only when that tournament score is
itself the declared action target. It must not be renamed common-population
deployment success.

## Required refusals without additional identification

Refuse:

1. selection of one best policy for a common task population;
2. per-policy task-success claims from comparative outcomes alone;
3. causal-effect claims about the evaluator or simulator;
4. transport to new policies, tasks, sites, or context mechanisms;
5. outcome-dependent pair weights;
6. decisions on unmeasured positive-weight edges; and
7. a context-independent interpretation of a mechanism-specific tournament
   ranking.

Any of these may become identifiable under separately recorded overlap,
invariance, randomization, bridge, or transport assumptions. H165 does not
supply those assumptions.

## Fixed K=3 known-answer construction

Use the three unordered pairs 01, 02, and 12 with uniform routing weights
\(\pi_{ab}=1/3\), and set

\[
(\theta^{pc}_{01},\theta^{pc}_{02},\theta^{pc}_{12})
=(3/4,1/4,3/4).
\]

The edge preferences form the cycle \(0>1\), \(1>2\), \(2>0\). The
edge-optimal routing rule chooses 0 for pair 01, 2 for pair 02, and 1 for pair
12, with exact value \(3/4\). The always-lower-index rule chooses 0, 0, and 1
and has exact value \(7/12\), hence regret \(1/6\).

The uniform-reference tournament scores for all three policies are exactly
\(1/2\). The tournament tie does not erase the pair-routing advantage, and
the routing advantage does not identify a unique global policy.

Reuse H151's all-half observed-law construction to retain the converse
warning: a pair-conditioned tournament tie is compatible with opposite
unique common-context winners and a \(1/3\) singleton regret floor. H152 must
independently agree with those facts.

## Reporting gate

Report a pair-routing value only when all of the following are explicit:

1. the operational action is choosing within a presented pair;
2. \(\pi\) was fixed independently of outcomes;
3. every positive-weight edge is identified or honestly bounded;
4. future observations use the same declared \(G_{ab}\);
5. edge orientation and tie handling are fixed; and
6. uncertainty respects the actual assignment and clustering structure.

H165 concerns identification semantics only. It does not specify a confidence
procedure, qualify a real site, or authorize field collection.

## Required checks

1. Use exact rational arithmetic.
2. Verify the three-edge cycle and edgewise-optimal route choices.
3. Verify routing values \(3/4\) and \(7/12\), and regret \(1/6\).
4. Verify the uniform-reference tournament tie at \(1/2\).
5. Hash-bind and verify the material H151 and H152 facts.
6. Reject promotion to every unsupported interpretation listed above.
7. Refuse a routing-value claim after removing any positive-weight edge.
8. Reproduce the canonical result byte-for-byte.

## Advancement

Advance if the known-answer construction shows that pair-conditioned evidence
can support a useful, explicit pair-routing action while neither identifying
a unique global policy nor escaping H151's common-context ambiguity.

This is a boundary and target-specification result within the prospective
study design. It is not asserted as standalone paper novelty.
