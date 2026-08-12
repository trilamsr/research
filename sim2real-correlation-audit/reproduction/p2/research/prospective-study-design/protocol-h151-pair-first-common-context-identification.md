# Protocol: H151 pair-first versus common-context identification

Date fixed: 2026-07-27

Status: fixed after H149--H150 established the context-first positive branch
and before executing the exact counterexample below.

## Question

When a policy pair is sampled before the evaluator constructs the task and
scene, does complete pair-type support identify the common-context
uniform-reference policy values targeted by H146/H149?

The smallest useful result is an exact observational-equivalence
counterexample. A negative result changes whether existing pair-first data can
be interpreted through the positive design theorems.

## Public-protocol premise

RoboArena's public paper describes the central server sampling a policy pair
before the evaluator arranges the scene and defines the task. The official
site states that evaluators choose the environment and task for each pairwise
evaluation.

Sources:

- Atreya et al., *RoboArena: Distributed Real-World Evaluation of Generalist
  Robot Policies*, https://arxiv.org/abs/2506.18123 and
  https://openreview.net/pdf/a471fe13a7dbbcf87d41a18be32b45e80671853d.pdf.
- Official site, https://robo-arena.github.io/.

This premise concerns the paper-described order, not an audit of current
server execution.

## Fixed K=3 construction

Use three policies, all three unordered pairs, and two named contexts A and B.
Every pair is assigned with positive probability and may be observed
arbitrarily many times. After the pair is known, the evaluator uses:

- context A for pair 01;
- context B for pair 02; and
- context A for pair 12.

For each realized pair/context route, the observed half-win outcome is fixed
at \(1/2\). The pair-conditioned edge vector is therefore
\((1/2,1/2,1/2)\), and its uniform-reference values tie.

The intended common-context target weights A and B equally for every pair:

\[
x_e=\{Y_{A,e}+Y_{B,e}\}/2.
\]

For each pair, exactly one context-specific potential outcome is observed.
Show that every \(x_e\in[1/4,3/4]\) is compatible with the same observed law
by setting the unobserved outcome to \(2x_e-1/2\).

Retain two explicit worlds:

- world L: all common-target edges equal \(1/4\);
- world H: all common-target edges equal \(3/4\).

Compute exact policy values and show that policy 2 is uniquely best in world
L while policy 0 is uniquely best in world H. Quantify the regret of carrying
either extreme policy across worlds.

## Fixed general statement

The counterexample should establish:

1. complete pair-type support is not common-context support;
2. unlimited repetitions within the same pair-conditioned context routes do
   not shrink the unidentified cross-context potential outcomes;
3. pair-conditioned Borda values remain well-defined as their own estimand;
4. they equal common-context values only under an additional context-order,
   overlap, invariance, or transport assumption; and
5. H149's context-before-pair contract removes this particular ambiguity by
   randomizing pair labels over a fixed context cohort.

Do not claim that pair-conditioned values are useless or that the public
benchmark is invalid. The result is a target distinction.

## Required checks

1. Use exact rational arithmetic throughout.
2. Reconstruct the observed law and pair-conditioned tie.
3. Verify all context-specific potential outcomes remain in \([0,1]\).
4. Verify both worlds induce exactly the same observed pair/outcome law.
5. Compute common-context policy values and unique winners exactly.
6. Exhaust all eight endpoint completions of
   \([1/4,3/4]^3\) and retain singleton worst-regret floors.
7. Reject a context-independent interpretation unless an explicit
   identifying condition is supplied.

## Advancement

Advance if the two worlds are observationally equivalent, reverse the unique
common-context winner, and leave a nonzero regret floor despite complete pair
support.

A pass would create an identification result, not a confidence or prevalence
claim. It would prioritize either a context-lock design or an explicit
pair-conditioned operational target before using pair-first data for policy
selection.
