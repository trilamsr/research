# Completeness-search record

What survives of the survey's completeness searches, released so the bounded corpus's coverage is auditable.
This file is the record the paper's own standard demands; where the record is incomplete, that is
stated rather than reconstructed.

## Frozen inclusion and exclusion rule

A paper enters when the pinned public report:

1. evaluates robot policies, checkpoints, or policy variants using both a
   simulated/generated evaluator and real-world robot outcomes on an aligned
   displayed panel; and
2. prints a named association coefficient between those evaluator and real
   outcomes, including a coefficient printed only in a figure or appendix.

Task domain and evaluator mechanism are not inclusion criteria. Physics
simulators, learned world models, generated-video evaluators, manipulation, and
navigation may all qualify.

A paper is excluded when the comparison is real-to-real or sim-to-sim only,
concerns reconstruction without a robot-policy evaluation coefficient, lacks
aligned real outcomes, or prints no coefficient. This last condition is the
earlier record's “Rule 3.” Near-misses remain tracked but are not a screening
denominator.

The final 22-paper pre-Search-3 roster combined an author-maintained,
opportunistic base assembled from prior reading and six web searches with
three Search-1 and one Search-2 additions. Its complete item-level discovery
trail was not preserved, so it is not represented as reproducibly sampled.
Later additions follow the logged rules below. Versions, duplicate handling,
and source identities are recorded in the source CSV headers and source
manifest.

## Search 1 — 2026-07-20

- **Instrument:** arXiv API, metadata search (title/abstract, not full text).
- **Categories:** cs.RO, cs.LG, cs.CV. **Window:** 2024–2026.
- **Shape:** seven queries combining sim-to-real / real-to-sim correlation phrasings with robot
  policy evaluation terms; 30 unique hits; 20 screened as candidates against
  the frozen inclusion criterion above.
- **Additions:** EmbodiedSplat (2509.17430), MolmoSpaces (2602.11337), Mem-World (2606.18960).
- **Confirmed exclusion:** AutoEval (2503.24278) — headline correlation is real-to-real.
- **Known recall bound:** the queries returned only 10 of the 22 papers known before the search;
  AutoEval's MMRV usage is body-text only and entered via a reviewer flag, not the queries.

## Search 2 — pre-submission rerun, 2026-07-21

- Same query battery plus four web searches.
- **Addition:** Colosseum V2 (2605.27759; posted 2026-05-26, missed by Search 1).
- **Exclusions for no printed coefficient:** GigaWorld-1 (2607.02642), RoboDojo.
- SC3-Eval's coding cell re-verified against its v3.

## Search 3 — logged rerun, 2026-07-21 (evening)

The first search in this project whose protocol is fully released before screening: verbatim
queries in `search_arxiv_corpus.py`, complete raw hit list in
`sources/log-arxiv-search.txt`.

- **Instrument:** arXiv API, metadata search (title/abstract). **Categories:** cs.RO, cs.LG,
  cs.CV. **Window:** 2024-01-01 to 2026-07-21. Nine queries, 47 unique hits.
- **Recall bound:** the battery recalled 14 of the 22 papers then in the census (log has the
  per-query breakdown) — metadata search alone remains insufficient, as in Search 1.
- **Screening:** 32 new candidates; 23 excluded on abstract (Real2Sim reconstruction
  pipelines, world-model training papers with no policy-evaluation correlation, autonomous
  driving, agriculture); 9 screened at full text; 5 of those excluded with reasons
  (2510.08571 offline-vs-online driving metrics; 2510.04041 no correlation at all;
  2607.15065 and 2607.19343 world-model-vs-*simulator* ground truth, not real;
  2606.05979 no printed coefficient). Every full-text verdict was then independently
  re-verified against the PDFs, including figure renders.
- **Additions — four papers meeting the claim-based criterion, missed by Searches 1–2:**
  - **VISER** (2605.06311v1): headline 0.92 = mean of two per-policy correlations
    (Octo r=0.9988 over 4 tasks, OpenVLA r=0.8496 over 5), each k=1; no uncertainty;
    no selection rule.
  - **OSCAR** (2606.04463v2): Table 4, world-model vs RoboArena real-robot pool,
    k=7 policies, Pearson +0.867 / Spearman +0.643 (latent-action row; adopted Skeleton
    row r=+0.852); no uncertainty.
  - **Hi-WM** (2604.21741v2): r=0.953 (abstract, §4.2.3, and inside Fig. 6a), pools
    3 tasks x 4 policy variants ~ 12 points; variants are 2 lineages (DP, pi0 + their
    post-trained finetunes), so k=2; no uncertainty; no rule.
  - **Scalable Policy Evaluation with Video World Models** (2511.11520v3): coefficient
    printed *only inside* Fig. 6b ("Cosmos MMRV=0.171, Pearson=0.687"; IRASim 0.613),
    prose says only "correlates positively"; k=3 off-the-shelf policies; the referenced
    real-world appendix is absent from the v3 PDF. Included on the same figure-counts
    basis as REALM and MolmoSpaces.
- **Consequence:** the bounded roster in the earlier draft (22 papers) was incomplete;
  the survey grid and all derived counts require recomputation over 26 papers. Three of
  the four additions repeat the survey's central findings (no uncertainty on r anywhere,
  no selection rule); VISER's headline is an average of k=1 correlations.

## What was not preserved

**The verbatim query strings and the 30-item hit list were not logged to a released file at search
time.** The outcomes above (additions, exclusions, recall bound) are retained,
but the queries themselves are reconstructible only from memory, and this
project's standard treats an
unreproducible search protocol as a gap, not a footnote. It is recorded here as such. Any future
search for a revision of this survey will log the verbatim queries, the full hit list, and the
per-hit screening decision to this file before screening begins.
