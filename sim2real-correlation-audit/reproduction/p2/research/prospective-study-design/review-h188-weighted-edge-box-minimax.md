# H188 weighted edge-box minimax independent challenge

Date: 2026-07-28

Status: pass; no critical or material theorem or scope issue.

## Independent derivation

For winner \(w\), let \(c_i=\mathbf 1\{i=w\}-p_i\). The midpoint contribution
cancels because \(\sum_i c_i=0\), and each independent target edge contributes

\[
\frac14|r_jc_i-r_ic_j|.
\]

Edges incident to \(w\) sum to \(1-p_w\), giving

\[
\mathcal R(p)=\frac14\max_w\left[
1-p_w+\sum_{i<j,\ i,j\ne w}|r_jp_i-r_ip_j|
\right].
\]

Let \(a=r_{(1)}\le b=r_{(2)}\le g=r_{(3)}\), choose indices 1 and 2
attaining \(a,b\), and write the bracketed objectives as \(F_w\). Then

\[
F_1+F_2\ge
2-p_1-p_2+|p_1+p_2-a-b|\ge2-a-b.
\]

Therefore

\[
\mathcal R^\star\ge(2-a-b)/8.
\]

Equality forces every \(i\ge3\) to share \(p_i/r_i=\lambda\), with
\(F_1=F_2=(2-a-b)/2\). Setting
\(h=p_1-(a+b)/2\) gives

\[
\lambda=\frac{2-a-b}{1-a}\left(\frac12-\frac h{1-a-b}\right)
\]

and exactly the protocol's lottery segment. For every \(j\ge3\),

\[
F_j-\frac{2-a-b}{2}=2h-(r_j-b).
\]

Hence the segment is both sufficient and complete precisely when

\[
0\le h\le(g-b)/2.
\]

The minimizer is unique iff \(b=g\). All tie regimes are label-invariant.
Uniform reference weights reduce uniquely to H186.

## Independent computation

A separate raw target-box endpoint oracle checked:

- 486 ordered rational reference vectors for \(K=3,4,5\);
- 1,458 exact segment points;
- 486 just-outside-segment points;
- 155 permuted optimal-face cases over 4,872 directions; and
- all 64 endpoints for the explicit non-uniqueness counterexample.

No optimizer outside the proposed segment was found. Numerical LP optima
agreed with the exact theorem within \(1.23\times10^{-15}\). The explicit case

\[
r=(1/10,1/5,3/10,2/5),\quad h=1/40
\]

gives

\[
p=(7/40,19/90,221/840,221/630),\qquad
\mathcal R=17/80,
\]

rejecting the preliminary strong uniqueness conjecture.

## Disposition and boundary

H188 passes for positive reference weights, \(K\ge3\), the weighted-Borda
full compatible edge box, and ex-ante expected regret. It is not a theorem
about every observed law, empirical roster, or realized-policy regret.
