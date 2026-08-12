#!/usr/bin/env node
// Independent exact H232 reconstruction. Does not import or execute producer code.

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const FAMILY = path.dirname(fileURLToPath(import.meta.url));
const PROTOCOL = path.join(FAMILY, "protocol-h232-edge-box-objective-comparison.md");
const PRODUCER = path.join(FAMILY, "edge_box_objective_comparison.py");
const PRODUCER_RESULT = path.join(FAMILY, "result-h232-edge-box-objective-comparison.json");
const OUTPUT = path.join(
  FAMILY,
  "result-h232-edge-box-objective-comparison-independent-challenge.json",
);

function requireCondition(condition, message) {
  if (!condition) throw new Error(message);
}

function sha256(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function* compositions(total, parts, prefix = []) {
  if (parts === 1) {
    yield [...prefix, total];
    return;
  }
  for (let first = 0; first <= total; first += 1) {
    yield* compositions(total - first, parts - 1, [...prefix, first]);
  }
}

function* endpointSigns(edgeCount) {
  const count = 1 << edgeCount;
  for (let mask = 0; mask < count; mask += 1) {
    yield Array.from({ length: edgeCount }, (_, i) => ((mask >> i) & 1) ? 1n : -1n);
  }
}

function edgeOrder(k) {
  const edges = [];
  for (let i = 0; i < k; i += 1) {
    for (let j = i + 1; j < k; j += 1) edges.push([i, j]);
  }
  return edges;
}

function marginEntry(edges, signs, i, j) {
  if (i === j) return 0n;
  const a = Math.min(i, j);
  const b = Math.max(i, j);
  const index = edges.findIndex(([x, y]) => x === a && y === b);
  requireCondition(index >= 0, "edge missing");
  return i < j ? signs[index] : -signs[index]; // Twice the margin.
}

function enumeratedScaledRobustMargin(counts) {
  const k = counts.length;
  const denominator = counts.reduce((a, b) => a + b, 0);
  const edges = edgeOrder(k);
  let worst = null;
  for (const signs of endpointSigns(edges.length)) {
    let againstMatrix = null;
    for (let opponent = 0; opponent < k; opponent += 1) {
      const column = counts.reduce(
        (sum, mass, i) => sum + mass * Number(marginEntry(edges, signs, i, opponent)),
        0,
      );
      if (againstMatrix === null || column < againstMatrix) againstMatrix = column;
    }
    if (worst === null || againstMatrix < worst) worst = againstMatrix;
  }
  const minimumMass = Math.min(...counts);
  const expected = -(denominator - minimumMass); // 2D times robust margin.
  requireCondition(worst === expected, `endpoint formula failed at K=${k}`);
  return worst;
}

function verifyCondorcetExclusion(k, excluded) {
  const winner = (excluded + 1) % k;
  const matrix = Array.from({ length: k }, () => Array(k).fill(0n));
  for (let opponent = 0; opponent < k; opponent += 1) {
    if (opponent === winner) continue;
    matrix[winner][opponent] = 1n;
    matrix[opponent][winner] = -1n;
  }
  for (let i = 0; i < k; i += 1) {
    for (let j = 0; j < k; j += 1) {
      requireCondition(matrix[i][j] === -matrix[j][i], "matrix is not skew-symmetric");
    }
  }
  for (let selected = 0; selected < k; selected += 1) {
    if (selected === winner) continue;
    requireCondition(
      matrix[winner][selected] > 0n,
      "constructed winner does not beat selected action",
    );
    requireCondition(
      matrix[selected][winner] < 0n,
      "selected action is not excluded by pure-winner payoff",
    );
  }
  return winner;
}

function build() {
  const rows = [];
  let gridCount = 0;
  let endpointGridCases = 0;
  for (const [k, denominator] of [[3, 12], [4, 8], [5, 5]]) {
    let best = null;
    let bestRows = [];
    for (const counts of compositions(denominator, k)) {
      const value = enumeratedScaledRobustMargin(counts);
      endpointGridCases += 1;
      if (best === null || value > best) {
        best = value;
        bestRows = [counts];
      } else if (value === best) {
        bestRows.push(counts);
      }
      gridCount += 1;
    }
    requireCondition(bestRows.length === 1, "robust uniform optimum not unique");
    requireCondition(
      bestRows[0].every((value) => value === denominator / k),
      "robust optimum is not uniform",
    );
    const excludedWitnesses = Array.from(
      { length: k },
      (_, excluded) => verifyCondorcetExclusion(k, excluded),
    );
    rows.push({
      k,
      edge_count: (k * (k - 1)) / 2,
      endpoint_count: 2 ** ((k * (k - 1)) / 2),
      grid_size: bestRows.length === 1
        ? Array.from(compositions(denominator, k)).length
        : null,
      scaled_robust_uniform_margin_numerator: best,
      scaled_robust_margin_denominator: 2 * denominator,
      p2_borda_regret: `${k - 1}/${4 * k}`,
      excluded_action_witness_winners: excludedWitnesses,
    });
  }
  return {
    schema: "h232-edge-box-objective-comparison-independent-challenge-v1",
    status: "pass",
    classification: "same_uniform_action_different_objectives",
    protocol_sha256: sha256(PROTOCOL),
    producer_implementation_sha256: sha256(PRODUCER),
    producer_result_sha256: sha256(PRODUCER_RESULT),
    runtime: { node: process.version },
    exact_endpoint_grid_cases: endpointGridCases,
    exact_simplex_grid_points: gridCount,
    rows,
    independently_verified: {
      zero_matrix_maximal_set: "entire simplex",
      possible_equilibrium_actions: "all",
      necessary_equilibrium_actions: "none",
      robust_margin_for_p: "-(1-min_i p_i)/2",
      robust_unique_lottery: "uniform",
      p2_unique_lottery: "uniform",
      objectives_and_values_differ: true,
    },
    imports_or_executes_producer: false,
  };
}

function validate(data) {
  requireCondition(
    data.schema === "h232-edge-box-objective-comparison-independent-challenge-v1",
    "unexpected schema",
  );
  requireCondition(data.status === "pass", "challenge did not pass");
  requireCondition(data.protocol_sha256 === sha256(PROTOCOL), "protocol changed");
  requireCondition(
    data.producer_implementation_sha256 === sha256(PRODUCER),
    "producer changed",
  );
  requireCondition(
    data.producer_result_sha256 === sha256(PRODUCER_RESULT),
    "producer result changed",
  );
  requireCondition(
    data.classification === "same_uniform_action_different_objectives",
    "classification changed",
  );
  requireCondition(data.imports_or_executes_producer === false, "independence changed");
}

const args = process.argv.slice(2);
requireCondition(args.length === 1, "choose exactly one of --write or --check");
if (args[0] === "--write") {
  const result = build();
  validate(result);
  fs.writeFileSync(OUTPUT, `${JSON.stringify(result, null, 2)}\n`);
  process.stdout.write(`WROTE ${OUTPUT}\n`);
} else if (args[0] === "--check") {
  requireCondition(fs.existsSync(OUTPUT), `missing result: ${OUTPUT}`);
  const stored = JSON.parse(fs.readFileSync(OUTPUT, "utf8"));
  validate(stored);
  requireCondition(
    JSON.stringify(stored) === JSON.stringify(build()),
    "stored challenge result is stale",
  );
  process.stdout.write("OK: independent H232 Node reconstruction\n");
} else {
  throw new Error("choose exactly one of --write or --check");
}
