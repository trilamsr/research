# H212 zero-reference-weight boundary independent challenge

Date: 2026-07-28

Status: pass; the value and complete optimizer segment extend unchanged to
nonnegative reference weights. No critical or material concern remains.

## Independently derived result

Let \(a=r_{(1)}\leq b=r_{(2)}\leq g=r_{(3)}\), now allowing zeros, and write
the bracketed reduced-objective terms as \(F_w\). For indices 1 and 2
attaining the two smallest weights,

\[
F_1+F_2
\geq 2-p_1-p_2+|p_1+p_2-a-b|
\geq 2-a-b.
\]

The lower bound therefore remains \((2-a-b)/8\). Equality forces every
tail cross-product \(r_jp_i-r_ip_j\) to vanish. The tail has positive total
reference weight because \(K\geq3\) and \(a+b<1\), so this also forces
\(p_i=0\) at any zero-weight tail index and, for one common
\(\lambda\), \(p_i=\lambda r_i\) throughout the tail. No division by a zero
reference weight is needed.

Solving \(F_1=F_2=(2-a-b)/2\) yields exactly H188's lottery segment. For each
tail index \(j\),

\[
F_j-\frac{2-a-b}{2}=2h-(r_j-b).
\]

Consequently the complete minimizer set remains

\[
0\leq h\leq \frac{g-b}{2},
\qquad
\mathcal R^\star=\frac{2-a-b}{8},
\]

and uniqueness remains equivalent to \(b=g\).

The boundary has a useful non-obvious interpretation. With exactly two
zero-reference policies, both may receive the same positive lottery mass
\(h\), up to half the smallest positive reference weight. With at least
three zero-reference policies, \(b=g=0\), the interval collapses and
\(p=r\) is the unique optimizer. Thus “zero reference weight implies zero
lottery mass” is false, but no new optimizer face appears beyond H188's
closed segment.

## Independent exact computation

A separate Node.js implementation using BigInt rational arithmetic, without
importing or executing the producer, reconstructed:

- all 242 fixed zero-pattern/positive-weight cases for \(K=3,\ldots,6\);
- 484 exact optimizer probes and proof-identity checks;
- 247 exact raw target-box endpoint comparisons for \(K\leq5\);
- 14,056 distinct label permutations;
- 40,395 denominator-eight simplex-grid lotteries for \(K\leq5\), including
  60 exact optima, all on the proposed segment; and
- 238 feasible just-outside-segment attacks, all strictly worse.

It agreed with the producer's classification, value, uniqueness condition,
case count, endpoint count, and permutation count. The producer's 242 LP
value checks differed from the exact value by at most
\(5.56\times10^{-17}\); its exact-face directional support checks differed by
at most \(5.19\times10^{-8}\). Those numerical checks are diagnostic only;
the equality-case proof is the canonical completeness argument.

## Attack disposition

The independent challenge rejected value failure, a new boundary optimizer
direction, invalidity of the reduced objective at zero weight, label/tie
dependence, and a larger face with three or more zero weights. It confirmed
only that zero reference weight does not always imply zero lottery mass.

Three pre-retention count/control assertions failed closed and were corrected:
the singleton-lottery known answer is \(1/2\), not \(1/4\); unique segments
contribute one distinct probe rather than three, giving 247 raw-oracle probes;
and four scale-equivalent \(K=3\), support-one cases have no feasible
continuation beyond \(h_{\max}=1/2\), giving 238 rather than 241 outside-face
attacks. None changed a retained computation, theorem, classification, or
acceptance threshold.

## Disposition and boundary

H212 supports
`value_and_optimizer_extend_without_change`. P2 may replace H188's
strictly-positive reference restriction with the closed simplex
\(r_i\geq0,\sum_i r_i=1\), while retaining every other construction and
interpretation boundary. This does not choose empirical reference weights,
privilege an optimizer on a nonunique segment, extend to another uncertainty
law, or produce a deployment recommendation.

Canonical artifacts:

- [protocol](protocol-h212-zero-reference-weight-edge-box-boundary.md);
- [producer result](result-h212-zero-reference-weight-edge-box-boundary.json);
- [independent challenge](result-h212-zero-reference-weight-edge-box-boundary-independent-challenge.json).
