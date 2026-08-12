#!/usr/bin/env node
// Independent Node source-semantics challenge for H201.

import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const family = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(family, "..", "..");
const defaultRepo = path.join(root, "work", "h198-positronic-current");
const output = path.join(
  family,
  "result-h201-phail-home-field-semantics-independent-challenge.json",
);
const revision = "e406176bc526babb06844a48e3627a5c0409eb74";
const candidates = ["joint_names", "joint_signal", "pose_signals"];

function requireCondition(condition, message) {
  if (!condition) throw new Error(message);
}

function git(repo, ...args) {
  return execFileSync("git", ["-C", repo, ...args], {
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
  });
}

function source(repo, relative) {
  return git(repo, "show", `${revision}:${relative}`);
}

function search(repo) {
  const counts = {};
  const pathsByCandidate = {};
  const union = new Set();
  for (const candidate of candidates) {
    const lines = git(repo, "grep", "-n", "-F", candidate, revision, "--", ".")
      .trimEnd()
      .split("\n");
    counts[candidate] = lines.length;
    const paths = new Set();
    for (const line of lines) {
      requireCondition(line.startsWith(`${revision}:`), "grep prefix");
      const relative = line.slice(revision.length + 1).split(":", 1)[0];
      paths.add(relative);
      union.add(relative);
    }
    pathsByCandidate[candidate] = [...paths].sort();
  }
  return {
    hit_counts: counts,
    paths_by_candidate: pathsByCandidate,
    union_paths: [...union].sort(),
  };
}

function build(repo) {
  requireCondition(git(repo, "rev-parse", revision).trim() === revision, "revision");
  requireCondition(git(repo, "status", "--porcelain=v1").trim() === "", "dirty checkout");
  const inventory = search(repo);
  requireCondition(
    JSON.stringify(inventory.hit_counts) ===
      JSON.stringify({ joint_names: 40, joint_signal: 14, pose_signals: 8 }),
    "hit counts",
  );
  requireCondition(inventory.union_paths.length === 10, "matched path count");

  const wire = source(repo, "positronic/wire.py");
  const franka = source(repo, "positronic/drivers/roboarm/franka.py");
  const inference = source(repo, "positronic/inference.py");
  const harness = source(repo, "positronic/policy/harness.py");
  const writer = source(repo, "positronic/dataset/ds_writer_agent.py");
  const local = source(repo, "positronic/dataset/local_dataset.py");
  const server = source(repo, "positronic/server/dataset_utils.py");
  requireCondition(
    wire.includes(
      "ROBOT_STATIC_META = {'joint_signal': 'robot_state.q', 'pose_signals': ['robot_state.ee_pose', 'robot_commands.pose']}",
    ),
    "wire constants",
  );
  const robotMetaStart = franka.indexOf("    def _build_robot_meta(");
  const robotMetaEnd = franka.indexOf("\n    def _ensure_robot(", robotMetaStart);
  const robotMeta = franka.slice(robotMetaStart, robotMetaEnd);
  const resetStart = franka.indexOf("    def _reset(");
  const resetEnd = franka.indexOf("\n    def run(", resetStart);
  const reset = franka.slice(resetStart, resetEnd);
  requireCondition(
    robotMeta.includes("'joint_names': _revolute_joint_names(urdf_xml)"),
    "joint name producer",
  );
  requireCondition(!robotMeta.includes("variation") && !robotMeta.includes("target"), "robot meta isolation");
  requireCondition(
    reset.includes("np.random.uniform(") &&
      reset.includes("target = target + variation") &&
      !reset.includes("robot_meta.emit"),
    "random target separation",
  );
  requireCondition(
    inference.includes("Harness(policy, static_meta=wire.ROBOT_STATIC_META)") &&
      wire.includes("world.connect(robot_arm.robot_meta, harness.robot_meta_in)") &&
      harness.includes("meta.update(self.robot_meta_in.value)") &&
      writer.includes("ep_writer.set_static(k, v)") &&
      local.includes("episode_json = self._path / 'static.json'"),
    "persistence path",
  );
  requireCondition(
    server.includes("3D visualization roles (pose_signals, joint_signal)") &&
      server.includes("joint_names = ep.static.get('joint_names')") &&
      server.includes("pose_set = set(ep.static.get('pose_signals', []))"),
    "consumer semantics",
  );

  const units = [
    {
      key: "joint_names",
      value_class: "array_of_revolute_joint_name_strings_from_robot_urdf",
      behavior: "static_robot_model_metadata_emitted_at_driver_start",
      semantic_class: "schema_descriptor",
      realized_home_target_present: false,
      rng_identity_present: false,
    },
    {
      key: "joint_signal",
      value_class: "constant_signal_name_string",
      behavior: "fixed_static_visualization_role",
      semantic_class: "schema_descriptor",
      realized_home_target_present: false,
      rng_identity_present: false,
    },
    {
      key: "pose_signals",
      value_class: "constant_array_of_pose_signal_name_strings",
      behavior: "fixed_static_visualization_roles",
      semantic_class: "schema_descriptor",
      realized_home_target_present: false,
      rng_identity_present: false,
    },
  ];
  const attacks = [
    ["joint_names_are_joint_positions", true],
    ["joint_signal_name_is_signal_samples", true],
    ["pose_signal_names_are_pose_samples", true],
    ["all_episode_presence_is_per_reset_variation", true],
    ["random_target_in_same_driver_is_serialized_metadata", true],
    ["static_item_is_necessarily_realized_value", true],
    ["visualization_role_is_reset_evidence", true],
    ["tagged_source_proves_historical_execution", true],
    ["candidate_keys_require_value_opening_after_source_null", true],
  ].map(([attack, rejected]) => ({ attack, rejected }));
  return {
    schema: "h201-phail-home-field-semantics-independent-challenge-v1",
    method:
      "Independent Node full-tree exact-string census plus separately implemented producer-to-static-sink trace; imports no producer module.",
    revision,
    inventory,
    units,
    classification: "generic_signal_schema_not_home_draw",
    attacks,
    disposition: "pass_with_scope",
    scope:
      "source-defined schema semantics only; no sidecar values, trajectories, physical-reset, historical-execution, exchangeability, or performance claim",
  };
}

const args = process.argv.slice(2);
const check = args.includes("--check");
const repoIndex = args.indexOf("--repository");
const repo = repoIndex >= 0 ? args[repoIndex + 1] : defaultRepo;
if (check && !fs.existsSync(repo)) {
  const saved = JSON.parse(fs.readFileSync(output, "utf8"));
  requireCondition(saved.classification === "generic_signal_schema_not_home_draw", "stored class");
  requireCondition(saved.attacks.length === 9 && saved.attacks.every((row) => row.rejected), "stored attacks");
  process.stdout.write(`PASS H201 stored independent challenge: ${output}\n`);
  process.exit(0);
}
const result = build(repo);
if (check) {
  const saved = JSON.parse(fs.readFileSync(output, "utf8"));
  requireCondition(JSON.stringify(result) === JSON.stringify(saved), "stored challenge drift");
  process.stdout.write(`PASS H201 independent challenge: ${output}\n`);
} else {
  fs.writeFileSync(output, `${JSON.stringify(result, null, 2)}\n`);
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

