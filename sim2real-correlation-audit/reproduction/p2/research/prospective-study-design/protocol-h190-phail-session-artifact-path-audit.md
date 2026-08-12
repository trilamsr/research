# Protocol: H190 PhAIL session-artifact path audit

Date fixed: 2026-07-28

Status: outcome-free path-only protocol fixed before inventory/tree search.

## Question

Do the exact PhAIL v1.0 public dataset inventory or pinned official source
trees expose a source-recorded session, reset, sequence, batch, or
run-metadata artifact that could close H187's chronology-identity gap?

## Fixed sources

- Public dataset prefix: `phail/v1.0/dataset/` at the source-declared Nebius
  endpoint, required to match H187 inventory SHA-256
  `8b69b6ad8c14b1f5d920dc7aa8c833c79536a8f3405205e9eb5d4f63e5353982`.
- Positronic tag `v0.2.1`, resolved tag/tree identity
  `e406176bc526babb06844a48e3627a5c0409eb74`.
- PhAIL paper/analysis snapshot
  `18ce72d5703dcbbbb10a980336aa5a1622601fb4`.

## Fixed path tokens

Case-insensitive path-component or filename matches:

```text
session
run_metadata
run-metadata
reset
sequence
batch
```

Also report root-level `.yaml`/`.yml`/`.json` objects outside episode
directories, without opening them.

## Method

1. Enumerate and hash the complete public inventory.
2. Retain only matching object keys and structural metadata
   `(key, size, ETag, LastModified)`.
3. Enumerate the two pinned Git trees through source APIs and retain only
   matching paths, type, object identity, and size when available.
4. Classify each path as dataset artifact, implementation/documentation lead,
   test/example, or unrelated lexical collision.
5. Do not fetch candidate object content under H190. Any content inspection
   requires a separately fixed allowlist and prohibited-field gate.

## Passing and adverse results

A content-stage lead exists only if a source-owned path plausibly stores
episode-linkable session/reset/run identity. Documentation, code, tests, or
examples may clarify semantics but do not themselves supply the 594-row join.

Preserve a zero data-artifact result. Never infer session identity from
timestamps, the constant `000000000000` storage partition, outcomes, notes,
media, Parquet, telemetry, or mutable service state.

## Scope

This is a recall-bounded path audit, not proof that no private or differently
named session record exists. A passing path would not establish physical reset
adequacy, independence, or exchangeability.
