---
title: "When Candidate-Dependent Context Can Leave a Common-Context Robot-Policy Winner Unidentified"
subtitle: "Exact regret, graph repair, and finite-sample decisions"
author: "Tri Lam"
date: "2026-08-11"
---

# Abstract

Pairwise robot-policy evaluations may report a global ranking even when each
pair is tested in a different physical setting. Even with every pair observed,
pair-specific contexts can admit opposite common-context winners. Under
primitive pair responses, the constructed full-edge ambiguity set has a unique
uniform minimax lottery, with regret \((K-1)/(4K)\). A shared-binary-success
sensitivity preserves that lottery and value, but the ambiguity then comes
from missing target-context support rather than candidate-dependent routing.

In the shared-success model, identifying all within-context policy differences
requires \(m-1\) comparable bridge types when the route graph has \(m\)
components and the allowable bridge graph is connected. Repeating existing
routes improves precision, not connectivity.

Simultaneous edge intervals propagate through the same graph constraints to
target-difference bounds, possible and certified winners, and a minimax action
by linear programming. Under an exact Bradley--Terry target, the winner set is
identified exactly when the common-context comparison graph is connected.

Three pinned records show the operational distinction. Complete common-state
panels identify exact finite-panel winners in three AnkIle tasks. RoboArena's
pair-support graph remains incomplete and lacks a common-context bridge, while
TRI's released outcome tables omit the trial keys needed to reconstruct its
published matched-bundle protocol.

## Practitioner summary

- If the evaluated pair can change the task or scene, a precise pairwise
  leaderboard may still fail to determine which single policy is best for one
  common deployment population.
- The route graph diagnoses the structural gap: disconnected policy groups
  need safe, comparable cross-group comparisons in the same declared context.
- In the shared-success model, \(m-1\) bridge types identify all within-context
  differences across \(m\) components when allowable bridges connect them.
- With finite samples, use jointly valid edge intervals; the graph program
  inherits their coverage but cannot repair invalid sampling units.
- Connectivity does not ensure precision, validity, or safety.

# 1. The decision precedes the score

A robot-policy comparison can support several distinct actions:

1. choose one policy for a common deployment population;
2. choose between two policies presented under the same pair-specific
   mechanism;
3. make a same-mechanism choice within each future presented pair; or
4. report a mechanism-specific tournament score.

These actions are not interchangeable. A complete table of pairwise win
probabilities identifies a tournament under the mechanisms that generated its
edges. It need not identify how the policies compare in a common physical
context population. The distinction matters when the evaluated pair can
change the task, scene, operator behavior, or other context.

We distinguish identification, minimax decisions under ambiguity, and evidence
connecting the target to a real system. We apply established ideas from partial
identification, minimax regret, randomized decisions, Borda ranking, comparison
graphs, and target-first evaluation to candidate-dependent physical contexts.

The closest antecedents already establish interval decisions, graph-based score
identifiability and precision, and robust lotteries. Our scoped contribution is
their interaction here: an exact candidate-dependent-context construction, its
edge-coupled regret values, a route-colored decision program, and an executable
finite-sample interface.

# 2. Pair-first context can leave the global action unidentified

## 2.1 Target and observed routes

Let \(K\geq3\) policies be indexed by \(i=1,\ldots,K\), and let one shared
context variable \(C\) have the target distribution. For a common-context
target, write \(q_{ij}\) for policy \(i\)'s expected half-credit comparison
score against \(j\), with \(q_{ji}=1-q_{ij}\) and \(q_{ii}=1/2\). This score
may be a conditional comparison probability or a deterministic fractional
score. The unrestricted construction below treats pair responses as
primitive and imposes no shared scalar-outcome, random-utility,
stochastic-transitivity, or cross-edge coherence constraint. Under the
uniform-reference normalized Borda target,

\[
V_i=\frac{\tfrac12+\sum_{j\ne i}q_{ij}}{K}.
\]

Borda is the declared comparison target. It equals success-mean ordering in
the shared-binary model below, but is not a generic deployment utility.

Now suppose the policy pair is selected before context is constructed. The
observed edge for pair \(\{i,j\}\) averages outcomes under a pair-specific
context mechanism \(G_{ij}\), not necessarily under the common target
population.

## 2.2 Observational-equivalence result

Let the one shared context variable take values A and B with equal target
weight. Each pair has a route \(G_{ij}\), degenerate at one of those shared
contexts. Fix the complete routed score law as a deterministic half tie.
Choose the hidden context-specific primitive pair score so that the target
edge can take any value in \([1/4,3/4]\). These context weights differ from
Theorem 3's opponent-reference weights. All completions generate the same
observed route/context/score law.
Two explicit completions reverse the unique common-context winner.

For every finite \(K\geq3\), one complete-support pair-first half-win law is
compatible with the full primitive-response box

\[
q_{ij}=\tfrac12+\delta_{ij},\qquad
\delta_{ij}\in[-1/4,1/4],
\]

independently for all \(\binom K2\) unordered pairs.

**Theorem 1 (construction-bounded non-identification).** For every
\(K\geq3\), there is a pair-first, complete-pair-support observed law for
which all compatible worlds agree on every observed route but the
common-context Borda winner is not identified. Repeating the same routed
comparisons without a bridge does not shrink this compatible target box.

Construction and proof:
[Supplement S1](SUPPLEMENT-identification-to-operation.md#s1-compatible-worlds-and-theorem-1).
This counterexample does not apply to every pair-first design.

# 3. Exact minimax-regret solutions for the constructed edge box

## 3.1 Uniform opponent reference

Let \(p\) be a policy lottery, used here as an ambiguity benchmark rather than
a deployment recommendation, chosen before the compatible world and policy
draw. Its worst-compatible expected regret is

\[
\mathcal R(p)=
\sup_q\left\{\max_wV_w-\sum_i p_iV_i\right\}.
\]

For a fixed candidate winner \(w\), independent edge extrema yield

\[
\mathcal R(p)=\frac1{4K}
\max_w\sum_{i<j}
\left|\{\mathbf1(i=w)-p_i\}-\{\mathbf1(j=w)-p_j\}\right|.
\]

**Theorem 2 (full-edge uniform-reference minimax).** In this compatible box:

- every deterministic singleton has worst-compatible regret
  \((K-1)/(2K)\);
- the unique minimax lottery is uniform over all \(K\) policies;
- its worst-compatible expected regret is \((K-1)/(4K)\).

Proof:
[Supplement S2](SUPPLEMENT-identification-to-operation.md#s2-uniform-reference-edge-coupled-minimax).

The factor of two concerns ex-ante expected regret. It does not halve the
worst regret of the realized policy.

Each policy's marginal interval has width \((K-1)/(2K)\), which already gives
the deterministic regret in Stoye's arbitrary-treatment interval model. An
independent product box would give uniform-lottery regret
\((K-1)^2/(2K^2)\). Our smaller value comes from antisymmetric edge coupling:
states with one policy at its upper bound and every other policy at its lower
bound are infeasible. Supplement S6 gives the comparison.

## 3.2 Arbitrary nonnegative opponent reference

Let nonnegative reference weights \(r_i\) sum to one and define

\[
V_i=\sum_j r_jq_{ij}.
\]

Order the three smallest weights as
\(a=r_{(1)}\leq b=r_{(2)}\leq g=r_{(3)}\). The robust objective reduces to

\[
\mathcal R(p)=\frac14\max_w
\left[1-p_w+\sum_{\substack{i<j\\i,j\ne w}}
|r_jp_i-r_ip_j|\right].
\]

**Theorem 3 (weighted-reference minimax).** The exact minimax value is

\[
\mathcal R^\star=\frac{2-a-b}{8}.
\]

The minimizers form the line segment in Supplement S3 and are unique exactly
when the second- and third-smallest reference weights are equal.

**Corollary 3.1 (hard support exclusion).** If the lottery must assign zero
mass to zero-reference policies while those policies remain possible oracle
comparators, \(p=r\) is uniquely minimax with value \(1/4\) whenever any
reference weight is zero (Supplement S3).

Here \(r\) is the opponent-reference distribution, not the pair-sampling
distribution or policy lottery \(p\). Its empirical choice lies outside the
theorem.

## 3.3 Shared-success sensitivity

Under a shared binary success outcome \(Y_i(C)\), a pair receives one point for
a strict success win and one half for a tie. Route every observed pair
through shared context A with identical policy outcomes, and let
\(x_i=E[Y_i(B)]\in[0,1]\). Then

\[
q_{ij}=\tfrac12+\tfrac14(x_i-x_j).
\]

The compatible edges form a gradient polytope satisfying
\(\delta_{ik}=\delta_{ij}+\delta_{jk}\), not the full independent box.
Nevertheless, \(x=e_1\) and \(x=e_K\) give opposite unique
common-context winners while preserving the complete observed half-tie law.
For any opponent-reference distribution \(r\),

\[
V_i=\tfrac12+\tfrac14(x_i-r^\top x),\qquad
\mathcal R(p)=\tfrac14(1-\min_i p_i).
\]

Thus deterministic worst regret becomes \(1/4\), while the unique uniform
minimax lottery and value \((K-1)/(4K)\) are unchanged and \(r\) cancels.
Theorem 3's weighted optimizer face and Corollary 3.1's uniqueness are
therefore response-model dependent. This reflects missing target-context
support, not candidate-dependent routing (Supplement S4).

If the observed-context success profile has range \(D<1\), any policy can be
uniquely best under a compatible missing-context completion within the
shared-success model (Supplement S4).

## 3.4 Candidate-dependent route graphs

For each positive-target-weight context \(c\), form a route graph whose edges
are the pairs observed there. Policy-success means are identified up to one
additive offset per component. Connected graphs identify all contextwise
differences; disconnected components can retain target-relevant offsets when
the outcome bounds leave slack. The exact criterion is zero compatible width
for every target difference, not connectivity alone (Supplement S4).

In a three-policy example, pair 1--2 routes through B while 1--3 and
2--3 route through A. The routed law is compatible with unique common-target
winners 1 and 3. Its ex-ante minimax lottery is uniquely
\((2/3,0,1/3)\), with regret \(1/12\), rather than the uniform lottery above.
The corresponding minimax action is a linear program (Supplement S4).

If a context graph has \(m\) components, \(m-1\) cross-component pair types
are necessary and sufficient when the allowable-pair quotient graph is
connected; with costs, a minimum spanning tree gives the cheapest repair
(Supplement S4).

### 3.4.1 Hypothetical robot design

Suppose policies \(A,B,C\) are evaluated in near and far reset strata. Near
comparisons \(A\!-\!C\) and \(B\!-\!C\) connect the roster, but far contains
only \(A\!-\!B\). Adding either safe \(C\!-\!A\) or \(C\!-\!B\) far-stratum
comparison closes the gap. The bridge requires comparable randomized trials,
recorded policy and reset lineage, and a separate precision analysis.

### 3.4.2 Finite samples

Replace each exact edge equation by a simultaneous interval,
\(\ell_c\leq E_cx^c\leq u_c\). Linear programs then give sharp bounds on every
target difference, the policies that can still win, any winner certified
against all compatible values, and the minimax lottery. If the edge intervals
jointly cover with probability \(1-\alpha\), these projected statements inherit
that coverage. They do not repair dependence, adaptive sampling, or target
drift (Supplement S4.3).

### 3.4.3 Bradley--Terry structure

Suppose exact common-context comparisons obey
\(q_{ij}=\sigma(s_i-s_j)\). Applying the inverse link to each observed edge
identifies score differences along paths. The Borda-winner set is therefore
identified exactly when the comparison graph is connected; a unique winner
also requires a unique largest score. Disconnected components retain separate
offsets and need bridges. This is an established graph-identifiability
consequence, not a new Bradley--Terry result (Supplement S4.4).

## 3.5 Relation to maximal and robust lotteries

On the observed zero margin matrix, every lottery is maximal. Robust maximal
and Borda-regret rules both select the uniform lottery here but use different
losses and adversaries (Supplement S5).

# 4. A different action can remain identified

For each pair \(a<b\), define the mechanism-specific edge

\[
\theta^{pc}_{ab}=E_{C\sim G_{ab}}[Z_{ab}(C)].
\]

If a future unordered pair is drawn from a fixed outcome-independent law
\(\pi\), and the same \(G_{ab}\) will be used, a routing rule has value

\[
V^{pc}(\delta)=\sum_{a<b}\pi_{ab}
\left[
\mathbf1\{\delta(a,b)=a\}\theta^{pc}_{ab}
+\mathbf1\{\delta(a,b)=b\}(1-\theta^{pc}_{ab})
\right].
\]

The objective is separable, so the optimal same-mechanism within-pair choice
selects the locally preferred member of each positive-weight pair.

In a three-edge example, the local rule has value \(3/4\), while always
choosing the lower-index policy has value \(7/12\), even though all tournament
scores tie at \(1/2\). This target requires a fixed future pair law, positive
edge support, stable pair mechanisms, and assignment-aware uncertainty
(Supplement S5).

# 5. What public records can identify

We fixed three public releases before aggregate analysis. They are purposive
examples, and missing public fields do not imply private absence.

## 5.1 A positive finite-panel case

Three AnkIle R5 releases each run three fixed policy artifacts on the same 50
declared Sobol states: routing, marker, and square
([routing](https://huggingface.co/datasets/ankile/real01b-routing-d1-r5-threearm-checkpoint100000-iql-g0997-n16-heldout-sobol50);
[marker](https://huggingface.co/datasets/ankile/real01b-marker-d2-r5-trio-baseline-dp-iql-cfinal-n16-heval-sobolseed2026070704);
[square](https://huggingface.co/datasets/ankile/real01b-square-d2-r5-trio-baseline-dp-iql-s3fixfinal-n16-heval-sobolseed2026070901)).
All 450 policy-state cells are present. The success counts are ((8,9,12)),
((19,32,31)), and ((28,36,33)), so the exact released-panel winner is
identified in each task, by margins of 3, 1, and 3 successes. Each three-edge
route graph is complete.

This identifies only the displayed states. One rollout per cell supplies no
population uncertainty law, and the files do not reconstruct achieved reset
acceptance or the full retry ledger. The omission can matter at the scale of
the reported differences. Under a worst-case sensitivity that replaces an
entire retained three-policy round by another binary outcome vector, reversing
the released winner requires only two routing rounds, one marker round, or two
square rounds. This is not evidence that any such replacement occurred. The
released configuration enables incomplete-round reruns for routing and marker,
but not square, so the retained attempt history is needed to distinguish a
stable result from selection through reruns.

## 5.2 Pair support is not a common-context graph

The pinned RoboArena release contains 3,883 sessions, 21 policy labels, and 104
of 210 possible label pairs
([data](https://huggingface.co/datasets/RoboArena/DataDump_07-17-2026);
[paper](https://proceedings.mlr.press/v305/atreya25a.html)). One unpaired label
forms a separate component; the other 20 labels are connected. Twenty-seven
observed edges appear in only one session.

This is policy-pair support, not the contextwise route graph of Section 3.4.
Tasks and scenes are constructed for the selected pair, and the release does
not bind assignment weights or pool epochs, exact initial states and resets,
robot instances, or retry ancestry to a common target. Connectivity among the
20 compared labels therefore does not identify a common-context winner.

## 5.3 A strong protocol can lose its join at release

TRI reports 1,800 real-world rollouts in blind, randomized test bundles that
hold the initial condition across compared policies
([paper](https://arxiv.org/html/2507.05331v1);
[data](https://datadryad.org/dataset/doi%3A10.5061/dryad.xd2547dxc)).
Dryad version 4 releases outcome arrays, but no bundle, rollout,
initial-condition, realized-order, reset, session, robot, retry, or immutable
policy-version identifier. Two published success rates also disagree with
their own arrays and counts. The public tables support marginal checks, not
reconstruction of the matched route edges.

Supplement S7 compares five additional public systems using the same evidence
layers.

# 6. What the missing records must answer

For a finite common-state policy comparison, the practical questions are
simple: were the declared states actually achieved comparably for every
policy, which attempts were retained or replaced, and could that choice depend
on policy or observed performance? An attempt record needs only enough fields
to join state, policy and realized order to reset status, execution status,
outcome, and any replacement. Video, operator identity, and fine-grained
telemetry are not required for this check.

For AnkIle, the decisive reanalysis is to compare the published retained panel
with the first valid attempt per policy-state cell and with all valid attempts,
averaged within each cell before restoring the original equal weighting of the
50 states. This prevents frequently retried cells from receiving extra weight.
If the winner is stable, the provenance strengthens the finite-panel claim. If
it changes, the size and direction of the retention effect should be reported.
For a disconnected route graph, the substantive repair remains a safe
common-context bridge; repeating an existing route cannot identify the missing
comparison.

# 7. Limitations

These counterexamples do not characterize every pair-first design or recommend
a policy lottery. Theorems 2--3 use a primitive-response box; the shared-success
sensitivity uses a narrower model. The real records are purposive. AnkIle
identifies only three exact released panels; its thin winner margins are
sensitive to one or two worst-case matched-round replacements, and the public
files do not show whether such replacements occurred. RoboArena supplies pair
support but not a common-context target, and TRI's public tables do not retain
its matched-bundle join.

The finite-sample program inherits the validity of supplied simultaneous edge
intervals. It does not provide a sampling unit, power, minimum detectable
effect, or stopping rule; each bridge study still needs those design choices.

The English-language review does not claim priority for the underlying
methods.

# Data and code availability

Data, code, and proofs are available in the package and supplement.
Project materials:
<https://github.com/trilamsr/research/tree/main/sim2real-correlation-audit>.

# Author and declarations

Tri Lam developed the analysis, conducted the public-record review, and wrote
the manuscript. No conflicts of interest are declared. The paper reports no
new human- or animal-subject experiment.

# References

- Aziz, H. et al. (2015). *Possible and Necessary Winners of Partial
  Tournaments*. JAIR 54. <https://doi.org/10.1613/jair.4856>
- Atreya, P. et al. (2025). *RoboArena: Distributed Real-World Evaluation of
  Generalist Robot Policies*. PMLR 305.
  <https://proceedings.mlr.press/v305/atreya25a.html>
- Anwar, A. et al. (2025). *Efficient Evaluation of Multi-Task Robot Policies
  With Active Experiment Selection*. <https://arxiv.org/abs/2502.09829>
- Balduzzi, D. et al. (2018). *Re-evaluating Evaluation*. NeurIPS 31.
  <https://arxiv.org/abs/1806.02643>
- Binette, O. and Reiter, J. P. (2024). *Improving the Validity and Practical
  Usefulness of AI/ML Evaluations Using an Estimands Framework*.
  <https://arxiv.org/abs/2406.10366>
- Bauer, S. et al. (2022). *A Robot Cluster for Running Reinforcement Learning
  Experiments on Real Robots*. CoRL. <https://proceedings.mlr.press/v176/bauer22a.html>
- Brandl, F., Brandt, F., and Seedig, H. G. (2016). *Consistent Probabilistic
  Social Choice*. *Econometrica* 84(5).
  <https://doi.org/10.3982/ECTA13337>
- Brill, M., Freeman, R., and Conitzer, V. (2016). *Computing Possible and
  Necessary Equilibrium Actions (and Bipartisan Set Winners)*. AAAI.
  <https://doi.org/10.1609/aaai.v30i1.10052>
- Dudík, M. et al. (2015). *Contextual Dueling Bandits*. PMLR 40.
  <https://proceedings.mlr.press/v40/dudik15.html>
- Hajek, B., Oh, S., and Xu, J. (2014). *Minimax-Optimal Inference from
  Partial Rankings*. NeurIPS 27. <https://arxiv.org/abs/1406.5638>
- Jiang, T. et al. (2026). *What Are We Actually Benchmarking in Robot
  Manipulation?* <https://arxiv.org/abs/2606.04233>
- Kress-Gazit, H. et al. (2024). *Robot Learning as an Empirical Science:
  Best Practices for Policy Evaluation*. <https://arxiv.org/abs/2409.09491>
- Kress-Gazit, H. et al. (2026). *A Careful Examination of Large Behavior
  Models for Multitask Dexterous Manipulation*.
  <https://arxiv.org/abs/2507.05331>
- Khalaf, H. et al. (2026). *Robust AI Evaluation through Maximal Lotteries*.
  <https://arxiv.org/abs/2602.21297>
- Lanctot, M. et al. (2025 version). *Evaluating Agents using Social Choice
  Theory*. <https://arxiv.org/abs/2312.03121>
- Lanctot, M. et al. (2026). *Active Evaluation of General Agents*.
  <https://arxiv.org/abs/2601.07651>
- Lu, T. and Boutilier, C. (2011). *Robust Approximation and Incremental
  Elicitation in Voting Protocols*. IJCAI.
  <https://www.cs.toronto.edu/~cebly/Papers/LuBoutilier_Elicitation_ijcai11.pdf>
- Montiel Olea, J. L., Qiu, C., and Stoye, J. (2025 version). *Decision Theory
  for Treatment Choice Problems with Partial Identification*.
  <https://arxiv.org/abs/2312.17623>
- Osting, B., Brune, C., and Osher, S. (2014). *Optimal Data Collection for
  Informative Rankings Expose Well-Connected Graphs*. JMLR 15(85).
  <https://www.jmlr.org/papers/v15/osting14a.html>
- Manski, C. F. (2009). *Diversified Treatment under Ambiguity*.
  <https://doi.org/10.1111/j.1468-2354.2009.00558.x>
- PhAIL (2026). *PhAIL v1.0*. arXiv:2605.29710v1.
  <https://arxiv.org/abs/2605.29710>
- RoboDojo (2026). *RoboDojo*. arXiv:2607.04434v3.
  <https://arxiv.org/abs/2607.04434>
- Saha, A., Koren, T., and Mansour, Y. (2021). *Adversarial Dueling Bandits*.
  PMLR 139. <https://proceedings.mlr.press/v139/saha21a.html>
- Selvaraj, P., Uttini, L., and Kuosmanen, V. (2026). *ArmnetBench v0.1:
  Parallel Real-World Evaluation of Manipulation Policies on a Low-Cost Arm
  Farm*. <https://arxiv.org/abs/2607.24481>
- Shah, N. and Wainwright, M. (2018). *Simple, Robust and Optimal Ranking from
  Pairwise Comparisons*. JMLR 18(199).
  <https://www.jmlr.org/papers/v18/16-206.html>
- Shah, N., Balakrishnan, S., Bradley, J., Parekh, A., Ramchandran, K., and
  Wainwright, M. (2016). *Estimation from Pairwise Comparisons: Sharp Minimax
  Bounds with Topology Dependence*. JMLR 17(58).
  <https://www.jmlr.org/papers/v17/15-189.html>
- Skalse, J. et al. (2023). *Invariance in Policy Optimisation and Partial
  Identifiability in Reward Learning*. PMLR 202.
  <https://proceedings.mlr.press/v202/skalse23a.html>
- Stoye, J. (2009). *Partial Identification and Robust Treatment Choice: An
  Application to Young Offenders*.
  <https://doi.org/10.1080/15598608.2009.10411923>
- Stoye, J. (2007). *Minimax Regret Treatment Choice with Incomplete Data and
  Many Treatments*. *Econometric Theory* 23(1).
  <https://doi.org/10.1017/S0266466607070089>
- Stoye, J. (2012). *Minimax Regret Treatment Choice with Covariates or with
  Limited Validity of Experiments*. *Journal of Econometrics* 166(1).
  <https://doi.org/10.1016/j.jeconom.2011.06.012>
- Suk, J. and Agarwal, A. (2024). *Non-Stationary Dueling Bandits Under a
  Weighted Borda Criterion*. <https://arxiv.org/abs/2403.12950>
- UMI-Bench (2026). *UMI-Bench 1.0*. arXiv:2606.10382v1.
  <https://arxiv.org/abs/2606.10382>
- Viappiani, P. (2020). *Robust Winner Determination in Positional Scoring
  Rules with Uncertain Weights*. *Theory and Decision* 88.
  <https://doi.org/10.1007/s11238-019-09734-3>
