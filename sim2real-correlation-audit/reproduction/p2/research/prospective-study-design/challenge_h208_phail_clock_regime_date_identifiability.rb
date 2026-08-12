#!/usr/bin/env ruby
# Independent H208 challenge using Ruby exact integer/Rational arithmetic.

require "csv"
require "digest"
require "json"

FAMILY = File.expand_path(__dir__)
COHORT = File.join(FAMILY, "result-h187-phail-context-support-sanitized.csv")
H206 = File.join(FAMILY, "projection-h206-phail-clock-offset-regimes.csv")
PRODUCER = File.join(
  FAMILY,
  "result-h208-phail-clock-regime-date-identifiability.json"
)
OUTPUT = File.join(
  FAMILY,
  "result-h208-phail-clock-regime-date-identifiability-independent-challenge.json"
)
EXPECTED = {
  COHORT => "ad43fca1da065a1cb7fd84dfa9afc5691c72ebe12e7f165c68a0050e51e87ebe",
  H206 => "7b7af23688e230325ec69070c8e5cd5523224990d7bc44defbe5b30f12c65529",
  PRODUCER => "df6c42066f26c7bbd69be25d01ef0d72517f2546c0a1d02d129b6fdc8b6981db"
}.freeze

def require_condition(condition, message)
  raise message unless condition
end

def sha256(path)
  Digest::SHA256.file(path).hexdigest
end

def load_join
  EXPECTED.each do |path, digest|
    require_condition(sha256(path) == digest, "input hash: #{File.basename(path)}")
  end
  cohort = CSV.read(COHORT, headers: true)
  clocks = CSV.read(H206, headers: true)
  require_condition(cohort.length == 594, "cohort count")
  require_condition(clocks.length == 594, "clock count")
  cohort_by_id = cohort.to_h { |row| [row["episode_id"], row] }
  require_condition(cohort_by_id.length == 594, "cohort identity")
  require_condition(clocks.map { |row| row["episode_id"] }.uniq.length == 594, "clock identity")
  clocks.map do |clock|
    source = cohort_by_id.fetch(clock["episode_id"])
    %w[policy_model utc_date created_ts_ns].each do |field|
      require_condition(source[field] == clock[field], "#{field} agreement")
    end
    group = Integer(clock["group_1h"])
    require_condition([1, 2].include?(group), "group")
    {
      "episode_id" => clock["episode_id"],
      "policy" => clock["policy_model"],
      "date" => clock["utc_date"],
      "group" => group
    }
  end
end

def exact_alias(rows)
  dates = rows.map { |row| row["date"] }.uniq.sort
  date_regimes = dates.to_h do |date|
    [date, rows.select { |row| row["date"] == date }.map { |row| row["group"] }.uniq.sort]
  end
  regime_two_dates = date_regimes.select { |_date, groups| groups == [2] }.keys.sort
  exact_single = date_regimes.values.all? { |groups| groups.length == 1 }
  exact_reconstruction = rows.all? do |row|
    (row["group"] == 2) == regime_two_dates.include?(row["date"])
  end
  date_rank = dates.length
  augmented_rank = date_rank + (exact_reconstruction ? 0 : 1)
  {
    "date_count" => dates.length,
    "date_regimes" => date_regimes,
    "regime_2_alias_dates" => regime_two_dates,
    "exact_single_regime_per_date" => exact_single,
    "exact_indicator_reconstruction" => exact_reconstruction,
    "date_only_design_rank" => date_rank,
    "date_plus_regime_design_rank" => augmented_rank,
    "rank_increment" => augmented_rank - date_rank
  }
end

def policy_table(rows)
  policies = rows.map { |row| row["policy"] }.uniq.sort
  counts = policies.to_h do |policy|
    [
      policy,
      {
        "1" => rows.count { |row| row["policy"] == policy && row["group"] == 1 },
        "2" => rows.count { |row| row["policy"] == policy && row["group"] == 2 }
      }
    ]
  end
  cells = policies.flat_map { |policy| [counts[policy]["1"], counts[policy]["2"]] }
  {
    "policies" => policies,
    "counts" => counts,
    "all_policy_regime_cells_positive" => cells.all?(&:positive?),
    "minimum_cell_count" => cells.min,
    "maximum_cell_count" => cells.max
  }
end

def metrics(table)
  policies = table["policies"]
  rows = [1, 2].map do |group|
    policies.map { |policy| table["counts"][policy][group.to_s] }
  end
  row_totals = rows.map(&:sum)
  column_totals = policies.each_index.map { |index| rows.sum { |row| row[index] } }
  total = row_totals.sum
  distributions = rows.each_with_index.map do |row, row_index|
    row.map { |count| Rational(count, row_totals[row_index]) }
  end
  tv = distributions[0].zip(distributions[1]).sum do |left, right|
    (left - right).abs
  end / 2
  chi_square = Rational(0, 1)
  rows.each_with_index do |row, row_index|
    row.each_with_index do |observed, column_index|
      expected = Rational(row_totals[row_index] * column_totals[column_index], total)
      chi_square += (Rational(observed, 1) - expected)**2 / expected
    end
  end
  {
    "policy_distribution_total_variation" => tv.to_f,
    "policy_distribution_total_variation_exact" => "#{tv.numerator}/#{tv.denominator}",
    "pearson_chi_square_descriptive" => chi_square.to_f,
    "pearson_chi_square_exact" => "#{chi_square.numerator}/#{chi_square.denominator}",
    "cramers_v" => Math.sqrt(chi_square.to_f / total)
  }
end

def classify(alias_result, table)
  exact_alias = alias_result["exact_single_regime_per_date"] &&
                alias_result["exact_indicator_reconstruction"]
  return "date_aliased_with_complete_policy_regime_support" if exact_alias &&
                                                                  table["all_policy_regime_cells_positive"]
  return "date_aliased_with_policy_regime_support_gap" if exact_alias

  "date_separable_at_utc_day_resolution"
end

def controls
  nested = [
    {"date" => "a", "group" => 1, "policy" => "p"},
    {"date" => "a", "group" => 1, "policy" => "q"},
    {"date" => "b", "group" => 2, "policy" => "p"},
    {"date" => "b", "group" => 2, "policy" => "q"}
  ]
  crossed = [
    {"date" => "a", "group" => 1, "policy" => "p"},
    {"date" => "a", "group" => 2, "policy" => "p"},
    {"date" => "b", "group" => 2, "policy" => "q"}
  ]
  {
    "nested_alias" => exact_alias(nested)["rank_increment"].zero?,
    "crossed_not_alias" => exact_alias(crossed)["rank_increment"] == 1,
    "complete_support" => policy_table(nested)["all_policy_regime_cells_positive"]
  }
end

def build
  challenge_controls = controls
  require_condition(challenge_controls.values.all?, "controls")
  rows = load_join
  alias_result = exact_alias(rows)
  table = policy_table(rows)
  {
    "schema" => "h208-phail-clock-regime-date-identifiability-independent-challenge-v1",
    "target_producer_result_sha256" => sha256(PRODUCER),
    "input_sha256" => {
      "cohort" => sha256(COHORT),
      "h206_projection" => sha256(H206)
    },
    "implementation" => {
      "language" => "Ruby",
      "ruby" => RUBY_VERSION,
      "producer_imported_or_executed" => false,
      "arithmetic" => "exact integer/Rational contingency and alias reconstruction"
    },
    "episode_count" => rows.length,
    "challenge_controls" => challenge_controls,
    "date_alias" => alias_result,
    "policy_regime_support" => table,
    "composition_metrics" => metrics(table),
    "classification" => classify(alias_result, table),
    "sampling_p_value_reported" => false,
    "later_state_or_performance_opened" => false,
    "clock_regime_treated_as_session_or_cause" => false,
    "outcome_analysis_authorized" => false,
    "unresolved_material_concerns" => []
  }
end

candidate = build
serialized = JSON.pretty_generate(candidate) + "\n"
if ARGV.include?("--check")
  require_condition(File.read(OUTPUT) == serialized, "exact challenge rebuild")
  puts "OK: H208 independent Ruby challenge reproduces"
else
  File.write(OUTPUT, serialized)
  puts serialized
end
