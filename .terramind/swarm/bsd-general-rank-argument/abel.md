# Abel smoothing and the coefficient-only prime criterion

## Result

Let (E/\mathbb Q) be an elliptic curve, let (N_p=\#E_{ns}(\mathbb F_p)), and use the usual good/bad local conventions. Suppose, as an explicit hypothesis, that for some real (R)

\[
 \log P_E(x)=\sum_{p\le x}\log(N_p/p)=R\log\log x+o(\log\log x). \tag{1}
\]

Then

\[
 \operatorname{ord}_{s=1}L(E,s)=R. \tag{2}
\]

This is a conditional sufficiency result. No assumption that the coefficient in (1) equals Mordell–Weil rank is proved here; establishing (1) with (R=\operatorname{rank}E(\mathbb Q)) for every curve remains a separate, unproved arithmetic problem. The criterion is strictly weaker than Goldfeld's positive-constant all-cutoff product asymptotic: (1) only gives (P_E(x)=(\log x)^{R+o(1)}), and asserts no limiting positive multiplicative constant.

## Abel transform from (1)

Put (b_p=\log(N_p/p)), (u=\log x), and (A(u)=\sum_{\log p\le u}b_p=\log P_E(e^u)). Hypothesis (1) says (A(u)=R\log u+o(\log u)), in particular (A(u)=O(\log(2+u))). Define the ordered prime sum

\[
 F(t)=\sum_p b_p p^{-t}=\int_{0^-}^\infty e^{-tu}\,dA(u).
\]

For every complex (t) with (\Re t>0), Stieltjes partial summation gives

\[
 F(t)=t\int_0^\infty A(u)e^{-tu}\,du,
\]

up to the harmless fixed lower-endpoint convention. The boundary term (e^{-tu}A(u)\) tends to zero; the integral converges locally uniformly on (\Re t>0\). Thus this ordered series converges there and defines a holomorphic function. Hasse alone gives only absolute convergence for (\Re t>1/2), since (b_p=O(p^{-1/2})); the additional conditional convergence for all (\Re t>0\) comes from (1), not from Hasse.

For positive real (t\downarrow0), substitute (v=tu) in the integral. Since

\[
 t\int_0^\infty e^{-tu}\log u\,du=\log(1/t)+O(1),
\]

and for each \(\epsilon>0\) the tail error satisfies \(|A(u)-R\log u|\le\epsilon\log u\) beyond some fixed (U\), while the initial interval contributes (O(t)\), this proves

\[
 F(t)=R\log(1/t)+o(\log(1/t)). \tag{3}
\]

This is an Abelian implication; no Tauberian converse is used.

## Compare with the Euler logarithm

At good primes (a_p=p+1-N_p), \,\(|a_p|\le2\sqrt p\), and

\[
 L_p(E,s)=(1-a_pp^{-s}+p^{1-2s})^{-1}.
\]

At bad primes the factor is degree one, (L_p=(1-a_pp^{-s})^{-1}), with (a_p\in\{0,\pm1\}). For (\Re s>3/2), Hasse's bound ensures absolute convergence of the Euler product and its logarithmic series. Set (s=1+t). In the half-plane (\Re t>1/2), define the holomorphic correction by the absolutely convergent expression

\[
 C(t)=\log L(E,1+t)+F(t),
\]

where the logarithm is the Euler logarithm there. At a good prime its local summand is

\[
 c_p(t)=-\log(1-a_pp^{-1-t}+p^{-1-2t})
       +p^{-t}\log(1-a_p/p+1/p).
\]

The linear (a_p/p^{1+t}) terms cancel. Expand each logarithm in its convergent local power series for sufficiently large (p); the remaining quadratic terms are bounded in absolute value by a constant times

\[
 \frac{p^{-t}-p^{-2t}}p
\]

for positive real (t), using (a_p^2\le4p). All terms of degree (k\ge3) are bounded uniformly for (t\ge0) by a constant multiple of (p^{-3/2}) (and higher summable powers), using Hasse. The finitely many small good primes can be retained as finite holomorphic summands; their logarithm arguments have no zeros for \(\Re t>0\), as follows from the local roots having modulus \(\sqrt p\) and \(|p^{-1-t}|<p^{-1}\). Bad primes contribute finitely many holomorphic terms on this half-plane and are bounded as (t\downarrow0\).

More precisely, the degree-two grouped series is normally convergent on compact subsets of \(\Re t>0\): on a compact with \(\Re t\ge\sigma>0\), its terms are (O(p^{-1-\sigma})). Thus the local correction defines a holomorphic (C(t)) on \(\Re t>0\), agreeing with the Euler-log expression where \(\Re t>1/2\). Its degree-two contribution need not have an absolutely convergent limit at (t=0\), but on the positive real approach it is bounded by

\[
 \sum_p\frac{p^{-t}-p^{-2t}}p=\log\zeta(1+t)-\log\zeta(1+2t)+O(1)=\log2+o(1).
\]

The (O(1)) here comes from subtracting the prime powers (m\ge2\) in the zeta logarithms; that difference is absolutely convergent and has a finite limit at (t=0\). Since \(\zeta(1+t)\sim1/t\), the displayed difference has the stated finite limit. This explicitly handles the prime-square boundary term: its pieces separately have divergent absolute majorants at zero, whereas the grouped difference is bounded. Consequently \(C(t)=O(1)\) for real (t\downarrow0\).

The local Euler logarithm is absolutely convergent only for \(\Re(s)>3/2\); no prime-by-prime logarithm is asserted beyond its domain. Instead, (C(t)) is continued by its normally convergent grouped local correction. On \(\Re t>1/2\),

\[
 L(E,1+t)=\exp(C(t)-F(t)).
\]

Both sides are holomorphic on \(\Re t>0\): (F,C) by the arguments above, and (L) by modularity/analytic continuation. The identity theorem extends this identity to the whole half-plane. This use of the identity theorem does not assume zero-freeness or choose a continued logarithm branch. It implies nonvanishing in \(\Re t>0\) under premise (1).

Now (3) and boundedness of (C(t)\) give

\[
 \log|L(E,1+t)|=-F(t)+\Re C(t)
 =-R\log(1/t)+o(\log(1/t)).
\]

If (r_{an}=\operatorname{ord}_{s=1}L(E,s)), holomorphy gives (L(E,1+t)=t^{r_{an}}g(t)) with (g(0)\ne0\); hence \(\log|L(E,1+t)|=-r_{an}\log(1/t)+O(1)\). Comparing coefficients proves (2). No real-zero-free hypothesis is needed in this deduction.

Bad-prime normalization changes (F) and (C) only by finite holomorphic terms and cannot change the logarithmic coefficient. The boundary (\Re(s)=3/2\) is exactly where Hasse ceases to guarantee absolute convergence of the original Euler logarithm; the continuation argument starts strictly to its right and does not claim convergence on that boundary.

## What remains unproved arithmetically

For a Mordell–Weil basis (P_1,\ldots,P_r\) modulo torsion, reduction maps the subgroup generated by the points into (E(\mathbb F_p)\). Its order divides (N_p\), but independence over \(\mathbb Q\) supplies no uniform lower bound for that image's order as (p\) grows, and gives no adequate estimate for (a_p\). Fixed-modulus Kummer/Chebotarev information does not provide the growing-modulus uniformity needed to control all prime cutoffs.

The exact missing universal claim is: for every (E/\mathbb Q\),

\[
 \sum_{p\le x}\log(N_p/p)=r_{MW}\log\log x+o(\log\log x).
\]

A proof of this estimate would combine with the conditional argument above to give weak BSD. Neither the estimate nor a counterexample is established here. It cannot be inferred just from the reduction of a fixed basis. Conversely, assuming the stronger sharp-cutoff asymptotic with a positive constant invokes Goldfeld's theorem and does not establish this weaker premise from arithmetic.

## Literature

- D. Goldfeld, “Sur les produits eulériens attachés aux courbes elliptiques,” *Comptes Rendus Acad. Sci. Paris* 294 (1982), 471–474. Its sharp partial-product implication is reproduced in the source below; this note makes no novelty claim.
- K. Conrad, “Partial Euler Products on the Critical Line,” *Canadian Journal of Mathematics* 57 (2005), 267–296, Theorem 1.1 (Goldfeld), Theorem 1.3 and Corollary 5.7. [Publisher PDF](https://www.cambridge.org/core/services/aop-cambridge-core/content/view/061A145952B0C1145EE31E0EAD47ED93/S0008414X0001871Xa.pdf/partial_euler_products_on_the_critical_line.pdf).
- A. Sheth, “Euler Product Asymptotics for L-functions of Elliptic Curves,” *IMRN* 2025, no. 14, rnaf214. [arXiv paper](https://arxiv.org/abs/2312.05236), [journal version](https://doi.org/10.1093/imrn/rnaf214). The RH-conditional result is outside a set of finite logarithmic measure and recovers Goldfeld's implication; it does not establish the coefficient-only point-reduction estimate claimed as missing above.
- Modularity of elliptic curves over \(\mathbb Q\) supplies analytic continuation of \(L(E,s)\); the good/bad local factors and Hasse absolute-convergence boundary are standard and are also summarized in the introduction to Sheth's paper. The local comparison, zeta difference and Abel transform here are derived directly.

## Scope

The analytic deduction from (1) to (2) is proved above, including conditional convergence of (F), grouped prime-square control, bad primes, the absolute-convergence boundary, and continuation without a zero-free or branch assumption. The arithmetic estimate making (R=r_{MW}\) for every curve remains unproved. Therefore this note does not derive unconditional weak BSD.
