# Independent audit: prime-product comparison

## Verdict

The main obstruction is real: reductions of a fixed Mordell–Weil basis do not by themselves yield the required sharp-cutoff product asymptotic. The source note is careful about fixed-modulus Chebotarev and about the distinction between a subgroup index and the full group order. However, its Goldfeld leading-constant formula has the reciprocal in the wrong direction. There is also a useful precision correction: Frobenius-trace averaging cannot simply be treated as a first-order term, since the quadratic terms in the logarithmic Euler-factor expansion contribute on the same `log log x` scale.

## Normalization and Goldfeld implication

At good primes, with `a_p=p+1-#E(F_p)`,

`#E(F_p)/p = 1 + (1-a_p)/p = (1-a_p/p+1/p)^(-1)`.

Thus the product `P_E(x)=∏_{p≤x} #E^ns(F_p)/p` is the product of the reciprocals of the local Euler factors at `s=1`. At bad primes the nonsingular locus has size `p-a_p` for the usual local coefficient `a_p∈{-1,0,1}`, and its ratio to `p` is likewise the reciprocal local factor. This agrees with Conrad's definition and means finitely many bad primes do not affect the exponent; their positive factors are retained in the leading constant.

The Goldfeld statement in Conrad is written for the reciprocal product `∏ p/#E^ns(F_p) ~ C_-(log x)^(-r)`. Its constant is

`C_- = (L^(r)(E,1)/r!) / (sqrt(2) exp(r gamma))`.

Consequently, for the direct product used in `prime-product.md`, the constant is the reciprocal:

`P_E(x) ~ C_+(log x)^r`, with `C_+ = (r! sqrt(2) exp(r gamma))/L^(r)(E,1)`.

Here `L^(r)(E,1)` is the nonzero first Taylor derivative and `r=ord_{s=1}L(E,s)`. This formula presupposes the product asymptotic, which itself forces the order to be `r`. The source note's displayed constant `L^(r)/(r! sqrt(2)e^(r gamma))` belongs to the reciprocal product, not to `P_E`; it must be inverted. Conrad's theorem assumes a positive constant (and states a real exponent); for the elliptic-curve application the rank/exponent is nonnegative integral. Goldfeld yields analytic rank, not equality with Mordell–Weil rank unless that is separately the assumed exponent.

This repairs a normalization error without changing the consequence needed by the argument: an all-cutoff asymptotic with exponent `rank E(Q)` implies analytic rank equals algebraic rank.

## Quantifiers, hypotheses, and limits

- The direct implication is for one fixed `E/Q`, with the asymptotic holding as real `x→∞` over **all** cutoffs and with a fixed nonzero leading constant. It gives nonvanishing for `Re(s)>1` and `ord_{s=1}L(E,s)=r`. It is not merely a statement along a subsequence or outside an exceptional set.
- Sheth's converse in the cited version assumes RH for `L(E,s)`, fixes `r=ord_{s=1}L(E,s)`, and obtains the product asymptotic only for `x` outside a measurable set `S` with `∫_S dx/x<∞`. It does not assert all-cutoff convergence. Nor does it identify analytic order with algebraic rank absent BSD. The source note correctly keeps the exceptional-set limitation.
- The Conrad equivalence is also important: the sharp original product asymptotic is equivalent to `psi_E(x)=o(x log x)`, where `psi_E(x)=∑_{p^k≤x, p good}(alpha_p^k+beta_p^k)log p`. RH gives only the substantially weaker `O(x(log x)^2)` estimate. Sheth's RH-conditional finite-log-measure control does not upgrade this to the needed unconditional all-cutoff estimate.
- “Finitely many bad-prime conventions change only a fixed nonzero constant” is safe for this product because each bad-prime factor is positive and nonzero. One should say explicitly that the definition uses nonsingular points at bad primes; it is not the cardinality of the possibly singular projective cubic.

## Index and trace claims: what follows, and what does not

For every good prime, reduction gives a homomorphism from the rational points integral at `p` into `E(F_p)`; after excluding the finite primes where the chosen points or model are not integral, the reductions of a chosen Mordell–Weil basis generate a subgroup `H_p`. Torsion can be removed from the basis choice or included as a fixed finite contribution; it does not make the reductions independent at every prime. The identity

`#E(F_p) = #H_p · [E(F_p):H_p]`

is exact. It supplies no lower bound for `#H_p` or upper bound for the index from Q-linear independence alone. Finite exceptional primes and reductions where points coalesce must be excluded/handled, not silently treated as independent.

The proposed precision target is correctly on the logarithmic scale:

`log P_E(x)=Σ_{p≤x} log(#E^ns(F_p)/p) = r log log x + o(log log x)`.

But the source note's phrasing that this requires “both Frobenius averaging and a mean-log-index error” should not be mistaken for a proved decomposition or a sufficient pair of independent estimates. The exact subgroup identity gives `log #E(F_p)=log #H_p+log index`; it does not express `log #E(F_p)` solely through a first-order trace average. At good primes,

`log(#E(F_p)/p)=log(1+(1-a_p)/p)`.

The expansion has a first term `-a_p/p` and a quadratic term of size `-a_p^2/(2p^2)`, with further terms. Since `|a_p|≤2√p`, these remainders are not absolutely summable over primes at the needed boundary: the quadratic contribution is potentially of order `Σ_{p≤x}1/p ~ log log x`. Any purported trace estimate must control the complete logarithmic Euler-factor sum (including secondary terms/cancellation), not just `Σ a_p/p`. Likewise, a subgroup-index estimate alone cannot establish the full product asymptotic. The source note's final required sum is the right target, but calling the ingredients “at minimum” should be read as a research agenda, not a theorem or a sufficient criterion as presently specified.

The Kummer/Chebotarev caution is sound. Fixed-modulus density statements do not automatically control moduli growing with the cutoff, and the needed error must be `o(log log x)` after summation. The note should avoid implying that a specific growing-modulus estimate is known to be necessary in every possible proof: it is a requirement of this proposed reduction strategy, not a formal necessity for proving the product by any method.

Freiberg–Kurlberg's cited result is correctly distinguished from the needed claim. Their Theorem 1.1 assumes RH for Dedekind zeta functions of all division fields in its stated GRH package and estimates the average exponent `e_p` of `E(F_p)` (with an unconditional CM theorem separately). The positive average of `e_p/#E(F_p)` does not concern the subgroup generated by a fixed rational basis and does not provide the log-product asymptotic or its sharp error.

## Repaired conclusion / precise remaining lemma

A corrected formulation is:

> For each fixed `E/Q`, prove unconditionally, for every real cutoff `x→∞`,
> `Σ_{p≤x} log(#E^ns(F_p)/p) = rank(E(Q)) log log x + o(log log x)`.
> This is equivalent to the asserted positive-constant sharp-cutoff product asymptotic. Goldfeld then implies `ord_{s=1}L(E,s)=rank(E(Q))` (and nonvanishing in `Re(s)>1`). No cited result derives this estimate from reductions of a fixed Mordell–Weil basis. Any basis-based proof must establish, in aggregate and with the stated uniformity, enough information on both the subgroup/index and the full Frobenius Euler-factor contributions; the current notes supply no such bound.

This is the precise unresolved implication. Sheth supplies only an RH-conditional asymptotic off a finite-logarithmic-measure set, while Goldfeld supplies the forward implication from the full asymptotic; neither closes the basis-to-product step.

## Sources independently checked

- Keith Conrad, [“Partial Euler Products on the Critical Line”](https://www.cambridge.org/core/services/aop-cambridge-core/content/view/061A145952B0C1145EE31E0EAD47ED93/S0008414X0001871Xa.pdf/partial-euler-products-on-the-critical-line.pdf), pp. 267–268, Theorems 1.1 and 1.3, Corollary 5.7. In particular, the direct-versus-reciprocal product and the constant's direction.
- Arshay Sheth, [“Euler Product Asymptotics for L-functions of Elliptic Curves”](https://warwick.ac.uk/fac/sci/maths/people/staff/sheth/eulerproductfinalversion.pdf), Theorem 1.5 and Corollary 1.6 in the final version; the preprint numbering differs. Also checked the [arXiv record](https://arxiv.org/abs/2312.05236). The exceptional set has finite logarithmic measure.
- Tristan Freiberg and Pär Kurlberg, [“On the Average Exponent of Elliptic Curves Modulo p”](https://kurlberg.github.io/eprints/ecexp.pdf), abstract and Theorems 1.1–1.2.

## Scope

This review corrects the leading-constant normalization and sharpens the precision caveat. It does not prove the uniform prime-product estimate or weak BSD for all `E/Q`.
