PYTHON ?= python3.12
PY := .venv/bin/python
PIP := .venv/bin/pip
FAMILY := research/prospective-study-design
METRO := research/evaluator-metrology

.PHONY: install verify verify-h251-roboarena sources verify-sources verify-h202-sources pdf clean

install:
	$(PYTHON) -m venv .venv
	$(PIP) install -q -r requirements.txt

verify:
	@$(PY) -c 'import numpy, scipy, sys; actual=(sys.version_info[:2], numpy.__version__, scipy.__version__); expected=((3, 12), "2.0.2", "1.13.1"); sys.exit(0) if actual == expected else sys.exit(f"requires Python 3.12, numpy 2.0.2, scipy 1.13.1; found {actual}")'
	$(PY) verify_manifest.py
	@test "$$(node --version)" = "v26.5.0"
	@test "$$(ruby -e 'print RUBY_VERSION')" = "2.6.10"
	$(PY) -m pytest -q \
		$(FAMILY)/test_pair_first_common_context_identification.py \
		$(FAMILY)/test_pair_conditioned_operational_target.py \
		$(FAMILY)/test_audit_h167_public_pair_routing_applicability.py \
		$(FAMILY)/test_target_bound_site_feasibility_repair.py \
		$(FAMILY)/test_validate_h179_cross_system_action_order.py \
		$(FAMILY)/test_pair_first_arbitrary_roster_identification.py \
		$(FAMILY)/test_full_roster_edge_box_minimax.py \
		$(FAMILY)/test_audit_h187_phail_context_support.py \
		$(FAMILY)/test_weighted_edge_box_minimax.py \
		$(FAMILY)/test_audit_h189_phail_initial_item_count_support.py \
		$(FAMILY)/test_audit_h190_phail_session_artifact_paths.py \
		$(FAMILY)/test_audit_h191_phail_time_partition_sensitivity.py \
		$(FAMILY)/test_audit_h193_phail_lifecycle_keys.py \
		$(FAMILY)/test_audit_h195_phail_session_identity_recording_trace.py \
		$(FAMILY)/test_audit_h198_current_phail_lifecycle_binding.py \
		$(FAMILY)/test_audit_h199_phail_randomized_home_target.py \
		$(FAMILY)/test_audit_h200_phail_home_field_keys.py \
		$(FAMILY)/test_audit_h201_phail_home_field_semantics.py \
		$(FAMILY)/test_acquire_h202_phail_initial_joint_state.py \
		$(FAMILY)/test_audit_h202_phail_initial_joint_state.py \
		$(FAMILY)/test_challenge_h202_phail_initial_joint_state.py \
		$(FAMILY)/test_audit_h203_phail_first_state_temporal_structure.py \
		$(FAMILY)/test_audit_h204_phail_first_state_group_balance.py \
		$(FAMILY)/test_audit_h205_phail_first_state_uniform_independence.py \
		$(FAMILY)/test_audit_h206_phail_monotonic_wall_clock_bridge.py \
		$(FAMILY)/test_audit_h207_phail_clock_regime_temporal_structure.py \
		$(FAMILY)/test_validate_h207_phail_clock_regime_temporal_structure_challenge.py \
		$(FAMILY)/test_audit_h208_phail_clock_regime_date_identifiability.py \
		$(FAMILY)/test_validate_h208_phail_clock_regime_date_identifiability_challenge.py \
		$(FAMILY)/test_audit_h209_phail_within_regime_policy_sequence.py \
		$(FAMILY)/test_validate_h209_phail_within_regime_policy_sequence_challenge.py \
		$(FAMILY)/test_audit_h210_phail_within_date_policy_sequence.py \
		$(FAMILY)/test_validate_h210_phail_within_date_policy_sequence_challenge.py \
		$(FAMILY)/test_audit_h212_zero_reference_weight_edge_box_boundary.py \
		$(FAMILY)/test_validate_h212_zero_reference_weight_edge_box_boundary_challenge.py \
		$(FAMILY)/test_audit_h213_support_constrained_zero_reference_boundary.py \
		$(FAMILY)/test_validate_h213_support_constrained_zero_reference_boundary_challenge.py \
		$(FAMILY)/test_shared_binary_success_sensitivity.py \
		$(FAMILY)/test_edge_box_objective_comparison.py \
		$(FAMILY)/test_route_colored_shared_success.py \
		$(FAMILY)/test_route_graph_repair_design.py \
		$(FAMILY)/test_finite_sample_route_graph.py \
		$(FAMILY)/test_challenge_h250_finite_sample_route_graph.py \
		$(FAMILY)/test_analyze_h251_three_source_records.py \
		$(FAMILY)/test_interior_route_law_nonidentification.py \
		$(FAMILY)/test_validate_h238_interior_route_law_nonidentification_challenge.py \
		$(METRO)/test_audit_h224_armnetbench_paper_design.py \
		$(METRO)/test_validate_h224_armnetbench_paper_design_challenge.py
	$(PY) $(FAMILY)/pair_first_common_context_identification.py --check
	@mkdir -p work/verification
	node $(FAMILY)/challenge_h152_pair_first_identification.mjs \
		--protocol $(FAMILY)/protocol-h151-pair-first-common-context-identification.md \
		--out work/verification/h152.json
	$(PY) $(FAMILY)/validate_h152_pair_first_identification_challenge.py \
		--result work/verification/h152.json
	$(PY) $(FAMILY)/pair_conditioned_operational_target.py --check
	node $(FAMILY)/challenge_h166_pair_conditioned_operational_target.mjs --check
	$(PY) $(FAMILY)/validate_h166_pair_conditioned_operational_target.py
	$(PY) $(FAMILY)/audit_h167_public_pair_routing_applicability.py --check
	node $(FAMILY)/challenge_h168_public_pair_routing_applicability.mjs --check
	$(PY) $(FAMILY)/validate_h168_public_pair_routing_applicability.py
	$(PY) $(FAMILY)/target_bound_site_feasibility_repair.py --check
	node $(FAMILY)/challenge_h171_target_bound_site_feasibility_repair.mjs --check
	$(PY) $(FAMILY)/validate_h171_target_bound_site_feasibility_repair.py
	$(PY) $(FAMILY)/validate_h179_cross_system_action_order.py
	$(PY) $(FAMILY)/pair_first_arbitrary_roster_identification.py --check
	$(PY) $(FAMILY)/full_roster_edge_box_minimax.py --check
	$(PY) $(FAMILY)/audit_h187_phail_context_support.py --check
	$(PY) $(FAMILY)/weighted_edge_box_minimax.py --check
	$(PY) $(FAMILY)/audit_h189_phail_initial_item_count_support.py --check
	$(PY) $(FAMILY)/audit_h190_phail_session_artifact_paths.py --check
	$(PY) $(FAMILY)/audit_h191_phail_time_partition_sensitivity.py --check
	$(PY) $(FAMILY)/audit_h195_phail_session_identity_recording_trace.py --check
	$(PY) $(FAMILY)/verify_p2_safe_projections.py
	$(PY) $(FAMILY)/validate_h196_positronic_session_identity_history_challenge.py
	$(PY) $(FAMILY)/audit_h198_current_phail_lifecycle_binding.py --check
	node $(FAMILY)/challenge_h198_current_phail_lifecycle_binding.mjs --check
	$(PY) $(FAMILY)/validate_h198_current_phail_lifecycle_binding_challenge.py
	$(PY) $(FAMILY)/audit_h199_phail_randomized_home_target.py --check
	node $(FAMILY)/challenge_h199_phail_randomized_home_target.mjs --check
	$(PY) $(FAMILY)/validate_h199_phail_randomized_home_target_challenge.py
	$(PY) $(FAMILY)/audit_h200_phail_home_field_keys.py --offline-projection-check
	node $(FAMILY)/challenge_h200_phail_home_field_keys.mjs --check
	$(PY) $(FAMILY)/validate_h200_phail_home_field_keys_challenge.py
	$(PY) $(FAMILY)/audit_h201_phail_home_field_semantics.py --check
	node $(FAMILY)/challenge_h201_phail_home_field_semantics.mjs --check
	$(PY) $(FAMILY)/validate_h201_phail_home_field_semantics_challenge.py
	$(PY) $(FAMILY)/audit_h202_phail_initial_joint_state.py --check \
		--repository vendor/positronic-v0.2.1
	$(PY) $(FAMILY)/audit_h203_phail_first_state_temporal_structure.py --check
	node $(FAMILY)/challenge_h203_phail_first_state_temporal_structure.mjs --check
	$(PY) $(FAMILY)/validate_h203_phail_first_state_temporal_structure_challenge.py
	$(PY) $(FAMILY)/audit_h204_phail_first_state_group_balance.py --check
	$(PY) $(FAMILY)/validate_h204_phail_first_state_group_balance_challenge.py
	$(PY) $(FAMILY)/audit_h205_phail_first_state_uniform_independence.py --check
	$(PY) $(FAMILY)/validate_h205_phail_first_state_uniform_independence_challenge.py
	$(PY) $(FAMILY)/audit_h206_phail_monotonic_wall_clock_bridge.py --check \
		--repository vendor/positronic-v0.2.1
	node $(FAMILY)/challenge_h206_phail_monotonic_wall_clock_bridge.mjs --check \
		--repository vendor/positronic-v0.2.1
	$(PY) $(FAMILY)/validate_h206_phail_monotonic_wall_clock_bridge_challenge.py
	$(PY) $(FAMILY)/audit_h207_phail_clock_regime_temporal_structure.py --check
	node $(FAMILY)/challenge_h207_phail_clock_regime_temporal_structure.mjs --check
	$(PY) $(FAMILY)/validate_h207_phail_clock_regime_temporal_structure_challenge.py
	$(PY) $(FAMILY)/audit_h208_phail_clock_regime_date_identifiability.py --check
	ruby $(FAMILY)/challenge_h208_phail_clock_regime_date_identifiability.rb --check
	$(PY) $(FAMILY)/validate_h208_phail_clock_regime_date_identifiability_challenge.py
	$(PY) $(FAMILY)/audit_h209_phail_within_regime_policy_sequence.py --check
	node $(FAMILY)/challenge_h209_phail_within_regime_policy_sequence.mjs --check
	$(PY) $(FAMILY)/validate_h209_phail_within_regime_policy_sequence_challenge.py
	$(PY) $(FAMILY)/audit_h210_phail_within_date_policy_sequence.py --check
	node $(FAMILY)/challenge_h210_phail_within_date_policy_sequence.mjs --check
	$(PY) $(FAMILY)/validate_h210_phail_within_date_policy_sequence_challenge.py
	$(PY) $(FAMILY)/audit_h212_zero_reference_weight_edge_box_boundary.py --check
	node $(FAMILY)/challenge_h212_zero_reference_weight_edge_box_boundary.mjs --check
	$(PY) $(FAMILY)/validate_h212_zero_reference_weight_edge_box_boundary_challenge.py
	$(PY) $(FAMILY)/audit_h213_support_constrained_zero_reference_boundary.py --check
	ruby $(FAMILY)/challenge_h213_support_constrained_zero_reference_boundary.rb --check
	$(PY) $(FAMILY)/validate_h213_support_constrained_zero_reference_boundary_challenge.py
	$(PY) $(FAMILY)/shared_binary_success_sensitivity.py --check
	node $(FAMILY)/challenge_h231_shared_binary_success_sensitivity.mjs --check
	$(PY) $(FAMILY)/edge_box_objective_comparison.py --check
	node $(FAMILY)/challenge_h232_edge_box_objective_comparison.mjs --check
	$(PY) $(FAMILY)/route_colored_shared_success.py --check
	node $(FAMILY)/challenge_h233_route_colored_shared_success.mjs --check
	$(PY) $(FAMILY)/route_graph_repair_design.py --check
	node $(FAMILY)/challenge_h234_route_graph_repair_design.mjs --check
	$(PY) $(FAMILY)/finite_sample_route_graph.py --check
	$(PY) $(FAMILY)/challenge_h250_finite_sample_route_graph.py --check
	$(PY) $(FAMILY)/interior_route_law_nonidentification.py --check
	node $(FAMILY)/challenge_h238_interior_route_law_nonidentification.mjs --check
	$(PY) $(FAMILY)/validate_h238_interior_route_law_nonidentification_challenge.py
	$(PY) $(METRO)/audit_h224_armnetbench_paper_design.py --check
	node $(METRO)/challenge_h224_armnetbench_paper_design.mjs --self-test
	$(PY) $(METRO)/validate_h224_armnetbench_paper_design_challenge.py
	@echo "ALL OFFLINE DECLARED P2 PACKAGE CHECKS PASSED."

verify-h251-roboarena:
	@test -n "$(ROBOARENA_ROOT)" || (echo "set ROBOARENA_ROOT to the pinned RoboArena snapshot" >&2; exit 2)
	$(PY) $(FAMILY)/analyze_h251_three_source_records.py --check --roboarena-root $(ROBOARENA_ROOT)
	ruby $(FAMILY)/challenge_h251_three_source_records.rb --check --roboarena-root $(ROBOARENA_ROOT)
	@echo "OK: H251 RoboArena-dependent producer and challenge checks passed"

sources:
	$(PY) $(FAMILY)/acquire_p2_h178_bound_pdfs.py --fetch
	$(PY) $(FAMILY)/acquire_h196_positronic_history.py --fetch

verify-sources:
	$(PY) $(FAMILY)/acquire_p2_h178_bound_pdfs.py --check
	$(PY) $(FAMILY)/audit_h178_cross_system_action_order.py --check
	$(PY) -m pytest -q $(FAMILY)/test_audit_h178_cross_system_action_order.py
	node $(FAMILY)/challenge_h179_cross_system_action_order.mjs --check
	$(PY) $(FAMILY)/validate_h179_cross_system_action_order.py
	$(PY) $(FAMILY)/acquire_h196_positronic_history.py --check
	@echo "OK: network-acquired H178 and H196 source bindings passed"

verify-h202-sources:
	$(PY) $(FAMILY)/acquire_h202_phail_initial_joint_state.py --check
	$(PY) $(FAMILY)/challenge_h202_phail_initial_joint_state.py
	$(PY) $(FAMILY)/audit_h202_phail_initial_joint_state.py --check \
		--repository vendor/positronic-v0.2.1
	@echo "OK: H202 public first-state sources and independent challenge passed"

pdf:
	@test "$$(pandoc --version | head -1)" = "pandoc 3.10"
	@test "$$(tectonic --version)" = "Tectonic 0.16.9"
	@test "$$(pdfunite -v 2>&1 | head -1)" = "pdfunite version 26.07.0"
	@mkdir -p work/pdf-rebuild
	pandoc $(FAMILY)/PAPER-identification-to-operation.md \
		-f markdown+tex_math_single_backslash \
		-o work/pdf-rebuild/PAPER-identification-to-operation.pdf \
		--pdf-engine=tectonic -V geometry:margin=1in -V fontsize=10.5pt \
		-V header-includes='\usepackage{{array,longtable}}' \
		-V colorlinks=true
	pandoc $(FAMILY)/SUPPLEMENT-identification-to-operation.md \
		-f markdown+tex_math_single_backslash \
		-o work/pdf-rebuild/SUPPLEMENT-identification-to-operation.pdf \
		--pdf-engine=tectonic -V geometry:margin=1in -V fontsize=10.5pt \
		-V header-includes='\usepackage{{array,longtable}}' \
		-V colorlinks=true
	pdfunite \
		work/pdf-rebuild/PAPER-identification-to-operation.pdf \
		work/pdf-rebuild/SUPPLEMENT-identification-to-operation.pdf \
		work/pdf-rebuild/PAPER-identification-to-operation-with-supplement.pdf
	@for name in PAPER-identification-to-operation SUPPLEMENT-identification-to-operation PAPER-identification-to-operation-with-supplement; do \
		pdftotext output/pdf/$$name.pdf work/pdf-rebuild/$$name.canonical.txt; \
		pdftotext work/pdf-rebuild/$$name.pdf work/pdf-rebuild/$$name.rebuilt.txt; \
		cmp work/pdf-rebuild/$$name.canonical.txt work/pdf-rebuild/$$name.rebuilt.txt; \
	done
	@echo "OK: P2 PDFs rebuild with identical extracted text"

clean:
	rm -rf .venv .pytest_cache work
	find research -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -f \
		$(FAMILY)/sources/h162/autoeval-2503.24278v2.pdf \
		$(FAMILY)/sources/h162/umi-bench-2606.10382v1.pdf \
		$(FAMILY)/sources/h162/robodojo-2607.04434v3.pdf \
		$(FAMILY)/sources/h178/2605.27491v1.pdf \
		$(FAMILY)/sources/h178/2606.10366v1.pdf \
		$(FAMILY)/sources/h178/2607.02642v1.pdf
