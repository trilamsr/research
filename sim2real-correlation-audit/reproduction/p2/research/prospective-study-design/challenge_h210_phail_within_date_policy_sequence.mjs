#!/usr/bin/env node
// Independent H210 date-restricted policy-sequence challenge.

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const FAMILY = path.dirname(fileURLToPath(import.meta.url));
const COHORT = path.join(FAMILY, "result-h187-phail-context-support-sanitized.csv");
const H206 = path.join(FAMILY, "projection-h206-phail-clock-offset-regimes.csv");
const PRODUCER = path.join(FAMILY, "result-h210-phail-within-date-policy-sequence.json");
const OUTPUT = path.join(FAMILY, "result-h210-phail-within-date-policy-sequence-independent-challenge.json");
const EXPECTED = {
  cohort: "ad43fca1da065a1cb7fd84dfa9afc5691c72ebe12e7f165c68a0050e51e87ebe",
  h206: "7b7af23688e230325ec69070c8e5cd5523224990d7bc44defbe5b30f12c65529",
  producer: "71bf7b49976b936c147cd021776dc3c5a32a401dff5824506a28b1ae5b77d112",
};
const KEYS = ["pooled_within_date", "regime_1_dates", "regime_2_dates"];
const PERMUTATIONS = 49_999;
const SEED_TEXT = "H210 independent challenge SplitMix64 v1";
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
  constructor(seed) { this.state = seed & MASK64; }
  nextU64() {
    this.state = (this.state + 0x9e3779b97f4a7c15n) & MASK64;
    let z = this.state;
    z = ((z ^ (z >> 30n)) * 0xbf58476d1ce4e5b9n) & MASK64;
    z = ((z ^ (z >> 27n)) * 0x94d049bb133111ebn) & MASK64;
    return (z ^ (z >> 31n)) & MASK64;
  }
  uniform() { return Number(this.nextU64() >> 11n) / 2 ** 53; }
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

function loadDates() {
  requireCondition(sha256(COHORT) === EXPECTED.cohort, "cohort hash");
  requireCondition(sha256(H206) === EXPECTED.h206, "H206 hash");
  requireCondition(sha256(PRODUCER) === EXPECTED.producer, "producer hash");
  const cohort = parseCsv(COHORT);
  const clocks = parseCsv(H206);
  const byId = new Map(cohort.map((row) => [row.episode_id, row]));
  requireCondition(cohort.length === 594 && clocks.length === 594 && byId.size === 594, "counts");
  const rows = clocks.map((clock) => {
    const source = byId.get(clock.episode_id);
    requireCondition(source !== undefined, "join");
    for (const field of ["policy_model", "utc_date", "created_ts_ns"]) {
      requireCondition(source[field] === clock[field], `${field} agreement`);
    }
    const timestamp = Number(clock.first_timestamp_ns);
    requireCondition(Number.isSafeInteger(timestamp) && timestamp > 0, "timestamp");
    return {
      date: clock.utc_date,
      regime: Number(clock.group_1h),
      timestamp,
      policy: clock.policy_model,
    };
  });
  const dates = {};
  for (const row of rows) (dates[row.date] ??= []).push(row);
  requireCondition(Object.keys(dates).length === 13, "date count");
  const output = {};
  for (const date of Object.keys(dates).sort()) {
    const ordered = dates[date].sort((left, right) => left.timestamp - right.timestamp);
    const regimes = new Set(ordered.map((row) => row.regime));
    requireCondition(regimes.size === 1 && ordered.length >= 3, "date nesting");
    output[date] = {
      regime: ordered[0].regime,
      labels: ordered.map((row) => row.policy),
    };
  }
  return output;
}

function adjacentCount(labels) {
  let count = 0;
  for (let index = 1; index < labels.length; index += 1) {
    if (labels[index] === labels[index - 1]) count += 1;
  }
  return count;
}
function selectedDates(dates) {
  const names = Object.keys(dates);
  return {
    pooled_within_date: names,
    regime_1_dates: names.filter((date) => dates[date].regime === 1),
    regime_2_dates: names.filter((date) => dates[date].regime === 2),
  };
}
function statistics(dates) {
  const selected = selectedDates(dates);
  return Object.fromEntries(KEYS.map((key) => {
    const names = selected[key];
    const numerator = names.reduce((sum, date) => sum + adjacentCount(dates[date].labels), 0);
    const denominator = names.reduce((sum, date) => sum + dates[date].labels.length - 1, 0);
    return [key, numerator / denominator];
  }));
}
function labelExpectation(labels) {
  const counts = new Map();
  for (const label of labels) counts.set(label, (counts.get(label) ?? 0) + 1);
  return [...counts.values()].reduce((sum, count) => sum + count * (count - 1), 0) /
    (labels.length * (labels.length - 1));
}
function expectations(dates) {
  const selected = selectedDates(dates);
  return Object.fromEntries(KEYS.map((key) => {
    const names = selected[key];
    const numerator = names.reduce(
      (sum, date) => sum + labelExpectation(dates[date].labels) * (dates[date].labels.length - 1),
      0,
    );
    const denominator = names.reduce((sum, date) => sum + dates[date].labels.length - 1, 0);
    return [key, numerator / denominator];
  }));
}
function quantile(sorted, probability) {
  const position = (sorted.length - 1) * probability;
  const lower = Math.floor(position);
  const upper = Math.ceil(position);
  if (lower === upper) return sorted[lower];
  return sorted[lower] * (upper - position) + sorted[upper] * (position - lower);
}
function summarize(observed, expected, values) {
  const sorted = [...values].sort((a, b) => a - b);
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
  const pooled = analyses.pooled_within_date;
  if (pooled.two_sided_p <= 0.01 && Math.abs(pooled.observed_minus_permutation_median) >= 0.1) {
    return "material_pooled_within_date_policy_sequence_structure";
  }
  if (
    pooled.two_sided_p <= 0.01 ||
    analyses.regime_1_dates.two_sided_p <= 0.005 ||
    analyses.regime_2_dates.two_sided_p <= 0.005
  ) return "regime_specific_or_small_within_date_policy_sequence_structure";
  return "no_detectable_within_date_policy_sequence_structure_at_fixed_resolution";
}
function controls() {
  const dates = {
    a: { regime: 1, labels: ["x", "x", "x"] },
    b: { regime: 2, labels: ["y", "y", "y"] },
  };
  const alternating = {
    a: { regime: 1, labels: ["x", "y", "x"] },
    b: { regime: 2, labels: ["y", "x", "y"] },
  };
  return {
    constant_one: KEYS.every((key) => statistics(dates)[key] === 1),
    alternating_zero: KEYS.every((key) => statistics(alternating)[key] === 0),
  };
}
function build() {
  const challengeControls = controls();
  requireCondition(Object.values(challengeControls).every(Boolean), "controls");
  const dates = loadDates();
  const observed = statistics(dates);
  const expected = expectations(dates);
  const nulls = Object.fromEntries(KEYS.map((key) => [key, []]));
  const rng = new SplitMix64(seedFromText(SEED_TEXT));
  for (let repetition = 0; repetition < PERMUTATIONS; repetition += 1) {
    const permuted = Object.fromEntries(Object.entries(dates).map(([date, value]) => [
      date,
      { regime: value.regime, labels: rng.shuffled(value.labels) },
    ]));
    const values = statistics(permuted);
    for (const key of KEYS) nulls[key].push(values[key]);
  }
  const analyses = Object.fromEntries(
    KEYS.map((key) => [key, summarize(observed[key], expected[key], nulls[key])]),
  );
  return {
    schema: "h210-phail-within-date-policy-sequence-independent-challenge-v1",
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
    episode_count: 594,
    date_count: Object.keys(dates).length,
    challenge_controls: challengeControls,
    analyses,
    classification: classify(analyses),
    permutation_reference_treated_as_assignment_law: false,
    date_treated_as_physical_session_or_cause: false,
    state_or_performance_opened: false,
    outcome_analysis_authorized: false,
    unresolved_material_concerns: [],
  };
}

const candidate = build();
const serialized = `${JSON.stringify(candidate, null, 2)}\n`;
if (process.argv.includes("--check")) {
  requireCondition(serialized === fs.readFileSync(OUTPUT, "utf8"), "exact challenge rebuild");
  process.stdout.write("OK: H210 independent challenge reproduces\n");
} else {
  fs.writeFileSync(OUTPUT, serialized);
  process.stdout.write(serialized);
}
