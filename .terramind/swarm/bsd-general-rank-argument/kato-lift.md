# Rank-two generalized Kato class and the Kummer quotient

**Question.** If \(\operatorname{ord}_{s=1}L(E,s)=2\), can the generalized Kato class of Castella–Hsieh be shown to have zero image in
\(V_p\Sha(E/\mathbf Q):=T_p\Sha(E/\mathbf Q)\otimes_{\mathbf Z_p}\mathbf Q_p\), so that it comes from a rational point? Can the theorem produce an independent second global class?

**Conclusion.** No such deduction follows. In the theorem’s CM auxiliary-form setting, the nonzero class is in a two-dimensional \(\mathbf Q_p\)-Selmer space and is related to a derived-height regulator. Its position in the rational Mordell–Weil structure is predicted by the strong elliptic Stark conjecture, and the paper proves the p-adic line relation only after assuming finiteness of \(\Sha[p^\infty]\) and working with a Mordell–Weil basis. Neither localizations nor Cassels–Tate duality force the image of the class in \(V_p\Sha\) to vanish. A second independent Selmer vector exists by dimension if the class is nonzero, but the theorem supplies no second named class independent of it and no rational point representative absent the missing Sha-finiteness/rank input.

## Exact class and theorem setting

Use Castella–Hsieh, *On the non-vanishing of generalized Kato classes for elliptic curves of rank two*, JEMS 24 (2022), ема; arXiv:1809.09066. The primary text is [the authors’ PDF](https://www.math.ntu.edu.tw/~mlhsieh/research/Kato.pdf) (also [arXiv record](https://arxiv.org/abs/1809.09066)). Their theorem assumes \(E/\mathbf Q\) has good ordinary reduction at \(p>3\), root number +1, and \(L(E,1)=0\) (hence analytic order at least two). For the proved nonvanishing theorem choose an imaginary quadratic \(K/\mathbf Q\), discriminant prime to the conductor \(N\), with \(p=\mathfrak p\bar{\mathfrak p}\) split; a ray class character \(\psi\) of conductor prime to \(Np\); \(\chi=\psi/\psi^\tau\) with \(\chi(\bar{\mathfrak p})\ne1\); and \(g=\theta_\psi, g^*=\theta_{\psi^{-1}}\). It further assumes

* \(L(E^K,1)L(E/K,\chi,1)\ne0\);
* \(E[p]\) is irreducible as a \(G_{\mathbf Q}\)-module;
* \(N^-\), the conductor factor supported on primes inert in \(K\), is squarefree, and \(E[p]\) is ramified at each prime dividing \(N^-\).

Writing \(f\) for the newform of \(E\), \(\alpha=\psi(\bar{\mathfrak p})\), and \(\beta=\psi(\mathfrak p)\), the class at issue is
\[
\kappa_{\alpha,\alpha^{-1}}(f,g,g^*)
=\kappa(\tilde f,\tilde g_\alpha,\tilde g^*_{\alpha^{-1}})|_{S=v-1}
\in H^1(\mathbf Q,V_{fgg^*}).
\]
The Galois representation decomposes as
\[
V_{fgg^*}\simeq V_pE\oplus(V_pE\otimes\operatorname{ad}^0V_p(g))
\simeq V_pE\oplus V_pE^K\oplus\operatorname{Ind}_{K/\mathbf Q}(V_pE\otimes\chi).
\]
The paper takes the projection to \(H^1(\mathbf Q,V_pE)\); Lemma 5.1 proves this projection lies in the Bloch–Kato Selmer group, using the assumed nonzero twist L-values to give vanishing of the other Selmer summands. Denote this projection by the same \(\kappa_{\alpha,\alpha^{-1}}\). The four root choices are \(\kappa_{\alpha,\alpha^{-1}},\kappa_{\alpha,\beta^{-1}},\kappa_{\beta,\alpha^{-1}},\kappa_{\beta,\beta^{-1}}\); Theorem A makes the two mixed classes zero. The diagonal classes are proportional and span one p-adic line (Remark 1.5), not two.

Theorem A assumes, among its CM auxiliary-form hypotheses, that \(N_f^-\) is the squarefree product of an odd number of primes and that \(E[p]\) is ramified at every prime dividing \(N_f^-\). It gives \(\kappa_{\alpha,\alpha^{-1}}\ne0\Rightarrow\dim_{\mathbf Q_p}\operatorname{Sel}(\mathbf Q,V_pE)=2\), and conversely nonvanishing if this dimension is 2 and \(\operatorname{Sel}(\mathbf Q,V_pE)\ne\ker(\operatorname{Loc}_p)\). Here \(\operatorname{Loc}_p\) is restriction to \(H^1(\mathbf Q_p,V_pE)\). The theorem does not assume analytic order exactly 2; it assumes just \(L(E,1)=0\). Even in an analytic-rank-two instance, identifying that two-dimensional Selmer space with the rational Mordell–Weil tensor is a separate step.

## Kummer exact sequence: what “rational” would mean

Castella–Hsieh state the exact sequence
\[
0\longrightarrow E(\mathbf Q)\otimes\mathbf Q_p
\longrightarrow \operatorname{Sel}(\mathbf Q,V_pE)
\longrightarrow T_p\Sha(E/\mathbf Q)\otimes\mathbf Q_p
\longrightarrow0.
\]
Thus the requested vanishing is exactly the assertion that this Selmer class lies in the Kummer image of \(E(\mathbf Q)\otimes\mathbf Q_p\); it is not a consequence of being locally trivial in the Bloch–Kato Selmer sense. The quotient is the rationalized Tate module, so it detects a divisible p-primary Sha contribution. Finite Sha would make this quotient zero, but that is precisely a finiteness hypothesis, not something established from analytic order 2 by this theorem.

At good ordinary \(p\), the theorem uses the ordinary local structure and the map \(\operatorname{Loc}_p\). Its converse needs a Selmer class with nonzero formal logarithm; this proves the generalized class is nonzero, not that its Sha quotient is zero. Remark 1.4 says if \(\operatorname{Sel}=\ker(\operatorname{Loc}_p)\), then \(E(\mathbf Q)\) is finite (since it injects into \(E(\mathbf Q_p)\)); if Selmer is also nonzero, the result would be infinite \(\Sha[p^\infty]\). This is a conditional diagnostic, not a way to rule out the quotient: the hypothesis \(\operatorname{Sel}\ne\ker(\operatorname{Loc}_p)\) permits nonzero localization and says nothing about the projection to \(V_p\Sha\). Nor can one choose a linear combination of classes to make the localization vanish and infer rationality: vanishing localization is not Kummer-image membership, and the Kummer image itself need not be the kernel of localization.

## Cassels–Tate test, including its divisible radical

Cassels–Tate duality pairs the finite-level Tate–Shafarevich group (more precisely the appropriate finite quotients / \(\Sha\) modulo its maximal divisible subgroup) with values in \(\mathbf Q/\mathbf Z\). Its radical contains the maximal divisible subgroup \(\Sha_{\mathrm{div}}\); for elliptic curves the standard pairing on \(\Sha\) is nondegenerate after quotienting this divisible radical. Consequently it gives no nondegenerate pairing on \(T_p\Sha\otimes\mathbf Q_p\): an element in the rationalized Tate module comes from exactly the p-divisible direction erased by the finite Cassels–Tate pairing. Testing orthogonality against all finite classes therefore cannot prove that this component is zero. Assuming the radical vanishes (equivalently enough Sha finiteness to eliminate this issue) would insert the missing conclusion as an assumption.

There is no alternate local argument in the theorem that repairs this. Bloch–Kato local conditions constrain restrictions at every place but define the full Selmer group appearing in the exact sequence; they do not select its Kummer subspace. The theorem’s nonzero local logarithm is compatible with either a Kummer component, a nonzero Sha component, or both in the exact sequence.

## What Theorem 5.5 does and does not buy

Theorem 5.5 works “in the setting” of Section 5 and additionally assumes \(\#\Sha(E/\mathbf Q)[p^\infty]<\infty\). In its stated identification
\(\operatorname{Sel}(\mathbf Q,V_pE)\simeq E(\mathbf Q)\otimes\mathbf Q_p\), it expresses the class as a nonzero scalar times
\[
\operatorname{Log}_p(P\wedge Q)=P\otimes\log_p(Q)-Q\otimes\log_p(P),
\]
where \((P,Q)\) is a basis of \(E(\mathbf Q)\otimes\mathbf Q\), and the scalar involves the leading term of the anticyclotomic theta element and the derived p-adic height \(h_p^{(r)}(P,Q)\). The exact equality is a theorem *under this finiteness hypothesis*. It shows the class belongs to the rational Kummer image only because finiteness has already killed the quotient. It does not prove that finiteness from analytic rank 2.

Moreover, \(\operatorname{Log}_p(P\wedge Q)\) is a p-adic linear-algebra construction in \(E(\mathbf Q)\otimes\mathbf Q_p\) (or the displayed tensor expression); it is not a new rational point. Even if a vector in this tensor lies in the Kummer image, it may be a \(\mathbf Q_p\)-linear combination of rational points, not a single element of \(E(\mathbf Q)\). With finite Sha and the theorem’s Selmer dimension two one obtains rank two, hence a rational basis exists; that conclusion uses the finiteness assumption. A p-adic line alone does not produce or certify two independent rational points.

## Is a second independent global class available?

Not from the four root choices: the mixed classes vanish and the two diagonal ones are scalar multiples spanning the same line. Under the theorem’s assumptions, a nonzero diagonal class implies \(\dim_{\mathbf Q_p}\operatorname{Sel}=2\), so ordinary vector-space linear algebra guarantees some \(x\) outside its line. This is a concrete dimension deduction, but it is only existence of an abstract Selmer vector; the theorem neither constructs a second Euler-system class nor proves \(x\) maps to zero in \(V_p\Sha\). If one additionally assumes finite p-primary Sha, then both independent Selmer vectors lie in \(E(\mathbf Q)\otimes\mathbf Q_p\), giving rank two as a conditional conclusion. That does not derive unconditional independence of rational points from analytic order two.

The failure can be displayed directly from the exact sequence: a two-dimensional \(\mathbf Q_p\)-space \(S\) can contain the nonzero Kato vector \(k\) while its Kummer subspace \(A\) has dimension 0 or 1 and the quotient \(S/A\) is nonzero. The Selmer dimension theorem alone does not constrain \(A\); imposing \(A=S\) is precisely the missing assertion that \(V_p\Sha=0\). The theorem’s nonzero class and line formula do not exclude that model without the extra Sha hypothesis.

## Precisely missing for the requested lift

For an analytic-rank-two curve satisfying Castella–Hsieh’s auxiliary hypotheses, one still needs a proof that the image of \(\kappa_{\alpha,\alpha^{-1}}\) under
\[
\operatorname{Sel}(\mathbf Q,V_pE)\twoheadrightarrow T_p\Sha(E/\mathbf Q)\otimes\mathbf Q_p
\]
vanishes. A sufficient condition is finiteness of \(\Sha(E/\mathbf Q)[p^\infty]\), but deriving it here would be circular/unsupported. Theorem A gives p-adic Selmer dimension two and nonvanishing under its hypotheses; Theorem 5.5 supplies rational placement only with the finiteness assumption. Neither Cassels–Tate duality (because of its divisible radical) nor local restriction/logarithm supplies the missing vanishing. Thus this route does not yield unconditional weak BSD.

## Primary-source locations

* Castella–Hsieh, [JEMS article / arXiv:1809.09066](https://arxiv.org/abs/1809.09066): Introduction (1.4)–(1.12), Theorem A, Remarks 1.4–1.6; §5.1, Lemma 5.1 (class projection and Selmer structure); §5.3, Theorem 5.3 (derived-height formula); §5.5 (nonzero class implies Selmer dimension two); §5.6, Theorem 5.5 and Remark 5.6 (conditional Kummer-line identity). The direct [authors’ PDF](https://www.math.ntu.edu.tw/~mlhsieh/research/Kato.pdf) was checked for these statements.
* Baseline: `.terramind/swarm/bsd-research-and-formal-attempt/higher-rank.md`, which correctly notes that rank-two generalized Kato results give restricted p-adic Selmer information, not a general Mordell–Weil rank theorem.
