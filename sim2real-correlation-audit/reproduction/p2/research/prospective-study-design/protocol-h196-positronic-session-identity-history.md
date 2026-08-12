# Protocol: H196 Positronic session-identity history

Date fixed: 2026-07-28

Status at fixation: prospective, source-unexposed, outcome-free source-history
audit. Before this protocol was written, only the public repository identity,
the `main` ref hash, and the already-audited `v0.2.1` source were viewed. No
source, diff, commit message, or file tree after `v0.2.1` was inspected.

Amendment after endpoint expansion, 2026-07-28: the prospectively authorized
direct-definition rule required opening
`positronic/policy/recording.py` (imported by `policy/remote.py`) and
`positronic/offboard/server.py` (imported by all four current backend server
files after `offboard/vendor_server.py` was deleted). While resolving their
endpoint semantics, targeted `git log -S` calls exposed the introduction
commits for the current episode UUID and `.rrd` metadata field before these
two paths had been formally added to the history enumeration. The endpoint
comparison remains within the prospectively fixed expansion rule. Timing and
change-history claims involving the two expansions are result-exposed and
exploratory. The repaired exhaustive history enumeration includes both
expansion paths, preserves the initial mismatch, and does not add further
paths or vocabulary. See
`incident-h196-expansion-history-exposure.md`.

## Question and decision value

Between Positronic `v0.2.1` and the public `main` revision pinned below, did
the public implementation add a collision-resistant inference/session
identifier to persistent episode metadata, or propagate the server-recording
locator identified by H195 into that metadata?

This determines whether P2's concrete repair request is still current. A
positive result should narrow or retire an obsolete request; a null should
strengthen the request only for the pinned public revision. Neither result
authorizes PhAIL performance analysis or establishes a valid dependence
cluster.

The smallest useful result is a complete, hash-bound comparison of the fixed
runtime-to-writer path at the two endpoints, plus the relevant intervening
path history.

## Fixed revisions

Upstream: `https://github.com/Positronic-Robotics/positronic`

- baseline tag: `v0.2.1`;
- baseline commit: `e406176bc526babb06844a48e3627a5c0409eb74`;
- comparison branch: `refs/heads/main`;
- comparison commit resolved with `git ls-remote`:
  `01b78e6f62ff5913490c360afdd2712eee070524`;
- resolution time: `2026-07-28T09:57:28Z`.

The comparison commit is immutable for H196 even if `main` advances.

## Fixed source boundary

Audit the commit range
`e406176bc526babb06844a48e3627a5c0409eb74..01b78e6f62ff5913490c360afdd2712eee070524`
for these H195 path owners:

1. `positronic/policy/remote.py`;
2. `positronic/offboard/client.py`;
3. `positronic/offboard/vendor_server.py`;
4. `positronic/data_collection.py`;
5. `positronic/dataset/episode.py`;
6. `positronic/dataset/ds_writer_agent.py`;
7. `positronic/policy/harness.py`;
8. `positronic/inference.py`;
9. `positronic/wire.py`;
10. `positronic/dataset/local_dataset.py`;
11. `positronic/cfg/policy.py`;
12. `positronic/policy/base.py`;
13. `positronic/policy/codec.py`;
14. `positronic/vendors/lerobot_0_3_3/server.py`;
15. `positronic/vendors/lerobot/server.py`;
16. `positronic/vendors/gr00t/server.py`; and
17. `positronic/vendors/openpi/server.py`.

The result-exposed history repair adds exactly:

18. `positronic/policy/recording.py`; and
19. `positronic/offboard/server.py`.

Use rename detection. A renamed path may be followed only when Git reports it
as a successor to one of these files. At the comparison commit, a directly
imported or invoked Positronic definition may be added only when necessary to
resolve an otherwise incomplete edge in identifier creation, reset,
ready/meta transport, recording-wrapper construction, writer input, or
persistent episode serialization. Every expansion must record the originating
symbol and file, the target symbol and file, and the reason.

Commit-message and diff searches use only this fixed case-insensitive
vocabulary:

`session_id`, `session uuid`, `session_uuid`, `inference_session_id`,
`inference session`, `request_id`, `request uuid`, `request_uuid`,
`execution_id`, `trace_id`, `run_id`, `episode_uuid`, `uuid`, `ulid`,
`recording`, `recording_dir`, `RecordingCodec`, `.rrd`, `ready`, `meta`,
`static`, `reset`, `writer`.

The vocabulary is a routing aid, not evidence of absence. Endpoint semantic
tracing of the complete fixed path is required even if the history search
finds no match.

## Fixed method

1. Acquire full public Git history into isolated work storage and verify that
   both fixed commits exist, the baseline is an ancestor of the comparison
   commit, and the checkout is clean.
2. Record retrieval time, remote, Git version, commit identities and dates,
   ancestry, and hashes of every inspected blob.
3. Enumerate every intervening commit touching a fixed or Git-detected renamed
   path, including the two result-exposed expansion paths. Retain commit hash,
   author date, parent count, subject, name-status, and the fixed-vocabulary
   matches in its relevant patch.
4. Compare the complete H195 semantic chain at both endpoints: identifier or
   locator creation, uniqueness construction, reset binding, client/server
   transport, ready/meta exposure, writer input, and persistent episode
   serialization.
5. For any current identifier or locator, report its exact construction and
   demonstrated uniqueness scope. Do not infer uniqueness from a variable
   name.
6. Produce a deterministic JSON result and fail-closed verifier. Tests must
   reject a wrong endpoint, incomplete path roster, omitted relevant commit,
   unrecorded expansion, blob-hash mismatch, unsupported classification, or
   semantic conclusion inconsistent with the recorded trace.

No PhAIL dataset object, recording location, video, action, telemetry, note,
performance value, outcome, success, reward, duration, safety field, or
private service is accessed.

## Fixed classification

Classify the comparison endpoint as exactly one of:

- `collision_resistant_identifier_recorded`: a distinct identifier is created
  per inference/session with an explicit collision-resistant construction and
  is serialized in persistent episode metadata;
- `recording_locator_recorded_without_collision_resistant_identifier`: the
  H195 server-recording locator reaches persistent episode metadata, but no
  qualifying collision-resistant identifier does;
- `locator_still_unjoined`: the relevant runtime path and locator remain, but
  neither a qualifying identifier nor the locator reaches persistent episode
  metadata;
- `no_relevant_implementation_change`: the endpoint trace is materially
  identical to the H195 result for this question; or
- `architecture_changed_trace_incomplete`: a fixed edge was removed,
  dynamically resolved, moved without a Git-detected rename, or cannot be
  traced to persistent episode metadata under the fixed expansion rule.

If both a qualifying identifier and the locator are recorded, use
`collision_resistant_identifier_recorded` and separately report locator
propagation.

## Acceptance and stop rules

A positive propagation result requires exact source edges from creation
through persistent serialization; a key name or commit message is
insufficient. A null requires a complete endpoint trace within the fixed
boundary and cannot be generalized beyond the pinned public revision.

Preserve every null, partial positive, architectural break, and unfavorable
result. Do not add vocabulary, paths, commits, repositories, or private
storage because of an intermediate result. Stop after the fixed history and
comparison-endpoint trace. Do not open server recordings to test availability.

H196 remains separate from H195: it cannot revise what `v0.2.1` did. Any
change to P2 must state the pinned revision and distinguish current public
implementation from the released PhAIL evaluation stack.

## Main risks

- rename or architecture changes can make a bounded trace incomplete;
- names can suggest an identifier without establishing construction or flow;
- a recording locator can be session-specific yet collide across restarts;
- current public code need not describe the exact historical evaluation
  deployment; and
- a favorable fix could be overgeneralized into reset quality, independence,
  exchangeability, or public recording availability.
