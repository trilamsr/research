# H233 route-colored shared-success review and disposition

Date: 2026-07-28

Status: exact result and distinct-implementation challenge pass; exploratory
reliance permitted within the declared construction. Human literature and
methods review remain open.

## What was tested

External review showed that H231's all-A route is a missing-target-context
support example rather than candidate-dependent routing. H233 therefore
formalizes context-specific route graphs for shared binary policy outcomes,
derives the compatible common-target polytope and minimax LP, and instantiates
the reviewer's genuine-routing three-policy case.

## Verification

- The Python producer verifies the incidence-rank identity for every graph on
  \(K=3,\ldots,6\) and deterministic samples for \(K=7,8\).
- Exact rational enumeration gives the four compatible B-context vertices.
- Direct robust-vertex and dual-LP formulations agree numerically at
  \(p=(2/3,0,1/3)\), regret \(1/12\).
- The closed-form objective
  \[
  \max\{1-p_1,p_1+2p_2,2-2p_1-p_2,p_2\}/8
  \]
  proves continuous-simplex uniqueness, rather than relying on a grid alone.
- A separate Node/Rational implementation imports no producer code and checks
  the binary half-tie identity, routed observational equivalence, opposite
  endpoint winners, and the unique optimizer on a denominator-12 grid.
- Mutation tests reject the uniform optimizer and would detect changes to the
  known-answer route geometry or value.

## Literature disposition

A post-H192 primary-source update confirms that comparison-graph
connectivity, invariance-based partial identifiability, contextual pairwise
policy decisions, and randomized minimax regret are established ideas. No
exact collision was found for H233's route-colored bounded shared-success
polytope or its three-policy optimizer/value. Absence from a bounded search is
not proof of novelty.

## Permitted claim

Within the declared shared-binary-success model, each context's route-graph
components give its additive identification freedoms. Connected
positive-target-weight graphs identify all target differences; disconnected
graphs can retain target-relevant offsets when bounds leave slack. A genuine
candidate-dependent three-policy route pattern is compatible with opposite
common-target winners and has unique ex-ante minimax lottery
\((2/3,0,1/3)\), regret \(1/12\).

## Prohibited claim

Do not claim that connectivity is a new principle, that disconnection alone
always implies non-identification, that every robot response is shared binary
success, that any named benchmark has the H233 route law, that the lottery is
operationally acceptable, or that H233 is confirmatory or novel.

## Release consequence

H233 repairs the specific structured-routing gap identified by P2A and shows
that H231's uniform action does not generalize to genuine route coloring.
P2's formal structured branch can advance to external methods review, but
expert human literature/statistical review and the separate editorial
decision about the multi-system audit remain release gates.
