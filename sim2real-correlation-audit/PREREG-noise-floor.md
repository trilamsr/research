# A1a — Preregistration

**Frozen:** 2026-07-20, v1.0. Written and hash-locked **before** running the analysis.

Scope: **A1a only** — the noise-floor characterisation of the reconstructible sim–real correlation in
arXiv:2511.04665v2. A1b (ablation deltas) and A1c (IsaacLab arm) are **not** covered here and require
their own preregistration.

This document exists so the analysis cannot be adjusted after seeing the numbers. Any change to a
locked artifact, a threshold, or a procedure below invalidates it — bump the version and record why.

---


<!-- REQUIREMENTS
R1: comparison arm -- the eyeballed dataset is analysed alongside the extracted one (§3)
R2: toy 15/16/17 checkpoint robustness rows -- never silently pick one (§3)
R3: reproduction gate -- computed r must match Table I within 0.001, else halt (§5.1)
R4: drop-one-cell fragility over the 4 (task x policy) cells (§5.2)
R5: specification curve across resampling units (§5.3)
-->

## 1. The question

**How much does the published per-task sim–real correlation move under resampling choices that are
equally defensible given what the paper discloses?**

This is a question about the *instrument*, not about the simulator's quality and not about the ablation
deltas. It is a **verifiability** claim.

## 2. What this analysis CANNOT do — stated before running

Preregistered so no result can be over-read later:

- ❌ **No minimum detectable effect.** 4 clusters per task ⇒ drop-one gives exactly 4 numbers. That is a
  range, not a distribution: no variance estimate, no MDE.
- ❌ **No calibrated confidence interval.** Bootstrap coverage at k=4 could not be certified — two
  independent simulations returned impossible results (coverage → 0% as clusters increase). §3.3 already
  concedes G=4 gives ~80% coverage and declines TOST on that basis; the same limit applies here.
- ❌ **No p-value, no hypothesis test, no equivalence claim.**
- ❌ **No statement about the ablation deltas.** Their per-checkpoint data does not exist publicly
  (proposal §9.8). Any delta claim requires A1b.
- ❌ **This analysis cannot kill or vindicate the program.** It characterises an instrument.

## 3. Data

| Input | File | Status |
|---|---|---|
| Primary | `harness/fig3_checkpoints_extracted.csv` | 52 rows (toy 17 / rope 20 / T 15); vector-extracted from Fig. 3, independently reproduced 3× |
| Comparison | `harness/real_ground_truth.csv` | 12 rows, eyeballed best-checkpoint |

**Both are run.** Agreement between them is itself a preregistered check: if the qualitative conclusion
is the same under both, the extraction-provenance question does not affect A1a's finding. Divergence is
reported, not resolved by preference.

**Episode counts:** toy 20, rope 27, T-block 16 per checkpoint (paper §IV-C: "16–27 per checkpoint").

**Toy checkpoint count — three-way disagreement, resolved by rule before seeing results:** primary
**17** (the count that reproduces the printed r = 0.944 to 0.0004); **15** and **16** reported as
robustness rows. Never silently pick one.

## 4. Cluster unit — fixed in advance

**The (task × policy) cell. 4 per task, 12 total.**

Derived, not assumed: Table VI publishes exactly one hyperparameter row per policy (ACT 7k iters,
DP 7k, SmolVLA 20k, Pi-0 30k) — one configuration, one run each — and a policy trained on rope cannot be
the same run as one trained on T-block. Checkpoints are successive stages of one run and are therefore
**not** exchangeable; a drawn cell contributes its checkpoint block intact.

⚠️ **Open, and it does not change the unit:** whether the four policies share a random seed. If they do,
k=4 per task is optimistic. Recorded as a limitation, not resolved.

## 5. Procedure

Three outputs, all deterministic except where noted.

**5.1 Per-task r.** Pearson r between real and simulated per-checkpoint success rates, per task, Ours
arm only. Sanity gate: must reproduce Table I (0.944 / 0.901 / 0.915) to ≤ 0.001. **If it does not, the
analysis halts and the extraction is re-examined** — this is a stopping rule, not a tuning opportunity.

**5.2 Drop-one-cell fragility (PRIMARY).** For each task, recompute r with each of the 4 policy cells
removed in turn. Report the range and the swing. This is the headline because it needs no distributional
assumption.

**5.3 Specification curve.** Recompute the 95% percentile interval under three resampling units —
none (episode-level), checkpoint, and (task × policy) cell — reported **as a range across
specifications**, explicitly labelled *not calibrated* (§2). 8,000 replicates, `numpy` PCG64,
**seed = 0**, recorded here before running.

## 6. Known omission, stated in advance

**Sim-side noise is NOT modelled.** Simulated rates are binomial proportions over the same small grids,
so omitting their noise is **anticonservative** — the true uncertainty is larger than reported.

It is omitted because the obvious fix is invalid: redrawing episodes as `Bin(n, p̂)` treats the observed
rate as truth and adds a *second* noise layer, attenuating mean bootstrap r below observed r by
**toy −0.131, rope −0.044, T-block −0.124** (independently reproduced twice). Such a resample is not
centred on the statistic it purports to bound, so its percentiles are not an interval for it.

A valid sim-side model is proposal §4b Q4 — open. Every A1a number is therefore a **lower bound on
uncertainty**, and must be reported as such.

## 7. What would change our mind

- 5.1 fails the ≤0.001 reproduction gate → halt, re-examine extraction. Do not interpret.
- Extracted and eyeballed CSVs give different qualitative conclusions → report both, claim neither, and
  escalate the provenance question to the authors.
- Drop-one swing exceeds the published ablation deltas → the instrument is too fragile to adjudicate
  those deltas, and that is the finding.
- Specification curve spans a range wide enough that "the correlation is strong" and "the correlation is
  weak" are both supportable → report the range as the result. Do not select a specification.

## 8. Locked artifacts (SHA-256)

| File | SHA-256 | Version |
|---|---|---|
| `harness/a1a_analysis.py` (renamed) | `43d7b04c0f191e96a349d9ad38efdf525d201fbbdde53fa963e66559d8f47e91` | **v1.0 — as preregistered and as run.** ⚠️ UNVERIFIABLE, see below |
| `research/noise-floor/measure_noise_floor.py` | `91147e834914b3c998c9a6968cd66fe9dbc18bcafa4bd5b82b78824f0776bef3` | v1.3 — superseded by v1.4, see below |
| `research/sim2real-correlation-audit/measure_noise_floor.py` | `638a14c56b8aa538f3916cf5d397fc001f0f3ababdae4fe659eb280b97a595a3` | v1.4 — superseded by v1.5 (data-folder flattening) |
| `research/sim2real-correlation-audit/measure_noise_floor.py` | `ddfd4db0cf9799a8b0a8dde07d0281bccf243850aa0b3285e640bdf9291b26bd` | v1.5 — superseded by v1.6 (repository split) |
| `sim2real-correlation-audit/measure_noise_floor.py` | `4efb24b81f25a2691ef9e084b0bc17f84d7274493df82bd0d7f8eeb82e356a20` | v1.6 — superseded by v1.7 (harness moved into the package) |
| `sim2real-correlation-audit/measure_noise_floor.py` | `201e19c2e8df9cfae479699970b7f51cd61acbb16fd028b48ece4b286465bb24` | **v1.7 — current.** Path retargeting only, 2026-07-21: comparison-arm root `parents[1]` → `parent`; `harness/` now lives inside the package beside this script. `results.json` verified identical again. |

### v1.4 amendment (2026-07-21) — repository restructuring, no analytic change

The paper folder was renamed (`research/noise-floor/` → `research/sim2real-correlation-audit/`) and
the data files moved under `data/<paper>-data/` for the reproduction package. `measure_noise_floor.py`
was edited **only** to retarget paths: the comparison-arm repository-root resolution
(`parents[3]` → `parents[2]` after the folder flattening), the internal reference to
the checkpoint CSV (now `data/real2sim-eval-fig3-checkpoints.csv`), and the docstring usage example.
No analytic statement changed. **Verified before locking:** `results.json` regenerated under v1.4 is
identical to the v1.3 output up to the `source` path string. The locked data file moved and was renamed
(`checkpoint_data_from_figure3.csv` → `data/real2sim-eval-fig3-checkpoints.csv`) without content
change (hash `fd89d11f…` unchanged). A further path-only edit on 2026-07-21 (data flattening) re-locks
`measure_noise_floor.py` at `ddfd4db0cf9799a8…`; `results.json` again verified identical.

### ⚠️ Hash-lock break found by audit (2026-07-20) — recorded, not overwritten

**`measure_noise_floor.py`: the lock had been silently broken.** This table claimed
`85ab4e51…` and labelled it "v1.2 — current." The file on disk was `91147e83…`. The break
occurred in commit `6bc7ced` ("Add prereg linter; cleanup items 7-9"), which added
`# IMPLEMENTS R1–R5` markers and one bookkeeping key; §8 was never updated to match.

**The edit was verified benign before this correction was made** — the full non-comment diff is
two lines: a trailing `# IMPLEMENTS R3` comment, and
`result["prereg_requirements_run"] = ["R1"…"R5"]`. No logic changed; no reported statistic moves.
The claimed hash `85ab4e51…` appears nowhere in git history.

Recorded here rather than quietly corrected, on the standard set by `harness/PREREG.md` §2:
*"an unexplained hash change in a preregistration is indistinguishable from tampering and must
never be normalised."* Note the irony worth keeping: **the commit that shipped `prereg_lint.py`
— the tool for catching silently-dropped requirements — is the commit that silently broke this
hash lock.** The linter does not check §8-style hash tables. That gap is the reason this went
unnoticed and should be closed.

**`a1a_analysis.py`: this hash matches nothing in the repository's entire history.** Established by
exhaustive search (2026-07-20): every `*.py` blob in every commit reachable from every ref was
hashed and compared. **No match for `43d7b04c…`.**

Note also that `e3b0c44298fc…`, cited in an earlier draft of this note as one of the file's
"historical hashes", is the SHA-256 of the **empty string** — i.e. the artifact of running
`git show <commit>:harness/a1a_analysis.py` on commits where that path does not exist and piping
empty output to `shasum`. It is not a hash of any file and must not be treated as one. Recording
this because it is an easy way to manufacture a convincing-looking but meaningless hash.

The lock is retained verbatim rather than deleted, because deleting an unverifiable lock destroys
the evidence that it was unverifiable. **It confers no reproducibility guarantee and must not be
cited as one.** The analysis it was meant to pin (A1a) is reproducible instead via
`measure_noise_floor.py` at the corrected hash above, together with the checkpoint CSV — both of
which do verify.
| `research/noise-floor/checkpoint_data_from_figure3.csv` | `fd89d11f121d73e7618c2cd74c92a6eb5a9c3676c79cf37fff5beccb5d503150` | renamed from fig3_checkpoints_extracted.csv, contents unchanged |

**Why two hashes for one file — v1.0 → v1.1 (2026-07-20), after the run.**

v1.0 is the preregistered artifact and is what produced the reported results. v1.1 was written **after
seeing the output**, in response to an independent implementation audit, and is recorded separately so
the distinction cannot be lost. **v1.1 changes no reported number** — it only exposes information v1.0
computed misleadingly:

1. **`cell_support_exact()` added.** The cell branch's distribution has only **35 atoms** (4⁴ = 256
   draws; r depends on the multiset alone). v1.0's 8,000-replicate Monte Carlo approximated this
   *bit-for-bit*, so §5.3's "8,000 replicates, seed = 0" was meaningless for that branch. v1.1
   enumerates the support exactly and marks the percentile pair superseded.
2. **Unmet §3 requirements now surfaced.** v1.0 skipped the comparison arm and the 15/16 robustness
   rows **silently, while reporting an empty halt list.** v1.1 records both in
   `prereg_requirements_unmet`.

⚠️ **Amending a locked artifact after seeing results is exactly what preregistration exists to prevent.**
It is defensible here only because (a) no reported statistic changed, (b) both changes *reduce* the
strength of what can be claimed, and (c) both hashes are retained. Had v1.1 moved a number in a
favourable direction, this would not be legitimate and the correct move would have been a new prereg.

⚠️ `fig3_checkpoints_extracted.csv` is **EXTRACTED / SENSITIVITY-ONLY**. It does **not** satisfy
`PREREG.md` §6, which requires the *authors'* numbers. It is hash-locked here for reproducibility of
**A1a**, and confers no standing on the GO/NO-GO verdict.

### v1.2 (2026-07-20) — the two silently-dropped §3 requirements are now implemented

v1.0 reported an EMPTY halt list while skipping two of its own mandated arms. Both now run:

- **§3 comparison arm.** Implemented in `comparison_arm()`. Requires a stated pairing rule because the
  eyeballed file has no sim column (rule recorded in that file's header). Result: rope goes negative
  under best-checkpoint selection in BOTH datasets (-0.1932 eyeballed, -0.3143 extracted), so the
  extraction-provenance question does not affect the conclusion. The preregistered check PASSES.
- **§3 toy 15/16 robustness rows.** Implemented in `toy_robustness()`. Result: **29 distinct subsets
  clear the <=0.001 reproduction gate** (22/136 at n=15, 6/17 at n=16, 1/1 at n=17). The gate does not
  identify a unique correct extraction, confirming it is partially circular for toy packing.

Both changes ADD checks and WEAKEN claims; neither alters a previously reported statistic.
Files were also renamed for legibility (a1a_* -> noise-floor naming) and moved to research/noise-floor/.
