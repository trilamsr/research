#!/usr/bin/env node
// Independent direct-CSV PAV and Murphy reconstruction.

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const input = path.join(here, "..", "corpus-reporting-audit", "sources", "source-wm-policyeval.csv");
const protocol = path.join(here, "protocol-wm-nonlinear-calibration-sensitivity.md");
const producer = path.join(here, "audit_wm_nonlinear_calibration_sensitivity.py");
const producerResult = path.join(here, "result-wm-nonlinear-calibration-sensitivity.json");
const output = path.join(here, "result-wm-nonlinear-calibration-sensitivity-independent-challenge.json");
const tolerance = 1e-10;

function sha256(filename) {
  return crypto.createHash("sha256").update(fs.readFileSync(filename)).digest("hex");
}

function mean(values) {
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function argmax(object) {
  return Object.entries(object).reduce(
    (best, row) => (row[1] > best[1] ? row : best),
  )[0];
}

function parsePanels() {
  const lines = fs.readFileSync(input, "utf8").split(/\r?\n/).filter(
    (line) => line.trim() && !line.startsWith("#"),
  );
  const header = lines[0].split(",");
  const rows = lines.slice(1).map((line) => {
    const values = line.split(",");
    const record = Object.fromEntries(header.map((name, index) => [name, values[index]]));
    return {
      model: record.world_model,
      policy: record.policy,
      task: record.task,
      predicted: Number(record.predicted_success_rate),
      real: Number(record.actual_success_rate),
    };
  });
  return Object.fromEntries(
    ["Cosmos", "IRASim"].map((model) => [model, rows.filter((row) => row.model === model)]),
  );
}

function levelMap(rows) {
  const grouped = new Map();
  for (const row of rows) {
    if (!grouped.has(row.predicted)) grouped.set(row.predicted, []);
    grouped.get(row.predicted).push(row.real);
  }
  const blocks = [...grouped.entries()]
    .sort((left, right) => left[0] - right[0])
    .map(([level, values]) => ({
      levels: [level],
      weight: values.length,
      sum: values.reduce((total, value) => total + value, 0),
    }));
  let index = 0;
  while (index < blocks.length - 1) {
    const left = blocks[index].sum / blocks[index].weight;
    const right = blocks[index + 1].sum / blocks[index + 1].weight;
    if (left <= right + 1e-15) {
      index += 1;
      continue;
    }
    blocks.splice(index, 2, {
      levels: [...blocks[index].levels, ...blocks[index + 1].levels],
      weight: blocks[index].weight + blocks[index + 1].weight,
      sum: blocks[index].sum + blocks[index + 1].sum,
    });
    index = Math.max(0, index - 1);
  }
  return blocks.flatMap((block, blockIndex) =>
    block.levels.map((level) => ({
      predicted_level: level,
      isotonic_fitted_rate: block.sum / block.weight,
      block_index: blockIndex,
    })),
  ).sort((left, right) => left.predicted_level - right.predicted_level);
}

function murphy(rows) {
  const prevalence = mean(rows.map((row) => row.real));
  const grouped = new Map();
  for (const row of rows) {
    if (!grouped.has(row.predicted)) grouped.set(row.predicted, []);
    grouped.get(row.predicted).push(row.real);
  }
  let reliability = 0;
  let resolution = 0;
  for (const [predicted, values] of grouped.entries()) {
    const weight = values.length / rows.length;
    const observed = mean(values);
    reliability += weight * (predicted - observed) ** 2;
    resolution += weight * (observed - prevalence) ** 2;
  }
  const uncertainty = prevalence * (1 - prevalence);
  const brier = mean(
    rows.map((row) => row.predicted ** 2 - 2 * row.predicted * row.real + row.real),
  );
  if (Math.abs(brier - reliability + resolution - uncertainty) > 1e-12) {
    throw new Error("Murphy identity failed");
  }
  return {
    reliability,
    resolution,
    uncertainty,
    brier,
    brier_skill_vs_empirical_prevalence: 1 - brier / uncertainty,
  };
}

function panel(rows) {
  const mapping = levelMap(rows);
  const byLevel = new Map(
    mapping.map((row) => [row.predicted_level, row.isotonic_fitted_rate]),
  );
  const policies = [...new Set(rows.map((row) => row.policy))].sort();
  const rawMeans = Object.fromEntries(
    policies.map((policy) => [
      policy,
      mean(rows.filter((row) => row.policy === policy).map((row) => row.predicted)),
    ]),
  );
  const fittedMeans = Object.fromEntries(
    policies.map((policy) => [
      policy,
      mean(rows.filter((row) => row.policy === policy).map((row) => byLevel.get(row.predicted))),
    ]),
  );
  return {
    isotonic_level_map: mapping,
    raw_policy_means: rawMeans,
    isotonic_policy_means: fittedMeans,
    original_winner: argmax(rawMeans),
    isotonic_winner: argmax(fittedMeans),
    winner_changed: argmax(rawMeans) !== argmax(fittedMeans),
    raw_cell_rate_mse: mean(rows.map((row) => (row.predicted - row.real) ** 2)),
    isotonic_in_sample_cell_rate_mse: mean(
      rows.map((row) => (byLevel.get(row.predicted) - row.real) ** 2),
    ),
    murphy_forecast_level_decomposition: murphy(rows),
  };
}

function compare(actual, expected, label, counter) {
  if (typeof actual === "number") {
    if (Math.abs(actual - expected) > tolerance) {
      throw new Error(`${label}: ${actual} vs ${expected}`);
    }
    counter.count += 1;
    return;
  }
  if (Array.isArray(actual)) {
    if (actual.length !== expected.length) throw new Error(`${label}: length`);
    actual.forEach((value, index) => compare(value, expected[index], `${label}/${index}`, counter));
    return;
  }
  if (actual && typeof actual === "object") {
    if (JSON.stringify(Object.keys(actual).sort()) !== JSON.stringify(Object.keys(expected).sort())) {
      throw new Error(`${label}: keys`);
    }
    for (const [key, value] of Object.entries(actual)) {
      compare(value, expected[key], `${label}/${key}`, counter);
    }
    return;
  }
  if (actual !== expected) throw new Error(`${label}: ${actual} vs ${expected}`);
}

function build() {
  const panels = parsePanels();
  const expected = JSON.parse(fs.readFileSync(producerResult, "utf8"));
  const results = {};
  const counter = { count: 0 };
  for (const [model, rows] of Object.entries(panels)) {
    const current = panel(rows);
    compare(current, expected.panels[model], model, counter);
    results[model] = current;
  }
  if (results.Cosmos.winner_changed || !results.IRASim.winner_changed) {
    throw new Error("winner-change pattern differs");
  }
  return {
    schema: "wm-nonlinear-calibration-sensitivity-independent-challenge-v1",
    status: "pass",
    method: "Node direct CSV grouping, pooled-adjacent-violators, and forecast-level Murphy decomposition; no Python import or execution",
    tolerance,
    numeric_comparisons: counter.count,
    panels: results,
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
    throw new Error("stored nonlinear calibration challenge differs");
  }
  process.stdout.write("OK: WM nonlinear calibration independent challenge\n");
}
