#!/usr/bin/env node
// Independent direct-Git reconstruction of the H196 endpoint result.

import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const family = dirname(fileURLToPath(import.meta.url));
const root = resolve(family, "../..");
const repository = resolve(root, "work/h196-positronic-history");
const producerPath = resolve(family, "result-h196-positronic-session-identity-history.json");
const protocolPath = resolve(family, "protocol-h196-positronic-session-identity-history.md");
const outputPath = resolve(family, "result-h196-positronic-session-identity-history-independent-challenge.json");

const base = "e406176bc526babb06844a48e3627a5c0409eb74";
const head = "01b78e6f62ff5913490c360afdd2712eee070524";
const paths = [
  "positronic/policy/remote.py",
  "positronic/offboard/client.py",
  "positronic/offboard/vendor_server.py",
  "positronic/data_collection.py",
  "positronic/dataset/episode.py",
  "positronic/dataset/ds_writer_agent.py",
  "positronic/policy/harness.py",
  "positronic/inference.py",
  "positronic/wire.py",
  "positronic/dataset/local_dataset.py",
  "positronic/cfg/policy.py",
  "positronic/policy/base.py",
  "positronic/policy/codec.py",
  "positronic/vendors/lerobot_0_3_3/server.py",
  "positronic/vendors/lerobot/server.py",
  "positronic/vendors/gr00t/server.py",
  "positronic/vendors/openpi/server.py",
  "positronic/policy/recording.py",
  "positronic/offboard/server.py",
];
const backends = {
  ACT: "positronic/vendors/lerobot_0_3_3/server.py",
  SmolVLA: "positronic/vendors/lerobot/server.py",
  GR00T: "positronic/vendors/gr00t/server.py",
  OpenPI: "positronic/vendors/openpi/server.py",
};

function sha256(buffer) {
  return createHash("sha256").update(buffer).digest("hex");
}

function git(args) {
  return execFileSync("git", ["-C", repository, ...args], { encoding: "utf8" });
}

function show(commit, path) {
  return git(["show", `${commit}:${path}`]);
}

function requireThat(condition, message) {
  if (!condition) throw new Error(message);
}

function containsAll(text, fragments, owner) {
  for (const fragment of fragments) {
    requireThat(text.includes(fragment), `${owner}: missing ${fragment}`);
  }
}

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function validateProducer(candidate) {
  requireThat(candidate.schema === "h196-positronic-session-identity-history-v1", "schema");
  requireThat(candidate.classification === "collision_resistant_identifier_recorded", "classification");
  requireThat(candidate.comparison_endpoint_prospective === true, "endpoint status");
  requireThat(candidate.expansion_history_result_exposed === true, "history exposure");
  requireThat(candidate.history.commit_count === 51, "history count");
  requireThat(candidate.history.commits.length === 51, "history rows");
  requireThat(candidate.trace.episode_uid_construction === "uuid.uuid4().hex", "uid construction");
  requireThat(candidate.trace.episode_uid_serialized_to_meta_json === true, "uid persistence");
  requireThat(
    candidate.trace.final_static_rrd_key === "inference.policy.server.recording.rrd",
    "rrd key",
  );
  requireThat(candidate.trace.recording_locator_supplies_episode_to_rrd_join === true, "rrd join");
  requireThat(candidate.trace.episode_uid_embedded_in_server_recording === false, "uid scope");
  requireThat(candidate.trace.physical_reset_or_operator_session_established === false, "cluster overreach");
  requireThat(candidate.server_recording_opened === false, "recording access");
  requireThat(candidate.trace.fixed_phail_backend_results.length === 4, "backend roster");
}

requireThat(git(["rev-parse", base]).trim() === base, "baseline mismatch");
requireThat(git(["rev-parse", head]).trim() === head, "endpoint mismatch");
execFileSync("git", ["-C", repository, "merge-base", "--is-ancestor", base, head]);
requireThat(git(["status", "--porcelain=v1"]).trim() === "", "dirty source checkout");

const recording = show(head, "positronic/policy/recording.py");
const server = show(head, "positronic/offboard/server.py");
const client = show(head, "positronic/offboard/client.py");
const remote = show(head, "positronic/policy/remote.py");
const basePolicy = show(head, "positronic/policy/base.py");
const harness = show(head, "positronic/policy/harness.py");
const writerAgent = show(head, "positronic/dataset/ds_writer_agent.py");
const localDataset = show(head, "positronic/dataset/local_dataset.py");

containsAll(recording, [
  "_EPISODE_COUNTER = itertools.count(1)",
  "self._rrd_path = self._dir / f'{ts}_{episode_num:04d}.rrd'",
  "'recording.rrd': str(self._rec._rrd_path)",
], "recording.py");
containsAll(server, [
  "rec = Recorder(self._recording_dir)",
  "**session.meta",
  "{'status': 'ready', 'meta': meta}",
], "offboard/server.py");
containsAll(client, [
  "self._metadata = self._handshake()",
  "return response['meta']",
], "offboard/client.py");
containsAll(remote, [
  "flatten_dict({'type': 'remote', 'server': self._session.metadata})",
], "policy/remote.py");
containsAll(basePolicy, [
  "{**self._policy_meta, **self._inner.meta, self._key_field: self._key}",
], "policy/base.py");
containsAll(harness, [
  "self._session = self.policy.new_session(self.context, clock.now)",
  "session_meta = self.policy.meta | (self._session.meta if self._session else {})",
  "meta[f'inference.policy.{k}'] = v",
  "DsWriterCommand.STOP({**self._build_episode_meta(self.context), **(payload or {})})",
], "policy/harness.py");
containsAll(writerAgent, [
  "ep_writer = self.ds_writer.new_episode()",
  "ep_writer.set_static(k, v)",
  "ep_writer.__exit__(None, None, None)",
], "dataset/ds_writer_agent.py");
containsAll(localDataset, [
  "'uid': uid or uuid.uuid4().hex",
  "self._path / 'static.json'",
  "self._path / 'meta.json'",
  "json.dump(self._meta, f, indent=2)",
], "dataset/local_dataset.py");

const backendResults = Object.entries(backends).map(([policy, path]) => {
  const text = show(head, path);
  const block = text.match(/'phail':\s*serve\.override\(([\s\S]*?)\n\s*\),/);
  requireThat(block, `${path}: phail block`);
  const recordingDir = block[1].match(/recording_dir\s*=\s*'([^']+)'/);
  requireThat(recordingDir, `${path}: recording dir`);
  return { policy, path, recording_dir: recordingDir[1] };
});

const historyCommits = git(["log", "--reverse", "--format=%H", `${base}..${head}`, "--", ...paths])
  .trim()
  .split("\n")
  .filter(Boolean);
requireThat(new Set(historyCommits).size === 51, "independent history count");
requireThat(historyCommits.includes("e370cbf1e6e31360fd17cc6d36a9ce74786abd94"), "uid commit absent");
requireThat(historyCommits.includes("91287959a41ee7ebb4b12212dd4dbe99c36efb99"), "rrd meta commit absent");

const uidIntroduction = git([
  "log", "--reverse", "--format=%H", "-S", "uuid.uuid4().hex",
  `${base}..${head}`, "--", "positronic/dataset/local_dataset.py",
]).trim().split("\n").filter(Boolean);
const rrdIntroduction = git([
  "log", "--reverse", "--format=%H", "-S", "recording.rrd",
  `${base}..${head}`, "--", "positronic/policy/recording.py",
]).trim().split("\n").filter(Boolean);
requireThat(uidIntroduction[0] === "e370cbf1e6e31360fd17cc6d36a9ce74786abd94", "uid introduction");
requireThat(rrdIntroduction[0] === "91287959a41ee7ebb4b12212dd4dbe99c36efb99", "rrd introduction");

const baselineCodec = show(base, "positronic/policy/codec.py");
const baselineDataset = show(base, "positronic/dataset/local_dataset.py");
requireThat(!baselineCodec.includes("'recording.rrd'"), "baseline unexpectedly exposes rrd");
requireThat(!baselineDataset.includes("uuid.uuid4().hex"), "baseline unexpectedly stamps uuid");

const producerBytes = readFileSync(producerPath);
const producer = JSON.parse(producerBytes);
validateProducer(producer);

const attacks = [
  ["wrong classification", c => { c.classification = "locator_still_unjoined"; }],
  ["endpoint relabeled exposed", c => { c.comparison_endpoint_prospective = false; }],
  ["history exposure hidden", c => { c.expansion_history_result_exposed = false; }],
  ["history row omitted", c => { c.history.commits.pop(); }],
  ["uuid weakened", c => { c.trace.episode_uid_construction = "timestamp"; }],
  ["rrd key altered", c => { c.trace.final_static_rrd_key = "recording.rrd"; }],
  ["rrd join removed", c => { c.trace.recording_locator_supplies_episode_to_rrd_join = false; }],
  ["uid promoted into rrd", c => { c.trace.episode_uid_embedded_in_server_recording = true; }],
  ["cluster promoted", c => { c.trace.physical_reset_or_operator_session_established = true; }],
  ["recording access hidden", c => { c.server_recording_opened = true; }],
];
const attackResults = attacks.map(([name, mutate]) => {
  const candidate = clone(producer);
  mutate(candidate);
  let rejected = false;
  try {
    validateProducer(candidate);
  } catch {
    rejected = true;
  }
  requireThat(rejected, `attack passed: ${name}`);
  return { name, rejected };
});

const sourceHashes = {};
for (const path of [
  "positronic/policy/recording.py",
  "positronic/offboard/server.py",
  "positronic/offboard/client.py",
  "positronic/policy/remote.py",
  "positronic/policy/harness.py",
  "positronic/dataset/ds_writer_agent.py",
  "positronic/dataset/local_dataset.py",
]) {
  sourceHashes[path] = sha256(Buffer.from(show(head, path)));
}

const result = {
  schema: "h196-positronic-session-identity-history-independent-challenge-v1",
  producer_modules_imported: false,
  method: "independent Node direct-Git endpoint trace and fixed-path history reconstruction",
  protocol_sha256: sha256(readFileSync(protocolPath)),
  producer_result_sha256: sha256(producerBytes),
  baseline_commit: base,
  comparison_commit: head,
  independently_reconstructed_history_commit_count: historyCommits.length,
  independently_reconstructed_uid_introduction: uidIntroduction[0],
  independently_reconstructed_rrd_meta_introduction: rrdIntroduction[0],
  independently_reconstructed_backend_results: backendResults,
  independently_reconstructed_final_static_rrd_key: "inference.policy.server.recording.rrd",
  independently_reconstructed_episode_uid: "uuid.uuid4().hex in finalized episode meta.json",
  episode_uid_is_shared_server_session_id: false,
  rrd_path_is_episode_to_server_recording_join: true,
  rrd_filename_globally_unique_across_restarts: false,
  physical_reset_or_operator_session_established: false,
  source_hashes: sourceHashes,
  semantic_attacks: attackResults,
  semantic_attacks_rejected: attackResults.length,
  performance_or_dataset_content_opened: false,
  server_recording_opened: false,
  agrees_with_producer_with_scope_narrowing: true,
  disposition: "pass_with_scope_narrowing",
};

const rendered = `${JSON.stringify(result, null, 2)}\n`;
if (process.argv.includes("--check")) {
  requireThat(readFileSync(outputPath, "utf8") === rendered, "stored challenge differs from exact rebuild");
  console.log(`PASS H196 independent challenge: ${outputPath}`);
} else {
  writeFileSync(outputPath, rendered);
  console.log(`WROTE ${outputPath}`);
}
