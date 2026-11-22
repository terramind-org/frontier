# Independent check: coprime splitting of coverings

## Verdict

The restriction-corestriction criterion is correct when stated for the image \(\alpha_n\in H^1(\mathbf Q,E)[p^n]\) of the finite Selmer class. For \([K:\mathbf Q]=d\) prime to (p), a (K)-point on the covering makes \(\operatorname{res}\alpha_n=0\); corestriction gives (d\alpha_n=0\), hence \(\alpha_n=0\), which is equivalent to a rational point on the same torsor. It does not imply \(x_n=0\) in (H^1(\mathbf Q,E[p^n])\): if the torsor is trivial, \(x_n\) is a Kummer class, generally nonzero.

For a (K)-point whose image on the base is (P\in E(K)), the Kummer functoriality identity gives
\[
 d x_n=\delta_{\mathbf Q}(\operatorname{Tr}_{K/\mathbf Q}P).
\]
Because (d\) is a unit modulo (p^n), this yields the exact required rational coset \([Q_n]=d^{-1}[\operatorname{Tr}P]\in E(\mathbf Q)/p^nE(\mathbf Q)\). Therefore a raw trace equal to the desired class is not the right condition unless normalized by (d^{-1}\).

The Heegner discussion is appropriately limited: ring-class Euler-system norm relations and Kolyvagin derivative classes control the classes constructed from those points, but no cited relation identifies a general prescribed transverse (x_n\) with their Kummer class or supplies strict localization for it. Degree coprime to (p) is automatic for a quadratic field at odd (p); it does not make an (E(K))-point a point on the given covering. Thus this criterion is equivalent to existing rational solubility and offers no independent source without the stated realization lemma.

## Scope caveat

The note uses the standard convention that an (E[p^n])-covering associated with (x_n=\delta(P)) is the fiber of multiplication by (p^n) over (P\). Under the alternate torsor action convention the point/class identification can carry a sign; the exact Kummer equality must be fixed consistently. This does not affect the restriction-corestriction conclusion or the degree-normalized trace coset.

## Source check

Howard's [Heegner point Kolyvagin system](https://arxiv.org/abs/1202.6340) gives the ring-class Heegner point norm relation and Kolyvagin-system construction. Castella–Hsieh [arXiv:1809.09066](https://arxiv.org/abs/1809.09066) does not provide the missing finite-level Kummer-coset match for a general transverse class; its rational Kummer placement is conditional as recorded in the adjacent notes. No overclaim of a general impossibility theorem is made: a specially constructed class could conceivably satisfy the missing equality.
