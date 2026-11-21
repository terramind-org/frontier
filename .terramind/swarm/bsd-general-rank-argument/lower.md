# Lower bound: producing independent rational points

Research cutoff: 21 November 2026. Let `E/Q` be an elliptic curve, let `r_an = ord_{s=1} L(E,s)`, and let `r_alg = rank_Z E(Q)`. The requested direction is `r_an <= r_alg`, with the stronger desired output being `r_an` independent points in `E(Q)`. No cited general theorem presently supplies this for arbitrary `r_an >= 2`.

## Exact algebraic implication, conditional on points and heights

By Mordell–Weil, `E(Q)/tors` is a free abelian group of rank `r_alg`. The Néron–Tate canonical height induces a positive-definite quadratic form on `E(Q) ⊗_Z R`; its associated symmetric bilinear pairing is

`<P,Q> = (hat h(P+Q) - hat h(P) - hat h(Q))/2`.

For any `P_1,...,P_m in E(Q)`, set `G=(<P_i,P_j>)`. Then

`det(G) != 0  =>  P_1,...,P_m are Z-linearly independent modulo torsion`.

Indeed, a rational linear relation gives a nonzero vector in the Gram matrix kernel. Conversely, if the classes are dependent in `E(Q)⊗Q`, the Gram matrix is singular. Thus `det(G)>0` is an exact certificate of independence when the pairing is the canonical height and the points are certified rational points. It gives `r_alg >= m`; combined with an independent proof that `r_an=m`, it gives the desired rank equality. Heights certify independence of already-produced rational points; they do not produce them.

For arbitrary analytic rank `r`, the needed arithmetic input can be stated without ambiguity as: construct `P_1,...,P_r in E(Q)` with `det(<P_i,P_j>) != 0`. For a purported construction over an extension `K/Q`, it is not enough that the points be independent in `E(K)`: one needs rational points. A trace `Tr_{K/Q}(P)` lies in `E(Q)`, but may vanish or be torsion, and traces of multiple classes may become dependent. A proof must establish non-torsion and a nonzero rational height determinant after tracing (or otherwise descend the points).

## What the known construction mechanisms actually imply

### Heegner points / Gross–Zagier / Kolyvagin

In a Heegner setup (an imaginary quadratic `K` satisfying the conductor splitting condition, with the remaining hypotheses of the specific formula), Gross–Zagier identifies the height of a Heegner point or its character component with a nonzero explicit factor times a first derivative of a Rankin `L`-series. In that setup, nonvanishing of that derivative is equivalent to positive height and hence to a non-torsion point over the relevant ring-class field. Kolyvagin's Euler system then bounds the Selmer group and yields rank one and finite Tate–Shafarevich group in the theorem's hypotheses. This mechanism produces one point from a first derivative, not `r` independent points from an order-`r` derivative of `L(E,s)`.

For `E/Q`, the classical unconditional theorem is `ord_{s=1}L(E,s) in {0,1} => rank E(Q)=ord L and Sha(E/Q) finite`, using modularity, Gross–Zagier/Kolyvagin and the necessary quadratic twists/Heegner systems. It does not extend by iteration to higher order. A nonzero `L^(r)(E,1)` is a complex scalar, not a rational point or a collection of points. The functional equation and parity may constrain `r`, but do not supply independent points.

### Higher derived classes and heights

Howard's derived p-adic height pairings relate successive Selmer/Iwasawa filtration data to higher derivatives of a cohomologically defined p-adic L-function under the paper's hypotheses. This is evidence/structure about p-adic Selmer classes and pairings; a nonzero derived pairing is not itself a rational point in `E(Q)`. The Castella–Hsu–Kundu–Lee–Liu BDP work proves an algebraic leading-coefficient result in its Heegner/split-good-prime setting and relates the analytic p-adic statement to a main-conjecture input; its order formula requires expected maximal nondegeneracy of the anticyclotomic p-adic height. Even granting those conditional p-adic conclusions, an additional descent/rationality theorem is required to get `r` independent rational points.

Burns–Kurihara–Sano prove higher derivative formulas for Kato Euler systems and an arbitrary-rank order-of-vanishing component under technical hypotheses, while formulating a generalized Perrin–Riou conjectural reciprocity/leading-term layer. Their derived Euler-system classes are cohomological. No general theorem identified here turns their nonvanishing into `r` independent points of `E(Q)` for arbitrary `E/Q` and arbitrary `r`.

Rank-two diagonal-cycle/generalized Kato constructions similarly yield classes in Galois cohomology/Selmer groups. The proved nonvanishing cases have restrictive ordinary-prime, residual, auxiliary-field and nonvanishing hypotheses. A Selmer dimension conclusion is not automatically a Mordell–Weil lower bound of the same dimension: the Selmer group also contains the Tate–Shafarevich contribution. To infer independent rational points one needs a theorem identifying or bounding that contribution (for example finiteness of the relevant `Sha[p^∞]`, with the precise Selmer exact sequence and local conditions), then a rationality/descent argument. This is exactly where rank-two class nonvanishing alone does not close the target.

## Hypothesis audit and removal attempts

1. **Nonvanishing.** A nonzero first derivative in a Gross–Zagier setting gives a non-torsion Heegner point. Higher-order complex nonvanishing for arbitrary `E/Q` is part of the target, not an available source of points. Higher p-adic derivative nonvanishing is a different analytic statement and may be conditional on height nondegeneracy or a main conjecture.
2. **Independence.** If rational points are explicitly obtained, positivity of the Néron–Tate Gram determinant is sufficient and unconditional. It cannot be applied to classes in a Selmer group until they are shown to come from rational points and the pairing is identified with the canonical height pairing.
3. **Rationality.** Heegner points usually start over an imaginary quadratic or ring-class field. Trace gives a rational point but no general nonvanishing or independence guarantee. The first-derivative theorem's rank-one conclusion uses its own sign and Euler-system hypotheses; it does not generalize to a family of independent rational traces at higher rank.
4. **Selmer versus Mordell–Weil.** A Selmer corank lower bound is not by itself a Mordell–Weil rank lower bound: the exact sequence includes `Sha[p^∞]`. Finiteness of `Sha` is known in the classical analytic-rank ≤1 range under the theorem, not generally in the higher-rank target.
5. **Removing conditions.** The hypotheses of the existing p-adic and diagonal-cycle theorems are theorem inputs, not technicalities that can be dropped by formal manipulation. The global gap remains even if individual local hypotheses are removed in particular families: no construction-and-descent theorem establishes a full-rank rational height matrix for every `E/Q`.

## Precise remaining lemma

A route using higher derivatives would need a theorem of the following strength, currently unproved in this audit:

> For every elliptic curve `E/Q` with `r=ord_{s=1}L(E,s)<∞`, there exist `P_1,...,P_r in E(Q)` such that the Néron–Tate height matrix `(<P_i,P_j>)` is nonsingular.

A motivic/Beilinson–Bloch formulation predicts appropriate global classes and a regulator determinant, but existence of these classes, their rational-point realization for elliptic curves over `Q`, the required nondegeneracy, and the link of the determinant to the complex leading coefficient are conjectural in general. Stating the height-matrix conclusion is already essentially the missing `r_an <= r_alg` inequality; it must not be represented as a deduction from the existence of a higher derivative or a p-adic derived class.

## Primary sources and prior swarm notes

- B. Gross and D. Zagier, “Heegner points and derivatives of L-series,” *Invent. Math.* 84 (1986), 225–320, [DOI](https://doi.org/10.1007/BF01388809).
- V. Kolyvagin, “Finiteness of `E(Q)` and `Sha(E,Q)` for a subclass of Weil curves,” *Math. USSR-Izv.* 32 (1989), 523–541, [Math-Net record and paper](https://www.mathnet.ru/eng/im1191).
- B. Howard, “Derived p-adic heights and p-adic L-functions,” [arXiv:1202.6343](https://arxiv.org/abs/1202.6343).
- F. Castella, C.-Y. Hsu, D. Kundu, Y.-S. Lee, Z. Liu, “Derived p-adic heights and the leading coefficient of the BDP p-adic L-function,” [arXiv:2308.10474](https://arxiv.org/abs/2308.10474), published in *Trans. AMS Ser. B* 12 (2025), 748–788, [DOI](https://doi.org/10.1090/btran/227).
- F. Castella, A. Grossi, J. Lee, C. Skinner, “On the non-vanishing of generalized Kato classes for elliptic curves of rank 2,” [arXiv:1809.09066](https://arxiv.org/abs/1809.09066), published in *JEMS* (2022).
- D. Burns, M. Kurihara, T. Sano, “On derivatives of Kato’s Euler system for elliptic curves,” *J. Math. Soc. Japan* 76 (2024), 855–919, [DOI](https://doi.org/10.2969/jmsj/90699069).
- Prior swarm notes read: `.terramind/swarm/bsd-research-and-formal-attempt/{higher-rank.md,heegner.md,iwasawa.md}` and handoffs `investigate-higher-rank-hm95g.md`, `trace-rank-zero-and-one-vqxgu.md`.

## Conclusion

The exact last step is not “higher derivative nonzero implies points.” It is a rationality-and-nondegeneracy theorem producing a nonsingular canonical-height matrix of rational points of size `r_an`. Gross–Zagier/Kolyvagin establish the relevant construction only in the rank-zero/one setting; higher derived Euler-system and p-adic-height results do not supply this universal rational-point statement. No unconditional proof of `r_an <= r_alg` for all `E/Q` has been found, and the precise missing assertion above is the desired inequality itself in a point-and-height form.
