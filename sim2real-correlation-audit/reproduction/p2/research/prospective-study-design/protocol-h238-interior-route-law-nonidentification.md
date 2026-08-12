# Protocol: H238 interior routed-law non-identification

Date fixed: 2026-07-31

Status: review-triggered and outcome-exposed exploratory extension. P2A
supplied the pairwise interval argument before this protocol, and the primary
analyst derived the range formulation and candidate regret expression before
fixing the computational gates. This is not confirmatory evidence.

## Question and decision value

Does H231's constant-route shared-binary-success non-identification require the
exact observed half-tie law, or does it hold on an open set of valid observed
laws?

A positive result removes the material knife-edge objection and changes the
scope of the formal finding. A negative result would keep H231 as a special
witness and block any claim of interior robustness.

## Model

There are \(K\geq3\) policies and two equal-target-weight contexts \(A,B\).
Every observed pair is routed through \(A\). Shared binary success means are
\(a_i=E[Y_i(A)]\) and \(x_i=E[Y_i(B)]\), each in \([0,1]\). Half-credit
pair comparison gives the observed score

\[
o_{ij}=\frac12+\frac12(a_i-a_j).
\]

The unobserved context-\(B\) means \(x\in[0,1]^K\) are unrestricted. The
equal-context target score and target policy ordering are

\[
q_{ij}=\frac12+\frac14\{(a_i+x_i)-(a_j+x_j)\},
\qquad
\operatorname{rank}(i)=\operatorname{rank}(a_i+x_i).
\]

Only differences in \(a\) are observed. Let

\[
D=\max_i a_i-\min_i a_i,
\]

which is invariant to the unidentified common offset.

For an ex-ante policy lottery \(p\) and any fixed opponent-reference
distribution \(r\), retain P2's completion-specific Borda regret.

## Fixed propositions

1. For each observed pair, its compatible equal-target score interval is
   \[
   q_{ij}\in[o_{ij}/2,(o_{ij}+1)/2].
   \]
   It has constant width \(1/2\), and it strictly straddles \(1/2\) exactly
   when \(o_{ij}\in(0,1)\).
2. \(D<1\) is equivalent to every ordered observed pair score lying strictly
   between zero and one.
3. If \(D<1\), every policy \(w\) is a compatible unique target winner:
   choose \(x=e_w\), so
   \(a_w+1>a_j\) for all \(j\ne w\).
4. At the boundary \(D=1\), any policy attaining \(\min a\) cannot be a
   compatible unique winner when another policy attains \(\max a\). This
   establishes that strict interiority is a real boundary, not a cosmetic
   proof condition.
5. Opponent-reference weights cancel from regret, and for fixed observed
   profile \(a\),
   \[
   \mathcal R(p;a)=\frac14\left[
   1-p^\top a+\max_w(a_w-p_w)
   \right].
   \]
   Adding a common offset to \(a\) leaves the formula unchanged. For constant
   \(a\), it reduces exactly to H231's
   \(\mathcal R(p)=(1-\min_i p_i)/4\).

The protocol does not fix or claim a general closed form for the minimax
lottery under heterogeneous \(a\). Numerical examples may be retained as
exploratory diagnostics, but the five propositions above govern promotion.

## Computation and staged gates

### Stage 0: exact known answers

- Verify the pair interval at \(o=0,1/4,1/2,3/4,1\).
- Verify all-policy winner compatibility for
  \(a=(0,1/4,1/2)\) and \(a=(0,1/3,2/3,5/6)\).
- Verify the boundary failure for \(a=(0,1/2,1)\).
- Verify the regret formula against all \(2^K\) context-\(B\) vertices for
  uniform, singleton, and unequal lotteries.

Stage 0 must pass before the census.

### Stage 1: exhaustive rational census

For \(K=3,\ldots,6\), enumerate every nondecreasing profile on the denominator-6
grid with minimum zero. Check:

- every profile with maximum below one admits every policy as a unique winner;
- every profile with maximum one rejects every minimum-\(a\) policy as a
  unique winner;
- the regret formula matches exhaustive context-\(B\) vertex enumeration for
  the fixed candidate lotteries; and
- offset invariance holds for every profile that can be shifted upward by one
  grid unit while remaining in \([0,1]^K\).

### Stage 2: method-distinct challenge

A Node implementation using exact integer/rational arithmetic must not import
or execute the Python producer. It must independently:

- enumerate denominator-5 profiles for \(K=3,\ldots,6\);
- verify the interior and boundary winner results;
- verify the regret formula for the fixed lotteries and every binary
  context-\(B\) vertex;
- check the five pair-interval known answers; and
- bind its result to the protocol, producer, and canonical producer-result
  hashes.

Mutation tests must reject a non-strict \(D\leq1\) interior rule, an interval
width other than \(1/2\), removal of the \(p^\top a\) term, and a claimed
unique minimum-profile winner at \(D=1\).

## Interpretation and stop conditions

Passing supports an open-set, constant-route, equal-weight, shared-binary-
success non-identification theorem. It does not establish the result for
candidate-dependent routing, unequal context weights, noisy estimated
observations, arbitrary primitive edge laws, or an empirical robot benchmark.

Stop and retain an adverse result if any valid \(D<1\) profile fails to admit
every policy as a unique winner, the regret expression disagrees with exact
vertex enumeration, or the method-distinct challenge fails. Sampling
uncertainty is a separate future question and must not be implied by this
structural result.
