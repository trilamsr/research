#!/usr/bin/env node
"use strict";

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

function components(k, edges) {
  const adjacent = Array.from({ length: k }, () => new Set());
  for (const [i, j] of edges) {
    adjacent[i].add(j);
    adjacent[j].add(i);
  }
  const unseen = new Set(Array.from({ length: k }, (_, i) => i));
  const groups = [];
  while (unseen.size) {
    const root = Math.min(...unseen);
    unseen.delete(root);
    const stack = [root];
    const group = [];
    while (stack.length) {
      const node = stack.pop();
      group.push(node);
      for (const neighbor of [...adjacent[node]].sort((a, b) => b - a)) {
        if (unseen.has(neighbor)) {
          unseen.delete(neighbor);
          stack.push(neighbor);
        }
      }
    }
    groups.push(group.sort((a, b) => a - b));
  }
  return groups;
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

const h233A = components(3, [[0, 2], [1, 2]]);
const h233B = components(3, [[0, 1]]);
assert(h233A.length - 1 === 0, "H233 A repair count changed");
assert(h233B.length - 1 === 1, "H233 B repair count changed");

for (let k = 3; k <= 8; k += 1) {
  assert(components(k, []).length - 1 === k - 1, `empty K=${k} count changed`);
}

// Constrained-cost quotient case: {0,1}, {2}, {3}.
// Cheapest bridges are 1--2 (2) and 2--3 (3), total 5.
const candidates = [
  [7, [0, 2]],
  [2, [1, 2]],
  [3, [2, 3]],
  [11, [0, 3]],
];
const selected = [];
let edges = [[0, 1]];
let total = 0;
for (const [cost, edge] of candidates.sort((a, b) => a[0] - b[0])) {
  const before = components(4, edges).length;
  const after = components(4, [...edges, edge]).length;
  if (after < before) {
    selected.push(edge);
    edges = [...edges, edge];
    total += cost;
  }
}
assert(JSON.stringify(selected) === JSON.stringify([[1, 2], [2, 3]]),
  "constrained selected edges changed");
assert(total === 5, "constrained cost changed");
assert(components(4, edges).length === 1, "constrained repair disconnected");

// Repetitions cannot change the simple component partition.
assert(
  JSON.stringify(components(4, [[0, 1], [1, 2]])) ===
    JSON.stringify(components(4, [[0, 1], [0, 1], [1, 2], [1, 2]])),
  "duplicate edge changed components"
);

const result = {
  schema: "h234-route-graph-repair-design-node-v1",
  status: "pass",
  h233_context_a_minimum: 0,
  h233_context_b_minimum: 1,
  h231_empty_context_k3_to_k8: Object.fromEntries(
    Array.from({ length: 6 }, (_, n) => [String(n + 3), n + 2])
  ),
  constrained_selected_edges: selected.map(([i, j]) => [i + 1, j + 1]),
  constrained_total_cost: total,
  repeated_existing_edges_repair_identification: false
};

if (process.argv.includes("--check")) {
  const here = path.dirname(fileURLToPath(import.meta.url));
  const stored = JSON.parse(fs.readFileSync(
    path.join(here, "result-h234-route-graph-repair-design-independent-challenge.json"),
    "utf8"
  ));
  assert(JSON.stringify(stored) === JSON.stringify(result), "stored H234 challenge is stale");
  process.stdout.write("OK: H234 dependency-light Node reconstruction\n");
} else {
  process.stdout.write(JSON.stringify(result, null, 2) + "\n");
}
