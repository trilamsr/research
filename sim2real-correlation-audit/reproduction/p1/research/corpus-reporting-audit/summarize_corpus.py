"""Legacy unit-sensitivity table and derived counts.

The legacy ``k`` fields retain PAPER.md section 8.1's policy/lineage-block
sensitivity convention. They are not a universal effective sample size.
Observable uncertainty and selection-rule facts are loaded from the
coefficient-level estimand grid so the two released codings cannot drift.

Run:  python summarize_corpus.py -> prints every count used in sections 6 and 8.
The paper's numbers are generated from this table, not hand-copied.
"""
import csv
from math import comb, factorial
from pathlib import Path

# Historical tuple layout: paper, arxiv, legacy_k, k_flag,
# units_description, obsolete_uncertainty, obsolete_selection, recovered.
# The two obsolete fields are retained only to minimize churn in the legacy
# sensitivity ledger and are always replaced from the estimand grid below.
_LEGACY_SEED = [
    ("real2sim-eval",    "2511.04665", 4,  None,  "4 policies per task, 3-6 checkpoints each",            None,       False, True),
    ("RoboWorld",        "2607.01060", 8,  None,  "8 open-sourced RoboArena policies",                    "p-values", False, True),
    ("Digital Cousins",  "2604.15805", 4,  None,  "4 architectures x 4 generalization levels",            None,       False, True),
    ("SIMPLER",          "2405.05941", 4,  None,  "6 points from 4 model lineages (3 RT-1 checkpoints)",  None,       False, True),
    # k coded 5 (conservative): headline is a mean of 7 per-task r, k=3 on the three
    # finetuned tasks and k=5 on the four zero-shot tasks; counting it at 3 would
    # overclaim the permutation ceiling against it.
    ("SimFoundry",       "2606.28276", 5,  "3-5", "mean of 7 per-task r; k=3 finetuned, k=5 zero-shot",   None,       True,  True),
    ("WorldGym",         "2506.00613", 3,  "3|17","3 policies x 17 tasks (points are task-policy pairs)", "p<0.001",  False, True),
    ("RoboSnap",         "2607.06699", 1,  None,  "task finetunes of one pi0.5 family, 10 tasks",         None,       True,  True),
    ("REALM",            "2512.19562", 3,  None,  "3 VLAs (r printed only inside Fig. 5)",                "p<0.001",  False, True),
    ("PolaRiS",          "2512.16881", 4,  None,  "4 policies, pre-specified 1k-step checkpoints",        None,       True,  False),
    ("SC3-Eval",         "2606.18610", 1,  "<=7", "7 checkpoints of one architecture x 3 criteria",       None,       False, False),
    # Raster-recovered 2026-07-22 (audit-the-auditor): 20 pts (5 tasks x 4 policies) from the
    # muti_task_corr raster; pooled r=0.926 vs printed avg r=0.942. Bonus: the two WorldEval
    # figures plot the same pi0 Bussing-Table real rate at different x (~1.0 vs ~0.83).
    ("WorldEval",        "2505.19017", 4,  None,  "4 policies x 5 tasks = 20 pts",                        None,       False, True),
    ("A Practical Recipe","2606.10366",5,  None,  "5 VLAs, correlations in tables (no scatter)",          None,       False, False),
    ("Cosmos-Surg-dVRK", "2510.16240", 3,  None,  "3 VLA runs x 2 checkpoint stages (half/full)",         "p<0.001",  True,  True),
    # Recovered 2026-07-22 (audit-the-auditor): 8 nominal pts pixel-read, Pearson 0.888 = fig 0.88.
    ("Gemini/Veo",       "2512.10675", 8,  "8?",  "8 variants of one GROD base; independence unstated",   None,       False, True),
    ("DreamDojo",        "2602.06949", 1,  None,  "checkpoints of one GR00T N1.5 lineage",                None,       False, True),
    ("dWorldEval",       "2604.22152", 1,  "1|3", "checkpoints of one pi0 (LIBERO headline); real-world r spans ~3 architectures", None, False, False),
    # k=2 units (2 policies pi0.5 + pi0.5-FT); the headline scatter is 10 points = 5 tasks x 2
    # policies. Vector-recovered 2026-07-21 (audit-the-auditor): all 3 panels reproduce printed
    # rho/r to +-0.002 (WEAVER-FT rho=0.870/r=0.863). Headline 0.870 is Spearman; the body results
    # sentence mislabels it "Pearson" (true Pearson 0.863).
    ("WEAVER",           "2606.13672", 2,  None,  "2 policies (pi0.5, pi0.5-FT) x 5 tasks = 10 pts; headline is Spearman", None, False, True),
    ("PlayWorld",        "2603.09030", 18, None,  "18 distinct trained policies",                         None,       False, False),
    # Added by the 2026-07-20 completeness search (documented queries; see paper section 8.1).
    # Recovered 2026-07-22 (audit-the-auditor): 8 pts pixel-read, Poly Pearson 0.976 / DN 0.866
    # reproduce the printed "SRCC" values -- which are Pearson, not Spearman (rank corr does not match).
    ("EmbodiedSplat",    "2509.17430", 2,  "2x4pt","two 4-point correlations (Polycam/DN mesh); 2 base lineages + sibling finetunes; navigation", None, True, True),
    ("MolmoSpaces",      "2602.11337", 4,  "<=4", "8 policy points from 3-4 lineages (CAP family, pi family, Paligemma)", "CIs on R and rho (printed inside figure)", False, True),
    ("Mem-World",        "2606.18960", 2,  None,  "two sibling pi finetunes x 5 tasks = 10 pooled points", "p-values", False, False),
    # Added by the 2026-07-21 pre-submission rerun. Posted 2026-05-26 — missed by the
    # original 2026-07-20 search, found on rerun; included under the same claim-based rule.
    # Hardware correlation is ONE multi-task ACT policy (pi0.5 is sim-only) across
    # perturbation conditions; avg R^2=0.798 (change prediction), avg Spearman=0.916 over
    # 3 tasks; per-task values unprinted; paper lists 5 conditions in IV-C but draws 6 in Fig. 7-8.
    # Recovered 2026-07-22 (audit-the-auditor): per-task R^2/Spearman arrays live only in the
    # LaTeX source comments; avg R^2 0.798 and avg Spearman 0.916 reproduce exactly. Figs 7-8 draw
    # 6 perturbation conditions though IV-C prose lists 5.
    ("Colosseum V2",     "2605.27759", 1,  None,  "one ACT multi-task policy; points are 5-6 perturbation conditions x 3 tasks", None, False, True),
    # Added by the 2026-07-21 logged Search 3 (protocol:
    # protocol-completeness-search.md; raw hits: sources/log-arxiv-search.txt).
    # Each row was deep-audited from the pinned PDF, with source records
    # retained under sources/ where recovery was possible.
    # VISER headline 0.92 = mean of two per-policy across-task r (Octo 0.9988/4 tasks,
    # OpenVLA 0.8496/5 tasks), each k=1; real side reused verbatim from SIMPLER Table V and
    # OpenVLA App. B without attribution. All four printed r reproduce exactly from Table 5.
    ("VISER",            "2605.06311", 1,  "1|2", "mean of 2 per-policy r over 4-5 tasks; k=1 each (2 lineages)", None, False, True),
    # OSCAR headline = Skeleton row r=+0.852 (front-page Fig. 1); 7 RoboArena policies =
    # 2 lineages (pi0-flow/pi0-FAST + 5 PaliGemma siblings differing only in action
    # representation, per RoboArena 2506.18123). rule_stated: replays recorded leaderboard
    # sessions, so the entering checkpoint is pinned (borderline yes). Pearson reproduces
    # (0.8552); Spearman +0.750 and MMRV 0.571 do not reproduce from published SRs.
    ("OSCAR",            "2606.04463", 2,  "2-7", "7 RoboArena policies from 2 base lineages (2 pi0 + 5 PaliGemma siblings)", None, True, True),
    # Hi-WM r=0.953 pools 3 tasks x 4 policy variants; variants are base+post-trained
    # finetunes of two lineages (pi0, DP). Raster-extracted 12 points reproduce r=0.954.
    # Fig 6a real-axis values contradict its own Table 2 (protocol unstated).
    ("Hi-WM",            "2604.21741", 2,  None,  "3 tasks x 4 variants of 2 lineages (pi0, DP + finetunes); 12 pooled points", None, False, True),
    # WM-PolicyEval: Pearson printed ONLY inside Fig 6b legend; k=3 off-the-shelf policies
    # (Octo-Small, Octo-Base, OpenVLA; recipe-level reading collapses the two Octo sizes
    # to one lineage, hence flag). Vector-extracted 24 points (exact 1/20 grid, drawn OLS
    # lines reproduce to 0.0006) give r=0.719 vs printed 0.687; IRASim legend values
    # irreconcilable with its plotted points (apparent transcription error). recovered=False:
    # data recovered, printed r NOT reproduced.
    ("WM-PolicyEval",    "2511.11520", 3,  "2|3", "3 policies (2 Octo sizes + OpenVLA) x 4 Bridge tasks = 12 points", None, False, False),
]


def _source_facts_from_estimand_grid() -> dict[str, tuple[str, str]]:
    path = Path(__file__).resolve().parent / "result-estimand-grid.csv"
    by_paper: dict[str, dict[str, set[str]]] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            facts = by_paper.setdefault(
                row["paper"], {"uncertainty_on_r": set(), "selection_rule": set()}
            )
            facts["uncertainty_on_r"].add(row["uncertainty_on_r"])
            facts["selection_rule"].add(row["selection_rule"])

    result: dict[str, tuple[str, str]] = {}
    for paper, facts in by_paper.items():
        uncertainty = facts["uncertainty_on_r"]
        selection = facts["selection_rule"]
        if len(uncertainty) != 1 or len(selection) != 1:
            raise ValueError(
                f"{paper}: paper-level source fact is not unique: "
                f"uncertainty={sorted(uncertainty)}, selection={sorted(selection)}"
            )
        result[paper] = (next(iter(uncertainty)), next(iter(selection)))
    return result


_SOURCE_FACTS = _source_facts_from_estimand_grid()
if {row[0] for row in _LEGACY_SEED} != set(_SOURCE_FACTS):
    raise ValueError("legacy survey and estimand grid contain different paper sets")
SURVEY = [
    row[:5] + _SOURCE_FACTS[row[0]] + row[7:]
    for row in _LEGACY_SEED
]

EXCLUDED = [
    ("GSWorld",               "2510.20813", "claims 'strong correlation'; prints no coefficient"),
    ("Interactive World Sim", "2603.08546", "plots a sim-vs-real scatter; prints no coefficient"),
    ("RoboSimGS",             "2510.10637", "reports no sim-vs-real correlation at all"),
    ("Benchmarking audit",    "2606.04233", "benchmark-protocol audit; no sim-real correlation"),
    ("AutoEval",              "2503.24278", "plots SIMPLER-vs-real correlations per task, prints no numeric coefficient; its headline 0.942 is real-to-real (autonomous vs human eval)"),
    # Screened 2026-07-21 (pre-submission rerun).
    ("GigaWorld-1",           "2607.02642", "defines the real-vs-predicted correlation (its Eq. 4) as its central quantity but never prints a value for it; its prose rhos (0.78, 0.88) are video-metric-vs-evaluator-score correlations"),
]

if __name__ == "__main__":
    n = len(SURVEY)
    ks = {p[0]: p[2] for p in SURVEY}
    assert n == 26, n

    under10   = [p[0] for p in SURVEY if p[2] < 10]
    no_unc    = [p[0] for p in SURVEY if p[5] == "none"]
    unstated  = [p[0] for p in SURVEY if p[6] == "no"]
    partial   = [p[0] for p in SURVEY if p[6] == "partial"]
    not_applicable = [p[0] for p in SURVEY if p[6] == "not-applicable"]
    recovered = [p[0] for p in SURVEY if p[7]]
    k1        = [p[0] for p in SURVEY if p[2] == 1]                 # permutation inapplicable
    perm_fail = [p[0] for p in SURVEY if 2 <= p[2] <= 3]            # min one-sided p = 1/k! > .05
    boot_fail = [p[0] for p in SURVEY if p[2] <= 4]                 # <= C(7,4)=35 atoms
    df_le2    = [p[0] for p in SURVEY if p[2] <= 5]                 # Fisher-z df = k-3 <= 2
    clears    = [p[0] for p in SURVEY if p[2] > 5]

    print(f"surveyed: {n}   excluded: {len(EXCLUDED)}   recovered: {len(recovered)}/{n}")
    print(f"fewer than 10 coded units          : {len(under10)}/{n}")
    print(f"no interval/significance on r      : {len(no_unc)}/{n}   (report it: {[p[0] for p in SURVEY if p[5] != 'none']})")
    print(f"selection rule = no                : {len(unstated)}/{n}")
    print(f"   selection rule = partial        : {len(partial)}/{n}  {partial}")
    print(f"   selection rule = not-applicable : {len(not_applicable)}/{n}  {not_applicable}")
    print(f"   selection rule = yes            : {n-len(unstated)-len(partial)-len(not_applicable)}/{n}")
    print(f"permutation inapplicable (k=1)     : {len(k1)}/{n}  {k1}")
    print(f"cannot reach p=.05 (2<=k<=3)       : {len(perm_fail)}/{n}  {perm_fail}  (SimFoundry partial: 3 of 7 tasks at k=3)")
    print(f"bootstrap <=35 atoms (k<=4)        : {len(boot_fail)}/{n}")
    print(f"Fisher-z df<=2 (k<=5)              : {len(df_le2)}/{n}")
    print(f"clears all three (k>5)             : {len(clears)}/{n}  {clears}")
    print()
    for kk in sorted(set(p[2] for p in SURVEY)):
        papers = [p[0] for p in SURVEY if p[2] == kk]
        print(f"k={kk:>2}  ceiling C(2k-1,k)={comb(2*kk-1,kk):>12,}  min one-sided p=1/k!={1/factorial(kk):.4f}  "
              f"mass of all-one-unit draw=1/k^k={100/kk**kk:.7g}%  {papers}")
