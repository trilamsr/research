# H195 independent source-trace challenge

Date: 2026-07-28

Status: pass for corrected v3 within declared scope.

## Independence and scope

The challenger used a separate read-only source-trace review and did not edit
the producer artifacts. It tested the fixed Positronic source chain,
data-flow completeness, identifier semantics, validator closure, public
release boundary, and claim wording. It had no access to PhAIL performance
content. This is an internal technical challenge, not expert human review,
peer review, or external endorsement.

## Candidate v1 blocked

Candidate result SHA-256
`09baa38178bb78cd9ea57af9ba8d51a82e21119b7061422fa4cd23b22bc340c4`
claimed `no_distinct_runtime_identity_found`. Challenge found that it:

- checked assigned names only in `InferenceSession.__init__`;
- omitted the concrete harness-to-writer connection and disk serializer;
- omitted the four public backend metadata producers;
- misused H193's fixed-vocabulary projection as general identifier absence;
- hard-coded material trace booleans behind weak syntactic checks; and
- validated fail-open to unexpected result fields.

The candidate was not relied upon. The protocol and implementation were
amended transparently, and the result remained outcome-free.

## Candidate v2 blocked

Candidate result SHA-256
`1d92fefc04e1e6d99f690c2e29993d4a7b99317ff4174e8300ba51383fcbbf73`
closed the initial gaps but still omitted the actual
`policy_cfg.phail_multiple` composition, `SampledPolicy` reset/meta
forwarding, and server codec wrapper. It supported only its listed source
roster, not the complete fixed public PhAIL path. It was not relied upon.

## Corrected v3 challenge

The corrected trace hash-binds:

- `phail_multiple` and selected-policy reset/meta forwarding;
- the base remote client/server WebSocket chain;
- all ACT, SmolVLA, GR00T, and OpenPI public PhAIL server configurations;
- `VendorServer` construction of `RecordingCodec`;
- per-reset `_RecordingSession` creation and the exact
  `{YYMMDD_HHMMSS}_{process_local_counter:04d}.rrd` locator;
- recording-session and recording-policy metadata forwarding;
- the ready handshake;
- the Harness `reset`-before-`START` order;
- the concrete emitter/receiver connection;
- application of `START` data to static fields;
- `static.json` serialization; and
- the complete outcome-free H190 public release inventory.

Ten focused tests reject injected handshake identifiers, reversed
reset/start order, missing writer wiring, altered static serialization,
public-wrapper metadata injection, recording-locator metadata exposure,
unexpected result fields, and semantic promotion. Exact stored-result
reconstruction passes.

## Disposition

Pass for
`session_recording_locator_created_but_not_exposed_to_writer`.

Every fixed public PhAIL backend activates server-side recording. Each server
policy reset creates a session-specific `.rrd` artifact locator from
second-resolution wall time and a process-local counter. The recording
wrapper's metadata path does not expose the locator to the ready handshake or
episode static writer. The fixed public release inventory has zero `.rrd`
paths.

The locator is not guaranteed unique across server restarts and is not a
physical reset, operator session, exchangeability cluster, or independence
unit. Zero public-release `.rrd` paths does not establish that the configured
server recording locations are unavailable or empty. Backend-internal,
private, injected, and opaquely named identity remain outside scope.
DreamZero's out-of-roster UUID behavior prevents framework-wide absence
claims.

No material concern remains within this scope. Downstream prose should say
"server-recording locator already generated," not "session identifier already
available."
