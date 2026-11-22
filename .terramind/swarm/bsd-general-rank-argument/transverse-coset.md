# Finite-level transverse Kummer cosets: detection is not solubility

## Scope and conclusion

Fix an elliptic curve `E/Q`, a prime `p`, and the classical `p^n`-Selmer groups with their downward transition maps. Let `P` be a known non-torsion point whose class is primitive in the free Mordell–Weil lattice `M=E(Q)/E(Q)_tors` (equivalently, `M/Z[P]` is torsion-free). Let

`x=(x_n) in lim Sel_{p^n}(E/Q)`

be an integral compatible class, assumed to satisfy any additional strict local condition in the problem. The strict condition does not change the following argument only if its classes are also in the **classical** Selmer group with the indicated compatible lifts; a strict subspace cannot be substituted silently.

There is a precise finite-level replacement for a uniform height bound: if `x` is independent of the image of `P` after tensoring the classical inverse-limit Selmer group with `Q_p`, then for every sufficiently large `n`, `x_n` lies outside the finite-level Kummer image of the saturation of `ZP` plus torsion. In fact it is enough that this exclusion occur at unboundedly many levels. This detects a transverse class, but does not show its `p^n`-covering has a rational point. If one such covering does have a rational point, that point is outside the saturated cyclic subgroup, so `rank E(Q) >= 2`.

The bounded-height claim also has a clean replacement: for every vector in the Mordell–Weil `p`-adic completion, centered representatives in a fixed Mordell–Weil basis have canonical heights `O_{E,B}(p^{2n})`. This is a direct quadratic-form estimate and does **not** assume that `x` is in the Mordell–Weil completion. If it is not, there are no such representatives for `x`; the estimate is not a solubility argument.

## The finite-level subgroup and criterion

Write `G=E(Q)`, `T=G_tors`, and `M=G/T ~= Z^r` by Mordell–Weil. Primitivity of `[P]` means it extends to a basis `[P],e_2,...,e_r` of `M`. In this basis the saturation of `ZP+T` in `G` is exactly `ZP+T` itself. More generally, if a nonprimitive point is used, define

`H = {Q in G : kQ in ZP+T for some nonzero integer k}`;

then `H/T` is the saturated rank-one sublattice `Q[P] intersect M`. This is the torsion-aware meaning of saturation; using only `ZP` without `T` can falsely label torsion translates as transverse.

Let `K_n` denote the Kummer injection `G/p^nG -> Sel_{p^n}(E/Q)`. Define the finite-level known-line subgroup

`L_n = K_n((H+p^nG)/p^nG) <= Sel_{p^n}(E/Q)`.

The assertion `x_n notin L_n` is an exact finite computation/test once `x_n` and the subgroup are represented. For a primitive `P`, a `Z_p`-basis of `M tensor Z_p` can be chosen beginning with `[P]`; in coordinates, `L_n` is the first coordinate modulo `p^n`, together with the full `p`-primary torsion Kummer contribution. Prime-to-`p` torsion contributes zero to `G/p^nG` after its multiplication by `p^n` is inverted, while `T[p^infty]` must be retained. Equivalently compute `L_n` from the displayed subgroup formula, which handles all torsion without a convention about generators.

For the compatible inverse system, the following are equivalent:

1. `x` lies in the image of `H tensor Z_p` (including the finite `p`-primary torsion completion) in `lim Sel_{p^n}`.
2. `x_n in L_n` for every `n`.
3. `x_n in L_n` for arbitrarily large `n`.

For (3) implies (1), choose unbounded `n_j` with `x_{n_j}=K_{n_j}(h_j)` for `h_j in H/p^{n_j}H` (with the formula interpreted in `G/p^{n_j}G`). Downward compatibility gives this equality at every fixed level `m<=n_j`. The compact inverse limit of the finite groups `H/p^mH` has a convergent subsequence of the representatives; its limit maps to `x` at every fixed level. Equivalently, in the basis beginning with `P`, the first coordinates have a convergent subsequence in `Z_p`, and all transverse coordinates vanish modulo arbitrarily large `p^{n_j}`, hence vanish in `Z_p`; the finite torsion factor is handled by a constant subsequence. Thus if `x` is not in this completed known line, there is an `N` such that

`x_n notin L_n for every n >= N`.

This compactness statement only uses the inverse-limit Kummer subgroup and compatibility. It does not assert that `x` itself is Kummer. More generally, if `x` has nonzero image in `T_p Sha` then it is automatically outside the Mordell–Weil known line, but that transverse Sha direction is not a rational point.

## A rational point on one transverse covering implies rank at least two

The exact finite Kummer sequence is

`0 -> G/p^nG --K_n--> Sel_{p^n}(E/Q) -> Sha(E/Q)[p^n] -> 0`.

The Selmer element `x_n` is represented by an everywhere locally soluble `p^n`-covering `C_n -> E`. It has a rational point if and only if its image in `H^1(Q,E)` is zero, equivalently if and only if its image in `Sha[p^n]` is zero. In that case exactness gives `Q_n in G` with `K_n(Q_n mod p^nG)=x_n`. If also `x_n notin L_n`, then `Q_n` cannot lie in `H`: otherwise its Kummer image would be in `L_n`. Hence `[Q_n]` is not in the saturated rational line `H/T`, so `[P],[Q_n]` are linearly independent in `M tensor Q` and `rank G >= 2`. The conclusion is unconditional **given the rational point on that covering**; no height estimate is needed.

Conversely, local solubility alone is the Selmer condition and does not imply a rational point. An everywhere locally soluble genus-one torsor can represent a nonzero Sha class. The finite-level test `x_n notin L_n` distinguishes a transverse Selmer class from the known rational line, not a rationally soluble class from an insoluble one.

## Height growth for arbitrary completion vectors

Choose a full `Z`-basis `Q_1,...,Q_r` of `M` and lifts to `G`. For any vector `u=(u_1,...,u_r) in Z_p^r`, let `a_i(n)` be a centered integer representative of `u_i mod p^n`, so `|a_i(n)| <= p^n/2`. Define the rational representative

`R_n(u) = sum_i a_i(n) Q_i`.

Its Kummer class is the level-`n` image of `u`; any torsion coordinate can be represented by an element of the finite `p`-primary torsion group and does not affect canonical height. The canonical height is a quadratic form on `M tensor R`; if `A=(<Q_i,Q_j>)` is its fixed positive-definite height matrix, then

`hat h(R_n(u)) = a(n)^t A a(n) <= ||A|| (sum_i |a_i(n)|^2) <= ||A|| r p^{2n}/4`.

Thus `hat h(R_n(u))=O_{E,(Q_i)}(p^{2n})`, uniformly for every `u in Z_p^r`. For any fixed bounded changes of representatives (including torsion), the same order bound holds. If “centered representative” instead means a representative minimizing canonical height among the entire coset of `p^n M`, its height is no larger than the displayed one, so the bound remains true.

This estimate is sharp in scale for a nonzero fixed coordinate represented by centered residues: their absolute values can be proportional to `p^n` along subsequences, and the quadratic height then grows on the `p^{2n}` scale. It is not a depth-independent bound and cannot invoke Northcott. Crucially, the basis spans only the Mordell–Weil completion. For a general compatible Selmer class with nonzero `T_p Sha` component, `u` does not exist and no rational representative `R_n(u)` is supplied. For a strict Kummer class that does lie in the completion, the estimate applies regardless of whether it is already in the known line; it does not construct any new rational points beyond the chosen representatives of that completion vector.

## Trying to prove solubility by descent or Cassels pairing

There are two mathematically distinct goals:

- **Necessary finite obstruction tests.** For `x_n` to be rationally soluble, its Sha image must vanish. Any descent obstruction that is functorial in the torsor and nonzero on `x_n` proves insolubility. Cassels–Tate pairings can detect nonzero Sha classes in suitable finite quotients; likewise, higher-descent pairings can obstruct a class from lifting to a specified higher Selmer group. A rational point necessarily makes the underlying torsor class zero and so passes all such tests.
- **Sufficient solubility certificate.** An explicit `Q_n in C_n(Q)` is sufficient, and is directly checkable. Equivalently, a proof that the image of `x_n` in `H^1(Q,E)` is zero is sufficient by the Kummer exact sequence. A theorem establishing injectivity of a chosen obstruction map on the relevant subgroup could also suffice, but that injectivity is an additional hypothesis/theorem, not a consequence of the pairing value being zero.

The natural attempted route is to pair the class with all available Selmer classes and seek a nonzero value (which rules it out) or a vanishing value (which might appear to prove it soluble). The latter inference fails in general: the Cassels–Tate pairing on `Sha` has divisible subgroup in its radical, and nondegeneracy is available under finiteness hypotheses on `Sha`; vanishing against tested classes is not a rational-point certificate without a theorem eliminating the radical and proving the tested subgroup is exhaustive. The analogous higher-descent pairing measures a lift obstruction, not the existence of a rational point on the original covering. In particular, a compatible nonzero divisible-Sha direction can survive every finite level and be orthogonal to every Cassels–Tate test while never becoming Kummer.

Searching for a rational point on an explicit covering is a valid direct route, and success on even one transverse level proves rank at least two. But the search is not a proof of existence if it fails, and no unconditional argument found here forces one of the transverse coverings to be soluble. The rank-two target itself cannot be used to assert that the classes are Kummer: that would assume the desired rationality conclusion.

## First missing noncircular input

The finite-level independence claim is established, conditional only on the classical integral compatible class and its independence from `P` in the inverse-limit Selmer group after tensoring with `Q_p`. It does not make that class rational. The first missing input for this route is precisely an **unconditional rationality/solubility theorem** for at least one transverse level:

> Given the specified nonzero strict compatible class `x` and known primitive point `P`, prove that there exists a finite `n` with `x_n notin L_n` and with the image of `x_n` in `Sha(E/Q)[p^n]` equal to zero.

The second condition is equivalent to a rational point on `C_n`; it is not implied by the first, by local conditions, by compatible lifting, or by bounded/centered height growth. Proving it by assuming finiteness of the relevant Sha subgroup, a rational-rank conclusion, or a leading-term formula that presupposes the same Kummer realization would be circular or would add a hypothesis. A Cassels–Tate strategy would need a new nondegeneracy/completeness input strong enough to kill the specific divisible-Sha alternative, plus an argument that the class is zero in Sha; merely computing pairings cannot do so. This is the first precise unproved lemma in the proposed unconditional route. Even if it is supplied for a class, one must separately establish the stated local and Selmer hypotheses that produced that class; this note does not provide a general such class or derive weak BSD.

## Sources

- Michael Stoll, [“Descent on elliptic curves”](https://arxiv.org/abs/math/0611694): the exact sequence `0 -> E(Q)/nE(Q) -> Sel^(n)(E/Q) -> Sha(E/Q)[n] -> 0`; Selmer elements as locally soluble coverings; searching for rational points as a way to prove Kummer membership.
- J. H. Silverman, [*The Arithmetic of Elliptic Curves*, Chapter VIII](https://www.pdmi.ras.ru/~lowdimma/BSD/Silverman-Arithmetic_of_EC.pdf): Mordell–Weil finite generation, Northcott, and the canonical height as a quadratic form. The displayed `O(p^{2n})` bound above is derived directly from these standard properties and the chosen basis.
- Alexander Smith, [“Selmer groups and a Cassels–Tate pairing for finite Galois modules”](https://arxiv.org/abs/2103.08530): pairing obstruction for lifting Selmer classes through finite-level sequences; vanishing is a lifting condition, not rational solubility.
- For the standard divisible-radical caveat for the Cassels–Tate pairing, see the overview of the pairing in [Selmer Groups](https://www.maths.nottingham.ac.uk/plp/pmzcw/download/baskerville_selmer_groups.pdf); the claim used here is only that a pairing with divisible radical cannot certify that a tested element is zero without further hypotheses.
- Prior swarm note `.terramind/swarm/bsd-general-rank-argument/descent-height.md` records the inverse-limit Kummer sequence, the role of `T_p Sha`, and why finite descent does not eliminate divisible Sha.
