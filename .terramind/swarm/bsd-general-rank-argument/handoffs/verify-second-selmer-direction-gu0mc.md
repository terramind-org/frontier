Outcome: done
## Done

- Added `derived-localization-review.md`. Independent review of Castella, *Generalised Kato classes on CM elliptic curves of rank 2*, arXiv:2204.09608v3, confirms that Theorem C's x_p^(2) lies in the same Q_p Selmer group as kappa_p and has nonzero restriction, while kappa_p spans its restriction kernel. Hence the vectors are independent and form the stated basis under Theorem C's hypotheses.
- Confirmed hypothesis scope: CM E/Q, split p >= 5 (therefore ordinary), positive even complex order, Theorem B's valid Hecke-character data, finite p-primary Sha, and Katz p-adic orders 2 and 1. The source proves compatibility at theorem level and existence of suitable character triples; no numerical (E,p) verifies the full analytic/Sha package.
- Clarified arithmetic limit: the basis is in the p-adic Selmer group; finite Sha is assumed, and the result constructs neither an arbitrary-curve Kato/BF derivative nor an unconditional rational-rank lower bound. Corrected citation is pinned to v3 (last revised 13 Feb 2026).
- `bun run check` passed after `bun install`: TypeScript check, 434 tests passed, 1 skipped, 0 failed; validation reports 18,618 problems and 0 attempts. Initial check lacked installed `tsc`; installing project dependencies resolved it.

## Deviations

None.

## Concerns

The conditional hypotheses remain unverified for any specific curve and prime in this audit. The stated conclusion does not complete the swarm's unconditional BSD goal.

## Follow-ups

For arbitrary E/Q, construct and verify a second global class in the same ordinary Selmer group with nonzero restriction and simultaneously satisfied auxiliary hypotheses; separately control Sha to infer rational points.
