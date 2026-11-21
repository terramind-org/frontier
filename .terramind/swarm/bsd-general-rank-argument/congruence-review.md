# Independent audit of the congruence rank-induction argument

Audit date: 21 November 2026. Scope: the quoted theorem statements and the proposed inference from level raising/Jochnowitz congruences to an induction on complex analytic rank. The primary texts checked were Zhang's paper, Bertolini–Darmon, and Vigni.

## Finding

The central negative inference in `congruence.md` is sound: congruence of residual Hecke eigensystems does not give a relation between the complex orders of vanishing of the two (L)-functions, nor a map transporting Mordell–Weil points between the two characteristic-zero abelian varieties. The cited Jochnowitz results compare particular algebraically normalized quantities modulo a residual maximal ideal. They do not establish an analytic-rank drop by one. Consequently they do not supply the induction step required for weak BSD in arbitrary rank.

The restricted Selmer-dimension statement is also supported by Zhang, Proposition 5.4, but it must be read with its exact Selmer structures and hypotheses. It is a genuine conditional one-dimensional drop, and the proposition itself does not use BSD. It is not a rank statement for (E/\mathbb Q).

## Exact statements and quantifiers

1. **Level raising (Zhang, Theorem 2.1).** For a weight-two newform (g) of level (N) with trivial nebentypus, a prime (p\) of its coefficient ring with irreducible residual representation and residue characteristic at least 5, and *each admissible prime* (q) (as defined in the paper's setup), the theorem supplies a weight-two newform (g') of level (Nq), a prime (p'\) above the same residual characteristic, and an isomorphism of residual representations. Equivalently, the Hecke eigenvalues agree modulo the selected primes for every Hecke index \(\ell\ne q\). This is not a statement for arbitrary (q\), arbitrary (E,p\), or about complex (L\)-values. The term “admissible” carries the paper's restrictions; it is not merely (q\nmid NpD_K\).

2. **Zhang's Proposition 5.4.** In the section's fixed setup (including its hypotheses on \((g,p,K)\), its coefficient primes, and the level-raised pair \((A,A')\)), assume the localization
   \[
   \operatorname{loc}_q:\operatorname{Sel}_{p_0}(A/K)\longrightarrow H^1_{\rm fin}(K_q,V)=H^1(K_q,k_0)
   \]
   is surjective. The target is one-dimensional, so “nontrivial” is equivalent to “surjective.” Then Zhang obtains
   \[
   \dim_{k'}\operatorname{Sel}_{p'}(A'/K)=\dim_k\operatorname{Sel}_{p}(A/K)-1,
   \]
   and identifies the left Selmer group, under the residual-representation identifications in the setup, with the kernel of localization on the *relaxed* group \(\operatorname{Sel}_{p_0}(A/K)\). In Zhang's notation this is the equality \(\operatorname{Sel}_{p'}(A'/K)=\operatorname{Sel}_s(K,V)=\ker(\operatorname{loc}_q:\operatorname{Sel}_r(K,V)\to H^1_{\rm fin}(K_q,V))\). It is essential not to silently replace the relaxed group by the ordinary Selmer group in the kernel assertion. The paper's dimension formula uses the indicated coefficient residue fields; it does not identify the two characteristic-zero Selmer groups.

   The proof cited by Zhang is the local-condition/parity comparison in Lemma 5.3: away from (q\) the selected structures agree, and at (q\) relaxed/strict conditions differ by the one-dimensional finite local condition. Thus the dimension drop is conditional on a nonzero localization; it is not a theorem that every surviving class has nonzero localization at a preselected prime.

3. **Bertolini–Darmon, Theorem 1.3.** In their specified Heegner/level-raised setting, nonzero image of the Heegner point in \(E(K_q)/pE(K_q)\) is equivalent to nonvanishing modulo the chosen maximal ideal of the algebraic part of \(L(g/K,1)\), for every newform (g\) on the indicated raised-level quotient. Their text explains the relation to \(L'(f/K,1)\) through Gross–Zagier. A consequence is nonvanishing of the auxiliary central value in that setting, hence analytic order zero for that auxiliary base-change (L)-function. It gives no assertion that the auxiliary order is (r-1\) for arbitrary (r\), and no comparison of exact complex orders.

4. **Vigni, Theorem 1.1 / abstract.** The formulation explicitly has opposite functional-equation signs: the original (L_K(E,s)\) has sign \(-1\), while the level-raised form's (L_K(g,1)\) has sign \(+1\). The theorem is a congruence between the algebraic part of the original central derivative and the algebraic part of the raised-level central value, subject to its hypotheses and normalizations. The signs impose parity of vanishing orders, not exact orders; the mod-prime congruence does not change that.

## Independence from BSD and restricted examples

The proof of Proposition 5.4 is a comparison of residual Selmer structures and local conditions. It does not invoke the BSD conjecture, infer equality between Mordell–Weil rank and analytic rank, or remove a Tate–Shafarevich contribution. So the narrow local-Selmer lemma is independent of BSD. This must not be conflated with later applications in Zhang's paper: later sections combine level raising and Selmer control with other inputs, including a (p)-adic BSD formula under their hypotheses, to prove specific results such as a rank-one converse. Those extra conclusions do not turn Proposition 5.4 into an unconditional general-rank theorem.

The paper's rank-one setting is a restricted positive result, not a counterexample or general induction example. It uses a suitable imaginary quadratic field, residual and local hypotheses, and an admissible prime selected so the relevant class localizes nontrivially; Lemma 7.3 supplies such primes in its setting. Its conclusion concerns a specially controlled Selmer group and the associated Heegner/Euler-system argument. No concrete elliptic-curve example in the note demonstrates an arbitrary-rank analytic drop, and none is needed to identify the logical gap.

## Corrections and qualifications to `congruence.md`

- Keep the explicit disclaimer that \(q\nmid NpD_K\) alone does **not** make (q\) admissible. State the paper's admissibility definition or refer readers directly to its setup; the additional Frobenius/eigenvalue and local conditions matter.
- Present Proposition 5.4's hypotheses as inherited from the paper's setup, not as if the localization condition alone sufficed for an arbitrary newform and quadratic field. The present note mostly does this, but its shorthand “under the local hypotheses ensuring the old and new Selmer structures agree” is less precise than the proposition's fixed global setup.
- Preserve the distinction between \(\operatorname{Sel}_{p_0}(A/K)\) (the relaxed source in the kernel equality), \(\operatorname{Sel}_p(A/K)\) (the dimension on the right), and \(\operatorname{Sel}_{p'}(A'/K)\) (the new strict group). The dimension statement is well-defined over the corresponding residue fields as in Zhang; avoid writing one field as if both dimensions naturally shared it.
- Say that a nonzero algebraic central value modulo the maximal ideal implies the corresponding complex central value is nonzero only after the paper's algebraic normalization and coefficient-module setup. This consequence is valid here, but does not imply an exact-order comparison for a general pair of forms.
- The proposed missing lemma must be stated for every (E/\mathbb Q) and every analytic rank (r>0), with explicit existence of a congruent raised-level form satisfying \(r_{\rm an}(g')=r-1\) (or a sufficient inequality) **and** a justified transport yielding \(\operatorname{rank}E(\mathbb Q)\ge r\). Neither cited theorem supplies either universal clause.

## Conclusion

No cited theorem proves the proposed level-congruence induction for arbitrary (E/\mathbb Q\). The conditional residual Selmer drop is valid with Zhang's full hypotheses and a nonzero localization, and is independent of BSD at the proposition level. The Jochnowitz congruences have the claimed derivative-versus-value scope, but they do not control complex order in general. The exact outstanding input remains a universal analytic-order control theorem together with a cross-level arithmetic transport theorem; absent these, this route does not prove either general weak-BSD inequality.

## Primary references

- W. Zhang, [*Selmer groups and the indivisibility of Heegner points*](https://math.mit.edu/~wz2113/math/online/Kconj.pdf), Theorem 2.1, Lemma 4.2, Lemma 5.3, Proposition 5.4, Theorem 1.3, and §§7–9.
- M. Bertolini and H. Darmon, [*Euler systems and Jochnowitz congruences*](https://citeseerx.ist.psu.edu/document?doi=07eec1de1af336a841d26e905494b6f7f17278a4&repid=rep1&type=pdf), Theorem 1.3 and Proposition 1.5.
- S. Vigni, [*Heegner points and Jochnowitz congruences on Shimura curves*](https://arxiv.org/abs/1204.0496), Theorem 1.1 and abstract.
