# H250 finite-sample route-graph review

Date: 2026-08-10

Status: exploratory synthetic method supported by producer tests and a
method-distinct vertex-enumeration challenge. Human statistical and robotics
review remain open.

## Result

Simultaneous intervals on context-specific shared-success edge differences can
be propagated by linear programming to sharp target-difference bounds,
possible winners, certified unique winners, and an ex-ante minimax-regret
lottery. If the edge intervals jointly cover the population differences with
probability at least \(1-\alpha\), the projected target set and every valid
certificate inherit that coverage.

The implementation supplies an optional Bonferroni--Hoeffding construction for
independent bounded observations within each edge. That construction is not
validity evidence for clustered, adaptive, or otherwise dependent trials.

## Verification

- Nine producer tests pass, including infeasible-system refusal and interval
  monotonicity.
- H233's point case reproduces lottery \((2/3,0,1/3)\) and half-credit regret
  \(1/12\).
- A connected exact three-policy path certifies the intended winner and
  returns zero regret for selecting it.
- A disconnected exact graph retains policies 1 and 3 as possible winners and
  certifies none.
- A separate implementation enumerates every feasible polytope vertex and
  solves the resulting finite-world primal minimax problem. It agrees with the
  producer's dual LP on all target bounds, winner sets, lotteries, and regret
  values for four fixed cases.
- Two challenge tests pass, including rejection of a mutated H233 lottery.

Canonical outputs:

- `finite_sample_route_graph.py`;
- `result-h250-finite-sample-route-graph.json`;
- `challenge_h250_finite_sample_route_graph.py`; and
- `result-h250-finite-sample-route-graph-vertex-challenge.json`.

## Interpretation

H250 closes P2's narrow executable gap between structural identification and
finite-sample edge uncertainty. It does not close the empirical gap: the
reviewed public records still lack the target-valid assignment, context,
reset, revision, and dependence join required to supply defensible intervals
to this program.

The confidence-set projection, Hoeffding input, LP duality, and graph
identifiability ingredients are established methods. The contribution is the
auditable interface to P2's route-colored target, not a new general inference
theory.

## Boundaries

- No PhAIL or other public-system performance value was opened.
- The program does not define the estimand, target weights, sampling unit,
  missingness rule, cluster adjustment, power, or stopping rule.
- A certified winner is valid only relative to the declared model and the
  supplied intervals.
- Numerical agreement on the fixed synthetic cases is not human review or a
  proof of empirical applicability.

## Reproduction

```text
.venv/bin/python -m pytest -q \
  research/prospective-study-design/test_finite_sample_route_graph.py \
  research/prospective-study-design/test_challenge_h250_finite_sample_route_graph.py
.venv/bin/python research/prospective-study-design/finite_sample_route_graph.py --check
.venv/bin/python research/prospective-study-design/challenge_h250_finite_sample_route_graph.py --check
```
