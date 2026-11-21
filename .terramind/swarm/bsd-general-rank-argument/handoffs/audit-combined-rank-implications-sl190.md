Outcome: done
## Done
Created `audit.md`, comparing both rank inequalities for arbitrary (E/\mathbb Q). It states the exact Selmer-corank and rational-point/height-matrix gaps, explains why the available p-adic main-conjecture and higher-derived-class results do not close them, records the rank-zero/one scope, and checks for circular use of BSD or Sha finiteness. Verified theorem scope against the primary Skinner–Urban manuscript and the cited primary papers/preprints (Gross–Zagier, Kolyvagin, Castella et al., Castella–Hsieh; bibliographic DOI for Mazur–Tate–Teitelbaum verified). No full unconditional proof for all (E/\mathbb Q) is established or known from the checked sources; the requested all-curve claim remains open.

Ran `bun run check`: passed TypeScript checking, all 434 tests (1 skipped), and catalog validation (`ok: 18618 problems, 0 attempts`). The initial attempt lacked installed dependencies; after `bun install`, the full check passed. This is a documentation-only task; no Lean checks were relevant.

## Deviations
The task requested reading the prior swarm `iwasawa.md` and `higher-rank.md`, but neither is present in this worktree. I did not access other workers' directories. I used the available `upper.md`, `lower.md`, and their cited sources, and recorded this limitation in `audit.md`.

## Concerns
None beyond the absent prior-note files. The conclusion is that weak BSD is open in general; it is not a claim that a counterexample exists.

## Follow-ups
None.
