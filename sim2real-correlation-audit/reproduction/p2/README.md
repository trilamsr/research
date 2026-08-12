# P2 reproduction package

This standalone package supports the working paper *When Candidate-Dependent
Context Can Leave a Common-Context Robot-Policy Winner Unidentified*. It contains
only the manuscript, its mathematical and empirical dependencies, exact
public-source acquisition records, and the pinned source
files needed for the PhAIL server-field semantics and runtime-to-writer
recording-locator checks, including the pinned current endpoint used by H196,
H198, and H199 and the v0.2.1 source used by H201. It also contains H202's
bounded achieved-first-state projection and source manifest, but not the
approximately 1.8 GB of raw public Parquet sources. H251's AnkIle and TRI source
files are retained in full. The pinned RoboArena metadata tree is public but is
not redistributed because it contains free text and participant metadata.

## Reproduce

Requires Python 3.12, Node.js **v26.5.0**, and Ruby **2.6.10**. The independent
Node and Ruby results record their runtime versions, so different releases are
not exact runtime reproductions. Python scientific and test dependencies are
pinned in `requirements.txt`.

```bash
make install
make verify
```

`make verify` checks the package manifest, runs the included tests and
independent implementations, rebuilds every executable manuscript result that
does not require public network reacquisition, and verifies the
H190/H193/H194/H200 aggregates and H195 source trace from outcome-free
projections and pinned source. It also verifies H196--H210, H212--H213, and
  H231--H234, H238, H250, and H251 result/challenge bindings and every required file
  in the two vendored Positronic endpoint projections.

## Evidence boundary

- The theorem and routing calculations are exact offline reproductions.
- H212 independently verifies that H188's value and complete optimizer segment
  extend unchanged to fixed nonnegative reference weights, including zero
  weights. Its closed-simplex theorem does not select empirical reference
  weights or a preferred point on a nonunique segment.
- H213 verifies the distinct decision set in which zero-reference policies
  are also forbidden from selection. It does not determine which meaning of
  zero a real system intends.
- H231 is a constant-route target-context-support sensitivity under a shared
  binary-success response model. Every observed pair routes through A, so it
  does not test candidate-dependent routing. The unrestricted edge box
  collapses to a gradient polytope, while opposite winners, the unique
  uniform minimax lottery, and its value survive.
- H232 compares the symmetric edge-box result with maximal lotteries,
  incomplete games, and a robust maximal-lottery objective. The robust and
  P2 objectives select the same uniform lottery on this box but differ in
  uncertainty object, adversary, loss, comparator, value, and interpretation.
- H233 supplies the genuine candidate-dependent shared-success route-graph
  extension. Context-specific connected components determine free offsets;
  the three-policy known answer has opposite compatible winners and unique
  minimax lottery `(2/3, 0, 1/3)` with regret `1/12`. It is review-triggered,
  outcome-exposed, construction-specific exploratory work.
- H234 turns that diagnosis into a contextwise design repair. A route graph
  with `m` current components needs `m-1` new cross-component pair types;
  allowable-pair feasibility is connectivity of the component quotient graph,
  and nonnegative pair costs reduce to a minimum spanning tree. This is an
  exploratory model-specific corollary, not a novelty or precision claim.
- H250 propagates jointly valid edge intervals through the route graph to
  target-difference bounds, possible and certified winners, and a minimax
  action. A separate vertex-enumeration primal agrees with the producer's dual
  LP on four fixed cases. Coverage is inherited from the supplied intervals;
  H250 does not define or validate an empirical sampling unit.
- H251 applies the paper to three pinned releases. The bundled AnkIle and TRI
  records reproduce the exact finite-panel and release-integrity checks
  offline. Reproducing RoboArena's pair-support topology additionally requires
  the pinned `DataDump_07-17-2026` snapshot and
  `make verify-h251-roboarena ROBOARENA_ROOT=/path/to/snapshot`.
- H238 proves that the routed-law non-identification is not confined to the
  exact half-tie construction. Within the exact additive shared-success law
  class with equal target-context weights, every model-consistent profile
  whose range is below one makes every policy a compatible unique target
  winner. It also gives the exact target interval and worst-case regret
  formula. This set is relative-open in the model class, not ambient-open in
  unrestricted pair-score space; these are model-specific identification
  results, not empirical prevalence claims.
- The retained H178/H179 result pair is schema- and hash-checked offline, but
  its source-bound calculation requires `make sources` followed by
  `make verify-sources`, which downloads six exact-version arXiv PDFs and
  rejects any hash mismatch. The PDFs are not bundled because four official
  records grant distribution to arXiv rather than clearly authorizing this
  third-party package. Reproduction does not substitute for recoding.
- H167 is recomputed from retained, hash-bound upstream audit snapshots. Those
  snapshots are trusted derived inputs here; the underlying public-source
  audits are not rerun by this package.
- H187, H189, H190, and H191 are checked against their retained sanitized
  source records. H190 is additionally rebuilt from a complete outcome-free
  14,361-object path projection and both complete pinned Git-tree projections.
- H193/H194 are recomputed offline from projections that retain only key/type
  records and the two disclosed nonperformance configuration fields. The
  1,188 raw public sidecars are deliberately excluded because they also contain
  sealed outcome-bearing fields.
- The included acquisition scripts can reacquire the H190 and H193/H194/H200 safe
  projections directly from the public sources without retaining raw
  sidecars. They require public network access and are not part of default
  offline verification.
- H194's counts and policy/date structure reproduce offline. Its
  infrastructure-versus-instance classification remains a source-semantic
  judgment supported by pinned Positronic source and review record.
- H195 traces the fixed public PhAIL policy, server-recording, handshake, and
  writer path. It verifies that a process-local per-reset `.rrd` locator is
  created but not exposed to episode metadata. It does not establish global
  uniqueness, public availability of server recordings, or a valid dependence
  cluster.
- H196 compares a later pinned public endpoint. Offline verification binds its
  result and independent challenge to its endpoint source files.
  Full reconstruction of the 51-commit history requires `make sources`
  followed by `make verify-sources`; this clones only the public Positronic
  repository and checks out the fixed commit. The endpoint writes a UUID
  episode identity and separately records the configured server `.rrd` path.
  It does not establish one shared end-to-end session ID, historical
  deployment code, or a dependence cluster.
- H198 binds the exact current `phail` command and distinguishes implemented
  home mechanics from accepted-state, camera-boundary, operator-session, and
  persistent reset/carryover evidence.
- H199 compares `v0.2.1` and current source and reproduces the unrecorded
  randomized Franka home-target mechanism and joint-space arithmetic. It does
  not infer physical reset quality, end-effector displacement, dependence, or
  performance.
- H200 is recomputed offline from a projection containing only matched key
  names, node types, and anonymized episode IDs. H201 binds its three candidate
  keys to pinned source and closes them as robot/signal visualization schema,
  not realized-home or RNG evidence. No candidate value is included.
- H202's offline projection contains only the first seven-joint observation,
  exact companion error flag, source identities/hashes, and row-count
  integrity fields for each fixed episode. The default verification
  recomputes its fixed summaries and checks the retained independent DuckDB
  challenge. `make verify-h202-sources` optionally reacquires all 1,188
  public Parquet sources (about 1.8 GB), checks the projection byte-for-byte,
  and reruns the independent first-row challenge. Raw Parquet is excluded
  from the package and all later state and performance fields remain sealed.
- H203 recomputes one fixed temporal diagnostic from the retained H187/H202
  projections and verifies a separate Node permutation challenge. Its null
  blocks a positive clustering claim at the tested resolution; it does not
  prove independence, authenticate physical order, or exclude carryover.
- H204 recomputes fixed policy/date mean-balance tests and validates an
  independent SciPy/Philox challenge. Its null is limited to seven achieved
  arm joints and does not establish full physical balance or exchangeability.
- H205 recomputes fixed marginal-shape and cross-joint-dependence tests and
  validates a separate SciPy/Philox challenge. Its bounded null concerns only
  achieved first arm state and does not validate commanded draws, RNG state,
  reset acceptance, or independence.
- H206 reconstructs the result-exposed wall/monotonic clock-offset regimes and
  validates an independent Node/BigInt implementation. It supports only
  within-regime chronology, not host/session/reset/carryover or dependence-
  cluster identity.
- H207 recomputes the fixed clock-regime temporal refinement and validates an
  independent Node/SplitMix64 permutation implementation. Its bounded null
  does not establish independence, physical order, session identity,
  carryover absence, or valid uncertainty units.
- H208 verifies exact clock-regime/date alias and coarse policy-regime support
  with an independent Ruby/Rational reconstruction. It blocks a separate
  date-adjusted regime effect and does not establish randomization,
  exchangeability, precision, session identity, causality, or outcome
  validity.
- H209 verifies the fixed within-regime policy-label adjacency diagnostic with
  an independent Node/SplitMix64 stream. Its regime-1 secondary signal and
  sub-threshold pooled effect do not establish an assignment law, scheduler,
  session identity, outcome dependence, or performance.
- H210 verifies the fixed within-date policy-label adjacency diagnostic with
  an independent Node/SplitMix64 stream. Its bounded null narrows H209 to
  coarse date composition or boundaries at the tested resolution but does not
  prove that mechanism, identify assignment or scheduling, validate
  exchangeability, or authorize outcomes.
- H182 is a retained source-semantic review classification. Reproducing its
  judgment requires reacquiring the exact archived webpages and pinned
  repository blobs named in its protocol/review; it is not an offline
  executable result in this package.
- H224 is a prospective source-design audit of ArmnetBench
  `2607.24481v1`, outside H178's fixed roster. Offline verification binds the
  twelve-unit producer record and separate Node challenge. Direct
  reconstruction requires the official PDF and source archive named and
  hash-bound in the protocol; they are not bundled. H224 is an
  adverse/mismatch design contrast, not a claim about benchmark validity or
  policy performance.
- The RRC 2020 adverse provenance contrast is bound to the fixed public-index
  structural audit and the retained source-owner response. The public index
  supports retained-run chronology and robot grouping; run type, exclusion of
  failed/cancelled attempts, and missing retry lineage are owner-confirmed.
  No policy/container, team, retry-parent, failed-attempt, or cancelled-attempt
  record is included or inferred, and no performance conclusion is drawn.
- H192 is a bounded literature-positioning record, not a proof of novelty.
  Its semantic judgment requires expert review of the pinned primary sources.
- No PhAIL performance value, ranking, success field, or outcome record is
  included.
- No ArmnetBench performance value or ranking is included or used by H224.
- Internal manuscript-review and review-disposition work products are not
  included. They are neither computational dependencies nor substitutes for
  external review of the paper and reproduced evidence.

## Optional PDF rebuild

`make pdf` rebuilds the manuscript, supplement, and combined PDF into
`work/pdf-rebuild/` and compares their extracted text with the inspected
renderings. Exact checked tool versions are Pandoc 3.10, Tectonic 0.16.9, and
Poppler `pdfunite` 26.07.0. PDF bytes include build metadata and are therefore
not claimed byte-deterministic.

The internal technical challenge records are not expert human review, peer
review, or external endorsement. Human statistical, robotics, and literature
review remain release gates.
