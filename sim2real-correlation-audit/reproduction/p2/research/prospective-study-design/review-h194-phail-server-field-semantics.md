# H194 server-field semantics independent challenge

Date: 2026-07-28

Status: pass after material validator repair.

## Independent census and source path

A separate Node implementation verified the H187/H193 input hashes, all 594
static-object hashes, the exact host/device value counts, policy and date
tables, episode-set hashes, and chronology arrays and totals:

- `server.host` is `0.0.0.0` in all 594 episodes and forms one chronological
  run;
- `server.device` is `cuda` in 267 episodes and missing in 327;
- `device=cuda` occurs exactly for all 151 ACT and 116 SmolVLA episodes;
- `device` is absent exactly for all 164 GR00T and 163 OpenPI episodes; and
- the device chronology has 119 `cuda` runs and 120 missing runs, totaling
  594 episodes.

The pinned Positronic checkout resolves to
`e406176bc526babb06844a48e3627a5c0409eb74`. All four fixed source hashes
match. The cited source lines define `host` as an inference-server bind
address and `device` as generic accelerator-backend metadata, flattened into
the recorded policy metadata.

The disposition
`infrastructure_configuration_not_session_identity` is therefore supported.
Neither field identifies an execution instance, session, reset boundary,
availability regime, or valid uncertainty cluster.

## Material validation concern and repair

The first H194 validator accepted unexpected top-level fields, including
synthetic `performance_score` and `outcome_value` keys. Exact rebuild equality
would catch corruption of the stored result but would not protect against a
future changed producer emitting the same prohibited field.

The corrected validator now requires:

- exact top-level, source-record, field-record, qualification, and
  chronology-record schemas;
- exact verified source records;
- exact policy and UTC-date key sets from H187;
- consistent literal-value keys across counts, hashes, and chronology; and
- policy/date and run-length totals that reconcile to the 594-row cohort.

Synthetic attacks cover source-hash mismatch, missing and duplicate episodes,
top-level and nested unknown/prohibited keys, a third selected field,
nonliteral candidate values, and summary corruption. Eight focused tests and
the exact rebuild check pass. Targeted re-review found no remaining critical
or material issue.

## Scope

H194 is result-exposed because sample values were accidentally printed before
its protocol was fixed. It is an exhaustive exploratory null over two
preselected nonperformance fields. No performance field or value was opened,
and the result does not authorize outcomes or exchangeability claims.
