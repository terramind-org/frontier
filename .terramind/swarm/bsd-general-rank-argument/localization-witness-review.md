# Independent audit: rational localization witness

## Scope and source version

This is an independent audit of `localization-witness.md` against Castella's author manuscript, *Nonvanishing of Generalised Kato Classes and Iwasawa Main Conjectures*, especially §5.1, Corollary 5.1.3 and Remark 5.1.4, and §5.2, Choice 5.2.1 and Theorem 5.2.3. The manuscript's Theorem 5.2.3 is the relevant result; Theorem A in its introduction is a summary of the same statement. This audit does not assume a rank-parity conclusion or finiteness of Sha.

## Findings

1. **A non-torsion rational point gives nonzero finite localization.** At a prime of good reduction, the Kummer map identifies the rational-point contribution to the Bloch–Kato finite local condition with the image of
   \(E(\mathbf Q_p)\otimes_{\mathbf Z}\mathbf Q_p\) in \(H^1_f(\mathbf Q_p,V_pE)\). The integral Kummer map has torsion kernel; after tensoring with \(\mathbf Q_p\), it is injective. The formal-group logarithm is injective on a sufficiently small open subgroup, and its extension to \(E(\mathbf Q_p)\otimes\mathbf Q_p\) has zero kernel. Equivalently, the group logarithm on \(E(\mathbf Q_p)\) has torsion kernel: pass from any point to a multiple in the formal subgroup, where the logarithm is injective. Thus an infinite-order \(P\in E(\mathbf Q)\), whose image remains infinite order in \(E(\mathbf Q_p)\), has nonzero local Kummer class. This is a direct local argument and does not invoke Castella or parity.

2. **The target must be kept straight.** Castella writes the restriction target as \(E(\mathbf Q_p)\widehat\otimes\mathbf Q_p\). For good reduction this is the Bloch–Kato finite local condition under the Kummer/logarithm identification. The point proves that \(\operatorname{loc}_p\) on the *whole* Selmer group is nonzero. It does not prove that the generalized Kato class has nonzero localization: Remark 5.1.4 says that this class is in the strict kernel in the setting used in §5.2.

3. **Theorem 5.2.3 is used in the correct direction, with important hypotheses.** It assumes positive even analytic order at 1, the §5.2 residual hypotheses (h1)–(h3), a Choice 5.2.1 auxiliary pair, and the Selmer-dimension-two premise for its converse. Under these assumptions, nonzero restriction implies \(\kappa_p(E)\ne0\), and the theorem says it spans the one-dimensional strict Selmer kernel. The source requires good ordinary reduction and \(p>3\). In the revised hypotheses, (h2) requires a prime \(q\) dividing the conductor exactly once, with residual ramification at \(q\) when \(q\equiv\pm1\pmod p\); (h3) is \(p>5\) or the stated residual image condition. Choice 5.2.1 includes its splitting and twist-value conditions, including \(L(E_K,1)\ne0\), \(L(E/K,\chi,1)\ne0\), and nontriviality of \(\chi|_{G_{K_p}}\). These are not consequences of the rational point. The companion note preserves these conditions.

4. **No second rational point follows.** From the Selmer exact sequence and finite generation of \(E(\mathbf Q)\), dimension two has the form \(r+t_p=2\), where \(r=\operatorname{rank}E(\mathbf Q)\) and \(t_p\) is the corank of the divisible subgroup of \(\Sha(E/\mathbf Q)[p^\infty]\). One exhibited point gives \(r\ge1\), leaving \((r,t_p)=(1,1)\) or \((2,0)\). The theorem produces a strict Selmer class; it does not show that this class is a rational Kummer class. No implication from these hypotheses to a second independent rational point has been established.

5. **Parity does not remove the alternative.** The p-parity theorem identifies the parity of total p-primary Selmer corank with analytic-rank parity; it does not, without further input, identify Mordell–Weil rank parity. For analytic rank two, Selmer corank two is already even, and \(r=1,t_p=1\) is compatible with it. Cassels–Tate duality pairs the reduced Tate–Shafarevich group after removing its maximal divisible subgroup. Its alternating-pairing consequence therefore does not force that divisible subgroup to vanish or rule out \(t_p=1\).

## Audited conclusion

The valid implication is conditional: under the cited Castella hypotheses, Selmer dimension two, and an independently known non-torsion rational point, the localization map is nonzero and \(\kappa_p(E)\) is a nonzero generator of its strict kernel. An additional independent rational point requires a separate rank-at-least-two result (or another argument eliminating the divisible-Sha contribution). The rational witness, Theorem 5.2.3, and parity do not supply that result. Consequently this route does not establish the general weak BSD lower bound.

## Primary sources

* F. Castella, [*Nonvanishing of Generalised Kato Classes and Iwasawa Main Conjectures*](https://web.math.ucsb.edu/~castella/GKC-IMC.pdf), §§5.1–5.2; in particular Remark 5.1.4, Choice 5.2.1 and Theorem 5.2.3.
* T. Dokchitser and V. Dokchitser, [*On the Birch–Swinnerton-Dyer quotients modulo squares*](https://arxiv.org/abs/math/0610290), for p-parity over \(\mathbf Q\).
* T. Trihan and C. Wüthrich, [*Parity conjectures for elliptic curves over global fields of positive characteristic*](https://doi.org/10.1112/S0010437X1100532X), §6, for the Cassels–Tate pairing and divisible radical discussion.
