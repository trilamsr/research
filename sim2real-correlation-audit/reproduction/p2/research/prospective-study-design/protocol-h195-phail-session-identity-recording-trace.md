# Protocol: H195 PhAIL session-identity recording trace

Date fixed: 2026-07-28

Status: source-exposed, result-exposed, outcome-free implementation trace. A preliminary
repository search had already shown that `RemotePolicy.reset()` creates an
`InferenceSession` and that the policy metadata path emits server metadata.
This protocol was fixed before inspecting the full identity creation,
transport, and dataset-writing chain. H195 is therefore explanatory and
result-exposed, not prospective.

Amendment after independent challenge, 2026-07-28: the first implementation
checked only the base client/server objects and did not establish the concrete
emitter/receiver wiring, disk serialization, or all four PhAIL backend
metadata producers. It also used H193's fixed-vocabulary projection as though
it were an exhaustive identifier-key census. That candidate result
(`09baa381...340c4`) is not relied upon. The repair adds the exact wiring,
writer, and four backend files below, drops the unsupported H193 absence
inference, makes validation fail-closed, and narrows the question to an
explicit Positronic-generated application-level identifier. Backend-internal,
private, injected, and opaque identifiers remain outside scope.

Second amendment after targeted re-review, 2026-07-28: the v2 repair still
omitted `policy_cfg.phail_multiple`, `SampledPolicy` forwarding, and the
server-side codec wrapper. It supported only the listed roster, not the
complete fixed public PhAIL path. Expanding those exact edges exposed an
unanticipated positive: every public PhAIL server configuration supplies a
recording directory, and `RecordingCodec` creates a per-reset `.rrd` artifact
locator from second-resolution wall time plus a process-local counter. Its
metadata path does not expose that locator. Candidate v2
(`1d92fefc...cbbf73`) is also not relied upon. The corrected classification
therefore distinguishes a session-specific artifact locator from a globally
unique identifier and from a dependence cluster.

## Question

Across the fixed public PhAIL paths in pinned Positronic `v0.2.1`, does
Positronic explicitly generate a stable, serializable application-level
identifier for each inference session and carry it into the episode metadata
writer?

## Fixed source and roster

Upstream: `https://github.com/Positronic-Robotics/positronic`

- tag: `v0.2.1`;
- commit: `e406176bc526babb06844a48e3627a5c0409eb74`;
- local hash-verified checkout:
  `work/h194-positronic-v0.2.1`.

Inspect only the following implementation chain and direct definitions they
invoke:

1. `positronic/policy/remote.py`;
2. `positronic/offboard/client.py`;
3. `positronic/offboard/vendor_server.py`;
4. `positronic/data_collection.py`;
5. `positronic/dataset/episode.py`; and
6. `positronic/dataset/ds_writer_agent.py`.

Directly imported Positronic definitions may be opened only when necessary to
resolve an otherwise ambiguous value or call edge. Record every expansion and
why it was necessary. Do not search the public sidecars for new fields.

The challenge-authorized repair adds:

7. `positronic/policy/harness.py`, for reset-to-static-metadata order;
8. `positronic/inference.py`, for the actual harness-to-writer connection;
9. `positronic/wire.py`, for `DsWriterAgent` construction;
10. `positronic/dataset/local_dataset.py`, for concrete `static.json`
    serialization; and
11. the four public PhAIL backend metadata producers:
    `positronic/vendors/lerobot_0_3_3/server.py`,
    `positronic/vendors/lerobot/server.py`,
    `positronic/vendors/gr00t/server.py`, and
    `positronic/vendors/openpi/server.py`.
12. `positronic/cfg/policy.py` and `positronic/policy/base.py`, for the
    `phail_multiple` composition and selected-policy reset/meta forwarding;
13. `positronic/policy/codec.py`, for server recording wrapper construction,
    per-reset locator creation, and metadata forwarding; and
14. the complete outcome-free H190 release-inventory projection, solely to
    count `.rrd` paths in the public release.

DreamZero is inspected only as adverse scope evidence: it creates a UUID
session identifier but is not in the public PhAIL four-policy configuration.
That counterexample prohibits any framework-wide absence claim.

## Fixed trace units

For each unit, retain exact file hash and line range:

1. inference-session identity creation;
2. identity transport between client and server;
3. the object holding the identity at policy runtime;
4. the policy metadata dictionary exposed to data collection;
5. the dataset writer's static-metadata input; and
6. the serialized sidecar fields, if explicitly defined.

Classify the repaired chain as one of:

- `identity_created_and_recorded`;
- `identity_created_but_not_exposed_to_writer`;
- `identity_exposed_to_writer_but_not_serialized`;
- `session_recording_locator_created_but_not_exposed_to_writer`;
- `no_positronic_generated_stable_recorded_identifier_found`; or
- `trace_incomplete`.

## Acceptance rule

An explanatory omission claim requires all of the following:

1. a distinct runtime identifier is created for each inference session;
2. a fixed call path binds a new inference session to an episode reset;
3. the metadata path used by the writer can be traced without speculation;
4. the runtime identifier is absent from that metadata path; and
5. an outcome-free, exhaustive key-name check independently confirms that no
   emitted public sidecar key carries it.

Any ambiguous or dynamic edge yields `trace_incomplete`. A per-episode
inference request is not a physical reset, operator session, exchangeability
cluster, or independence unit.

The narrower null
`no_positronic_generated_stable_recorded_identifier_found` requires exact
wiring and serialization edges, inspection of every fixed public PhAIL
backend metadata producer, no explicit identifier creation/generator in that
source roster, and explicit disclosure that external backend internals,
private configuration, injected metadata, and opaque names remain unresolved.
It does not require or imply an exhaustive sidecar-key absence result.

The locator-positive classification requires all four fixed public PhAIL
server configurations to activate `recording_dir`, the server wrapper to
create one recording session per reset, an exact locator construction, a
metadata path that omits the locator, and the concrete client-to-writer trace.
The locator must be described with its actual uniqueness scope. A public
release count of zero `.rrd` paths establishes only that the fixed release
inventory does not bundle these server recordings; it does not establish that
the configured server recording locations are unavailable or empty.

## Outcome and exposure controls

- Do not open any PhAIL performance field or value.
- Do not inspect videos, telemetry, notes, outcomes, success, reward, rank,
  duration, termination, or safety content.
- Do not add source files or search terms because of a favorable intermediate
  result.
- Preserve a null or incomplete trace.

## Decision consequence

A supported omission trace would strengthen P2's evidence-request section:
future public pairwise/global evaluations should retain the runtime episode or
inference-session identifier already available in the framework, while still
separately recording physical reset/carryover and operator-session identity.
It would not authorize PhAIL outcome analysis or make the runtime identifier a
valid dependence cluster by itself.
