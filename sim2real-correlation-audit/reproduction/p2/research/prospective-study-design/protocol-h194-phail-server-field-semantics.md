# Protocol: H194 PhAIL server-field semantics and value census

Date fixed: 2026-07-28

Status: result-exposed outcome-free protocol. H193 selected the two fields
before value inspection, but the subsequent exposure incident revealed sample
values `0.0.0.0` and `cuda` before this protocol was fixed.

## Question

Do H193's two infrastructure-key candidates carry a source-defined,
episode-linkable server or device identity that can replace calendar bins with
an operational dependence cluster?

The exact fields are:

```text
static.inference.policy.server.host
static.inference.policy.server.device
```

No other field may be added after value inspection.

## Fixed inputs

- H193 result SHA-256
  `3c9eec888c77e425349ffb9997f0eb249c99b73eb9b24bf94278ee8a2e25f429`.
- Exact H187 sanitized cohort CSV SHA-256
  `ad43fca1da065a1cb7fd84dfa9afc5691c72ebe12e7f165c68a0050e51e87ebe`.
- The 594 H187-hash-bound `static.json` objects in the content-addressed,
  gitignored H193 cache.
- Positronic tag `v0.2.1`, resolved tag/tree identity
  `e406176bc526babb06844a48e3627a5c0409eb74`.

## Fixed analyses

For each of the two selected fields:

1. verify every static object against its H187 SHA-256;
2. report missing count, nonmissing count, literal value counts, and value
   types;
3. cross-tabulate presence and literal value by the already sanitized
   `policy_model`;
4. cross-tabulate presence and literal value by UTC date;
5. sort by `created_ts_ns` and report the number and lengths of contiguous
   value-or-missing runs; and
6. hash the sorted episode set for each value without emitting episode IDs.

Search only the pinned Positronic source tree and its exact file contents for
definitions or uses of the two full keys or their `server.host` and
`server.device` components. Record exact file, revision, and line or object
identity. Do not search the sidecar cache for semantics.

## Fixed qualification rule

A field can advance as an operational cluster candidate only if all are true:

1. the pinned source defines it as an execution-instance, server-instance, or
   physical-device identity rather than a bind address, transport
   configuration, generic accelerator type, or policy-specific option;
2. at least two nonmissing values occur in the release;
3. values are not deterministic functions of policy identity;
4. the field is populated for every episode in the intended target; and
5. its source semantics support stable equality within and meaningful
   difference across dependence clusters.

Otherwise the disposition is
`infrastructure_configuration_not_session_identity`. A constant, generic, or
policy-deterministic result must be preserved.

## Outcome seal and exposure

Only the two selected nonperformance values, H187 sanitized design fields, and
pinned source semantics may be inspected. Success, item count, duration,
termination, safety, HRT, rank, note, video, telemetry, and all other
performance fields remain prohibited.

Because candidate values were accidentally exposed before this protocol,
H194 is exploratory/result-exposed even though the field set and exhaustive
analyses are now fixed. It cannot provide confirmatory evidence.

## Validation

Synthetic tests must reject a third field, source-hash mismatch, missing or
duplicate episode, nonliteral candidate value, prohibited output key, and
stored-result corruption. The canonical check must rebuild from exact cached
objects and require equality.

## Scope

Even a qualifying infrastructure identifier would support only a new
dependence/support sensitivity. It would not establish reset quality,
exchangeability, target weighting, or authorization to open outcomes.
