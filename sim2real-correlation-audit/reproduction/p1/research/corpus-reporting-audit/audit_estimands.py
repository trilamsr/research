"""Summarize the estimand-first coding of the full 26-paper corpus.

This script intentionally does not produce a single universal ``k``. It reports
what is supported under fixed-panel, new-policy, new-task, and crossed readings,
shows how permutation resolution changes with the chosen axis, and contrasts
those results with the legacy one-k-per-paper sensitivity table.
"""

from __future__ import annotations

import csv
from math import factorial
from pathlib import Path


ROOT = Path(__file__).resolve().parent
GRID = ROOT / "result-estimand-grid.csv"

INFERENCE = {"supported", "unsupported", "unidentified"}
YES_NO_UNCLEAR = {"yes", "no", "unclear"}


def load_rows(path: Path = GRID) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("estimand grid is empty")

    required = {
        "paper",
        "coefficient_id",
        "arxiv_version",
        "displayed_points",
        "coefficient_axis",
        "finite_panel_description",
        "generalization_axis_stated",
        "target_population_defined",
        "new_policy_inference",
        "new_task_inference",
        "crossed_inference",
        "k_policy",
        "k_task",
        "k_run",
        "k_condition",
        "source_passage",
        "fact_ambiguity",
        "interpretive_note",
        "coder_id",
        "coding_date",
        "judgment_fields",
    }
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")

    seen: set[tuple[str, str]] = set()
    for row in rows:
        paper = row["paper"].strip()
        coefficient = row["coefficient_id"].strip()
        key = (paper, coefficient)
        if not paper or not coefficient or key in seen:
            raise ValueError(f"empty or duplicate paper/coefficient: {key!r}")
        seen.add(key)
        if row["finite_panel_description"] not in YES_NO_UNCLEAR:
            raise ValueError(f"{paper}: invalid finite-panel classification")
        if row["target_population_defined"] not in {"yes", "no"}:
            raise ValueError(f"{paper}: invalid target-population classification")
        for field in ("new_policy_inference", "new_task_inference", "crossed_inference"):
            if row[field] not in INFERENCE:
                raise ValueError(f"{paper}: invalid {field}={row[field]!r}")
        for field in (
            "source_passage",
            "fact_ambiguity",
            "interpretive_note",
            "coder_id",
            "coding_date",
        ):
            if not row[field].strip():
                raise ValueError(f"{paper}/{coefficient}: {field} must be documented")
    return rows


def integer(value: str) -> int | None:
    value = value.strip()
    return int(value) if value.isdigit() else None


def p_floor(k: int) -> float:
    return 1 / factorial(k)


def summarize(rows: list[dict[str, str]]) -> dict[str, object]:
    by_paper: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_paper.setdefault(row["paper"], []).append(row)

    n = len(by_paper)
    summary: dict[str, object] = {
        "papers": n,
        "coefficient_rows": len(rows),
        "finite_panel_defined": sum(
            all(r["finite_panel_description"] == "yes" for r in group)
            for group in by_paper.values()
        ),
        "generalization_axis_named": sum(
            any(r["generalization_axis_stated"] != "no" for r in group)
            for group in by_paper.values()
        ),
        "target_population_defined": sum(
            any(r["target_population_defined"] == "yes" for r in group)
            for group in by_paper.values()
        ),
        "new_policy_supported": sum(
            any(r["new_policy_inference"] == "supported" for r in group)
            for group in by_paper.values()
        ),
        "new_task_supported": sum(
            any(r["new_task_inference"] == "supported" for r in group)
            for group in by_paper.values()
        ),
        "crossed_supported": sum(
            any(r["crossed_inference"] == "supported" for r in group)
            for group in by_paper.values()
        ),
        "printed_p_value": sum(
            any("p-value" in r["uncertainty_on_r"] for r in group)
            for group in by_paper.values()
        ),
        "correlation_interval": sum(
            any("CI" in r["uncertainty_on_r"] for r in group)
            for group in by_paper.values()
        ),
        "any_correlation_uncertainty": sum(
            any(r["uncertainty_on_r"] != "none" for r in group)
            for group in by_paper.values()
        ),
    }
    summary["no_correlation_uncertainty"] = n - summary["any_correlation_uncertainty"]

    conditional = []
    for row in rows:
        if "p-value" not in row["uncertainty_on_r"]:
            continue
        kp, kt = integer(row["k_policy"]), integer(row["k_task"])
        conditional.append(
            {
                "paper": row["paper"],
                "coefficient_id": row["coefficient_id"],
                "k_policy": kp,
                "policy_floor": p_floor(kp) if kp else None,
                "k_task": kt,
                "task_floor": p_floor(kt) if kt else None,
            }
        )
    summary["conditional_permutation_floors"] = conditional

    # This is a comparison to the previous sensitivity convention, not an
    # endorsement of a universal independent-unit count.
    from summarize_corpus import SURVEY

    summary["legacy_universal_k_under_10"] = sum(item[2] < 10 for item in SURVEY)
    summary["legacy_universal_k_over_5"] = sum(item[2] > 5 for item in SURVEY)
    return summary


def main() -> None:
    rows = load_rows()
    result = summarize(rows)
    n = result["papers"]
    print("FULL-CORPUS ESTIMAND AUDIT")
    print(f"papers coded                              : {n}")
    print(f"coefficient structures coded              : {result['coefficient_rows']}")
    print(f"finite-panel coefficient defined          : {result['finite_panel_defined']}/{n}")
    print(f"generalization axis named or implied      : {result['generalization_axis_named']}/{n}")
    print(f"target population/sampling frame defined  : {result['target_population_defined']}/{n}")
    print(f"supports inference to new policies        : {result['new_policy_supported']}/{n}")
    print(f"supports inference to new tasks           : {result['new_task_supported']}/{n}")
    print(f"supports crossed policy/task inference    : {result['crossed_supported']}/{n}")
    print(f"prints a p-value on the coefficient        : {result['printed_p_value']}/{n}")
    print(f"prints a correlation interval              : {result['correlation_interval']}/{n}")
    print(f"prints either                               : {result['any_correlation_uncertainty']}/{n}")
    print(f"prints neither                              : {result['no_correlation_uncertainty']}/{n}")
    print()
    print("COMPARISON WITH LEGACY UNIVERSAL-k SENSITIVITY")
    print(
        "papers coded k<10 under the old convention : "
        f"{result['legacy_universal_k_under_10']}/{n}"
    )
    print(
        "papers coded k>5 under the old convention  : "
        f"{result['legacy_universal_k_over_5']}/{n}"
    )
    print("These are sensitivity counts, not estimand-free inferential verdicts.")
    print()
    print("CONDITIONAL ONE-SIDED FULL-PERMUTATION RESOLUTION")
    print("(combinatorial resolution only; not an exact test result or a universal floor)")
    for item in result["conditional_permutation_floors"]:
        policy = (
            f"k={item['k_policy']}: {item['policy_floor']:.6f}"
            if item["policy_floor"] is not None
            else "not identified"
        )
        task = (
            f"k={item['k_task']}: {item['task_floor']:.6f}"
            if item["task_floor"] is not None
            else "not identified"
        )
        print(
            f"{item['paper']}/{item['coefficient_id']:<28} "
            f"policy blocks {policy}   task blocks {task}"
        )


if __name__ == "__main__":
    main()
