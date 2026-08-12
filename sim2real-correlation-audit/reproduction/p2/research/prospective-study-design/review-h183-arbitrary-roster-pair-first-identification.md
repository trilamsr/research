# H183 arbitrary-roster independent challenge

Date: 2026-07-28

Status: pass with narrowing; critical corrections verified.

## Independent route

An independent challenger reconstructed explicit A/B potential-outcome
schedules and checked the complete construction for every \(K=3,\ldots,200\).
The challenger derived, for \(m=K-3\), pair-conditioned core numerator
\(m+3/2\), low-world core numerators \(m+1,m+3/2,m+2\), their high-world
reversal, and added-policy numerator \(m/2\). Thus the weakest core exceeds an
added policy by \((K-1)/(2K)>0\), the unique winners reverse, and transferring
either extreme winner to the opposite selected world loses \(1/K\).

## Concerns and disposition

1. **Quantifier.** The result is existential for each integer \(K\geq3\), not
   universal over empirical rosters or pair-first designs. The protocol,
   result scope, and hypothesis record now say this explicitly.
2. **Symbolic proof.** Finite enumeration alone did not prove the arbitrary-K
   claim. The exact derivation and dominance inequality are now retained in
   the fixed protocol.
3. **Circular implementation check.** The initial producer built both
   observed-law objects directly from the same observed edge map. It now
   constructs distinct low/high A/B potential schedules, projects each
   observed route independently, and verifies equal projected laws and target
   edges. A regression test protects this path.
4. **Regret scope.** \(1/K\) is the cross-world loss for policies 0 and 2, not
   a two-world minimax floor; policy 1 has worst loss \(1/(2K)\). This is now
   explicit.
5. **Impact boundary.** The construction pads the H151 core with dominated
   policies. It defeats a K=3-only scope objection but does not establish
   richer roster-wide ambiguity or prevalence; the gap shrinks with K.
6. **Normalization.** Values use self half-win and division by \(K\). A
   \(K-1\)-opponent convention preserves ordering but rescales regret.

## Primary verification

After correction, the canonical Python producer and five tests pass, including
an independent projection of the low and high potential schedules at
\(K=3,7,101\). The generated result is byte-stable under `--check`.

## Permitted claim

For every integer \(K\geq3\), there exists a complete-pair-support
construction with the same observed pair/context/outcome law in two compatible
worlds and opposite unique common-context winners. This does not establish
that every roster or pair-first design is unidentified.
