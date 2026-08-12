# H238 challenge-gate repair

Date fixed: 2026-07-31

Status: prospective repair fixed after domain-expert challenge and before
changing the H238 challenge implementation or stored result. The H238 theorem
and Python census passed review; this repair concerns challenge truthfulness,
topological scope, and runtime trace.

## Diagnosed defects

1. The Node challenge executed only three explicit mutation checks but
   hard-coded `mutation_controls_rejected: 4`. Its interval check was a
   constant inequality rather than an injected mutant evaluated against the
   checker.
2. The validator trusted that literal count and did not require named mutation
   outcomes or exact census counts.
3. `open set` was ambiguous. For \(K\geq3\), additive shared-success pair laws
   occupy a \(K-1\)-dimensional model manifold inside the
   \(\binom K2\)-dimensional ambient pair-score space. The condition \(D<1\)
   is relative-open within that exact model class, not ambient-open.
4. The Node result omitted its runtime even though the reproduction package
   promises runtime-bound independent results.

## Fixed repair

- Execute and name four distinct mutation probes:
  1. remove the \(-p^\top a\) term from regret;
  2. replace strict \(D<1\) by \(D\leq1\);
  3. replace interval width \(1/2\) by \(2/5\) and compare the mutated interval
     with the actual interval function;
  4. claim a minimum-profile policy is a unique winner at \(D=1\).
- Derive the reported rejection count from the four named successful
  rejections.
- Require the exact mutation-name roster, exact denominator-5 census counts,
  all five pair-interval known answers, and the Node runtime in the validator.
- Bind the stored challenge result to this repair protocol as well as the
  original H238 protocol, producer, and producer result.
- Use `relative_open_within_additive_shared_success_model` in machine-readable
  classification and qualify every short-form scientific claim with the exact
  additive model and equal target-context weights.

## Gates

Regenerate the producer and Node challenge results, then require:

- all H238 producer, manuscript-binding, validator, and mutation tests;
- the Node `--check` and evidence-binding validator;
- P2 package-selection tests;
- the complete P2 manuscript dependency gate; and
- successful paper/supplement PDF rebuild.

This repair does not promote H238 to confirmatory evidence, establish ambient
robustness, supply finite-sample uncertainty, or close human methods and
prior-art review.
