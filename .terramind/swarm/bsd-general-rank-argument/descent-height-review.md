# Independent audit of the descent-height inference

## Verdict

The Northcott extraction in `descent-height.md` is valid conditional on having rational points in compatible Kummer cosets with a uniform height bound on their images in (E(mathbb Q)). The proposed inference from a nonzero strict Selmer class to such points is not valid. It has two separate obstructions: passage from a rational (p)-adic cohomology class to integral classical Selmer levels requires an integral local-condition argument, and a nonzero strict class cannot be the localization/Kummer class of an individual non-torsion rational point when the strict condition is the kernel of the local logarithm. The argument may concern a nontrivial (p)-adic Mordell–Weil combination, but that is not an individual rational point and yields no rational representatives with bounded height.

## From a strict (V_pE) class to an integral tower

Put (T=T_pE), (V=Totimes_{mathbb Z_p}mathbb Q_p), and let (xin H^1(mathbb Q,V)) be a class in the rational strict Selmer space. A continuous cocycle representing (x) has compact image in (V), hence bounded denominators relative to (T). For some (ageq0), multiplication by (p^a) makes that cocycle (T)-valued and defines (cin H^1(mathbb Q,T)). This is the basic denominator-clearing step; it gives an integral cohomology class, not yet a class in every classical finite-level Selmer group. Also (c) maps to (p^a x), not to (x) with its original normalization.

The coefficient exact sequence
\[
0\to T\xrightarrow{p^n}T\to E[p^n]\to0
\]
gives a coefficient-reduction map (H^1(\mathbb Q,T)\to H^1(\mathbb Q,E[p^n])). Reductions of the cocycle for (c) are compatible under the downward transition (E[p^m]\xrightarrow{p^{m-n}}E[p^n]), and therefore define a class in the inverse limit of (H^1(\mathbb Q,E[p^n])). This map need not be surjective: its image is contained in the kernel of the map (H^1(\mathbb Q,E[p^n])\to H^2(\mathbb Q,T)) from the coefficient exact sequence. Conversely, the map (H^1(\mathbb Q,E[p^n])\to H^1(\mathbb Q,T)[p^n]) has kernel equal to the image of the connecting map from (H^0(\mathbb Q,E[p^n])) (equivalently, that invariant group modulo the image of (H^0(\mathbb Q,T))). Thus finite-level torsion and divisibility must be tracked; one cannot silently identify every finite-level class with a reduction of an integral Tate-module class, or discard rational (p)-power torsion.

For the reductions to land in the *classical* \,\(\operatorname{Sel}_{p^n}(E/\mathbb Q)\), one needs the integral local conditions. At (v\nmid p\), the usual finite condition is the unramified condition (with the standard treatment at bad primes); at (p), the finite condition is the integral Kummer image. A rational Bloch–Kato finite condition says only that the localization of (x) lies in (H_f^1(\mathbb Q_v,V)). To pass from this rational condition to the integral Kummer subgroup in (H^1(\mathbb Q_v,T)), one must prove the relevant lattice comparison and account for its torsion/finite-index cokernel. If that cokernel is finite, multiplying by a further (p^b) kills it, giving (p^{a+b}x) an integral classical tower. This factor must be justified for the specified strict structure; it is not supplied merely by saying “clear denominators.”

The required comparison is particularly delicate at the distinguished prime: if “strict” means the kernel of the formal logarithm on the finite local condition, it is a subspace of the rational finite local condition, so it is compatible with classical local conditions after the integral lattice comparison. If instead it is defined as a kernel inside a different Selmer structure or of a map on a quotient, the inclusion must be checked from that definition. At bad primes the local conditions likewise need to be compared explicitly. Scaling preserves a linear rational local condition, but it does not by itself prove that an arbitrary chosen integral cocycle satisfies an integral local condition.

Once this is established, the reduction classes (c_n\in H^1(\mathbb Q,E[p^n])) satisfy the classical local Kummer conditions and form a compatible tower. Their images in the rational cohomology system represent (p^{a+b}x); the finite-level class can still include a Kummer term from rational torsion, and the inverse limit has the Mordell–Weil completion together with the (T_p\Sha) quotient. This construction does not produce a point on any covering. It constructs cohomology classes satisfying local solubility conditions only.

## Individual rational points versus strict classes

In the argument used in the preceding localization notes, the strict condition at (p) is the kernel of
\[
\mathrm{loc}_p:\operatorname{Sel}(\mathbb Q,V)\longrightarrow H_f^1(\mathbb Q_p,V)
\xrightarrow{\log_E} \mathbb Q_p,
\]
with the finite local condition identified with the local point/logarithm space under the stated good-ordinary hypotheses. For (Q\in E(\mathbb Q)), its global Kummer class localizes to the local Kummer class of (Q), and its logarithm is the (p)-adic elliptic logarithm of (Q) (up to the fixed nonzero normalization).

The kernel of the elliptic logarithm on (E(\mathbb Q_p)) is torsion. Thus if (Q) is non-torsion in (E(\mathbb Q)), it remains non-torsion as a point of (E(\mathbb Q_p)), its local logarithm is nonzero, and its Kummer class is not strict. If (Q) is rational torsion, its class in (H^1(\mathbb Q,V)) is zero after tensoring with \(\mathbb Q_p\); its finite-level integral Kummer classes may be nonzero, but they cannot represent a nonzero rational strict vector. Consequently, subject to the stated identification of the strict map with localization/logarithm, **no nonzero strict rational class can equal the (V)-Kummer image of an individual rational point**.

This does not rule out a (p)-adic Mordell–Weil combination. If (P_1,\ldots,P_r) are independent rational points, their completed Kummer classes allow coefficients (a_i\in\mathbb Z_p), and the local logarithm is the linear form
\[
(a_1,\ldots,a_r)\longmapsto \sum_i a_i\log_E(P_i).
\]
When (r>1), its kernel can contain nonzero coefficient vectors even though each non-torsion individual point has nonzero logarithm. Such a vector is a point of the (p)-adic completion (E(\mathbb Q)\otimes\mathbb Z_p), not generally a point of (E(\mathbb Q)). Its finite-level representatives can be integer combinations whose coefficients grow with (n); they do not meet the Northcott hypothesis just because the (p)-adic coefficients are bounded.

## Primitive (p)-adic example and Northcott

Take a non-torsion (P\in E(\mathbb Q)), and choose the primitive unit
\[
a=1+\sum_{j\ge2}p^{j!}\in\mathbb Z_p^\times.
\]
Its base-(p) expansion has infinitely many nonzero digits, so (a\notin\mathbb Z). The inverse-limit Kummer class (a\,\delta(P)) is nonzero. At level (n), it is represented in the Mordell–Weil quotient by (k_nP), where (k_n\) is any integer congruent to (a\pmod {p^n}). No choice of such integers stays bounded in ordinary absolute value along an unbounded sequence of levels: a bounded subsequence would repeat one integer infinitely often, forcing (a) to equal that integer in \(\mathbb Z_p\). Since
\[
\hat h(k_nP)=k_n^2\hat h(P),
\]
these standard rational representatives have unbounded height. More generally, if any representatives of this compatible class had bounded height along unbounded levels, Northcott would give a single repeated rational point (Q); compatibility would force (a\delta(P)=\delta(Q)) in the completed Kummer group, which is impossible because the free rank-one coordinate of a rational point is an integer. This example is primitive (a unit), rather than a nonprimitive scalar such as (p a\), and makes explicit that (p)-adic boundedness is not a height bound.

The individual-point obstruction and the example fit together: a strict vector can be a (p)-adic combination in a logarithmic kernel, but cannot itself be an individual non-torsion rational point. Northcott can only extract a point if rational representatives already exist at arbitrarily high levels and have uniformly bounded image heights. Indeed, in the logarithmic-kernel setting the extracted point would have to be torsion, whose rational (V)-Kummer class is zero, contradicting nonzero strictness.

## Precise status of the inference

The PR 213 inference fails before Northcott unless it supplies both (i) the integral comparison needed to map the specified strict rational Selmer space, after a fixed denominator scaling, into the classical inverse system and (ii) rational points on the associated torsors at unbounded levels with a depth-independent height bound on their images in (E(\mathbb Q)). Even granting (i), (ii) does not follow: the classes certify local solubility, not global solubility, and the strict/logarithmic condition rules out the proposed individual non-torsion point as representative. A p-adic Mordell–Weil combination does not fix this, since its rational approximants need not have bounded height and Northcott would extract an individual point, not a new p-adic combination.

The exact missing implication is therefore not simply “bounded-height representatives imply a point” (that conditional statement is sound). It is a theorem producing globally rational points on the relevant compatible coverings, with the prescribed Kummer cosets, integral local conditions, and a uniform bound on their image heights; moreover, for a nonzero strict class defined as the localization/logarithm kernel, it would need to explain how the resulting individual point can avoid the local logarithm obstruction. No such theorem is established by the descent-height argument. The claimed route does not prove the desired second rational direction.
