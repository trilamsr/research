# Protocol: H182 positive-contrast artifact reconstruction

Date fixed: 2026-07-27

Status: fixed after source discovery and before repository-tree or selected-file
coding.

## Purpose

Determine whether UMI-Bench and RoboDojo's H178 positive contrasts can be
reconstructed from public artifacts rather than paper prose. This audit tests
public evidence availability, not whether either system executed correctly.

## Exposure before fixation

Source discovery had already exposed:

- the UMI-Bench project page's claim of a unified protocol and its `Code` link,
  which resolves back to the project page;
- the existence and top-level README of the RoboDojo and XPolicyLab
  repositories; and
- their public documentation's broad division between benchmark and policy
  infrastructure.

The audit is therefore exploratory with respect to artifact availability. The
unit rubric, tree predicates, size limits, and decisions below are fixed before
tree enumeration and selected-file coding.

## Fixed source identities

1. UMI-Bench project page: <https://umibenchmark.github.io/>, retrieved
   2026-07-27; record the retrieved HTML hash.
2. UMI-Bench public Hugging Face dataset:
   `UMIbenchmark/UMI-Benchmark-v1` at commit
   `156c7b7fb065bf82a2feb3d2e08c3cd3722f719c`.
3. RoboDojo repository:
   `RoboDojo-Benchmark/RoboDojo` at commit
   `e0703b03bb1af6075400e9d60dc17a792793960c`.
4. XPolicyLab repository:
   `XPolicyLab/XPolicyLab` at commit
   `5071d8ff557f8f258e50aec5b46a701772bc3295`.
5. RoboDojo public documentation at
   <https://robodojo-benchmark.com/doc/>, retrieved 2026-07-27.

No model, checkpoint, dataset archive, result table, video, leaderboard value,
or performance outcome may be downloaded or inspected.

## Fixed reconstruction units

For each system code:

1. `finite_evaluation_frame`: machine-readable task/condition roster or exact
   finite evaluation manifest;
2. `candidate_roster`: machine-readable candidate methods/policies or an exact
   interface-bound roster;
3. `execution_order`: an executable or machine-readable path showing the frame
   and condition are fixed before policy execution;
4. `reset_rule`: an executable, configuration-bound, or exact operational reset
   procedure;
5. `episode_or_trial_identity`: stable per-execution identity and result/log
   schema sufficient to distinguish trials.

Codes are `yes`, `partial`, `no`, or `unresolved`. Documentation alone may
support `partial`; `yes` requires a public machine-readable or executable
artifact at the fixed identity.

## Fixed repository inspection

1. Enumerate path, type, mode, and object identity without opening blobs.
2. Select files using only case-insensitive path terms:
   `task`, `eval`, `reset`, `episode`, `trial`, `result`, `log`, `config`,
   `manifest`, `policy`, `deploy`, and `README`.
3. Exclude model, checkpoint, asset, media, dataset, cache, environment,
   package-lock, and generated-result directories.
4. Open at most 40 text files per repository, each at most 256 KiB and at most
   2 MiB total per repository.
5. Search only for field/control semantics needed by the five units. Do not
   retain or report performance values.

For the UMI-Bench dataset, enumerate sibling names and inspect only README or
metadata files at most 256 KiB. Do not open any data archive.

## Decisions

- `artifact_reconstructed`: all five units are `yes`.
- `artifact_partial`: at least three units are `yes` and the remainder are
  `partial` or `unresolved`.
- `source_described_only`: fewer than three units are `yes`.
- `inconclusive`: access failure prevents the fixed inspection.

The two systems are decided separately. A partial or negative result narrows
P2's evidence label; it does not reverse the paper-source coding or imply that
the evaluation was not performed.

## Validation and stop rule

Record exact source identities, inspected paths and object hashes, byte caps,
unit decisions, and refusal boundaries. Stop after the fixed two systems. Do
not expand to another benchmark, inspect outcomes, run policy code, accept new
terms, authenticate, or contact authors.
