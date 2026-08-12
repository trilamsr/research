# H192 adverse literature challenge: H186/H188 full-edge minimax

Date: 2026-07-28

Status: independently challenged fixed-scope primary-source search.
Classification `material_narrowing`; no remaining critical or material
review issue.

## Decision

The exact H186/H188 edge-coupled randomized formulas and complete weighted
optimizer face were not found in the bounded search. However, Stoye (2007)
already gives an exact arbitrary-finite-action minimax-regret lottery and
complete optimizer-set characterization under interval-valued partial
identification. That result also reproduces H186's deterministic-singleton
value after projecting the edge box to marginal score intervals. Together
with established incomplete-Borda and pairwise-lottery work, this materially
narrows P2. The general principles and the deterministic value cannot be
presented as new.

The surviving theorem delta is construction-specific:

- a candidate-dependent-context observational equivalence class whose
  common-context target edges fill the independent box \([1/4,3/4]\);
- the exact edge-coupled ex-ante lottery value \((K-1)/(4K)\) and uniqueness
  of the uniform lottery, contrasted with the already-occupied deterministic
  interval width \((K-1)/(2K)\); and
- for an arbitrary positive opponent-reference distribution, exact value
  \((2-r_{(1)}-r_{(2)})/8\) and the complete optimizer segment with uniqueness
  exactly when \(r_{(2)}=r_{(3)}\).

Absence of those expressions from this search is not proof of novelty.

## Search execution

All ten fixed strings were run in order across the seven protocol lanes.
Primary full texts were followed for the closest minimax-regret, randomized
partial-identification, dueling-bandit, and policy-lottery sources. The search
stopped at the protocol boundary; no query was added in response to the
emerging classification.

## Unit coding

Legend: `Y` yes, `P` partial/adjacent, `N` no.

| source | observational equivalence | independent edge box | opponent-reference Borda | robust ex-ante lottery regret | H186 values | uniform uniqueness | weighted reference | H188 value | complete optimizer face | robotics application |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Stoye (2007) | N | N | N | Y | P | P | N | N | P | N |
| Lu & Boutilier (2011) | N | N | P | P | N | N | N | N | N | N |
| Aziz et al. (2015) | N | Y | Y | N | N | N | N | N | N | N |
| Manski (2007) | N | N | N | Y | N | N | N | N | N | N |
| Brill, Freeman & Conitzer (2016) | N | P | N | N | N | N | N | N | N | N |
| Montiel Olea, Qiu & Stoye (2025 version) | P | N | N | Y | N | N | N | N | P | N |
| Stoye (2009) | P | N | N | Y | N | N | N | N | N | N |
| Dudík et al. (2015) | N | N | P | P | N | N | N | N | P | N |
| Saha, Koren & Mansour (2021) | N | N | Y | N | N | N | N | N | N | N |
| Shah & Wainwright (2018) | N | N | Y | N | N | N | N | N | N | N |
| Viappiani (2020) | N | N | P | P | N | N | P | N | N | N |

No source states H186's edge-coupled randomized value or units 7--9. Stoye
(2007) occupies the arbitrary-finite-action robust lottery problem and the
deterministic component of unit 5 under the marginal interval projection.

## Closest primary sources and consequences

### Incomplete preferences plus Borda minimax regret

Lu and Boutilier define regret of selecting a deterministic alternative under
all completions of a partial preference profile, pairwise max regret, max
regret, and the minimax-regret alternative. For Borda-like positional rules,
adversarial completions can be optimized independently across voters.

Source: Tyler Lu and Craig Boutilier, *Robust Approximation and Incremental
Elicitation in Voting Protocols*, IJCAI 2011, equations (1)--(5), Section 4,
<https://www.cs.toronto.edu/~cebly/Papers/LuBoutilier_Elicitation_ijcai11.pdf>.

**Consequence:** P2 cannot claim minimax regret over incomplete Borda
information or completion-wise adversarial scoring as a new principle. This
paper chooses one deterministic alternative and does not state H186's
candidate-context construction, policy lottery objective, edge box, or exact
values.

### Randomized and nonunique minimax decisions under partial identification

Stoye treats an arbitrary finite set of treatments whose partially identified
mean values lie in intervals. Proposition 1 reduces the problem to a zero-sum
game, characterizes all minimax-regret lotteries, supplies uniqueness
conditions, and describes nonunique optimizer sets. Its key extreme-state
condition requires that the state space contain, for each action, the state
where that action is at its marginal upper bound while every other action is
at its marginal lower bound.

Source: Jörg Stoye, *Minimax Regret Treatment Choice with Incomplete Data and
Many Treatments*, *Econometric Theory* 23(1), 190--199 (2007), Proposition 1
and proof, <https://doi.org/10.1017/S0266466607070089>; public author version:
<https://stoye.economics.cornell.edu/docs/ManyTreatments.pdf>.

For H186, marginal policy values range from
\[
L=(K+1)/(4K)\quad\text{to}\quad U=(3K-1)/(4K).
\]
Stoye's product-box model therefore gives the same deterministic regret
\(U-L=(K-1)/(2K)\). H186's deterministic value is not a standalone theorem
delta.

The randomized values distinguish the models. Stoye's required simultaneous
state—one policy at \(U\), every other policy at \(L\)—is generally infeasible
under H186's antisymmetric edge coupling. A uniform lottery over the marginal
product box has worst regret
\((K-1)^2/(2K^2)\), whereas the edge-coupled H186 box has
\((K-1)/(4K)\). Their difference is
\((K-1)(K-2)/(4K^2)>0\) for \(K\geq3\). Stoye does not state H188's
opponent-weighted edge objective, value, or optimizer segment.

**Consequence:** P2 cannot claim arbitrary-\(K\) robust randomization,
zero-sum reduction, optimizer-set analysis, general nonuniqueness, or its
deterministic value as distinct. The defensible delta, if retained, is the
edge-coupled randomized geometry and H188's exact weighted optimizer face.

Montiel Olea, Qiu, and Stoye define actions in \([0,1]\) as randomized or
fractional policy choice and expected regret relative to the oracle action.
Their Theorem 3 shows that sufficiently severe partial identification can
produce infinitely many minimax-regret rules and can require randomization.

Source: José Luis Montiel Olea, Chen Qiu, and Jörg Stoye, *Decision Theory for
Treatment Choice Problems with Partial Identification*, arXiv:2312.17623,
Sections 2 and 3.3, especially equation (2.1) and Theorem 3,
<https://arxiv.org/abs/2312.17623>.

Stoye gives an earlier applied partial-identification treatment-choice
analysis in which interior decision probabilities are randomized assignments
and minimax regret uses them to hedge unidentified outcome risks.

Source: Jörg Stoye, *Partial Identification and Robust Treatment Choice: An
Application to Young Offenders*, *Journal of Statistical Theory and Practice*
3(1), 2009, Sections 1 and 4,
<https://doi.org/10.1080/15598608.2009.10411923>.

**Consequence:** P2 cannot claim that partial identification can make
randomization minimax-regret optimal, that ex-ante mixing can improve on
deterministic action, or that a minimax set may be nonunique. H186/H188's
multi-policy Borda geometry and exact optimizer face remain different.

### Policy lotteries for arbitrary pairwise matrices

Dudík et al. define a von Neumann winner as a distribution over policies that
beats or ties every opposing policy. Proposition 1 identifies it with a
maxmin strategy of the skew-symmetric preference-matrix game and guarantees
existence. Their contextual version observes context before action and
integrates a common context/preference distribution.

Source: Miroslav Dudík et al., *Contextual Dueling Bandits*, COLT 2015,
PMLR 40, Sections 2--3, Proposition 1,
<https://proceedings.mlr.press/v40/dudik15.html>.

**Consequence:** randomized policy actions over arbitrary nontransitive
pairwise matrices and their game-theoretic analysis are prior art. The
von-Neumann maxmin objective is not Borda regret over an observationally
compatible edge box.

### Online Borda regret and nonparametric Borda recovery

Saha, Koren, and Mansour define uniform-reference Borda scores for arbitrary
preference matrices and study cumulative online regret against the
hindsight Borda winner under a sequence of adversarial matrices.

Source: Aadirupa Saha, Tomer Koren, and Yishay Mansour, *Adversarial Dueling
Bandits*, ICML 2021, PMLR 139, Sections 1 and 2,
<https://proceedings.mlr.press/v139/saha21a.html>.

Shah and Wainwright study Borda top-\(k\) and ranking recovery from noisy
pairwise comparisons without a Bradley--Terry parametric restriction.

Source: Nihar Shah and Martin Wainwright, *Simple, Robust and Optimal Ranking
from Pairwise Comparisons*, JMLR 18(199), 2018,
<https://www.jmlr.org/papers/v18/16-206.html>.

**Consequence:** arbitrary pairwise matrices, uniform Borda value, and Borda
regret/recovery are established. Their uncertainty is sampling or online
adversarial variation, not H186's static observational-equivalence class, and
their regret bounds do not state H186/H188's robust one-shot values.

### Partial tournaments and uncertain scoring weights

Aziz et al. analyze possible and necessary Borda winners under partial
tournament completion. Viappiani uses minimax regret when the positional
scoring vector itself is uncertain and gives closed-form deterministic-winner
characterizations.

Sources:

- Haris Aziz et al., *Possible and Necessary Winners of Partial Tournaments*,
  JAIR 54, 2015, <https://doi.org/10.1613/jair.4856>.
- Paolo Viappiani, *Robust Winner Determination in Positional Scoring Rules
  with Uncertain Weights*, *Theory and Decision* 88, 2020,
  <https://doi.org/10.1007/s11238-019-09734-3>.

**Consequence:** completion-dependent Borda winners and minimax regret under
score-weight ambiguity are not P2 contributions. Neither source uses
candidate-dependent physical context or H188's fixed opponent-reference
weights with uncertain target pair edges.

Brill, Freeman, and Conitzer study mixed equilibria of incompletely specified
symmetric zero-sum or tournament games. This is a close uncertainty-plus-
lottery comparator, but its equilibrium/bipartisan objective is not Borda
regret and does not select one robust fixed lottery across completions.

Source: Markus Brill, Rupert Freeman, and Vincent Conitzer, *Computing
Possible and Necessary Equilibrium Actions (and Bipartisan Set Winners)*,
AAAI 2016, Sections 1--3,
<https://doi.org/10.1609/aaai.v30i1.10052>.

## Final classification

`material_narrowing`

The H186 deterministic value is an interval-width corollary already covered
by Stoye's arbitrary-treatment product-box framework and is not a standalone
delta. H186's smaller edge-coupled randomized value and H188's weighted value
and optimizer face may be presented only as scoped results for one constructed
compatible class, positioned against Stoye's exact arbitrary-action theorem,
deterministic Borda minimax regret, randomized treatment choice under partial
identification, and randomized pairwise policy solutions. The paper must not
sell “randomization helps,” “robust Borda,” “minimax regret under incomplete
comparisons,” “arbitrary finite actions,” “zero-sum reduction,” or “nonunique
randomized optima” as its conceptual novelty.

An independent fixed-query execution confirmed `material_narrowing`, located
Stoye (2007) as the closest theorem, and derived the exact product-box versus
edge-box comparison above. It also followed partial-tournament references to
incomplete symmetric games. No inspected source states H186's edge-coupled
randomized value or H188's weighted value, optimizer segment, or uniqueness
boundary. Expert human literature review remains a release gate because
bounded search cannot establish novelty by absence.

## 2026-07-28 H233 route-graph update

External review prompted H233 after the fixed H192 search, so this is a
separate outcome-exposed literature update rather than an extension of the
fixed-query challenge. Four primary-source lanes were searched for graph
identification, contextual pairwise comparison, partial identification, and
minimax regret.

- Hajek, Oh, and Xu show that comparison-graph topology and Laplacian
  connectivity govern global parameter recovery under Plackett--Luce and
  Thurstone ranking models; a disconnected graph provides no basis for
  gauging one component against another. Source:
  <https://arxiv.org/abs/1406.5638>.
- Dudík et al. study contextual pairwise policy comparison and randomized von
  Neumann winners, but context is observed before action and the objective is
  not H233's compatible common-target Borda regret. Source:
  <https://proceedings.mlr.press/v40/dudik15.html>.
- Skalse et al. characterize invariances and downstream consequences of
  partial identifiability from comparison and demonstration data. Source:
  <https://proceedings.mlr.press/v202/skalse23a.html>.
- Montiel Olea, Qiu, and Stoye establish randomized minimax-regret decision
  rules under partial identification. Source:
  <https://arxiv.org/abs/2312.17623>.

**Disposition:** graph connectivity as an identification principle, invariance
analysis, contextual pairwise policies, and randomized minimax regret are all
prior art. No exact collision was found for the combination of
context-specific route colors, bounded shared binary-success component
offsets, the common-target compatible polytope, or the H233 three-policy
optimizer \((2/3,0,1/3)\) and value \(1/12\). This absence is not proof of
novelty. H233 may be presented only as a construction-specific synthesis and
exact result pending expert human literature review.

## 2026-07-28 H234 constructive-design update

H234 follows H233 after outcome exposure and asks what additional route edges
repair contextwise identification. Two primary sources make the prior-art
boundary explicit:

- Osting, Brune, and Osher formulate pairwise-comparison data collection as a
  graph-design problem and optimize informativeness through algebraic
  connectivity:
  <https://www.jmlr.org/papers/v15/osting14a.html>.
- Shah et al. derive topology-dependent minimax estimation bounds for
  pairwise comparisons and state that the graph topology guides which pairs
  to collect:
  <https://www.jmlr.org/papers/v17/15-189.html>.

**Disposition:** the \(m-1\) component-bridging count, allowable quotient
connectivity test, and minimum-spanning-tree cost rule are applications of
established graph principles, not novel methods. H234 may be used as an
executable constructive corollary within H233's model: bridge components to
repair structural identification, then use repeated measurements to address
precision. Human literature review remains required for any stronger
contribution claim.
