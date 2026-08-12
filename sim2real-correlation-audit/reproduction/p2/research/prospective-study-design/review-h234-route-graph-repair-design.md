# H234 minimum route-graph repair review and disposition

Date: 2026-07-28

Status: exact exploratory result and dependency-light reconstruction pass;
permitted as a constructive H233 corollary. Human methods and robotics review
remain open.

## Result

Under H233's shared binary-success incidence model, a context route graph
with \(m\) current components needs \(m-1\) new cross-component pair types to
identify every within-context policy difference when a repair is feasible.
If candidate pairs are restricted, feasibility is equivalent to connectivity
of the allowable quotient graph on the current components. With nonnegative
pair-specific costs, the least-cost repair is a minimum spanning tree on that
quotient graph, using the cheapest schedulable policy pair for each quotient
edge.

The count is for contextwise difference identification. It can be stronger
than the minimum needed to identify one boundary-specific winner or an
aggregate target with offset cancellation across contexts.

## Verification

- Every current graph on \(K=2,\ldots,5\) was enumerated: 1,098 graphs.
- A deterministic 503-graph sample was checked at \(K=6\).
- Every ternary current/allowable edge state through \(K=5\) was enumerated:
  59,808 states.
- Minimum-spanning-tree cost agreed with brute-force least-cost repair on 330
  deterministic cost panels through \(K=6\).
- Duplicate existing edges left component count unchanged.
- H233's A graph needs zero additions and its B graph needs one; H231's empty
  B graph needs \(K-1\) for \(K=3,\ldots,8\).
- A dependency-light Node implementation reconstructs both known answers, the
  empty-context sequence, duplicate-edge null, and a constrained cost case.

## Prior-art disposition

This is not a graph-theory novelty claim. Osting, Brune, and Osher formulate
pairwise-comparison data collection through graph informativeness and
algebraic connectivity, and Shah et al. derive topology-dependent estimation
bounds and design guidance. The component-count lower bound and
minimum-spanning-tree repair are elementary graph consequences. H234's value
is operational: it applies those established ideas to H233's
candidate-dependent context route graphs and cleanly separates structural
identification from repeated-edge precision.

Primary sources:

- Braxton Osting, Christoph Brune, and Stanley Osher, *Optimal Data
  Collection for Informative Rankings Expose Well-Connected Graphs*, JMLR
  15(85), 2014,
  <https://www.jmlr.org/papers/v15/osting14a.html>.
- Nihar Shah et al., *Estimation from Pairwise Comparisons: Sharp Minimax
  Bounds with Topology Dependence*, JMLR 17(58), 2016,
  <https://www.jmlr.org/papers/v17/15-189.html>.

## Permitted interpretation

P2 may say what to collect next: first bridge route components in each
positive-target-weight context; only then do additional repetitions address
precision rather than structural non-identification. If some pair types
cannot be scheduled, report whether the allowable quotient graph itself is
disconnected.

## Prohibited interpretation

Do not claim that one observation per added edge is sufficient for precise
estimation, that every context must be connected for every narrower
decision, that any named public benchmark exposes the route graph required to
run this repair, or that H234 is confirmatory or novel.
