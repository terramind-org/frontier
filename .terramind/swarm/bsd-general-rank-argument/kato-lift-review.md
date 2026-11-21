# Independent audit: generalized Kato class and the Kummer lift

I checked the claim against the published Castella–Hsieh paper, *On the non-vanishing of generalized Kato classes for elliptic curves of rank 2*, Forum of Mathematics, Sigma 9 (2021), and its authors’ [published PDF](https://web.math.ucsb.edu/~castella/Kato.pdf). This is the version with Theorem A, Theorem B, Theorem 5.5 and Remark 5.6; the arXiv v4 manuscript has different numbering and a differently formulated main theorem. References below use the published version.

## Findings

**The Kato class under discussion is a projection.** The four classes are first constructed in $H^1(\mathbf Q,V_{fgg^*})$. The representation splits as $V_pE\oplus(V_pE\otimes\operatorname{ad}^0V_p(g))$, so the class denoted \(\kappa_{\alpha,\alpha^{-1}}(f,g,g^*)\) in Theorem A is its image in $H^1(\mathbf Q,V_pE)$, not the entire triple-product class. The paper places these classes in the corresponding Bloch–Kato Selmer groups when $L(E,1)=0$; its CM factorization and auxiliary nonvanishing hypotheses isolate the $V_pE$ summand for the statements at issue. The note’s use of the projected class is therefore appropriate.

**Theorem A is not an analytic-rank-two theorem.** In the published version it assumes good ordinary reduction at $p>3$, root number $+1$, $L(E,1)=0$, nonvanishing of $L(E^K,1)L(E/K,\chi,1)$, irreducibility of $E[p]$, and that $N_f^-$ is the squarefree product of an odd number of primes, with $E[p]$ ramified at every prime dividing $N_f^-$. This is the exact condition stated in Theorem A (p. 4); the summary in `kato-lift.md` now includes it. Under these hypotheses the mixed-root classes vanish. The theorem states
\[
\kappa_{\alpha,\alpha^{-1}}\ne0\Rightarrow
\dim_{\mathbf Q_p}\operatorname{Sel}(\mathbf Q,V_pE)=2,
\]
and the converse when additionally \(\operatorname{Sel}(\mathbf Q,V_pE)\ne\ker(\operatorname{Loc}_p)\). Here \(\operatorname{Loc}_p\) is restriction to \(H^1(\mathbf Q_p,V_pE)\). The paper’s Remark 1.5 explains that equality with the kernel would force $E(\mathbf Q)$ finite; if the Selmer group were then nonzero, the (p\)-primary Sha would be infinite. None of these statements identifies the Selmer space with the rational-point tensor unconditionally.

The earlier note omitted the published theorem’s “odd number of primes” condition on $N_f^-$. The summary has now been corrected to require the squarefree product of an odd number of primes. Also, the odd root number of the inert-prime factor $N_f^-$ is part of the specified CM setting, not an optional consequence of squarefreeness.

**The exact sequence leaves the requested lift open.** The paper gives
\[
0\to E(\mathbf Q)\otimes\mathbf Q_p\to\operatorname{Sel}(\mathbf Q,V_pE)
\to T_p\Sha(E/\mathbf Q)\otimes\mathbf Q_p\to0.
\]
Thus the Kato class has a Mordell–Weil representative precisely if its image in the final quotient is zero. A Bloch–Kato local condition is a condition on localization at each place and defines this full Selmer group; it does not identify the Kummer subspace with a kernel of localization. In particular, the nonzero formal logarithm used by Theorem A’s converse is a nonzero local image criterion for nonvanishing, not a proof that the global class lies in the Kummer image.

**Theorem 5.5 is conditional on finite $p$-primary Sha.** The hypothesis appears immediately before the strong elliptic Stark discussion in §5.7: \(\#\Sha(E/\mathbf Q)[p^\infty]<\infty\). Under it, the Kummer quotient above vanishes, so the identification \(\operatorname{Sel}(\mathbf Q,V_pE)\simeq E(\mathbf Q)\otimes\mathbf Q_p\) and the formula in Theorem 5.5 are legitimate. This theorem does not prove the finiteness hypothesis. The earlier one-dimensional line relation in Remark 1.6 is instead unconditional under Theorem A’s hypotheses: the two diagonal classes are scalar multiples, and their line is \(\ker(\log_p)\) in the two-dimensional Selmer group. Remark 1.6 only interprets that line using \(\operatorname{Log}_p(P\wedge Q)\) when the Sha finiteness condition holds.

**Cassels–Tate does not eliminate this quotient.** The Cassels–Tate pairing on Sha has the maximal divisible subgroup in its radical; its nondegeneracy statement is after quotienting by that subgroup. The inverse-limit $T_p\Sha\otimes\mathbf Q_p$ is exactly the part not detected by a finite-level pairing on the reduced Sha group. Orthogonality against finite classes therefore supplies no proof that this Kato class has zero image in the quotient. This is consistent with the exact sequence and does not contradict the existence of a nonzero Selmer class.

**There is an abstract second Selmer direction, but not a second rational direction.** If the diagonal class is nonzero, Theorem A gives Selmer dimension two, so elementary linear algebra supplies a vector independent of it. The theorem does not identify that complementary vector as another Euler-system class. The other two root classes are zero, and the two diagonal classes lie on the same line (Remark 1.6); hence the four choices do not produce two independent classes. Without vanishing of the Kummer quotient, neither the named Kato line nor an abstract complement certifies a second independent rational point. If $p$-primary Sha is finite, both directions are in the Kummer image and the resulting rank-two conclusion is conditional on that finiteness.

## Audit conclusion

The main gap identified in `kato-lift.md` is real: the nonzero generalized Kato class and the two-dimensional Selmer conclusion do not, without an additional argument, prove that the class maps to zero in $T_p\Sha\otimes\mathbf Q_p$, and they do not yield two independent rational points. The sufficient hypothesis used for the Mordell–Weil identification in Theorem 5.5 is finiteness of \(\Sha[p^\infty]\), not a consequence of the class construction. The independent second vector is only an abstract Selmer-space consequence. Correct the stated Theorem A hypothesis by adding the odd-prime-factor condition on $N_f^-$.

## Primary-source pointers

- [Published authors’ PDF](https://web.math.ucsb.edu/~castella/Kato.pdf): §1.2 Theorem A and Remark 1.5 (hypotheses, localization converse); Remark 1.6 (same diagonal line); §5.1 (class projection / Selmer placement); §5.5 (dimension implication); §5.7 and Theorem 5.5 (finite-$p$-Sha hypothesis and conditional Kummer formula).
- [Cambridge journal page](https://www.cambridge.org/core/journals/forum-of-mathematics-sigma/article/on-the-nonvanishing-of-generalised-kato-classes-for-elliptic-curves-of-rank-2/72ED842AB428A7ED619B1B84287A6864).
