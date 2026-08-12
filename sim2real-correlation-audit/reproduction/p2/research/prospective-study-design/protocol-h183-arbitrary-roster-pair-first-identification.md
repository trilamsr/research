# Protocol: H183 arbitrary-roster pair-first identification

Date fixed: 2026-07-28

Status: fixed before implementing or evaluating the arbitrary-\(K\)
construction.

## Question

Is H151's pair-first/common-context non-identification result confined to a
three-policy toy, or, for every integer \(K\geq3\), does there exist a
\(K\)-policy construction in which the same observational equivalence reverses
the unique global winner?

This is a theory-scope test. It may strengthen the exact formal component of
P2, but it cannot establish field prevalence, current benchmark execution, or
the correctness of any public leaderboard.

## Fixed construction

For each integer \(K\geq3\):

1. retain policies 0, 1, and 2 as the H151 core;
2. retain the H151 pair-first routes and observed half-win law for pairs
   01, 02, and 12;
3. add policies \(3,\ldots,K-1\);
4. set every core-versus-added common-target and observed edge to a certain
   core win in both worlds;
5. set every added-versus-added edge to a half-win in both worlds; and
6. keep the H151 low and high completions only on the three core edges.

Use the uniform-reference Borda value with a self half-win:

\[
V_i={1\over K}\left\{{1\over2}+\sum_{j>i}q_{ij}
 +\sum_{j<i}(1-q_{ji})\right\}.
\]

## Fixed claims to test

The construction passes only if exact rational arithmetic proves:

1. both worlds have the same observed pair/context/outcome law for all
   \(\binom K2\) pairs;
2. every pair has positive support;
3. the pair-conditioned global maximizer set is exactly \(\{0,1,2\}\);
4. policy 2 is the unique common-context winner in the low world;
5. policy 0 is the unique common-context winner in the high world;
6. every added policy is strictly below every core policy in both worlds; and
7. choosing either extreme core winner across worlds incurs exact regret
   \(1/K>0\).

Derive and retain the closed forms for every core and added-policy value.
Check them by enumeration for every \(K=3,\ldots,32\). The finite enumeration
is an implementation check; the symbolic construction carries the
arbitrary-roster statement.

For \(m=K-3\) added policies, the pair-conditioned core numerator is
\(m+3/2=K-3/2\). The low-world core numerators are
\(m+1,m+3/2,m+2\), the high-world numerators reverse the first and third,
and every added-policy numerator is \(m/2=(K-3)/2\). Division by \(K\)
gives the recorded Borda values. The weakest core exceeds any added policy by
\((K-1)/(2K)>0\), and carrying either extreme winner into the opposite
selected world has regret \(1/K\).

## Failure and stop rules

- If an added policy can tie or beat a core policy, stop and do not repair the
  construction after inspecting other favorable variants.
- If the observed laws differ, stop.
- If the unique-winner reversal or \(1/K\) regret identity fails at any checked
  \(K\), preserve the adverse result and return P2 to the \(K=3\) scope.
- Do not use public outcomes or expand the empirical roster for this test.

## Advancement

A pass promotes only the formal scope from an exact \(K=3\) witness to the
existential arbitrary finite-roster embedding above. Padding with dominated
policies does not show roster-wide ambiguity or empirical prevalence, and its
extreme-winner transfer regret shrinks as \(1/K\). That quantity is not the
two-world minimax regret: policy 1 has worst regret \(1/(2K)\). Independent
symbolic or separately implemented challenge is required before manuscript
reliance.
