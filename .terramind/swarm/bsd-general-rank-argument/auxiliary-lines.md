# Varying Castella–Hsieh auxiliary data does not produce a second Selmer direction

## Question and fixed ambient space

Fix (E/\mathbf Q) and a good ordinary prime (p>3), and suppose

\[
S=\operatorname{Sel}(\mathbf Q,V_pE),\qquad \dim_{\mathbf Q_p}S=2,
\]

with restriction (\operatorname{Loc}_p:S\to H^1(\mathbf Q_p,V_pE)) of rank one. The strict space in this note means

\[
S^{\mathrm{str}}=\ker(\operatorname{Loc}_p:S\to H^1(\mathbf Q_p,V_pE));
\]

it is one-dimensional by rank-nullity. The question is whether varying the imaginary quadratic field and CM forms in Castella–Hsieh can yield projected generalized Kato classes outside this fixed line.

**Conclusion (conditional obstruction).** For each auxiliary choice satisfying the paper's hypotheses, its projected diagonal classes, after coefficient extension, lie in the scalar extension of this same (S^{\mathrm{str}}). For any pair of such choices their exterior product is zero after extension to a common coefficient field. This does not assert that the individual classes descend to (S), nor that every possible auxiliary choice meets the hypotheses, and it gives no rational-rank conclusion.

More precisely, let (L_a/\mathbf Q_p) be a finite coefficient field for choice (a), with projected class (c_a\in S\otimes_{\mathbf Q_p}L_a). For a pair (a,b), choose a finite extension (M/\mathbf Q_p) and embeddings (\iota_a:L_a\hookrightarrow M), (\iota_b:L_b\hookrightarrow M). Via (s\otimes z\mapsto s\otimes\iota_a(z)) and its b-analogue, regard both classes in (S_M=S\otimes_{\mathbf Q_p}M). The fixed localization extends to (\operatorname{Loc}_{p,M}:S_M\to H^1(\mathbf Q_p,V_pE)\otimes_{\mathbf Q_p}M); flat scalar extension preserves rank and kernel, so (\ker\operatorname{Loc}_{p,M}=S^{\rm str}\otimes M) is one-dimensional. Thus (c_a\wedge c_b=0) in (\bigwedge^2_M S_M). The embeddings may depend on the pair; this asserts no single finite field for an unrestricted family.

## Construction and maps for each choice

For a choice \(a=(K,\psi)\), the paper takes (K/\mathbf Q) imaginary quadratic, (p=\mathfrak p\bar{\mathfrak p}) split, and the ring/ray class character data described in §5.1. It sets (g_a=\theta_\psi), (g_a^*=\theta_{\psi^{-1}}), and

\[
\alpha=\psi(\bar{\mathfrak p}),\qquad \beta=\psi(\mathfrak p),
\]

with distinct roots. The global generalized Kato classes are constructed by specializing the diagonal-cycle family at the two root choices:

\[
\kappa_{\gamma,\delta}(f,g_a,g_a^*)\in H^1(\mathbf Q,V_f\otimes V_{g_a}\otimes V_{g_a^*}),
\quad \gamma\in\{\alpha,\beta\},\;\delta\in\{\alpha^{-1},\beta^{-1}\}.
\]

The target representation is identified as

\[
V_f\otimes V_{g_a}\otimes V_{g_a^*}
\simeq V_pE\otimes\operatorname{End}(V_{g_a})
\simeq V_pE\oplus(V_pE\otimes\operatorname{ad}^0 V_{g_a}).
\]

The first projection is the natural projection to the (V_pE) constituent in decomposition (1.7); no separate trace normalization is needed here. In the CM case, the trace-zero summand further decomposes as

\[
V_pE\otimes\operatorname{ad}^0(V_{g_a})
\simeq V_pE^K\oplus\operatorname{Ind}_{K/\mathbf Q}(V_pE\otimes\chi),
\qquad \chi=\psi/\psi^\tau.
\]

Thus the map to the fixed (V_pE)-cohomology is the scalar-isotypic projection for each (a), followed by the canonical identification of the (f)-representation with the fixed (V_pE). The decompositions of the auxiliary summands depend on (a); the (V_pE) target and its localization map do not. Write (c_a(\gamma,\delta)\in H^1(\mathbf Q,V_pE)) for this projection.

For choices covered by Theorem A, the projection is Selmer-valued: Lemma 5.1 says exactly this, using the vanishing of \(\operatorname{Sel}(\mathbf Q,V_pE^K)\) and \(\operatorname{Sel}(K,V_pE\otimes\chi)\) from the nonzero auxiliary twist (L)-values. This step is choice-dependent: it must be verified anew for every (K,\psi\), and it is not a formal consequence of merely having a class in the triple-product representation.

## Why all admissible projections land in the same strict line

The local map used in the paper is

\[
\log_p:S\longrightarrow\mathbf Q_p,
\]

the formal-group logarithm composed with localization at the selected prime above (p) (Introduction, Remark 1.6; in §5 it is denoted \(\log_{\omega_E,\mathfrak p}\)). The paper's argument gives, for the diagonal classes, membership in \(\ker(\log_p)\): Theorem 5.3 expresses the derived-height pairing of the class against (x\) as a nonzero scalar times \(\log_p(x)\); in the rank-two case the derived height is a nondegenerate alternating pairing on (S) (the reduction (5.8) and §5.4). Substituting the class itself in the pairing gives \(\log_p(c_a)=0\). Remark 1.6 states the resulting line explicitly: for fixed (g_a\), the two diagonal classes span \(\ker(\log_p)\).

Under the present assumptions, \(\log_p\) is nonzero: the stated rank-one localization, together with the Bloch–Kato local condition at good ordinary (p), puts the local image in the one-dimensional finite subspace on which the formal logarithm is an isomorphism up to the chosen nonzero differential normalization. Consequently

\[
\ker(\log_p)=\ker(\operatorname{Loc}_p)=S^{\mathrm{str}},\qquad \dim S^{\mathrm{str}}=1.
\]

This equality uses that the localizations of Selmer classes lie in the finite local subspace; it would not follow for an arbitrary map on all of (H^1(\mathbf Q_p,V_pE)). Therefore for any two admissible auxiliary choices (a,b), and any diagonal roots,

\[
c_a(\alpha,\alpha^{-1}),c_b(\alpha',\alpha'^{-1})\in S^{\mathrm{str}},\qquad
c_a(\alpha,\alpha^{-1})\wedge c_b(\alpha',\alpha'^{-1})=0
\quad\text{after common scalar extension, in }\bigwedge^2_M(S\otimes_{\mathbf Q_p}M).
\]

The assertion also holds if either projected class is zero. For the two roots within one fixed (a), the stronger statement in Remark 1.6 is that the diagonal classes are proportional (and nonzero under Theorem A's converse hypotheses). For varying (a,b), the paper does not assert equality of normalized classes or an algebraic proportionality constant across choices; the common one-dimensional ambient kernel alone proves proportionality over \(\mathbf Q_p\).

The theorem's converse hypothesis is (S\ne\ker(\operatorname{Loc}_p)\), equivalently \(\operatorname{Loc}_p\ne0\) on (S). The task's rank-one localization supplies this. Theorem A also requires, separately for each auxiliary choice: root number (+1) and (L(E,1)=0); (L(E^K,1)L(E/K,\chi,1)\ne0); irreducibility of (E[p]); (N_f^-\) squarefree with an odd number of prime factors; and ramification of (E[p]) at every prime dividing (N_f^-\). The setup also requires the prescribed class-character conductors and distinct roots. Dimension two plus rank-one localization alone does not validate a choice that fails any of these conditions.

## Other components and possible lifts

The unprojected triple-product class has components in (V_pE\), (V_pE^K\), and \(\operatorname{Ind}_{K/\mathbf Q}(V_pE\otimes\chi)\). These latter two components are not elements of (S\): they belong to different Galois representations and hence cannot be used as vectors outside (S^{\mathrm{str}}\). Under the nonvanishing twist hypotheses, the proof of Lemma 5.1 uses the vanishing of the complementary Selmer groups, so the components of these Selmer classes there are zero. They do not furnish nonzero lifts in the fixed (\operatorname{Sel}(\mathbf Q,V_pE)\).

Among the four (p\)-root choices for a given (a), Theorem A says the two mixed-root projections vanish. The two diagonal projections are the only potentially nonzero ones; they lie on the common strict line and are proportional for fixed (a). Thus neither root variation nor changing admissible (K,\psi\) gives a second direction in the specified (S\). This does not rule out other constructions of classes in (S\), nor does it prove an impossibility theorem for all auxiliary Euler systems.

## What this does not say about rational rank

The conclusion is conditional on the existence of admissible auxiliary choices and on the fixed Selmer/localization assumptions. It is only a dependence statement among these particular projected cohomology classes. The Kummer exact sequence

\[
0\to E(\mathbf Q)\otimes\mathbf Q_p\to S\to T_p\Sha(E/\mathbf Q)\otimes\mathbf Q_p\to0
\]

does not identify (S^{\mathrm{str}}\) with a rational subspace or show that its nonzero classes come from (E(\mathbf Q)\otimes\mathbf Q_p\). Castella–Hsieh's Theorem 5.5 makes its formula inside that Kummer image only after assuming \(\#\Sha(E/\mathbf Q)[p^\infty]<\infty\). Accordingly this argument neither derives a rational point nor proves or refutes \(\operatorname{rank}E(\mathbf Q)=\operatorname{ord}_{s=1}L(E,s)\); it only shows why this particular auxiliary variation cannot supply two independent Selmer classes in the fixed setting.

## Coefficient descent and scope of the source statements

The common-field argument proves only that the two images become collinear after the chosen embeddings into (M). Descent of either class to (S) would require its Galois/coefficient invariance under (\operatorname{Gal}(L_a/\mathbf Q_p)) (and the corresponding descent datum); collinearity after scalar extension does not imply that invariance. The paper’s fixed-(K) character-variation statement gives no comparison across distinct quadratic fields; the cited PDF version has §5.1 (not a Corollary 5.1), so the lead’s numbered reference must be checked against the intended edition before reuse. Any varying-(K) claim used here instead follows pairwise from the common fixed Selmer space and kernel argument above, provided every individual choice satisfies the theorem and yields a class in that kernel.

## Primary-source audit

Castella–Hsieh, *On the non-vanishing of generalized Kato classes for elliptic curves of rank 2*, JEMS 24 (2022), [authors' PDF](https://web.math.ucsb.edu/~castella/Kato.pdf), [arXiv:1809.09066](https://arxiv.org/abs/1809.09066): Introduction §1.1, equations (1.5), (1.7)–(1.10), Theorem A, Remarks 1.5–1.6; §5.1 and Lemma 5.1 (projection to H^1(Q,V_pE) is Selmer-valued); §5.2 (mixed-root vanishing); §5.3, Theorem 5.3 and the rank-two reduction in §5.4 (derived-height formula and local logarithm); §5.5 (dimension implication); §5.7 and Theorem 5.5 (finite-Sha qualification for the Kummer-image formula). The source is explicit that its analytic assumption is (L(E,1)=0), not analytic order exactly two.
