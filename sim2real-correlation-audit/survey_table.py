"""Survey reconciliation table and derived counts.

Every row verified against arXiv full text (HTML, and vector-figure PDFs where
text-only was insufficient) on 2026-07-20. Coding rules are PAPER.md section 8.1:
the training run is the independent unit; a checkpoint is not; a task is not a
policy. k is the unit count behind the paper's HEADLINE sim-vs-real correlation.

Run:  python survey_table.py     -> prints every count used in sections 6 and 8.
The paper's numbers are generated from this table, not hand-copied.
"""
from math import comb, factorial

# paper, arxiv, k, k_flag, units_description, uncertainty_on_r, rule_stated, recovered
SURVEY = [
    ("real2sim-eval",    "2511.04665", 4,  None,  "4 policies per task, 3-6 checkpoints each",            None,       False, True),
    ("RoboWorld",        "2607.01060", 8,  None,  "8 open-sourced RoboArena policies",                    "p-values", False, True),
    ("Digital Cousins",  "2604.15805", 4,  None,  "4 architectures x 4 generalization levels",            None,       False, True),
    ("SIMPLER",          "2405.05941", 4,  None,  "6 points from 4 model lineages (3 RT-1 checkpoints)",  None,       False, True),
    # k coded 5 (conservative): headline is a mean of 7 per-task r, k=3 on the three
    # finetuned tasks and k=5 on the four zero-shot tasks; counting it at 3 would
    # overclaim the permutation ceiling against it.
    ("SimFoundry",       "2606.28276", 5,  "3-5", "mean of 7 per-task r; k=3 finetuned, k=5 zero-shot",   None,       True,  True),
    ("WorldGym",         "2506.00613", 3,  "3|17","3 policies x 17 tasks (points are task-policy pairs)", None,       False, True),
    ("RoboSnap",         "2607.06699", 1,  None,  "task finetunes of one pi0.5 family, 10 tasks",         None,       True,  True),
    ("REALM",            "2512.19562", 3,  None,  "3 VLAs (r printed only inside Fig. 5)",                "p<0.001",  False, True),
    ("PolaRiS",          "2512.16881", 4,  None,  "4 policies, pre-specified 1k-step checkpoints",        None,       True,  False),
    ("SC3-Eval",         "2606.18610", 1,  "<=7", "7 checkpoints of one architecture x 3 criteria",       None,       False, False),
    ("WorldEval",        "2505.19017", 4,  None,  "4 policies",                                           None,       False, False),
    ("A Practical Recipe","2606.10366",5,  None,  "5 VLAs, correlations in tables (no scatter)",          None,       False, False),
    ("Cosmos-Surg-dVRK", "2510.16240", 3,  None,  "3 VLA runs x 2 checkpoint stages (half/full)",         "p<0.001",  True,  True),
    ("Gemini/Veo",       "2512.10675", 8,  "8?",  "8 variants of one GROD base; independence unstated",   None,       False, False),
    ("DreamDojo",        "2602.06949", 1,  None,  "checkpoints of one GR00T N1.5 lineage",                None,       False, True),
    ("dWorldEval",       "2604.22152", 1,  "1|3", "checkpoints of one pi0 (LIBERO headline); real-world r spans ~3 architectures", None, False, False),
    ("WEAVER",           "2606.13672", 2,  None,  "base pi0.5 + one finetune (headline is Spearman)",     None,       False, False),
    ("PlayWorld",        "2603.09030", 18, None,  "18 distinct trained policies",                         None,       False, False),
    # Added by the 2026-07-20 completeness search (documented queries; see paper section 8.1).
    ("EmbodiedSplat",    "2509.17430", 2,  "2x4pt","two 4-point correlations (Polycam/DN mesh); 2 base lineages + sibling finetunes; navigation", None, True, False),
    ("MolmoSpaces",      "2602.11337", 4,  "<=4", "8 policy points from 3-4 lineages (CAP family, pi family, Paligemma)", "CIs on R and rho (printed inside figure)", False, True),
    ("Mem-World",        "2606.18960", 2,  None,  "two sibling pi finetunes x 5 tasks = 10 pooled points", "p-values", False, False),
    # Added by the 2026-07-21 pre-submission rerun. Posted 2026-05-26 — missed by the
    # original 2026-07-20 search, found on rerun; included under the same claim-based rule.
    # Hardware correlation is ONE multi-task ACT policy (pi0.5 is sim-only) across
    # perturbation conditions; avg R^2=0.798 (change prediction), avg Spearman=0.916 over
    # 3 tasks; per-task values unprinted; paper lists 5 conditions in IV-C but draws 6 in Fig. 7-8.
    ("Colosseum V2",     "2605.27759", 1,  None,  "one ACT multi-task policy; points are 5-6 perturbation conditions x 3 tasks", None, False, False),
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
    assert n == 22, n

    under10   = [p[0] for p in SURVEY if p[2] < 10]
    no_unc    = [p[0] for p in SURVEY if p[5] is None]
    unstated  = [p[0] for p in SURVEY if not p[6]]
    recovered = [p[0] for p in SURVEY if p[7]]
    k1        = [p[0] for p in SURVEY if p[2] == 1]                 # permutation inapplicable
    perm_fail = [p[0] for p in SURVEY if 2 <= p[2] <= 3]            # min one-sided p = 1/k! > .05
    boot_fail = [p[0] for p in SURVEY if p[2] <= 4]                 # <= C(7,4)=35 atoms
    df_le2    = [p[0] for p in SURVEY if p[2] <= 5]                 # Fisher-z df = k-3 <= 2
    clears    = [p[0] for p in SURVEY if p[2] > 5]

    print(f"surveyed: {n}   excluded: {len(EXCLUDED)}   recovered: {len(recovered)}/{n}")
    print(f"P1 fewer than 10 independent units : {len(under10)}/{n}")
    print(f"P3 no uncertainty on correlation   : {len(no_unc)}/{n}   (report it: {[p[0] for p in SURVEY if p[5]]})")
    print(f"P2 selection rule unstated         : {len(unstated)}/{n} (stated: {[p[0] for p in SURVEY if p[6]]})")
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
