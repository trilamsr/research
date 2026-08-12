# Protocol: H198 current PhAIL lifecycle binding

Date fixed: 2026-07-28

Status at fixation: mixed-exposure, outcome-free source audit. H196 already
exposed the pinned current `positronic/inference.py`,
`positronic/policy/harness.py`, dataset writer/serializer path, policy-session
path, and four server commands. Those files show generic reset, home,
episode-context, UUID, and recording-locator capabilities. The current
PhAIL command's direct runner, task, embodiment, and UI definitions have not
been opened for this question.

## Question and decision value

At pinned public Positronic commit
`01b78e6f62ff5913490c360afdd2712eee070524`, does the documented `phail`
command actually bind the generic harness to:

1. a physical scene-reset operation with completion/acceptance evidence;
2. an inter-episode home operation with completion/acceptance evidence;
3. a persistent operator-session or collection-session identity; and
4. persistent reset/carryover evidence?

H196 establishes available framework fields, not that the PhAIL command
instantiates them. A positive binding could narrow P2's remaining
instrumentation request. A partial or null binding would distinguish useful
generic lifecycle mechanics from the missing evidence needed for dependence
and exchangeability.

## Fixed revision and base paths

Upstream: `https://github.com/Positronic-Robotics/positronic`

Pinned commit:
`01b78e6f62ff5913490c360afdd2712eee070524`

Already exposed base paths:

1. `positronic/inference.py`;
2. `positronic/policy/harness.py`;
3. `positronic/data_collection.py`;
4. `positronic/dataset/ds_writer_agent.py`;
5. `positronic/dataset/episode.py`;
6. `positronic/dataset/local_dataset.py`;
7. `positronic/cfg/policy.py`;
8. `positronic/policy/base.py`;
9. `positronic/policy/remote.py`;
10. `positronic/offboard/client.py`; and
11. `positronic/offboard/server.py`.

Prospectively fixed direct paths:

12. `positronic/cli/eval/run.py`;
13. `positronic/eval.py`;
14. `positronic/cfg/embodiment.py`;
15. `positronic/gui/eval.py`.

A directly imported or invoked Positronic definition may be added only when
one of those 15 paths leaves an otherwise unresolved edge in the exact
`phail` alias → runner → harness construction → task reset → embodiment home
→ directive context → writer serialization path. Record every expansion,
origin symbol/path, target symbol/path, and reason. Do not inspect Git history
or broaden the question based on a result.

## Fixed qualification units

Code support for a unit requires an exact source edge, not a name or comment.
Report each as `supported`, `not_supported`, or `unresolved`.

1. `phail_real_hardware_binding`: the `phail` command binds a real embodiment,
   not only a generic or simulated configuration.
2. `phail_task_binding`: the command supplies a non-null `Task`.
3. `pre_session_scene_reset_call`: the instantiated path calls a task/scene
   reset before policy-session creation.
4. `scene_reset_completion_gate`: the path observes completion or checks an
   acceptance condition before session creation/recording.
5. `inter_episode_home_command`: the instantiated embodiment has a nonempty
   home command emitted before the first and between completed episodes.
6. `home_completion_gate`: the path observes arrival/completion or checks a
   tolerance before opening the next episode.
7. `post_reset_recording_boundary`: the writer excludes pre-reset/pre-start
   samples and retains the post-reset first sample by implemented ordering.
8. `persistent_episode_identity`: a collision-resistant episode identity is
   serialized.
9. `persistent_operator_session_identity`: a source-created, stable
   operator/collection-session identifier is serialized across its episodes.
10. `persistent_reset_carryover_evidence`: reset attempt/result, accepted
    state, prior-episode link, or carryover evidence is serialized.
11. `persistent_directive_context`: fixed context carried by the PhAIL UI is
    serialized into episode static metadata.
12. `server_recording_join`: the server recording locator is serialized into
    episode static metadata.

An arbitrary operator-supplied key does not qualify as a source-created
identity or reset record. A command emission does not qualify as a completion
gate. An inference-session websocket, episode UUID, wall-clock timestamp,
directory counter, robot descriptor, operator pose, or constant host/device
does not qualify as operator-session identity.

## Fixed classification

Classify exactly one:

- `lifecycle_evidence_bound`: units 1--12 are supported;
- `mechanics_bound_evidence_incomplete`: at least one of units 3, 5, or 7 is
  supported, but any of 4, 6, 9, or 10 is not supported or unresolved;
- `generic_capability_not_bound_to_phail`: the generic harness exposes reset
  or home mechanics but neither unit 3 nor unit 5 is supported on the exact
  PhAIL command;
- `trace_incomplete`: the fixed/direct-expansion rule cannot resolve an edge
  needed to decide the preceding classifications.

## Method and verification

1. Acquire the exact public Git commit into isolated work storage; verify
   commit identity and a clean checkout.
2. Hash every inspected blob and record line-bound source edges for all 12
   units.
3. Resolve only the exact current `phail` command path. Do not infer from
   unrelated tests, examples, simulated configs, teleoperation commands, or
   generic capability alone.
4. Produce deterministic JSON and an exact offline verifier.
5. Tests must reject a wrong commit, missing base path, unrecorded expansion,
   blob-hash mismatch, missing unit, invalid evidence status, unsupported
   classification, command-versus-completion conflation, arbitrary-context
   identity promotion, or any claim that H198 establishes physical reset
   adequacy or exchangeability.

## Stop and scope

Preserve positive mechanics, null evidence fields, partial bindings, and
architectural breaks. Do not open a dataset object, server recording, episode,
sidecar, media item, action, telemetry, performance field, score, outcome,
success, reward, duration, or private service.

Source ordering can show what the implementation commands and records. It
cannot establish that a physical reset succeeded, a tolerance was adequate,
operators followed the workflow, hardware reached home, carryover is absent,
episodes are independent/exchangeable, or the pinned code was used for the
historical `v1.0` release.

