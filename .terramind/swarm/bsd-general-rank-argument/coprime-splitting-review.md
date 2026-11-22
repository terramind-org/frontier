# Independent review: coprime splitting of coverings

## Verdict

The restriction–corestriction criterion is correct for the **underlying (E)-torsor** of the finite (p^n)-covering. If (x_n\in H^1(\mathbf Q,E[p^n])) is the Selmer lift and \(\alpha_n\in H^1(\mathbf Q,E)\) its image, then a (K)-point on the covering implies \(\operatorname{res}_{K/\mathbf Q}(\alpha_n)=0\). Corestriction gives \([K:\mathbf Q]\alpha_n=0\). Since \(\alpha_n\) is killed by (p^n), a degree prime to (p) forces \(\alpha_n=0\). The converse is the torsor criterion for a rational point. Equivalently, exactness of the Kummer sequence says

\[
\alpha_n=0\quad\Longleftrightarrow\quad
x_n=\delta_{\mathbf Q}(Q)\text{ for some }Q\in E(\mathbf Q).
\]

This does **not** say (x_n=0) in finite cohomology. The Kummer class of a rational point is generally nonzero. Stoll’s account gives the exact Selmer sequence and interprets Selmer elements as locally soluble coverings [Stoll, §§1–2](https://arxiv.org/abs/math/0611694).

For a (K)-point of the covering mapping to (P\in E(K)), with the convention that the covering is the fiber of \([p^n]\) above its base point, its restricted finite class is \(\delta_K(P)\). Kummer maps commute with corestriction/norm, so

\[
 [K:\mathbf Q]x_n
 =\operatorname{cor}(\delta_K(P))
 =\delta_{\mathbf Q}(\operatorname{Tr}_{K/\mathbf Q}P).
\]

Thus the rational Kummer coset is the **degree-normalized** trace, with the degree inverted modulo (p^n). A sign can change if the torsor action or covering convention is reversed; fixing the Kummer convention resolves it. The note correctly distinguishes the finite Selmer lift from its image in (H^1(\mathbf Q,E)), and correctly warns that a point on (E(K)) alone is not a point on the specified covering.

## Heegner trace and citation audit

The quadratic-field degree argument is valid for odd (p), since ([K:\mathbf Q]=2). Given an actual point of the specified covering over (K), the criterion forces rational solubility. But the existence of an ordinary Heegner point (P\in E(K)) does not provide that covering point: one must verify \(\delta_K(P)=\operatorname{res}(x_n)\). The trace coset is a genuine rationality certificate only if its finite Kummer class is exactly (x_n); nonvanishing or norm compatibility by itself is insufficient.

Howard is an appropriate source for the limited claim that Heegner points over ring class fields satisfy Euler-system norm relations and produce Kolyvagin-system classes. The specific formula in Howard §1.7 is \(\operatorname{Norm}_{K[n\ell]/K[n]}P[n\ell]=a_\ell P[n]\), under the paper’s setup (n\ell\in\mathcal N) (its admissible auxiliary primes are inert in (K) and satisfy the imposed residual conditions); it is not an unrestricted formula for arbitrary conductor changes [Howard, §1.7, especially pp. 19–20](https://arxiv.org/abs/1202.6340). The reviewed note qualifies its example with “usual good-prime hypotheses,” but naming the inert/admissibility scope avoids suggesting a universal relation. Nothing in that relation identifies an arbitrary prescribed transverse (x_n) with a Heegner Kummer class.

The Castella–Hsieh citation is correctly presented as a generalized-Kato source, not as an identity for this prescribed finite-level Kummer coset. Its abstract itself describes nonvanishing consequences for the (p)-adic Selmer group, not the needed covering-point equality [Castella–Hsieh](https://arxiv.org/abs/1809.09066). The Stoll, Howard and Castella–Hsieh references exist and match the cited subject matter. The functoriality identity used above is standard functoriality of the Kummer exact sequence; the note appropriately identifies it as a direct derivation rather than attributing the displayed degree-normalized criterion to one of these papers.

## Does rational rank follow?

Only conditionally. If (x_n\notin L_n), where (L_n) is the Kummer image of the torsion-aware saturated known rational line, and the specified covering has a rational point, Kummer exactness gives a rational point whose class is outside that line. Under the hypotheses and definition of (L_n) in `transverse-coset.md`, this certifies \(\operatorname{rank}E(\mathbf Q)\ge 2\). The known-line exclusion alone does not prove the covering has a rational point; it can instead represent a nonzero Sha class.

Consequently the coprime-splitting result does not itself derive rank, nor does it give a new route to weak BSD. It restates rational solubility for the same torsor. The actual missing input is an unconditional construction of a point on at least one specified transverse covering over a degree-prime-to-(p) field (or a proof that its torsor class vanishes). For the proposed Heegner construction this requires the exact restricted Kummer equality, along with the stated local conditions. No cited norm relation, twist nonvanishing, or generalized-Kato result supplies that equality in general.

## Scope caveat

An (E[p^n])-covering has class in (H^1(\mathbf Q,E[p^n])); its underlying genus-one (E)-torsor is the image in (H^1(\mathbf Q,E)). Keeping these objects distinct is essential. The argument proves splitting of the torsor, not triviality of the finite lift. Trace compatibility then pins down the rational Kummer coset only when there is an actual point on that covering over the extension.
