#!/usr/bin/env node
// Independent H233 known-answer reconstruction; imports no producer code.

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const FAMILY = path.dirname(fileURLToPath(import.meta.url));
const PROTOCOL = path.join(FAMILY, "protocol-h233-route-colored-shared-success.md");
const PRODUCER = path.join(FAMILY, "route_colored_shared_success.py");
const PRODUCER_RESULT = path.join(FAMILY, "result-h233-route-colored-shared-success.json");
const OUTPUT = path.join(
  FAMILY,
  "result-h233-route-colored-shared-success-independent-challenge.json",
);

function requireCondition(condition, message) {
  if (!condition) throw new Error(message);
}

function sha256(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function gcd(a, b) {
  let x = a < 0n ? -a : a;
  let y = b < 0n ? -b : b;
  while (y !== 0n) [x, y] = [y, x % y];
  return x;
}

function fraction(n, d = 1n) {
  const sign = d < 0n ? -1n : 1n;
  const divisor = gcd(n, d);
  return [sign * n / divisor, sign * d / divisor];
}

function add(a, b) {
  return fraction(a[0] * b[1] + b[0] * a[1], a[1] * b[1]);
}

function sub(a, b) {
  return fraction(a[0] * b[1] - b[0] * a[1], a[1] * b[1]);
}

function mul(a, b) {
  return fraction(a[0] * b[0], a[1] * b[1]);
}

function gt(a, b) {
  return a[0] * b[1] > b[0] * a[1];
}

function equal(a, b) {
  return a[0] * b[1] === b[0] * a[1];
}

function textFraction(a) {
  return a[1] === 1n ? `${a[0]}` : `${a[0]}/${a[1]}`;
}

function verifyBinaryIdentity() {
  let cases = 0;
  for (const yi of [0n, 1n]) {
    for (const yj of [0n, 1n]) {
      const twiceScore = yi > yj ? 2n : (yi < yj ? 0n : 1n);
      requireCondition(twiceScore === 1n + yi - yj, "half-tie identity failed");
      cases += 1;
    }
  }
  return cases;
}

function vertices() {
  const half = fraction(1n, 2n);
  return [0n, 1n].flatMap((upper) => {
    const x2 = upper === 0n ? fraction(0n) : half;
    return [fraction(0n), fraction(1n)].map((x3) => [
      add(x2, half), x2, x3,
    ]);
  });
}

function regret(counts, denominator) {
  let worst = fraction(0n);
  const half = fraction(1n, 2n);
  for (const b of vertices()) {
    const mu = b.map((value) => mul(half, value));
    let mixture = fraction(0n);
    counts.forEach((count, i) => {
      mixture = add(mixture, mul(fraction(BigInt(count), BigInt(denominator)), mu[i]));
    });
    for (const value of mu) {
      const candidate = mul(half, sub(value, mixture));
      if (gt(candidate, worst)) worst = candidate;
    }
  }
  return worst;
}

function build() {
  const identityCases = verifyBinaryIdentity();
  const endpointLow = [fraction(1n, 2n), fraction(0n), fraction(0n)];
  const endpointHigh = [fraction(1n, 2n), fraction(0n), fraction(1n)];
  requireCondition(gt(endpointLow[0], endpointLow[1]), "low winner 1 failed");
  requireCondition(gt(endpointLow[0], endpointLow[2]), "low winner 1 failed");
  requireCondition(gt(endpointHigh[2], endpointHigh[0]), "high winner 3 failed");
  requireCondition(gt(endpointHigh[2], endpointHigh[1]), "high winner 3 failed");

  let best = null;
  let bestRows = [];
  let gridPoints = 0;
  const denominator = 12;
  for (let p1 = 0; p1 <= denominator; p1 += 1) {
    for (let p2 = 0; p2 <= denominator - p1; p2 += 1) {
      const row = [p1, p2, denominator - p1 - p2];
      const value = regret(row, denominator);
      if (best === null || gt(best, value)) {
        best = value;
        bestRows = [row];
      } else if (equal(best, value)) {
        bestRows.push(row);
      }
      gridPoints += 1;
    }
  }
  requireCondition(bestRows.length === 1, "grid optimizer not unique");
  requireCondition(
    JSON.stringify(bestRows[0]) === JSON.stringify([8, 0, 4]),
    "grid optimizer changed",
  );
  requireCondition(textFraction(best) === "1/12", "minimax value changed");

  return {
    schema: "h233-route-colored-shared-success-independent-challenge-v1",
    status: "pass",
    classification: "genuine_routing_counterexample_and_minimax_verified",
    protocol_sha256: sha256(PROTOCOL),
    producer_implementation_sha256: sha256(PRODUCER),
    producer_result_sha256: sha256(PRODUCER_RESULT),
    runtime: { node: process.version },
    exact_binary_identity_cases: identityCases,
    compatible_vertex_count: vertices().length,
    exact_simplex_grid_points: gridPoints,
    unique_grid_optimizer_counts: bestRows[0],
    denominator,
    exact_minimax_lottery: ["2/3", "0", "1/3"],
    exact_minimax_regret: textFraction(best),
    opposite_unique_winners: [1, 3],
    imports_or_executes_producer: false,
  };
}

function validate(data) {
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
  const stored = JSON.parse(fs.readFileSync(OUTPUT, "utf8"));
  validate(stored);
  requireCondition(JSON.stringify(stored) === JSON.stringify(build()), "stale result");
  process.stdout.write("OK: independent H233 Node reconstruction\n");
} else {
  throw new Error("choose exactly one of --write or --check");
}
