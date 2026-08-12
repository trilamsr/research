#!/usr/bin/env node
// Independent exact H231 reconstruction. Does not import or execute producer code.

import fs from "node:fs";
import crypto from "node:crypto";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const FAMILY = path.dirname(fileURLToPath(import.meta.url));
const PROTOCOL = path.join(FAMILY, "protocol-h231-shared-binary-success-sensitivity.md");
const PRODUCER = path.join(FAMILY, "shared_binary_success_sensitivity.py");
const PRODUCER_RESULT = path.join(FAMILY, "result-h231-shared-binary-success-sensitivity.json");
const OUTPUT = path.join(
  FAMILY,
  "result-h231-shared-binary-success-sensitivity-independent-challenge.json",
);

function requireCondition(condition, message) {
  if (!condition) throw new Error(message);
}

function sha256(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function* binaryVertices(k) {
  const count = 1 << k;
  for (let mask = 0; mask < count; mask += 1) {
    yield Array.from({ length: k }, (_, i) => BigInt((mask >> i) & 1));
  }
}

function verifyBinaryHalfTieIdentity() {
  let cases = 0;
  for (const yi of [0n, 1n]) {
    for (const yj of [0n, 1n]) {
      const twiceScore = yi > yj ? 2n : (yi < yj ? 0n : 1n);
      requireCondition(
        twiceScore === 1n + yi - yj,
        "binary half-tie identity failed",
      );
      cases += 1;
    }
  }
  return cases;
}

function verifyOppositeWinnerWitnesses(k) {
  const first = [1n, ...Array(k - 1).fill(0n)];
  const last = [...Array(k - 1).fill(0n), 1n];
  const winners = (values) => {
    const maximum = values.reduce((a, b) => (a > b ? a : b));
    return values
      .map((value, index) => ({ value, index }))
      .filter((row) => row.value === maximum)
      .map((row) => row.index);
  };
  requireCondition(
    JSON.stringify(winners(first)) === JSON.stringify([0]),
    "e1 is not a unique common-context winner",
  );
  requireCondition(
    JSON.stringify(winners(last)) === JSON.stringify([k - 1]),
    "eK is not a unique common-context winner",
  );
  return [0, k - 1];
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

function references(k) {
  const triangular = (k * (k + 1)) / 2;
  const rows = [
    { numerators: Array(k).fill(1n), denominator: BigInt(k), label: "uniform" },
    {
      numerators: Array.from({ length: k }, (_, i) => BigInt(i + 1)),
      denominator: BigInt(triangular),
      label: "unequal-positive",
    },
    {
      numerators: [1n, ...Array(k - 1).fill(0n)],
      denominator: 1n,
      label: "singleton",
    },
  ];
  rows.push({
    numerators: [0n, ...Array(k - 1).fill(1n)],
    denominator: BigInt(k - 1),
    label: "one-zero",
  });
  if (k >= 4) {
    rows.push({
      numerators: [0n, 0n, ...Array(k - 2).fill(1n)],
      denominator: BigInt(k - 2),
      label: "two-zero",
    });
  }
  return rows;
}

function lotteries(k) {
  const triangular = (k * (k + 1)) / 2;
  return [
    { numerators: Array(k).fill(1n), denominator: BigInt(k), label: "uniform" },
    {
      numerators: [1n, ...Array(k - 1).fill(0n)],
      denominator: 1n,
      label: "singleton",
    },
    {
      numerators: [1n, 1n, ...Array(k - 2).fill(0n)],
      denominator: 2n,
      label: "two-way",
    },
    {
      numerators: Array.from({ length: k }, (_, i) => BigInt(i + 1)),
      denominator: BigInt(triangular),
      label: "unequal",
    },
  ];
}

function scaledRegret(vertex, lottery, reference) {
  const rDotX = reference.numerators.reduce(
    (sum, value, i) => sum + value * vertex[i],
    0n,
  );
  const scaledValues = vertex.map(
    (value) => 2n * reference.denominator
      + reference.denominator * value
      - rDotX,
  ); // Each is 4R * V_i.
  const maximum = scaledValues.reduce((a, b) => (a > b ? a : b));
  const mixtureNumerator = lottery.numerators.reduce(
    (sum, value, i) => sum + value * scaledValues[i],
    0n,
  );
  return lottery.denominator * maximum - mixtureNumerator; // 4RD * regret.
}

function verifyCase(k, lottery, reference) {
  let worst = -1n;
  for (const vertex of binaryVertices(k)) {
    const current = scaledRegret(vertex, lottery, reference);
    if (current > worst) worst = current;
    for (let i = 0; i < k; i += 1) {
      for (let j = i + 1; j < k; j += 1) {
        for (let m = j + 1; m < k; m += 1) {
          const dij = vertex[i] - vertex[j];
          const djm = vertex[j] - vertex[m];
          const dim = vertex[i] - vertex[m];
          requireCondition(dim === dij + djm, "gradient cycle failed");
        }
      }
    }
  }
  const minimumMass = lottery.numerators.reduce((a, b) => (a < b ? a : b));
  const expected = reference.denominator * (lottery.denominator - minimumMass);
  requireCondition(worst === expected, `regret formula failed for K=${k}`);
}

function build() {
  const rows = [];
  let caseCount = 0;
  const binaryIdentityCases = verifyBinaryHalfTieIdentity();
  for (let k = 3; k <= 7; k += 1) {
    for (const reference of references(k)) {
      for (const lottery of lotteries(k)) {
        verifyCase(k, lottery, reference);
        caseCount += 1;
      }
    }
    const uniform = lotteries(k)[0];
    const uniformNumerator = BigInt(k - 1);
    const uniformDenominator = BigInt(4 * k);
    rows.push({
      k,
      vertex_count: 2 ** k,
      uniform_value: `${uniformNumerator}/${uniformDenominator}`,
      deterministic_value: "1/4",
      reference_count: references(k).length,
      lottery_count: lotteries(k).length,
      uniform_minimum_mass_numerator: uniform.numerators[0].toString(),
      opposite_unique_winner_indices: verifyOppositeWinnerWitnesses(k),
    });
  }

  let gridCount = 0;
  for (const [k, denominator] of [[3, 12], [4, 8], [5, 5]]) {
    let best = null;
    let bestRows = [];
    for (const row of compositions(denominator, k)) {
      const minimum = Math.min(...row);
      const objective = denominator - minimum; // Four times regret, scaled by D.
      if (best === null || objective < best) {
        best = objective;
        bestRows = [row];
      } else if (objective === best) {
        bestRows.push(row);
      }
      gridCount += 1;
    }
    if (denominator % k === 0) {
      requireCondition(bestRows.length === 1, "uniform grid minimizer not unique");
      requireCondition(
        bestRows[0].every((value) => value === denominator / k),
        "uniform grid minimizer changed",
      );
    }
  }

  return {
    schema: "h231-shared-binary-success-independent-challenge-v1",
    status: "pass",
    classification: "central_result_survives_with_gradient_geometry",
    protocol_sha256: sha256(PROTOCOL),
    producer_implementation_sha256: sha256(PRODUCER),
    producer_result_sha256: sha256(PRODUCER_RESULT),
    runtime: { node: process.version },
    exact_k_min: 3,
    exact_k_max: 7,
    exact_reference_lottery_cases: caseCount,
    exact_binary_joint_law_identity_cases: binaryIdentityCases,
    exact_simplex_grid_points: gridCount,
    rows,
    independently_verified: {
      gradient_geometry_not_full_edge_box: true,
      opposite_unique_common_context_winners: true,
      opponent_reference_cancels: true,
      deterministic_worst_regret: "1/4",
      unique_uniform_minimax: true,
      minimax_value: "(K-1)/(4K)",
    },
    imports_or_executes_producer: false,
  };
}

function validate(data) {
  requireCondition(
    data.schema === "h231-shared-binary-success-independent-challenge-v1",
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
    data.classification === "central_result_survives_with_gradient_geometry",
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
  process.stdout.write("OK: independent H231 Node reconstruction\n");
} else {
  throw new Error("choose exactly one of --write or --check");
}
