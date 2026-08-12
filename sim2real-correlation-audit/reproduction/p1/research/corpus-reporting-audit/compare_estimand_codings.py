"""Compare the released estimand grid with two preserved blind codings.

The raw coders used different row granularities, so agreement is reported at
paper level as the set of values assigned anywhere in that paper. This avoids
manufacturing row matches between coefficient structures the coders did not
define identically.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCES = ROOT / "sources"
CODINGS = {
    "released": ROOT / "result-estimand-grid.csv",
    "blind-a": SOURCES / "source-estimand-blind-a.csv",
    "blind-b": SOURCES / "source-estimand-blind-b.csv",
}
FIELDS = (
    "uncertainty_on_r",
    "selection_rule",
    "finite_panel_description",
    "generalization_axis_stated",
    "target_population_defined",
    "new_policy_inference",
    "new_task_inference",
    "crossed_inference",
)
PIPE_FIELDS = {"uncertainty_on_r", "generalization_axis_stated"}
SELECTION = {"yes", "no", "partial", "not-applicable"}
INFERENCE = {"supported", "unsupported", "unidentified"}


def load(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"{path} is empty")
    if "paper" not in rows[0]:
        raise ValueError(f"{path} lacks paper column")
    required = {
        "paper",
        "coefficient_id",
        "uncertainty_on_r",
        "selection_rule",
        "finite_panel_description",
        "generalization_axis_stated",
        "target_population_defined",
        "new_policy_inference",
        "new_task_inference",
        "crossed_inference",
        "source_passage",
        "coder_id",
        "coding_date",
        "judgment_fields",
    }
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"{path} lacks columns: {sorted(missing)}")
    version_field = "arxiv_version" if "arxiv_version" in rows[0] else "pinned_arxiv"
    seen: set[tuple[str, str]] = set()
    for row in rows:
        key = (row["paper"].strip(), row["coefficient_id"].strip())
        if not all(key) or key in seen:
            raise ValueError(f"{path}: empty or duplicate paper/coefficient {key!r}")
        seen.add(key)
        if row["selection_rule"] not in SELECTION:
            raise ValueError(f"{path}: invalid selection_rule for {key!r}")
        if row["finite_panel_description"] not in {"yes", "no", "unclear"}:
            raise ValueError(f"{path}: invalid finite_panel_description for {key!r}")
        if row["target_population_defined"] not in {"yes", "no"}:
            raise ValueError(f"{path}: invalid target_population_defined for {key!r}")
        if any(row[field] not in INFERENCE for field in INFERENCE_FIELDS):
            raise ValueError(f"{path}: invalid inference label for {key!r}")
        for field in ("source_passage", "coder_id", "coding_date", version_field):
            if not row[field].strip():
                raise ValueError(f"{path}: empty {field} for {key!r}")
    return rows


INFERENCE_FIELDS = ("new_policy_inference", "new_task_inference", "crossed_inference")


def normalize(field: str, value: str) -> str:
    if field not in PIPE_FIELDS or "|" not in value:
        return value
    return "|".join(sorted(set(part.strip() for part in value.split("|"))))


def paper_sets(rows: list[dict[str, str]], field: str) -> dict[str, tuple[str, ...]]:
    result: dict[str, set[str]] = {}
    for row in rows:
        value = row[field].strip()
        if not value:
            raise ValueError(f"{row['paper']}: empty {field}")
        result.setdefault(row["paper"], set()).add(normalize(field, value))
    return {paper: tuple(sorted(values)) for paper, values in result.items()}


def exact_agreement(left: dict[str, tuple[str, ...]], right: dict[str, tuple[str, ...]]) -> int:
    if set(left) != set(right):
        raise ValueError("paper sets differ")
    return sum(left[paper] == right[paper] for paper in left)


def summarize() -> dict[str, object]:
    rows = {name: load(path) for name, path in CODINGS.items()}
    paper_names = {name: {row["paper"] for row in coding} for name, coding in rows.items()}
    if len({frozenset(names) for names in paper_names.values()}) != 1:
        raise ValueError(f"paper coverage differs: {paper_names}")
    papers = sorted(next(iter(paper_names.values())))
    released_versions = {
        row["paper"]: row["arxiv_version"] for row in rows["released"]
    }
    for name in ("blind-a", "blind-b"):
        for row in rows[name]:
            if row["pinned_arxiv"] != released_versions[row["paper"]]:
                raise ValueError(
                    f"{name}/{row['paper']}: pin {row['pinned_arxiv']} != "
                    f"{released_versions[row['paper']]}"
                )

    details: dict[str, dict[str, dict[str, tuple[str, ...]]]] = {}
    agreements: dict[str, dict[str, int]] = {}
    for field in FIELDS:
        values = {name: paper_sets(coding, field) for name, coding in rows.items()}
        details[field] = {
            paper: {name: values[name][paper] for name in CODINGS} for paper in papers
        }
        agreements[field] = {
            "released_vs_a": exact_agreement(values["released"], values["blind-a"]),
            "released_vs_b": exact_agreement(values["released"], values["blind-b"]),
            "a_vs_b": exact_agreement(values["blind-a"], values["blind-b"]),
            "all_three": sum(
                len({values[name][paper] for name in CODINGS}) == 1 for paper in papers
            ),
        }
    return {
        "rows": {name: len(coding) for name, coding in rows.items()},
        "papers": papers,
        "agreements": agreements,
        "details": details,
    }


def main() -> None:
    result = summarize()
    n = len(result["papers"])
    print("INDEPENDENT ESTIMAND-CODING COMPARISON")
    print("rows:", ", ".join(f"{name}={count}" for name, count in result["rows"].items()))
    print(f"paper coverage: {n}/{n} in every coding")
    print()
    print(
        f"{'field':31} {'released/A':>10} {'released/B':>10} "
        f"{'A/B':>7} {'all 3':>7}"
    )
    for field, counts in result["agreements"].items():
        print(
            f"{field:31} "
            f"{counts['released_vs_a']:>7}/{n:<2} "
            f"{counts['released_vs_b']:>7}/{n:<2} "
            f"{counts['a_vs_b']:>4}/{n:<2} "
            f"{counts['all_three']:>4}/{n:<2}"
        )

    print()
    print("DISAGREEMENTS (paper-level sets; raw row structures remain in the CSVs)")
    for field, papers in result["details"].items():
        disagree = {
            paper: values
            for paper, values in papers.items()
            if len(set(values.values())) > 1
        }
        print(f"\n{field}: {len(disagree)}/{n}")
        for paper, values in disagree.items():
            rendered = "; ".join(
                f"{name}={'|'.join(value)}" for name, value in values.items()
            )
            print(f"  {paper}: {rendered}")


if __name__ == "__main__":
    main()
