Outcome: done

## Done

- Recovered PR 107 / `4d34c06f`, verified its frozen-assignment ledger, and rechecked the planted 512-point fixture. The fixture SHA-256 is `eb991105b685d77e13acc0d8ae467b9f04db22ca30fb0b3d7a4d656f68a72bf5`; Frontier diagnose accepts it and reports a tie with the best known value.
- Extended the deterministic search at seeds 145--148 using 12-anchor groups biased to shared mutable blocker endpoints. The generator now compares yields with exact integer arithmetic and expands only when `eligible * 125 > 60 * deletions`; it separately counts screened yield-prunes, duplicates, cardinality prunes, exact UNSAT, SAT, and timeouts.
- All four screened boundaries exceeded the benchmark. Three were novel and exact restricted UNSAT; seed 146 was an in-run duplicate of seed 145. There were no yield/cardinality prunes, prior duplicates, SAT candidates, or timeouts. Best verified size remains 512.
- The best new boundary was seed 147: 12 anchors, 201 deletions, 182 eligible alternatives (strictly above 60/125), with 383 variables. Each novel case retained the 264 fixed points and passed planted/direct and 256-assignment direct-versus-clause controls with zero mismatches; the positive-gain toy control also passed.
- Saved compact hashes, ledger, raw run record and repository-check result under `search/cap8-witness-neighborhood-r5/`. The exact next cursor is seed 149. `bun run check` passed: 434 passed, 1 skipped, 0 failed.

## Deviations

- No candidate reached 513, so Frontier diagnose/check was applicable only to the planted 512-point fixture, not to a new witness.

## Concerns

- Restricted UNSAT is scoped only to its fingerprinted frozen assignment. It does not exclude the full 813-variable mixed pool.
- The best 12-anchor boundary improves the screening ratio but still deletes more incumbent optionals than it exposes, so this family has not produced a net gain.

## Follow-ups

- Resume at seed 149, retaining all r1--r5 fingerprints, and evaluate larger groups only when their actual boundary yield strictly exceeds 60/125.
- Independently scan and run Frontier diagnose/check on any future 513+ decoded candidate.
