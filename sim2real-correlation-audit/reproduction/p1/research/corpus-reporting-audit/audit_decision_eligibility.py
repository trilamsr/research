"""Generate the eligibility-complete paper-level decision-case ledger."""

from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
GRID = HERE / "result-estimand-grid.csv"
REVERSAL = HERE.parent / "decision-validity" / "result-reversal-evidence.json"
REAL2SIM = HERE.parent / "claim-evidence-synthesis" / "result-paper-evidence.json"
DEFAULT_OUT = HERE / "result-decision-eligibility.csv"


EXCLUSIONS = {
    "SimFoundry": (
        "ineligible_unreconstructable_estimand",
        "The headline averages task-level correlations with different candidate rosters; "
        "no common candidate-level decision matrix is publicly recoverable.",
    ),
    "PolaRiS": (
        "ineligible_unreconstructable_estimand",
        "The point cloud is only partially recoverable and the source-specific "
        "per-environment estimator needed for a common decision is unavailable.",
    ),
    "SC3-Eval": (
        "ineligible_unrecoverable_matrix",
        "The plotted markers are too occluded to deconflict into a complete candidate matrix, "
        "and no authoritative result matrix is released.",
    ),
    "DreamDojo": (
        "ineligible_no_common_roster",
        "The recovered headline panel follows checkpoints of one policy training lineage "
        "rather than at least two candidate policies on a common decision roster.",
    ),
    "dWorldEval": (
        "ineligible_unrecoverable_matrix",
        "Only a partial headline panel is recoverable; the complete policy-by-task candidate "
        "matrix and identities are not available.",
    ),
    "PlayWorld": (
        "ineligible_unrecoverable_matrix",
        "Heavy marker occlusion prevents a complete candidate-level reconstruction, and no "
        "authoritative result matrix is released.",
    ),
    "Colosseum V2": (
        "ineligible_no_common_roster",
        "The headline association varies perturbation conditions for one fixed policy and "
        "does not define a multi-policy candidate decision.",
    ),
    "VISER": (
        "ineligible_unreconstructable_estimand",
        "The component correlations use different task rosters for fixed policies; they do "
        "not supply a common policy-candidate matrix for winner comparison.",
    ),
}


def corpus_papers() -> list[str]:
    with GRID.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    papers: list[str] = []
    for row in rows:
        if row["paper"] not in papers:
            papers.append(row["paper"])
    return papers


def build_rows() -> list[dict[str, str]]:
    reversal = json.loads(REVERSAL.read_text(encoding="utf-8"))
    reversal_papers = set(reversal)
    rows: list[dict[str, str]] = []

    for paper in corpus_papers():
        if paper == "real2sim-eval":
            status = "eligible_numeric"
            reason = (
                "The tie-complete paper-evidence result enumerates every maximizing "
                "checkpoint combination and identifies possible and necessary policy "
                "winner sets under every declared checkpoint-collapse rule."
            )
            output = (
                "research/claim-evidence-synthesis/"
                "result-paper-evidence.json#checkpoint_selection"
            )
        elif paper == "A Practical Recipe":
            status = "eligible_rank_only"
            reason = (
                "Eleven printed real/sim rank panels identify top-1 agreement, but absolute "
                "policy outcomes and displayed-real regret are unavailable."
            )
            output = "research/decision-validity/result-reversal-evidence.json#A Practical Recipe"
        elif paper in reversal_papers:
            status = "eligible_numeric"
            reason = (
                "The retained source record supplies a common candidate roster with real and "
                "simulated/evaluator values sufficient for winner and regret calculation."
            )
            output = f"research/decision-validity/result-reversal-evidence.json#{paper}"
        else:
            status, reason = EXCLUSIONS[paper]
            output = ""

        rows.append(
            {
                "paper": paper,
                "eligibility_status": status,
                "reason": reason,
                "canonical_decision_output": output,
                "scope_note": (
                    "Outcome-exposed completeness accounting within the frozen 26-paper corpus; "
                    "not a prevalence or calibration sample."
                ),
            }
        )
    return rows


def render_csv(rows: list[dict[str, str]]) -> str:
    buffer = io.StringIO(newline="")
    fields = [
        "paper",
        "eligibility_status",
        "reason",
        "canonical_decision_output",
        "scope_note",
    ]
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = render_csv(build_rows())
    if args.check:
        if not args.out.exists() or args.out.read_text(encoding="utf-8") != rendered:
            raise SystemExit("decision eligibility ledger is stale")
        print("decision eligibility ledger matches canonical output")
        return
    args.out.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
