# H196 independent-method source-history challenge

Date: 2026-07-28

Status: pass with scope narrowing for the pinned comparison endpoint.

## Independence and scope

The challenge used a separate Node implementation that reads immutable Git
objects directly. It did not import the producer module. It independently
checked the two endpoint commits, 19 fixed/expanded paths, 51 relevant
commits, all four current public PhAIL server commands, the server
recording-to-ready path, the remote-session-to-writer path, UUID construction,
and both persistent metadata serializers. Ten semantic mutations were
rejected.

The challenge did not access a PhAIL dataset object, performance field, server
recording, private storage location, video, action, telemetry, note, or
outcome. It is an internal technical challenge, not expert human review, peer
review, or external endorsement.

Producer result SHA-256:
`9f832fddbdb90383ed6cbb330628dce0c7494d703a8c5889e22d26e88d0cd42c`.

Independent challenge result SHA-256:
`0fee1cf30115f698402b292d04871d38ac00ab604872bbfc59c10ea3de115555`.

## Reconstructed result

At public Positronic commit
`01b78e6f62ff5913490c360afdd2712eee070524`:

- each of the four public PhAIL server commands still configures a server
  recording directory;
- each server WebSocket session constructs a `Recorder`;
- the recording session exposes its full `.rrd` path as `recording.rrd`;
- the ready handshake includes that session metadata;
- the client and selected policy preserve it;
- the harness prefixes it as
  `inference.policy.server.recording.rrd` and supplies it to the writer at
  episode finalization;
- the writer serializes it to `static.json`; and
- normal local episode creation separately writes a `uuid.uuid4().hex` value
  under `uid` in `meta.json`.

The independent implementation reconstructs the same 51 path-history commits
and the same result-exposed introduction commits for the UUID and `.rrd`
metadata field.

## Scope challenge and disposition

The classification label
`collision_resistant_identifier_recorded` can be misread if “identifier” is
silently promoted to a shared server-side inference-session ID. The source
supports a narrower two-field design:

1. `uid` is a collision-resistant **episode identity** created by the dataset
   writer. It is not embedded in or sent back to the server recording.
2. `inference.policy.server.recording.rrd` is the explicit
   episode-to-server-recording join. Its filename remains second-resolution
   wall time plus a process-wide counter and is not proven unique across
   process restarts.

The producer interpretation already makes this distinction, so no result
change is required. Downstream prose must not say that current code propagates
one collision-resistant session ID end to end. It may say that pinned current
code records a UUID episode identity and, separately, the configured server
recording locator.

The current endpoint does not revise H195's historical `v0.2.1` result, prove
that the historical PhAIL deployment used later code, retroactively add fields
to released episodes, establish server-recording availability, or identify a
physical reset, operator session, exchangeability cluster, or independence
unit.

The recorded path-boundary incident is correctly handled: endpoint expansion
was prospective under the original rule, while change-timing claims for the
two expansion files are result-exposed and exploratory.

## Disposition

Pass with the stated scope narrowing. No unresolved material issue remains for
the pinned current-source endpoint. P2 may update its repair language only if
it preserves the historical/current distinction and the two-field identity
distinction above.

