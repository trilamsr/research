from audit_decision_eligibility import build_rows, render_csv


def test_complete_paper_accounting():
    rows = build_rows()
    assert len(rows) == 26
    assert len({row["paper"] for row in rows}) == 26
    assert sum(row["eligibility_status"].startswith("eligible_") for row in rows) == 18
    assert sum(row["eligibility_status"].startswith("ineligible_") for row in rows) == 8


def test_every_disposition_is_explained_and_eligible_rows_link_output():
    for row in build_rows():
        assert row["reason"].strip()
        if row["eligibility_status"].startswith("eligible_"):
            assert row["canonical_decision_output"].strip()
        else:
            assert not row["canonical_decision_output"]


def test_known_boundary_cases():
    by_paper = {row["paper"]: row for row in build_rows()}
    assert by_paper["A Practical Recipe"]["eligibility_status"] == "eligible_rank_only"
    assert by_paper["Colosseum V2"]["eligibility_status"] == "ineligible_no_common_roster"
    assert by_paper["SC3-Eval"]["eligibility_status"] == "ineligible_unrecoverable_matrix"
    assert by_paper["real2sim-eval"]["eligibility_status"] == "eligible_numeric"


def test_render_is_deterministic():
    assert render_csv(build_rows()) == render_csv(build_rows())
