Outcome: done
## Done
Independently reviewed `abel.md` and wrote the full audit to `abel-review.md`. The Abel partial-summation and positive-real asymptotic steps are valid under the stated premise. Found a decisive error in the Euler comparison: the linear local terms in `log L + F` add to `p^(-1-t)`, leaving a prime-zeta divergence. The proposed bounded correction is therefore not bounded, and the claimed analytic order is not established. With the missing prime-zeta term isolated, the comparison instead gives `ord_{s=1} L(E,s)=1-R`, conditionally on the premise. The required arithmetic estimate from Mordell–Weil rank remains unproved, and the target coefficient requires correction.

Ran `bun run check`: passed (434 tests, 1 skipped, 0 failed; validation reports 18,618 problems and 0 attempts). The first check invocation lacked `tsc`; installed declared dependencies with `bun install` and reran successfully.
## Deviations
None.
## Concerns
`abel.md` currently asserts an invalid cancellation and consequently an invalid coefficient identity. Its central result needs correction before it can be used by the swarm argument.
## Follow-ups
Revise `abel.md` to include the prime-zeta term and use coefficient `1-R`; separately establish or refute the resulting arithmetic asymptotic needed to identify that coefficient with analytic and Mordell–Weil rank. No unconditional weak BSD implication is proved here.
