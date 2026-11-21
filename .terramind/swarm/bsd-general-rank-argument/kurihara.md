# Kurihara numbers do not compare to complex vanishing order

## Result

Chan-Ho Kim's modular-symbol theorem makes the first nonzero Kurihara index an exact formula for the p-adic Selmer corank under restrictive hypotheses. It does **not** identify that index with the order of vanishing of the complex (L)-function, nor give an inequality between them. The paper obtains only a parity congruence with the complex order. Consequently, the Kurihara route supplies a conditional formula for Selmer corank (and, with finite Ш, Mordell–Weil rank), but does not establish either weak-BSD inequality in arbitrary rank.

## Primary theorem and normalization

The source is Chan-Ho Kim, [*The structure of Selmer groups and the Iwasawa main conjecture for elliptic curves*](https://preprint.press.jhu.edu/ajm/sites/default/files/AJM-kim.pdf), especially §1.2.2, §1.4.1–§1.4.4 and Theorem 1.8 (§1.5.2). The journal-hosted PDF is the primary source. I state the residual-representation hypothesis as $\bar\rho$ surjective, consistently with the paper’s Theorem 1.1 and Corollary 1.6 and its surrounding definitions.

Let $E/\mathbb Q$ have conductor $N$, let $p\ge5$, and let $f=\sum a_mq^m\in S_2(\Gamma_0(N))$ be the associated newform. For each $k\ge1$, Kim uses the Kolyvagin-prime set
\[
\mathcal P_k=\{\ell:\ell\nmid Np,\quad \ell\equiv1\pmod {p^k},\quad a_\ell(E)\equiv \ell+1\pmod {p^k}\},
\]
and let $\mathcal N_k$ denote the set of square-free products of primes in $\mathcal P_k$. For $n\in\mathcal N_k$, set
\[
 I_n=\sum_{\ell\mid n}(\ell-1,a_\ell(E)-\ell-1)\mathbb Z_p.
\]
The modular symbols are normalized by the real Néron period of a global minimal model:
\[
2\pi\int_0^\infty f(a/b+iy)\,dy
=[a/b]^+\Omega_E^+ + [a/b]^- i\Omega_E^-.
\]
Under irreducibility of \(\bar\rho\) and $p\nmid$ the Manin constant, $[a/b]^+$ is $p$-integral. For each prime ℓ|n a primitive root ηℓ modulo ℓ is chosen; the resulting class is well-defined up to a unit and is
\[
\tilde\delta_n=\sum_{a\in(\mathbb Z/n\mathbb Z)^\times}
\overline{[a/n]^+}\prod_{\ell\mid n}\overline{\log_{\eta_\ell}(a)}
\quad\in\mathbb Z_p/I_n\mathbb Z_p.
\]
For $n=1$, this normalization gives the actual special value
\[
\tilde\delta_1=[0]^+=L(E,1)/\Omega_E^+.
\]
Write \(\nu(n)\) for the number of distinct prime factors and define
\[
\operatorname{ord}(\tilde\delta)=\min\{\nu(n):n\in\mathcal N_1,\ \tilde\delta_n\ne0\},
\]
with value $\infty$ if every class vanishes.

**Kim, Theorem 1.8.** Suppose $\bar\rho_{E,p}:G_\mathbb Q\to\mathrm{Aut}_{\mathbb F_p}(E[p])$ is surjective, $p\ge5$, and the Manin constant is prime to $p$. If $\operatorname{ord}(\tilde\delta)<\infty$, then
\[
\operatorname{corank}_{\mathbb Z_p}\mathrm{Sel}(\mathbb Q,E[p^\infty])
=\operatorname{ord}(\tilde\delta).
\]
The same theorem gives the higher Fitting ideals and the finite/divisible decomposition of this Selmer group from the $p$-adic valuations of the classes. If, in addition, \(\Sha(E/\mathbb Q)[p^\infty]\) is finite, it gives
\[
\operatorname{rank}_{\mathbb Z}E(\mathbb Q)=\operatorname{ord}(\tilde\delta).
\]
The theorem does **not** assume good ordinary reduction; the displayed hypotheses above are the ones for Theorem 1.8. Nonvanishing of the collection is a separate input, not part of its hypotheses. Kim's Corollary 1.6 supplies that input from the Iwasawa main conjecture localized at $X\Lambda$, and in particular in listed rank-at-most-one settings; it does not supply it unconditionally for all $(E,p)$.

## What it says about complex analytic rank

Kim's Corollary 1.12, using the functional equation of the Kurihara collection, states only
\[
\operatorname{corank}_{\mathbb Z_p}\mathrm{Sel}(\mathbb Q,E[p^\infty])
\equiv \operatorname{ord}_{s=1}L(E,s)\pmod2,
\]
under the Theorem 1.8 hypotheses and finite \(\operatorname{ord}(\tilde\delta)\). Combining this with Theorem 1.8 yields
\[
\operatorname{ord}(\tilde\delta)\equiv r_{\rm an}(E)\pmod2,
\]
not equality or an order inequality. Corollary 1.13 says that any one nonzero \(\tilde\delta_n\) gives \(\operatorname{rank}E(\mathbb Q)\le\nu(n)\), a bound in terms of that chosen index. It is not a comparison to $r_{\rm an}$.

## Augmentation filtration versus the Taylor variable

There are three different constructions here and their indices cannot be silently identified.

* The complex order $r_{\rm an}=\operatorname{ord}_{s=1}L(E,s)$ is the first nonzero coefficient in the Taylor expansion in $s-1$.
* The cyclotomic Iwasawa augmentation order is the $X$-adic order in \(\Lambda\simeq\mathbb Z_p[[X]]\), with a topological generator γ sent to $1+X$. This is the variable used for the characteristic-ideal localization at $X\Lambda$, and is related to the cyclotomic $p$-adic $L$-function through a $p$-adic interpolation theorem only in settings where the relevant (p)-adic (L)-function and local factors are controlled.
* Kim's \(\operatorname{ord}(\tilde\delta)\) is the minimum number of auxiliary Kolyvagin primes needed for a nonzero finite-level modular-symbol class. Its log factors record discrete derivatives across auxiliary primes and its quotient depends on the ideals $I_n$. It is not defined as an augmentation-ideal order.

Even if a (p)-adic interpolation formula identifies the order at the trivial character of a suitably normalized $p$-adic $L$-function with the complex order, that formula controls the cyclotomic $X$-adic order (with possible Euler factors / exceptional-zero corrections); it does not identify it with the minimum auxiliary-prime count. Kim's theorem connects the latter to Selmer **corank**, while Corollary 1.12 connects Selmer corank to complex analytic order only modulo two. Specializing a Λ-adic object at $X=0$ or interpolating its values therefore does not produce a comparison between $\operatorname{ord}(\tilde\delta)$ and $r_{\rm an}$ from the cited results.

This is a precise obstruction to the proposed route: the missing assertion would be an unconditional theorem (under an explicitly stated set of hypotheses) that the number of auxiliary prime factors at the first nonzero Kurihara class is bounded by, or equals, the complex Taylor order. Kim proves neither; the available consequence is parity. No argument converting a congruence modulo $2$ into either desired inequality is available here.

## Restricted deduction

For a fixed $(E,p)$ satisfying the surjectivity and Manin-constant hypotheses, assume (i) the Kurihara collection is not identically zero and (ii) \(\Sha(E/\mathbb Q)[p^\infty]\) is finite. Then Kim proves the concrete formula
\[
\operatorname{rank}E(\mathbb Q)=\operatorname{ord}(\tilde\delta),
\]
and, independently, its parity agrees with (r_{\rm an}(E)\). This is a genuine arithmetic consequence and a restricted rank formula, but still leaves the equality of rank and analytic order open outside already-known cases. In analytic rank zero, the paper's Corollary 1.11 / Theorem 1.2 proves the rank-zero converse (L(E,1)\ne0\iff E(\mathbb Q),\Sha(E/\mathbb Q)\text{ finite}\); it does not extend the sought comparison to arbitrary order.

## Sources

* Chan-Ho Kim, [primary paper (journal-hosted PDF)](https://preprint.press.jhu.edu/ajm/sites/default/files/AJM-kim.pdf): definitions and normalization §1.2.2, §1.4.1–§1.4.4; structure theorem 1.8; parity Corollary 1.12; rank bound Corollary 1.13; nonvanishing input Corollary 1.6.
* [arXiv record 2203.12159](https://arxiv.org/abs/2203.12159) for bibliographic/version context.
