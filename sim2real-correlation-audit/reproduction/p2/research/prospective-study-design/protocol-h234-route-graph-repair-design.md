# Protocol: H234 minimum route-graph repair for identification

## Status and outcome exposure

This protocol was fixed on 2026-07-28 after H233 established the
route-colored shared-success identification geometry and after its known-answer
route graphs and minimax result were known. H234 is therefore
outcome-exposed exploratory follow-up work. It is intended to turn H233's
diagnosis into a bounded design repair; it is not confirmatory evidence or a
novelty claim.

## Question

Under H233's shared binary-success model, what is the smallest set of new
context-specific pair types that guarantees identification of all
within-context policy differences, and therefore all common-target
differences, for a positive-target-weight context?

## Model and design objective

For one context \(c\), let the current route graph be
\(G_c=(V,E_c)\), with one policy per vertex. An added route observation for
pair \(\{i,j\}\) adds that edge to \(E_c\). The design objective is
**contextwise difference identification**: make \(G_c\) connected so that
the incidence equations identify every \(x_i^c-x_j^c\).

This is a prospective worst-case structural objective. It can be stronger
than the minimum needed to identify one winner for one boundary-constrained
observed law, or to identify a target aggregate through cross-context
cancellation. Those data-specific objectives remain separate linear-program
design problems.

## Fixed claims to test

1. If \(G_c\) has \(m_c\) connected components, at least \(m_c-1\) new
   cross-component pair types are necessary to make it connected.
2. If any cross-component policy pair can be scheduled, \(m_c-1\) pair types
   are sufficient: connect the component quotient graph with a spanning tree.
3. If only a subset of new policy pairs is allowable, repair is feasible if
   and only if the allowable quotient graph on current components is
   connected.
4. With nonnegative pair-specific costs, the least-cost contextwise repair is
   a minimum spanning tree of the allowable quotient graph, where the cost of
   a component-pair edge is the cheapest allowable policy pair joining those
   components.
5. Repeating an already observed within-component pair can improve precision
   under a stochastic model but cannot reduce the incidence nullity or repair
   structural identification.
6. Across positive-target-weight contexts, if each new execution contributes
   to only one context-specific route graph and the design requires every
   such graph to be connected, the minimum number of distinct new pair types
   is \(\sum_c(m_c-1)\), subject to allowable-edge feasibility in every
   context.
7. Known answers:
   - H233's A graph is already connected; its B graph has two components, so
     one added B-context pair, either 1--3 or 2--3, repairs contextwise
     identification.
   - H231's unobserved B graph has \(K\) singleton components and requires
     \(K-1\) distinct B-context pair types for the same objective.

## Computation and gates

- Exhaustively verify the unit-cost \(m-1\) result for every undirected graph
  on \(K=2,\ldots,5\), comparing the constructive repair with brute-force
  enumeration of missing-edge subsets; use a deterministic graph sample for
  \(K=6\).
- Exhaustively verify allowable-edge feasibility for every current/allowable
  edge partition on \(K=2,\ldots,5\).
- Compare the minimum-spanning-tree cost with brute-force least-cost repairs
  on deterministic cost panels through \(K=6\).
- Verify that duplicate existing edges leave graph rank unchanged.
- Add known-answer and mutation tests for the H233 and H231 route patterns.
- Use a separate dependency-light Node implementation for the two known
  answers, the component-count lower bound, and one constrained-cost case.

## Interpretation and stop conditions

Passing H234 supports a design prescription only within H233's
shared-success/incidence model and the stated contextwise-identification
objective. It does not establish that a named benchmark's context is measured
correctly, that one observation per new edge is statistically precise, that
physical reset/carryover is controlled, or that the repaired decision is
operationally acceptable. Connectivity is established prior art in
pairwise-comparison design; H234 is an application and executable repair
rule, not a general graph-theory contribution.
