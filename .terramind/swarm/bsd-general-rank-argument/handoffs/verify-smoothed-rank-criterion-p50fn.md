Outcome: done
## Done
Independently rechecked the exact good-prime identity using normalized roots \(u=\alpha_p/p,v=\beta_p/p\) and \(z=p^{-t}\):
\[
\log L_p(E,1+t)+z\log(N_p/p)=\sum_{k\ge1}(u^k+v^k)(z^k-z)/k.
\]
The \(k=1\) term vanishes identically. The \(k=2\) bound and compact normal convergence of the grouped correction hold; higher terms are summable by \(O(p^{-3/2})\). The prior review’s alleged uncancelled prime-zeta term was an error caused by omitting the quadratic term in the scalar logarithm. Updated `abel-review.md` with corrected signs, bounds, bad-prime treatment, analytic continuation, and order comparison. The coefficient conclusion is valid conditionally on the stated partial-product asymptotic; the arithmetic estimate identifying its coefficient with Mordell–Weil rank is still unproved.

Ran `bun run check`: 434 tests passed, 1 skipped, 0 failed; validation found 18,618 problems and 0 attempts. Committed on `swarm/bsd-general-rank-argument--verify-smoothed-rank-criterion-p50fn-c2`.

## Deviations
None.

## Concerns
The analytic deduction does not supply the arithmetic premise needed for unconditional weak BSD. This remains a substantial unproved estimate, not a detail of the smoothing argument.

## Follow-ups
Prove or refute, for every elliptic curve over Q, the all-cutoff estimate `sum_{p≤x} log(N_p/p) = rank(E(Q)) log log x + o(log log x)`, or provide another unconditional comparison of analytic and Mordell–Weil ranks. No official submission.
