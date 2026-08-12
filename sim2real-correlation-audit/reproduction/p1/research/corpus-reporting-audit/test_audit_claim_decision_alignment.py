from audit_claim_decision_alignment import read_rows, validate


def test_alignment_record_validates():
    rows = read_rows()
    validate(rows)


def test_all_exact_top1_rules_are_labeled_audit_defined():
    for row in read_rows():
        if row["top1_rule_explicit"] == "no":
            assert "audit-defined" in row["p1_decision_origin"]
            assert "is source-specified" not in row["permitted_p1_wording"]


def test_strong_substitution_cases_are_not_downgraded_to_description():
    by_case = {row["case"]: row for row in read_rows()}
    assert (
        by_case["OSCAR Skeleton"]["strongest_source_action_class"]
        == "real_evaluation_substitution"
    )
    assert (
        by_case["WM-PolicyEval / IRASim"]["strongest_source_action_class"]
        == "real_evaluation_substitution"
    )
    assert (
        by_case["Digital Cousins"]["strongest_source_action_class"]
        == "relative_ranking"
    )
    assert by_case["Cosmos-Surg manual"]["top1_rule_explicit"] == "yes"
    assert "source-matched" in by_case["Cosmos-Surg manual"]["p1_decision_origin"]
