from audit_complete_matrix_decisions import build_rows


def test_complete_matrix_set_is_eligibility_complete():
    rows = build_rows()
    assert len(rows) == 19
    assert len({row["panel_id"] for row in rows}) == 19
    assert {
        "REALM/Overall",
        "REALM/Default",
        "REALM/VB-POSE",
        "Mem-World",
        "MolmoSpaces/common-appendix-roster",
        "EmbodiedSplat/mesh-conditions",
    } <= {row["panel_id"] for row in rows}


def test_complete_matrix_outcomes_are_not_balanced_by_selection():
    rows = build_rows()
    assert sum(row["top1_result"] == "correct" for row in rows) == 17
    assert sum(row["top1_result"] == "wrong" for row in rows) == 2
    by_panel = {row["panel_id"]: row for row in rows}
    assert (
        by_panel["Cosmos-Surg-dVRK/automated_fig1b"][
            "all_nonempty_task_subsets_correct"
        ]
        == 5
    )


def test_every_matrix_reports_companion_metric_context_and_rank_result():
    rows = build_rows()
    for row in rows:
        assert row["source_metric_bundle"]
        assert -1 <= float(row["audit_spearman_rho"]) <= 1
        assert row["rule_provenance"] in {
            "audit-defined",
            "source-matched aggregation/action; audit-defined ties/loss",
        }
    cosmos_rows = [
        row for row in rows if row["paper"] == "Cosmos-Surg-dVRK"
    ]
    assert len(cosmos_rows) == 2
    assert all(row["rule_provenance"].startswith("source-matched") for row in cosmos_rows)
