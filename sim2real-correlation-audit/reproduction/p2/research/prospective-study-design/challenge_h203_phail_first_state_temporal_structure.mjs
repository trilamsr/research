#!/usr/bin/env node
// Independent Node reconstruction of the H203 chronology diagnostic.

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const cohortPath = path.join(here, "result-h187-phail-context-support-sanitized.csv");
const projectionPath = path.join(here, "projection-h202-phail-initial-joint-state.csv");
const producerPath = path.join(here, "result-h203-phail-first-state-temporal-structure.json");
const outputPath = path.join(here, "result-h203-phail-first-state-temporal-structure-independent-challenge.json");
const expectedCohort = "ad43fca1da065a1cb7fd84dfa9afc5691c72ebe12e7f165c68a0050e51e87ebe";
const expectedProjection = "44b7cd9729c691a610cc1fbbefffc5668d31030e013b92f2d4550f9869020370";
const permutations = 49_999;
const base = [0.0, -0.31, 0.0, -1.65, 0.0, 1.522, 0.0];
const halfWidths = [0.03, 0.05, 0.08, 0.08, 0.10, 0.10, 0.10];
const challengeSeedText = "H203 independent Node challenge v1";

function requireCondition(condition, message) {
  if (!condition) throw new Error(message);
}

function sha256File(filename) {
  return crypto.createHash("sha256").update(fs.readFileSync(filename)).digest("hex");
}

function parseCsv(text) {
  const records = [];
  let row = [];
  let field = "";
  let quoted = false;
  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    if (quoted) {
      if (char === '"' && text[index + 1] === '"') {
        field += '"';
        index += 1;
      } else if (char === '"') {
        quoted = false;
      } else {
        field += char;
      }
    } else if (char === '"') {
      quoted = true;
    } else if (char === ",") {
      row.push(field);
      field = "";
    } else if (char === "\n") {
      row.push(field.replace(/\r$/, ""));
      records.push(row);
      row = [];
      field = "";
    } else {
      field += char;
    }
  }
  if (field.length > 0 || row.length > 0) {
    row.push(field);
    records.push(row);
  }
  requireCondition(!quoted, "unterminated CSV quote");
  const header = records.shift();
  requireCondition(header && header.length > 0, "CSV header");
  return records
    .filter((values) => values.length > 1)
    .map((values) => {
      requireCondition(values.length === header.length, "CSV width");
      return Object.fromEntries(header.map((name, index) => [name, values[index]]));
    });
}

function loadRows() {
  requireCondition(sha256File(cohortPath) === expectedCohort, "cohort hash");
  requireCondition(sha256File(projectionPath) === expectedProjection, "projection hash");
  const cohort = parseCsv(fs.readFileSync(cohortPath, "utf8"));
  const projection = parseCsv(fs.readFileSync(projectionPath, "utf8"));
  requireCondition(cohort.length === 594 && projection.length === 594, "row count");
  const byEpisode = new Map(projection.map((row) => [row.episode_id, row]));
  requireCondition(byEpisode.size === 594, "projection identity");
  const rows = cohort.map((row) => {
    const projected = byEpisode.get(row.episode_id);
    requireCondition(projected, "join identity");
    requireCondition(projected.error === "0", "first error");
    const state = Array.from({ length: 7 }, (_, joint) => {
      const value = Number(projected[`q${joint}`]);
      requireCondition(Number.isFinite(value), "finite state");
      return (value - base[joint]) / (halfWidths[joint] / Math.sqrt(3));
    });
    return {
      episode: row.episode_id,
      timestamp: BigInt(row.created_ts_ns),
      policy: row.policy_model,
      date: row.utc_date,
      state,
    };
  });
  requireCondition(new Set(rows.map((row) => row.timestamp.toString())).size === 594, "timestamps");
  return rows;
}

function groups(rows, key) {
  const map = new Map();
  if (key === null) {
    map.set("all", rows.map((_, index) => index));
  } else {
    rows.forEach((row, index) => {
      const label = row[key];
      if (!map.has(label)) map.set(label, []);
      map.get(label).push(index);
    });
  }
  return [...map.entries()]
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([, indices]) => {
      indices.sort((left, right) => {
        if (rows[left].timestamp < rows[right].timestamp) return -1;
        if (rows[left].timestamp > rows[right].timestamp) return 1;
        return rows[left].episode.localeCompare(rows[right].episode);
      });
      requireCondition(indices.length >= 3, "group size");
      return indices;
    });
}

function distanceMatrix(rows) {
  const count = rows.length;
  const matrix = new Float64Array(count * count);
  for (let left = 0; left < count; left += 1) {
    for (let right = left + 1; right < count; right += 1) {
      let distance = 0;
      for (let joint = 0; joint < 7; joint += 1) {
        const difference = rows[left].state[joint] - rows[right].state[joint];
        distance += difference * difference;
      }
      matrix[left * count + right] = distance;
      matrix[right * count + left] = distance;
    }
  }
  return matrix;
}

function pairCount(groupList) {
  return groupList.reduce((total, group) => total + group.length - 1, 0);
}

function statistic(matrix, count, groupList) {
  let total = 0;
  for (const group of groupList) {
    for (let index = 1; index < group.length; index += 1) {
      total += matrix[group[index - 1] * count + group[index]];
    }
  }
  return total / pairCount(groupList);
}

function splitmix64(seed) {
  let state = BigInt.asUintN(64, seed);
  return () => {
    state = BigInt.asUintN(64, state + 0x9e3779b97f4a7c15n);
    let value = state;
    value = BigInt.asUintN(64, (value ^ (value >> 30n)) * 0xbf58476d1ce4e5b9n);
    value = BigInt.asUintN(64, (value ^ (value >> 27n)) * 0x94d049bb133111ebn);
    return BigInt.asUintN(64, value ^ (value >> 31n));
  };
}

function seedFromText(text) {
  const digest = crypto.createHash("sha256").update(text).digest();
  return digest.readBigUInt64BE(0);
}

function shuffle(values, next) {
  const output = values.slice();
  for (let index = output.length - 1; index > 0; index -= 1) {
    const selected = Number(next() % BigInt(index + 1));
    [output[index], output[selected]] = [output[selected], output[index]];
  }
  return output;
}

function quantile(sorted, probability) {
  const position = (sorted.length - 1) * probability;
  const lower = Math.floor(position);
  const upper = Math.ceil(position);
  if (lower === upper) return sorted[lower];
  const weight = position - lower;
  return sorted[lower] * (1 - weight) + sorted[upper] * weight;
}

function analyze(matrix, count, groupList, next) {
  const observed = statistic(matrix, count, groupList);
  const nullValues = new Float64Array(permutations);
  let lower = 0;
  let upper = 0;
  for (let repetition = 0; repetition < permutations; repetition += 1) {
    const permuted = groupList.map((group) => shuffle(group, next));
    const value = statistic(matrix, count, permuted);
    nullValues[repetition] = value;
    if (value <= observed) lower += 1;
    if (value >= observed) upper += 1;
  }
  const sorted = Array.from(nullValues).sort((left, right) => left - right);
  const lowerP = (lower + 1) / (permutations + 1);
  const upperP = (upper + 1) / (permutations + 1);
  const median = quantile(sorted, 0.5);
  return {
    group_count: groupList.length,
    adjacent_pair_count: pairCount(groupList),
    observed_mean_successive_squared_distance: observed,
    permutation_median: median,
    permutation_q025: quantile(sorted, 0.025),
    permutation_q975: quantile(sorted, 0.975),
    observed_to_permutation_median_ratio: observed / median,
    lower_tail_p: lowerP,
    upper_tail_p: upperP,
    two_sided_p: Math.min(1, 2 * Math.min(lowerP, upperP)),
    permutations,
  };
}

function classify(analyses) {
  const primary = analyses.global;
  const ratio = primary.observed_to_permutation_median_ratio;
  if (primary.two_sided_p <= 0.01 && (ratio <= 0.9 || ratio >= 1.1)) {
    return "material_global_temporal_structure";
  }
  if (
    primary.two_sided_p <= 0.01 ||
    analyses.within_policy.two_sided_p <= 0.01 ||
    analyses.within_utc_date.two_sided_p <= 0.01
  ) {
    return "secondary_only_or_small_temporal_structure";
  }
  return "no_detectable_temporal_structure_at_fixed_resolution";
}

function syntheticControls() {
  const fake = [
    { state: [0, 0, 0, 0, 0, 0, 0] },
    { state: [1, 0, 0, 0, 0, 0, 0] },
    { state: [3, 0, 0, 0, 0, 0, 0] },
  ];
  const matrix = distanceMatrix(fake);
  const known = statistic(matrix, 3, [[0, 1, 2]]);
  const first = splitmix64(seedFromText(challengeSeedText));
  const second = splitmix64(seedFromText(challengeSeedText));
  const replay = Array.from({ length: 100 }, () => first().toString())
    .every((value) => value === second().toString());
  return {
    known_distance: Math.abs(known - 2.5) < 1e-15,
    deterministic_rng_replay: replay,
  };
}

function build() {
  const controls = syntheticControls();
  requireCondition(Object.values(controls).every(Boolean), "synthetic controls");
  const rows = loadRows();
  const matrix = distanceMatrix(rows);
  const next = splitmix64(seedFromText(challengeSeedText));
  const analyses = {
    global: analyze(matrix, rows.length, groups(rows, null), next),
    within_policy: analyze(matrix, rows.length, groups(rows, "policy"), next),
    within_utc_date: analyze(matrix, rows.length, groups(rows, "date"), next),
  };
  const producer = JSON.parse(fs.readFileSync(producerPath, "utf8"));
  let maximumObservedDifference = 0;
  for (const key of Object.keys(analyses)) {
    maximumObservedDifference = Math.max(
      maximumObservedDifference,
      Math.abs(
        analyses[key].observed_mean_successive_squared_distance -
          producer.analyses[key].observed_mean_successive_squared_distance,
      ),
    );
  }
  const classification = classify(analyses);
  requireCondition(maximumObservedDifference <= 1e-12, "observed statistic disagreement");
  requireCondition(classification === producer.classification, "classification disagreement");
  return {
    schema: "h203-node-independent-challenge-v1",
    node_version: process.version,
    producer_result_sha256: sha256File(producerPath),
    cohort_sha256: sha256File(cohortPath),
    projection_sha256: sha256File(projectionPath),
    method:
      "independent CSV join, standardized squared-distance matrix, SplitMix64 Fisher-Yates permutations",
    seed_text: challengeSeedText,
    synthetic_controls: controls,
    analyses,
    maximum_observed_statistic_difference: maximumObservedDifference,
    producer_classification: producer.classification,
    independent_classification: classification,
    later_state_or_outcome_opened: false,
    independence_established: false,
    result: "pass",
  };
}

function validate(result) {
  requireCondition(result.schema === "h203-node-independent-challenge-v1", "schema");
  requireCondition(result.producer_result_sha256 === sha256File(producerPath), "producer hash");
  requireCondition(result.cohort_sha256 === expectedCohort, "cohort");
  requireCondition(result.projection_sha256 === expectedProjection, "projection");
  requireCondition(Object.values(result.synthetic_controls).every(Boolean), "controls");
  requireCondition(result.maximum_observed_statistic_difference <= 1e-12, "observed difference");
  requireCondition(
    result.independent_classification ===
      "no_detectable_temporal_structure_at_fixed_resolution",
    "classification",
  );
  requireCondition(result.producer_classification === result.independent_classification, "agreement");
  requireCondition(result.later_state_or_outcome_opened === false, "scope");
  requireCondition(result.independence_established === false, "independence");
  requireCondition(result.result === "pass", "result");
}

const check = process.argv.includes("--check");
if (check) {
  const stored = JSON.parse(fs.readFileSync(outputPath, "utf8"));
  validate(stored);
  console.log("OK: H203 stored independent challenge validates");
} else {
  const result = build();
  validate(result);
  fs.writeFileSync(outputPath, `${JSON.stringify(result, null, 2)}\n`);
  console.log(JSON.stringify(result, null, 2));
}
