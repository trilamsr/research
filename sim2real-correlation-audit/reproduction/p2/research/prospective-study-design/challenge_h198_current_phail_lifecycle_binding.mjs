#!/usr/bin/env node
// Independent Node reconstruction of the pinned H198 PhAIL lifecycle path.

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const family = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(family, "..", "..");
const defaultRepo = path.join(root, "work", "h198-positronic-current");
const output = path.join(
  family,
  "result-h198-current-phail-lifecycle-binding-independent-challenge.json",
);
const commit = "01b78e6f62ff5913490c360afdd2712eee070524";
const h196Path = path.join(
  family,
  "result-h196-positronic-session-identity-history.json",
);

function requireCondition(condition, message) {
  if (!condition) throw new Error(message);
}

function git(repo, ...args) {
  return execFileSync("git", ["-C", repo, ...args], {
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
  }).trim();
}

function read(repo, relative) {
  return fs.readFileSync(path.join(repo, relative), "utf8");
}

function hasAll(text, tokens, label) {
  for (const token of tokens) {
    requireCondition(text.includes(token), `${label}: missing ${token}`);
  }
}

function sha256File(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function functionSlice(text, startToken, endToken) {
  const start = text.indexOf(startToken);
  requireCondition(start >= 0, `missing start token ${startToken}`);
  const end = text.indexOf(endToken, start + startToken.length);
  requireCondition(end > start, `missing end token ${endToken}`);
  return text.slice(start, end);
}

function build(repo) {
  requireCondition(git(repo, "rev-parse", "HEAD") === commit, "wrong commit");
  requireCondition(git(repo, "status", "--porcelain=v1") === "", "dirty checkout");

  const files = {
    inference: "positronic/inference.py",
    runner: "positronic/cli/eval/run.py",
    eval: "positronic/eval.py",
    embodiment: "positronic/cfg/embodiment.py",
    ui: "positronic/gui/eval.py",
    harness: "positronic/policy/harness.py",
    writer: "positronic/dataset/ds_writer_agent.py",
    serializers: "positronic/dataset/serializers.py",
    local: "positronic/dataset/local_dataset.py",
    wire: "positronic/wire.py",
    armConfig: "positronic/cfg/hardware/roboarm/__init__.py",
    arm: "positronic/drivers/roboarm/franka.py",
  };
  const source = Object.fromEntries(
    Object.entries(files).map(([key, relative]) => [key, read(repo, relative)]),
  );

  hasAll(source.inference, [
    "embodiment=positronic.cfg.embodiment.droid",
    "'phail': run_cfg.override",
    "driver=eval_ui",
  ], "phail alias");
  const attended = functionSlice(
    source.runner,
    "def main(",
    "\n\n@cfn.config(eval=placeholder",
  );
  hasAll(attended, [
    "if driver is not None:",
    "_run_world(policy, embodiment, None, None",
  ], "attended task binding");
  const begin = functionSlice(
    source.harness,
    "    def _begin_episode(",
    "\n    def _end_episode(",
  );
  hasAll(begin, [
    "if self._task is not None and self._task.reset is not None:",
    "self._task.reset(self.context)",
    "self.policy.new_session",
    "DsWriterCommand.START()",
  ], "begin ordering");
  hasAll(source.embodiment, [
    "def droid(",
    "roboarm_command.Reset()",
    "simulated=False",
    "Serializers.camera_images",
  ], "droid embodiment");
  hasAll(source.harness, [
    "def _home(",
    "self._embodiment.home.items()",
    "self._home(clock)",
  ], "home mechanics");
  hasAll(source.arm, [
    "def _reset(",
    "robot.set_target_joints(target, asynchronous=False)",
    "robot_state._finish_reset()",
  ], "franka reset");
  hasAll(source.serializers, [
    "RobotStatus.RESETTING",
    "RobotStatus.ERROR",
    "return None",
  ], "readiness filter");
  hasAll(source.writer, [
    "after_start = not opened or msg.ts > cmd_msg.ts",
    "case DsWriterCommandType.ABORT_EPISODE:",
    "ep_writer.abort()",
  ], "writer boundary");
  hasAll(source.local, [
    "'uid': uid or uuid.uuid4().hex",
    "'static.json'",
    "'meta.json'",
  ], "episode persistence");
  const uiStart = functionSlice(source.ui, "    def start(", "\n    def _on_stop_button");
  hasAll(uiStart, [
    "context = {keys.TASK: task_name}",
    "context['eval.total_items']",
    "Directive.RUN(**context)",
  ], "UI context");
  hasAll(source.harness, ["meta.update(context)", "DsWriterCommand.STOP"], "context persistence");
  hasAll(source.wire, [
    "ds_agent.add_signal(name, obs.serializer)",
    "TrajectoryOverrideSerializer(cmd.serializer)",
  ], "writer wiring");

  // The attended path's task=None disables the only scene-reset branch.
  const taskBound = !attended.includes("_run_world(policy, embodiment, None, None");
  const sceneReset = taskBound && begin.includes("self._task.reset(self.context)");
  const homeBound =
    source.embodiment.includes("roboarm_command.Reset()") &&
    source.harness.includes("self._home(clock)") &&
    source.arm.includes("asynchronous=False");

  // A synchronous driver motion is not a pre-open Harness gate: _begin_episode
  // has no wait/accept step before START, and attended RUN can call it directly.
  const preOpenHomeGate =
    /await|wait_until|accept|tolerance/.test(begin) &&
    begin.indexOf("DsWriterCommand.START()") >
      Math.max(
        begin.indexOf("await"),
        begin.indexOf("wait_until"),
        begin.indexOf("accept"),
        begin.indexOf("tolerance"),
      );

  // Only robot_state is status-filtered; camera serializers remain active once
  // START opens the writer, so this is not a complete post-reset boundary.
  const completePostResetBoundary =
    source.serializers.includes("RobotStatus.RESETTING") &&
    !source.embodiment.includes("Serializers.camera_images");

  const uiCreatedKeys = [
    "task",
    "eval.object",
    "eval.tote_placement",
    "eval.external_camera",
    "eval.total_items",
    "eval.cap_per_item",
  ];
  const operatorSessionKey = uiCreatedKeys.some((key) =>
    /operator.*session|collection.*session|session.*id/.test(key),
  );
  const resetEvidenceKey = uiCreatedKeys.some((key) =>
    /reset|carryover|previous.*episode/.test(key),
  );

  const h196 = JSON.parse(fs.readFileSync(h196Path, "utf8"));
  requireCondition(
    h196.classification === "collision_resistant_identifier_recorded",
    "H196 classification",
  );
  requireCondition(
    h196.decision_consequence.includes("server-recording locator"),
    "H196 recording join",
  );

  const unitMap = {
    phail_real_hardware_binding: true,
    phail_task_binding: taskBound,
    pre_session_scene_reset_call: sceneReset,
    scene_reset_completion_gate: sceneReset && preOpenHomeGate,
    inter_episode_home_command: homeBound,
    home_completion_gate: preOpenHomeGate,
    post_reset_recording_boundary: completePostResetBoundary,
    persistent_episode_identity: source.local.includes("uuid.uuid4().hex"),
    persistent_operator_session_identity: operatorSessionKey,
    persistent_reset_carryover_evidence:
      resetEvidenceKey && !source.writer.includes("ep_writer.abort()"),
    persistent_directive_context:
      uiStart.includes("Directive.RUN(**context)") &&
      source.harness.includes("meta.update(context)"),
    server_recording_join: true,
  };
  const units = Object.entries(unitMap).map(([unit, supported]) => ({
    unit,
    status: supported ? "supported" : "not_supported",
  }));

  const attacks = [
    ["generic_task_reset_is_phail_binding", !taskBound],
    ["synchronous_driver_reset_is_preopen_acceptance", !preOpenHomeGate],
    ["robot_state_filter_gates_all_recording", !completePostResetBoundary],
    ["arbitrary_context_is_operator_session_id", !operatorSessionKey],
    ["episode_uuid_is_operator_session_id", !operatorSessionKey],
    ["reset_command_is_persistent_reset_evidence", !resetEvidenceKey],
    ["abort_is_persistent_reset_evidence", source.writer.includes("ep_writer.abort()")],
    ["current_source_proves_historical_v1_deployment", true],
  ].map(([attack, rejected]) => ({ attack, rejected }));
  requireCondition(attacks.every((row) => row.rejected), "attack rejection");

  const blobs = Object.values(files)
    .sort()
    .map((relative) => ({
      path: relative,
      git_blob: git(repo, "rev-parse", `${commit}:${relative}`),
    }));
  return {
    schema: "h198-current-phail-lifecycle-binding-independent-challenge-v1",
    method:
      "Independent Node direct-source reconstruction using function-bound slices and semantic attack predicates; imports no producer module.",
    commit,
    source_blobs: blobs,
    h196_sha256: sha256File(h196Path),
    units,
    supported_count: units.filter((row) => row.status === "supported").length,
    not_supported_count: units.filter((row) => row.status === "not_supported").length,
    classification: "mechanics_bound_evidence_incomplete",
    attacks,
    disposition: "pass_with_scope",
    scope:
      "pinned current command binding only; no physical-success, historical-deployment, independence, exchangeability, or performance claim",
  };
}

const args = process.argv.slice(2);
const check = args.includes("--check");
const repoIndex = args.indexOf("--repository");
const repo = repoIndex >= 0 ? args[repoIndex + 1] : defaultRepo;
if (check && !fs.existsSync(repo)) {
  const saved = JSON.parse(fs.readFileSync(output, "utf8"));
  requireCondition(
    saved.schema ===
      "h198-current-phail-lifecycle-binding-independent-challenge-v1",
    "stored schema",
  );
  requireCondition(saved.commit === commit, "stored commit");
  requireCondition(saved.classification === "mechanics_bound_evidence_incomplete", "stored classification");
  requireCondition(saved.supported_count === 5 && saved.not_supported_count === 7, "stored counts");
  requireCondition(saved.attacks.length === 8 && saved.attacks.every((row) => row.rejected), "stored attacks");
  process.stdout.write(`PASS H198 stored independent challenge: ${output}\n`);
  process.exit(0);
}
const result = build(repo);
if (check) {
  const saved = JSON.parse(fs.readFileSync(output, "utf8"));
  requireCondition(JSON.stringify(result) === JSON.stringify(saved), "stored challenge drift");
  process.stdout.write(`PASS H198 independent challenge: ${output}\n`);
} else {
  fs.writeFileSync(output, `${JSON.stringify(result, null, 2)}\n`);
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}
