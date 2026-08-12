# Decision-case eligibility and claim-alignment protocol

Date fixed: 2026-07-26

## Purpose

This protocol addresses two threats to the P1 decision analysis:

1. a decision case could appear selected because its outcome was interesting; and
2. an audit-defined top-1 decision could be mistaken for a decision explicitly
   claimed by the source paper.

The first control accounts for every paper in the frozen 26-paper corpus. The
second records source-claim strength separately from numerical decision
eligibility. Neither converts the bounded corpus into a prevalence sample.

## Decision-case eligibility

Eligibility is outcome-independent in definition, although the current corpus
was already outcome-exposed before this protocol was written. A paper is
eligible for the finite-panel decision ledger when public or permanently
retained evidence supplies:

1. at least two named policy or policy-checkpoint candidates;
2. real and simulated/evaluator outcomes for the same candidate roster;
3. enough candidate identity to determine real and evaluator winner sets;
4. a source-defined aggregation or an audit-defined aggregation stated before
   interpreting its winner; and
5. sufficient numerical or rank information to recompute winner agreement.

Exact regret additionally requires absolute real outcomes. Rank-only evidence
can establish winner agreement but not regret.

A paper is ineligible when the public evidence has no common candidate roster,
only one policy varies over conditions, the result matrix is not recoverable,
or the source's estimator cannot be reconstructed well enough to identify the
candidate decision. Ineligibility is not evidence against the source paper.

The ledger uses these statuses:

- `eligible_numeric`: winner sets and absolute displayed-real regret are
  recoverable;
- `eligible_rank_only`: winner sets are recoverable, but absolute regret is
  not;
- `ineligible_no_common_roster`: the coefficient does not compare at least two
  candidates on a common recoverable decision target;
- `ineligible_unrecoverable_matrix`: the candidate matrix cannot be
  deconflicted or recovered from available evidence; and
- `ineligible_unreconstructable_estimand`: public values exist, but the
  source-specific estimator or roster cannot be reconstructed into a
  defensible common decision.

Every eligible paper must link to its canonical decision output. Every
ineligible paper must give a source-specific reason.

The separate direct-cell matrix ledger is derived from every retained numeric
source CSV. Eligibility requires at least two stable candidate identities, at
least two commensurable task or condition blocks, and exactly one real and
evaluator value for every candidate-block cell. Different judge metrics are
not pooled as blocks. Checkpoint panels with multiple values per
candidate-task cell require a separate collapse rule and are not direct-cell
matrices.

Candidate identity may use explicit source columns, as for EmbodiedSplat's
base lineage x finetuning status. When task rosters differ, the matrix may use
their candidate intersection only when that outcome-independent rule is
declared, as for the MolmoSpaces appendix panel. Every retained source file,
eligible matrix, and exclusion reason is recorded in
`result-matrix-source-disposition.csv`. Matrix cells are computationally
checked for Cartesian completeness before outcomes are summarized. No panel
may be added or removed because its displayed top-1 result is favorable or
unfavorable. A smaller paper-facing display must be labeled illustrative and
must link to this complete accounting.

## Source-claim alignment

Eligibility does not establish that the source paper claimed top-1 deployment.
For every paper used in a headline decision contrast, record the strongest
source-supported action class:

- `descriptive_association`;
- `relative_ranking`;
- `policy_screening`;
- `policy_selection_or_deployment`; or
- `real-evaluation_substitution`.

Also record:

- the pinned source version and exact passage location;
- whether Pearson is presented alone or with rank-sensitive metrics;
- whether the source itself reports a decision disagreement or limitation;
- whether the P1 decision is source-defined or audit-defined; and
- the strongest wording P1 may use without attributing the audit's decision to
  the source.

An abstract may establish broad intended use, but a claim of a particular
top-1 rule, task mixture, tolerance, or real-test budget requires a source
passage that states it. Otherwise those components remain audit-defined
sensitivities.

## Interpretation

The complete ledger can establish that the audit did not omit an eligible
paper or complete matrix because its decision was favorable. It cannot estimate
a field-wide failure rate because the parent corpus is bounded and
outcome-exposed.

The claim-alignment record determines whether a case tests a source-claimed
decision, a plausible operational consequence, or only a deliberately
audit-defined diagnostic. These roles must not be conflated.
