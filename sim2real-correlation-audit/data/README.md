# Data — one CSV per source paper

Files are named `survey-<paper>.csv`, one per surveyed paper whose data we recovered. Each was
extracted from a published figure (vector drawing operators where available, pixel reads otherwise)
or transcribed from a printed table, and validated by reproducing a statistic the source paper
printed. Each CSV's header comments record the exact source, extraction method, calibration
residuals, validation gate, and known caveats. Full methodology: `../README.md`.

| file | source paper (arXiv) | points | validated against |
|---|---|---|---|
| `survey-real2sim-eval-fig3-checkpoints.csv` | real2sim-eval (2511.04665) | 52 — 3 tasks × 4 policies × 3–6 checkpoints | Table I r to ≤ 0.0004; MMRV exact under §7.2's convention |
| `survey-real2sim-eval-fig9-200ep.csv` | real2sim-eval (2511.04665) | 52 — 200-episode appendix eval | printed r to ≤ 0.00014; whiskers = exact Clopper–Pearson bounds |
| `survey-roboworld.csv` | RoboWorld (2607.01060) | 32 — 4 panels × 8 policies | all four printed r to ≤ 0.0005; independent pixel re-extraction |
| `survey-digital-cousins.csv` | Digital Cousins (2604.15805) | 16 — 4 architectures × 4 levels | printed r = 0.91; exact match to its numeric tables |
| `survey-realm.csv` | REALM (2512.19562) | 77 — 4 panels | panel r to ≤ 0.0038; 3 of 4 printed MMRVs |
| `survey-cosmos-surg-dvrk.csv` | Cosmos-Surg-dVRK (2510.16240) | 48 — 2 panels × 24 | both printed r to ≤ 0.00005 |
| `survey-dreamdojo.csv` | DreamDojo (2602.06949) | 6 — one training lineage | printed r to 0.00035 |
| `survey-molmospaces.csv` | MolmoSpaces (2602.11337) | 24 rows — pick ×2, open, close | printed r to ≤ 0.0027; Spearman exact |
| `survey-robosnap.csv` | RoboSnap (2607.06699) | 10 + the paper's own inline table | as-plotted r = 0.9089 and table r = 0.887 both exact |
| `survey-viser.csv` | VISER (2605.06311) | 9 — Table 5 transcription | all 4 printed r exact; real column traced to SIMPLER + OpenVLA (§8.1) |
| `survey-oscar.csv` | OSCAR (2606.04463) | 7 policies — Fig. 1 bar labels | Pearson +0.852 reproduces (0.8552); ρ/MMRV not jointly reproducible (§8.1) |
| `survey-hi-wm.csv` | Hi-WM (2604.21741) | 12 — Fig. 6a raster extraction | printed r = 0.953, extracted 0.954 |
| `survey-wm-policyeval.csv` | WM-PolicyEval (2511.11520) | 24 — Fig. 6b vector extraction | points exact (drawn lines to 0.0006) but r = 0.719 ≠ printed 0.687 (§8.0) |
| `survey-weaver.csv` | WEAVER (2606.13672) | 30 — 3 vector panels × 10 | all three panels' ρ and r to ≤ 0.002 |
| `survey-worldeval.csv` | WorldEval (2505.19017) | 20 — 5 panels × 4 policies, raster | pooled r = 0.926 vs printed avg r = 0.942 |
| `survey-gemini-veo.csv` | Gemini/Veo (2512.10675) | 8 — pixel-read | Pearson 0.888 = printed 0.88 |
| `survey-embodiedsplat.csv` | EmbodiedSplat (2509.17430) | 8 — pixel-read | Poly Pearson 0.976 / DN 0.866 (the "SRCC" is Pearson, §8.1) |
| `survey-colosseum-v2.csv` | Colosseum V2 (2605.27759) | per-condition arrays from LaTeX source | avg R² 0.798 and avg Spearman 0.916 reproduce exactly |
| `survey-recipe-rankings.csv` | A Practical Recipe (2606.10366) | 11 rank tables | Spearman ρ reproduces exactly from ranks; Pearson not recoverable |

The coordinates are facts recovered from the papers' own published figures; the renderings in those
papers remain theirs. Seven surveyed papers have no full CSV: SC3-Eval and PlayWorld (markers too
heavily occluded to de-conflict), dWorldEval and Mem-World (recoverable only in part), and PolaRiS
(point cloud recovers but its per-environment estimator does not); their in-figure values were
verified by zoom reads and are quoted in the paper. See §3 of `../PAPER.md` for the full
recoverability accounting and the correction to our earlier verdicts.
