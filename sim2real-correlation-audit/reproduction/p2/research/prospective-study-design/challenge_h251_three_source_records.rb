#!/usr/bin/env ruby
# Method-distinct reconstruction of H251's load-bearing aggregate claims.

require "csv"
require "json"
require "optparse"
require "set"
require "yaml"

family = File.expand_path(__dir__)
project = File.expand_path("../..", family)
sources = File.join(family, "sources", "h251")
options = {
  canonical: File.join(family, "result-h251-three-source-real-record-application.json"),
  output: File.join(family, "result-h251-three-source-real-record-challenge.json"),
  check: false
}
OptionParser.new do |parser|
  parser.on("--roboarena-root PATH") { |value| options[:roboarena_root] = value }
  parser.on("--canonical PATH") { |value| options[:canonical] = value }
  parser.on("--output PATH") { |value| options[:output] = value }
  parser.on("--check") { options[:check] = true }
end.parse!
raise "--roboarena-root is required" unless options[:roboarena_root]

canonical = JSON.parse(File.read(options[:canonical]))
checks = []

def check(checks, name, observed, expected)
  checks << {"name" => name, "observed" => observed, "expected" => expected, "pass" => observed == expected}
end

def graph_components(nodes, edges)
  graph = nodes.to_h { |node| [node, Set.new] }
  edges.each do |edge|
    left, right = edge
    graph.fetch(left).add(right)
    graph.fetch(right).add(left)
  end
  seen = Set.new
  groups = []
  graph.keys.sort.each do |start|
    next if seen.include?(start)
    queue = [start]
    seen.add(start)
    group = []
    until queue.empty?
      node = queue.shift
      group << node
      graph.fetch(node).to_a.sort.each do |neighbor|
        next if seen.include?(neighbor)
        seen.add(neighbor)
        queue << neighbor
      end
    end
    groups << group.sort
  end
  groups.sort_by { |group| [-group.length, group] }
end

def median(values)
  ordered = values.sort
  mid = ordered.length / 2
  ordered.length.odd? ? ordered[mid] : (ordered[mid - 1] + ordered[mid]) / 2.0
end

%w[routing marker square].each do |task|
  source = JSON.parse(File.read(File.join(sources, "ankile", task, "results.json")))
  rollouts = source.fetch("rollouts")
  values = {}
  rollouts.each do |row|
    key = [row.fetch("policy_id"), row.fetch("manifest_idx")]
    raise "duplicate AnkIle key" if values.key?(key)
    values[key] = row.fetch("outcome") == "success" ? 1 : 0
  end
  policy_ids = values.keys.map(&:first).uniq.sort
  state_ids = values.keys.map(&:last).uniq.sort
  successes = policy_ids.to_h { |policy| [policy, state_ids.sum { |state| values.fetch([policy, state]) }] }
  pairs = policy_ids.combination(2).map do |left, right|
    counts = [0, 0, 0]
    state_ids.each do |state|
      a = values.fetch([left, state])
      b = values.fetch([right, state])
      a > b ? counts[0] += 1 : (a == b ? counts[1] += 1 : counts[2] += 1)
    end
    ["#{task}-P#{left}", "#{task}-P#{right}", *counts, (counts[0] + 0.5 * counts[1]) / state_ids.length]
  end
  panel = canonical.fetch("ankile").fetch(task).fetch("released_finite_panel")
  expected_successes = panel.fetch("policy_results").map { |row| row.fetch("successes") }
  expected_pairs = panel.fetch("pair_results").map do |row|
    [row.fetch("left"), row.fetch("right"), row.fetch("left_wins"), row.fetch("ties"), row.fetch("right_wins"), row.fetch("half_credit_score_left")]
  end
  check(checks, "ankile_#{task}_rectangle", [rollouts.length, policy_ids.length, state_ids.length, values.length], [150, 3, 50, 150])
  check(checks, "ankile_#{task}_successes", successes.values, expected_successes)
  check(checks, "ankile_#{task}_pairs", pairs, expected_pairs)
  check(checks, "ankile_#{task}_all_submitted", source.fetch("arena_submitted_round_indices").sort, (0...50).to_a)
end

session_paths = Dir.glob(File.join(options[:roboarena_root], "evaluation_sessions", "*", "metadata.yaml")).sort
nodes = Set.new
edge_counts = Hash.new(0)
set_sizes = Hash.new(0)
session_paths.each do |path|
  row = YAML.safe_load(File.read(path), permitted_classes: [Time])
  policies = row.fetch("policies").values.map { |policy| policy.fetch("policy_name").strip }.uniq.sort
  set_sizes[policies.length] += 1
  policies.each { |policy| nodes.add(policy) }
  policies.combination(2).each { |pair| edge_counts[pair] += 1 }
end
edges = edge_counts.keys.to_set
groups = graph_components(nodes, edges)
paired_nodes = edges.to_a.flatten.to_set
paired_groups = graph_components(paired_nodes, edges)
support = edge_counts.values
robo = canonical.fetch("roboarena")
check(checks, "roboarena_sessions", session_paths.length, robo.fetch("sessions"))
check(checks, "roboarena_set_sizes", set_sizes.transform_keys(&:to_s).sort.to_h, robo.fetch("sessions_by_distinct_policy_count"))
check(checks, "roboarena_nodes_edges", [nodes.length, edges.length, groups.length], [robo.dig("policy_cooccurrence_graph", "policies"), robo.dig("policy_cooccurrence_graph", "observed_edges"), robo.dig("policy_cooccurrence_graph", "components").length])
check(checks, "roboarena_pair_eligible", [paired_nodes.length, paired_groups.length], [robo.dig("policy_cooccurrence_graph", "pair_eligible_policies"), robo.dig("policy_cooccurrence_graph", "pair_eligible_components").length])
check(
  checks,
  "roboarena_support",
  [support.min, median(support), support.max, support.count(1), support.count { |value| value >= 10 }, support.count { |value| value >= 50 }],
  robo.fetch("policy_cooccurrence_graph").fetch("session_support").values_at("minimum", "median", "maximum", "edges_with_one_session", "edges_with_at_least_10_sessions", "edges_with_at_least_50_sessions")
)

tri_root = File.join(sources, "tri", "files")
tri_files = Dir.glob(File.join(tri_root, "*.csv")).sort
tri_counts = Hash.new(0)
tri_files.each do |path|
  CSV.foreach(path, headers: true) do |row|
    tri_counts[:rows] += 1
    tri_counts[:hardware_rows] += 1 if row.fetch("Panel").include?("_HW_")
    n = row.fetch("Num_Rollouts").to_f.to_i
    success_text = row["Success/Failure"].to_s.strip
    progress_text = row["Task_Progress_Results"].to_s.strip
    if !success_text.empty?
      tri_counts[:binary_rows] += 1
      repaired = success_text.end_with?("]'")
      tri_counts[:repairs] += 1 if repaired
      cleaned = repaired ? success_text[0...-1] : success_text
      tokens = cleaned.scan(/\b(?:True|False)\b/)
      observed = tokens.count("True")
      tri_counts[:binary_length_mismatches] += 1 unless tokens.length == n
      tri_counts[:binary_count_mismatches] += 1 unless observed == row.fetch("Num_Successes").to_f.to_i
      rate = n.zero? ? 0.0 : observed.to_f / n
      tri_counts[:binary_rate_mismatches] += 1 unless (rate - row.fetch("Success_Rate").to_f).abs <= 5e-10
    elsif !progress_text.empty?
      tri_counts[:progress_rows] += 1
      values = progress_text.delete_prefix("[").delete_suffix("]").split(",").reject(&:empty?).map(&:to_f)
      bins = row.fetch("Task_Progress_Bins").delete_prefix("[").delete_suffix("]").split(",").reject(&:empty?).map(&:to_f)
      tri_counts[:progress_length_mismatches] += 1 unless values.length == n
      tri_counts[:progress_bin_mismatches] += 1 unless bins.length == row.fetch("Num_Milestones").to_f.to_i + 1
      mean = values.empty? ? 0.0 : values.sum / values.length
      tri_counts[:progress_mean_mismatches] += 1 unless (mean - row.fetch("Avg_Task_Progress").to_f).abs <= 5e-9
    else
      tri_counts[:aggregate_rows] += 1
      successes = row.fetch("Num_Successes").to_f.to_i
      rate = n.zero? ? 0.0 : successes.to_f / n
      tri_counts[:aggregate_rate_mismatches] += 1 unless (rate - row.fetch("Success_Rate").to_f).abs <= 5e-10
    end
  end
end
tri = canonical.fetch("tri")
check(checks, "tri_structure", [tri_files.length, tri_counts[:rows], tri_counts[:hardware_rows], tri_counts[:binary_rows], tri_counts[:progress_rows], tri_counts[:aggregate_rows]], [tri.dig("release_structure", "csv_files"), tri.dig("release_structure", "rows"), tri.dig("release_structure", "hardware_rows"), tri.dig("release_structure", "binary_rows"), tri.dig("release_structure", "progress_rows"), tri.dig("release_structure", "aggregate_only_rows")])
check(checks, "tri_repairs", tri_counts[:repairs], tri.dig("integrity", "trailing_apostrophe_cells_repaired"))
check(checks, "tri_binary_integrity", [tri_counts[:binary_length_mismatches], tri_counts[:binary_count_mismatches], tri_counts[:binary_rate_mismatches]], [tri.dig("integrity", "binary_array_length_mismatches"), tri.dig("integrity", "binary_success_count_mismatches"), tri.dig("integrity", "binary_success_rate_mismatches")])
check(checks, "tri_progress_integrity", [tri_counts[:progress_length_mismatches], tri_counts[:progress_bin_mismatches], tri_counts[:progress_mean_mismatches]], [tri.dig("integrity", "progress_array_length_mismatches"), tri.dig("integrity", "progress_bin_count_mismatches"), tri.dig("integrity", "progress_mean_mismatches")])
check(checks, "tri_aggregate_integrity", tri_counts[:aggregate_rate_mismatches], tri.dig("integrity", "aggregate_only_rate_mismatches"))

result = {
  "schema" => "h251-three-source-real-record-challenge-v1",
  "runtime" => RUBY_DESCRIPTION,
  "method" => "Ruby reconstruction using JSON, Psych YAML, CSV, regular-expression Boolean counts, and an independent graph traversal",
  "canonical_result" => File.expand_path(options[:canonical]).sub(project + "/", ""),
  "checks" => checks,
  "checks_passed" => checks.count { |row| row.fetch("pass") },
  "checks_total" => checks.length,
  "status" => checks.all? { |row| row.fetch("pass") } ? "pass" : "fail",
  "limitations" => [
    "This challenge reconstructs aggregate arithmetic and graph topology, not the external data-generation process.",
    "It does not validate AnkIle reset execution, RoboArena context equivalence, or TRI bundle identity."
  ]
}
rendered = JSON.pretty_generate(result) + "\n"
if options[:check]
  raise "canonical challenge differs from regeneration" unless File.read(options[:output]) == rendered
else
  File.write(options[:output], rendered)
end
puts "OK: H251 method-distinct challenge #{result.fetch('status')} (#{result.fetch('checks_passed')}/#{result.fetch('checks_total')})"
