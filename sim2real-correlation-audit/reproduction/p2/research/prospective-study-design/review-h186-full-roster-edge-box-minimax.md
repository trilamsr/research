# Independent challenge: H186 full-roster compatible-edge-box minimax

Date: 2026-07-27

Disposition: **pass after evidence-trace correction**

## Independence and method

The challenger did not edit producer or canonical files before reporting and
did not import the producer implementation. A standalone exact-arithmetic path
checked 23 full endpoint-enumeration cases for \(K=3,\ldots,6\), 89 direct
adverse endpoint witnesses through \(K=1009\), 1,918 rational-simplex
mixtures, and explicit endpoint and interior routed schedules through
\(K=257\). Every one of the \(\binom K2\) edges varies independently; there is
no three-policy core, dominated padding, or fixed noncore target edge.

## Reconstructed theorem

Use the normalized Borda target

\[
V_i=\{\tfrac12+\sum_{j\ne i}q_{ij}\}/K,\qquad
q_{ij}=\tfrac12+\delta_{ij},\quad \delta_{ij}\in[-1/4,1/4].
\]

For an ex-ante mixture \(p\) and candidate winner \(w\), let
\(c_i=\mathbf1\{i=w\}-p_i\). Independent edge extrema give

\[
\mathcal R(p)=\frac1{4K}\max_w\sum_{i<j}|c_i-c_j|.
\]

Every deterministic singleton has minimax regret \((K-1)/(2K)\). Uniform
randomization has worst-case expected regret \((K-1)/(4K)\). Averaging the
fixed-\(w\) objective over \(w\) yields

\[
K-1+\frac{K-2}{K}\sum_{i<j}|p_i-p_j|,
\]

so every nonuniform mixture is strictly worse and the uniform lottery is
unique.

## Compatibility correction

The first producer pass checked only scalar hidden-outcome bounds and asserted
the common observed law. In response, the producer now defines an explicit
alternating A/B route for every edge, constructs both context outcomes,
projects each full schedule independently to the observed and target laws,
retains structured endpoint and interior witnesses, and tests all-edge
projection for \(K\in\{3,4,7,16,32\}\).

The routed outcome remains \(1/2\), while the hidden outcome
\(2q_{ij}-1/2\) ranges over \([0,1]\). Thus every target edge in the declared
box is compatible with the same complete-support observed half-win law.

## Scope

The formulas use a self half-win and division by \(K\). Under opponent-only
division by \(K-1\), the corresponding deterministic and randomized values are
\(1/2\) and \(1/4\); uniqueness and the factor-of-two relation remain.

This is one constructed pair-first observed law and its full independent edge
box. It is not every observed distribution, empirical roster, protocol,
prevalence result, or realized-policy guarantee. The compatible world is fixed
independently of the ex-ante lottery and its realized draw.

