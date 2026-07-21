# Data — one CSV per source paper

Every file was vector-extracted from a published figure (PDF drawing operators, not pixels) and
validated by reproducing a statistic the source paper printed. Each CSV's header comments record the
exact source figure, extraction method, calibration residuals, validation gate, and known caveats.
Full methodology: `../README.md`.

| file | source paper (arXiv) | points | validated against |
|---|---|---|---|
| `real2sim-eval-fig3-checkpoints.csv` | real2sim-eval (2511.04665) | 52 — 3 tasks × 4 policies × 3–6 checkpoints | Table I r to ≤ 0.0004; MMRV exact under §7.2's convention |
| `real2sim-eval-fig9-200ep.csv` | real2sim-eval (2511.04665) | 52 — 200-episode appendix eval | printed r to ≤ 0.00014; whiskers = exact Clopper–Pearson bounds |
| `roboworld.csv` | RoboWorld (2607.01060) | 32 — 4 panels × 8 policies | all four printed r to ≤ 0.0005; independent pixel re-extraction |
| `digital-cousins.csv` | Digital Cousins (2604.15805) | 16 — 4 architectures × 4 levels | printed r = 0.91; exact match to its numeric tables |
| `realm.csv` | REALM (2512.19562) | 77 — 4 panels | panel r to ≤ 0.0038; 3 of 4 printed MMRVs |
| `cosmos-surg-dvrk.csv` | Cosmos-Surg-dVRK (2510.16240) | 48 — 2 panels × 24 | both printed r to ≤ 0.00005 |
| `dreamdojo.csv` | DreamDojo (2602.06949) | 6 — one training lineage | printed r to 0.00035 |
| `molmospaces.csv` | MolmoSpaces (2602.11337) | 24 rows — pick ×2, open, close | printed r to ≤ 0.0027; Spearman exact |
| `robosnap.csv` | RoboSnap (2607.06699) | 10 + the paper's own inline table | as-plotted r = 0.9089 and table r = 0.887 both exact |

The coordinates are facts recovered from the papers' own published figures; the renderings in those
papers remain theirs. Raster-only papers (EmbodiedSplat, Mem-World) have no CSV — their in-figure
values were verified by character-level zoom reads and are quoted in the paper, not extracted.
