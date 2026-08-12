#!/usr/bin/env ruby
# Independent exact H213 challenge. Does not import or execute the producer.

require "digest"
require "json"

HERE = File.expand_path(File.dirname(__FILE__))
PROTOCOL = File.join(HERE, "protocol-h213-support-constrained-zero-reference-boundary.md")
PRODUCER = File.join(HERE, "result-h213-support-constrained-zero-reference-boundary.json")
OUTPUT = File.join(
  HERE,
  "result-h213-support-constrained-zero-reference-boundary-independent-challenge.json"
)
EXPECTED_PROTOCOL = "5fec939a816ef97ac8e16587ac0dcddbb0f9298ac0fb311eb804c0a45a7921c7"
EXPECTED_PRODUCER = "a482b94e6dd2dc9b89be52f01bb7dbb9c0348ea565a6fd753fd94cffd9ed32ce"

def require_condition(condition, message)
  raise message unless condition
end

def sha256(path)
  Digest::SHA256.file(path).hexdigest
end

def fraction(value)
  {
    "numerator" => value.numerator.to_s,
    "denominator" => value.denominator.to_s,
    "text" => "#{value.numerator}/#{value.denominator}",
    "decimal" => value.to_f
  }
end

def normalize(raw)
  require_condition(raw.length >= 3, "at least three policies required")
  require_condition(raw.all? { |value| value >= 0 }, "negative reference")
  total = raw.sum
  require_condition(total > 0, "all-zero reference")
  raw.map { |value| value / total }
end

def edges(k)
  (0...k).to_a.combination(2).to_a
end

def validate_lottery(p, k)
  require_condition(p.length == k, "lottery length")
  require_condition(p.all? { |value| value >= 0 }, "negative lottery")
  require_condition(p.sum == 1, "lottery sum")
end

def validate_support(raw, p)
  r = normalize(raw)
  validate_lottery(p, r.length)
  require_condition(
    r.each_index.all? { |index| r[index] > 0 || p[index] == 0 },
    "support constraint"
  )
end

def objectives(raw, p)
  r = normalize(raw)
  validate_lottery(p, r.length)
  r.each_index.map do |winner|
    dispersion = edges(r.length)
      .reject { |i, j| i == winner || j == winner }
      .map { |i, j| (r[j] * p[i] - r[i] * p[j]).abs }
      .sum
    1 - p[winner] + dispersion
  end
end

def reduced_regret(raw, p)
  objectives(raw, p).max / 4
end

def endpoint_values(r, mask)
  k = r.length
  q = Array.new(k) { Array.new(k, Rational(1, 2)) }
  edges(k).each_with_index do |(i, j), edge_index|
    q[i][j] = ((mask >> edge_index) & 1) == 1 ? Rational(3, 4) : Rational(1, 4)
    q[j][i] = 1 - q[i][j]
  end
  (0...k).map do |i|
    (0...k).map { |j| r[j] * q[i][j] }.sum
  end
end

def raw_endpoint_regret(raw, p)
  r = normalize(raw)
  validate_lottery(p, r.length)
  worst = Rational(0)
  (0...(2**edges(r.length).length)).each do |mask|
    values = endpoint_values(r, mask)
    regret = values.max - values.each_index.map { |i| p[i] * values[i] }.sum
    worst = [worst, regret].max
  end
  worst
end

def segment_info(raw)
  r = normalize(raw)
  order = r.each_index.sort_by { |index| [r[index], index] }
  first, second, third = order.first(3)
  a, b, g = r[first], r[second], r[third]
  {
    r: r,
    order: order,
    first: first,
    second: second,
    a: a,
    b: b,
    g: g,
    h_min: Rational(0),
    h_max: (g - b) / 2,
    value: (2 - a - b) / 8
  }
end

def segment_lottery(raw, h)
  info = segment_info(raw)
  r = info[:r]
  first, second = info[:first], info[:second]
  a, b = info[:a], info[:b]
  complement = 1 - a - b
  p = Array.new(r.length, Rational(0))
  p[first] = (a + b) / 2 + h
  p[second] = b * (2 - a - b) / (2 * (1 - a)) + (1 - b) * h / (1 - a)
  multiplier = (2 - a - b) / (1 - a) * (Rational(1, 2) - h / complement)
  r.each_index do |index|
    p[index] = r[index] * multiplier unless [first, second].include?(index)
  end
  validate_lottery(p, r.length)
  p
end

def canonical_cases
  rows = []
  (3..6).each do |k|
    (1...k).each do |support|
      [1, 2, 3, 4].repeated_combination(support) do |positive|
        rows << Array.new(k - support, Rational(0)) + positive.map { |value| Rational(value) }
      end
    end
  end
  rows
end

def distinct_permutations(raw)
  raw.permutation.to_a.uniq
end

def compositions(total, parts, prefix = [], output = [])
  if parts == 1
    output << (prefix + [total])
    return output
  end
  (0..total).each do |first|
    compositions(total - first, parts - 1, prefix + [first], output)
  end
  output
end

def support_grid(raw, denominator)
  r = normalize(raw)
  support = r.each_index.select { |index| r[index] > 0 }
  compositions(denominator, support.length).map do |composition|
    p = Array.new(r.length, Rational(0))
    support.each_with_index do |index, offset|
      p[index] = Rational(composition[offset], denominator)
    end
    p
  end
end

def support_dispersion(raw, p)
  r = normalize(raw)
  support = r.each_index.select { |index| r[index] > 0 }
  support.combination(2).map { |i, j| (r[j] * p[i] - r[i] * p[j]).abs }.sum
end

def build
  require_condition(sha256(PROTOCOL) == EXPECTED_PROTOCOL, "protocol drift")
  require_condition(sha256(PRODUCER) == EXPECTED_PRODUCER, "producer drift")
  producer = JSON.parse(File.read(PRODUCER))
  require_condition(
    producer["classification"] == "support_constraint_creates_boundary_value_jump",
    "producer classification"
  )

  cases = canonical_cases
  require_condition(cases.length == 242, "case count")
  by_zero = Hash.new(0)
  by_support = Hash.new(0)
  raw_count = 0
  permutation_count = 0
  grid_count = 0
  grid_equalities = 0
  proof_checks = 0
  one_zero_cases = 0
  two_zero_face_collapses = 0
  many_zero_unchanged = 0
  limit_rows = 0
  interior_checks = 0

  cases.each do |raw|
    r = normalize(raw)
    zero_indices = r.each_index.select { |index| r[index] == 0 }
    zero_count = zero_indices.length
    support_size = r.length - zero_count
    by_zero[zero_count] += 1
    by_support[support_size] += 1
    validate_support(raw, r)

    f = objectives(raw, r)
    zero_indices.each do |zero|
      require_condition(f[zero] == 1 + support_dispersion(raw, r), "zero-winner identity")
    end
    require_condition(support_dispersion(raw, r) == 0, "reference dispersion")
    require_condition(f.max == 1, "attained bracket value")
    require_condition(reduced_regret(raw, r) == Rational(1, 4), "boundary value")
    proof_checks += 1

    if raw.length <= 5
      require_condition(raw_endpoint_regret(raw, r) == Rational(1, 4), "raw oracle")
      raw_count += 1
      support_grid(raw, 8).each do |p|
        validate_support(raw, p)
        regret = reduced_regret(raw, p)
        require_condition(regret >= Rational(1, 4), "grid lower value")
        if regret == Rational(1, 4)
          require_condition(p == r, "second grid optimizer")
          grid_equalities += 1
        end
        grid_count += 1
      end
    end

    distinct_permutations(raw).each do |permuted|
      permuted_r = normalize(permuted)
      validate_support(permuted, permuted_r)
      require_condition(
        reduced_regret(permuted, permuted_r) == Rational(1, 4),
        "label dependence"
      )
      permutation_count += 1
    end

    unrestricted = segment_info(raw)
    if zero_count == 1
      b = r.sort[1]
      gap = Rational(1, 4) - unrestricted[:value]
      require_condition(gap == b / 8 && gap > 0, "one-zero value gap")
      [unrestricted[:h_min], unrestricted[:h_max]].uniq.each do |h|
        p = segment_lottery(raw, h)
        require_condition(p[zero_indices.first] > 0, "H212 endpoint became feasible")
      end
      positive = r.select { |value| value > 0 }
      [Rational(1, 10), Rational(1, 100), Rational(1, 1000), Rational(1, 10_000)].each do |epsilon|
        interior = [epsilon] + positive.map { |value| (1 - epsilon) * value }
        next if epsilon > interior.drop(1).min
        limit = (2 - b) / 8
        require_condition(
          (segment_info(interior)[:value] - limit).abs <= epsilon / 4,
          "one-zero interior limit"
        )
        limit_rows += 1
      end
      one_zero_cases += 1
    elsif zero_count == 2
      require_condition(unrestricted[:value] == Rational(1, 4), "two-zero value")
      require_condition(unrestricted[:h_max] > 0, "two-zero face")
      require_condition(segment_lottery(raw, Rational(0)) == r, "h=0 endpoint")
      two_zero_face_collapses += 1
    else
      require_condition(unrestricted[:value] == Rational(1, 4), "many-zero value")
      require_condition(unrestricted[:h_max] == 0, "many-zero face changed")
      require_condition(segment_lottery(raw, Rational(0)) == r, "many-zero optimizer")
      many_zero_unchanged += 1
    end
  end

  [
    [1, 1, 1],
    [1, 2, 3],
    [1, 2, 3, 4],
    [1, 3, 3, 3],
    [1, 1, 2, 4],
    [1, 2, 2, 5, 7]
  ].each do |integers|
    raw = integers.map { |value| Rational(value) }
    info = segment_info(raw)
    [info[:h_min], info[:h_max]].uniq.each do |h|
      require_condition(reduced_regret(raw, segment_lottery(raw, h)) == info[:value], "interior parity")
      interior_checks += 1
    end
  end

  require_condition(raw_count == 117, "raw count")
  require_condition(permutation_count == 14_056, "permutation count")
  require_condition(grid_count == 7_857, "grid count")
  require_condition(grid_equalities == 42, "grid equality count")
  require_condition(limit_rows == 453, "limit row count")
  require_condition(one_zero_cases == 121, "one-zero count")
  require_condition(two_zero_face_collapses == 69, "two-zero count")
  require_condition(many_zero_unchanged == 52, "many-zero count")

  attacks = [
    {
      "attack" => "support_constrained_value_below_one_quarter",
      "disposition" => "rejected",
      "evidence" => "#{grid_count} exact restricted-grid lotteries plus zero-winner proof"
    },
    {
      "attack" => "second_support_constrained_optimizer",
      "disposition" => "rejected",
      "evidence" => "#{grid_equalities} exact grid equalities, all p=r, plus equality proof"
    },
    {
      "attack" => "exactly_one_zero_changes_face_only",
      "disposition" => "rejected",
      "evidence" => "#{one_zero_cases} exact positive gaps and infeasible H212 endpoints"
    },
    {
      "attack" => "exactly_two_zeros_raise_value",
      "disposition" => "rejected",
      "evidence" => "#{two_zero_face_collapses} value-equal face collapses to h=0"
    },
    {
      "attack" => "three_or_more_zeros_change_h212",
      "disposition" => "rejected",
      "evidence" => "#{many_zero_unchanged} cases already unique at p=r"
    },
    {
      "attack" => "raw_reduction_fails_under_support_constraint",
      "disposition" => "rejected",
      "evidence" => "#{raw_count} exact raw endpoint comparisons"
    },
    {
      "attack" => "label_dependence",
      "disposition" => "rejected",
      "evidence" => "#{permutation_count} distinct label permutations"
    }
  ]

  {
    "schema" => "h213-support-constrained-zero-reference-boundary-independent-challenge-v1",
    "protocol_sha256" => EXPECTED_PROTOCOL,
    "producer_result_sha256" => EXPECTED_PRODUCER,
    "implementation" => "independent Ruby Rational arithmetic",
    "ruby_version" => RUBY_VERSION,
    "imports_or_executes_producer" => false,
    "classification" => "support_constraint_creates_boundary_value_jump",
    "theorem" => {
      "any_nonempty_zero_set_value" => "1/4",
      "complete_optimizer" => "p=r, unique",
      "exactly_one_zero_gap" => "r_(2)/8",
      "exactly_two_zeros" => "value unchanged; H212 face collapses to h=0",
      "at_least_three_zeros" => "no H212 value or optimizer change"
    },
    "exact_case_census" => {
      "canonical_cases" => cases.length,
      "by_zero_count" => by_zero.sort.to_h.transform_keys(&:to_s),
      "by_positive_support_size" => by_support.sort.to_h.transform_keys(&:to_s),
      "proof_identity_checks" => proof_checks,
      "positive_interior_endpoint_checks" => interior_checks,
      "raw_endpoint_oracle_cases_k_le_5" => raw_count,
      "distinct_label_permutations" => permutation_count,
      "support_grid_lotteries_k_le_5_denominator_8" => grid_count,
      "grid_equalities_at_unique_optimizer" => grid_equalities,
      "accepted_exactly_one_zero_limit_rows" => limit_rows
    },
    "exact_derivation" => [
      "For any zero-reference winner z, support-constrained p gives F_z=1+D_r(p)>=1.",
      "The reference lottery p=r is feasible, has D_r(p)=0, and makes every F_w<=1.",
      "Equality forces p proportional to r on positive support; normalization gives p=r uniquely.",
      "For exactly one zero, H212's unrestricted value is (2-r_(2))/8, so exclusion adds r_(2)/8."
    ],
    "attacks" => attacks,
    "producer_agreement" => {
      "classification" => true,
      "case_count" => producer.dig("exact_case_census", "canonical_cases") == cases.length,
      "raw_count" => producer.dig("exact_case_census", "raw_endpoint_oracle_cases_k_le_5") == raw_count,
      "permutation_count" => producer.dig("exact_case_census", "distinct_label_permutations") == permutation_count,
      "grid_count" => producer.dig("exact_case_census", "support_grid_lotteries_k_le_5_denominator_8") == grid_count,
      "limit_count" => producer.dig("exact_case_census", "accepted_exactly_one_zero_limit_rows") == limit_rows
    },
    "scope" => "one hard p_i=0 when r_i=0 constraint under the H212 full-edge-box model"
  }
end

def main
  require_condition(ARGV.length == 1 && ["--write", "--check"].include?(ARGV[0]), "choose --write or --check")
  result = build
  if ARGV[0] == "--check"
    retained = JSON.parse(File.read(OUTPUT))
    require_condition(retained == result, "challenge result drift")
  else
    File.write(OUTPUT, JSON.pretty_generate(result) + "\n")
  end
end

main
