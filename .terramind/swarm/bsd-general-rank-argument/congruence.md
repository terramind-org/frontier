# Rank lowering by congruences: what it controls

Research cutoff: 21 November 2026. This note tests whether level raising/lowering and Jochnowitz congruences can induct from complex analytic rank (r) to (r-1), then transport the result back to the original elliptic curve over \(\mathbb Q\).

## Proposed step and its missing premise

The tempting step is: starting with (E/\mathbb Q) and (r_{\rm an}(E)=r>0), choose an auxiliary prime (q) and a weight-two eigenform (g'), congruent to (f_E\pmod{\mathfrak p}) after raising level by (q), whose functional equation sign is reversed. If one could show (r_{\rm an}(g')=r-1), apply an induction theorem to (g'), and transport the resulting rational points or rank back to (E), one might lower rank one step.

There is no such unconditional step in the sources checked. A mod-(p) congruence is a congruence of residual Hecke eigenvalues/Galois representations. It is not equality of complex (L)-functions, nor a comparison of their orders of vanishing. The Jochnowitz results compare *algebraic reductions* of a Heegner point/derivative on one side with a normalized algebraic central value on a sign-reversed form on the other. A nonzero congruence class can prove nonvanishing of a specific algebraic value, hence analytic rank zero for that auxiliary form in the relevant quadratic base-change setting. It does not identify a general order (r) with (r-1).

## A valid restricted one-step lemma (Selmer dimension only)

Wei Zhang, *Selmer groups and the indivisibility of Heegner points*, proves the following precise kind of lowering statement (Proposition 5.4; the setup and assumptions in §§2, 4, 5 matter). Let (K/\mathbb Q) be an imaginary quadratic field satisfying the paper's modified Heegner hypotheses for a weight-two newform (g) of level (N=N^+N^-), with the stated residual representation, prime, and local hypotheses (Hypothesis \(\heartsuit\)); let (p\ge5) be the residual characteristic and (V\) the common residual representation. Let (q\nmid NpD_K) be an admissible prime in the paper's sense, so (V\) is unramified at (q), its restriction to (G_{K_q}) splits into the two one-dimensional finite/singular pieces, and the level-raising theorem (Ribet, Diamond–Taylor) supplies a newform (g') of level (Nq) congruent to (g\) at chosen primes over (p). Under the local hypotheses ensuring the old and new Selmer structures agree away from (q), if
\[
\operatorname{loc}_q:\operatorname{Sel}_{p,0}(A/K)\longrightarrow H^1_{\rm fin}(K_q,V)
\]
is nonzero (equivalently surjective, since the target is one-dimensional), then
\[
\dim_{k'}\operatorname{Sel}_{p'}(A'/K)
=\dim_k\operatorname{Sel}_{p}(A/K)-1,
\]
and the new strict Selmer group is the kernel of that localization map. Here (A,A') are the GL2-type abelian varieties attached to the forms, and \,\(\operatorname{Sel}_{p,0}\) is the paper's specified Selmer variant. The proof is a parity/local-condition comparison: at (q), the old/new conditions exchange the finite and transverse lines; away from (q), their conditions match. This is rank lowering for a *residual Selmer dimension*, not for Mordell–Weil rank or complex analytic order.

The paper's later iteration makes this limitation visible: it chooses admissible (q_i) where a surviving class has nonzero localization, raises level successively, and lowers Selmer dimensions one at a time. Its output is an Euler/Kolyvagin-system and Selmer result under the hypotheses, not a universal sequence of elliptic curves over \(\mathbb Q\) with complex analytic ranks (r,r-1,\ldots\).

## What Jochnowitz congruence actually says

Bertolini–Darmon, *Euler systems and Jochnowitz congruences*, Theorem 1.3, relates the image of the Heegner point (y_K\) in (E(K_q)/pE(K_q)) to whether the algebraic part of (L(g/K,1)) is nonzero modulo the relevant maximal ideal for all newforms (g) on the raised-level quotient. The derivative (L'(E/K,1)) enters through Gross–Zagier: the Heegner point encodes that derivative. Thus the relation is a residual congruence between (i) the reduction of a Heegner point representing derivative/height data and (ii) an algebraic part of a central value for a sign-changed form. It is not an equality of complex derivatives or a theorem on their orders.

The theorem is useful when one side is already known nonzero modulo (p). Together with Kolyvagin in the paper's setting, nondivisibility of the Heegner point gives a one-dimensional (p)-Selmer group and a generator (Proposition 1.5). This is a strong rank-one mechanism. Its hypotheses and conclusion are specific; it does not iterate from arbitrary analytic rank.

Wei Zhang's version on Shimura curves states the sign-changing situation explicitly: the original (L(E/K,s)) has sign (-1), while the level-raised (L(g/K,s)) has sign (+1), and the congruence relates the algebraic part of (L'_K(E,1)) to that of (L_K(g,1)). This gives a derivative-versus-value congruence, but only modulo a residual maximal ideal and after algebraic period normalization. It cannot determine the complex order of either function beyond what independent nonvanishing information already gives.

## The complex-order and transport obstructions

1. **No order-of-vanishing control across congruence.** Equality of residual Hecke eigenvalues does not imply equality or a fixed order difference of complex (L)-functions. The sign reversal only forces parity of the orders. A root number (+1) permits orders (0,2,4,\ldots); sign (-1) permits (1,3,5,\ldots). Jochnowitz supplies a mod-(p) relation between selected algebraic quantities, not a bound (r_{\rm an}(g')\le r-1) or equality (r-1). In particular, a vanishing or nonvanishing modulo (p) of an algebraic period-normalized value is not an assertion about the exact complex order when that value is zero or divisible by (p).
2. **The local hypotheses are substantive.** Level raising requires an admissible (q) and an irreducible residual representation with characteristic at least 5 in Zhang's Theorem 2.1. Selmer lowering additionally requires a nonzero localization map and compatible local conditions at every place; the paper's Hypothesis \(\heartsuit\) handles exceptional bad-prime cases. At (q), finite/unramified and singular/transverse lines are exchanged. These hypotheses cannot be suppressed for arbitrary (E,p,K).
3. **Residual Selmer dimension is not rank.** The proposition compares mod-(p) Selmer groups over (K) for distinct level forms/abelian varieties. It does not show that the dimension is the Mordell–Weil rank; the Kummer sequence leaves a Tate–Shafarevich quotient. Nor does a congruence between (f_E) and (g') give a map taking rational points of (A') to (E(\mathbb Q)). They are different characteristic-zero abelian varieties, linked only through residual representations at the chosen prime.
4. **Field and analytic-rank mismatch.** The cited Heegner arguments concern (L(E/K,s)=L(E,s)L(E^D,s)), with (K) and auxiliary data satisfying Heegner conditions, rather than a free-standing order statement for (L(E/\mathbb Q,s)). Even if a product order is lowered by one in a special case, a theorem is still needed to allocate that order between the two factors and transport rational points to the original curve.

Therefore the proposed induction would need, at minimum, a theorem that (a) chooses a level-raised congruent form with a controlled *complex* order (r-1), and (b) transports (r-1) independent rational points (or the relevant rank inequality) back to (E/\mathbb Q), while reconciling all local conditions and Sha contributions. Neither Jochnowitz congruences nor bipartite Euler systems provide either statement generally.

## Bipartite Euler systems: what the graph buys

Howard's axiomatic formalism packages classes and special-value elements in two parity families, indexed by products of admissible primes, with explicit reciprocity laws relating localizations and adjacent vertices. This bipartite structure explains how a nonzero class/value on one side can control Selmer groups on the other and supports one-sided bounds, parity statements, and Iwasawa main-conjecture results under residual irreducibility and local hypotheses. The graph is not a ladder of complex analytic ranks: its vertices encode Selmer structures and algebraic (p)-adic or mod-(p) special-value data. It does not prove exact complex orders or provide a cross-level rational-point map.

## Sources (primary)

- M. Bertolini and H. Darmon, [“Euler systems and Jochnowitz congruences”](https://citeseerx.ist.psu.edu/document?doi=07eec1de1af336a841d26e905494b6f7f17278a4&repid=rep1&type=pdf), *Amer. J. Math.* 121 (1999), 259–281. Theorem 1.3 and Proposition 1.5 give the Heegner-point/algebraic-value congruence and its rank-one Selmer consequence.
- W. Zhang, [“Selmer groups and the indivisibility of Heegner points”](https://intlpress.com/site/pub/files/_fulltext/journals/cjm/2014/0002/0002/CJM-2014-0002-0002-a002.pdf), *Cambridge Journal of Mathematics* 2 (2014), 191–253. Theorem 2.1 (Ribet, Diamond–Taylor level raising); Lemma 4.2 (finite/singular local decomposition at admissible primes); Proposition 5.4 (one-dimensional Selmer lowering); Theorem 1.3 and §6 (special-value mod-(p) formula); §§8–9 (iterated Selmer/Kolyvagin-system arguments).
- S. Vigni, [“Heegner points and Jochnowitz congruences on Shimura curves”](https://arxiv.org/abs/1204.0496), *Math. Z.* 284 (2016), 1231–1269. Theorem 1.1 relates the algebraic part of (L'_K(E,1)) to that of (L_K(g,1)) for opposite signs, under its modified Heegner and descent-prime hypotheses.
- B. Howard, [“Bipartite Euler systems”](https://doi.org/10.1515/CRELLE.2006.062), *J. Reine Angew. Math.* 597 (2006), 1–25. Its abstract and formalism concern anticyclotomic Selmer groups and nonvanishing of p-adic L-functions in sign-dependent settings, not a complex-order comparison across congruent forms.

**Assessment:** a restricted one-step lemma lowering residual Selmer dimension is valid and sourced. The requested analytic-rank induction is false as an inference from congruence data alone and remains unsupported in general; no elliptic-curve counterexample to BSD is claimed. The exact missing lemma is the controlled complex-order-plus-rational-rank transport statement above.
