# Review: rational localization witness

## Scope checked

This review checks the implication required by revised Castella §5.2 and its boundary. It is a source-based audit of the companion note, not an independent worker's review.

## Findings

1. **Point to finite localization:** Correct, conditional on good reduction at \(p\). The local Kummer class of \(P\) is in \(H^1_f(\mathbf Q_p,V_pE)\). The local Kummer map after tensoring with \(\mathbf Q_p\) has source \(E(\mathbf Q_p)\otimes\mathbf Q_p\); the formal logarithm has torsion kernel, so an infinite-order rational point has nonzero logarithm and nonzero local class. A period normalization cannot affect nonvanishing.
2. **Use of Castella's theorem:** The direction is correct. The rational point establishes that the map \(\operatorname{loc}_p\) on the entire Selmer group is nonzero. Under the theorem's positive-even-analytic-order and dimension-two hypotheses, Theorem 5.2.3 gives \(\kappa_p(E)\ne0\) and says it spans \(\ker(\operatorname{loc}_p)\). The strict class therefore has zero localization by definition; the point is a witness for nonzero map, not nonzero image of the strict class.
3. **Hypotheses:** The inference must retain revised (h1)–(h3) and Choice 5.2.1, including \(q\parallel N_E\), the residual ramification clause, the \(p>5\) or residual-image alternative, auxiliary splitting and twist nonvanishing. The companion note does not treat these as automatic.
4. **Lift to rational rank two:** Dimension two and one non-torsion point yield only \(r+t_p=2\), with \((r,t_p)=(1,1)\) or \((2,0)\). The second case is not forced. Cassels–Tate's alternating nondegenerate pairing is on the reduced quotient; the maximal divisible subgroup is its radical. Its finite square-order consequence does not kill corank-one divisible Sha.
5. **Parity distinction:** The unconditional p-parity theorem over \(\mathbf Q\) concerns total p-primary Selmer corank. With analytic order two, it is consistent with total corank two. It does not by itself assert MW rank even: the decomposition includes the divisible-Sha corank. Do not infer MW parity from Selmer parity by assuming that contribution vanishes.

## Exact conclusion

The defensible conditional partial result is: under Castella's revised hypotheses, Selmer dimension two, and an independently exhibited infinite-order \(P\in E(\mathbf Q)\), the generalized Kato class is a nonzero generator of the one-dimensional strict Selmer kernel. To conclude that both dimensions are rational, add an independent second-point/rank-at-least-two certificate or eliminate the divisible p-primary Sha contribution by a separate theorem. The hypotheses and parity argument alone do neither. No example or universal weak-BSD implication is claimed.

## Primary-source anchors

* Castella revised manuscript, §§5.1–5.2, especially Remark 5.1.4 and Theorem 5.2.3: https://web.math.ucsb.edu/~castella/GKC-IMC.pdf
* Dokchitser–Dokchitser, p-parity theorem over \(\mathbf Q\): https://arxiv.org/abs/math/0610290
* Trihan–Wüthrich, Cassels–Tate pairing and divisible radical, §6: https://doi.org/10.1112/S0010437X1100532X
