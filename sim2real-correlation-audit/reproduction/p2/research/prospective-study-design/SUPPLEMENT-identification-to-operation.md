---
title: "Supplement to: When Candidate-Dependent Context Can Leave a Common-Context Robot-Policy Winner Unidentified"
author: "Tri Lam"
date: "2026-08-10"
---

# Status and notation

This supplement gives the derivations for the three construction-bounded
theorems, the route-graph uncertainty program, and the Bradley--Terry
connectivity corollary in the main paper.

There are \(K\geq3\) policies. For \(i<j\), \(q_{ij}\) is policy \(i\)'s
expected half-credit comparison score against \(j\) in the target context
population; \(q_{ji}=1-q_{ij}\) and
\(q_{ii}=1/2\). Under uniform opponent reference,

\[
V_i=\frac{\tfrac12+\sum_{j\ne i}q_{ij}}{K}.
\]

For the compatible class below,

\[
q_{ij}=\tfrac12+\delta_{ij},\qquad
\delta_{ij}\in[-1/4,1/4],\qquad
\delta_{ji}=-\delta_{ij}.
\]

# S1. Compatible worlds and Theorem 1

## S1.1 Explicit potential-outcome schedule

Let one shared context variable \(C\) take values A and B, and define the
common target population as their equal-weight mixture. For every unordered
pair \(e=\{i,j\}\), choose one value as its routed context \(R_e\). The route
may alternate across edges; only its being fixed independently of the
compatible target completion matters. Pair scores are primitive responses:
this construction imposes no shared scalar policy outcome or other cross-edge
coherence restriction.

For any desired target edge \(q_e\in[1/4,3/4]\), define the potential outcomes
for the orientation \(i<j\) by

\[
E[Z_e\mid R_e]=\tfrac12,\qquad
E[Z_e\mid \bar R_e]=2q_e-\tfrac12.
\]

The second outcome is valid because

\[
0\leq2q_e-\tfrac12\leq1.
\]

Fix the complete routed score law as a deterministic half tie, not merely an
equality of routed means. The observed routed edge is therefore \(1/2\), while
the equal-context target
projection is

\[
\frac12\left\{\tfrac12+
\left(2q_e-\tfrac12\right)\right\}=q_e.
\]

This construction is applied separately to every one of the
\(\binom K2\) edges. Consequently every vector
\((q_{ij}:i<j)\in[1/4,3/4]^{\binom K2}\) has a valid potential-outcome
schedule, and every such schedule projects to the same observed
complete-pair-support half-win law.

## S1.2 Opposite unique winners

Two endpoint completions are enough to show that the common-context winner is
not identified. If \(q_{ij}=3/4\) for every \(i<j\), policy \(1\) has strictly
the largest Borda value. If \(q_{ij}=1/4\) for every \(i<j\), policy \(K\)
has strictly the largest value. More explicitly, under the all-high
completion the unnormalized score of policy \(i\) is

\[
\tfrac12+\tfrac34(K-i)+\tfrac14(i-1),
\]

which strictly decreases with \(i\). Under the all-low completion the
coefficients \(1/4\) and \(3/4\) exchange, so the score strictly increases
with \(i\). The two worlds agree on every observed pair, routed context, and
routed outcome.

Thus, for every \(K\geq3\), this particular complete-support observed law is
compatible with opposite unique common-context winners. Repeating routed
comparisons estimates the routed half-win law more precisely but supplies no
information about the unobserved context-specific potential outcomes.

# S2. Uniform-reference edge-coupled minimax

Let \(p\) be an ex-ante policy lottery, and for a candidate oracle winner \(w\)
put

\[
c_i=\mathbf1\{i=w\}-p_i.
\]

Because \(\sum_i c_i=0\), the midpoint terms cancel. The regret against
candidate \(w\) is

\[
V_w-\sum_i p_iV_i
=\frac1K\sum_{i<j}(c_i-c_j)\delta_{ij}.
\]

The edges vary independently over \([-1/4,1/4]\), so maximizing each term at
its sign-compatible endpoint gives

\[
\mathcal R(p)
=\frac1{4K}\max_w\sum_{i<j}|c_i-c_j|.
\tag{S2.1}
\]

## S2.1 Deterministic and uniform values

For a deterministic choice \(p=e_s\), choosing \(w\ne s\) in (S2.1) gives
one difference of magnitude two, \(2(K-2)\) differences of magnitude one,
and all other differences zero. Hence

\[
\mathcal R(e_s)=\frac{2+2(K-2)}{4K}
=\frac{K-1}{2K}.
\]

For the uniform lottery, \(p_i=1/K\). For any \(w\), only the \(K-1\) edges
incident to \(w\) have nonzero differences, all of magnitude one. Therefore

\[
\mathcal R(p_{\mathrm{unif}})=\frac{K-1}{4K}.
\]

These are ex-ante expected-regret values. The second expression does not bound
the worst regret of the policy realized from the lottery.

## S2.2 Uniqueness

For a general \(p\), averaging the unscaled objective in (S2.1) over all
candidate winners gives

\[
\frac1K\sum_w\sum_{i<j}|c_i-c_j|
=K-1+\frac{K-2}{K}\sum_{i<j}|p_i-p_j|.
\tag{S2.2}
\]

The maximum over \(w\) is at least this average. Equation (S2.2) equals
\(K-1\) only when every \(p_i\) is equal, and is strictly larger otherwise.
The uniform lottery attains \(K-1\) for every \(w\), so it is the unique
minimizer.

# S3. Weighted-reference minimax

Now let \(r_i\geq0\), \(\sum_i r_i=1\), and define

\[
V_i=\sum_j r_jq_{ij}.
\]

For candidate winner \(w\), use the same
\(c_i=\mathbf1\{i=w\}-p_i\). Maximizing each edge over the compatible interval
gives

\[
\mathcal R(p)=\frac14\max_w F_w,
\]

where the incident-edge terms sum to \(1-p_w\), leaving

\[
F_w=1-p_w+
\sum_{\substack{i<j\\i,j\ne w}}|r_jp_i-r_ip_j|.
\tag{S3.1}
\]

Order the weights and relabel so that

\[
a=r_1\leq b=r_2\leq g=r_3\leq\cdots.
\]

Tie permutations do not change the resulting optimizer set.

## S3.1 Lower bound

The first two candidate-winner objectives obey

\[
F_1+F_2
\geq2-p_1-p_2+|p_1+p_2-a-b|
\geq2-a-b.
\tag{S3.2}
\]

At least one of \(F_1,F_2\) is therefore at least
\((2-a-b)/2\), which yields

\[
\mathcal R^\star\geq\frac{2-a-b}{8}.
\tag{S3.3}
\]

## S3.2 Equality conditions and complete optimizer face

To expose the equality cases, write \(C=1-a-b\) and
\(s=p_1+p_2\). Before the final inequality in (S3.2), the complete lower-bound
chain is

\[
\begin{aligned}
F_1+F_2
&\geq 2-s+
\sum_{k\geq3}
\left\{
|r_kp_2-bp_k|+|r_kp_1-ap_k|
\right\}\\
&\geq 2-s+
\sum_{k\geq3}|r_ks-(a+b)p_k|\\
&\geq2-s+|Cs-(a+b)(1-s)|\\
&=2-s+|s-a-b|\\
&\geq2-a-b.
\end{aligned}
\tag{S3.2a}
\]

The first line drops twice the nonnegative terms
\(|r_jp_i-r_ip_j|\) for \(3\leq i<j\). If \(p\) is optimal, both
\(F_1\) and \(F_2\) are at most \((2-a-b)/2\), so equality must hold
throughout (S3.2a). The dropped terms must therefore vanish. Because the tail
has positive total reference weight, this implies, for one common
\(\lambda\),

\[
p_i=\lambda r_i
\quad\text{for every }i\geq3.
\tag{S3.2b}
\]

In particular, any zero-weight tail index has \(p_i=0\); the argument never
divides by a zero reference weight.

Equality in the last line requires \(s\geq a+b\). Since
\(\lambda=(1-s)/C\), equality in the two triangle inequalities further
requires

\[
p_1-a\lambda\geq0,\qquad p_2-b\lambda\geq0.
\tag{S3.2c}
\]

The two candidate-winner objectives must also be equal:

\[
F_1=F_2=\frac{2-a-b}{2}.
\]

Put

\[
h=p_1-\frac{a+b}{2}.
\]

Solving \(F_1=(2-a-b)/2\), (S3.2b), and the simplex constraint gives

\[
p_1=\frac{a+b}{2}+h,
\]

\[
p_2=\frac{b(2-a-b)}{2(1-a)}
    +\frac{1-b}{1-a}h,
\]

and, for \(i\notin\{1,2\}\),

\[
p_i=r_i\frac{2-a-b}{1-a}
\left(\frac12-\frac{h}{1-a-b}\right).
\tag{S3.4}
\]

In this parametrization,

\[
p_2-b\lambda=\frac{h}{C},
\]

so (S3.2c) forces \(h\geq0\); the other sign condition is then satisfied
because \(b\geq a\). Only on this equality-case domain, substitution in
(S3.1) gives, for every \(j\geq3\),

\[
F_j-\frac{2-a-b}{2}=2h-(r_j-b).
\tag{S3.5}
\]

Thus all remaining candidate-winner inequalities are satisfied exactly when

\[
0\leq h\leq\frac{g-b}{2}.
\]

Every point in this segment attains the lower bound (S3.3), so

\[
\mathcal R^\star=\frac{2-a-b}{8}.
\]

The segment collapses to a single point exactly when \(b=g\). The
proportional water-filling solution is the \(h=0\) endpoint and has no general
priority over the rest of the segment.

When exactly two weights are zero, they are indices 1 and 2 and receive equal
mass \(h\), up to half the smallest positive reference weight. When at least
three weights are zero, \(b=g=0\); the segment collapses to \(h=0\), and
\(p=r\) is unique.

## S3.3 Hard support exclusion

Theorem 3 allows \(p_i>0\) when \(r_i=0\). Now restrict the action lottery by
\(r_i=0\Rightarrow p_i=0\), while retaining zero-reference policies as possible
oracle comparators. For any zero-reference candidate winner \(z\),
(S3.1) gives

\[
F_z=1+
\sum_{\substack{i<j\\r_i>0,\ r_j>0}}
|r_jp_i-r_ip_j|
\geq1.
\tag{S3.6}
\]

The feasible lottery \(p=r\) makes the sum zero and every other \(F_w\leq1\).
Equality forces \(p_i=\lambda r_i\) on positive support, and normalization
gives \(\lambda=1\) (support size one is immediate). Hence the exact value is
\(1/4\), uniquely at \(p=r\). Relative to Theorem 3, exactly one zero raises
the value by \(r_{(2)}/8\); exactly two retain only \(h=0\); at least three
change nothing.

# S4. Shared-success sensitivity and route-graph repair

Let \(Y_i(C)\in\{0,1\}\) be policy \(i\)'s success outcome in shared context
\(C\). Give policy \(i\) one point for a strict success win over policy \(j\),
zero for a strict loss, and one half for a tie:

\[
Z_{ij}(C)=
\mathbf1\{Y_i(C)>Y_j(C)\}
+\tfrac12\mathbf1\{Y_i(C)=Y_j(C)\}.
\]

For any joint binary law,

\[
\begin{aligned}
E[Z_{ij}(C)]
&=P(Y_i=1,Y_j=0)
 +\tfrac12P(Y_i=Y_j)\\
&=\tfrac12+\tfrac12\{E[Y_i(C)]-E[Y_j(C)]\}.
\end{aligned}
\tag{S4.1}
\]

No independence between \(Y_i\) and \(Y_j\) is required for (S4.1).
Route every observed pair through shared context A and fix identical policy
outcomes there, so the complete observed score law is a deterministic half
tie. Because every pair uses the same route, this section isolates absence of
support for target context B; it does not test candidate-dependent routing.
Put \(x_i=E[Y_i(B)]\in[0,1]\). Under the equal-context target,

\[
q_{ij}
=\tfrac12+\tfrac14(x_i-x_j).
\tag{S4.2}
\]

Thus \(\delta_{ij}=(x_i-x_j)/4\), and every triple satisfies

\[
\delta_{ik}=\delta_{ij}+\delta_{jk}.
\tag{S4.3}
\]

The compatible region is a gradient image of \([0,1]^K\), not the full
\(\binom K2\)-dimensional edge box. Yet \(x=e_1\) and \(x=e_K\) preserve the
observed law and make policies 1 and \(K\), respectively, unique target Borda
winners for every \(K\geq3\).

For arbitrary nonnegative opponent-reference weights \(r\) summing to one,

\[
\begin{aligned}
V_i
&=\sum_jr_j\left\{\tfrac12+\tfrac14(x_i-x_j)\right\}\\
&=\tfrac12+\tfrac14(x_i-r^\top x).
\end{aligned}
\tag{S4.4}
\]

The reference term is common to all actions and cancels from regret:

\[
\begin{aligned}
\mathcal R(p)
&=\frac14\sup_{x\in[0,1]^K}
\{\max_i x_i-p^\top x\}\\
&=\frac14\max_w(1-p_w)
=\frac14(1-\min_i p_i).
\end{aligned}
\tag{S4.5}
\]

The last equality is sharp at a cube vertex with \(x_w=1\) and every other
coordinate zero. Maximizing the smallest lottery mass uniquely gives
\(p_i=1/K\), hence

\[
\mathcal R^\star=\frac{K-1}{4K}.
\tag{S4.6}
\]

Every deterministic lottery has a zero-mass alternative and regret \(1/4\).
The structured and primitive models therefore share the unique uniform
lottery and its value, but not deterministic regret, weighted optimizer
geometry, or the hard-support uniqueness statement.

The half-tie profile is one point in a larger exact class. Let
\(a_i=E[Y_i(A)]\) be an arbitrary compatible observed-context profile, defined
up to a common offset by the routed pair scores, and retain
\(x_i=E[Y_i(B)]\). Then

\[
o_{ij}=\tfrac12+\tfrac12(a_i-a_j),\qquad
q_{ij}=\tfrac12+\tfrac14\{(a_i+x_i)-(a_j+x_j)\}.
\tag{S4.7}
\]

For one pair, the missing-context score ranges over \([0,1]\), so

\[
q_{ij}\in[o_{ij}/2,(o_{ij}+1)/2].
\tag{S4.8}
\]

The interval always has width \(1/2\) and strictly straddles one half exactly
when \(o_{ij}\in(0,1)\). Globally, put
\(D=\max_i a_i-\min_i a_i\). If \(D<1\), the completion \(x=e_w\) makes
policy \(w\) uniquely best for every \(w\), since
\(a_w+1>a_j\) for all \(j\ne w\). If \(D=1\), any policy attaining
\(\min a\) can at best tie a maximum-\(a\) policy and cannot be a unique
winner. Thus strict interiority is an exact boundary.

For heterogeneous \(a\), fixed-winner maximization over the missing-context
cube gives

\[
\begin{aligned}
\mathcal R(p;a)
&=\frac14\max_w\sup_{x\in[0,1]^K}
\{a_w+x_w-p^\top(a+x)\}\\
&=\frac14\{1-p^\top a+\max_w(a_w-p_w)\}.
\end{aligned}
\tag{S4.9}
\]

A common offset in \(a\) cancels. Constant \(a\) reduces (S4.9) to (S4.5).
The result is relative-open only within the additive shared-success law with
equal target-context weights; it is neither ambient-open in unrestricted
pair-score space nor a finite-sample confidence statement.

## S4.1 Route-colored graph extension

For context \(c\), orient the observed route edges and let \(E_c\) be the
incidence matrix. The routed half-credit scores identify
\(E_cx^c=d_c\), \(0\leq x^c\leq1\). The null space has one constant-offset
degree of freedom per connected component. Consequently, if every
positive-target-weight route graph is connected, every within-context policy
difference and hence every common-target difference is identified.
Disconnection can retain component offsets when the box constraints leave
slack; the exact criterion is zero compatible width for every target
difference \(\mu_i-\mu_j\), where
\(\mu=\sum_c\alpha_cx^c\).

For a lottery \(p\), fixed opponent-reference terms cancel and

\[
\mathcal R(p)=\tfrac12\max_w\sup_{\{x^c\}}
(e_w-p)^\top\sum_c\alpha_cx^c.
\tag{S4.10}
\]

Each inner support function is linear. Introducing free
\(\lambda_{wc}\) and \(u_{wc}\geq0\) gives the joint LP

\[
\begin{aligned}
\min\quad &t\\
\text{s.t.}\quad&
t\geq\tfrac12\sum_c(d_c^\top\lambda_{wc}+\mathbf1^\top u_{wc})
&&\forall w,\\
&E_c^\top\lambda_{wc}+u_{wc}\geq\alpha_c(e_w-p)
&&\forall w,c,\\
&p\geq0,\quad\mathbf1^\top p=1,\quad u_{wc}\geq0.
\end{aligned}
\tag{S4.11}
\]

For the three-policy known answer, A contains edges 1--3 and 2--3 with
zero differences, while B contains edge 1--2 with
\(x_1^B-x_2^B=1/2\). The compatible B vertices are
\[
(1/2,0,0),\ (1/2,0,1),\ (1,1/2,0),\ (1,1/2,1).
\]
The first two already give opposite unique target winners 1 and 3. Writing
\(p=(p_1,p_2,p_3)\), exact vertex evaluation yields
\[
\mathcal R(p)=
\frac18\max\{1-p_1,\ p_1+2p_2,\ 2-2p_1-p_2,\ p_2\}.
\tag{S4.12}
\]
The maximum of the middle two terms is at least \(2/3+p_2\), with equality
only when \(p_1+p_2=2/3\). This bound is uniquely minimized at
\(p_2=0,p_1=2/3\), giving \(p=(2/3,0,1/3)\) and regret \(1/12\).

### S4.2 Minimum contextwise repair

Let the current route graph in context \(c\) have \(m_c\) connected
components. One new pair type can merge at most two components, so at least
\(m_c-1\) additions are necessary for contextwise difference identification.
If every cross-component policy pair is schedulable, any spanning tree on the
component quotient graph supplies \(m_c-1\) edges and is sufficient.

If only some pairs are allowable, form a quotient graph whose vertices are
the current components and whose edges are allowable cross-component pairs.
Repair is feasible exactly when this quotient is connected. With nonnegative
pair costs, retain the cheapest policy pair for each quotient edge and choose
a minimum spanning tree. Consequently, when each new pair type belongs to
only one context and every positive-target-weight context must be connected,
the total minimum is
\[
\sum_{c:\alpha_c>0}(m_c-1),
\tag{S4.13}
\]
provided every allowable quotient graph is connected.

In the three-policy example, context A is already connected and context B has components
\(\{1,2\}\) and \(\{3\}\), so either B-context pair 1--3 or 2--3 closes the
contextwise gap. A wholly unobserved B context has \(K\) singleton components
and needs \(K-1\) distinct B-context pair types for the same objective.
Repeating an existing within-component pair does not change incidence rank.
It may improve precision under a sampling model, but it cannot repair
structural identification. Sufficiency also requires a named along-path
stationarity/comparability condition: every edge in an identifying path must
refer to the same stable context meaning. Connectivity alone does not supply
that empirical bridge.

This count need not be minimal for identifying one winner at one
boundary-constrained law, or when cross-context component offsets cancel.
Connectivity and well-connected comparison design are prior art.

## S4.3 Simultaneous edge intervals

Finite samples replace the exact incidence equation by

\[
\ell_c\leq E_cx^c\leq u_c,\qquad 0\leq x^c\leq1.
\tag{S4.14}
\]

Let \(\mathcal X(\ell,u)\) be the product of these contextwise feasible sets
and let

\[
\mathcal M(\ell,u)=
\left\{\sum_c\alpha_cx^c:(x^c)_c\in\mathcal X(\ell,u)\right\}.
\tag{S4.15}
\]

The sharp bounds on target difference \(\mu_i-\mu_j\) are the minimum and
maximum of that linear contrast over \(\mathcal X\). Policy \(i\) is a possible
winner if the same feasible system admits
\(\mu_i\geq\mu_j\) for every \(j\). It is certified as the unique winner only
when the lower bound on \(\mu_i-\mu_j\) is strictly positive for every
\(j\ne i\).

If the intervals in (S4.14) jointly contain the population edge differences
with probability at least \(1-\alpha\), then the population target belongs to
\(\mathcal M(\ell,u)\) with at least the same probability. The projected
difference bounds and any certified winner therefore inherit that coverage.
This is a deterministic confidence-set projection: it adds no assumption and
cannot repair invalid edge intervals.

The minimax action is also an LP. Define

\[
A_c=\begin{bmatrix}E_c\\-E_c\\I\\-I\end{bmatrix},\qquad
b_c=\begin{bmatrix}u_c\\-\ell_c\\\mathbf1\\\mathbf0\end{bmatrix}.
\]

Dualizing the contextwise support functions gives

\[
\begin{aligned}
\min\quad &t\\
\text{s.t.}\quad&
t\geq\tfrac12\sum_c b_c^\top y_{wc} &&\forall w,\\
&A_c^\top y_{wc}=\alpha_c(e_w-p) &&\forall w,c,\\
&p\geq0,\quad\mathbf1^\top p=1,\quad y_{wc}\geq0.
\end{aligned}
\tag{S4.16}
\]

Point intervals recover (S4.11). For the three-policy known answer, the program
again returns \(p=(2/3,0,1/3)\) and regret \(1/12\). A separate
vertex-enumeration implementation agrees on that case and on connected,
disconnected, and widened-interval controls.

One distribution-free input construction is available when each observed edge
has \(n_e\) independent bounded half-credit outcomes \(Z\in[0,1]\). For \(M\)
edges, Bonferroni--Hoeffding intervals use

\[
\epsilon_e=\sqrt{\frac{\log(2M/\alpha)}{2n_e}},\qquad
q_e\in[\hat q_e-\epsilon_e,\hat q_e+\epsilon_e]\cap[0,1],
\tag{S4.17}
\]

then map to \(d_e=2q_e-1\). Across-edge independence is unnecessary for the
Bonferroni step, but every edge interval must be valid for its own sampling
unit. Clustered, sequential, or adaptively collected trials need a procedure
valid for that design.

## S4.4 Bradley--Terry connectivity corollary

Suppose exact target-context comparisons follow the Bradley--Terry law

\[
q_{ij}=\sigma(s_i-s_j),\qquad
\sigma(z)=\frac{1}{1+e^{-z}}.
\tag{S4.18}
\]

For each observed common-context edge, the inverse link identifies
\(s_i-s_j=\operatorname{logit}(q_{ij})\). If the comparison graph is connected,
these differences identify all scores up to one common offset. The Borda
ordering equals the score ordering: if \(s_i>s_j\), then policy \(i\)'s
comparison probability exceeds policy \(j\)'s against every third policy and
also in their direct comparison. Equal scores give equal Borda values.
Consequently the Borda-winner set is identified, and it is a singleton exactly
when the identified largest score is unique.

If the graph has two or more components, each component retains its own
additive offset. Shifting one component above another changes the global
winner set without changing an observed edge. Thus, with unrestricted finite
scores, the winner set is identified if and only if the graph is connected.
A graph with \(m\) current components needs \(m-1\) cross-component edges when
such a repair is feasible; \(K-1\) is the empty-graph case.

This is the standard connected-comparison-graph identifiability consequence
for a latent difference model, not a new Bradley--Terry theorem. It also does
not extend to strong stochastic transitivity alone, which is a broader model
and does not make connected edge probabilities determine every score
difference.

# S5. Same-box comparison with pairwise-lottery antecedents

Write the target margin matrix as \(M_{ij}=2q_{ij}-1\), so every primitive
edge lies independently in \([-1/2,1/2]\). The four neighboring questions are
not interchangeable.

\begin{longtable}{@{}>{\raggedright\arraybackslash}p{0.22\linewidth}
>{\raggedright\arraybackslash}p{0.35\linewidth}
>{\raggedright\arraybackslash}p{0.35\linewidth}@{}}
\hline
\textbf{framework} & \textbf{uncertainty and comparator} &
\textbf{action/output on this example} \\
\hline
Observed maximal lottery & Known routed matrix \(M^0=0\); worst opposing
lottery & Every policy lottery is maximal \\
Incomplete equilibrium action & Equilibrium support in some or every
completion & Every action is possible; none is necessary \\
Robust maximal lottery & \(\max_p\min_M\min_q p^\top Mq\) & Unique uniform
\(p\); worst margin \(-(K-1)/(2K)\) \\
P2 Borda regret & Regret to the Borda-best policy in the same compatible world
& Unique uniform \(p\); regret \((K-1)/(4K)\) \\
\hline
\end{longtable}

For fixed \(p\), a pure opponent \(j\) and the completion
\(M_{ij}=-1/2\) for every \(i\ne j\) give

\[
\min_M\min_qp^\top Mq
=-\tfrac12\max_j(1-p_j)
=-\tfrac12(1-\min_jp_j).
\tag{S5.1}
\]

The robust maximal-lottery value is therefore maximized uniquely by the
uniform lottery. Its margin value is \(-(K-1)/(2K)\), equivalently worst win
probability \((K+1)/(4K)\). The selected lottery happens to agree with P2 on
this symmetric box, but the loss, comparator, value, and interpretation differ.

The zero matrix is one completion, so every action is possible in an
equilibrium support. For any queried action, another completion can make a
different action the unique Condorcet winner and unique maximin action; no
action is necessary. This comparison follows Brandl, Brandt, and Seedig; Brill,
Freeman, and Conitzer; and Khalaf et al. It is not a reproduction of those
papers or evidence of novelty.

# S6. Prior-art boundary

The deterministic value in S2 is the marginal interval width

\[
U-L=\frac{K-1}{2K},\qquad
L=\frac{K+1}{4K},\quad U=\frac{3K-1}{4K},
\]

and is already recovered by Stoye's arbitrary-finite-treatment interval
model. General robust randomization, zero-sum reduction, optimizer-set
analysis, and nonunique minimax decisions are also established work. The
bounded surviving objects are the edge-coupled randomized value and uniqueness
in S2 and the weighted exact face in S3, each for this constructed compatible
class. Absence of a formula from the bounded search is not evidence of novelty.

# S7. Public-evidence and diagnostic-reference details

## S7.1 Evidence layers

The evidence labels are cumulative only within a specified unit:
*source-described* means a fixed primary source states the feature;
*artifact-reconstructable* means pinned code or data support it;
*artifact-partial* means only a stated subset is reconstructable; and
*realized-law verified* requires version-bound assignment and lifecycle
records. “Absent” always means absent from the fixed public sources, not
privately absent.

H251 fixes the three AnkIle R5 repositories at revisions `15d4190...`,
`cd5d0d...`, and `d2d109...`; RoboArena `DataDump_07-17-2026` at
`7931db8...`; and TRI Dryad version 4. The AnkIle rectangles contain all 450
declared policy-state cells. RoboArena contains 104 of 210 possible label
pairs: the 20 pair-eligible labels are connected, while one unpaired label is
isolated. TRI's 20 CSVs omit the published test-bundle join; three cells need a
narrow trailing-apostrophe parse repair, and two released rates disagree with
their arrays and counts. Separate Python and Ruby implementations reproduce
these facts.

The AnkIle released-panel margins are three, one, and three successes. In a
worst-case retained-round sensitivity, replacing a matched round by an
arbitrary three-policy binary outcome vector can reverse the routing, marker,
and square winners in two, one, and two rounds, respectively. Exact subset
enumeration verifies those minima. This bounds fragility; it does not show
that any round was replaced. The released configuration permits
incomplete-round reruns for routing and marker and disables them for square.

\small
\begin{tabular}{@{}>{\raggedright\arraybackslash}p{0.13\linewidth}
>{\raggedright\arraybackslash}p{0.25\linewidth}
>{\raggedright\arraybackslash}p{0.25\linewidth}
>{\raggedright\arraybackslash}p{0.29\linewidth}@{}}
\hline
\textbf{system} & \textbf{favorable source evidence} &
\textbf{reconstructed public layer} & \textbf{unresolved layer} \\
\hline
AnkIle R5 & Three policies on the same 50 declared states per task; randomized
within-round order & Complete rectangles, exact outcomes, fixed artifacts,
state manifests, submitted-round lists, and one/two-round replacement
sensitivity & Whether any retained round replaced an earlier attempt and why;
population sampling law \\
RoboArena & Random pair sampling; policy-identity blinding & Pinned 3,883
sessions; 21 labels; 104 pair edges; complete public schema & Deployed weights,
pool epochs, context bridge, exact resets, robot and attempt lineage \\
TRI LBM & Blind randomized matched test bundles in the paper & Version-4
outcome arrays and margins; two rate inconsistencies & Bundle/trial/order/reset,
session/robot, retry, and immutable policy-version join \\
\hline
\end{tabular}
\normalsize

Five earlier systems supply useful design or metadata evidence but do not add
an artifact-reconstructable common-context comparison.

\small
\begin{tabular}{@{}>{\raggedright\arraybackslash}p{0.13\linewidth}
>{\raggedright\arraybackslash}p{0.25\linewidth}
>{\raggedright\arraybackslash}p{0.25\linewidth}
>{\raggedright\arraybackslash}p{0.29\linewidth}@{}}
\hline
\textbf{system} & \textbf{favorable source evidence} &
\textbf{reconstructed public layer} & \textbf{unresolved layer} \\
\hline
UMI-Bench & Common finite frame; reset and trial records described &
Demonstration corpus is not the evaluation runner or trial ledger & Execution
ledger and realized law \\
RoboDojo & Common layouts and roster; blinded scoring & Frame, roster,
execution path, trial identity; reset partial & Historical realization and
accepted-state evidence \\
ArmnetBench & All policies per cell; independent placement; checkpoint release
claimed & Public trials and 84 resolving repositories & Exact revisions,
execution order, reset law, realized state, physical block \\
PhAIL & Context first; \texttt{BalancedSampler}; operator blinding & Sampler
code, context fields, labels, 594 episode identities & Realized draws,
historical revision, reset lineage, operator/physical block \\
RRC 2020 & Complete retained runs; run type owner-confirmed from ID format &
Job/start/robot index and structural audit & Excluded attempts, policy/team
join, retry parent, attempt-level selection \\
\hline
\end{tabular}
\normalsize

## S7.2 Diagnostic metadata sensitivities

The values below are Monte Carlo reference-tail fractions under explicitly
chosen diagnostic laws. They are not p-values calibrated by an identified
physical assignment, sampling, session, or dependence law.

\small
\begin{longtable}{@{}>{\raggedright\arraybackslash}p{0.19\linewidth}
>{\raggedright\arraybackslash}p{0.23\linewidth}
>{\raggedleft\arraybackslash}p{0.08\linewidth}
>{\raggedright\arraybackslash}p{0.21\linewidth}
>{\raggedright\arraybackslash}p{0.17\linewidth}@{}}
\hline
\textbf{analysis} & \textbf{diagnostic reference} & \textbf{draws} &
\textbf{decision boundary} & \textbf{exposure} \\
\hline
State simulation & Independent-uniform state simulation; fixed statistics & 49,999 &
Joint tail/effect gates & Fixed before result \\
Clock-regime state permutation & State permutation within clock regime & 49,999 & Pooled 0.01/10\%
gate; two 0.005 secondary gates & Result-exposed \\
Clock-regime label permutation & Label permutation within clock regime & 49,999 & Pooled 0.01/0.10
gate; two Bonferroni tests & Result-exposed \\
UTC-date label permutation & Label permutation within UTC date & 49,999 & Same pooled/secondary
gates & Result-exposed \\
\hline
\end{longtable}
\normalsize

The state simulation and clock-regime state permutation miss their fixed
material gates. The clock-regime label permutation crosses one secondary gate
but misses the pooled effect gate. Under the UTC-date reference, the
pooled and regime-1 excesses contract to 0.01205 and 0.03704, with tail
fractions 0.52872 and 0.23688. These diagnostics motivate a metadata request;
they do not establish independence, assignment, session, carryover, outcome
uncertainty, or performance.
