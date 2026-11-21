# Abel smoothing and a weaker prime-product criterion

## Conclusion

Let

\[
 P_E(x)=\prod_{p\le x}N_p/p,
 \qquad N_p=\#E_{\rm ns}(\mathbb F_p),
\]

with the standard good- and bad-prime conventions. The weaker statement

\[
 \log P_E(x)=R\log\log x+o(\log\log x) \tag{1}
\]

does have an Abelian consequence: a particular Laplace smoothing of the *local logarithms* has coefficient \(R\) in front of \(\log(1/t)\). This is a genuine weakening of the sharp-cutoff constant asymptotic. It does **not**, by itself, identify \(R\) with the order of vanishing of \(L(E,s)\). The smoothed local logarithms are not \(\log L(E,1+t)\), and the discrepancy contains prime-power terms that are not absolutely summable at the boundary. Even after supplying the needed local correction, continuation only gives the analytic order; connecting that to Mordell–Weil rank is the BSD assertion unless an independent arithmetic theorem supplies it.

Thus (1) is not a proved route to weak BSD. It is a weaker arithmetic hypothesis whose analytic interpretation needs additional input, not an unconditional estimate derived from point reductions.

## The Abelian calculation (proved)

Set \(b_p=\log(N_p/p)\), \(u=\log x\), and

\[
 A(u)=\sum_{\log p\le u}b_p=\log P_E(e^u).
\]

For \(t>1/2\), the smoothed sum

\[
 S(t)=\sum_p b_p p^{-t}=\int_{0^-}^{\infty}e^{-tu}\,dA(u)
\]

converges absolutely. Indeed Hasse gives \(N_p/p=1+O(p^{-1/2})\), hence \(b_p=O(p^{-1/2})\), and \(\sum_p p^{-1/2-t}\) converges for \(t>1/2\). This only justifies the transform in that half-line, not near \(t=0\). The Abelian limit is therefore not defined by this series without a stronger summability statement. The Stieltjes integral has the same issue: the crude Hasse bound does not imply its convergence for small \(t\).

There is, however, a standard abstract Abelian implication if one assumes the additional convergence/growth hypotheses needed to define the transform near zero. If \(A(u)=R\log u+o(\log u)\), has bounded variation on compact intervals, and \(S(t)=\int e^{-tu}dA(u)\) converges for every \(t>0\), integration by parts yields

\[
 S(t)=t\int_0^\infty e^{-tu}A(u)\,du,
\]

up to a fixed lower-endpoint term. Substituting \(v=tu\), using \(\log(v/t)=\log(1/t)+\log v\), and splitting the integral into a compact range of \(v\) and its tails gives

\[
 S(t)=R\log(1/t)+o(\log(1/t)). \tag{2}
\]

For the error term, for every \(\epsilon>0\) choose \(U\) such that \(|A(u)-R\log u|\le\epsilon\log u\) for \(u\ge U\); then \(t\int_U^\infty e^{-tu}\log u\,du=O(\log(1/t))\), while the fixed initial interval contributes \(O(t)\). This proves the claimed little-oh after letting \(\epsilon\to0\). But for the actual \(b_p\), (1) alone does not give convergence of \(S(t)\) for \(0<t\le1/2\). The formal Abelian passage is therefore conditional, not a consequence of (1) plus Hasse.

This convergence defect matters: \(b_p\sim -a_p/p\) in magnitude can be as large as \(p^{-1/2}\); absolute convergence of \(\sum_p b_pp^{-t}\) is guaranteed only for \(t>1/2\). A conditional/regularized transform could still exist, but must be proved by additional cancellation estimates, which are not encoded in (1).

## Why this is not the logarithm of the L-function

At good primes write \(a_p=p+1-N_p\). The local factor is

\[
 L_p(E,s)=(1-a_pp^{-s}+p^{1-2s})^{-1}.
\]

At \(s=1\), \(b_p=\log(1-a_p/p+1/p)=-\log L_p(E,1)\) exactly. But the Abel weight in (2) gives

\[
 \sum_p p^{-t}\log(1-a_p/p+1/p),
\]

whereas the Euler logarithm in its region of absolute convergence is

\[
 \log L(E,1+t)=\sum_p\sum_{m\ge1}
 \frac{\alpha_p^m+\beta_p^m}{m p^{m(1+t)}}
\]

at good primes, with \(\alpha_p+\beta_p=a_p\), \(\alpha_p\beta_p=p\); bad primes have the degree-one factor \((1-a_pp^{-s})^{-1}\). These are different weights and different local expansions. In particular the \(m=2\) term has size \((a_p^2-2p)/(2p^{2+2t})\); its absolute majorant from Hasse is \(O(1/p^{1+2t})\), summable for every \(t>0\) but **not** absolutely summable at \(t=0\). Higher prime powers are boundary-summable, while this square term is the boundary obstruction. The fact that the prime-square series converges for each positive \(t\) does not allow replacing its limit by an absolutely convergent value at zero; its possible logarithmic contribution has to be computed/controlled.

There is also a first-order mismatch: expanding \(b_p\) at good primes gives

\[
 b_p=-a_p/p+1/p-a_p^2/(2p^2)+O(p^{-3/2})
\]

with a uniform Hasse-based remainder of this order for sufficiently large \(p\) (more exactly the next cubic term is \(O(p^{-3/2})\)). The \(1/p\) and quadratic terms each have divergent prime sums at the boundary. Their net contribution cannot be dropped as an \(O(1)\) error. Determining it requires second-moment information about Frobenius traces, or an equivalent symmetric-square input. Accordingly, (2), even if its convergence is supplied, is a statement about the transform of \(b_p\), not about \(\log L(E,1+t)\).

Bad primes are finite in number. Their factors \(b_p=\log(1-a_p/p)\) are finite because \(N_p>0\); changing or omitting them changes every relevant cumulative sum by a constant and does not affect a logarithmic coefficient. They cannot repair the good-prime square-term issue.

## What analytic continuation does give

Modularity gives analytic continuation of \(L(E,s)\) to the whole plane and the functional equation. If \(r_{\rm an}=\operatorname{ord}_{s=1}L(E,s)\), then locally

\[
 L(E,1+t)=t^{r_{\rm an}}g(t),\qquad g(0)\ne0,
\]

so along positive real \(t\downarrow0\), once a local logarithm of the nonzero function \(g\) is chosen,

\[
 \log |L(E,1+t)|=r_{\rm an}\log t+O(1).
\]

The coefficient is the analytic order, by definition. But this local logarithm is not automatically the branch obtained from the Euler product: the Euler product and its logarithm are absolutely convergent only for \(\Re(s)>3/2\), by Hasse. Continuing the *function* does not continue the prime-by-prime logarithmic expansion. To connect them through \(1<s\le3/2\) requires zero-free/branch control and an explicit formula or a justified regularization of the prime-power terms. Assuming no zeros in \(\Re(s)>1\) allows a consistent logarithm along the real interval, but does not alone justify the boundary expansion of the raw prime sum.

Conrad's exposition of Goldfeld's theorem makes this distinction important: Goldfeld's sharp partial-product asymptotic with a positive constant implies both the zero-free statement in \(\Re(s)>1\) and \(r_{\rm an}=\operatorname{rank}E(\mathbb Q)\). A coefficient-only hypothesis (1) is weaker and does not meet that theorem's stated hypothesis. Sheth's later converse assumes RH and obtains the sharp product asymptotic only outside a set of finite logarithmic measure; it does not turn the proposed point-reduction estimate into an all-cutoff result.

## Attempt from point reductions and the exact missing input

For a Mordell–Weil basis \(P_1,\dots,P_r\) modulo torsion, good reduction maps the generated subgroup into \(E(\mathbb F_p)\). Its order divides \(N_p\), but independence over \(\mathbb Q\) gives no lower bound for that subgroup's order uniformly in \(p\), and no estimate for the Frobenius trace \(a_p\). Fixed-modulus Kummer/Chebotarev information does not provide the growing-modulus uniformity needed as \(p\) and the product cutoff grow.

For criterion (1), a point-based proof would at minimum need a new theorem giving

\[
 \sum_{p\le x}\log(N_p/p)=r_{\rm MW}\log\log x+o(\log\log x)
\]

for every \(E/\mathbb Q\), together with enough cancellation to define and relate the Abel transform for \(0<t\le1/2\). To infer analytic rank from that arithmetic estimate, it would additionally need a theorem identifying the smoothed local-log transform's coefficient with \(r_{\rm an}\), including the boundary contribution of prime squares and the logarithm branch. Neither follows from reduction of a fixed basis. If one instead assumes the exact sharp-cutoff asymptotic with a positive constant, Goldfeld already gives rank equality; that returns to the stronger original product criterion rather than deriving a genuinely new theorem.

There is a further distinction in the goal: even an unconditional equality \(r_{\rm an}=r_{\rm MW}\) is weak BSD, but extracting \(r_{\rm MW}\) from the product is precisely the unproved arithmetic estimate above. No example or numerical trace data resolves its universal quantifier.

## Literature checked

- D. Goldfeld, “Sur les produits eulériens attachés aux courbes elliptiques,” *Comptes Rendus Acad. Sci. Paris* 294 (1982), 471–474. The stated implication and constant are reproduced in the sources below; this note does not claim a new strengthening of Goldfeld.
- K. Conrad, “Partial Euler Products on the Critical Line,” *Canadian Journal of Mathematics* 57 (2005), 267–296, especially Theorems 1.1 and 1.3 and Corollary 5.7. [Publisher PDF](https://www.cambridge.org/core/services/aop-cambridge-core/content/view/061A145952B0C1145EE31E0EAD47ED93/S0008414X0001871Xa.pdf/partial_euler_products_on_the_critical_line.pdf).
- A. Sheth, “Euler Product Asymptotics for L-functions of Elliptic Curves,” *IMRN* 2025, no. 14, rnaf214. [arXiv:2312.05236](https://arxiv.org/abs/2312.05236); [journal version](https://doi.org/10.1093/imrn/rnaf214). The abstract and theorem state the RH-conditional asymptotic outside a finite-log-measure exceptional set and recover Goldfeld's implication.
- The Euler local factors, Hasse bound, and \(\Re(s)>3/2\) absolute-convergence boundary are also stated in Sheth's introduction and in standard elliptic-curve L-function treatments. The local expansions and Abel calculation above are derived directly here.

## Scope

The Abelian transform calculation is conditional on convergence near \(t=0\); Hasse alone only supplies absolute convergence for \(t>1/2\) for the proposed transform. The analytic continuation calculation determines the analytic order but does not identify the local-log transform with it. The weaker coefficient criterion has not been shown sufficient for weak BSD, and no unconditional estimate from point reductions is established.
