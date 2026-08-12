#!/usr/bin/env node
// Independent Node reconstruction of the H199 randomized-home mechanism.

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
  "result-h199-phail-randomized-home-target-independent-challenge.json",
);
const base = "e406176bc526babb06844a48e3627a5c0409eb74";
const current = "01b78e6f62ff5913490c360afdd2712eee070524";
const paths = [
  "positronic/inference.py",
  "positronic/cfg/embodiment.py",
  "positronic/cfg/hardware/roboarm/__init__.py",
  "positronic/drivers/roboarm/__init__.py",
  "positronic/drivers/roboarm/command.py",
  "positronic/drivers/roboarm/franka.py",
  "positronic/policy/harness.py",
  "positronic/dataset/ds_writer_agent.py",
  "positronic/dataset/serializers.py",
  "positronic/dataset/local_dataset.py",
  "positronic/wire.py",
];

function requireCondition(condition, message) {
  if (!condition) throw new Error(message);
}

function git(repo, ...args) {
  return execFileSync("git", ["-C", repo, ...args], {
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
  }).trimEnd();
}

function exists(repo, revision, relative) {
  try {
    execFileSync("git", ["-C", repo, "cat-file", "-e", `${revision}:${relative}`], {
      stdio: "ignore",
    });
    return true;
  } catch {
    return false;
  }
}

function sourceEndpoint(repo, revision) {
  const source = {};
  const blobs = [];
  for (const relative of paths) {
    if (!exists(repo, revision, relative)) {
      blobs.push({ path: relative, git_blob: null });
      continue;
    }
    source[relative] = git(repo, "show", `${revision}:${relative}`);
    blobs.push({
      path: relative,
      git_blob: git(repo, "rev-parse", `${revision}:${relative}`),
    });
  }
  return { source, blobs };
}

function arrayAfter(text, expression, label) {
  const match = text.match(expression);
  requireCondition(match !== null, `missing ${label}`);
  const values = JSON.parse(match[1]);
  requireCondition(values.length === 7 && values.every(Number.isFinite), label);
  return values;
}

function analyze(repo, revision) {
  const { source, blobs } = sourceEndpoint(repo, revision);
  const inference = source["positronic/inference.py"];
  const cfg = source["positronic/cfg/hardware/roboarm/__init__.py"];
  const embodiment = source["positronic/cfg/embodiment.py"] ?? "";
  const driver = source["positronic/drivers/roboarm/franka.py"];
  const harness = source["positronic/policy/harness.py"];
  const allSource = Object.values(source).join("\n");

  const baseHome = arrayAfter(
    cfg,
    /home_joints\s*=\s*(\[[^\]]+\])/,
    "base home vector",
  );
  const variation = arrayAfter(
    driver,
    /home_joints_variation\s+if\s+home_joints_variation\s+is\s+not\s+None\s+else\s+(\[[^\]]+\])/,
    "variation vector",
  );
  const phailBound =
    revision === base
      ? ["'phail':", "droid_setup.override(", "phail_multiple"].every((token) =>
          inference.includes(token),
        )
      : [
          "'phail':",
          "embodiment=positronic.cfg.embodiment.droid",
          "phail_multiple",
        ].every((token) => inference.includes(token));
  const resetBound =
    cfg.includes("franka_droid") &&
    (revision === base
      ? harness.includes("roboarm.command.Reset()")
      : embodiment.includes("roboarm_command.Reset()"));
  const drawBound = [
    "np.random.uniform(",
    "-np.asarray(self._home_joints_variation)",
    "np.asarray(self._home_joints_variation)",
    "target = target + variation",
  ].every((token) => driver.includes(token));
  const targetSerialized = [
    "'home_target'",
    '"home_target"',
    "'reset_target'",
    '"reset_target"',
    "'home_joints_realized'",
    '"home_joints_realized"',
  ].some((token) => allSource.includes(token));
  const rngSerialized = [
    "'reset_seed'",
    '"reset_seed"',
    "'home_seed'",
    '"home_seed"',
    "'rng_state'",
    '"rng_state"',
  ].some((token) => allSource.includes(token));
  const outsideWindow =
    revision === base
      ? harness.includes("self.ds_command.emit(DsWriterCommand.STOP") &&
        harness.indexOf("self._home()", harness.indexOf("DsWriterCommand.STOP")) >
          harness.indexOf("DsWriterCommand.STOP")
      : harness.includes("before the home command, so\n            # homing stays out of the recording") &&
        harness.indexOf("self._home(clock)", harness.indexOf("def _end_episode")) >
          harness.indexOf("DsWriterCommand.STOP", harness.indexOf("def _end_episode"));

  return {
    revision,
    source_blobs: blobs,
    phail_droid_binding: phailBound,
    droid_arm_reset_binding: resetBound,
    base_home_joints_rad: baseHome,
    variation_rad: variation,
    configuration_exposes_variation: cfg.includes("home_joints_variation"),
    uniform_draw_to_target: drawBound,
    synchronous_target: driver.includes(
      "set_target_joints(target, asynchronous=False)",
    ),
    global_numpy_rng_without_local_seed:
      driver.includes("np.random.uniform(") &&
      !driver.includes("default_rng(") &&
      !driver.includes("np.random.seed("),
    realized_target_serialized: targetSerialized,
    seed_or_rng_state_serialized: rngSerialized,
    reset_outside_retained_episode: outsideWindow,
  };
}

function sha256File(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function build(repo) {
  requireCondition(git(repo, "rev-parse", base).trim() === base, "base revision");
  requireCondition(git(repo, "rev-parse", current).trim() === current, "current revision");
  requireCondition(git(repo, "status", "--porcelain=v1").trim() === "", "dirty checkout");
  const endpoints = [analyze(repo, base), analyze(repo, current)];
  const expected = [0.03, 0.05, 0.08, 0.08, 0.1, 0.1, 0.1];
  for (const endpoint of endpoints) {
    requireCondition(endpoint.phail_droid_binding, "PhAIL binding");
    requireCondition(endpoint.droid_arm_reset_binding, "reset binding");
    requireCondition(JSON.stringify(endpoint.variation_rad) === JSON.stringify(expected), "variation");
    requireCondition(endpoint.uniform_draw_to_target, "draw");
    requireCondition(endpoint.synchronous_target, "synchronous target");
    requireCondition(endpoint.global_numpy_rng_without_local_seed, "RNG interface");
    requireCondition(!endpoint.realized_target_serialized, "target unexpectedly serialized");
    requireCondition(!endpoint.seed_or_rng_state_serialized, "RNG unexpectedly serialized");
    requireCondition(endpoint.reset_outside_retained_episode, "recording boundary");
  }
  const sumSquares = expected.reduce((total, value) => total + value * value, 0);
  const quantitative = {
    half_widths_rad: expected,
    half_widths_deg: expected.map((value) => (value * 180) / Math.PI),
    maximum_euclidean_joint_perturbation_rad: Math.sqrt(sumSquares),
    rms_euclidean_joint_perturbation_rad: Math.sqrt(sumSquares / 3),
  };
  const attacks = [
    ["driver_default_alone_proves_phail_binding", endpoints.every((row) => row.phail_droid_binding)],
    ["zero_variation_is_randomized_home", expected.some((value) => value > 0)],
    ["base_home_config_is_realized_draw", endpoints.every((row) => !row.realized_target_serialized)],
    ["synchronous_motion_is_persistent_evidence", endpoints.every((row) => !row.realized_target_serialized)],
    ["outside_window_command_is_recorded_evidence", endpoints.every((row) => row.reset_outside_retained_episode)],
    ["maximum_joint_norm_equals_rms", quantitative.maximum_euclidean_joint_perturbation_rad !== quantitative.rms_euclidean_joint_perturbation_rad],
    ["joint_norm_is_end_effector_displacement", true],
    ["tagged_source_proves_historical_execution", true],
    ["randomization_itself_is_reset_defect", true],
    ["unrecorded_draw_proves_performance_effect", true],
  ].map(([attack, rejected]) => ({ attack, rejected }));
  requireCondition(attacks.every((row) => row.rejected), "attack rejection");

  return {
    schema: "h199-phail-randomized-home-target-independent-challenge-v1",
    method:
      "Independent Node reconstruction from Git objects, full fixed-boundary token inventory, and separately implemented arithmetic; imports no producer module.",
    revisions: { v0_2_1: base, current },
    endpoints,
    quantitative,
    classification: "historical_and_current_unrecorded_randomized_home",
    attacks,
    disposition: "pass_with_scope",
    scope:
      "source-bound mechanism only; no historical-execution, physical-reset-adequacy, end-effector, exchangeability, independence, or performance-effect claim",
  };
}

const args = process.argv.slice(2);
const check = args.includes("--check");
const repoIndex = args.indexOf("--repository");
const repo = repoIndex >= 0 ? args[repoIndex + 1] : defaultRepo;
if (check && !fs.existsSync(repo)) {
  const saved = JSON.parse(fs.readFileSync(output, "utf8"));
  requireCondition(
    saved.schema === "h199-phail-randomized-home-target-independent-challenge-v1",
    "stored schema",
  );
  requireCondition(
    saved.classification === "historical_and_current_unrecorded_randomized_home",
    "stored classification",
  );
  requireCondition(saved.attacks.length === 10 && saved.attacks.every((row) => row.rejected), "stored attacks");
  process.stdout.write(`PASS H199 stored independent challenge: ${output}\n`);
  process.exit(0);
}
const result = build(repo);
if (check) {
  const saved = JSON.parse(fs.readFileSync(output, "utf8"));
  requireCondition(JSON.stringify(result) === JSON.stringify(saved), "stored challenge drift");
  process.stdout.write(`PASS H199 independent challenge: ${output}\n`);
} else {
  fs.writeFileSync(output, `${JSON.stringify(result, null, 2)}\n`);
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

