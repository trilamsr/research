#!/usr/bin/env node
// Independent exact H212 challenge. This does not import or execute the producer.

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const PROTOCOL = path.join(HERE, "protocol-h212-zero-reference-weight-edge-box-boundary.md");
const PRODUCER = path.join(HERE, "result-h212-zero-reference-weight-edge-box-boundary.json");
const OUTPUT = path.join(
  HERE,
  "result-h212-zero-reference-weight-edge-box-boundary-independent-challenge.json",
);
const EXPECTED_PROTOCOL =
  "2204934e1e4729a0d1dff29b89e544c0da59b654d01a6270655265eda5b61e7c";
const EXPECTED_PRODUCER =
  "60197dc7967bdb388d0707299c6652403e289c2fc58a010d7a121a17b78f839e";

function requireCondition(condition, message) {
  if (!condition) throw new Error(message);
}

function gcd(a, b) {
  a = a < 0n ? -a : a;
  b = b < 0n ? -b : b;
  while (b !== 0n) [a, b] = [b, a % b];
  return a;
}

class Q {
  constructor(numerator, denominator = 1n) {
    let n = BigInt(numerator);
    let d = BigInt(denominator);
    requireCondition(d !== 0n, "zero denominator");
    if (d < 0n) {
      n = -n;
      d = -d;
    }
    const divisor = gcd(n, d);
    this.n = n / divisor;
    this.d = d / divisor;
  }
  add(other) {
    return new Q(this.n * other.d + other.n * this.d, this.d * other.d);
  }
  sub(other) {
    return new Q(this.n * other.d - other.n * this.d, this.d * other.d);
  }
  mul(other) {
    return new Q(this.n * other.n, this.d * other.d);
  }
  div(other) {
    return new Q(this.n * other.d, this.d * other.n);
  }
  neg() {
    return new Q(-this.n, this.d);
  }
  abs() {
    return new Q(this.n < 0n ? -this.n : this.n, this.d);
  }
  compare(other) {
    const delta = this.n * other.d - other.n * this.d;
    return delta < 0n ? -1 : delta > 0n ? 1 : 0;
  }
  eq(other) {
    return this.n === other.n && this.d === other.d;
  }
  text() {
    return `${this.n}/${this.d}`;
  }
  number() {
    return Number(this.n) / Number(this.d);
  }
}

const ZERO = new Q(0n);
const ONE = new Q(1n);
const TWO = new Q(2n);
const FOUR = new Q(4n);
const HALF = new Q(1n, 2n);
const QUARTER = new Q(1n, 4n);

function qsum(values) {
  return values.reduce((total, value) => total.add(value), ZERO);
}

function qmax(values) {
  return values.reduce((best, value) => (value.compare(best) > 0 ? value : best));
}

function fraction(value) {
  return {
    numerator: value.n.toString(),
    denominator: value.d.toString(),
    text: value.text(),
    decimal: value.number(),
  };
}

function sha256(filename) {
  return crypto.createHash("sha256").update(fs.readFileSync(filename)).digest("hex");
}

function normalize(raw) {
  requireCondition(raw.length >= 3, "at least three policies required");
  requireCondition(raw.every((value) => value.compare(ZERO) >= 0), "negative reference");
  const total = qsum(raw);
  requireCondition(total.compare(ZERO) > 0, "all-zero reference");
  return raw.map((value) => value.div(total));
}

function combinations(items, size) {
  const result = [];
  function visit(start, chosen) {
    if (chosen.length === size) {
      result.push(chosen.slice());
      return;
    }
    for (let index = start; index <= items.length - (size - chosen.length); index += 1) {
      chosen.push(items[index]);
      visit(index + 1, chosen);
      chosen.pop();
    }
  }
  visit(0, []);
  return result;
}

function edges(k) {
  return combinations(
    Array.from({ length: k }, (_, index) => index),
    2,
  );
}

function validateLottery(p, k) {
  requireCondition(p.length === k, "lottery length");
  requireCondition(p.every((value) => value.compare(ZERO) >= 0), "negative lottery");
  requireCondition(qsum(p).eq(ONE), "lottery sum");
}

function objectives(raw, p) {
  const r = normalize(raw);
  validateLottery(p, r.length);
  return r.map((_, winner) => {
    const dispersion = qsum(
      edges(r.length)
        .filter(([i, j]) => i !== winner && j !== winner)
        .map(([i, j]) => r[j].mul(p[i]).sub(r[i].mul(p[j])).abs()),
    );
    return ONE.sub(p[winner]).add(dispersion);
  });
}

function reducedRegret(raw, p) {
  return qmax(objectives(raw, p)).div(FOUR);
}

function endpointValues(r, mask) {
  const k = r.length;
  const q = Array.from({ length: k }, () => Array(k).fill(HALF));
  edges(k).forEach(([i, j], edgeIndex) => {
    const sign = (mask >> edgeIndex) & 1;
    q[i][j] = sign ? new Q(3n, 4n) : QUARTER;
    q[j][i] = ONE.sub(q[i][j]);
  });
  return Array.from({ length: k }, (_, i) =>
    qsum(Array.from({ length: k }, (_, j) => r[j].mul(q[i][j]))),
  );
}

function rawEndpointRegret(raw, p) {
  const r = normalize(raw);
  validateLottery(p, r.length);
  let worst = ZERO;
  const edgeCount = edges(r.length).length;
  for (let mask = 0; mask < 2 ** edgeCount; mask += 1) {
    const values = endpointValues(r, mask);
    const regret = qmax(values).sub(qsum(values.map((value, i) => p[i].mul(value))));
    if (regret.compare(worst) > 0) worst = regret;
  }
  return worst;
}

function segmentInfo(raw) {
  const r = normalize(raw);
  const order = Array.from({ length: r.length }, (_, index) => index).sort((left, right) => {
    const comparison = r[left].compare(r[right]);
    return comparison === 0 ? left - right : comparison;
  });
  const [first, second, third] = order;
  const [a, b, g] = [r[first], r[second], r[third]];
  return {
    r,
    order,
    first,
    second,
    third,
    a,
    b,
    g,
    hMin: ZERO,
    hMax: g.sub(b).div(TWO),
    value: TWO.sub(a).sub(b).div(new Q(8n)),
  };
}

function segmentLottery(raw, h) {
  const info = segmentInfo(raw);
  const { r, first, second, a, b } = info;
  const complement = ONE.sub(a).sub(b);
  const p = r.map(() => ZERO);
  p[first] = a.add(b).div(TWO).add(h);
  p[second] = b
    .mul(TWO.sub(a).sub(b))
    .div(TWO.mul(ONE.sub(a)))
    .add(ONE.sub(b).mul(h).div(ONE.sub(a)));
  const multiplier = TWO.sub(a)
    .sub(b)
    .div(ONE.sub(a))
    .mul(HALF.sub(h.div(complement)));
  r.forEach((value, index) => {
    if (index !== first && index !== second) p[index] = value.mul(multiplier);
  });
  validateLottery(p, r.length);
  return p;
}

function probes(raw) {
  const info = segmentInfo(raw);
  const candidates = [info.hMin, info.hMin.add(info.hMax).div(TWO), info.hMax];
  return [...new Map(candidates.map((value) => [value.text(), value])).values()].sort((a, b) =>
    a.compare(b),
  );
}

function combinationsWithReplacement(values, size, start = 0, prefix = [], output = []) {
  if (prefix.length === size) {
    output.push(prefix.slice());
    return output;
  }
  for (let index = start; index < values.length; index += 1) {
    prefix.push(values[index]);
    combinationsWithReplacement(values, size, index, prefix, output);
    prefix.pop();
  }
  return output;
}

function canonicalCases() {
  const result = [];
  const choices = [new Q(1n), new Q(2n), new Q(3n), new Q(4n)];
  for (let k = 3; k <= 6; k += 1) {
    for (let support = 1; support < k; support += 1) {
      const zeros = Array(k - support).fill(ZERO);
      for (const positive of combinationsWithReplacement(choices, support)) {
        result.push([...zeros, ...positive]);
      }
    }
  }
  return result;
}

function distinctPermutations(values) {
  const result = [];
  function visit(prefix, remaining) {
    if (remaining.length === 0) {
      result.push(prefix.slice());
      return;
    }
    const used = new Set();
    for (let index = 0; index < remaining.length; index += 1) {
      const key = remaining[index].text();
      if (used.has(key)) continue;
      used.add(key);
      const next = remaining.slice();
      const [value] = next.splice(index, 1);
      prefix.push(value);
      visit(prefix, next);
      prefix.pop();
    }
  }
  visit([], values);
  return result;
}

function compositions(total, parts) {
  const result = [];
  function visit(remaining, count, prefix) {
    if (count === 1) {
      result.push([...prefix, remaining]);
      return;
    }
    for (let value = 0; value <= remaining; value += 1) {
      prefix.push(value);
      visit(remaining - value, count - 1, prefix);
      prefix.pop();
    }
  }
  visit(total, parts, []);
  return result;
}

function onSegment(raw, p) {
  const info = segmentInfo(raw);
  const left = segmentLottery(raw, info.hMin);
  const right = segmentLottery(raw, info.hMax);
  if (left.every((value, index) => value.eq(right[index]))) {
    return left.every((value, index) => value.eq(p[index]));
  }
  const coordinate = left.findIndex((value, index) => !value.eq(right[index]));
  const t = p[coordinate].sub(left[coordinate]).div(right[coordinate].sub(left[coordinate]));
  if (t.compare(ZERO) < 0 || t.compare(ONE) > 0) return false;
  return p.every((value, index) =>
    value.eq(left[index].add(t.mul(right[index].sub(left[index])))),
  );
}

function build() {
  requireCondition(sha256(PROTOCOL) === EXPECTED_PROTOCOL, "protocol drift");
  requireCondition(sha256(PRODUCER) === EXPECTED_PRODUCER, "producer result drift");
  const producer = JSON.parse(fs.readFileSync(PRODUCER, "utf8"));
  requireCondition(
    producer.classification === "value_and_optimizer_extend_without_change",
    "producer classification changed",
  );

  const cases = canonicalCases();
  requireCondition(cases.length === 242, "independent census count");
  const byK = {};
  const bySupport = {};
  let segmentProbeCount = 0;
  let rawProbeCount = 0;
  let permutationCount = 0;
  let exactProofIdentityCount = 0;
  let outsideSegmentAttackCount = 0;
  let gridLotteryCount = 0;
  let gridOptimalCount = 0;

  for (const raw of cases) {
    const info = segmentInfo(raw);
    const support = raw.filter((value) => value.compare(ZERO) > 0).length;
    byK[raw.length] = (byK[raw.length] ?? 0) + 1;
    bySupport[support] = (bySupport[support] ?? 0) + 1;
    const bracketValue = info.value.mul(FOUR);

    for (const h of probes(raw)) {
      const p = segmentLottery(raw, h);
      const f = objectives(raw, p);
      requireCondition(qmax(f).eq(bracketValue), "segment value mismatch");
      requireCondition(f[info.first].eq(bracketValue), "first equalizer mismatch");
      requireCondition(f[info.second].eq(bracketValue), "second equalizer mismatch");
      for (const tail of info.order.slice(2)) {
        const identity = f[tail].sub(bracketValue);
        const expected = h.mul(TWO).sub(info.r[tail].sub(info.b));
        requireCondition(identity.eq(expected), "tail face identity mismatch");
      }
      for (const [i, j] of combinations(info.order.slice(2), 2)) {
        requireCondition(
          info.r[j].mul(p[i]).sub(info.r[i].mul(p[j])).eq(ZERO),
          "tail proportionality mismatch",
        );
      }
      exactProofIdentityCount += 1;
      segmentProbeCount += 1;
      if (raw.length <= 5) {
        requireCondition(rawEndpointRegret(raw, p).eq(info.value), "raw endpoint mismatch");
        rawProbeCount += 1;
      }
    }

    for (const permuted of distinctPermutations(raw)) {
      const permutedInfo = segmentInfo(permuted);
      requireCondition(permutedInfo.value.eq(info.value), "permutation value mismatch");
      for (const h of probes(permuted)) {
        requireCondition(
          reducedRegret(permuted, segmentLottery(permuted, h)).eq(info.value),
          "permutation optimizer mismatch",
        );
      }
      permutationCount += 1;
    }

    const complementHalf = ONE.sub(info.a).sub(info.b).div(TWO);
    if (info.hMax.compare(complementHalf) < 0) {
      const outsideH = info.hMax.add(complementHalf).div(TWO);
      const outsideP = segmentLottery(raw, outsideH);
      requireCondition(
        reducedRegret(raw, outsideP).compare(info.value) > 0,
        "outside-segment attack remained optimal",
      );
      outsideSegmentAttackCount += 1;
    }

    if (raw.length <= 5) {
      const denominator = 8;
      for (const integerP of compositions(denominator, raw.length)) {
        const p = integerP.map((value) => new Q(BigInt(value), BigInt(denominator)));
        const f = objectives(raw, p);
        requireCondition(
          f[info.first].add(f[info.second]).compare(TWO.sub(info.a).sub(info.b)) >= 0,
          "lower-bound identity violated",
        );
        const regret = qmax(f).div(FOUR);
        requireCondition(regret.compare(info.value) >= 0, "grid found lower value");
        if (regret.eq(info.value)) {
          requireCondition(onSegment(raw, p), "grid found optimizer outside segment");
          gridOptimalCount += 1;
        }
        gridLotteryCount += 1;
      }
    }
  }

  requireCondition(segmentProbeCount === 484, "segment probe count");
  requireCondition(rawProbeCount === 247, "raw endpoint count");
  requireCondition(permutationCount === 14056, "permutation count");
  requireCondition(outsideSegmentAttackCount === 238, "outside attack count");

  const attacks = [
    {
      attack: "value_formula_boundary_failure",
      disposition: "rejected",
      evidence: `${cases.length} exact zero-pattern cases and ${gridLotteryCount} exact grid lotteries`,
    },
    {
      attack: "new_optimizer_direction_on_boundary",
      disposition: "rejected",
      evidence: `${gridOptimalCount} grid optima all lie on the proposed exact segment`,
    },
    {
      attack: "raw_reduction_invalid_at_zero_weight",
      disposition: "rejected",
      evidence: `${rawProbeCount} exact raw-box endpoint comparisons`,
    },
    {
      attack: "label_or_tie_dependence",
      disposition: "rejected",
      evidence: `${permutationCount} distinct label permutations`,
    },
    {
      attack: "segment_endpoint_is_not_complete",
      disposition: "rejected",
      evidence: `${outsideSegmentAttackCount} exact just-outside face attacks`,
    },
    {
      attack: "zero_weight_implies_zero_lottery_mass",
      disposition: "confirmed_as_false",
      evidence:
        "with exactly two zeros, both may receive equal h mass through min-positive/2",
    },
    {
      attack: "three_or_more_zero_weights_create_a_larger_face",
      disposition: "rejected",
      evidence: "r_(2)=r_(3)=0 collapses h to zero and p=r uniquely",
    },
  ];

  return {
    schema: "h212-zero-reference-weight-edge-box-boundary-independent-challenge-v1",
    protocol_sha256: EXPECTED_PROTOCOL,
    producer_result_sha256: EXPECTED_PRODUCER,
    implementation: "independent Node.js BigInt rational arithmetic",
    imports_or_executes_producer: false,
    classification: "value_and_optimizer_extend_without_change",
    exact_case_census: {
      canonical_cases: cases.length,
      by_k: byK,
      by_positive_support_size: bySupport,
      segment_probes: segmentProbeCount,
      raw_endpoint_oracle_probes_k_le_5: rawProbeCount,
      distinct_label_permutations: permutationCount,
      exact_grid_lotteries_k_le_5_denominator_8: gridLotteryCount,
      grid_optima_on_claimed_segment: gridOptimalCount,
      just_outside_segment_attacks: outsideSegmentAttackCount,
      proof_identity_checks: exactProofIdentityCount,
    },
    exact_derivation: [
      "F_1+F_2 >= 2-p_1-p_2+|p_1+p_2-a-b| >= 2-a-b.",
      "Equality forces every tail cross-product to zero; a positive tail total forces p_i=lambda*r_i even for zero tail weights.",
      "Solving F_1=F_2 yields the unchanged H188 h-segment on the closed simplex.",
      "Every tail constraint reduces exactly to 2h <= r_j-b, so the complete face is 0<=h<=(r_(3)-r_(2))/2.",
    ],
    attacks,
    producer_agreement: {
      classification: true,
      canonical_case_count: producer.exact_case_census.canonical_cases === cases.length,
      raw_endpoint_count:
        producer.exact_case_census.raw_endpoint_oracle_probes_k_le_5 === rawProbeCount,
      permutation_count:
        producer.exact_case_census.distinct_label_permutations === permutationCount,
      theorem_value: producer.closed_simplex_theorem.value === "(2-r_(1)-r_(2))/8",
      uniqueness:
        producer.closed_simplex_theorem.uniqueness_condition === "r_(2)=r_(3)",
    },
    scope:
      "closed reference simplex only for the weighted-Borda full compatible edge box and ex-ante expected regret",
  };
}

function stable(value) {
  if (Array.isArray(value)) return value.map(stable);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.keys(value).sort().map((key) => [key, stable(value[key])]));
  }
  return value;
}

function main() {
  const args = new Set(process.argv.slice(2));
  requireCondition(args.size === 1 && (args.has("--write") || args.has("--check")), "choose --write or --check");
  const result = stable(build());
  if (args.has("--check")) {
    const retained = JSON.parse(fs.readFileSync(OUTPUT, "utf8"));
    requireCondition(JSON.stringify(retained) === JSON.stringify(result), "challenge result drift");
    return;
  }
  fs.writeFileSync(OUTPUT, `${JSON.stringify(result, null, 2)}\n`);
}

main();
