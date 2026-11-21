# Independent review of the Abel-smoothed rank criterion

## Verdict

The proposed local comparison is valid when expanded using the normalized Frobenius roots, including the full quadratic contribution from \(\log(N_p/p)\). For a good prime let \(u=\alpha_p/p\), \(v=\beta_p/p\), and \(z=p^{-t}\). Then \(|u|=|v|=p^{-1/2}\), \(u+v=a_p/p\), \(uv=1/p\), and
\[
 N_p/p=(1-u)(1-v).
\]
In the domain of absolute convergence, termwise logarithmic expansion gives the exact local summand
\[
 \log L_p(E,1+t)+z\log(N_p/p)
 =\sum_{k\ge1}\frac{u^k+v^k}{k}(z^k-z).
\]
The \(k=1\) term is identically zero. The \(k=2\) term is bounded by \((z-z^2)/p\) for real \(0<z<1\). The terms \(k\ge3\) have a summable \(O(p^{-3/2})\) majorant as real \(t\downarrow0\). Thus the earlier review’s claim of an uncancelled prime-zeta term was wrong: it arose by keeping the linear term in the scalar logarithm while dropping its quadratic term, whose \(a_p^2/p^2\) contribution is also of order \(1/p\). The exact identity cancels all of that first-order-in-\(z\) residue at once.

With the correction series defined by these grouped local terms (and the finitely many bad-prime terms), it is normally convergent on compact subsets of \(\Re t>0\). Its real-axis value is bounded as \(t\downarrow0\), by the prime-zeta difference for the \(k=2\) terms and absolute summability for \(k\ge3\). Consequently the analytic deduction in \(abel.md\) is sound conditional on its displayed premise:
\[
 \sum_{p\le x}\log(N_p/p)=R\log\log x+o(\log\log x)
 \quad\Longrightarrow\quad
 \operatorname{ord}_{s=1}L(E,s)=R.
\]
The implication is an Abelian one; no converse or unconditional rank estimate is supplied. The arithmetic premise with \(R=\operatorname{rank}E(\mathbb Q)\) remains unproved.

## Abel transform

Writing \(A(u)=\sum_{\log p\le u}\log(N_p/p)\), the hypothesis gives \(A(u)=R\log u+o(\log u)\), hence \(A(u)=O(\log(2+u))\). Stieltjes partial summation gives the ordered series
\[
 F(t)=\sum_p\log(N_p/p)p^{-t}=t\int_0^\infty A(u)e^{-tu}\,du
\]
for \(\Re t>0\), with a consistent lower-endpoint convention. The boundary term vanishes, and the integral converges locally uniformly there. This proves conditional convergence and holomorphy throughout \(\Re t>0\); Hasse alone would give absolute convergence only for \(\Re t>1/2\). On the positive real axis, the same premise and the substitution \(v=tu\) yield \(F(t)=R\log(1/t)+o(\log(1/t))\).

## Exact local comparison and bounds

For good \(p\), the Euler factor at \(1+t\) is \(((1-uz)(1-vz))^{-1}\), while the product coefficient is \((1-u)(1-v)\). Since \(|uz|,|vz|<1\) for \(\Re t>0\), the logarithmic power-series identity is valid there locally, with branches fixed by the convergent series. Its grouped \(k=2\) term is
\[
 \frac{u^2+v^2}{2}(z^2-z),\qquad
 \left|\frac{u^2+v^2}{2}(z^2-z)\right|\le (z-z^2)/p
\]
for positive real \(t\), because \(|u^2+v^2|\le2/p\). For a compact subset of \(\Re t>0\), \(|z|\le p^{-\sigma}\) for some \(\sigma>0\), so the terms are \(O(p^{-1-\sigma})\) and normally summable. On the real axis their total absolute value is bounded by
\[
 \sum_p\frac{p^{-t}-p^{-2t}}p
 =\log\zeta(1+t)-\log\zeta(1+2t)+O(1)
 \longrightarrow\log 2.
\]
The prime-power correction represented by \(O(1)\) converges to a finite limit as \(t\downarrow0\). Separately, for \(k\ge3\), on compact subsets the terms are bounded by a constant times \(p^{-k/2}(1+p^{-k\sigma})\); summing over \(k\ge3\) gives a prime-summable majorant, uniformly down to real \(t=0\). This proves normal convergence of the grouped correction and boundedness on the real approach.

At bad primes there are only finitely many degree-one factors and finitely many terms in \(F\). They can be combined directly into the correction and are holomorphic and bounded near \(t=0\) on the positive real axis. Any consistent finite bad-prime normalization changes no logarithmic coefficient.

The Euler logarithm itself is initially used only for \(\Re(1+t)>3/2\), where Hasse gives absolute convergence. The grouped correction defines a holomorphic function on \(\Re t>0\), agreeing with \(\log L(E,1+t)+F(t)\) in that initial domain. Exponentiating there gives \(L(E,1+t)=\exp(C(t)-F(t))\). Both sides are holomorphic on \(\Re t>0\), so the identity theorem extends the equality throughout that half-plane; this does not assume a continued logarithm or zero-freeness. Under the premise, it conditionally implies nonvanishing for real \(t>0\), as a consequence rather than an input.

Finally, if the analytic order is \(m\), holomorphy gives \(L(E,1+t)=t^m g(t)\), \(g(0)\ne0\), and therefore \(\log|L(E,1+t)|=-m\log(1/t)+O(1)\). Since \(C(t)=O(1)\) and \(F(t)=R\log(1/t)+o(\log(1/t))\), comparison yields \(m=R\), with the sign consistent with a central zero.

## Remaining arithmetic question

Nothing in this analytic argument proves the required asymptotic from Mordell–Weil rank. The precise missing universal assertion is, for every elliptic curve \(E/\mathbb Q\),
\[
 \sum_{p\le x}\log(N_p/p)
 =\operatorname{rank}E(\mathbb Q)\log\log x+o(\log\log x).
\]
Reduction of a fixed Mordell–Weil basis supplies no uniform lower bound for the order of its image in \(E(\mathbb F_p)\) as \(p\) grows, and fixed-modulus Kummer/Chebotarev information does not supply the required all-cutoff uniformity. This estimate (or a different unconditional argument identifying analytic and algebraic rank) remains open in this work. No unconditional weak BSD implication is established.
