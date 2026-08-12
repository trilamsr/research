# P2 narrow claim-evidence ledger

Date: 2026-08-10

Status: independently challenged and narrowed through H238, with H250's
synthetic finite-sample extension added after a method-distinct vertex
cross-check. H231--H234, H238, and H250 are exploratory additions, not
confirmatory results. This is not a manuscript or release artifact.

## Purpose

Translate the surviving P2 evidence into individually falsifiable claim units
before prose composition. Claims may be reordered, narrowed, removed, or
retired as evidence changes. The ledger is not a story outline and does not
authorize selecting evidence for rhetorical fit.

## C1 — Pair-first evaluation can fail to identify a common-context winner

**Permitted claim.** For every integer \(K\geq3\), there exists a finite
\(K\)-policy, two-context construction in which every policy pair is observed
and the full observed law is identical across compatible worlds, yet those
worlds produce different common-context winners. Complete pair support and
unlimited precision on the observed routes therefore do not identify the
common-context winner without an additional bridge.

**Evidence.** H151 exact construction and endpoint exhaustion; H152 standalone
Node.js reconstruction; H183 exact existential embedding, explicit
potential-world projection, symbolic proof, and independent reconstruction
through \(K=200\).

**Challenged strengthening.** Across the full three-core-edge compatible box
of the fixed H183 embedding, every core deterministic singleton has worst
compatible regret \(1/K\), every added singleton has \((K+1)/(2K)\), and the
deterministic-singleton minimax value is \(1/K\). H184's exact enumeration and
symbolic derivation were independently reconstructed through \(K=257\), with
additional checks at \(K=509\) and \(K=1009\).

**Do not promote to.** Every pair-first evaluation is unidentified; no useful
decision is possible; every roster exhibits the ambiguity; \(1/K\) applies to
randomized choice or the full compatible \(K\)-policy class; or this is a new
general result about contextual comparison. H183 pads the three-policy core
with dominated policies, H184 fixes all noncore target edges, and uniform
randomization over the core improves the box-specific worst regret to
\(1/(2K)\).

**Challenged randomized extension.** H185 derives
\[
\mathcal R(p)=
\frac{(1-s)K/2+\{1+\max_{i<3}p_i-\min_{i<3}p_i\}/2}{K},
\]
where \(s\) is total probability on the core. This gives unique randomized
minimax worst-case expected regret \(1/(2K)\) at the uniform core mixture.
A separate implementation reconstructed the formula and uniqueness. The
compatible world is fixed independently of the realized ex-ante draw; a
realized core policy can still incur \(1/K\).

**Full-roster strengthening.** H186 removes the three-policy core, dominated
padding, and fixed noncore target edges. For one constructed complete-support
pair-first half-win law, every common-context pair edge varies independently
over \([1/4,3/4]\). Under the self-half-win, divide-by-\(K\) Borda target, every
deterministic singleton has minimax regret \((K-1)/(2K)\), while the unique
uniform ex-ante lottery has worst-case expected regret \((K-1)/(4K)\).
Separate exact arithmetic and full routed potential schedules reconstruct the
formula, uniqueness, and observational compatibility.

**Would change the claim.** A valid proof that either construction's observed
law determines the common-context winner, an error in the exhaustive
compatible-completion census, or failure of the arbitrary-\(K\) symbolic
embedding.

**H186 boundary.** The full-box theorem concerns one constructed observed law,
not every pair-first observed distribution, empirical roster, protocol, or
prevalence claim. Its factor-of-two improvement is expected regret for a
lottery fixed before the compatible world and realized draw. Under
opponent-only division by \(K-1\), the values rescale to \(1/2\) and \(1/4\).
Stoye's arbitrary-treatment interval model already recovers the deterministic
value from H186's marginal score bounds and establishes randomized minimax,
zero-sum, arbitrary-\(K\), and optimizer-set principles. The surviving scoped
delta is the smaller exact randomized value imposed by antisymmetric edge
coupling, not deterministic interval regret or robust randomization in
general.

**Weighted-reference strengthening.** H188 replaces uniform reference weights
with arbitrary positive weights, and H212 independently extends the exact
result to the closed simplex \(r_i\geq0,\sum_i r_i=1\). If
\(a=r_{(1)}\le b=r_{(2)}\le g=r_{(3)}\), the exact minimax value is
\((2-a-b)/8\), and the complete optimizer is a line segment indexed by
\(0\le h\le(g-b)/2\). The preliminary proportional water-filling rule is its
\(h=0\) endpoint but is not generally unique. Uniqueness holds exactly when
\(b=g\); uniform weights uniquely recover H186. A separate equality-case
proof, raw endpoint oracle, 486 rational reference vectors, 1,458 exact
segment points, and optimal-face searches independently support the interior
theorem. H212 adds 242 zero-pattern cases, 247 raw endpoint probes, 14,056
label permutations, 40,395 exact grid lotteries, and a separate
BigInt-rational equality-case challenge. Exactly two zero-reference policies
may receive equal positive lottery mass; with at least three, the segment
collapses and \(p=r\) is unique.

**Decision-set boundary.** H212 keeps zero-reference policies selectable.
H213 proves that additionally requiring \(p_i=0\) whenever \(r_i=0\) gives
value \(1/4\) and unique optimizer \(p=r\) for every nonempty zero set. With
exactly one zero this is a value increase of \(r_{(2)}/8\); with exactly two
zeros it is a face collapse without a value change; with at least three it
changes nothing. The paper may state both decision sets but may not infer
which one an empirical system intends.

**H188/H212 boundary.** The result remains one weighted-Borda full compatible
edge box with fixed nonnegative reference weights and ex-ante expected regret.
H213 changes only the selectable action set by hard support exclusion. These
are not empirical policy recommendations, results for every pair-first
observed law, or realized-policy guarantees.

**Constant-route target-context-support sensitivity.** H231 replaces primitive
independent pair responses with shared binary per-policy success and half
credit for ties. Every observed pair routes through A, so this is a
missing-target-context-support result, not a candidate-dependent-routing test. The
compatible edges become the gradient polytope
\[
q_{ij}=\tfrac12+\tfrac14(x_i-x_j),
\]
so the full independent box is not generic. Opposite unique common-context
winners remain compatible with the complete observed half-tie law for every
\(K\geq3\). Every deterministic policy has worst regret \(1/4\); the unique
uniform minimax lottery and value \((K-1)/(4K)\) survive; and
opponent-reference weights cancel. Theorem 3's optimizer face and H213's
uniqueness do not transfer. H231 is review-triggered exploratory sensitivity,
supported by exact producer and separate Node implementations.

**Do not promote H231 to.** Every structured response model has this gradient
geometry; the empirical robot outcome is shared binary success; Theorem 3 is
robust to response-model choice; or H231 is confirmatory.

**Route-colored extension.** H233 allows genuine candidate-dependent routing.
Context-specific route-graph components determine which shared-success
offsets remain free. Connected positive-weight graphs identify target
differences; disconnected graphs can leave them unidentified when bounds
leave slack. A three-policy routed law has opposite compatible winners and
unique minimax lottery \((2/3,0,1/3)\) with regret \(1/12\). This is a
review-triggered, outcome-exposed construction and LP, not a universal
response model, novelty proof, or empirical policy recommendation.

**Constructive route-graph repair.** H234 turns H233's component diagnosis
into a bounded design rule. For the objective of identifying every
within-context difference, a positive-target-weight context with \(m\)
components needs at least \(m-1\) new cross-component pair types, and a
spanning tree achieves that minimum when every cross-component pair is
available. With restrictions or nonnegative costs, feasibility and least-cost
repair are respectively connectivity and a minimum spanning tree on the
component quotient graph. Repeating existing pair types does not repair
identification. This is stronger than necessary for some boundary-specific
winner or cross-context aggregate targets and says nothing about finite-sample
precision, physical execution validity, or operational acceptability.

**Finite-sample interface.** H250 replaces exact edge equations by simultaneous
intervals and projects the resulting polytope onto target differences, possible
and certified winners, and minimax regret. If the supplied edge intervals have
joint coverage at least \(1-\alpha\), every projected statement inherits that
coverage. The dual support-function implementation reproduces H233's
\((2/3,0,1/3)\) lottery and \(1/12\) regret; a separate vertex-enumeration
primal implementation agrees on connected, disconnected, point, and widened
known answers. H250 is an executable application of established confidence-set
projection and robust optimization, not new interval theory. It does not
license a sampling unit, dependence assumption, or public-system outcome
analysis.

**Bradley--Terry boundary.** Under an exact logistic difference law, observed
common-context edges identify score differences along graph paths. The Borda
winner set is identified if and only if that graph is connected; uniqueness
also requires a unique largest score. This is an established latent-score graph
identifiability consequence. It does not extend to strong stochastic
transitivity alone and is not promoted as a new theorem.

**Interior routed-law strengthening.** H238 shows that H231's
non-identification is not confined to an exact half-tie within the exact
additive shared-success law class with equal target-context weights. For an
arbitrary model-consistent observed profile \(a\), let
\(D=\max_i a_i-\min_i a_i\). If \(D<1\), every policy is a compatible unique
target winner under a missing-context completion. At \(D=1\), a policy
attaining the minimum observed score cannot be a unique winner. For an
observed pair score \(o\), the compatible target interval is
\([o/2,(o+1)/2]\); it has width \(1/2\) and straddles \(1/2\) exactly when
\(o\in(0,1)\). The exact worst-case regret of lottery \(p\) is
\[
\mathcal R(p;a)=
\frac{1-p\cdot a+\max_w(a_w-p_w)}{4}.
\]
Exact rational censuses, a method-distinct implementation, and an independent
mathematical derivation verify the relative-interior theorem, boundary
exclusions, interval, and regret formula. The set is relative-open inside the
model manifold and has empty ambient interior for \(K\ge3\). This is a
model-specific identification statement, not an empirical prevalence,
finite-sample precision, power, or design-validity result.

**Pairwise-lottery comparator.** H232 shows that, on the same symmetric margin
box, a Khalaf-style robust maximal lottery also uniquely selects the uniform
lottery, but maximizes worst head-to-head margin rather than minimizing regret
to the world-specific Borda oracle. The observed zero matrix makes every
lottery maximal; every action is a possible incomplete-game equilibrium
action and none is necessary. Same selected action on this box is not
objective equivalence or a novelty claim.

## C2 — A same-mechanism within-pair action can remain identified

**Permitted claim.** In a separate known-answer construction within the same
class of pair-conditioned mechanisms, a rule that chooses within the presented
pair is identified even when a unique global policy is not. In H165's fixed
cycle, the local within-pair rule has value \(3/4\) and the
always-lower-index rule \(7/12\), while all three uniform-reference tournament
scores tie at \(1/2\). This identification is conditional on H165's fixed
outcome-independent future pair law, positive edge support, and invariant
pair-specific outcome laws; the construction does not establish those
conditions empirically or define standalone task-success deployment.

**Evidence.** H165 construction and H166 independent challenge.

**Do not promote to.** This within-pair action is the intended action of an
audited public system; it is an established robotics workflow; it is useful
under a new deployment context law; or the numerical advantage transports to
another roster or mechanism.

**Would change the claim.** Failure of the exact arithmetic, loss of a
positive-weight pair, or a target that is not the declared same-mechanism
within-pair target.

## C3 — The examined public record does not qualify either interpretation

**Permitted claim.** The fixed public RoboArena record declares a global
leaderboard, but the inspected public evidence does not establish the
assignment, stable context-law, current-support, bridge, and cluster conditions
needed for a common-context interpretation. RoboArena's source-described
random pair sampling and evaluator policy-identity blinding are favorable
evidence but do not reconstruct the realized historical law. Separately, the
record does not qualify H165's same-mechanism within-pair target because it does not publicly
bind the required action alignment, future pair law, pair-specific invariance,
support, and lifecycle evidence.

**Evidence.** H151's no-bridge construction; H167 15-unit public-record audit;
and H168 independent reconstruction.

**Do not promote to.** RoboArena is invalid; its outcomes or rankings are
wrong; the assignment mechanism was biased; or the missing evidence does not
exist privately.

**Would change the claim.** A version-bound public release supplying the
missing assignment/context/support/bridge/cluster evidence for the same
declared action.

## C4 — Separate evidence layers can recognize positive protocol structure

**Permitted claim.** H178's common ten-unit source rubric records UMI-Bench and
RoboDojo as source-described finite-panel positive contrasts. Within H182's
separate five-unit artifact reconstruction layer, RoboDojo reconstructs four
units—a finite task frame, interface-bound candidate roster, execution path,
and trial identity—while physical reset remains partial. UMI-Bench remains
source-described only because its released demonstration corpus is not the
paper's evaluation package.

**Evidence.** H177--H179 source coding and independent challenge; H182 bounded
artifact reconstruction.

**Do not promote to.** Either protocol was executed exactly as documented;
RoboDojo is fully artifact-reproduced; UMI-Bench lacks an evaluation package
outside the inspected sources; or the two examples estimate field prevalence.

**Would change the claim.** A version-bound public physical reset interface
for RoboDojo, a version-bound UMI-Bench evaluation runner and common episode
package, or a material coding/repository-identity error.

## C4A — A new multi-policy benchmark remains an adverse design contrast

**Permitted claim.** H224 prospectively codes the newly submitted ArmnetBench
v0.1 paper, outside H178's fixed historical roster. The source supports
standalone seven-policy execution, a common task/cell setup, public
per-episode artifact/outcome linkage, and useful cost/capacity evidence. It
also reports releasing every evaluated checkpoint, and the fixed public audit
resolves all 84 linked repositories. Independent initial-state sampling is not
intrinsically unidentified. The public record does not bind the
policy-independence and stability of that sampling law, a policy
execution-order law, realized initial positions, measured reset acceptance, a
physical-block/dependence unit, fixed horizons, dependence-aware uncertainty,
or exact evaluated checkpoint revisions. It is therefore an
adverse/mismatch design contrast, not a positive contrast.

**Evidence.** H224 exact official source/PDF audit, independent Node
reconstruction, and adjudication review.

**Do not promote to.** ArmnetBench is invalid; its assignment was biased; its
rankings or policy outcomes are wrong; the missing evidence does not exist
privately; or H224 estimates how common these design gaps are.

**Would change the claim.** A version-bound source for the same evaluation
supplying policy assignment/order, reset acceptance and lifecycle, a declared
dependence unit with matching uncertainty, or an immutable checkpoint
manifest. Such evidence could upgrade individual units without automatically
establishing the full positive contrast.

## C4B — A retained-run archive need not close attempt or policy lineage

**Permitted claim.** The RRC 2020 public index supports retained-run job,
start-time, and robot grouping. A source-owner reply states that numerical job
IDs identify participant-submitted runs, `eval`-prefixed IDs identify
evaluation runs, failed and cancelled runs were excluded, failing jobs were
not automatically rerun, and the retained dataset does not link jobs to prior
failed attempts. Per-run container/source identity was never recorded and the
historical team join is no longer recoverable. The release therefore does not
expose attempt-level failure, cancellation, selection, retry-parent, or
immutable policy/container lineage, even though retained runs should be
complete.

**Evidence.** The exact user-provided source-owner transcript and its source
boundary are retained in
`review-source-native-data-owner-outreach-feasibility-2026-07-30.md`. The
separately fixed structural audit of the official SQLite index verifies the
public columns, 10,278 retained rows, ID strata, ordering properties, robot
labels, and absence of separate policy/container, team, retry, cancellation,
invalidation, and exclusion columns. The run-type semantics and excluded-run
facts remain owner-confirmed rather than independently reconstructed.

**Do not promote to.** RRC 2020 is invalid; its retained runs are incomplete;
failed attempts were automatically rerun; the missing joins exist privately;
the public archive identifies executed policy versions; or retained-run data
can estimate the attempt-level exclusion process.

**Would change the claim.** A version-bound organizer export or primary
record that links all scheduled attempts to terminal states, retry parents,
and immutable anonymous policy/container revisions. Such a record could close
individual lineage units without itself validating outcomes, assignment, or
uncertainty.

## C4C — Three public real-robot records separate identification from protocol description

**Permitted claim.** H251 identifies the exact released 50-state finite-panel
winner in each of three AnkIle tasks because all three fixed policy artifacts
appear on every manifest state. The winner margins over the runner-up are 3,
1, and 3 successes; they are descriptive and carry no population interval.
RoboArena's pinned 21-label co-occurrence graph has two components, while its
20 pair-eligible labels form one connected component; neither graph supplies
the common-context law or lifecycle join required by P2's target. TRI's paper
describes blind randomized matched bundles, but Dryad version 4 omits the
bundle/trial/reset/order/version join and contains two success-rate cells that
disagree with their arrays and counts. TRI is therefore a structural release
contrast only.

**Evidence.** H251 protocol, retained source manifest, deterministic Python
result, eight producer tests, 22-check method-distinct Ruby reconstruction,
and review disposition.

**Do not promote to.** The AnkIle winners generalize beyond the released
states; their reset and retry process is fully reconstructed; RoboArena's
leaderboard is wrong; TRI did not execute its stated protocol; or any missing
field is absent privately.

**Would change the claim.** A missing or duplicated AnkIle policy-state cell;
a policy artifact or state mismatch; a different pinned RoboArena topology;
or a TRI release that binds its outcome arrays to the paper's matched bundles.

## C5 — A target-bound evidence interface illustrates schema-level refusal

**Permitted claim.** The H170 interface makes a partial target descriptor and
authorization status explicit enough to reject target-altering or incomplete
synthetic dossiers under its fixed tests and independent attacks. It is a
deterministic schema-level engineering illustration, not an empirically
qualified action or a necessary part of the central identification result.

**Evidence.** H169 failure diagnosis, H170 repair, and H171 independent
challenge.

**Do not promote to.** The interface proves a submitted record is truthful,
qualifies a real site, establishes physical reset adequacy, or is itself a new
general provenance method. It does not bind an actual target population,
policy roster, estimand, outcome, reference weights, or the physical truth of
submitted evidence.

**Would change the claim.** A bypass that authorizes a dossier with missing or
changed target identity, or failure of the independent artifact/hash
reconstruction.

## C6 — Context-first order does not by itself satisfy a support gate

**Permitted claim.** PhAIL v1.0 is a public, materially different
context-first contrast: the operator fixes recorded episode context before a
context-aware sampler selects one of four policies. In the exact 594-rollout
release, 17 of 19 full-window
`task × object × tote × camera` cells contain all four policies, so the exact
full-release no-extrapolation gate fails. Under the prespecified
UTC-calendar-date sensitivity partition, only 18 of 126 cells contain all four
policies; the resulting outcome-free subset contains 194 episodes and excludes
400. UTC date is a reproducible proxy, not a source-recorded session block or
an actionable target. Chronology/session dependence remains unresolved, and
performance analysis is not authorized.

**Evidence.** H187 exact public inventory and outcome-stripped support audit,
including independent source and result challenges. H189 independently tests
the pre-assignment initial item count: 80 episodes use 4 items and 514 use 8.
Item count splits the full-window context into 27 cells but is deterministic
within every H187 dated cell, leaving exactly the same 18-cell, 194-episode
target. H190's complete path-only inventory and pinned-tree search finds no
fixed-token session-artifact path in the 594-rollout subtree or release root;
its two reset-token matches belong to the separate teleoperation corpus.
H191's exhaustive outcome-free grid shows that retained exposure depends on
calendar-bin width and phase: 24-hour phases range from 15--19 supported cells
and 154--194 retained episodes, while H187's UTC phase has minimum per-policy
count only one or two in every retained cell. H193's independently reproduced
key-only census finds two differently named infrastructure leads:
`server.host` in all 594 episodes and `server.device` in 267. A result-exposed
H194 census, fixed after an accidental nonperformance value exposure, shows
that host is the constant bind address `0.0.0.0` and device is the
policy-deterministic accelerator label `cuda` for ACT/SmolVLA and missing for
GR00T/OpenPI. Pinned Positronic source semantics and independent challenge
confirm that neither field is session or dependence-cluster identity. H194
passes after a material validator repair that closes unexpected nested output
fields; its counts and null disposition did not change.
H195 then traces the fixed public PhAIL Positronic path across
`phail_multiple`, selected-policy forwarding, the base client/server chain,
the server codec wrapper, concrete harness-to-writer wiring, `static.json`
serialization, and all four public backend server configurations. Every fixed
backend activates `RecordingCodec`, which creates a per-reset `.rrd` locator
from second-resolution wall time plus a process-local counter but does not
expose it through metadata. The complete fixed public release inventory has
zero `.rrd` paths, without establishing whether configured server recording
locations are available or populated. Two preliminary H195 candidates
overreached and were blocked by independent challenge before reliance.
DreamZero provides an out-of-roster UUID counterexample. The retained result
is an unjoined server-recording-locator finding, not a globally unique ID,
physical reset, operator session, or dependence cluster.

H196 prospectively pins a later public Positronic endpoint before inspecting
post-`v0.2.1` source. At commit `01b78e6f...070524`, every public PhAIL server
command still configures recording, and the redesigned server session exposes
the full `.rrd` path through the ready handshake. The remote-session and
harness path writes it to finalized episode `static.json` as
`inference.policy.server.recording.rrd`. Normal dataset writing separately
creates a `uuid.uuid4().hex` episode `uid` in `meta.json`. An independent
Node/Git-object reconstruction agrees across the 19 fixed/expanded paths and
51 relevant commits. The UUID is not a shared server-session identifier or
embedded in the `.rrd`; the locator supplies the join and is not proven
globally unique across restarts. The two expansion-path introduction timings
are result-exposed after a recorded path-boundary mismatch; the endpoint
comparison remains prospective.

H198 binds the exact pinned current `phail` command. It supports real
arm/gripper home mechanics, episode UUID, fixed UI context, and the
server-recording join, but not a bound scene-reset task, Harness-side pre-open
accepted-state gate, complete camera boundary, operator-session identity, or
persistent reset/carryover evidence. H199 then finds that both `v0.2.1` and
the pinned current path use the same nonzero independent-uniform Franka
home-joint perturbation and do not serialize the realized target or RNG
identity. H200's independently reproduced key-only census finds three
possible public sidecar fields in all 594 episodes; H201 source semantics
closes them as robot/signal visualization descriptors rather than
realized-home or RNG evidence. H202 then opens only the prospectively fixed
first `robot_state.q` observation and exact error companion. All 594 first
pairs are timestamp-aligned and nonerror; the achieved per-joint spread is
0.980--1.029 times the standard deviation implied by the configured uniform
target supports, and the seven-joint deviation RMS is 0.1244 rad. This
recovers achieved first arm state, not the commanded draw, RNG, reset
acceptance, scene/gripper state, session, carryover, or performance. No later
state or performance field was opened.

**Do not promote to.** PhAIL assignment is randomized; the restricted target
is representative of all 594 runs; missing dated support proves biased
assignment; item count is balanced across policies; chronology is ignorable;
UTC date is a session surrogate; the 194-row subset has adequate effective
sample size; equal cell weights represent a justified target population; the
published ranking is wrong; or the restricted target authorizes opening
outcomes. The H193/H194 server fields must not be promoted to machine, server
instance, session, or physical-device identity. The result audits recorded
exposure support and infrastructure configuration, not scene replay,
exchangeability, performance, or benchmark validity.
H195 must not be promoted to global locator uniqueness, public availability of
server recordings, absence of other identity, or framework-wide session
support; a recording artifact or connection object is not a dependence
cluster.
H196 must not be used to revise the historical `v0.2.1` trace, infer the exact
historical deployment code, claim that released PhAIL episodes contain the
later fields, call the episode UUID an end-to-end server-session identifier,
or promote either field to physical reset, operator session, exchangeability,
or independence.
H198--H202 must not be promoted to historical execution fidelity, physical
reset success or inadequacy, harmful randomization, end-effector displacement,
episode dependence or nonexchangeability, or a performance effect. Generic
joint and pose schema names are not the values of those signals or evidence
of the randomized home draw. H202's achieved observation is not the commanded
target or random draw, and complete first-state coverage is not complete
physical-context or dependence coverage.
H203's fixed successive-distance diagnostic finds no material temporal
structure globally, within policy, or within UTC date. This must not be
promoted to independence, authenticated execution order, carryover absence,
or valid outcome uncertainty units; it only blocks a positive clustering
claim at the tested resolution.
H204 likewise finds no material policy mean association conditional on UTC
date or date mean association conditional on policy. This supports only
seven-joint achieved-state mean balance at fixed resolution, not randomized
assignment, full physical balance, exchangeability, or outcome validity.
H205 finds no material marginal-uniformity or cross-joint-dependence
departure at its fixed resolution. The largest correlation has nominal
upper-tail p=0.0282 but misses both fixed material gates and must not be
selected post hoc. This achieved-state consistency is not commanded-draw or
RNG validation, reset acceptance, historical execution fidelity, full
physical balance, or proof of independence.
H206 result-exposed dual-clock analysis identifies two scale-separated
clock-offset regimes and perfect wall/monotonic order agreement within each.
This may narrow the public chronology statement to source-qualified
within-regime order. It must not be promoted to machine, reboot, operator
session, physical reset, carryover, exchangeability cluster, or valid
uncertainty-unit identification.
H207's fixed result-exposed refinement retains the temporal bounded null when
adjacency and permutation are restricted to those two regimes: the pooled
ratio is 1.031 with p=0.0498 against the fixed p<=0.01 material gate, and
neither regime-specific p-value passes 0.005. This blocks a positive
clock-regime temporal-structure claim at the tested resolution; it must not
be promoted to independence, authenticated physical order, carryover absence,
session identity, or valid uncertainty units.
H208 shows that clock regime is exactly aliased with the 13 saturated UTC-date
indicators (rank increment zero), although all eight policy-regime cells are
observed (18--146 episodes; total variation 0.386; descriptive Cramer's V
0.452). A date-adjusted regime effect is therefore not separately identified
on this release. Complete coarse cells must not be promoted to randomization,
precision, exchangeability, session identity, causality, or outcome validity.
H209 finds pooled same-policy adjacency 0.39189 versus permutation median
0.30574 (p=0.00004), but its 0.08615 excess misses the fixed 0.10 pooled
material gate. Regime 1 supplies the fixed secondary signal (0.48594 versus
0.32129, p=0.00004); regime 2 does not (p=0.23864). This supports a bounded
policy-scheduling metadata request, not a global material batching claim,
assignment law, scheduler/session identity, outcome dependence, or
performance effect.
H210 preserves policy composition independently within all 13 UTC dates.
Pooled excess contracts to 0.01205 (p=0.52872), regime-1-date excess to
0.03704 (p=0.23688), and regime-2-date excess is -0.00296 (p=0.90884).
No fixed gate passes. This narrows the H209 signal to coarse date composition
or boundaries at the tested resolution; it does not prove that explanation,
identify assignment or scheduling mechanics, validate exchangeability, or
authorize an outcome analysis.

**Would change the claim.** A material source-identity or sidecar-content
change, an error in the exact contingency reconstruction, a source-recorded
session/context field that changes the support target, a source-qualified
realized reset target/RNG field joined to each episode, or a protocol-valid
chronology bridge.

## Combined contribution boundary

The paper candidate may test the joined proposition that:

1. protocol order, support, and bridge or stability assumptions jointly
   constrain which robot-policy action is identified: pair-first evaluation
   can destroy common-context identification while preserving a formal
   same-mechanism within-pair target;
2. this distinction changes what evidence would be needed to interpret one
   fixed public global action;
3. separate source and artifact layers can record positive protocol structure
   at explicitly different evidence strengths; and
4. one public context-first release supplies an anti-sufficiency boundary:
   favorable action order does not itself satisfy an exact full-release
   no-extrapolation support gate.

H170 may appear only as a schema-level implementation illustration; removing
it does not alter the central scientific proposition. C6 is a boundary case,
not a necessary fifth contribution, and does not extend H180--H181's prior
jointness or novelty coverage. No component is presented as an independent
novelty claim. External-validity partial identification, maximal and robust
lotteries, game/social-choice agent evaluation, active task-agent selection,
weighted Borda objectives, matched initial
conditions, blinded interleaving, fixed benchmark scope, evaluation estimands,
common random numbers, adaptive paired design, and generic evidence logging
are prior art or design premises.

## Next challenge

The independent methods and robotics/design challenges require the narrowings
above. Before manuscript conversion, verify those dispositions against the
revised ledger, preserve H187's negative full-release result, H189's null
target change, H190's recall-bounded path null, and every outcome-sealing
boundary. H188/H212's reference vector is an opponent-reference distribution, not
pair-sampling weights or the deployment lottery; no empirical choice of
reference weights, zero semantics, or optimizer has yet been supplied. H192
supplies bounded prior-art coverage for H186--H188; H232 adds an exact
same-box comparison with robust/maximal lotteries. Both require material
narrowing to the candidate-dependent-context construction, edge-coupled Borda
regret, weighted optimizer face, and robotics-specific public-evidence
application. This is not novelty proof; expert human literature review remains
required before any public novelty language.
