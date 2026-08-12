# Protocol: H201 PhAIL home-field candidate semantics

Date fixed: 2026-07-28

Status: prospective source-semantics protocol fixed after H200 key names were
exposed and before searching the pinned source for those names. Sidecar values
remain unopened.

## Question and decision value

Do H200's three public sidecar key candidates—`joint_names`,
`joint_signal`, and `pose_signals`—source-define or serialize the realized
randomized Franka home target, its perturbation, or its RNG identity?

A positive would justify a separately fixed safe-value audit of only the
qualifying field. A source-defined schema/stream descriptor, generic signal
name, base configuration, or unrelated pose list closes the candidate without
opening sidecar values.

## Fixed source and search

Upstream: `https://github.com/Positronic-Robotics/positronic`

Revision: Positronic `v0.2.1`,
`e406176bc526babb06844a48e3627a5c0409eb74`.

Inputs:

- H200 result SHA-256
  `85e6f82975a6c9e3a6802cfd68d0dcdff954c90e262949c47f1ea7c31dee1010`;
- H199 result SHA-256
  `2571b41e1796e5eb85ac96ac820c73aa0192c1703ffb9bb6abd85f454f0c41a8`.

Search the complete Git tree at the fixed revision for the exact,
case-sensitive strings:

```text
joint_names
joint_signal
pose_signals
```

Record every matching path, Git blob, line number, and containing
definition/constant. Follow only directly referenced imports or constructors
needed to resolve:

1. how each key is produced;
2. what value class it carries;
3. whether it varies by episode or reset;
4. whether it contains the configured base home vector;
5. whether it contains the realized random perturbation/target; and
6. whether it contains a seed or RNG state.

Record each expansion and reason. Stop after 12 expanded paths; classify
unresolved if semantics require broader search. Do not inspect history or
current code.

## Fixed units and classification

For each candidate report:

- producer path and symbol;
- value class from source;
- static versus per-episode/reset behavior;
- realized target present/absent/ambiguous;
- RNG identity present/absent/ambiguous; and
- semantic class:
  `schema_descriptor`, `base_configuration`, `realized_home_evidence`,
  `rng_evidence`, `unrelated`, or `ambiguous`.

Classify exactly one:

- `realized_home_or_rng_evidence_source_defined`;
- `generic_signal_schema_not_home_draw`;
- `mixed_or_ambiguous_candidate_semantics`;
- `source_trace_incomplete`.

## Verification, stop, and scope

Bind every source conclusion to the fixed Git object. Add deterministic tests
for missing search hits, incomplete path coverage, candidate/key mismatch,
schema-descriptor versus realized-value conflation, static versus per-reset
conflation, and source semantics versus historical execution overreach.

Do not open any sidecar value, Parquet, recording, action, observation, media,
telemetry, performance field, outcome, or private service. Do not add search
terms or paths based on results. A source definition does not prove historical
execution fidelity, accurate recording, reset quality, exchangeability, or a
performance effect.

