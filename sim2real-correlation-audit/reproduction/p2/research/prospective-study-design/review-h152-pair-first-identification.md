# H152 independent challenge of pair-first common-context identification

Date: 2026-07-27

Status: pass with scope

## Challenged claim

H151 claims that complete pair-type support does not identify a common-context
uniform-reference ranking when the evaluator's context may be constructed
after the pair is known. Its K=3 counterexample has a pair-conditioned
three-way tie, two observationally equivalent common-context worlds with
opposite unique winners, and a \(1/3\) worst-regret floor for every singleton
policy.

## Independent path

The challenge uses a standalone Node.js implementation with an internal
BigInt rational arithmetic layer and imports no producer module. It:

1. reconstructs the pair-conditioned routes and observed projections;
2. builds the low world by setting every unobserved context outcome to zero;
3. builds the high world by setting every unobserved context outcome to one;
4. derives common-context edges and policy values directly;
5. exhausts all eight binary choices for the three unobserved outcomes; and
6. computes singleton regret floors without reading the producer result.

The Python validator compares the independently written result with H151 only
afterward.

## Outcome

The independent implementation confirms:

- all three observed pair/context outcomes are \(1/2\) in both worlds;
- pair-conditioned policy values are exactly \((1/2,1/2,1/2)\);
- common-context edges are all \(1/4\) in the low world and all \(3/4\) in
  the high world;
- policy 2 is uniquely best in the low world;
- policy 0 is uniquely best in the high world; and
- all eight endpoint completions give worst regret \(1/3\) for each singleton
  policy.

No critical disagreement was found.

## Scope

The challenge establishes a target-identification failure, not a sampling
frequency, confidence, causal-effect, or benchmark-validity claim. It does not
show that pair-conditioned Borda values are undefined. It shows that they
cannot be relabeled as common-context values without context-before-pair
randomization, common context support, invariance, or an explicit transport
assumption.

The public-source premise remains limited to the order described in the
RoboArena paper and official site; current server execution was not observed.

## Evidence identity

- H151 protocol SHA-256:
  `1e90a4dcc07651024c301807c264215142eaa90a79fa0d2a4a31c7ac9f4bb687`
- H151 result SHA-256:
  `cce705e152077072cef5ff6b8c313e975cf345f97483b8d6ea00e7c0eaf22a34`
- Node challenge source SHA-256:
  `c246019b7e5b6b7b40999cddb93e897cd53a1a7a8f5cd5b94bca293f3387fb75`
- independent result SHA-256:
  `1119cb2d4885d996c60d589bfe0c62440e6369876e42c66e9ea075fc3225362e`
- validator SHA-256:
  `5301d6c71390c41a4a993470b0eaec57216e4268556085ec8778d7a9c4c397f5`

## Disposition

H151 is independently confirmed. Existing pair-first data may support a
pair-conditioned operational estimand, but complete pair support and unlimited
same-route repetition do not by themselves support H146/H149's
common-context target. Program work must either implement a context lock or
name and validate the pair-conditioned target on its own terms.
