# Rank zero and one: Heegner points, Euler systems, and BSD

Research cutoff: 2026-11-21. Scope: elliptic curves over `Q` unless stated. “Rank part” below means equality of analytic and Mordell–Weil ranks; finiteness of `Sha` is stated separately. The full BSD leading-term formula is strictly stronger.

## The implication to keep straight

For an elliptic curve `E/Q`, modularity (now known for every such curve) supplies the weight-two modular form and analytic continuation of `L(E,s)`. The Gross–Zagier/Kolyvagin theorem gives

`ord_{s=1} L(E,s) = r in {0,1}  =>  rank_Z E(Q) = r and Sha(E/Q) is finite.`

This is the analytic-to-arithmetic direction. It does not assert the converse in general, nor by itself the exact BSD leading coefficient. The converse requires extra hypotheses and an arithmetic finiteness/Selmer condition; see below. For `r=0`, rank zero means `E(Q)` is finite (by Mordell–Weil); for `r=1`, it means rank one.

## Gross–Zagier (1986): formula for height, not BSD by itself

B. H. Gross and D. B. Zagier, “Heegner points and derivatives of L-series,” *Invent. Math.* 84 (1986), 225–320. [Original paper PDF](https://wiki.epfl.ch/waldspurger/documents/gross-zagier.pdf), [DOI](https://doi.org/10.1007/BF01388809).

The theorem relates the Néron–Tate height of a Heegner point (more generally, a height pairing of Heegner divisors on `J_0(N)`) to the first derivative at `s=1` of a Rankin `L`-series. In the elliptic-curve specialization, for an imaginary quadratic field `K` satisfying the Heegner condition for the conductor `N` (each prime dividing `N` splits in `K`; the original setup also imposes its stated coprimality/discriminant and parametrization conditions), the Heegner trace `y_K in E(K)` has canonical height equal to an explicit nonzero factor times `L'(E/K,1)`. Thus it gives `L'(E/K,1) != 0 <=> y_K` is nontorsion in that setup. This produces a point and a rank lower bound; it does not alone bound the rank above, prove `Sha` finite, or establish the BSD coefficient.

The original paper also combines this formula with Waldspurger to prove an existence result when `L(E,1)=0`; one must not misread that as the general rank equality. The height identity is the key input to the rank-one Euler-system argument.

## Kolyvagin (1988–1990): rank and `Sha` finiteness

V. A. Kolyvagin, “Finiteness of `E(Q)` and `Sha(E,Q)` for a subclass of Weil curves,” *Math. USSR-Izv.* 32:3 (1989), 523–541 (received 1987). [Math-Net original-paper record and English PDF](https://www.mathnet.ru/eng/im1191), [DOI](https://doi.org/10.1070/IM1989v032n03ABEH000779). Related Euler-system paper: “Euler systems,” in *The Grothendieck Festschrift*, vol. II (1990), 435–483.

The 1989 theorem assumes a Weil parametrization `X_N -> E`, an imaginary quadratic `K` with discriminant congruent to a square modulo `4N`, and a Heegner point `y_K`; if `L(E/Q,1) != 0` and `y_K` has infinite order (excluding a finite exceptional set of fields in the paper), it proves `E(Q)` and `Sha(E/Q)` finite. The abstract’s example/corollary states extra coprimality and nonvanishing conditions for `L'_f(E/K,1)`. Combined with Gross–Zagier, the Heegner-point Euler system gives the standard analytic rank one theorem and finite `Sha`; the rank is exactly one because Gross–Zagier supplies a non-torsion point while Kolyvagin bounds the Selmer group/rank above.

For analytic rank zero, Kolyvagin’s Euler systems similarly establish rank zero and finiteness of `Sha` from nonzero central value (with the classical modularity/parametrization setting; later results and modularity extend this to all `E/Q`). Neither finiteness theorem alone determines `#Sha` or proves the exact leading coefficient identity.

## Converse theorems: the reverse implication is conditional

* Christopher Skinner, “A converse to a theorem of Gross, Zagier, and Kolyvagin,” first preprint 2014; *Annals of Mathematics* 191 (2020), 329–354. [Annals page / paper](https://annals.math.princeton.edu/2020/191-2/p01), [DOI](https://doi.org/10.4007/annals.2020.191.2.1), [arXiv](https://arxiv.org/abs/1405.7294). For semistable `E/Q`, if `E` has nonsplit multiplicative reduction at at least one odd prime, or split multiplicative reduction at at least two odd primes, then `rank E(Q)=1` and finite `Sha(E/Q)` imply `ord_{s=1}L(E,s)=1`. This is a genuine arithmetic-to-analytic converse in a restricted family; it assumes finiteness of `Sha`, which is not known unconditionally for arbitrary curves.
* Wei Zhang, “Selmer groups and the indivisibility of Heegner points,” *Cambridge Journal of Mathematics* 2 (2014), 191–253. [Author PDF](https://math.mit.edu/~wz2113/math/online/Kconj.pdf). Theorem 1.5 gives the equivalence `rank E(Q)=1 and finite Sha <=> ord L(E,s)=1` under the paper’s conductor condition: if `N` is not square-free, it assumes at least two primes `ell || N`. This broadens the Skinner converse in a different direction; neither theorem should be quoted without its hypotheses. The proof uses a p-indivisibility theorem for derived Heegner points and substantial residual-representation/local hypotheses in intermediate results.

The cited modern “converse” headlines often refer to a *p-converse*: a condition such as `corank_Zp Sel_{p∞}(E/Q)=1` implies analytic rank one, for eligible primes and with explicit residual, local, and reduction assumptions. It is not an unconditional equivalence of analytic and algebraic rank. Zhang’s 2014 paper, for example, has Theorem 1.3: for its eligible `(E,p,K)` setup, Selmer corank one over `K` forces a nontorsion Heegner point, and hence rank and analytic rank one over `K`, plus finite `Sha(E/K)`. The paper’s Theorem 1.4 lists `p>=5` and residual-representation / local hypotheses; Theorem 1.5 is the rational converse above.

## Rank equality versus the full formula

The rank equality plus finite `Sha` is only the weak-rank consequence. The strong BSD leading coefficient formula (in rank `r`) compares `L^(r)(E,1)/r!` to `Omega_E * Reg(E/Q) * #Sha(E/Q) * product_l c_l`, divided by `#E(Q)_tors^2`, with the usual normalization of the real period and Tamagawa factors. Gross–Zagier is a height-versus-derivative identity; Kolyvagin proves finiteness and bounds, not in general the exact order of `Sha` needed for the formula.

There are important conditional-on-prime / p-primary refinements. Wei Zhang’s 2014 paper proves a `p`-part of the refined BSD formula in analytic rank one under its eligible-prime hypotheses (Theorem 1.6), and its abstract identifies good ordinary `p>=5` with suitable local ramification hypotheses for a key result. Kato’s 2004 Euler-system theorem gives one divisibility toward the GL(2) Iwasawa main conjecture; it is not itself the full BSD formula. Skinner–Urban (2014) prove ordinary main-conjecture cases, again under hypotheses. Such results control `p`-adic valuations of the formula, not automatically all primes and the rational equality.

Recent primary-source status:

* Ashay Burungale, Francesc Castella, Christopher Skinner, “Base change and Iwasawa Main Conjectures for GL2” (2024 preprint). [arXiv:2405.00270](https://arxiv.org/abs/2405.00270). Its abstract says the one-variable main conjectures imply the `p`-part of BSD when `ord L(E,s)<=1`; this is a prime-by-prime conclusion, not a blanket full formula.
* Ashay Burungale, Francesc Castella, Chan-Ho Kim, Jishnu Ray, Christopher Skinner, Ye Tian, “Zeta elements for elliptic curves and applications” (2024 preprint). [arXiv:2409.01350](https://arxiv.org/abs/2409.01350). It proves Kobayashi’s supersingular main conjecture for semistable `E/Q` at supersingular `p`, and obtains p-part BSD at analytic rank zero or one in that setting, as well as p-converse cases. Its full-BSD statement is for specified infinite families, not all curves.
* Xiaojun Yan and Xiuwu Zhu, “Main conjectures for non-CM elliptic curves at good ordinary primes” (preprint dated 2024-12-28). [arXiv:2412.20078](https://arxiv.org/abs/2412.20078). For `p>2` good ordinary with irreducible residual representation, Corollary 1.4 gives equivalence between Selmer corank `r` and analytic order `r` for `r<=1`; with an additional theorem hypothesis it yields the `p`-part BSD formula. The paper’s Theorem 4.15 states the ordinary setting and the additional condition for p-part BSD. This is generalized p-primary progress, not full BSD for every rank-zero/one curve.
* Ashay A. Burungale and Ye Tian, “A rank zero p-converse to a theorem of Gross–Zagier, Kolyvagin and Rubin,” *Annals* 203 (2026), 1–13. [Annals paper](https://annals.math.princeton.edu/2026/203-1/p01), [DOI](https://doi.org/10.4007/annals.2026.203.1.1). For a CM elliptic curve over `Q` and a prime `p`, it proves `corank_Zp Sel_{p∞}(E/Q)=0 => ord_{s=1} L(E/Q,s)=0`; it is a rank-zero p-converse, not an unrestricted theorem for non-CM curves or the full BSD coefficient.

## What a checker-facing formal attempt can safely target

A Lean theorem formalizing “analytic order zero/one implies rank equality and finite `Sha`” needs the hypotheses and substantial arithmetic infrastructure (modularity, analytic continuation/nonvanishing order, Heegner points/Gross–Zagier, Euler systems/Kolyvagin). It is not a routine consequence of definitions and is far beyond a small standalone proof attempt. A realistic formal target, if the repository has the relevant definitions, is a narrowly stated elementary lemma within an already formalized setup—not a claimed proof of BSD. Never replace finite `Sha` with a known cardinality or equate this rank theorem with the strong formula.

## Primary-source list

1. Gross–Zagier (1986): https://doi.org/10.1007/BF01388809 and paper PDF above.
2. Kolyvagin (1989): https://doi.org/10.1070/IM1989v032n03ABEH000779 and Math-Net record above.
3. Kato (2004), *Astérisque* 295, 117–290: [Numdam paper](https://www.numdam.org/item/AST_2004__295__117_0.pdf).
4. Skinner–Urban (2014), “The Iwasawa main conjectures for GL2”: [Inventiones DOI](https://doi.org/10.1007/s00222-013-0464-5).
5. Skinner (2020) and Zhang (2014): links in converse section.
6. Recent Iwasawa results and 2026 CM rank-zero p-converse: arXiv/Annals primary links above.
