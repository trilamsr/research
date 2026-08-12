"""Validate the headline source-claim to audit-decision alignment record."""

from __future__ import annotations

import csv
from pathlib import Path


HERE = Path(__file__).resolve().parent
RECORD = HERE / "result-headline-claim-decision-alignment.csv"

ACTION_CLASSES = {
    "descriptive_association",
    "relative_ranking",
    "policy_screening",
    "policy_selection_or_deployment",
    "real_evaluation_substitution",
}
ALIGNMENTS = {
    "aligned_broad_use_exact_rule_audit_defined",
    "aligned_strong_use_exact_rule_audit_defined",
}
EXPECTED_CASES = {
    "WorldGym",
    "Digital Cousins",
    "SIMPLER Google",
    "Real2Sim T best-sim checkpoint",
    "OSCAR Skeleton",
    "Cosmos-Surg manual",
    "WM-PolicyEval / Cosmos",
    "WM-PolicyEval / IRASim",
}


def read_rows() -> list[dict[str, str]]:
    with RECORD.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate(rows: list[dict[str, str]]) -> None:
    cases = [row["case"] for row in rows]
    if set(cases) != EXPECTED_CASES or len(cases) != len(EXPECTED_CASES):
        raise ValueError("headline alignment record must contain each atlas case exactly once")
    for row in rows:
        if row["strongest_source_action_class"] not in ACTION_CLASSES:
            raise ValueError(f"invalid action class for {row['case']}")
        if row["alignment_disposition"] not in ALIGNMENTS:
            raise ValueError(f"invalid alignment disposition for {row['case']}")
        if row["top1_rule_explicit"] not in {"yes", "no", "unclear"}:
            raise ValueError(f"invalid top-1 status for {row['case']}")
        if not row["source_url"].startswith("https://arxiv.org/abs/"):
            raise ValueError(f"unversioned or non-arXiv source URL for {row['case']}")
        if row["pinned_source_version"] not in row["source_url"]:
            raise ValueError(f"source version mismatch for {row['case']}")
        for field in (
            "source_location",
            "source_claim_summary",
            "p1_decision_origin",
            "companion_metrics",
            "permitted_p1_wording",
            "evidence_status",
        ):
            if not row[field].strip():
                raise ValueError(f"missing {field} for {row['case']}")


def main() -> None:
    rows = read_rows()
    validate(rows)
    print(f"claim-decision alignment record valid: {len(rows)} headline cases")


if __name__ == "__main__":
    main()
