# Independent review: the second Selmer direction

## Verdict

Castella's Theorem C gives a valid conditional second direction for the same fixed pair \((E,p)\) and the same two-dimensional space
\[
S=\operatorname{Sel}(\mathbf Q,V_pE),
\]
but it is specifically a derived elliptic unit, not a derivative of the generalized Kato or Beilinson–Flach class. The hypotheses are compatible as a single theorem's hypotheses; the paper supplies no numerical \((E,p)\) for which all analytic and Sha assumptions have been independently verified. The result is conditional and is not a rational-rank lower bound.

## Common curve, prime, local condition, and Selmer space

The source fixes a CM elliptic curve \(E/\mathbf Q\), its CM field \(K\), and a prime \(p\ge5\) split in \(K\). It explicitly notes that splitting gives good ordinary reduction. It assumes positive even complex analytic order at \(s=1\). Theorem B then attaches, for any Hecke-character triple satisfying (1.5) and Theorem A (i)–(ii), a generalized Kato class \(\kappa_p\in S\). The theorem's restriction map is
\[
r_p:S\longrightarrow E(\mathbf Q_p)\widehat\otimes\mathbf Q_p.
\]
In dimension two, it states \(\kappa_p\ne0\) iff \(r_p\ne0\); the introduction further says that when nonzero, \(\kappa_p\) generates the one-dimensional kernel of \(r_p\).

Theorem C adds finite \(\Sha(E/\mathbf Q)[p^\infty]\) and the two Katz p-adic order conditions \(\operatorname{ord}_{s=1}L_p(s)=2\) and \(\operatorname{ord}_{s=1}L_p^*(s)=1\). It concludes that this same \(S\) is two-dimensional and has basis \((\kappa_p,x_p^{(2)})\), with \(x_p^{(2)}\) a derived elliptic unit. Its proof specifically places \(x_p^{(2)}\in\operatorname{Sel}(K,T_pE)\simeq\operatorname{Sel}(\mathbf Q,T_pE)\), and says the Rubin theorem plus the hypotheses imply \(r_p(x_p^{(2)})\ne0\). Thus the candidate is not merely in an intermediate anticyclotomic or balanced Selmer group: it belongs to the same global Selmer space and satisfies the same restriction map.

## Simultaneous hypotheses and independence

There is no conflict between the shared assumptions: Theorem C expressly requires the hypotheses of Theorem B, then adds finite p-primary Sha and the two p-adic order conditions. Positive even complex analytic order is compatible with those conditions; in fact, the p-adic order 2 is used in the cited proof to get the upper Selmer-dimension bound, while Coates–Wiles and p-parity give the lower bound. The source also states that the required character triples for Theorem B exist (indeed infinitely many) under its setup. These facts establish theorem-level compatibility, not a verified arithmetic instance: neither the two p-adic orders nor finite Sha are demonstrated for a named curve and prime.

Independence follows in two ways within the source. Theorem C states the direct-sum decomposition. More structurally, \(x_p^{(2)}\) has nonzero restriction, whereas the nonzero \(\kappa_p\) spans \(\ker r_p\). Therefore they cannot be proportional. The p-adic orders are hypotheses about the two Katz p-adic L-functions attached to \(E,p,K\), not choices of auxiliary triple; the triple is used to construct \(\kappa_p\), and the paper says different valid triples give the same class up to scaling. Thus no mixing of different \(E,p\), coefficient fields, or Selmer targets is needed for this second direction.

## Arithmetic meaning and limits

The basis is a statement about the p-adic Selmer group, not two independent rational points. The source records the exact sequence
\[
0\to E(\mathbf Q)\otimes_{\mathbf Z_p}\mathbf Q_p\to S\to \mathbf Q_p\otimes_{\mathbf Z_p}T_p\Sha(E/\mathbf Q)\to0.
\]
Finiteness of \(\Sha[p^\infty]\) removes the p-adic Tate-module contribution and identifies the Selmer dimension with the Mordell–Weil rank in this setting. But Theorem C assumes that finiteness; it does not prove it unconditionally, nor does the basis theorem itself give two point-valued generators. It therefore cannot supply an unconditional second rational point direction or the general BSD lower bound.

The strongest supported conclusion is: **for CM \(E/\mathbf Q\) and split ordinary \(p\), conditional on positive even complex order, finite p-primary Sha, and the stated Katz p-adic orders, a derived elliptic unit complements the generalized Kato class in the same two-dimensional \(\mathbf Q_p\)-Selmer group, with nonzero localization.** No analogous Kato/BF derivative is established here for arbitrary elliptic curves.

## Citation correction

The current primary citation is Francesc Castella, *Generalised Kato classes on CM elliptic curves of rank 2*, arXiv:2204.09608v3, last revised 13 February 2026, Theorems B and C and §1.2–1.3. Version 3 is the final version noted as to appear in the *American Journal of Mathematics*. Its abstract itself specifies the common \(\operatorname{Sel}(\mathbf Q,V_pE)\) target and the restriction-map criterion; Theorem C and its proof give the added assumptions, derived unit, and nonzero restriction. Cite the pinned version URL so the edition is reproducible: https://arxiv.org/abs/2204.09608v3.

The corrected Castella–Hsieh authors' PDF remains relevant only to the separate auxiliary construction and its Lemma 5.1/Remark 1.6/Theorem 5.5 discussion. It does not establish that the CM derived elliptic unit is a Kato/BF derivative, and it does not supply the missing arbitrary-curve construction. The withdrawn Corollary 5.1 assertion remains unsupported.

## Remaining gap

For the general BSD argument, the missing lemma remains a construction, for arbitrary \(E/\mathbf Q\) and relevant \(p\), of a second class in the very same ordinary Selmer group with nonzero localization, with the full simultaneous hypotheses established. Even in the CM theorem, the finiteness of p-primary Sha and both p-adic order assumptions are conditional and no numerical instance was certified here. A Selmer basis alone does not yield rational points unless the Sha contribution is controlled.

## Primary sources

- F. Castella, [*Generalised Kato classes on CM elliptic curves of rank 2*, arXiv:2204.09608v3](https://arxiv.org/abs/2204.09608v3), especially Theorems B and C, §1.2–1.3, and the proof of Theorem C.
- F. Castella and M.-L. Hsieh, [*On the non-vanishing of generalized Kato classes for elliptic curves of rank 2*, authors' PDF](https://web.math.ntu.edu.tw/~mlhsieh/research/Kato.pdf), for the distinct auxiliary construction.
