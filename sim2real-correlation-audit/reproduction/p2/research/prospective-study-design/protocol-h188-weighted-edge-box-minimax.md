# Protocol: H188 weighted full-edge-box minimax

Date fixed: 2026-07-27

Status: result-exposed validation protocol. H188 was recorded after preliminary
optimization suggested a water-filling rule. An independent derivation then
identified the exact value and a non-unique minimizer regime before this
canonical implementation.

## Question

H186 uses a uniform reference distribution over policies. Let positive
reference weights \(r_i\) sum to one and define

\[
V_i=\sum_j r_jq_{ij},\qquad q_{ii}=1/2,\quad
q_{ij}\in[1/4,3/4],\quad q_{ji}=1-q_{ij}.
\]

For an ex-ante lottery \(p\), determine

\[
\inf_p\sup_q\{\max_i V_i-\sum_i p_iV_i\}
\]

exactly. Preserve a counterexample to H188's preliminary uniqueness
conjecture.

## Proposed exact result to validate

Order \(a=r_{(1)}\le b=r_{(2)}\le g=r_{(3)}\), choose indices 1 and 2
attaining \(a,b\), and put \(C=1-a-b\). The proposed minimax value is

\[
\mathcal R^\star=(2-a-b)/8.
\]

The complete proposed minimizer segment is indexed by
\(0\le h\le(g-b)/2\):

\[
p_1=(a+b)/2+h,
\]

\[
p_2=\frac{b(2-a-b)}{2(1-a)}+\frac{1-b}{1-a}h,
\]

\[
p_i=r_i\frac{2-a-b}{1-a}\left(\frac12-\frac hC\right),
\quad i\notin\{1,2\}.
\]

Thus the preliminary water-filling lottery is the \(h=0\) endpoint. It is
unique only when \(b=g\). Uniform weights must reduce exactly to H186.

## Validation

1. Implement the reduced exact edge-extrema objective
   \[
   \mathcal R(p)=\frac14\max_w\left[
   1-p_w+\sum_{i<j,\ i,j\ne w}|r_jp_i-r_ip_j|
   \right].
   \]
2. Independently enumerate raw target-box endpoints and compute weighted
   Borda regret for rational cases at \(K=3,\ldots,6\).
3. Test every tie regime, permutations, segment endpoints/interiors, invalid
   \(h\), raw-weight normalization, H186's uniform reduction, and an interior
   non-water-filling minimizer.
4. Preserve non-uniqueness and do not select \(h=0\) as uniquely preferred.

## Scope

This is one constructed compatible edge box and one weighted Borda target.
It is not an empirical policy recommendation, a theorem for every observed
law, or realized-policy regret.
