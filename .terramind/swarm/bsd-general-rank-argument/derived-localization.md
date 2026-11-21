# Derived classes and localization in the fixed rank-two Selmer space

## Finding

A derived class does give the second localization direction in a precise CM setting, but the verified result is a **derived elliptic unit**, not a derivative of a Kato or Beilinson–Flach class. It therefore supplies a conditional analogue of the requested second vector, not the requested general Kato/BF derivative.

The primary theorem is Castella, *Generalised Kato classes on CM elliptic curves of rank 2*, arXiv:2204.09608v3 (dated 13 February 2026), Theorems B and C. Fix (E/\mathbf Q) with CM by the imaginary quadratic field (K), and a prime (p\ge5) of good reduction that splits in (K). The source explicitly notes that splitting gives good ordinary reduction. Under positive even analytic order, Theorem B puts its generalized Kato class \(\kappa_p\) in the ordinary Selmer group
\[
S=\operatorname{Sel}(\mathbf Q,V_pE)
\]
and, when \(\dim_{\mathbf Q_p}S=2\), says \(\kappa_p\ne0\) iff \(\operatorname{loc}_p\) on \(S\) is nonzero. Theorem C assumes additionally finite \(\Sha(E/\mathbf Q)[p^\infty]\) and
\[
\operatorname{ord}_{s=1}L_p(s)=2,\qquad \operatorname{ord}_{s=1}L_p^*(s)=1.
\]
It gives the explicit basis \(S=\mathbf Q_p\kappa_p\oplus\mathbf Q_p x_p^{(2)}\), where \(x_p^{(2)}\) is Rubin’s derived elliptic unit. Theorem C proof invokes Rubin to show \(\operatorname{loc}_p(x_p^{(2)})\ne0\). Consequently \(\kappa_p\) is nonzero and lies in the one-dimensional strict kernel; \(x_p^{(2)}\) is the complementary vector with nonzero localization. This is exactly the desired pair in one fixed two-dimensional finite Selmer space, under the stated hypotheses.

This is a theorem-level match of curve, prime, reduction and local condition: (E) is the CM curve over \(\mathbf Q\), (p\ge5\) splits in its CM field and is good ordinary, and the final classes lie in the same ordinary \(\operatorname{Sel}(\mathbf Q,V_pE)\). The proof passes through anticyclotomic Selmer groups over \(K\) and a big balanced triple-product Selmer group, but those are intermediate groups with distinct local conditions. The theorem’s final control/duality argument identifies the resulting classes in ordinary \(S\); membership in the extended/balanced group alone would not establish this. The local comparison is at the prime above (p) selected by the fixed embedding, with strict kernel defined by restriction \(\operatorname{loc}_p\).

## What this establishes about Kato/BF derivatives

The generalized Kato class in Theorem B is made from a specialization/projection of a big diagonal-cycle class. The second vector in Theorem C, however, is an elliptic-unit derivative, not a derivative of that Kato class or a Beilinson–Flach class. Thus the answer is **yes for a derived class in a conditional CM theorem, but no verified source here identifies that complementary vector as the requested Kato/BF derivative**.

The CM theorem cannot simply be combined with the earlier Castella–Hsieh auxiliary construction. The current CM paper’s introduction says the non-CM approach is essentially excluded in the CM setting; for instance, it requires a prime \(\ell\ne p\) of multiplicative reduction. CM elliptic curves over \(\mathbf Q\) have integral (j)-invariant and no multiplicative primes. The earlier paper’s needed auxiliary twist nonvanishing is therefore not supplied for the same CM curve by that cited theorem. This is a failure of the cited simultaneous verification, not proof that no auxiliary data can ever work. The CM theorem is an independent construction and its local conclusion depends on finite Sha and the two assumed (p)-adic orders.

The theorem statement does not single out a numerical \((E,p)\) for which those two p-adic orders and finite-Sha condition have all been verified. Accordingly, this identifies a compatible primary theorem and exact hypotheses, not a verified numerical instance. It yields no unconditional rational-rank conclusion.

## Corollary 5.1 attribution

No verified edition containing the conflicting Corollary 5.1 sentence was found. The verified Castella–Hsieh authors’ PDF (JEMS 24 (2022), arXiv:1809.09066) has §5.1 and Lemma 5.1, not a Corollary 5.1 asserting fixed-(K) character dependence. Its Remark 1.6 discusses the position/algebraicity refinement and proportionality of the two diagonal classes for fixed data; Theorem 5.5 gives a point-valued formula under its hypotheses. Neither supplies the disputed corollary wording. The unsupported attribution and assertion are withdrawn in `auxiliary-lines-review.md`; do not restore them without a matching, independently verified edition.

## Primary sources

- F. Castella, [*Generalised Kato classes on CM elliptic curves of rank 2*, arXiv:2204.09608v3](https://arxiv.org/pdf/2204.09608), Theorems B and C, especially the CM split-prime/good-ordinary setup (§1.2) and Theorem C proof.
- F. Castella and M.-L. Hsieh, [*On the non-vanishing of generalized Kato classes for elliptic curves of rank 2* (authors’ PDF)](https://web.math.ntu.edu.tw/~mlhsieh/research/Kato.pdf), Theorem A, Lemma 5.1, Remark 1.6, Theorem 5.5; [arXiv:1809.09066](https://arxiv.org/abs/1809.09066).

## Remaining gap

For arbitrary \(E/\mathbf Q\), the missing Kato/BF lemma remains a construction in the same ordinary two-dimensional \(S\) whose localization is nonzero, with every auxiliary hypothesis simultaneously verified. The CM result only gives this basis conditionally (finite \(\Sha[p^\infty]\) and the two p-adic orders) and uses a derived elliptic unit for the second vector. Neither route proves an unconditional rational-rank lower bound.
