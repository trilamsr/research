#!/usr/bin/env node
// Method-distinct Monte Carlo challenge for WM missing simulator evidence.

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const input = path.join(here, "..", "corpus-reporting-audit", "sources", "source-wm-policyeval.csv");
const protocol = path.join(here, "protocol-wm-missing-simulator-evidence-sensitivity.md");
const producer = path.join(here, "analyze_wm_missing_simulator_uncertainty.py");
const producerResult = path.join(here, "result-wm-missing-simulator-evidence-sensitivity.json");
const output = path.join(here, "result-wm-missing-simulator-evidence-sensitivity-independent-challenge.json");
const draws = 120_000;

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

function parsePanels() {
  const lines = fs.readFileSync(input, "utf8").split(/\r?\n/).filter(
    (line) => line.trim() && !line.startsWith("#"),
  );
  const header = lines[0].split(",");
  const records = lines.slice(1).map((line) => {
    const fields = line.split(",");
    return Object.fromEntries(header.map((name, index) => [name, fields[index]]));
  });
  const panels = {};
  for (const model of ["Cosmos", "IRASim"]) {
    const rows = records.filter((row) => row.world_model === model);
    const candidates = [...new Set(rows.map((row) => row.policy))].sort();
    const tasks = [...new Set(rows.map((row) => row.task))].sort();
    const byKey = new Map(rows.map((row) => [`${row.policy}\0${row.task}`, row]));
    const realSuccesses = candidates.map((candidate) =>
      tasks.map((task) => 20 * Number(byKey.get(`${candidate}\0${task}`).actual_success_rate)),
    );
    const simRates = candidates.map((candidate) =>
      tasks.map((task) => Number(byKey.get(`${candidate}\0${task}`).predicted_success_rate)),
    );
    panels[model] = { candidates, tasks, realSuccesses, simRates };
  }
  return panels;
}

function argmax(values) {
  let best = 0;
  for (let index = 1; index < values.length; index += 1) {
    if (values[index] > values[best]) best = index;
  }
  return best;
}

function means(matrix) {
  return matrix.map((row) => row.reduce((sum, value) => sum + value, 0) / row.length);
}

function evaluate(panel, evidence, seed) {
  const rng = mulberry32(seed);
  let matches = 0;
  const fixedSimBest = argmax(means(panel.simRates));
  for (let draw = 0; draw < draws; draw += 1) {
    const realMeans = panel.realSuccesses.map((row) =>
      row.reduce(
        (sum, successes) => sum + beta(successes + 1, 20 - successes + 1, rng),
        0,
      ) / row.length,
    );
    let simBest = fixedSimBest;
    if (evidence !== "infinity_fixed_display") {
      const simMeans = panel.simRates.map((row) =>
        row.reduce(
          (sum, rate) => sum + beta(evidence * rate + 1, evidence * (1 - rate) + 1, rng),
          0,
        ) / row.length,
      );
      simBest = argmax(simMeans);
    }
    if (simBest === argmax(realMeans)) matches += 1;
  }
  const probability = matches / draws;
  return {
    evidence: evidence === "infinity_fixed_display" ? evidence : String(evidence),
    probability_sampled_winners_match: probability,
    monte_carlo_se: Math.sqrt(probability * (1 - probability) / draws),
  };
}

function producerProbability(result, model, evidence) {
  const label = evidence === "infinity_fixed_display" ? evidence : String(evidence);
  const row = result.panels[model].scenarios.find(
    (candidate) =>
      candidate.prior_alpha_beta === 1 &&
      candidate.sim_effective_bernoulli_equivalents_per_policy_task === label,
  );
  if (!row) throw new Error(`missing producer scenario ${model}/${label}`);
  return row.probability_sampled_sim_winner_is_sampled_real_best;
}

function build() {
  const panels = parsePanels();
  const producerData = JSON.parse(fs.readFileSync(producerResult, "utf8"));
  const results = {};
  let comparisons = 0;
  let analyticChecks = 0;
  for (const [modelIndex, model] of ["Cosmos", "IRASim"].entries()) {
    const panel = panels[model];
    const displayedReal = panel.candidates[argmax(means(panel.realSuccesses))];
    const displayedSim = panel.candidates[argmax(means(panel.simRates))];
    if (displayedReal !== "OpenVLA") throw new Error(`${model}: real winner changed`);
    if (displayedSim !== (model === "Cosmos" ? "OpenVLA" : "Octo-Base")) {
      throw new Error(`${model}: simulator winner changed`);
    }
    const rows = [0, 10, "infinity_fixed_display"].map((evidence, evidenceIndex) =>
      evaluate(panel, evidence, 907_031 + 10_000 * modelIndex + evidenceIndex),
    );
    for (const row of rows) {
      const expected = producerProbability(producerData, model, row.evidence);
      if (Math.abs(row.probability_sampled_winners_match - expected) > 0.015) {
        throw new Error(`${model}/${row.evidence}: challenge differs from producer`);
      }
      row.producer_probability = expected;
      row.absolute_difference = Math.abs(row.probability_sampled_winners_match - expected);
      comparisons += 1;
      if (row.evidence === "0") {
        const analyticSe = Math.sqrt((1 / 3) * (2 / 3) / draws);
        if (Math.abs(row.probability_sampled_winners_match - 1 / 3) > 6 * analyticSe) {
          throw new Error(`${model}: zero-evidence analytic limit failed`);
        }
        analyticChecks += 1;
      }
      const expectedAboveHalf = model === "Cosmos" && row.evidence !== "0";
      if ((row.probability_sampled_winners_match > 0.5) !== expectedAboveHalf) {
        throw new Error(`${model}/${row.evidence}: half-boundary direction changed`);
      }
    }
    results[model] = { displayed_real_winner: displayedReal, displayed_sim_winner: displayedSim, scenarios: rows };
  }
  return {
    schema: "wm-missing-simulator-evidence-independent-challenge-v1",
    status: "pass",
    method: "Node custom PRNG and Marsaglia-Tsang gamma/Beta sampler; no Python import or execution",
    draws_per_scenario: draws,
    prior_alpha_beta: 1,
    comparisons_within_0_015: comparisons,
    zero_evidence_analytic_checks: analyticChecks,
    panels: results,
    protocol_sha256: sha256(protocol),
    producer_sha256: sha256(producer),
    producer_result_sha256: sha256(producerResult),
    input_sha256: sha256(input),
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
    throw new Error("stored WM independent challenge differs from recomputation");
  }
  process.stdout.write("OK: WM missing-simulator independent challenge\n");
}
