# Review: H198 current PhAIL lifecycle binding

Date: 2026-07-28

## Disposition

**Pass with scope as `mechanics_bound_evidence_incomplete`.**

At pinned public Positronic commit
`01b78e6f62ff5913490c360afdd2712eee070524`, 5 of 12 fixed units are
supported and 7 are not supported:

- supported: real DROID embodiment binding, inter-episode arm/gripper home
  command, persistent episode UUID, persistent fixed UI directive context, and
  server-recording join;
- not supported: a PhAIL `Task` binding, pre-session scene reset,
  scene-reset completion gate, pre-open home-completion gate, complete
  post-reset recording boundary, persistent operator-session identity, and
  persistent reset/carryover evidence.

The exact `phail` alias is an attended driver path. Its runner passes
`task=None` and `trials=None` into the Harness, so the generic
`Task.reset(context)` branch is not instantiated. The real DROID embodiment
does bind an arm `Reset()` and gripper home value. The Harness emits those
values before the first episode and after each finish or abort, and the Franka
driver performs its arm motion synchronously.

That is not a pre-open acceptance gate. The UI may emit the next `RUN` while
idle; `_begin_episode` immediately creates the policy session and opens the
writer. `RESETTING`/`ERROR` robot-state samples are dropped and inference
waits for a valid robot state, but camera streams are not gated by that arm
status. Thus the implementation supplies useful mechanical and inference
readiness protections without proving or recording a complete accepted
physical initial state.

## Independent challenge

A separate Node implementation imports no producer module. It reconstructs
the command path from function-bound source slices and exact Git objects,
agrees on all 12 units and the 5/7 split, and rejects eight semantic attacks:

1. generic task reset implies PhAIL binding;
2. synchronous driver reset implies pre-open acceptance;
3. robot-state filtering gates every recorded modality;
4. arbitrary UI context is an operator-session identifier;
5. episode UUID is an operator-session identifier;
6. emitting reset is persistent reset evidence;
7. aborting is persistent reset evidence; and
8. current source proves historical `v1.0` deployment.

The challenge disposition is `pass_with_scope`. Producer result SHA-256 is
`9ec06f012f6efe78c29ea96fed360a8060efb8f02b9f14e4f744dad89f6f5e3b`;
challenge result SHA-256 is
`f3ef1e01e7a5e72623c5cf16df3dcbc41ed8fb7c6d8bb6d9f44d53f9bf0f8898`.

## Evidence and verification

- Exact source projection covers 21 fixed/expanded blobs.
- Six direct expansions are recorded with their origin symbol and reason.
- Eleven producer tests reject unit, blob, excerpt, classification, semantic,
  and scope corruption.
- The Node challenge directly binds 12 source blobs and eight semantic
  attacks.
- The producer trace and independent challenge both reproduce exactly.
- No dataset object, server recording, sidecar, media, action, telemetry,
  performance field, score, outcome, or private service was opened.

## Limitations and consequence

Source shows implemented commands, ordering, and serialization only. It does
not establish that hardware reached home, a scene reset succeeded, an
acceptance tolerance was adequate, operators waited, carryover is absent,
episodes are independent or exchangeable, or this commit was used for the
historical `v1.0` release.

P2 may now state the narrower current-source fact: current PhAIL binds real
home mechanics but still lacks the persistent lifecycle evidence and pre-open
acceptance needed to treat those mechanics as an exchangeability or
dependence repair.

