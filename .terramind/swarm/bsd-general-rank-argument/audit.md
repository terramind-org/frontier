# Combined audit of the two rank implications

Cutoff: 21 November 2026. Fix an elliptic curve (E/\mathbb Q). Write
\[
r_{\rm alg}(E)=\operatorname{rank}_{\mathbb Z}E(\mathbb Q),\qquad
r_{\rm an}(E)=\operatorname{ord}_{s=1}L(E,s).
\]
Modularity gives analytic continuation at the center; the order is finite. The weak BSD claim is the conjunction
\[
r_{\rm alg}(E)\le r_{\rm an}(E)\quad\text{and}\quad
r_{\rm an}(E)\le r_{\rm alg}(E)
\]
for every (E/\mathbb Q). Neither inequality follows from the other. Their combination is exactly equality; no regulator, leading coefficient, or finiteness of the full Tate–Shafarevich group is needed for this rank statement.

## Direction A: algebraic rank at most analytic rank

For each prime (p), the Kummer sequence gives
\[
0\longrightarrow E(\mathbb Q)\otimes\mathbb Q_p/\mathbb Z_p
\longrightarrow \operatorname{Sel}_{p^\infty}(E/\mathbb Q)
\longrightarrow \Sha(E/\mathbb Q)[p^\infty]\longrightarrow0.
\]
Thus (r_{\rm alg}\le\operatorname{corank}_{\mathbb Z_p}\operatorname{Sel}_{p^\infty}), without assuming Sha finite. To prove Direction A by this route one needs an unconditional bound on that Selmer corank by (r_{\rm an}) for each curve (or at least for a suitable prime for each curve), with compatible local conditions and descent.

The cyclotomic main-conjecture route in `upper.md` does not provide this. Skinner–Urban prove a main-conjecture equality for a specified ordinary modular-form class under stated residual, level, and other hypotheses. Even in that setting the characteristic series is for a (p)-adic L-function and a particular Iwasawa Selmer group. Specialization/control, comparison with the classical Selmer structure, and the order of the corrected (p)-adic L-function versus the *complex* (L(E,s)) still need proof. Interpolation of values is not an equality of the two central vanishing orders. An exceptional zero at split multiplicative reduction changes the (p)-adic order and needs its explicit correction. The missing universal comparison is therefore substantive, not just a choice of notation or a consequence of the main conjecture.

**Status:** no unconditional proof of Direction A for arbitrary (E/\mathbb Q) is given or found. Rank-zero/one results do not establish it in arbitrary rank. Do not use finiteness of Sha to replace Selmer corank by rank in the general case.

## Direction B: analytic rank at most algebraic rank

For (r=r_{\rm an}), the precise point-construction statement that would suffice is: there exist (P_1,\ldots,P_r\in E(\mathbb Q)) with nonsingular Néron–Tate Gram matrix
\[
G=(\langle P_i,P_j\rangle),\qquad \det G\ne0.
\]
The canonical height pairing is positive definite on (E(\mathbb Q)\otimes\mathbb R), so this condition implies independence modulo torsion and (r_{\rm alg}\ge r_{\rm an}). This implication is unconditional **given those rational points**. Conversely, Mordell–Weil and positive definiteness supply such a matrix of size (r_{\rm alg}), not (r_{\rm an}) unless the desired inequality is already known.

Gross–Zagier and Kolyvagin supply the classical construction/ rank result in analytic rank zero or one under their hypotheses. They do not iterate to arbitrary order. A nonzero higher complex derivative is a scalar, not (r) rational points. Higher derived (p)-adic heights, generalized Kato classes, and Selmer-dimension conclusions likewise do not by themselves produce rational points: classes can be non-rational or fail to descend, and Selmer groups include the Sha contribution. Tracing extension-field points may give zero, torsion, or dependent rational points. Each of these bridges needs its own theorem; none follows merely from a nonzero derived class or a height pairing on a Selmer group.

The missing universal assertion in point form is:

> For every (E/\mathbb Q), there are (r_{\rm an}(E)) rational points whose Néron–Tate height matrix is nonsingular.

This is equivalent in strength to Direction B: the point assertion implies it by the Gram criterion; if Direction B is true, choose a basis of the free Mordell–Weil quotient of size at least (r_{\rm an}), whose canonical-height matrix is positive definite. This equivalence is a diagnostic restatement, not a proof. Do not infer this assertion from conjectural finiteness of Sha or from a Selmer corank lower bound.

**Status:** Direction B is proved in the established analytic-rank-zero/one range, but no unconditional proof for arbitrary rank is supplied or found.

## Combined conclusion and no-circularity check

Both inequalities together give (r_{\rm alg}=r_{\rm an}). Auditing both therefore does not close the gap: the unresolved universal statements are (A) a Selmer-corank-to-complex-order upper bound with the required local/control/(p)-adic comparison, and (B) a rational-point/height-matrix lower bound. In particular:

* A main conjecture for one (p)-adic Selmer structure is not itself either required inequality.
* Finiteness of Sha would identify Selmer corank and Mordell–Weil rank at a prime, but it is not known generally and does not compare either with the complex order.
* Assuming the full BSD rank equality, a p-adic BSD equality, a universal leading-term formula, or the point-matrix assertion as an input simply assumes the missing conclusion in equivalent or stronger form.
* The converse (r_{\rm an}\le r_{\rm alg}) cannot repair a missing upper bound (r_{\rm alg}\le r_{\rm an}), nor vice versa.

Accordingly, no full unconditional proof of weak BSD for all elliptic curves over \(\mathbb Q\) exists in this audit. The correct outcome is two precise unproved implications, not a proof assembled by identifying algebraic and analytic ranks.

## Primary sources checked

1. C. Skinner and E. Urban, [“The Iwasawa Main Conjectures for GL₂”](https://www.math.columbia.edu/~urban/eurp/MC.pdf), especially introduction, Theorem 1 and §1.2. The paper states a theorem for a large class and lists its hypotheses; it defines the ordinary Selmer group and interpolation factors. This verifies the limitation described in `upper.md`, not a universal BSD implication.
2. B. Gross and D. Zagier, [“Heegner points and derivatives of L-series”](https://doi.org/10.1007/BF01388809), *Invent. Math.* 84 (1986), 225–320; V. Kolyvagin, [“Finiteness of (E(\mathbb Q)) and (Ш(E,\mathbb Q)) for a subclass of Weil curves”](https://doi.org/10.1070/IM1989v032n03ABEH000779), *Math. USSR-Izv.* 32 (1989), 523–541. These are the classical first-derivative/Euler-system sources, not arbitrary-rank theorems.
3. F. Castella, C.-Y. Hsu, D. Kundu, Y.-S. Lee, Z. Liu, [“Derived (p)-adic heights and the leading coefficient of the BDP (p)-adic (L)-function”](https://arxiv.org/abs/2308.10474), revised 2025. Its abstract states the Heegner-field and split-good-prime setting and formulates a (p)-adic BSD conjecture; it does not claim universal rational-point construction.
4. F. Castella and M.-L. Hsieh, [“On the non-vanishing of generalized Kato classes for elliptic curves of rank 2”](https://arxiv.org/abs/1809.09066). Its abstract explicitly concludes a two-dimensional (p)-adic Selmer group from nonvanishing, which is not itself two independent rational points.
5. B. Mazur, J. Tate, J. Teitelbaum, [“On (p)-adic analogues of the conjectures of Birch and Swinnerton-Dyer”](https://doi.org/10.1007/BF01388731), *Invent. Math.* 84 (1986), 1–48; R. Greenberg and G. Stevens, [“(p)-adic L-functions and (p)-adic periods of modular forms”](https://doi.org/10.1007/BF01231297), *Invent. Math.* 111 (1993), 407–447. These supply the exceptional-zero context; the corrected (p)-adic leading term must not be silently identified with the complex order.

The primary source material supports the stated scope and failure points. Claims above about the equivalence of the point-matrix statement and Direction B are deductions from Mordell–Weil and positive definiteness of the canonical height, not claims quoted from those sources. No source is offered as proving weak BSD in all ranks.

## Prior-note availability

The task brief asked for the earlier swarm notes `iwasawa.md` and `higher-rank.md`; neither file is present in this worktree. The combined audit used the available `upper.md`, `lower.md`, and their embedded primary-source references. It did not access other workers' directories. The `lower.md` itself records prior-swarm references and the relevant source conclusions, but this is not a substitute for inspecting the absent note files.
