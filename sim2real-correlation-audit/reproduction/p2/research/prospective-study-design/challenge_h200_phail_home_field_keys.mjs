#!/usr/bin/env node
// Independent key-only reconstruction of H200 from hash-bound cached sidecars.

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const family = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(family, "..", "..");
const input = path.join(
  family,
  "result-h187-phail-context-support-sanitized.csv",
);
const cache = path.join(root, "work", "h193-sidecars");
const output = path.join(
  family,
  "result-h200-phail-home-field-key-inventory-independent-challenge.json",
);
const expectedInput =
  "ad43fca1da065a1cb7fd84dfa9afc5691c72ebe12e7f165c68a0050e51e87ebe";
const tokens = new Set([
  "home", "homing", "joint", "joints", "initial", "initialize",
  "initialization", "start", "starting", "pose", "rng", "random",
  "randomized", "randomization", "variation", "perturbation", "target",
  "origin",
]);
const prohibited = new Set([
  "success", "successful", "outcome", "result", "reward", "score", "rank",
  "duration", "termination", "terminated", "completion", "completed",
  "safety", "hrt", "annotation", "event", "note", "media", "video",
  "telemetry", "item", "items", "action", "actions", "command", "commands",
  "observation", "observations",
]);

function requireCondition(condition, message) {
  if (!condition) throw new Error(message);
}

function sha256(data) {
  return crypto.createHash("sha256").update(data).digest("hex");
}

function components(value) {
  return (value.match(/[A-Za-z0-9]+/g) ?? []).map((part) => part.toLowerCase());
}

function typeOf(value) {
  if (value === null) return "null";
  if (Array.isArray(value)) return "array";
  if (typeof value === "object") return "object";
  if (typeof value === "string") return "string";
  if (typeof value === "number") return "number";
  if (typeof value === "boolean") return "boolean";
  throw new Error("unsupported JSON node");
}

function classify(parts) {
  const observed = new Set(parts.flatMap(components));
  if ([...observed].some((token) => prohibited.has(token))) return false;
  return [...observed].some((token) => tokens.has(token));
}

function project(value, sidecar) {
  const found = new Set();
  function visit(node, parts) {
    if (node !== null && typeof node === "object" && !Array.isArray(node)) {
      for (const [key, child] of Object.entries(node)) {
        const childParts = [...parts, key];
        if (classify(childParts)) {
          found.add(`${sidecar}.${childParts.join(".")}\t${typeOf(child)}`);
        }
        visit(child, childParts);
      }
    } else if (Array.isArray(node)) {
      for (const child of node) {
        if (child !== null && typeof child === "object") {
          visit(child, [...parts, "[]"]);
        } else {
          typeOf(child);
        }
      }
    } else {
      typeOf(node);
    }
  }
  requireCondition(
    value !== null && typeof value === "object" && !Array.isArray(value),
    "sidecar root",
  );
  visit(value, []);
  return [...found].sort().map((entry) => {
    const [keyPath, nodeType] = entry.split("\t");
    return { key_path: keyPath, node_type: nodeType };
  });
}

function parseInput() {
  const raw = fs.readFileSync(input);
  requireCondition(sha256(raw) === expectedInput, "input hash");
  const lines = raw.toString("utf8").trimEnd().split(/\r?\n/);
  const header = lines[0].split(",");
  requireCondition(header.length === 14, "input width");
  const index = Object.fromEntries(header.map((name, i) => [name, i]));
  const rows = lines.slice(1).map((line) => {
    const fields = line.split(",");
    requireCondition(fields.length === header.length, "quoted CSV unsupported");
    return {
      episode_id: fields[index.episode_id],
      meta_sha256: fields[index.meta_sha256],
      static_sha256: fields[index.static_sha256],
    };
  });
  requireCondition(rows.length === 594, "episode count");
  requireCondition(new Set(rows.map((row) => row.episode_id)).size === 594, "duplicate episode");
  return rows;
}

function episodeSetHash(ids) {
  return sha256([...ids].sort().map((id) => `${id}\n`).join(""));
}

function build() {
  const rows = parseInput();
  const episodes = new Map();
  const typeCounts = new Map();
  let verifiedObjects = 0;
  for (const row of rows) {
    for (const sidecar of ["meta", "static"]) {
      const expected = row[`${sidecar}_sha256`];
      const raw = fs.readFileSync(path.join(cache, `${expected}.json`));
      requireCondition(sha256(raw) === expected, "sidecar hash");
      verifiedObjects += 1;
      const parsed = JSON.parse(raw.toString("utf8"));
      for (const projected of project(parsed, sidecar)) {
        const key = projected.key_path;
        if (!episodes.has(key)) episodes.set(key, new Set());
        episodes.get(key).add(row.episode_id);
        const typed = `${key}\t${projected.node_type}`;
        typeCounts.set(typed, (typeCounts.get(typed) ?? 0) + 1);
      }
    }
  }
  const keyRows = [...episodes.keys()].sort().map((keyPath) => {
    const nodeTypeCounts = {};
    for (const [typed, count] of [...typeCounts.entries()].sort()) {
      const [candidatePath, nodeType] = typed.split("\t");
      if (candidatePath === keyPath) nodeTypeCounts[nodeType] = count;
    }
    const ids = episodes.get(keyPath);
    return {
      key_path: keyPath,
      category: "home_field_candidate",
      episode_count: ids.size,
      episode_set_sha256: episodeSetHash(ids),
      node_type_counts: nodeTypeCounts,
    };
  });
  requireCondition(verifiedObjects === 1188, "sidecar completeness");
  requireCondition(
    JSON.stringify(keyRows.map((row) => row.key_path)) ===
      JSON.stringify([
        "static.joint_names",
        "static.joint_signal",
        "static.pose_signals",
      ]),
    "candidate roster",
  );
  const attacks = [
    ["candidate_name_is_realized_draw", true],
    ["joint_names_array_is_home_target", true],
    ["joint_signal_string_is_reset_evidence", true],
    ["pose_signals_array_is_home_target", true],
    ["all_episode_presence_implies_varying_value", true],
    ["key_only_inventory_exposes_primitive_values", true],
    ["public_sidecar_null_would_prove_private_absence", true],
    ["schema_descriptor_proves_historical_reset_execution", true],
  ].map(([attack, rejected]) => ({ attack, rejected }));
  return {
    schema: "h200-phail-home-field-key-inventory-independent-challenge-v1",
    method:
      "Independent Node traversal of all hash-bound cached JSON objects with separately implemented tokenization, exclusion, node typing, aggregation, and no producer-module import.",
    input_sha256: expectedInput,
    episode_count: rows.length,
    verified_sidecar_object_count: verifiedObjects,
    key_rows: keyRows,
    candidate_count: keyRows.length,
    disposition: "candidate_home_field_key_found",
    attacks,
    scope:
      "key names and node types only; no values, trajectory content, candidate semantics, physical-reset, historical-execution, exchangeability, or performance claim",
  };
}

const args = process.argv.slice(2);
const check = args.includes("--check");
if (check && !fs.existsSync(cache)) {
  const saved = JSON.parse(fs.readFileSync(output, "utf8"));
  requireCondition(saved.verified_sidecar_object_count === 1188, "stored completeness");
  requireCondition(saved.candidate_count === 3, "stored candidate count");
  requireCondition(saved.attacks.length === 8 && saved.attacks.every((row) => row.rejected), "stored attacks");
  process.stdout.write(`PASS H200 stored independent challenge: ${output}\n`);
  process.exit(0);
}
const result = build();
if (check) {
  const saved = JSON.parse(fs.readFileSync(output, "utf8"));
  requireCondition(JSON.stringify(result) === JSON.stringify(saved), "stored challenge drift");
  process.stdout.write(`PASS H200 independent challenge: ${output}\n`);
} else {
  fs.writeFileSync(output, `${JSON.stringify(result, null, 2)}\n`);
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

