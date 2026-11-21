# Descent height bounds do not remove the second-point gap

## Scope and conclusion

Fix an elliptic curve (E/\mathbb Q), a prime (p), and the classical Selmer groups. This note tests whether rational representatives of bounded height on compatible (p^n)-coverings can turn a nonzero strict Selmer direction into rational points, and whether finite descent can rule out a divisible Tate–Shafarevich contribution.

The elementary height argument is valid only with a uniform bound on the **images in (E(\mathbb Q))** (or on rational points in a fixed projective embedding), independent of (n). Then Northcott yields a repeated rational point along a subsequence, and compatibility identifies the resulting inverse-limit Kummer direction with that point. This is a conditional extraction lemma, not a source of the uniform bound. A bound on (p)-adic coefficients is not a bound on point heights; conversely, a bounded-height sequence of actual rational points cannot converge to a genuinely new (\mathbb Z_p)-multiple in the Mordell–Weil completion.

The covering-height theorems found here give bounds for points **conditional on a rational point on the covering** and (in the explicit theorem of Fisher–Sills) for covering degrees 2, 3, and 4. They do not prove rational solubility of a covering or furnish a uniform bound across an unbounded (p^n)-tower. Finite descent also cannot eliminate the (T_p\Sha) / divisible-Sha alternative: every finite layer can be nonzero, and compatibility can persist in the inverse limit. No unconditional second rational direction follows.

## Kummer sequences at finite levels

The multiplication-by-(p^n) Kummer sequence of Galois modules is
\[
0\longrightarrow E[p^n]\longrightarrow E(\overline{\mathbb Q})
 \xrightarrow{[p^n]} E(\overline{\mathbb Q})\longrightarrow0.
\]
Its global and local connecting maps define
\[
0\longrightarrow E(\mathbb Q)/p^nE(\mathbb Q)
 \xrightarrow{\delta_n} H^1(\mathbb Q,E[p^n])
 \longrightarrow H^1(\mathbb Q,E)[p^n]\longrightarrow0,
\]
and the classical Selmer group is the subgroup cut out by the local Kummer images. Restricting the last map gives the exact sequence
\[
0\longrightarrow E(\mathbb Q)/p^nE(\mathbb Q)
 \xrightarrow{\delta_n}\operatorname{Sel}_{p^n}(E/\mathbb Q)
 \longrightarrow\Sha(E/\mathbb Q)[p^n]\longrightarrow0.
\]
Here the rightmost surjectivity follows from the definition of \(\Sha[p^n]\): a class killed by (p^n) has a lift to (H^1(\mathbb Q,E[p^n])), and local triviality makes each localization a local Kummer class.

For (m\ge n), the coefficient map (E[p^m]\xrightarrow{[p^{m-n}]}E[p^n]) induces the usual **downward** transition
\[
\rho_{m,n}:\operatorname{Sel}_{p^m}\longrightarrow\operatorname{Sel}_{p^n}.
\]
On the Kummer subgroup it sends
\[
\delta_m(P\bmod p^mE(\mathbb Q))\longmapsto
\delta_n(P\bmod p^nE(\mathbb Q));
\]
on the Sha quotient it is multiplication by (p^{m-n}), from
\(\Sha[p^m]\) to \(\Sha[p^n]\). In particular (\rho_{n+1,n}) is induced by multiplication by (p) on the torsion modules, not by the inclusion (E[p^n]\hookrightarrow E[p^{n+1}]). There is also the upward coefficient inclusion, which gives the other standard transition used in direct-limit (p^\infty)-Selmer; it should not be conflated with this inverse-system transition.

Taking inverse limits under \(\rho_{n+1,n}\), the Kummer terms identify with the (p)-adic completion
\[
\widehat{E(\mathbb Q)}_p=\varprojlim_n E(\mathbb Q)/p^nE(\mathbb Q)
\simeq (E(\mathbb Q)/E(\mathbb Q)_{\rm tors})\otimes\mathbb Z_p
 \oplus E(\mathbb Q)_{\rm tors}^{(p)},
\]
where (E(\mathbb Q)_{\rm tors}^{(p)}) denotes the (p)-primary torsion (canonically interpreted as its finite completion). The right-hand inverse limit is (T_p\Sha=\varprojlim_n\Sha[p^n]) with transition multiplication by (p). The finite groups \(\Sha[p^n]\) satisfy the Mittag–Leffler condition, so inverse limit preserves exactness here:
\[
0\longrightarrow\widehat{E(\mathbb Q)}_p
 \longrightarrow\varprojlim_n\operatorname{Sel}_{p^n}
 \longrightarrow T_p\Sha(E/\mathbb Q)\longrightarrow0.
\]
The strict Selmer structure used in a particular argument may replace the local conditions; then one must state its own Kummer kernel and transition maps. The formulas above are for the classical Selmer group and cannot silently be transferred to a strict subgroup.

## What bounded-height representatives would imply

Suppose (s=(s_n)_n\in\varprojlim_n\operatorname{Sel}_{p^n}) is compatible and, for an unbounded sequence (n_j), its level (s_{n_j}) is the Kummer image \(\delta_{n_j}(Q_j\bmod p^{n_j}E(\mathbb Q))\) of a rational point (Q_j\). Assume
\[
\sup_j\hat h(Q_j)<\infty.
\]
For a fixed (E/\mathbb Q), the Néron–Tate height differs from a projective Weil height by a bounded quantity. Northcott therefore implies that only finitely many rational points have this height bound. Some (Q\in E(\mathbb Q)) occurs for infinitely many (j). For any fixed (n), choose such a (j) with (n_j\ge n). Compatibility gives
\[
s_n=\rho_{n_j,n}(s_{n_j})
 =\delta_n(Q\bmod p^nE(\mathbb Q)).
\]
Thus (s) is the image of the **single rational point** (Q) in the inverse-limit Kummer subgroup. If the (Q_j) instead are rational points on covering curves (C_{n_j}\) and the covering maps (\pi_{n_j}:C_{n_j}\to E) put (\pi_{n_j}(Q_j)\) in those Kummer cosets, the required boundedness is on (\hat h(\pi_{n_j}(Q_j))\). Northcott applies to these images. A height bound on the covering coordinates alone works only if a uniform, depth-independent comparison transfers it to bounded height on (E).

This argument does **not** turn an arbitrary compatible Selmer class into rational points (Q_j). A Selmer class is an everywhere locally soluble torsor/covering. Local solubility is not rational solubility. If a covering has no rational point, it has no rational representative at all; a height inequality conditional on (C_n(\mathbb Q)\ne\varnothing) cannot supply one.

### A known-point test: \(\mathbb Z_p\)-multiples

Let (P\in E(\mathbb Q)) be non-torsion and choose the primitive unit (a=1+\sum_{j\ge2}p^{j!}\in\mathbb Z_p^\times), which is not an ordinary integer. Its compatible Kummer direction has level
\[
s_n=\delta_n(a_nP\bmod p^nE(\mathbb Q)),\qquad a_n\equiv a\pmod {p^n},
\]
where (a_n) is any integer representative of (a\bmod p^n). This is a bona fide element of the inverse-limit Kummer group. The coefficient (a) is p-adically bounded, but the canonical heights of rational representatives satisfy
\[
\hat h(kP)=k^2\hat h(P).
\]
For (a\notin\mathbb Z), every choice of integers (a_n\equiv a\pmod {p^n}) has unbounded absolute value along an unbounded subsequence: otherwise a bounded set of integers would contain one value infinitely often, forcing (a) to equal that integer in \(\mathbb Z_p\). Hence the heights of the points (a_nP) are unbounded. More strongly, if any representatives (Q_j) of this compatible direction had bounded height on an unbounded subsequence, Northcott and compatibility would force the direction to equal (Q\otimes1) for one (Q\in E(\mathbb Q)). In the free rank-one subgroup generated by (P), this requires (a\in\mathbb Z) (up to finite torsion ambiguity).

So a bound on coefficients in \(\mathbb Z_p\) does not produce a bounded-height rational point sequence, and an irrational p-adic scalar is not itself a rational point. The special direction (a=1) is represented by the same point (P) at every level; this checks that a bounded-height argument can recover an actual point when one is already present, but it says nothing about extracting new independent points from a general Selmer direction. This example is a coefficient/height test, not a strict-class example: if strictness is the kernel of the local elliptic logarithm, a non-torsion individual rational point has nonzero localization and cannot itself lie in that strict kernel. A nonzero strict class may instead be a p-adic combination of several Mordell–Weil points whose logarithms cancel; such a combination is not an individual rational point.

## Covering height theorem found and its limits

Fisher–Sills, *Local solubility and height bounds for coverings of elliptic curves* (arXiv:1103.4944), define an (n)-covering as a genus-one curve with map \(\pi:C\to E\) that becomes multiplication-by-(n\) after an isomorphism over an algebraic closure. Their Theorem 4.1(iv), for non-singular genus-one models of degree (n\in\{2,3,4\}\), gives explicit constants from the model such that for every **existing** (Q\in C(K)\),
\[
-\sum_v\log\delta_v(C)\le 2n h_C(Q)-h_E(\pi Q)
 \le-\sum_v\log\varepsilon_v(C).
\]
Equivalently their introduction states constants (B_1,B_2\), depending on the covering/model, with
\(B_1\le h_C(Q)-(1/(2n))h_E(\pi Q)\le B_2\). They explicitly note that if (C(K)\ne\varnothing\), then \(\pi(C(K))\) is a coset of (nE(K)\). The theorem controls the relative heights of a rational covering point and its image; it is useful in searches for generators.

It does not assert (C(K)\ne\varnothing\), and its explicit degree range is only (2,3,4\), not (p^n\to\infty\). The general height comparison is indexed by the covering and its model; no depth-uniform bound over compatible (p^n\)-coverings is supplied. In particular, a bound on coefficients describing the covering equations is neither a bound on rational points of (C_n\) nor a proof such points exist. Even if one separately had a uniform bound on (h_{C_n}(Q_n)\), the comparison would need constants uniform in (n\) and models before it implied a uniform bound on \(h_E(\pi_nQ_n)\). This source is a search-height theorem, not a rational-solubility theorem for Selmer torsors.

## Why finite descent leaves divisible Sha

The finite exact sequence shows exactly the obstruction:
\[
\operatorname{Sel}_{p^n}/\delta_n(E(\mathbb Q)/p^nE(\mathbb Q))\simeq\Sha[p^n].
\]
Any finite computation or finite-level vanishing statement sees only a bounded level. A divisible subgroup \(D\simeq\mathbb Q_p/\mathbb Z_p\) of \(\Sha[p^\infty]\) has (D[p^n]\simeq\mathbb Z/p^n\mathbb Z\) at every level, and its Tate module is nonzero. Thus it produces nonzero compatible Selmer classes at every (n\), with no rational Kummer representative. The finite-level class is locally soluble by definition; its global covering may remain insoluble. No finite descent bound on (\dim_{\mathbb F_p}\operatorname{Sel}_p\), or on a single (\operatorname{Sel}_{p^n}\), rules out this alternative.

If one proves independently that (\Sha[p^\infty]\) is finite, then (T_p\Sha=0\), so inverse-limit Selmer classes all come from the (p)-adic completion of Mordell–Weil. This is an effective conditional conclusion, not a finite-descent removal of the hypothesis. Finiteness is not established by the mere compatible Selmer lifts or their bounded coefficients. In the target general-rank setting, assuming the needed Sha finiteness would be an extra unproved input, and still would not show that a strict direction is represented by a rational point of positive height independent of already-known points.

## Scoped deductions versus the circular step

The following deductions are proved under their stated assumptions:

1. A compatible Kummer sequence of rational representatives with uniformly bounded canonical heights on (E(\mathbb Q)\) contains a subsequence equal to one rational point; compatibility identifies the inverse-limit class with that point.
2. A nonsingular canonical-height Gram matrix for actual rational points proves their independence, as recorded in `lower.md`.
3. If (\Sha[p^\infty]\) is finite, then its Tate module vanishes and the inverse-limit Kummer sequence has no Tate–Shafarevich quotient.

None establishes the missing premise needed in the proposed repair: that a nonzero strict direction has globally rationally soluble representatives at arbitrarily high (p^n\) level whose images have a depth-independent height bound. Nor does the height theorem supply solubility, this uniformity, or independence from a pre-existing point. To assert these properties for every nonzero strict direction and thereby produce the second rational point would be a rationality-and-height theorem of the same missing strength as the rank lower bound; deriving it from the desired rank conclusion or a BSD leading-term formula is circular.

**Precise missing lemma for this route.** Given the specified compatible strict Selmer direction (and its exact local structure), prove that for unbounded (n\) there are (Q_n\in C_n(\mathbb Q)\) on its (p^n\)-coverings, with the image points (R_n=\pi_n(Q_n)\in E(\mathbb Q)\) lying in the prescribed Kummer cosets and satisfying \(\sup_n\hat h(R_n)<\infty\); then also prove the extracted point contributes a new independent direction rather than lying in the span of the known point. No primary theorem found proves these assertions without assuming rational solubility, and no general theorem found provides the required bound uniformly in (n\).

## Primary source

- T. A. Fisher and G. F. Sills, [“Local solubility and height bounds for coverings of elliptic curves”](https://arxiv.org/abs/1103.4944), especially the definition and discussion of (n)-coverings in §1 and Theorem 4.1(iv). It treats explicit height comparison for degree 2, 3 and 4 genus-one models and conditional rational points; it does not establish rational solubility. The paper's Remark 3.9 explicitly says that an analogue of its covering-map result for general (n)-coverings is only suspected and that their method is unlikely to generalize to larger (n\).
