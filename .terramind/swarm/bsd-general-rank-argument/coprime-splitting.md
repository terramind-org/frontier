# Coprime splitting of a transverse covering

## Conclusion

Let (x_n\in\operatorname{Sel}_{p^n}(E/\mathbf Q)) and let
\[
 \alpha_n=\iota(x_n)\in H^1(\mathbf Q,E)[p^n]
\]
be its image under the map induced by (E[p^n]\hookrightarrow E(\overline{\mathbf Q})\). The associated genus-one covering (C_n) is a torsor under (E) with class \(\alpha_n\). For every finite extension (K/\mathbf Q) of degree (d) prime to (p),
\[
 C_n(K)\ne\varnothing\quad\Longleftrightarrow\quad \alpha_n=0
 \quad\Longleftrightarrow\quad C_n(\mathbf Q)\ne\varnothing.
\]
The forward implication is restriction-corestriction: a (K)-point trivializes the torsor over (K), so \(0=\operatorname{cor}_{K/\mathbf Q}\operatorname{res}_{K/\mathbf Q}(\alpha_n)=d\alpha_n\); multiplication by (d) is invertible on a (p)-primary group. The reverse implication is immediate. This statement concerns the **underlying (E)-torsor class**, not the finite Selmer lift (x_n\in H^1(\mathbf Q,E[p^n])).

If \(\alpha_n=0\), exactness of the Kummer sequence says (x_n=\delta_{\mathbf Q}(Q_n)) for a rational point (Q_n\in E(\mathbf Q)), unique only as a coset in (E(\mathbf Q)/p^nE(\mathbf Q)). Therefore coprime splitting is equivalent to the existing rationality criterion for this fixed covering. It is not an independent route to rationality or an additional rank argument. Transversality (for example, (x_n\notin L_n), the known-line Kummer subgroup) is compatible with either value of \(\alpha_n\); if the class is transverse and the covering has a point, then the resulting (Q_n) is outside that known line and certifies rank at least two, as in `transverse-coset.md`.

## Exact Kummer coset after a point over (K)

Let \(P\in E(K)\) be the image in (E(K)\) of a point of the covering (C_n(K)\). The torsor trivialization given by this point identifies the finite covering with the (p^n)-Kummer fiber over (P): with the convention that (C_n\) parametrizes (R\) satisfying \([p^n]R=P\), the class (x_n|_K\) is \(\delta_K(P)\). For the opposite torsor/action convention a sign may occur; fix the convention by the Kummer exact sequence. Crucially, the requirement is equality of the **restricted class** and this Kummer class, not just that (P\) is a Heegner point or has some nonzero trace.

Taking corestriction and using compatibility of Kummer maps with field trace gives
\[
 d x_n=\operatorname{cor}(x_n|_K)
 =\operatorname{cor}(\delta_K(P))
 =\delta_{\mathbf Q}(\operatorname{Tr}_{K/\mathbf Q}P)
 \quad\text{in }H^1(\mathbf Q,E[p^n]).
\]
Thus the required rational Kummer coset is
\[
 [Q_n]=d^{-1}[\operatorname{Tr}_{K/\mathbf Q}P]
 \quad\text{in }E(\mathbf Q)/p^nE(\mathbf Q),
 \qquad \delta_{\mathbf Q}(Q_n)=x_n.
\]
Here (d^{-1}) is any integer inverse to (d\bmod p^n); the coset is independent of the chosen inverse. This is not the assertion that the unscaled trace itself has Kummer class (x_n). More generally, for a proposed rational point (Q\), the exact test is
\[
 Q\in E(\mathbf Q),\qquad [Q]\in E(\mathbf Q)/p^nE(\mathbf Q),\qquad \delta_{\mathbf Q}(Q)=x_n.
\]
The point must occupy precisely this coset; a point in another coset does not split (C_n\).

For an auxiliary field (F\) containing (K), a point (P_F\in E(F)) can be used only after forming its appropriate trace to (K), then the above trace to (\mathbf Q), with the total degree factor inverted modulo (p^n). If \([F:\mathbf Q]\) is divisible by (p), restriction-corestriction does not force the torsor class to vanish; a trace point alone does not repair this. One can still use any actual (K)-point when (K/\mathbf Q) itself has degree prime to (p).

## Concrete Heegner trace test

Fix an imaginary quadratic field K satisfying the Heegner hypothesis for the modular parametrization of E, with p odd. Let H_c/K be a ring class field and y_c in E(H_c) a Heegner point after applying that parametrization. The point normally used at quadratic-field level is a trace P_c=Tr_{H_c/K}(y_c) in E(K); any normalization factor used in a source must be retained. The sole candidate rational coset furnished by this point is

\[
 q_c=2^{-1}[\operatorname{Tr}_{K/\mathbf Q}P_c]
      =2^{-1}[\operatorname{Tr}_{H_c/\mathbf Q}y_c]
       \in E(\mathbf Q)/p^nE(\mathbf Q),
\]

where 2^{-1} is modulo p^n. This is a test, not a reciprocity theorem. There are two distinct assertions:

* The Heegner trace itself gives a point on the covering over K exactly when \(\delta_K(P_c)=\operatorname{res}_{K/\mathbf Q}(x_n)\). This is the actual covering-point test.
* Its normalized rational trace coset gives a rational point on the covering exactly when \(\delta_{\mathbf Q}(q_c)=x_n\).

The first equality implies the second by corestriction and cor∘res=2 on H^1(Q,E[p^n]). The converse does not follow: corestriction can have a kernel, so equality of the rational trace coset alone need not put P_c on C_n over K. It does, however, prove rational solubility via the rational point represented by q_c. Both tests are equalities in the finite Kummer quotient, not equality of points, nonvanishing of P_c, or equality only after tensoring with Q_p. A point on E(K) is not by that fact a point on C_n.

If y_c is supplied only over H_c, whose degree over Q can have a p-part, H_c-rationality of a point on the covering does not imply rational solubility. One must form an actual K-rational trace point and check the displayed equality. The Heegner norm relation determines how P_c at different conductors relate, but does not force any of their Kummer classes to equal prescribed x_n.

For a strict condition at a rational place v, equality also requires δ_{Q_v}(q_c)=loc_v(x_n)=0. By exactness of the local Kummer sequence this means q_c lies in p^n E(Q_v), not merely that a Heegner point has a favorable sign or is norm-compatible. If strictness is imposed after a specified twist or local identification, transport through that same identification before testing zero. Twist nonvanishing hypotheses used to eliminate complementary Selmer summands establish Selmer membership of the constructed class under those hypotheses; they do not assert this finite-level equality or local divisibility for q_c.

If the source is a Heegner point on a quadratic twist E^D, its K-isomorphism with E transports the point to E(K), but the Galois action is controlled by the twisting character. Its trace is a rational point on E only after taking the character projection compatible with descent; an unprojected trace may descend to E^D(Q) or vanish. A twist point therefore meets the test only after transport to the fixed E, projection to the trivial G_Q character, and comparison with x_n. Nonvanishing of a twist L-value can produce a nonzero point/class in that twist channel but cannot identify it with the chosen transverse class on E.

## Heegner and ring class field proposal

For odd (p), a quadratic field (K/\mathbf Q) has degree (2\), prime to (p). Hence a Heegner point over a quadratic field would split a given (p^n)-covering only if its associated point on that particular covering is (K)-rational; equivalently, the resulting underlying torsor class \(\alpha_n\) must restrict to zero. A Heegner point on (E\) is not automatically a point on (C_n\): it produces a Kummer class in the fiber over that point of (E\), and that class must be exactly (x_n|_K\).

The standard Heegner-point Euler system supplies points over ring class fields and norm relations such as \(\operatorname{Tr}_{K[n\ell]/K[n]}P[n\ell]=a_\ell P[n]\) (with the usual good-prime hypotheses). Kolyvagin derivative operators turn these into cohomology classes with controlled Selmer/local properties. These distribution and reciprocity relations compare classes in the Heegner Euler system and constrain Selmer groups; they do not identify an arbitrary prescribed transverse \(x_n\) with \(\delta(P)\) for one of those points. Explicit reciprocity laws relating Heegner classes to special values or (p)-adic (L)-functions likewise provide numerical/cohomological identities, not the missing equality in the finite Kummer coset above.

Ring class extensions have degrees that may have (p)-parts. Taking a trace from such a field may therefore lose the invertibility needed for the criterion. A quadratic field has the clean coprime degree when (p\) is odd, but the point must already be on the fixed covering after restriction. Additional hypotheses are needed for the Heegner construction itself: the Heegner splitting condition on primes dividing the conductor, a compatible modular parametrization and character/level setup, and local Selmer conditions. None follows merely from the fact (x_n) is transverse or satisfies a strict local condition.

### Strict localization and twist conditions

The proposed source must satisfy two separate matching conditions:

1. **Global finite-level match:** \(\delta_K(P)=\operatorname{res}_{K/\mathbf Q}(x_n)\), up to the chosen sign convention, so that the point lies on the specified (p^n)-covering, not merely on (E\).
2. **Local and coefficient match:** the class constructed from the point must obey every local condition defining the chosen classical Selmer group and, if (x_n\) is in a strict subspace, the required strict localization (typically zero at the specified prime/place). A Heegner point or its trace has no automatic zero-localization property. Twist nonvanishing conditions used to kill complementary Selmer summands in generalized Kato constructions are theorem-specific and do not imply this equality or strict condition for (x_n\).

In the Castella–Hsieh setting already audited in `auxiliary-lines.md` and `kato-lift.md`, projected generalized Kato classes lie on a strict line under their stated hypotheses, but the theorem does not identify them with a Heegner Kummer class in (E(\mathbf Q)/p^nE(\mathbf Q)). Its Kummer-image formula additionally assumes finite (p)-primary Sha. The cited source therefore supplies no reciprocity law matching the required finite-level coset for a given transverse integral class. The Heegner/Kolyvagin construction is a genuinely different source of points and Selmer classes, but to solve this task it would need the new assertion that one of its point classes equals this (x_n) (or its restriction) and meets the strict local condition. No general such assertion is established here.

## Exact obstruction and relation to existing rationality

The proposed coprime-splitting criterion is **equivalent** to rational solubility of the same covering: a point over any degree-prime-to-(p) extension implies \(\alpha_n=0\), which is exactly the existing rationality condition. It provides a useful certificate only if an independently constructed point on (C_n\) over such a field is already available. An auxiliary point on (E\) is insufficient.

The precise missing lemma for this construction is:

> For the specified transverse compatible class (x=(x_m)_m), construct an odd-prime quadratic field (K\) satisfying the required Heegner and local hypotheses and a point (P\) on the twist/fiber of the covering (C_n\) over (P\in E(K)), such that \(\delta_K(P)=\operatorname{res}(x_n)\) in (H^1(K,E[p^n])\), and such that the resulting trace class satisfies the required strict local condition. Equivalently, construct the exact rational Kummer coset \(d^{-1}\operatorname{Tr}_{K/\mathbf Q}P\) equal to (x_n\).

This lemma is not supplied by norm compatibility, the Heegner hypothesis, nonvanishing of a twist (L)-value, or the standard reciprocity laws cited above. If it were proved, it would prove that \(\alpha_n=0\), hence solve the existing rationality problem for that level. It is not an independent proof of weak BSD absent this missing realization. The elementary restriction-corestriction implication itself is proved unconditionally.

## Sources

- The finite Kummer sequence and Selmer-covering interpretation are standard; see Michael Stoll, [“Descent on elliptic curves”](https://arxiv.org/abs/math/0611694).
- Howard, [“The Heegner point Kolyvagin system”](https://arxiv.org/abs/1202.6340), states the ring-class-field Heegner point Euler-system norm relation and constructs the associated Kolyvagin system. This is the applicable source for what the standard system supplies; it does not assert equality with an arbitrary fixed Selmer lift.
- Castella–Hsieh, [“On the non-vanishing of generalized Kato classes for elliptic curves of rank 2”](https://arxiv.org/abs/1809.09066), is the auxiliary generalized-Kato source discussed above. Its hypotheses and Kummer-image qualification are detailed in the neighboring swarm notes.
- The identity \(\operatorname{cor}\delta_K(P)=\delta_{\mathbf Q}(\operatorname{Tr}_{K/\mathbf Q}P)\) follows from functoriality of the Kummer connecting homomorphism for restriction/corestriction; the resulting displayed coset is a direct derivation here.
