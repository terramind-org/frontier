Outcome: done

## Done

- Recovered PR 115 / `67fa1b42`, the r1--r6b ledgers, cached boundary generator, and planted 512-point fixture. Fixture SHA-256 remains `eb991105b685d77e13acc0d8ae467b9f04db22ca30fb0b3d7a4d656f68a72bf5`; Frontier diagnose accepts it at 512, tying the best known value.
- Ran the deterministic 12-anchor continuation over seeds 157--164 on CPU 0 with the unchanged integer gate `125 * eligible > 60 * deletions`, loading 24 prior fingerprints before any solve. Every screened seed passed the gate; none was yield- or cardinality-pruned.
- Outcomes, recorded in deterministic completed-boundary order: seed 161 UNSAT (177 deletions, 133 eligible); 160 UNSAT (213, 155); 159 prior duplicate (213, 150); 164 UNSAT (212, 149); 157 prior duplicate (173, 121); 163 prior duplicate (213, 140); 162 UNSAT (197, 129); 158 UNSAT (196, 121). There were five exact restricted UNSAT cases, three prior duplicates, and zero SAT candidates, timeouts, same-run duplicates, yield prunes, or cardinality prunes.
- The best boundary in this batch was seed 161 at 133 eligible alternatives for 177 deletions. Best directly verified cap size remains 512. All five novel cases passed planted assignment and direct scanner checks, exhaustive 256-assignment direct-versus-clause checks with zero mismatches, and the positive-gain toy control.
- Preserved command, exact restart state, ledger, hashes, Frontier baseline scan, and repository gate under `search/cap8-witness-neighborhood-r7/`. Ledger SHA-256 is `fdbbe411e1195de3bd4712e3792c2b04d1b377e36520f4e706b2429425c7c34b`; next unvisited seed is 165. `bun run check` passed: 434 passed, 1 skipped, 0 failed.

## Deviations

- No 513-point candidate was decoded, so Frontier diagnose/check was required only for the planted 512-point fixture. No attempt scaffold or declaration was created or changed.

## Concerns

- Each UNSAT verdict is exact only for its fingerprinted restricted neighborhood with all other assignments frozen; it does not resolve the full 813-optional mixed pool.
- All tested boundaries remain net-negative: even the best 133/177 boundary exposes fewer alternatives than incumbent deletions.

## Follow-ups

- Resume at seed 165 with r1--r7 fingerprint deduplication, the cached completed-boundary calculation, and the same strict yield gate.
- If a future restricted model yields 513 or more points, independently scan it and run Frontier diagnose and check before making any claim.
