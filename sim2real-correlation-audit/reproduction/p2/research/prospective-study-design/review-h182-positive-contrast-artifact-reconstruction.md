# H182 positive-contrast artifact reconstruction

Date: 2026-07-27

Status: completed bounded public-artifact audit.

## Decision

| system | finite frame | candidate roster | execution order | reset rule | episode/trial identity | decision |
|---|---:|---:|---:|---:|---:|---|
| UMI-Bench | partial | no | no | partial | partial | `source_described_only` |
| RoboDojo | yes | yes | yes | partial | yes | `artifact_partial` |

At least one positive contrast is therefore materially reconstructable from
public artifacts, but neither is fully artifact-reconstructed under H182's
five-unit rule. P2 may use RoboDojo as an `artifact_partial` positive contrast
and UMI-Bench as `source_described_only`. It may not imply that either released
an independently executable physical evaluation package.

## UMI-Bench

The project page and pinned dataset card expose the ten-task frame and the
dataset tree exposes task/session manifests. Those artifacts concern the
released demonstration corpus. They do not expose the three-method evaluation
roster, a common evaluation episode list, the evaluation runner or assignment
path, or stable identities for the paper's evaluation rollouts.

The paper-described reset images, scene JSON, common episode lists, and rollout
identifiers therefore remain useful source statements, but the public
artifacts inspected here do not independently reconstruct them as an
evaluation package.

### Fixed identities and trace

- Project page: <https://umibenchmark.github.io/>, retrieved 2026-07-27,
  HTML SHA-256
  `8f798c0578ea67f1a7ad7b56ba1398076edb9d8c6e27c873ecf91960ec21e518`.
- Dataset: `UMIbenchmark/UMI-Benchmark-v1`, commit
  `156c7b7fb065bf82a2feb3d2e08c3cd3722f719c`.
- Dataset README: 5,413 bytes, SHA-256
  `554670d11784dab85ae5199a24c7fccfa0734713d79f15b73ac8806b2913f3f9`.
- Top-level tree: `data/`, `metadata/`, `scripts/`, `.gitattributes`, and
  `README.md`. Metadata path names expose ten task families, session lists,
  scene mappings, and chunk manifests. No data archive, script, model,
  checkpoint, result, video, or performance outcome was opened.

## RoboDojo

The pinned RoboDojo source reconstructs a 54-task runnable configuration
inventory, fixes task/config/policy/seed arguments before the client begins,
passes those values through the policy-server and environment-client path,
and assigns run, evaluation, trial, layout, and result-path identities.
XPolicyLab's pinned source exposes 41 policy adapter directories and a common
evaluation interface, including policy-side state reset between episodes.

The released evaluator also contains an executable simulator reset path and
layout replay/stability logic. That is not promoted to `yes` for the physical
positive contrast: the inspected public package does not release the
RoboDojo-RealEval operator reset/acceptance interface described by the paper.

### Fixed identities and trace

- Documentation: <https://robodojo-benchmark.com/doc/>, retrieved 2026-07-27,
  HTML SHA-256
  `19e951d0c7f50ad4f0c1d95c05f4cfc8b580b81bf005f21103d58f4ebedbc22c`.
- RoboDojo: commit
  `e0703b03bb1af6075400e9d60dc17a792793960c`.
- XPolicyLab: commit
  `5071d8ff557f8f258e50aec5b46a701772bc3295`.
- The dependency-light task inventory executed successfully with 54/54
  runnable task configurations, zero config-only entries, and output SHA-256
  `25f3f274341341fae029411f87fb33115c26c6ccd5990de40541761a948ed38a`.

Selected RoboDojo blobs, totaling 101,209 bytes:

| path | blob | bytes |
|---|---|---:|
| `README.md` | `e8f12335fea7a6372ea6be023f7621f587770ae9` | 9,150 |
| `scripts/eval_policy.sh` | `b86c88e0d02307963954b13ec5338181c67177df` | 5,613 |
| `scripts/internal/run_policy_eval.sh` | `8c01af87a56539a2aeb5f353a50d9d1c9c125836` | 3,145 |
| `scripts/internal/task_inventory.py` | `cf238996e75946d8ffdb9153ac6d75cc7c21178f` | 10,939 |
| `scripts/internal/summarize_result.py` | `19ce6bf8e027a5fac1869f201b33a8f62e1df82b` | 24,181 |
| `src/eval_client/eval_env.py` | `dad90a823f8d1c9881cbd6c2cb7df0c9f47d7e89` | 44,813 |
| `task/RoboDojo/config/_task.yml` | `236d82eb436f19e78ff9b113343e083b20b0c885` | 2,651 |
| `task/RoboDojo/task_registry.py` | `ddd119ca1c236927923dfd8998394d5a970cbeda` | 717 |

Selected XPolicyLab blobs, totaling 28,153 bytes:

| path | blob | bytes |
|---|---|---:|
| `README.md` | `dbc5a25f5974a2738789aa7e80a912946b5699ee` | 25,430 |
| `XPolicyLab.py` | `635484277e69a4bfd48b2fe2d1171a5b64e78391` | 206 |
| `policy/ACT/deploy.yml` | `8507b6e1a78df8fe36af60c5a112788f5af1ea5b` | 703 |
| `policy/ACT/eval.sh` | `6d2f7614bd70dfad1a0c3510a856e94cb22ddc95` | 1,814 |

## Refusal and interpretation boundaries

- No model, checkpoint, dataset archive, media, result file, leaderboard value,
  or performance direction/magnitude was downloaded or inspected.
- Repository execution was limited to the dependency-light task inventory; no
  evaluator, simulator, policy, or robot code was run.
- Public artifact absence is not evidence that a protocol was not executed.
- Simulator reset code is not evidence of physical reset validity.
- The audit is exploratory with respect to artifact availability because
  top-level source discovery preceded protocol fixation, as disclosed in the
  protocol.

## P2 consequence

The positive-design side of P2 is now asymmetric and more precise:

1. RoboDojo demonstrates that the common-rubric contrast can be checked
   substantially in released machinery, while the physical reset gate remains
   source-described.
2. UMI-Bench remains a paper-source contrast because its released corpus is
   not the evaluation package described in the paper.
3. Claim drafting may begin only with these strength labels visible. External
   methods and robotics review remains required before release.
