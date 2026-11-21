Outcome: done
## Done
- Corrected `.terramind/swarm/bsd-general-rank-argument/prime-product.md` at source. Conrad's Theorem 1.1 uses the reciprocal product `Q_E=1/P_E`, whose constant is `(L^(r)(E,1)/r!)/(sqrt(2) exp(r gamma))`; for the direct nonsingular-point product `P_E`, the constant is its reciprocal, `r! sqrt(2) exp(r gamma)/L^(r)(E,1)`.
- Made the normalization explicit for both good primes and bad primes. The direct factors `N_p/p` are reciprocals of the local Euler factors at `s=1`; Conrad's finite bad-prime convention changes the leading constant if changed, not the exponent. Distinguished the derivative from the leading Taylor coefficient `L^(r)/r!`.
- Aligned `prime-product-review.md` and this handoff with the source correction. Tightened the unresolved estimate: `sum_{p<=x} log(N_p/p)=rank(E(Q)) log log x+c_E+o(1)` for all real cutoffs is required for a positive-constant sharp-cutoff product asymptotic. `o(log log x)` alone only fixes the exponent and is insufficient for Goldfeld. The basis/index and full Frobenius Euler-factor contribution remain uncontrolled at this precision.
- Verified the normalization against Conrad, “Partial Euler Products on the Critical Line,” Theorem 1.1, equations (1.1)–(1.3), and checked the review's existing Sheth and Freiberg–Kurlberg references. Conrad source: https://www.cambridge.org/core/services/aop-cambridge-core/content/view/061A145952B0C1145EE31E0EAD47ED93/S0008414X0001871Xa.pdf/partial-euler-products-on-the-critical-line.pdf
- `bun run check` passed: TypeScript check succeeded, 434 tests passed, 1 skipped, 0 failed; validation reported 18,618 problems and 0 attempts.

## Deviations
- Updated the task-owned source note as explicitly requested in the live instruction, in addition to the independently owned review and handoff.

## Concerns
- The corrected constant repairs normalization only. The all-cutoff `o(1)` remainder after the logarithmic main term and constant remains unproved; no weak BSD result follows without it.

## Follow-ups
- None for this task. The uniform arithmetic estimate remains an open research obligation of the swarm goal.
