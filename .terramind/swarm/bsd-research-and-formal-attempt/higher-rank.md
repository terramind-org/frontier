# Higher-rank BSD: derived heights, cycles, and derivatives

**Research snapshot: 21 November 2026.** Scope: elliptic curves over number fields, with emphasis on the rank-≥2 frontier. “Higher rank” is not a single theorem: one must distinguish the complex BSD formula, conjectural motivic formulations, (p)-adic BSD for a chosen (p)-adic (L)-function, and theorems about particular Euler-system classes or special cycles.

## What the sources establish

### Classical boundary and the higher-cycle prediction

For elliptic curves over ℚ, Gross–Zagier plus Kolyvagin establishes the rank equality and finiteness of Ш when analytic rank is 0 or 1. It does not prove the full BSD leading-term formula in every such case, and it does not extend the general rank equality to analytic rank ≥2. The higher-rank expectation is part of the Beilinson–Bloch/Bloch–Kato picture: algebraic cycle or motivic cohomology classes should have a height/regulator pairing whose determinant accounts for the first nonzero coefficient of an (L)-function. For an elliptic curve, this specializes to the Néron–Tate regulator and strong BSD, but the general conjectural framework is not a general proof.

The 1986 Gross–Zagier formula relates a height of Heegner points to a first derivative in a specific Rankin (L)-series setting. The much broader Gross–Zagier formula on Shimura curves by Yuan, Zhang, and Zhang (book published 2013; work extending through their 2009–12 papers) gives height formulas for Heegner points / CM cycles and first derivatives in its stated automorphic settings. This extends the geometric and field scope, not the derivative order to arbitrary (r>1). Higher-dimensional cycles, diagonal cycles, and Euler systems are candidate sources of classes when the classical Heegner point is insufficient; their existence or a formula for a special (L)-value does not by itself establish BSD for all rank-≥2 elliptic curves.

### Derived (p)-adic heights

Benjamin Howard, *Derived p-adic heights and p-adic L-functions*, arXiv:1202.6343 (submitted 28 February 2012; published in Algebra & Number Theory 8 (2014), no. 1), constructs successive derived (p)-adic height pairings from the Selmer/Iwasawa filtration. It proves a relation between these derived pairings and higher derivatives of a cohomologically defined (p)-adic (L)-function, and relates degeneracy to failure of semisimplicity of the Selmer module. This is a theorem about (p)-adic height pairings and a (p)-adic (L)-function under its hypotheses; it is not a theorem that the complex (L(E,s)) has order equal to Mordell–Weil rank in all higher ranks.

The 2023 preprint by Castella, Hsu, Kundu, Lee, and Liu, *Derived p-adic heights and the leading coefficient of the Bertolini–Darmon–Prasanna p-adic L-function* (arXiv:2308.10474, submitted 21 August 2023; v2 18 March 2025; published in Transactions of the AMS, Series B 12 (2025), 748–788), treats (E/ℚ), an imaginary quadratic field satisfying the Heegner hypothesis, and an odd good prime (p) split in that field. It formulates a (p)-adic BSD conjecture for the BDP (p)-adic (L)-function. It proves the algebraic leading-coefficient statement for an algebraic analogue; with the relevant Iwasawa–Greenberg main conjecture this controls the (p)-adic (L)-function leading coefficient up to a (p)-adic unit. The order-of-vanishing conclusion is conditional on the *expected maximal nondegeneracy* of the anticyclotomic (p)-adic height. Its appendix proves many supersingular-prime cases of the main conjecture under mild hypotheses. The authors explicitly say maximal nondegeneracy remains difficult. Thus this is substantial progress, not unconditional higher-rank classical BSD.

### Rank two and diagonal-cycle Euler systems

Bertolini–Darmon–Rotger's diagonal-cycle / generalized-Kato-class program supplies classes in triple-product Galois representations. The paper *On the non-vanishing of generalized Kato classes for elliptic curves of rank 2* (arXiv:1809.09066; original submission 2018; published in the Journal of the European Mathematical Society, 2022) proves first cases of their conjecture for good ordinary (p), with additional hypotheses on (E), the auxiliary imaginary quadratic field and characters, and nonvanishing/factorization conditions. In those cases it constructs nonzero generalized Kato classes and proves that nonvanishing forces the relevant (p)-adic Selmer group to have dimension 2. Its proof uses derived (p)-adic heights and an explicit reciprocity law relating diagonal-cycle families to a three-variable (p)-adic (L)-function. The theorem is specific to these hypotheses and these classes; it does not prove (r_{[31man}=r_{[31malg}=2) or the full strong BSD formula for every rank-two curve.

The paper itself notes a numerical rank-two family and interprets nonzero classes as evidence toward a refined Darmon–Rotger conjecture. Its proposed implication from the refined class construction to a (p)-adic BSD formula is presented as something suggested by the formula, not established in general.

## Status ledger

| Claim | Status supported by primary sources | Important boundary |
|---|---|---|
| Complex BSD rank equality and leading coefficient for arbitrary elliptic curves over ℚ, rank ≥2 | Conjecture | No general theorem identified. |
| Gross–Zagier height/first derivative identities | Theorem in specified modular/automorphic settings | First derivative formula, not a general higher-derivative BSD theorem. |
| Howard derived heights linked with higher (p)-adic (L)-function derivatives | Theorem under the paper's hypotheses | (p)-adic and Iwasawa-theoretic statement; semisimplicity/nondegeneracy matters. |
| BDP (p)-adic BSD leading coefficient for algebraic analogue | Theorem in the stated Heegner/split-good-prime setting | Transfer to analytic BDP function uses a main conjecture; unit ambiguity. |
| BDP (p)-adic order-of-vanishing formula | Conditional on maximal nondegeneracy | This is the explicit remaining bridge in the 2025 paper. |
| Generalized Kato class nonvanishing at rank two | Theorem in first cases with restrictive hypotheses | Gives a 2-dimensional Selmer conclusion in the theorem's setting, not universal rank-two BSD. |
| Beilinson–Bloch / motivic regulator explains arbitrary higher derivatives | Conjectural framework | Expected cycle groups, regulator, and leading coefficient are not generally constructed/proved for all elliptic curves. |

## Falsifiable subproblem suitable for the formal attempt

Do not ask Lean to formalize the arithmetic conjecture as if it were proved. A useful and genuinely falsifiable bridge is the finite-dimensional algebra lemma abstracting the “first nonzero derived height” step:

> Let (M) be a finite free module of rank (n) over a discrete valuation ring, with a descending filtration (M=M_0\supseteq M_1\supseteq\cdots\supseteq M_{k+1}=0). Suppose a bilinear pairing (h_k) on (M_k/M_{k+1}) is perfect and the lower derived pairings vanish on the relevant successive quotients. Prove that the determinant of the induced pairing on a basis of (M_k/M_{k+1}) is a unit, and that the first nonzero graded contribution to the determinant/regulator occurs in degree (k\cdot\operatorname{rank}(M_k/M_{k+1})).

The statement must be made precise before formalization: specify the coefficient ring, filtered pairing compatibility, determinant convention, and whether “degree” is valuation in a formal parameter (T). These are not cosmetic; omitting them risks proving a vacuous or false algebra claim. A machine-checkable counterexample can falsify a proposed lemma quickly. Passing it would verify only the linear-algebra bridge, not the arithmetic hypotheses that derived heights are compatible, maximally nondegenerate, or arise from the relevant cycles.

A more arithmetic but still falsifiable computational target is to reproduce one explicit ordinary rank-two example from the generalized-Kato paper: record the curve, (p), auxiliary (K)/character, verify every theorem hypothesis from the paper, and independently check its stated Euler-factor/(p)-adic nonvanishing data. Treat this only as a consistency check, not as a proof of a class being nonzero unless the exact algebraic value and certification method are supplied.

## Source trail (original research / publication records)

- B. Howard, [*Derived p-adic heights and p-adic L-functions*](https://arxiv.org/abs/1202.6343), arXiv submission 2012; journal publication 2014.
- F. Castella, C.-Y. Hsu, D. Kundu, Y.-S. Lee, Z. Liu, [*Derived p-adic heights and the leading coefficient of the Bertolini–Darmon–Prasanna p-adic L-function*](https://arxiv.org/abs/2308.10474), submitted 2023, revised 2025; published 2025, Trans. AMS Ser. B 12, 748–788, DOI [10.1090/btran/227](https://doi.org/10.1090/btran/227).
- F. Castella, A. Grossi, J. Lee, C. Skinner, [*On the non-vanishing of generalized Kato classes for elliptic curves of rank 2*](https://arxiv.org/abs/1809.09066), arXiv submission 2018; JEMS publication 2022.
- X. Yuan, S.-W. Zhang, W. Zhang, [*The Gross–Zagier Formula on Shimura Curves*](https://press.princeton.edu/books/ebook/9781400845644/the-gross-zagier-formula-on-shimura-curves-1), Princeton University Press, 2013; source for the higher-field/automorphic scope of the height/first-derivative identity.
- A. Gross, [*Lectures on the conjecture of Birch and Swinnerton-Dyer*](https://people.math.harvard.edu/~gross/preprints/lectures-pcmi.pdf), for the standard BSD statement and its explicit finiteness caveat for the strong leading-term formula. For original foundational formulations, see A. Beilinson, “Higher regulators and values of (L)-functions,” J. Soviet Math. 30 (1985), and S. Bloch, *Algebraic K-theory and zeta functions of elliptic curves* (1978).

**Date caveat.** Search snippets and extracted arXiv HTML for some older arXiv records displayed a misleading “Date: March 22, 2026” (likely a conversion artifact). I used the arXiv version history for actual submission/revision dates and publisher metadata for publication dates; do not cite that extracted date field as the paper's first-submission date.
