# Central-zero averaging and the all-cutoff premise

## Conclusion

The coefficient-only premise in [abel.md](abel.md),

\[
 \sum_{p\le x}\log(N_p/p)=R\log\log x+o(\log\log x),
 \tag{A}
\]

is already a zero-free assertion in disguise: together with the argument in `abel.md`, it implies that (L(E,s)\) has no zero for \(\Re(s)>1\). The completed elliptic-curve (L)-function has the functional equation (s\leftrightarrow2-s\), and its zeros are closed under conjugation. Reflection therefore rules out zeros with \(\Re(s)<1\) as well. In the critical strip this is precisely RH for (L(E,s)\) (whose central line in this normalization is \(\Re(s)=1\)). This implication does not use BSD. Thus (A) is not a weaker unconditional route around RH; it implies RH even without its positive product constant.

The premise can be rewritten with smooth cutoffs, but the usual compact-Fourier-support explicit formula does not unconditionally isolate the central multiplicity. Its zero side includes every zero. Positivity of a central-zero kernel is available on the critical line, not throughout the plane, and off-line zeros make the standard nonnegative-kernel argument unavailable. The arithmetic input needed to turn a smoothed prime sum into the central multiplicity is still an explicit-formula error estimate that controls all noncentral zeros (or a zero-free/RH hypothesis). No such estimate follows here from point reductions.

## What smoothing does to (A)

Set \(u=\log p\), \(b_p=\log(N_p/p)\), and \(A(u)=\sum_{\log p\le u}b_p\). For a smooth compactly supported weight \(w\) on \([0,\infty)\) that equals 1 near 0, summation by parts gives

\[
 S_w(U)=\sum_p b_p w((\log p)/U)
       =-\int_0^\infty A(u)\,U^{-1}w'(u/U)\,du.
\]

There is no endpoint term since \(A(0)=0\), and \(w'\) is supported away from 0. If (A) holds, \(A(u)=R\log u+o(\log u)\), then \(\int_0^\infty w'(v)\,dv=-1\) and

\[
 S_w(U)=R\log U-R\int_0^\infty \log(v)w'(v)\,dv+o(\log U).
\]

Conversely, a family of sufficiently sharp smooth cutoffs whose errors are uniform enough to recover all sharp cutoffs gives (A) by a Tauberian/unsmoothing step. Such uniformity is substantive: one smoothed statistic at a fixed scale, or a scale average with no error control, is not (A).

This smoothing alone does not remove the RH consequence. Any smoothed hypothesis strong enough to recover the Abel growth (A(u)=R\log u+o(\log u)\) reinstates the proof in `abel.md` and hence RH. A strictly weaker smoothed statement might avoid RH, but then it does not automatically identify its coefficient with the analytic order.

## Explicit formula and the off-line-zero obstruction

Use the standard normalization in which the completed function is centered at (s=1), and write a nontrivial zero as \(\rho=1+z\). For an admissible even entire test function (h) with compactly supported Fourier transform, the explicit formula has the schematic form

\[
 \sum_{\rho} h(\rho-1)
 = \mathcal G_E(h)-\sum_{n\ge1}\frac{c_n}{\sqrt n}
       \bigl(\widehat h(\log n/(2\pi))+\widehat h(-\log n/(2\pi))\bigr),
\]

where (c_{p^k}=(\alpha_p^k+\beta_p^k)\log p\) (with the usual degree-one bad factors), and \(\mathcal G_E\) is the conductor and gamma-factor term. Exact signs and Fourier conventions vary; Bober's Lemma 2.1 gives one precise version. Compact support of \(\widehat h\) makes the prime-power sum finite.

The zero sum is over all nontrivial zeros with multiplicity. If RH is assumed and (h(t)\ge0\) for real (t\), with (h(0)=1\), then

\[
 \sum_\rho h(\rho-1)=r_{an}+\sum_{\rho\ne1}h(\rho-1)\ \ge r_{an}.
\]

This is the central mechanism in Bober's rank bound. Without RH, write (z=\beta+i\gamma\). Even when \(h(t)\ge0\) for real (t\), (h(\beta+i\gamma)\) need not be real or nonnegative. The functional equation pairs (z\) with \(-z\); conjugation pairs (z\) with \(\bar z\). For an even real-type (h\), a quartet contributes (2h(z)+2h(\bar z)=4\operatorname{Re}h(z)\), which has no fixed sign. Symmetry does not turn it into a nonnegative term.

There is also a quantitative obstruction to shrinking a compact-Fourier-support kernel around the center. If \(\operatorname{supp}\widehat h\subset[-\Delta,\Delta]\), Fourier inversion gives the Paley–Wiener growth bound

\[
 |h(x+iy)|\le C_h e^{2\pi\Delta|y|}
\]

(with polynomial factors allowed for the usual smooth compactly supported transform). Thus the decay of (h\) on the real line supplies no uniform decay in the transverse, off-line direction. For scaled kernels (h(Tz)), the Paley–Wiener bound grows like \(e^{2\pi\Delta T|\operatorname{Im}z|}\); it does not suppress fixed off-line zeros as (T\to\infty\). The functional equation provides symmetry, not a bound that cancels this growth. Therefore an approximate-identity argument on the critical line cannot be transferred to the full zero set without a separate off-line-zero estimate.

Contour localization is different but not a free arithmetic replacement. For a small circle around (s=1) containing no other zero,

\[
 r_{an}=\frac1{2\pi i}\int_{|s-1|=\epsilon}\frac{L'(E,s)}{L(E,s)}\,ds.
\]

This is unconditional by the argument principle, but it presupposes choosing a zero-free boundary and uses values of (L'/L) on a contour. It does not produce a prime-reduction criterion until one proves an explicit approximation to that contour integral from prime data, with errors controlled uniformly as the contour approaches the center. That missing control is at least as consequential as excluding off-line zeros in the averaging approach.

## Relation to Bober's bound

Bober takes (h_\Delta(t)=(\sin(\pi\Delta t)/(\pi\Delta t))^2\), whose Fourier transform is supported on \([-\Delta,\Delta]\), is nonnegative for real (t\), and satisfies (h_\Delta(0)=1\). His explicit formula makes the zero sum a finite prime-power sum plus conductor and gamma terms. The inequality “explicit-formula value \(\ge r_{an}\)” is conditional on RH: that is what ensures all ordinates (t=\gamma\) are real and all noncentral summands are nonnegative. Bober also assumes BSD to turn the analytic-rank bound into a Mordell–Weil-rank statement. The formula itself is unconditional; the positivity inference is not.

The proposed logarithmic smoothing of point counts changes the prime weights and may give a cleaner coefficient criterion, but it does not improve Bober's logical dependency. To isolate only (r_{an}\) from the explicit formula without RH one needs either (i) a proved bound for the total off-line contribution for the chosen family of kernels, strong enough that its limit vanishes or has known sign, or (ii) contour data with a comparably controlled prime approximation. Neither input is provided by (A); indeed (A) itself forces RH.

## Arithmetic comparison from point reductions

At good primes, (N_p/p=1-a_p/p+1/p\), and Hasse gives \(|a_p|\le2\sqrt p\). Hence

\[
 b_p=\log(1-a_p/p+1/p)=-a_p/p+O(1/p)
\]

as a pointwise bound, while a more useful Taylor expansion has a quadratic contribution involving \((1-a_p)^2/p^2\). The explicit formula instead weights the first prime coefficient by \(a_p\log p/\sqrt p\) after centering, or by \(a_p\log p/p\) at (s=1\). Passing from those prime-power sums to \(\sum b_p\) requires cancellation and control of the quadratic and higher local terms at the relevant growing cutoff; it is not a termwise identity. The exact grouped quadratic cancellation analyzed in `abel.md` is conditional on a prime-sum premise and does not prove that premise.

Reduction of a fixed Mordell–Weil subgroup only says its image order divides (N_p\). Independence over \(\mathbb Q\) gives no uniform lower bound on those image orders over primes, and fixed-modulus Kummer/Chebotarev information does not supply estimates uniform in moduli growing with the cutoff. Hasse's bound alone permits an absolute sum of the scale \(\sum_{p\le x}p^{-1/2}\), far larger than the desired \(\log\log x\) scale; it gives no needed cancellation for \(a_p/p\). This identifies the arithmetic gap, but is not a counterexample to the criterion for elliptic curves.

An unconditional sufficient arithmetic lemma would need to state, for every (E/\mathbb Q\), a smoothed estimate of the form

\[
 \sum_p b_p w((\log p)/U)
 =R\,\mathcal W_w(U)+o(\mathcal W_w(U)),
\]

for an explicit normalization \(\mathcal W_w(U)\asymp\log U\), together with uniformity in a family of weights strong enough to identify the central multiplicity from the explicit formula and to handle the off-line-zero term. No such estimate is proved here. If the family is strong enough to imply (A), it also implies RH by the preceding argument. If it is weaker, an independent zero-side theorem is still required to show its coefficient is (r_{an}\).

## Sources

- J. W. Bober, [“Conditionally Bounding Analytic Ranks of Elliptic Curves”](https://mathweb.ucsd.edu/~kedlaya/ants10/bober/paper.pdf), especially §2, Lemma 2.1 and equations (2)–(3). This is the primary source for the compact-Fourier-support kernel and its RH-dependent positivity bound.
- A. Sheth, [“Euler Product Asymptotics for (L)-functions of Elliptic Curves”](https://arxiv.org/abs/2312.05236), Theorem 1.3 and §1.2. It states Goldfeld's theorem that the full positive-constant sharp product asymptotic implies RH and analytic BSD, and discusses the weaker (\psi_E(x)=o(x\log x)\) criterion of Conrad and Kuo–Murty.
- H. Conrad, [“Partial Euler Products on the Critical Line”](https://www.cambridge.org/core/services/aop-cambridge-core/content/view/061A145952B0C1145EE31E0EAD47ED93/S0008414X0001871Xa.pdf/partial_euler_products_on_the_critical_line.pdf), Theorems 1.1 and 1.3, Corollary 5.7. Primary treatment of the sharp partial-product criterion and its relation to zero distribution.
- K. Kuo and M. R. Murty, [“On a conjecture of Birch and Swinnerton-Dyer”](https://doi.org/10.1090/S0025-5718-05-01742-8), *Mathematics of Computation* 74 (2005), 329–334. The point-counting/prime-sum criterion is discussed by Sheth alongside Conrad's independent result.

## Scope

The symmetry argument proving that (A) implies RH is unconditional once the conditional analytic deduction in `abel.md` is accepted. The failure of Bober's positivity argument without RH is explicit in the zero terms, and the Paley–Wiener growth bound explains why compact Fourier support does not by itself suppress off-line zeros. The arithmetic estimate needed to prove any suitable point-reduction premise remains unproved. No unconditional weak BSD result follows.
