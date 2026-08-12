#!/usr/bin/env node
// Independent H209 policy-sequence challenge; no producer import/execution.

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const FAMILY = path.dirname(fileURLToPath(import.meta.url));
const COHORT = path.join(FAMILY, "result-h187-phail-context-support-sanitized.csv");
const H206 = path.join(FAMILY, "projection-h206-phail-clock-offset-regimes.csv");
const PRODUCER = path.join(FAMILY, "result-h209-phail-within-regime-policy-sequence.json");
const OUTPUT = path.join(
  FAMILY,
  "result-h209-phail-within-regime-policy-sequence-independent-challenge.json",
);
const EXPECTED = {
  cohort: "ad43fca1da065a1cb7fd84dfa9afc5691c72ebe12e7f165c68a0050e51e87ebe",
  h206: "7b7af23688e230325ec69070c8e5cd5523224990d7bc44defbe5b30f12c65529",
  producer: "2879b1c4b0ade1e4d1fd47e5a0db5312fce2d401c5f1580f7e2af2c211da7794",
};
const PERMUTATIONS = 49_999;
const KEYS = ["pooled_within_regime", "regime_1", "regime_2"];
const SEED_TEXT = "H209 independent challenge SplitMix64 v1";
const MASK64 = (1n << 64n) - 1n;

function requireCondition(condition, message) {
  if (!condition) throw new Error(message);
}

function sha256(filePath) {
  return crypto.createHash("sha256").update(fs.readFileSync(filePath)).digest("hex");
}

function parseCsv(filePath) {
  const lines = fs.readFileSync(filePath, "utf8").trimEnd().split(/\r?\n/);
  const header = lines[0].split(",");
  return lines.slice(1).map((line) => {
    const values = line.split(",");
    requireCondition(values.length === header.length, "CSV width");
    return Object.fromEntries(header.map((key, index) => [key, values[index]]));
  });
}

class SplitMix64 {
  constructor(seed) {
    this.state = seed & MASK64;
  }
  nextU64() {
    this.state = (this.state + 0x9e3779b97f4a7c15n) & MASK64;
    let z = this.state;
    z = ((z ^ (z >> 30n)) * 0xbf58476d1ce4e5b9n) & MASK64;
    z = ((z ^ (z >> 27n)) * 0x94d049bb133111ebn) & MASK64;
    return (z ^ (z >> 31n)) & MASK64;
  }
  uniform() {
    return Number(this.nextU64() >> 11n) / 2 ** 53;
  }
  shuffled(values) {
    const output = [...values];
    for (let index = output.length - 1; index > 0; index -= 1) {
      const target = Math.floor(this.uniform() * (index + 1));
      [output[index], output[target]] = [output[target], output[index]];
    }
    return output;
  }
}

function seedFromText(text) {
  return crypto.createHash("sha256").update(text).digest().readBigUInt64BE(0);
}

function loadGroups() {
  requireCondition(sha256(COHORT) === EXPECTED.cohort, "cohort hash");
  requireCondition(sha256(H206) === EXPECTED.h206, "H206 hash");
  requireCondition(sha256(PRODUCER) === EXPECTED.producer, "producer hash");
  const cohort = parseCsv(COHORT);
  const clocks = parseCsv(H206);
  requireCondition(cohort.length === 594 && clocks.length === 594, "row counts");
  const cohortById = new Map(cohort.map((row) => [row.episode_id, row]));
  requireCondition(cohortById.size === 594, "cohort identity");
  const rows = clocks.map((clock) => {
    const source = cohortById.get(clock.episode_id);
    requireCondition(source !== undefined, "join");
    for (const field of ["policy_model", "utc_date", "created_ts_ns"]) {
      requireCondition(source[field] === clock[field], `${field} agreement`);
    }
    const timestamp = Number(clock.first_timestamp_ns);
    requireCondition(Number.isSafeInteger(timestamp) && timestamp > 0, "timestamp");
    const group = Number(clock.group_1h);
    requireCondition(group === 1 || group === 2, "group");
    return { group, timestamp, policy: clock.policy_model };
  });
  requireCondition(new Set(rows.map((row) => row.timestamp)).size === 594, "timestamp identity");
  const groups = { 1: [], 2: [] };
  for (const row of rows) groups[row.group].push(row);
  for (const group of [1, 2]) {
    groups[group].sort((left, right) => left.timestamp - right.timestamp);
    groups[group] = groups[group].map((row) => row.policy);
  }
  requireCondition(groups[1].length === 250 && groups[2].length === 344, "group sizes");
  return groups;
}

function adjacentCount(labels) {
  let count = 0;
  for (let index = 1; index < labels.length; index += 1) {
    if (labels[index] === labels[index - 1]) count += 1;
  }
  return count;
}

function statistics(groups) {
  const count1 = adjacentCount(groups[1]);
  const count2 = adjacentCount(groups[2]);
  const pairs1 = groups[1].length - 1;
  const pairs2 = groups[2].length - 1;
  requireCondition(pairs1 > 0 && pairs2 > 0, "pair counts");
  return {
    pooled_within_regime: (count1 + count2) / (pairs1 + pairs2),
    regime_1: count1 / pairs1,
    regime_2: count2 / pairs2,
  };
}

function expectation(labels) {
  const counts = new Map();
  for (const label of labels) counts.set(label, (counts.get(label) ?? 0) + 1);
  const numerator = [...counts.values()].reduce(
    (total, count) => total + count * (count - 1),
    0,
  );
  return numerator / (labels.length * (labels.length - 1));
}

function expectations(groups) {
  const expected1 = expectation(groups[1]);
  const expected2 = expectation(groups[2]);
  return {
    pooled_within_regime: (expected1 * 249 + expected2 * 343) / 592,
    regime_1: expected1,
    regime_2: expected2,
  };
}

function quantile(sorted, probability) {
  const position = (sorted.length - 1) * probability;
  const lower = Math.floor(position);
  const upper = Math.ceil(position);
  if (lower === upper) return sorted[lower];
  const weight = position - lower;
  return sorted[lower] * (1 - weight) + sorted[upper] * weight;
}

function summarize(observed, expected, values) {
  const sorted = [...values].sort((left, right) => left - right);
  const lower = (values.filter((value) => value <= observed).length + 1) / (values.length + 1);
  const upper = (values.filter((value) => value >= observed).length + 1) / (values.length + 1);
  const median = quantile(sorted, 0.5);
  return {
    observed_same_policy_adjacency_fraction: observed,
    analytic_exchangeability_expectation: expected,
    permutation_median: median,
    permutation_q025: quantile(sorted, 0.025),
    permutation_q975: quantile(sorted, 0.975),
    observed_minus_permutation_median: observed - median,
    lower_tail_p: lower,
    upper_tail_p: upper,
    two_sided_p: Math.min(1, 2 * Math.min(lower, upper)),
    permutations: values.length,
  };
}

function classify(analyses) {
  const pooled = analyses.pooled_within_regime;
  if (
    pooled.two_sided_p <= 0.01 &&
    Math.abs(pooled.observed_minus_permutation_median) >= 0.1
  ) {
    return "material_pooled_policy_sequence_structure";
  }
  if (
    pooled.two_sided_p <= 0.01 ||
    analyses.regime_1.two_sided_p <= 0.005 ||
    analyses.regime_2.two_sided_p <= 0.005
  ) {
    return "regime_specific_or_small_policy_sequence_structure";
  }
  return "no_detectable_policy_sequence_structure_at_fixed_resolution";
}

function controls() {
  const constant = statistics({ 1: ["a", "a", "a"], 2: ["b", "b", "b"] });
  const alternating = statistics({ 1: ["a", "b", "a"], 2: ["b", "a", "b"] });
  const rngA = new SplitMix64(seedFromText("H209 replay"));
  const rngB = new SplitMix64(seedFromText("H209 replay"));
  const source = ["a", "b", "c", "d", "e", "f"];
  return {
    constant_one: KEYS.every((key) => constant[key] === 1),
    alternating_zero: KEYS.every((key) => alternating[key] === 0),
    deterministic_replay:
      JSON.stringify(rngA.shuffled(source)) === JSON.stringify(rngB.shuffled(source)),
  };
}

function build() {
  const challengeControls = controls();
  requireCondition(Object.values(challengeControls).every(Boolean), "controls");
  const groups = loadGroups();
  const observed = statistics(groups);
  const expected = expectations(groups);
  const nulls = Object.fromEntries(KEYS.map((key) => [key, []]));
  const rng = new SplitMix64(seedFromText(SEED_TEXT));
  for (let repetition = 0; repetition < PERMUTATIONS; repetition += 1) {
    const values = statistics({
      1: rng.shuffled(groups[1]),
      2: rng.shuffled(groups[2]),
    });
    for (const key of KEYS) nulls[key].push(values[key]);
  }
  const analyses = Object.fromEntries(
    KEYS.map((key) => [key, summarize(observed[key], expected[key], nulls[key])]),
  );
  return {
    schema: "h209-phail-within-regime-policy-sequence-independent-challenge-v1",
    target_producer_result_sha256: sha256(PRODUCER),
    input_sha256: { cohort: sha256(COHORT), h206_projection: sha256(H206) },
    implementation: {
      language: "Node.js",
      node: process.version,
      producer_imported_or_executed: false,
      rng: "independent SplitMix64 and Fisher-Yates stream",
      seed_text: SEED_TEXT,
      permutations: PERMUTATIONS,
    },
    episode_count: groups[1].length + groups[2].length,
    group_sizes: { 1: groups[1].length, 2: groups[2].length },
    challenge_controls: challengeControls,
    analyses,
    classification: classify(analyses),
    permutation_reference_treated_as_assignment_law: false,
    state_or_performance_opened: false,
    scheduler_or_cause_identified: false,
    outcome_analysis_authorized: false,
    unresolved_material_concerns: [],
  };
}

const candidate = build();
const serialized = `${JSON.stringify(candidate, null, 2)}\n`;
if (process.argv.includes("--check")) {
  requireCondition(serialized === fs.readFileSync(OUTPUT, "utf8"), "exact challenge rebuild");
  process.stdout.write("OK: H209 independent challenge reproduces\n");
} else {
  fs.writeFileSync(OUTPUT, serialized);
  process.stdout.write(serialized);
}
