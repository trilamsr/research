# Source-native data-owner outreach feasibility

Date: 2026-07-30

Status: public contact and willingness-signal audit complete. On 2026-07-31,
the user reported sending the narrowed TRI LBM/N-SCORE request separately to
`rares@lbm.global`, `dasnyder@princeton.edu`, and `contact@tri.global`, and
reported an RRC 2020 reply from Felix Widmaier. The user also opened
ArmnetBench issue `armnet-dev/armnetbench-v0.1#1`. No TRI or ArmnetBench
response has yet been reported.

## Purpose and boundary

This review identifies owners who may hold the small control-plane records
missing from otherwise useful public real-robot evaluation datasets. It ranks
contact routes and narrows each request to the minimum metadata needed. It
does not treat public release behavior as consent or a promise to share.
Willingness ratings are forecasts to prioritize outreach; only an owner reply
can establish actual willingness, access, rights, or data availability.

No contact, issue, direct message, form submission, dataset request, or
external upload was made during this audit. The later TRI outreach described
above was performed by the user. The first follow-up window is 2026-08-11
through 2026-08-14; no further contact is planned before then unless a
recipient replies.

## Ask for metadata, not another large dataset

The first request should not ask for video, model weights, or full
trajectories. For ArmnetBench and AutoEval, most trajectory bytes are already
public. The useful missing object is a de-identified control-log export with:

- stable run/episode and source-session identifiers;
- exact policy checkpoint and execution-container digest;
- task, cell/site, route/context, and evaluator/rubric revision;
- planned and realized execution order;
- assignment/scheduling rule, probabilities where applicable, and RNG/seed;
- reset procedure, accepted initial-state artifact or acceptance result, and
  carryover/intervention events;
- pseudonymous operator/session/dependence-cluster identity;
- start/end time, retry/cancellation/exclusion reason, and missingness status;
- the public trajectory/outcome locator; and
- license, privacy, and permitted-use status.

If a historical export is unavailable, the fallback request is a small fresh
prospective run that records these fields before outcomes are opened.

The lowest-burden first message should ask whether the fields exist and who
can authorize a de-identified export. The revision 1.12 preflight packet
should be offered only after interest; sending the full schema unprompted
would create unnecessary work.

## Priority 1 — Armnet / ArmnetBench

### Why it is the best first contact

ArmnetBench is the closest public retrospective substrate:

- the paper and release are only days old;
- the authors released 3,718 labelled episodes, exact task-policy checkpoint
  links, and extensive operational detail;
- 40 public author-account raw repositories represent 31 exact source
  sessions, suggesting the control plane and raw recorder are still active;
- author accounts and the release repository were updated in July 2026; and
- the paper explicitly names initial-position logging and repeatable reset as
  future improvements.

Sources:

- paper: <https://arxiv.org/html/2607.24481>;
- release repository:
  <https://github.com/armnet-dev/armnetbench-v0.1>;
- organization: <https://github.com/armnet-dev>;
- public author profiles:
  <https://github.com/pravsels> and
  <https://github.com/villekuosmanen>.

### Estimated willingness

**High for a conversation or small metadata export; medium for a fully
qualified historical record.**

The unusually broad public release, exact checkpoints, raw session
repositories, and active infrastructure are strong positive signals. The main
uncertainty is whether reset acceptance, assignment RNG, and exact execution
receipts were recorded at all. The paper states that object positions were not
recorded, so no request should imply those historical values can be recovered.

### What to request

Ask for the v0.1 control-plane slice that joins the 2,520 attempted benchmark
rollouts, including the two removed reset-error runs, to:

- source session and episode;
- scheduled policy/task/cell and realized order;
- checkpoint and container digest actually executed;
- run start/end and retry/cancellation state;
- operator/session pseudonym;
- reset confirmation and any retained first-frame/state locator;
- score/rubric revision and scoring time; and
- exclusion/missingness reason.

Do not request raw video or outcomes in the first message.

### Appropriate contact route

1. Open a concise technical question in the
   [ArmnetBench GitHub issue tracker](https://github.com/armnet-dev/armnetbench-v0.1/issues/new),
   asking for the preferred private contact for a de-identified metadata
   request.
2. If a nonpublic first approach is preferred, direct-message
   [Praveen Selvaraj](https://x.com/pravsels) or
   [Ville Kuosmanen](https://x.com/VilleKuosmanen), linking the exact public
   crosswalk finding and asking where to send the field list.

No public email address was found in the paper, release repository, Armnet
website, or public GitHub profiles. Do not infer an Armnet email pattern.

### Suggested first message

> We are auditing what metadata is needed to make real-robot policy
> evaluations reproducible at the execution/control-plane level. We found
> that 31 ArmnetBench v0.1 source-session IDs join exactly to public raw
> LeRobot repositories, covering 1,080 released trajectories. This gives us
> the trajectories already; we are not asking for video or model weights.
> Does Armnet retain a de-identified scheduler/reset manifest that links each
> attempted v0.1 rollout to its source episode, realized order, executed
> checkpoint/container digest, reset confirmation, session pseudonym, and
> exclusion reason? If so, who is the right person to discuss a small
> metadata-only export or a fresh prospectively logged run with?

### Contact status — 2026-07-31

The user opened
<https://github.com/armnet-dev/armnetbench-v0.1/issues/1>. The public issue
asks whether a run-level table can connect each rollout to source episode,
task/cell, checkpoint, run order, reset status, and retry/exclusion reason. It
states that public trajectories are already available, accepts partial or
never-recorded answers, and asks for an alternate contact if needed. This is
appropriately narrower than the full field inventory. Do not add another
comment or follow-up unless the maintainers reply or the user explicitly
requests one.

## Priority 2 — AutoEval

### Why it is strong

AutoEval is the best fresh-run route. Its official site says:

- public users can submit policies to real WidowX stations;
- full-resolution observations, actions, and success are logged;
- job reports link to the dataset directory; and
- users should contact the authors or official Discord when needed.

The public code includes the scheduler and logging stack. The repository is
unarchived and was pushed in March 2026. The project page, however, says the
listed four tasks were available only until 2026-01-01 and that 2026 tasks
were TBD, so current station availability must be confirmed rather than
assumed.

Sources:

- project and official contact routes: <https://auto-eval.github.io/>;
- code: <https://github.com/zhouzypaul/auto_eval>;
- principal author's current homepage:
  <https://zhouzypaul.github.io/>.

### Estimated willingness

**High for technical discussion or a fresh instrumented job; medium for a
historical scheduler-database export.**

The system is explicitly community-facing and the authors invite contact.
Historical logs may contain submitter network endpoints, W&B identities, or
other private operational fields that require redaction. A fresh job can
avoid most of that problem.

### What to request

First ask whether the stations are currently active and whether a fresh job
can return or seal:

- immutable policy-server revision/manifest;
- scheduler job ID, robot/task, planned and realized episode order;
- reset-policy and success-classifier revision;
- reset acceptance and retry state;
- run/session timestamps and dependence grouping;
- exact W&B/Hugging Face trajectory locators; and
- cancellation/missingness reason.

For historical data, request only the de-identified scheduler-to-public-log
join for a bounded set of public `eval_id` directories.

### Appropriate contact route

1. Email Zhiyuan “Paul” Zhou at the address published on his current homepage:
   `zhiyuan_zhou@berkeley.edu`.
2. Use the official AutoEval Discord linked from the project page for a short
   operational availability question.
3. Use the
   [AutoEval GitHub issue tracker](https://github.com/zhouzypaul/auto_eval/issues)
   only for public technical/schema questions, not private log access.

### Suggested first message

> We are looking for a small, prospectively controlled real-robot evaluation
> record—not a large new trajectory release. AutoEval appears especially well
> suited because actions, observations, success, resets, and scheduler jobs
> are already logged. Are any AutoEval stations currently accepting research
> jobs, and could a fresh bounded job preserve the scheduler order, exact
> policy/reset/success-classifier revisions, reset acceptance, session
> identity, retries/missingness, and public trajectory locators before
> outcomes are opened? We can send a short field-level preflight and adapt to
> your privacy and operational constraints.

## Priority 3 — Toyota Research Institute LBM / N-SCORE

### Why it is valuable

The TRI LBM evaluation has the strongest public blinded and randomized
matched-initial-condition design in the current candidate set. The paper
describes blind A/B hardware testing, consistent initial-condition bundles,
randomized policy order, and 50 trials per task. N-SCORE releases transformed
hardware score data and code, while the project page exposes hardware rollout
videos.

Sources:

- project: <https://toyotaresearchinstitute.github.io/lbm1/>;
- paper: <https://arxiv.org/html/2507.05331>;
- N-SCORE code/data: <https://github.com/dasnyder5/nscore>.

The supplementary author section states that, unless otherwise indicated, TRI
author email addresses follow `firstname.lastname@tri.global`.

### Estimated willingness

**Medium for a de-identified bundle/order table; low-to-medium for raw
trajectories or internal infrastructure logs.**

The public method, score data, and rollout videos are positive reproducibility
signals. Corporate IP, unreleased policy details, workplace imagery, and a
large multi-author approval chain are material friction. A narrow metadata
request that avoids sensor data and policy bytes has a better chance.

### What to request

Ask only for the original 500-record LBM comparison table, de-identified:

- stable trial and initial-condition bundle ID;
- task and anonymous policy revision;
- randomized A/B order and realized execution order;
- operator/session or cluster pseudonym;
- reset completion/acceptance indicator;
- exclusion/missingness and retry state; and
- the already released score-record key or public video locator.

If exact policy identity cannot be shared, anonymous stable revision IDs are
sufficient for the first structural study.

### Appropriate contact route

Email one primary evaluation contributor and one project lead using the
paper-published institutional pattern. A reasonable pair is
`jose.barreiros@tri.global` and `rares.ambrus@tri.global`. The N-SCORE GitHub
repository does not accept unrestricted new issues, so it is not the preferred
route. Do not use TRI's press contact for a research-data request.

### Suggested first message

> Your blinded, randomized initial-condition bundle design is the closest
> published match we found to a reproducible real-robot comparison. We are not
> requesting proprietary trajectories, model weights, or unredacted
> infrastructure logs. Would TRI consider sharing a de-identified
> trial/bundle metadata table linking the released 500 hardware scores to
> initial-condition bundle, randomized A/B order, realized order,
> session/operator pseudonym, reset completion, and missingness? Stable
> anonymous policy-revision IDs would be sufficient. We can first send a
> result-empty field inventory so your team can assess burden and disclosure
> risk.

## Priority 4 — Real Robot Challenge 2020

### Why it remains useful

The official release contains 10,278 physical runs with actions,
observations, goals, reward, timestamps, initial pose, calibration, and
original software images. Its public SQLite index deliberately omits
team/policy/submission/user identity, while the challenge infrastructure
necessarily scheduled submitted Singularity images.

Sources:

- dataset: <https://people.tuebingen.mpg.de/mpi-is-software/data/rrc2020/>;
- challenge: <https://real-robot-challenge.com/2020>;
- paper/contact list:
  <https://proceedings.mlr.press/v176/bauer22a/bauer22a.pdf>;
- current maintainer profile:
  <https://is.mpg.de/person/felixwidmaier>.

### Estimated willingness

**Medium for an anonymized submission-revision join; low for restored human or
team identities.**

The group has a strong open-data record and a named current robot maintainer.
The data are six years old, and stripped identity may reflect deliberate
privacy or competition-policy decisions. The request should preserve
anonymity and ask only for stable revision linkage.

### What to request

Ask whether the organizer database can export:

- `job_id` to anonymous submission/container revision;
- weekly-evaluation versus participant-run status;
- scheduled block/order and any seed;
- retry/cancellation/exclusion state; and
- session/robot dependence group.

Do not request usernames, team identities, or private submission code.

### Appropriate contact route

Email Felix Widmaier/Kloss, the current TriFinger maintainer and challenge
co-organizer, at the address printed in the challenge paper:
`felix.widmaier@tuebingen.mpg.de`. The official challenge site also directs
questions to its forum, but direct email is more appropriate for an archival
metadata and privacy question.

### Suggested first message

> The public RRC 2020 release already contains the real actions,
> observations, goals, rewards, timestamps, and calibration we need. The
> remaining reproducibility gap is the intentionally stripped execution
> identity. Does an organizer archive retain a privacy-preserving mapping from
> `job_id` to anonymous stable submission/container revision, evaluation
> block/order, robot/session group, and retry/exclusion state? We do not need
> usernames, team identities, or source code. If such a mapping exists, would
> MPI consider a de-identified metadata export or a result-empty schema
> preflight?

## Recommended outreach sequence

1. **Armnet first.** Highest information value and lowest likely burden.
2. **AutoEval second.** Ask about current availability and a fresh,
   prospectively logged run rather than relying on old scheduler data.
3. **TRI third.** Keep the request strictly de-identified and metadata-only.
4. **RRC fourth.** Treat as an archival fallback and foreground privacy.

Send messages separately rather than as a mass request. The first message
should be short, cite the exact public data already found, state what is not
being requested, and ask for the correct owner. Do not attach the 27-table
schema until the recipient expresses interest.

## Decision

The owner-contact route is worth pursuing. Armnet and AutoEval have credible
signals of willingness and could close the program's dominant external gap
with a small export or bounded fresh run. TRI and RRC are useful independent
fallbacks but have higher organizational or archival friction.

Actual willingness, rights, field existence, and turnaround remain unknown
until the user authorizes contact and a source owner responds.

## Send-ready outreach packet

Contact details and project state were rechecked on 2026-07-30. These are
separate requests, not a mass mailing. Do not attach the full revision 1.12
schema to the first message.

| priority | source | primary recipient and channel | exact first request | acceptable minimum | follow-up |
|---|---|---|---|---|---|
| 1 | ArmnetBench v0.1 | ArmnetBench repository maintainers through `https://github.com/armnet-dev/armnetbench-v0.1/issues/new`; mention `@pravsels` and `@villekuosmanen` | Ask whether a de-identified v0.1 scheduler/reset manifest exists and who can authorize a metadata-only research export | One CSV/JSONL row per attempted rollout linking attempted-run ID, public source session/episode, task, cell, policy/checkpoint/container revision, realized order/times, reset confirmation, anonymous session/operator group, scoring/rubric revision, and retry/exclusion status | If they prefer privacy, move to the private channel they identify. One friendly follow-up after 7--10 business days. |
| 2 | AutoEval | Zhiyuan “Paul” Zhou, `zhiyuan_zhou@berkeley.edu`; alternate short operational question in the official Discord linked from `https://auto-eval.github.io/` | First confirm whether a station currently accepts research jobs; then ask for one small fresh job whose control metadata is fixed and retained before results are viewed | A result-sealed job manifest with immutable submitted-policy revision, scheduler job/episode IDs, robot/task, planned and realized order, reset-policy and success-classifier revisions, reset acceptance/retries, session/times, public data locators, and missingness/cancellation status | If no reply after 7--10 business days, post only the availability question in Discord. Use GitHub issues only for public schema/implementation questions. |
| 3 | TRI LBM/N-SCORE | To `jose.barreiros@tri.global`; cc `rares.ambrus@tri.global` | Ask whether TRI can share a de-identified structural join for the released five-task, two-policy, 50-bundle-per-task N-SCORE comparison | 500 rows with stable trial/bundle ID, task, anonymous stable policy revision, randomized and realized within-bundle order, anonymous station/session/operator cluster, reset completion, retry/exclusion/missingness, and released score/video key | Offer a result-empty column template. Do not ask for images, trajectories, weights, names, or infrastructure logs. One follow-up after 10 business days. |
| 4 | Real Robot Challenge 2020 | Felix Widmaier/Kloss, `felix.widmaier@tuebingen.mpg.de` | Ask whether an organizer archive retains a privacy-preserving join from public `job_id` to stable anonymous submission/container revision and scheduling status | A table containing `job_id`, anonymous submission/container revision, participant-run versus weekly-evaluation flag, block/order, seed if retained, robot/session group, and retry/cancellation/exclusion status | Explicitly decline usernames, team identities, private code, or deanonymization. One follow-up after 10 business days. |

### Why these exact asks

- **ArmnetBench:** the public data already supply trajectories, actions,
  states, outcomes, source sessions, task-policy checkpoint repositories, and
  within-session episode order. The owner-only gaps are the scheduler,
  realized cross-session order, exact executed artifact receipt, reset
  confirmation, anonymous dependence groups, and per-attempt disposition.
  The paper explicitly says object positions were randomized but not recorded,
  so historical object coordinates should not be requested.
- **AutoEval:** the official public workflow already logs observations,
  actions, per-episode success, reports, videos, and job-linked dataset
  locations. The owner-only opportunity is to preserve the scheduler,
  reset-policy, success-classifier, retry, session, and exact policy-revision
  state for a new bounded job. The project page's four-task notice expired on
  2026-01-01 and leaves 2026 tasks unresolved, so availability must be asked
  rather than assumed.
- **TRI LBM/N-SCORE:** the public paper establishes blinded evaluators,
  matched initial-condition bundles, randomized within-bundle policy order,
  and 50 trials per task and policy; N-SCORE releases transformed scores. The
  missing owner-only object is the structural bundle/order join, not more
  outcome data.
- **RRC 2020:** the public release already contains actions, observations,
  goals, timestamps, robot name, calibration, object trajectory, and rewards
  for 10,278 physical runs. The missing owner-only object is an anonymous
  execution-revision and scheduling join. The request must preserve the
  release's deliberate removal of participant identity.

## Exact first messages

### ArmnetBench GitHub issue

**Title:** Research question: de-identified v0.1 execution metadata

Hi Armnet team,

Congratulations on the ArmnetBench release. It is one of the most open
real-robot evaluation datasets we have come across.

We are working on a study of reproducible robot evaluation. We already have
the public trajectories, so we are only looking for a small amount of
run-level metadata.

Would you happen to have a table linking each attempted rollout to its source
episode, task and cell, executed checkpoint, run order and time, reset status,
and any retry or exclusion reason?

Even a partial table would help, and knowing that some fields were never
recorded would also be useful. Is this something you might be able to share,
or is there someone else we should ask?

Thanks again for making so much of the benchmark public.

Best,

[Name / affiliation]

### AutoEval email

**To:** `zhiyuan_zhou@berkeley.edu`

**Subject:** Small prospectively logged AutoEval research run?

Hi Paul,

I really enjoyed the AutoEval work. It seems like a great fit for a study we
are doing on reproducible real-robot evaluation.

Are any AutoEval stations currently accepting research jobs?

If so, we would love to run a small evaluation while keeping a little extra
metadata: the policy version, job and episode order, robot and task, reset and
success-classifier versions, retries, timestamps, and links to the resulting
logs.

We do not need any private user information, extra videos, or model weights.
We can send a simple empty template if that is helpful.

If the public stations are not running right now, advice on doing the same
with a local AutoEval setup would be just as useful.

Thanks for your time—and for making AutoEval available to the community.

Best,

[Name / affiliation]

### TRI LBM/N-SCORE email

**To:** `jose.barreiros@tri.global`

**Cc:** `rares.ambrus@tri.global`

**Subject:** De-identified trial/bundle metadata for the LBM evaluation

Hi Jose and Rares,

I came across your LBM evaluation while looking at ways to make real-robot
comparisons more reproducible. The matched initial conditions, blinding, and
randomized policy order are exactly the kind of design we have been looking
for.

Would you be open to sharing a de-identified table for the released N-SCORE
comparison? We mainly need the task and bundle IDs, anonymous policy version,
run order, station or session grouping, reset status, and the matching public
score or video.

We do not need raw trajectories, images, model weights, internal logs, or
anyone's identity. Even a partial table would be useful.

I would be happy to send a simple empty template first if that makes the
request easier to assess.

Thanks for considering it, and for documenting the evaluation so carefully.

Best,

[Name / affiliation]

### Real Robot Challenge 2020 email

**To:** `felix.widmaier@tuebingen.mpg.de`

**Subject:** Privacy-preserving execution metadata for the RRC 2020 dataset

Hi Felix,

Thank you for keeping the RRC 2020 dataset available. It already contains
almost everything we need for a study of reproducible real-robot evaluation.

I had one archival question: does the organizer database still contain a
private mapping from each public job ID to an anonymous submission or
container version, evaluation order, robot or session, and any retry or
exclusion status?

We do not need names, team identities, source code, or anything that could
identify participants. Anonymous version IDs would be enough.

Even a partial table—or simply knowing that the mapping no longer
exists—would help us document the dataset accurately. Would it be okay if I
sent a short empty template showing the fields we have in mind?

Thanks very much for your time and for maintaining this resource.

Best,

[Name / affiliation]

## Response handling

For every reply, record separately:

1. whether the requested fields exist;
2. which fields can be shared and under what license/use conditions;
3. whether the owner is offering historical data, a fresh run, or only
   technical guidance;
4. whether any result/outcome is exposed before the analysis commitment;
5. the promised delivery route and expected timing; and
6. unresolved privacy, access, citation, or authorship expectations.

Do not treat a friendly reply as data authorization, and do not accept
authorship, confidentiality, data-use, or publication terms without explicit
user review.

## RRC 2020 owner response — 2026-07-31

Source trace: user-provided reply from Felix Widmaier in the active research
session. This is an owner statement about archival custody, not an independently
reconstructed database fact.

Retained findings:

- regular job IDs are sequential by submission: a greater job ID was submitted
  after a lesser job ID;
- public `start_time` can order realized run starts;
- public `robot_name` identifies the robot used for each run;
- per-run container/source-code identity was never recorded; and
- Felix no longer has the data needed to reconstruct which job belonged to
  which team.

The first three points strengthen public chronology and robot-cluster
reconstruction. The last two definitively block a historical per-job executed
container/team join through this owner route. Anonymous policy/submission
version remains unidentified, not merely access-restricted.

The user reported sending a concise follow-up on 2026-07-31. It asked whether
runs were repeated after technical failure, cancelled or invalid, omitted
from official scoring, or linked to an earlier job as a retry, and whether any
flag distinguished participant-submitted runs from evaluation runs. The
follow-up response below resolves those questions.

### RRC 2020 owner follow-up — 2026-08-05

Source trace: user-provided reply from Felix Widmaier in the active research
session. As above, this is a source-owner statement rather than an independently
reconstructed database fact.

User-provided transcript:

> We excluded failed or cancelled runs, so the runs in the dataset should
> all be complete.
>
> There was no automatic re-run of failing jobs, so there is no
> information if a job was executed after a previous failure.
>
> Participant-submitted runs and evaluation runs can be distinguished by
> the job id:
> - participant-submitted runs have purely numerical ids (e.g. 12345)
> - evaluation runs are prefixed with "eval" (e.g. eval1234)
>
> Best,
> Felix

Retained findings:

- failed or cancelled runs were excluded, so released dataset runs should all
  be complete;
- failing jobs were not automatically rerun, and the dataset does not contain
  information linking a job to a previous failed attempt;
- purely numerical job IDs identify participant-submitted runs; and
- `eval`-prefixed job IDs identify evaluation runs.

This confirms the public-index prefix as a run-type label. It does not recover
policy, container, team, retry-parent, failure, or cancellation records. Because
failed and cancelled attempts were excluded, the public dataset cannot estimate
attempt-level failure, cancellation, or selection processes from retained runs
alone.

In the already fixed H247 roster, the previously named identifier strata are
therefore 98 participant-submitted runs and 37 evaluation runs. The 52 observed
robot-day/regime cells comprise 39 participant-run cells and 13 evaluation-run
cells. H247 already used the exact binary ID regime as a baseline covariate and
roster-stratification variable, so this semantic clarification changes neither
the roster nor any fitted value, loss, interval, or conclusion. It permits the
covariate to be described prospectively as run type while leaving the original
frozen analysis and its historical `id_regime_interpreted_as_run_type: false`
boundary unchanged.

### Public-index follow-through — 2026-07-31

The separately fixed structural audit of the official 1,695,744-byte SQLite
index passed and is canonical in
`result-rrc2020-public-index-structural-audit-2026-07-31.json` (source SHA-256
`deb7e9f9f2e26b3c2e3c6478cd5122e5cb9287b287c0e4783465b5780aa837af`).
It selected no reward or trajectory values.

The index contains 7,231 integer “regular” IDs and 3,047 text IDs matching
`eval[0-9]+`. The regular IDs have zero inversions against realized start
order (with 404 tied start-time pairs). The `eval`-prefixed suffix order has
492,373 inversions and 18 tied pairs. The official dataset page confirms that
participant submissions and evaluation runs are both present, but neither that
page nor the official query utility defines the `eval` prefix. Felix
Widmaier's 2026-08-05 source-owner follow-up now confirms the mapping:
numerical IDs are participant-submitted runs and `eval`-prefixed IDs are
evaluation runs. This mapping is owner-confirmed rather than independently
documented in the public index.

The index has no separate policy/container, team, retry, cancellation,
invalidation, or official-exclusion column. Run type is encoded in the job-ID
format according to the source owner. The index identifies seven robot labels,
although `roboch2` has only two retained rows. These facts support chronology,
robot grouping, and run-type grouping but do not repair the missing
policy-version join or expose excluded attempts.
