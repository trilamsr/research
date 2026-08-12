#!/usr/bin/env node
// Method-distinct challenge for heterogeneous WM simulator evidence.

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const input = path.join(here, "..", "corpus-reporting-audit", "sources", "source-wm-policyeval.csv");
const protocol = path.join(here, "protocol-wm-heterogeneous-simulator-evidence-sensitivity.md");
const producer = path.join(here, "analyze_wm_heterogeneous_simulator_evidence.py");
const producerResult = path.join(here, "result-wm-heterogeneous-simulator-evidence-sensitivity.json");
const output = path.join(here, "result-wm-heterogeneous-simulator-evidence-independent-challenge.json");
const draws = 150_000;

function sha256(filename) {
  return crypto.createHash("sha256").update(fs.readFileSync(filename)).digest("hex");
}

function mulberry32(seed) {
  let state = seed >>> 0;
  return () => {
    state = (state + 0x6d2b79f5) >>> 0;
    let value = state;
    value = Math.imul(value ^ (value >>> 15), value | 1);
    value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
    return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
  };
}

function normal(rng) {
  const u1 = Math.max(rng(), Number.MIN_VALUE);
  const u2 = rng();
  return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
}

function gamma(shape, rng) {
  if (!(shape > 0)) throw new Error("invalid gamma shape");
  if (shape < 1) {
    return gamma(shape + 1, rng) * Math.pow(Math.max(rng(), Number.MIN_VALUE), 1 / shape);
  }
  const d = shape - 1 / 3;
  const c = 1 / Math.sqrt(9 * d);
  while (true) {
    const x = normal(rng);
    const v0 = 1 + c * x;
    if (v0 <= 0) continue;
    const v = v0 ** 3;
    const u = rng();
    if (u < 1 - 0.0331 * x ** 4) return d * v;
    if (Math.log(u) < 0.5 * x * x + d * (1 - v + Math.log(v))) return d * v;
  }
}

function beta(alpha, betaShape, rng) {
  const x = gamma(alpha, rng);
  const y = gamma(betaShape, rng);
  return x / (x + y);
}

function parseIRASim() {
  const lines = fs.readFileSync(input, "utf8").split(/\r?\n/).filter(
    (line) => line.trim() && !line.startsWith("#"),
  );
  const header = lines[0].split(",");
  const records = lines.slice(1).map((line) => {
    const fields = line.split(",");
    return Object.fromEntries(header.map((name, index) => [name, fields[index]]));
  }).filter((row) => row.world_model === "IRASim");
  const candidates = [...new Set(records.map((row) => row.policy))].sort();
  const tasks = [...new Set(records.map((row) => row.task))].sort();
  const byKey = new Map(records.map((row) => [`${row.policy}\0${row.task}`, row]));
  return {
    candidates,
    realSuccesses: candidates.map((candidate) =>
      tasks.map((task) => 20 * Number(byKey.get(`${candidate}\0${task}`).actual_success_rate)),
    ),
    simRates: candidates.map((candidate) =>
      tasks.map((task) => Number(byKey.get(`${candidate}\0${task}`).predicted_success_rate)),
    ),
  };
}

function argmax(values) {
  let best = 0;
  for (let index = 1; index < values.length; index += 1) {
    if (values[index] > values[best]) best = index;
  }
  return best;
}

function evaluate(panel, evidence, seed) {
  const rng = mulberry32(seed);
  let matches = 0;
  for (let draw = 0; draw < draws; draw += 1) {
    const realMeans = panel.realSuccesses.map((row) =>
      row.reduce(
        (sum, successes) => sum + beta(successes + 1, 21 - successes, rng),
        0,
      ) / row.length,
    );
    const simMeans = panel.simRates.map((row, policy) =>
      row.reduce(
        (sum, rate) =>
          sum + beta(1 + evidence[policy] * rate, 1 + evidence[policy] * (1 - rate), rng),
        0,
      ) / row.length,
    );
    if (argmax(realMeans) === argmax(simMeans)) matches += 1;
  }
  const probability = matches / draws;
  return {
    evidence,
    latent_winner_concordance: probability,
    monte_carlo_se: Math.sqrt(probability * (1 - probability) / draws),
  };
}

function build() {
  const panel = parseIRASim();
  if (JSON.stringify(panel.candidates) !== JSON.stringify(["Octo-Base", "Octo-Small", "OpenVLA"])) {
    throw new Error("candidate order changed");
  }
  const expected = JSON.parse(fs.readFileSync(producerResult, "utf8"));
  const specifications = [
    ["common_10", [10, 10, 10], false],
    ["openvla_10", [500, 500, 10], true],
    ["openvla_0", [500, 500, 0], true],
  ];
  const scenarios = specifications.map(([name, evidence, above], index) => {
    const row = evaluate(panel, evidence, 41_238_000 + index);
    const producerValue = expected.panels.IRASim.scenarios[name].latent_winner_concordance;
    row.name = name;
    row.producer_probability = producerValue;
    row.absolute_difference = Math.abs(row.latent_winner_concordance - producerValue);
    if (row.absolute_difference > 0.015) throw new Error(`${name}: producer disagreement`);
    if ((row.latent_winner_concordance > 0.5) !== above) {
      throw new Error(`${name}: half-boundary direction changed`);
    }
    return row;
  });
  return {
    schema: "wm-heterogeneous-simulator-evidence-independent-challenge-v1",
    status: "pass",
    method: "Node custom PRNG and Marsaglia-Tsang Gamma/Beta sampler; direct retained-CSV parse; no Python import or execution",
    draws_per_scenario: draws,
    prior_alpha_beta: 1,
    tolerance: 0.015,
    scenarios,
    protocol_sha256: sha256(protocol),
    producer_sha256: sha256(producer),
    producer_result_sha256: sha256(producerResult),
    input_sha256: sha256(input),
    runtime: { node: process.version, platform: process.platform, architecture: process.arch },
  };
}

const args = new Set(process.argv.slice(2));
if ((args.has("--write") ? 1 : 0) + (args.has("--check") ? 1 : 0) !== 1) {
  throw new Error("choose exactly one of --write or --check");
}
const result = build();
const serialized = `${JSON.stringify(result, null, 2)}\n`;
if (args.has("--write")) {
  fs.writeFileSync(output, serialized);
  process.stdout.write(`WROTE ${output}\n`);
} else {
  if (fs.readFileSync(output, "utf8") !== serialized) {
    throw new Error("stored heterogeneous-evidence challenge differs");
  }
  process.stdout.write("OK: WM heterogeneous-evidence independent challenge\n");
}
