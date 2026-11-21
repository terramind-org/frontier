# Non-CM projection test: what survives, and what it proves

## Result

There is a primary-theorem construction for an ordinary non-CM elliptic curve which projects a *diagonal-cycle* class attached to (f_E) and a dual pair of auxiliary CM theta Hida families to (V_pE). Castella's 2023 note (arXiv:2312.01481, §5.1) defines this projected class κ_p(E) and proves its local properties. It is the Darmon–Rotger generalized Kato class, not the classical Beilinson–Kato Euler-system class. It is already known in this setting; it does not furnish a new universal rank-two class or prove it is nonzero.

A more literal Beilinson–Flach construction with an auxiliary CM family degenerating to a weight-one Eisenstein series also exists for ordinary (f_E). Bertolini–Darmon–Venerucci, Theorem 4.2 and §5.1, give the specialization and Galois-equivariant character projection; their comparison identifies the projected class, up to explicit factors and the relevant quadratic twist, with Beilinson–Kato classes. That projection is not Castella's generalized Kato class used in the rank-two argument. Neither construction supplies the missing nonzero finite localization required for a general rank-two implication.

## First CM-specific input in the reviewed v3 argument

Castella v3 (arXiv:2204.09608v3) is CM-specific already at the start of §1.1's proof strategy: its weight-two family φ and both auxiliary families (g,h) are CM by one fixed imaginary quadratic field (K), with (p) split. The displayed representation decomposition (1.2) into four induced Hecke-character summands then gives the Selmer decomposition (1.4) into anticyclotomic Hecke-character Selmer groups. The main-conjecture input is the anticyclotomic main conjecture for those characters, together with the triple-product/Katz (p)-adic (L)-function factorization. That factorization and character-Selmer control are the intrinsically CM mechanism; they are not consequences of merely projecting a Rankin/Beilinson–Flach class.

The specialization to the curve in §1.2 makes the dependence explicit: (E) has CM by (K), (p) splits in (K), and (V_pE) is identified with the induced representation of the Hecke character ψ_E. The class is obtained from a big diagonal class for ((\theta(\lambda_0),\theta_{\lambda_1}(S_1),\theta_{\lambda_2}(S_2))), projected to an induced summand and specialized at (W_1=0). Theorem C further requires finite (\Sha(E/\mathbf Q)[p^\infty]), (\operatorname{ord}_{s=1}L_p(s)=2), and (\operatorname{ord}_{s=1}L_p^*(s)=1). It is therefore not an unconditional all-curves theorem even within the CM family.

Sources: [Castella, v3, §§1.1–1.3 and Theorems B–C](https://arxiv.org/pdf/2204.09608v3).

## The primary non-CM projection that does exist

Let (E/\mathbf Q) have conductor (N_f), and let (p>3) be a prime of good ordinary reduction. Let (f) be the ordinary (p)-stabilization of its weight-two newform. Choose a dual pair of primitive CM Hida families (g=\theta_\psi(S_1)), (g^*=\theta_{\psi^{-1}}(S_2)), associated with an auxiliary imaginary quadratic field (K) in which (p) splits, and satisfying Castella's condition (3.2) on (\chi=\psi/\psi^c). These are auxiliary CM forms; (E) itself need not have CM.

Castella, arXiv:2312.01481, §5.1, Definition 5.1.1, starts with the big diagonal class \(\kappa(f,gg^*)\), not a two-factor Beilinson–Flach class. Shapiro's lemma and the explicit direct-sum decomposition (5.1) project it to the first summand
\[
 H^1(K,T_f\otimes\Psi_T^{1-c})
 \longrightarrow H^1(K,T_f),
\]
where the second arrow is induced by multiplication by the augmentation parameter (T), followed by specialization at (T=0). Since (T_f\simeq T_pE) at the weight-two specialization, the target is (H^1(K,T_pE)). This is a theorem-defined specialization/projection, not a conjectural projection of an unspecified auxiliary family. The resulting (\kappa_p(E)) is precisely the generalized Kato class of Darmon–Rotger in the adjoint case.

The explicit reciprocity law is Theorem 4.1.1. On the ordinary quotient (T_f^-=T_f/T_f^+) at a prime of (K) above (p), the big regulator
\[
 \mathrm{Log}_f:H^1(K_p,T_f^-\otimes\Psi_T^{1-c})\longrightarrow\Lambda
\]
satisfies
\[
 \mathrm{Log}_f\bigl(p_f^-(\operatorname{loc}_p\kappa(f,gg^*))\bigr)
 = L_p^f(f,gg^*).
\]
At the weight-two specialization (T=0), the local map on the relevant ordinary quotient is the Bloch–Kato dual exponential (\exp_p^*); at higher specializations it is the Bloch–Kato logarithm. Thus this reciprocity law detects the image in the *singular quotient* (H^1(K_p,V_pE)/H^1_f(K_p,V_pE)), not a nonzero class in the finite subspace.

In the paper's normalization the specialization identity gives
\[
 \exp_p^*(\operatorname{res}_p\kappa_p(E))=0
 \quad\Longleftrightarrow\quad
 L(f/K,1)L(f/K\otimes\chi,1)=0.
\]
If (L(E,1)=0) and (L(E_K,1)\ne0), Corollary 5.1.3 uses Kato's vanishing result for the twist (E_K) to descend from (K) to (\mathbf Q); Remark 5.1.4 says the class is in fact strict at (p): its localization in (H^1(\mathbf Q_p,V_pE)) is zero. Zero localization is in (H^1_f), but the reciprocity law then says nothing that could certify a nonzero finite localization. A nonzero value of the dual exponential would instead certify a nonzero singular quotient and obstruct the Bloch–Kato finite condition. These are different claims.

## Hypotheses and rank-two implication

The non-CM specialization is available under the modular/ordinary and auxiliary-family conditions above. For the nonvanishing criterion in Theorem 5.2.3, Castella additionally assumes positive even analytic rank and the residual hypotheses (h1)–(h3): (\bar\rho_{E,p}) absolutely irreducible; a prime (q\nmid N_f) with ramification at (q) if (q\equiv\pm1\pmod p); and either (p>5) or the residual image contains a conjugate of (\mathrm{GL}_2(\mathbf F_p)). The auxiliary choice in 5.2.1 includes (\ell\nmid6pN_f), the splitting/inertness conditions on (K), (L(E_K,1)\ne0), (L(E/K,\chi,1)\ne0), and (\chi|_{G_{K_p}}\ne1). The note explains existence of suitable choices subject to those residual conditions; it does not remove the conditions.

Under these hypotheses, Theorem 5.2.3 proves
\[
 \kappa_p(E)\ne0\;\Longrightarrow\;\dim_{\mathbf Q_p}\mathrm{Sel}(\mathbf Q,V_pE)=2.
\]
Conversely, if that Selmer space has dimension two, then (\kappa_p(E)\ne0) if and only if the restriction map (\mathrm{loc}_p:\mathrm{Sel}(\mathbf Q,V_pE)\to E(\mathbf Q_p)\widehat\otimes\mathbf Q_p) is nonzero; in that event (\kappa_p(E)) spans its kernel (the strict Selmer line). This is not a proof that the localization map is nonzero. Positive even analytic rank gives (L(E,1)=0), hence (with the auxiliary twist condition) Selmer membership and strict local vanishing, but not nonvanishing of the projected class. The converse direction still has exactly the nonzero-localization hypothesis, and the theorem's residual and auxiliary assumptions remain in force.

Sources: [Castella, nonvanishing of generalized Kato classes and Iwasawa main conjectures, §§4–5](https://arxiv.org/pdf/2312.01481); [Castella–Hsieh, Theorem A and its hypotheses](https://arxiv.org/pdf/1809.09066).

## Why the proposed Beilinson–Flach shortcut does not close the gap

For ordinary (f_E), the primary construction of Bertolini–Darmon–Venerucci uses a Coleman family through the (p)-irregular weight-one Eisenstein series (\mathrm{Eis}_1(\varepsilon_K)), whose Galois representation is (1\oplus\varepsilon_K). Theorem 4.2 compares the Beilinson–Flach class with the two character components of the Beilinson–Kato system; §5.1 specializes this identity and gives the projected formula. When (L(f,1)=0), the component involving (L_p(f)\zeta_{f,\varepsilon_K}^{\mathrm{Kato}}) drops out, and the other is proportional to (L_p(f\otimes\varepsilon_K)\zeta_f^{\mathrm{Kato}}\otimes v_{g,1}). Thus, when that twist factor is nonzero, the trivial-character projection is the classical Beilinson–Kato class up to a nonzero scalar. If it vanishes, that identity does not certify a nonzero projection. This is not Castella's generalized Kato class: that class comes from a three-form diagonal-cycle construction with a dual theta pair and the augmentation-parameter specialization above. Replacing that geometry with the Eisenstein degeneration changes the class and its reciprocity law.

Moreover, the classical Beilinson–Kato explicit reciprocity law controls the local dual exponential by a (p)-adic (L)-value. At a central zero it can establish vanishing of the singular image, which is compatible with finiteness; it cannot by itself establish that the finite localization is nonzero. The generalized class's theorem-level reciprocity likewise makes the class finite/strict at (p) when the central value vanishes, while the two-dimensional theorem makes its nonvanishing equivalent (in the stated setting) to a separate nonzero Selmer localization map. The rank-two vanishing therefore supplies the local condition but not the missing nonzero finite localization. No unconditional weak-BSD implication for arbitrary non-CM (E/\mathbf Q) follows.

Source: [Bertolini–Darmon–Venerucci, *Heegner points and Beilinson–Kato elements*, §4.2, Theorem 4.2](https://www.esaga.uni-due.de/f/massimo.bertolini/publications/BDV-Final.pdf).

## Precise remaining obstruction

To turn this route into the requested unconditional implication one would need, for every relevant non-CM (E/\mathbf Q), a theorem proving that the correctly normalized projected generalized class is nonzero in the finite/strict Selmer space (or proving (\mathrm{loc}_p(\mathrm{Sel}(\mathbf Q,V_pE))\ne0) once its dimension is two), with all auxiliary choices and residual hypotheses removed or proved available. The available rank-two results do not provide that uniform assertion. A nonzero singular quotient is the wrong substitute: it violates the finite local condition instead of producing a nonzero finite localization.
