Outcome: done
## Done
- Independently reviewed `.terramind/swarm/bsd-general-rank-argument/auxiliary-primes.md` and wrote `.terramind/swarm/bsd-general-rank-argument/auxiliary-review.md`.
- Confirmed the fixed-prime Kummer exact sequences and the abstract exact-sequence countermodel. The countermodel proves insufficiency of formal exactness and equal coranks, but makes no elliptic-curve realization claim.
- Clarified that the rational Bloch–Kato space is not formed by naively tensoring the torsion (p^\infty)-Selmer group with \(\mathbb Q_p\), and that any cross-prime comparison needs additional structure/theorem. Identified the valid one-prime implication: a Selmer corank upper bound gives the same upper bound on Mordell–Weil rank. No lower bound or new unconditional weak BSD implication follows from prime variation alone.
- `bun install` succeeded. `bun run check` succeeded: 434 passed, 1 skipped, 0 failed; validation reported 18,618 problems and 0 attempts.

## Deviations
None.

## Concerns
- The Bloch–Kato/Kummer comparison is convention-sensitive; the review cites the standard rational representation and Selmer-structure formulation rather than treating it as a literal tensor operation on a torsion group.

## Follow-ups
- General weak BSD still needs the all-curves lower bound \(\operatorname{rank}E(\mathbb Q)\geq \operatorname{ord}_{s=1}L(E,s)\), or an unconditional theorem supplying the relevant analytic-to-Selmer and Selmer-to-Mordell–Weil comparisons.
