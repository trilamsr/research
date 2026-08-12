#!/usr/bin/env node
// Independent H207 challenge: no import or execution of the Python producer.

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const FAMILY = path.dirname(fileURLToPath(import.meta.url));
const H202 = path.join(FAMILY, "projection-h202-phail-initial-joint-state.csv");
const H206 = path.join(FAMILY, "projection-h206-phail-clock-offset-regimes.csv");
const PRODUCER = path.join(
  FAMILY,
  "result-h207-phail-clock-regime-temporal-structure.json",
);
const OUTPUT = path.join(
  FAMILY,
  "result-h207-phail-clock-regime-temporal-structure-independent-challenge.json",
);
const EXPECTED = {
  h202: "44b7cd9729c691a610cc1fbbefffc5668d31030e013b92f2d4550f9869020370",
  h206: "7b7af23688e230325ec69070c8e5cd5523224990d7bc44defbe5b30f12c65529",
  producer:
    "31ef2b4162157769bf9f99ce47f50865076b99e114c7a67592319ce8df2b2252",
};
const GROUP_SIZES = { 1: 250, 2: 344 };
const ANALYSIS_KEYS = ["pooled_within_regime", "regime_1", "regime_2"];
const PERMUTATIONS = 49_999;
const BASE = [0.0, -0.31, 0.0, -1.65, 0.0, 1.522, 0.0];
const HALF_WIDTHS = [0.03, 0.05, 0.08, 0.08, 0.1, 0.1, 0.1];
const MASK64 = (1n << 64n) - 1n;
const SEED_TEXT = "H207 independent challenge SplitMix64 v1";

function requireCondition(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function sha256(filePath) {
  return crypto.createHash("sha256").update(fs.readFileSync(filePath)).digest("hex");
}

function parseCsv(filePath) {
  const lines = fs
    .readFileSync(filePath, "utf8")
    .trimEnd()
    .split(/\r?\n/);
  const header = lines[0].split(",");
  return lines.slice(1).map((line) => {
    const values = line.split(",");
    requireCondition(values.length === header.length, `CSV width: ${filePath}`);
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
  const digest = crypto.createHash("sha256").update(text).digest();
  return digest.readBigUInt64BE(0);
}

function loadJoin() {
  requireCondition(sha256(H202) === EXPECTED.h202, "H202 hash");
  requireCondition(sha256(H206) === EXPECTED.h206, "H206 hash");
  requireCondition(sha256(PRODUCER) === EXPECTED.producer, "producer hash");
  const stateRows = parseCsv(H202);
  const clockRows = parseCsv(H206);
  requireCondition(stateRows.length === 594, "H202 count");
  requireCondition(clockRows.length === 594, "H206 count");
  const stateById = new Map(stateRows.map((row) => [row.episode_id, row]));
  requireCondition(stateById.size === 594, "H202 identity");
  requireCondition(new Set(clockRows.map((row) => row.episode_id)).size === 594, "H206 identity");

  const rows = clockRows.map((clock) => {
    const state = stateById.get(clock.episode_id);
    requireCondition(state !== undefined, "join identity");
    requireCondition(Number(state.error) === 0, "first-state error");
    const timestamp = Number(clock.first_timestamp_ns);
    requireCondition(Number.isSafeInteger(timestamp) && timestamp > 0, "timestamp");
    requireCondition(Number(state.timestamp_ns) === timestamp, "timestamp agreement");
    const group = Number(clock.group_1h);
    requireCondition(group === 1 || group === 2, "group label");
    const z = BASE.map((base, joint) => {
      const q = Number(state[`q${joint}`]);
      requireCondition(Number.isFinite(q), "finite state");
      return (q - base) / (HALF_WIDTHS[joint] / Math.sqrt(3));
    });
    return { episodeId: clock.episode_id, timestamp, group, z };
  });
  requireCondition(new Set(rows.map((row) => row.timestamp)).size === 594, "timestamp identity");
  return rows;
}

function orderedGroups(rows) {
  const groups = { 1: [], 2: [] };
  rows.forEach((row, index) => groups[row.group].push(index));
  for (const label of [1, 2]) {
    requireCondition(groups[label].length === GROUP_SIZES[label], `group ${label} size`);
    groups[label].sort((left, right) => rows[left].timestamp - rows[right].timestamp);
  }
  return groups;
}

function groupDistanceSum(states, indices) {
  let total = 0;
  for (let position = 1; position < indices.length; position += 1) {
    const previous = states[indices[position - 1]];
    const current = states[indices[position]];
    for (let joint = 0; joint < 7; joint += 1) {
      const difference = current[joint] - previous[joint];
      total += difference * difference;
    }
  }
  return total;
}

function statistics(states, groups) {
  const sum1 = groupDistanceSum(states, groups[1]);
  const sum2 = groupDistanceSum(states, groups[2]);
  const pairs1 = groups[1].length - 1;
  const pairs2 = groups[2].length - 1;
  requireCondition(pairs1 > 0 && pairs2 > 0, "pair counts");
  return {
    pooled_within_regime: (sum1 + sum2) / (pairs1 + pairs2),
    regime_1: sum1 / pairs1,
    regime_2: sum2 / pairs2,
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

function summarize(observed, values) {
  const sorted = [...values].sort((left, right) => left - right);
  const lowerCount = values.filter((value) => value <= observed).length;
  const upperCount = values.filter((value) => value >= observed).length;
  const lowerP = (lowerCount + 1) / (values.length + 1);
  const upperP = (upperCount + 1) / (values.length + 1);
  const median = quantile(sorted, 0.5);
  return {
    observed_mean_successive_squared_distance: observed,
    permutation_median: median,
    permutation_q025: quantile(sorted, 0.025),
    permutation_q975: quantile(sorted, 0.975),
    observed_to_permutation_median_ratio: observed / median,
    lower_tail_p: lowerP,
    upper_tail_p: upperP,
    two_sided_p: Math.min(1, 2 * Math.min(lowerP, upperP)),
    permutations: values.length,
  };
}

function classify(analyses) {
  const pooled = analyses.pooled_within_regime;
  const ratio = pooled.observed_to_permutation_median_ratio;
  if (
    pooled.two_sided_p <= 0.01 &&
    (ratio <= 0.9 || ratio >= 1.1)
  ) {
    return "material_pooled_clock_regime_temporal_structure";
  }
  if (
    pooled.two_sided_p <= 0.01 ||
    analyses.regime_1.two_sided_p <= 0.005 ||
    analyses.regime_2.two_sided_p <= 0.005
  ) {
    return "regime_specific_or_small_clock_regime_temporal_structure";
  }
  return "no_detectable_clock_regime_temporal_structure_at_fixed_resolution";
}

function controls() {
  const states = [
    [0, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [3, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [3, 0, 0, 0, 0, 0, 0],
  ];
  const known = statistics(states, { 1: [0, 1, 2], 2: [3, 4, 5] });
  const rngA = new SplitMix64(seedFromText("H207 challenge replay"));
  const rngB = new SplitMix64(seedFromText("H207 challenge replay"));
  const source = Array.from({ length: 20 }, (_, index) => index);
  const drawA = rngA.shuffled(source);
  const drawB = rngB.shuffled(source);
  const first = new Set(rngA.shuffled([0, 1, 2, 3]));
  const second = new Set(rngA.shuffled([4, 5, 6, 7, 8, 9]));
  return {
    known_distance: Math.abs(known.pooled_within_regime - 2.5) <= 1e-15,
    deterministic_replay: drawA.every((value, index) => value === drawB[index]),
    restricted_membership:
      [...first].every((value) => value < 4) &&
      [...second].every((value) => value >= 4),
  };
}

function build() {
  const challengeControls = controls();
  requireCondition(Object.values(challengeControls).every(Boolean), "challenge controls");
  const rows = loadJoin();
  const groups = orderedGroups(rows);
  const states = rows.map((row) => row.z);
  const observed = statistics(states, groups);
  const nulls = Object.fromEntries(ANALYSIS_KEYS.map((key) => [key, []]));
  const rng = new SplitMix64(seedFromText(SEED_TEXT));
  for (let repetition = 0; repetition < PERMUTATIONS; repetition += 1) {
    const permuted = {
      1: rng.shuffled(groups[1]),
      2: rng.shuffled(groups[2]),
    };
    const values = statistics(states, permuted);
    for (const key of ANALYSIS_KEYS) nulls[key].push(values[key]);
  }
  const analyses = Object.fromEntries(
    ANALYSIS_KEYS.map((key) => [key, summarize(observed[key], nulls[key])]),
  );
  const producer = JSON.parse(fs.readFileSync(PRODUCER, "utf8"));
  return {
    schema: "h207-phail-clock-regime-temporal-independent-challenge-v1",
    target_producer_result_sha256: sha256(PRODUCER),
    input_sha256: {
      h202_projection: sha256(H202),
      h206_projection: sha256(H206),
    },
    implementation: {
      language: "Node.js",
      node: process.version,
      producer_imported_or_executed: false,
      csv_parser: "independent exact-width line parser",
      rng: "independent SplitMix64 and Fisher-Yates stream",
      seed_text: SEED_TEXT,
      permutations: PERMUTATIONS,
    },
    episode_count: rows.length,
    group_sizes: { 1: groups[1].length, 2: groups[2].length },
    pooled_pair_count: 592,
    challenge_controls: challengeControls,
    analyses,
    classification: classify(analyses),
    producer_classification: producer.classification,
    later_state_or_performance_opened: false,
    clock_regime_treated_as_session: false,
    independence_established: false,
    unresolved_material_concerns: [],
  };
}

const candidate = build();
const serialized = `${JSON.stringify(candidate, null, 2)}\n`;
if (process.argv.includes("--check")) {
  requireCondition(serialized === fs.readFileSync(OUTPUT, "utf8"), "exact challenge rebuild");
  process.stdout.write("OK: H207 independent challenge reproduces exactly\n");
} else {
  fs.writeFileSync(OUTPUT, serialized);
  process.stdout.write(serialized);
}
