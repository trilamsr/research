# Protocol: H193 PhAIL lifecycle-key inventory

Date fixed: 2026-07-28

Status: outcome-free key-only protocol fixed before inspecting sidecar schemas.

## Question

H190 found no session/reset/run-metadata lead in public object or source-tree
paths, but it did not test differently named fields inside the already pinned
PhAIL v1.0 episode sidecars. Do the exact 594 `meta.json`/`static.json` pairs
contain an episode-linkable key that could identify an operational session,
assignment block, availability regime, reset boundary, or dependence cluster?

This is a schema-recall audit. A key-name hit is only a candidate for a later
semantics and safe-value protocol; it cannot itself close the chronology gap.

## Fixed inputs

- Exact H187 sanitized cohort CSV:
  `result-h187-phail-context-support-sanitized.csv`, SHA-256
  `ad43fca1da065a1cb7fd84dfa9afc5691c72ebe12e7f165c68a0050e51e87ebe`.
- Exactly 594 unique episode IDs and their 1,188 source paths and SHA-256
  hashes recorded in that CSV.
- Source endpoint:
  `https://storage.eu-north1.nebius.cloud/positronic-public`.

Every fetched object must match its H187 hash. Any mismatch stops the run
without producing a canonical result.

A disposable cache under the project's gitignored `work/` directory may
retain successfully hash-verified objects across endpoint interruptions.
Cache entries are addressed by expected content hash and reverified before
use; the canonical result must not depend on an unverified cache state.

## Fixed lifecycle vocabulary

Match case-insensitive key components after splitting on punctuation:

```text
session
run
batch
block
sequence
seq
trial
shift
operator
worker
user
robot
device
host
machine
reset
restart
sampler
seed
assignment
availability
candidate
roster
pool
retry
abort
deviation
carryover
parent
previous
group
cluster
```

Also report exact full-key matches for `episode_id`, `created_ts_ns`, and
generic `id` only as known identity/time controls, not session candidates.

## Outcome seal

The loader may parse the fixed JSON sidecars and traverse object keys and node
types. It must not retain, compare, summarize, print, or branch on primitive
values other than validating JSON structure. It must never emit source
content or keys outside the fixed lifecycle vocabulary and identity/time
controls.

Values under success, item-count, duration, termination, safety, completion,
HRT, rank, annotation, event-time, note, media, video, telemetry, or other
performance fields remain prohibited. A synthetic test must place distinctive
forbidden values under both flat and nested keys and establish that no value
or prohibited key reaches the projected output.

## Staged validation

1. On synthetic `meta` and `static` fixtures, verify punctuation-aware key
   matching, nested-path handling, deterministic projection, and complete
   exclusion of primitive values and prohibited keys.
2. Verify fail-closed behavior for a source-hash mismatch, duplicate episode,
   missing pair, malformed JSON, and a projected-output schema change.
3. Run the exact 594-episode inventory only after those controls pass.
4. Record, for each retained key path, sidecar type, number of episodes in
   which it appears, node-type counts, and a stable hash of the sorted episode
   IDs. Do not emit the episode IDs themselves.
5. Recompute the complete result from the hash-bound input in `--check`;
   equality with a self-referential or incomplete stored summary is
   insufficient.

## Dispositions

- `candidate_lifecycle_key_found`: at least one non-control lifecycle key
  occurs in the target sidecars. Advance only that fixed key to a separate
  source-semantics and safe-value protocol.
- `no_fixed_vocabulary_lifecycle_key_found`: no such key occurs.
- `input_drift_or_integrity_failure`: a fixed input cannot be verified.

Preserve a null. Do not broaden tokens, interpret timestamp gaps, or inspect
values after seeing the result.

## Scope

A positive key hit does not show that its value is populated, stable,
source-defined, session-like, independent, or sufficient for uncertainty. A
negative result is bounded to the fixed vocabulary and exact sidecars; it does
not exclude opaque names, relationships encoded elsewhere, or private data.
No outcome or performance analysis is authorized.
