#!/usr/bin/env node
// Independent BigInt-rational reconstruction of H151.

import crypto from "node:crypto";
import fs from "node:fs";

function gcd(a, b) {
  a = a < 0n ? -a : a;
  b = b < 0n ? -b : b;
  while (b !== 0n) {
    const next = a % b;
    a = b;
    b = next;
  }
  return a;
}

function rat(numerator, denominator = 1n) {
  if (denominator === 0n) throw new Error("zero denominator");
  if (denominator < 0n) {
    numerator = -numerator;
    denominator = -denominator;
  }
  const divisor = gcd(numerator, denominator);
  return { n: numerator / divisor, d: denominator / divisor };
}

function add(left, right) {
  return rat(left.n * right.d + right.n * left.d, left.d * right.d);
}

function sub(left, right) {
  return rat(left.n * right.d - right.n * left.d, left.d * right.d);
}

function mul(left, right) {
  return rat(left.n * right.n, left.d * right.d);
}

function div(left, right) {
  return rat(left.n * right.d, left.d * right.n);
}

function compare(left, right) {
  const delta = left.n * right.d - right.n * left.d;
  return delta < 0n ? -1 : delta > 0n ? 1 : 0;
}

function text(value) {
  return `${value.n}/${value.d}`;
}

const ZERO = rat(0n);
const ONE = rat(1n);
const HALF = rat(1n, 2n);
const QUARTER = rat(1n, 4n);
const THREE_QUARTERS = rat(3n, 4n);
const THIRD = rat(1n, 3n);
const PAIRS = ["01", "02", "12"];
const ROUTES = { "01": "A", "02": "B", "12": "A" };

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function policyValues([q01, q02, q12]) {
  return [
    div(add(add(HALF, q01), q02), rat(3n)),
    div(add(add(HALF, sub(ONE, q01)), q12), rat(3n)),
    div(add(add(HALF, sub(ONE, q02)), sub(ONE, q12)), rat(3n)),
  ];
}

function schedule(unobserved) {
  const result = {};
  for (const pair of PAIRS) {
    const observed = ROUTES[pair];
    const other = observed === "A" ? "B" : "A";
    result[pair] = { [observed]: HALF, [other]: unobserved };
  }
  return result;
}

function observedProjection(value) {
  return PAIRS.map((pair) => [
    pair,
    ROUTES[pair],
    text(value[pair][ROUTES[pair]]),
  ]);
}

function commonEdges(value) {
  return PAIRS.map((pair) =>
    div(add(value[pair].A, value[pair].B), rat(2n)),
  );
}

function uniqueWinner(values) {
  let winner = 0;
  for (let index = 1; index < values.length; index += 1) {
    if (compare(values[index], values[winner]) > 0) winner = index;
  }
  assert(
    values.filter((value) => compare(value, values[winner]) === 0).length === 1,
    "winner is not unique",
  );
  return winner;
}

const lowSchedule = schedule(ZERO);
const highSchedule = schedule(ONE);
const lowObserved = observedProjection(lowSchedule);
const highObserved = observedProjection(highSchedule);
assert(JSON.stringify(lowObserved) === JSON.stringify(highObserved), "laws differ");
const lowEdges = commonEdges(lowSchedule);
const highEdges = commonEdges(highSchedule);
assert(lowEdges.every((value) => compare(value, QUARTER) === 0), "low edges changed");
assert(
  highEdges.every((value) => compare(value, THREE_QUARTERS) === 0),
  "high edges changed",
);
const lowValues = policyValues(lowEdges);
const highValues = policyValues(highEdges);
assert(uniqueWinner(lowValues) === 2, "low winner changed");
assert(uniqueWinner(highValues) === 0, "high winner changed");

const pairConditionedValues = policyValues([HALF, HALF, HALF]);
assert(
  pairConditionedValues.every((value) => compare(value, HALF) === 0),
  "pair-conditioned tie changed",
);

const worst = [ZERO, ZERO, ZERO];
const endpointRows = [];
for (let mask = 0; mask < 8; mask += 1) {
  const edges = [0, 1, 2].map((index) =>
    mask & (1 << index) ? THREE_QUARTERS : QUARTER,
  );
  const values = policyValues(edges);
  const best = values.reduce((left, right) =>
    compare(left, right) >= 0 ? left : right,
  );
  const regrets = values.map((value) => sub(best, value));
  regrets.forEach((regret, policy) => {
    if (compare(regret, worst[policy]) > 0) worst[policy] = regret;
  });
  endpointRows.push({
    edges: edges.map(text),
    values: values.map(text),
    regrets: regrets.map(text),
  });
}
assert(worst.every((value) => compare(value, THIRD) === 0), "floor changed");

const argumentsMap = new Map();
for (let index = 2; index < process.argv.length; index += 2) {
  argumentsMap.set(process.argv[index], process.argv[index + 1]);
}
const outPath = argumentsMap.get("--out");
const protocolPath = argumentsMap.get("--protocol");
assert(outPath, "--out is required");
assert(protocolPath, "--protocol is required");

const result = {
  schema: "h152-pair-first-identification-independent-challenge-v1",
  challenge_runtime: process.version,
  producer_modules_imported: false,
  protocol_sha256: crypto
    .createHash("sha256")
    .update(fs.readFileSync(protocolPath))
    .digest("hex"),
  pair_conditioned_policy_values: pairConditionedValues.map(text),
  low_world: {
    observed_projection: lowObserved,
    common_edges: lowEdges.map(text),
    policy_values: lowValues.map(text),
    unique_winner: 2,
  },
  high_world: {
    observed_projection: highObserved,
    common_edges: highEdges.map(text),
    policy_values: highValues.map(text),
    unique_winner: 0,
  },
  same_observed_law: true,
  endpoint_completions_exhausted: endpointRows.length,
  endpoint_rows: endpointRows,
  singleton_worst_regret: worst.map(text),
  complete_pair_support_identifies_common_context_target: false,
  disposition: "pass_with_scope",
};

fs.writeFileSync(outPath, `${JSON.stringify(result, null, 2)}\n`);
process.stdout.write(
  `${JSON.stringify({
    disposition: result.disposition,
    low_winner: 2,
    high_winner: 0,
    singleton_floor: text(THIRD),
  })}\n`,
);
