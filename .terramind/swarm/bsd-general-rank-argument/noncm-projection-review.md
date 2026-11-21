# Independent review: projected class conditions

## Verdict

The proposed projection argument is sound in its main conclusion: Castella's non-CM construction gives a well-defined generalized Kato class in the elliptic-curve representation, but the theorem does not establish that this class is nonzero in the finite/strict Selmer space. Its explicit reciprocity law controls the ordinary local quotient, and the rank-two criterion leaves a separate local-nonvanishing condition. The classical Beilinson–Flach/Eisenstein specialization is a different construction and does not repair that gap.

I checked the statements below against Castella, *Nonvanishing of generalised Kato classes and Iwasawa main conjectures*, arXiv:2312.01481, especially §§3.2–3.3, 4.1, and 5.1–5.4, and Bertolini–Darmon–Venerucci, *Heegner points and Beilinson–Kato elements*, especially Theorem 4.2 and §5.1.

## Projection and coefficients

Castella §5.1 starts with the big diagonal class \(\kappa(f,gg^*)\). Under the direct-sum decomposition (5.1), it projects to the first summand
\[
H^1(K,T_f\otimes\Psi_T^{1-c})\longrightarrow H^1(K,T_f),
\]
where the second arrow is induced by multiplication by the augmentation parameter \(T\). The image is then identified with \(H^1(K,T_pE)\) at the weight-two specialization. This is the generalized Kato class \(\kappa_p(E)\), in the adjoint case; it is not the two-factor Beilinson–Flach class. The note correctly distinguishes the construction from the later class comparison using an Eisenstein specialization.

The decomposition used here requires the auxiliary CM theta families and the residual local condition \(\bar\chi|_{G_{K_p}}\ne 1\), where \(\chi=\psi/\psi^c\) (Castella (3.2)). For the rank-two application, Choice 5.2.1 additionally requires the actual character condition \(\chi|_{G_{K_p}}\ne1\), along with the stated splitting, inertness, ordinary-prime, and nonvanishing conditions. These are distinct levels of hypotheses; the review note should keep the residual condition for the decomposition separate from the stronger choice condition in the application.

## Local condition and specialization

Castella's Theorem 4.1.1 interpolates the regulator as a logarithm at weights \(k\ge3\), and as a nonzero scalar times the Bloch–Kato dual exponential at weight two. Proposition 5.1.2 then proves that \(L(f/K,1)=0\) puts the specialized class in the Selmer group over \(K\); Corollary 5.1.3 descends it to \(\mathbf Q\) if also \(L(E_K,1)\ne0\), using Kato's vanishing for the twist. Remark 5.1.4 says the class is strict at \(p\) in this setting. Thus vanishing of the singular/ordinary-quotient image establishes the needed local condition, but cannot establish nonzero localization in the finite subspace. A nonzero image under the dual exponential would instead be a nonzero singular quotient and would conflict with that finite local condition.

This separates the two relevant claims accurately: membership in the finite Selmer group and nonvanishing of the class within it. Central vanishing gives the first (with the twist hypothesis for descent), not the second.

## Rank-two criterion and scope

Theorem 5.2.3 assumes positive even analytic rank and is stated after the residual hypotheses (h1)–(h3) and Choice 5.2.1. It proves \(\kappa_p(E)\ne0\Rightarrow \dim_{\mathbf Q_p}\mathrm{Sel}(\mathbf Q,V_pE)=2\). If that Selmer space has dimension two, then \(\kappa_p(E)\ne0\) if and only if the localization map on that Selmer space is nonzero; in that case the class spans its strict kernel. The theorem does not prove the local map is nonzero. Nor is its statement an unconditional result for every elliptic curve and prime: the residual and auxiliary hypotheses remain part of this application.

The existing `noncm-projection.md` contains a material transcription error in its list of these residual hypotheses. Castella's (h2) is: there is a prime \(q\parallel N_f\) (so \(q\) divides the conductor exactly once), and if \(q\equiv\pm1\pmod p\), then \(\bar\rho_f\) is ramified at \(q\). It is not a prime \(q\nmid N_f\). Castella's (h3) is: either \(p>5\) or the image of \(\bar\rho_f\) contains a conjugate of \(\mathrm{SL}_2(\mathbf F_p)\); it is not \(\mathrm{GL}_2(\mathbf F_p)\). The source also has a typographical “of” where the logical connective is “or”; the intended formulation is clear from the theorem's use. The auxiliary Choice 5.2.1 then takes this same \(q\), requires it inert in \(K\), and requires every prime factor of \(N_f/q\) split in \(K\). Any downstream use of the malformed hypotheses should be corrected to this version.

The source describes existence of suitable \((K,\chi)\) choices under these conditions: the nonvanishing of \(L(E_K,1)\) is obtained for infinitely many eligible \(K\), and for each such \(K\), \(L(E/K,\chi,1)\ne0\) holds for all but finitely many ring-class characters in the specified family. This does not remove the residual hypotheses or prove universal availability for every \((E,p)\).

## Beilinson–Flach/Eisenstein route

BDV Theorem 4.2 compares a Beilinson–Flach class with the Beilinson–Kato system attached to a family through the weight-one Eisenstein series \(\mathrm{Eis}_1(\varepsilon_K)\), whose Galois representation is \(1\oplus\varepsilon_K\). Its §5.1 specializes the comparison. This supports the review note's identification of a separate route and its warning that the class and reciprocity law differ from Castella's diagonal-cycle generalized Kato class. The specialization identity only identifies a projected Kato class up to the displayed nonzero factors when the corresponding twist value is nonzero; it cannot manufacture nonvanishing when that factor vanishes. At a central zero, the Kato reciprocity law's vanishing of the singular image is compatible with Selmer membership and supplies no nonzero finite localization.

## Corrections and remaining obstruction

The substantive correction required in the source note is the pair of residual-hypothesis fixes above: \(q\parallel N_f\), not \(q\nmid N_f\), and \(\mathrm{SL}_2\), not \(\mathrm{GL}_2\). The rank-two implication and local-condition discussion otherwise agree with the cited primary sources, subject to retaining the hypotheses and distinguishing \(\bar\chi|_{G_{K_p}}\ne1\) from \(\chi|_{G_{K_p}}\ne1\).

The remaining gap is precise: an unconditional all-curves weak-BSD argument by this route would need a theorem establishing, for every required \((E,p)\), nonzero localization of the relevant Selmer space (or directly nonvanishing of the correctly specialized class in its finite/strict Selmer space), while removing or proving availability of the residual and auxiliary hypotheses. Neither the reciprocity law nor Theorem 5.2.3 supplies this input. No example can replace that universal assertion.
