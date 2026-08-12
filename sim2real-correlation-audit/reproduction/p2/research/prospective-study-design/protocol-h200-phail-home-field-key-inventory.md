# Protocol: H200 PhAIL home-field key inventory

Date fixed: 2026-07-28

Status: prospective, outcome-free key-only extension fixed after H199 and
before searching the release sidecars for the new vocabulary.

## Question and decision value

Do the exact 594 public PhAIL v1.0 `meta.json`/`static.json` pairs contain a
differently named field that could record the realized randomized Franka home
target, its perturbation, or its RNG identity?

H193 already tested `reset` and `seed` under its fixed vocabulary and found no
such key. H199 later exposed a source-bound random home-joint target and
therefore justifies a separate, prospectively fixed vocabulary. H193 is not
amended or reinterpreted.

A positive is only a key-name candidate for a separately fixed source-semantics
and safe-value audit. A null closes this exact public sidecar-schema route and
strengthens only the absence-of-public-evidence claim.

## Fixed inputs and integrity

- H187 sanitized cohort CSV:
  `result-h187-phail-context-support-sanitized.csv`, SHA-256
  `ad43fca1da065a1cb7fd84dfa9afc5691c72ebe12e7f165c68a0050e51e87ebe`.
- Exactly 594 unique episode IDs and their 1,188 sidecar paths and SHA-256
  hashes.
- Source endpoint:
  `https://storage.eu-north1.nebius.cloud/positronic-public`.
- H199 result as the reason for the vocabulary extension, not as a source of
  sidecar outcomes.

Every sidecar must match the H187 hash. A disposable content-addressed cache
may be used and must be reverified. The result must remain exactly
reconstructible from public objects or an outcome-free projection.

## Fixed vocabulary

Split every JSON key component on punctuation and match case-insensitively:

```text
home
homing
joint
joints
initial
initialize
initialization
start
starting
pose
rng
random
randomized
randomization
variation
perturbation
target
origin
```

The already-tested H193 components `reset` and `seed` are controls: report
their prior null from H193, but do not silently add them to this new search.

## Outcome and value seal

The loader may parse only the fixed sidecars and traverse keys and node types.
It must not retain, compare, summarize, print, hash, or branch on primitive
values. It must emit no unmatched key.

Exclude every path containing any of these punctuation-split components:

```text
success successful outcome result reward score rank duration termination
terminated completion completed safety hrt annotation event note media video
telemetry item items action actions command commands observation observations
```

The exclusion prevents a generic key such as `target` from exposing action,
command, observation, or performance schemas. Synthetic tests must place
distinctive forbidden values under flat and nested matching keys and prove
that no primitive value or prohibited path reaches output.

## Fixed outputs and classification

Retain only:

- sidecar (`meta` or `static`);
- matched key path;
- category `home_field_candidate`;
- node type;
- episode count; and
- SHA-256 of the sorted matching episode-ID set.

Classify exactly one:

- `candidate_home_field_key_found`;
- `no_fixed_vocabulary_home_field_key_found`;
- `input_drift_or_integrity_failure`.

## Staged validation and challenge

Before the 594-episode run:

1. test punctuation-aware matching and nested traversal on synthetic JSON;
2. prove primitive values and prohibited paths cannot reach the projection;
3. test malformed roots, hash mismatch, duplicate episodes, and missing pairs;
4. test deterministic aggregation and fail-closed stored-result validation.

If the material result is to support P2, independently reconstruct the
key-only inventory with a distinct implementation that imports no producer
module and challenge key-name/semantics, command/evidence, and source/history
overreach.

## Stop and scope

Preserve a null. Do not expand vocabulary, inspect candidate values, add
sidecars, search recordings, interpret timestamps, or open actions,
observations, media, telemetry, performance, or outcomes after seeing the
result.

A key-name hit does not establish that a field is populated, source-defined,
the realized draw, accurate, or sufficient for dependence adjustment. A null
does not prove the field is absent from private systems, recordings, code not
used by the release, or the physical procedure.

