Outcome: done

## Done

- Recovered PR 102 / `180766f3` and re-verified the saved mixed-pool scope: 264 fixed points, 813 optional choices, 248 planted optionals, and target 249 optionals for total 513. The stored 512-point fixture passed Frontier diagnose (`valid: yes`, ties the known value).
- Extended the deterministic witness-directed search at seed 137 using eight-anchor groups. The updated generator first evaluates each full restricted boundary and prioritizes eligible alternatives per incumbent deletion, then records all prior- and same-run frozen-assignment duplicates rather than silently skipping them.
- The r4 ledger covers seeds 137--144. Seven distinct frozen assignments were exact restricted UNSAT; seed 144 duplicated seed 139 within this run. There were no cardinality-pruned cases, solver timeouts, SAT candidates, or 513-point witnesses. Best independently scanned size remains 512.
- The highest-yield boundary was seed 138: 8 anchors, 125 deletions, 60 eligible alternatives, 185 variables and 16,561 exact line constraints (0.480 alternatives per deletion). All solved cases retained the 264 fixed points; their solver times were 0.027--0.068 seconds after deterministic boundary generation.
- Repeated controls in the recorded ledger: direct scan of baseline and planted assignment, 256 direct-versus-clause assignments per nonduplicate case (zero mismatches), and a valid positive-gain toy exchange from 1 to 2 points. The exact run was CPU-pinned to core 0, from `2026-11-18T16:12:02Z` to `2026-11-18T16:18:29Z`; next deterministic cursor is seed 145.
- Saved hashes, Frontier baseline output, ledger, raw run log and repository-check output under `search/cap8-witness-neighborhood-r4/`. `bun run check` passed: 434 passed, 1 skipped, 0 failed.

## Deviations

- No candidate reached 513, so Frontier diagnose/check was applicable only to the planted 512-point fixture, not to a new witness.

## Concerns

- Restricted UNSAT is scoped only to its fingerprinted frozen assignment. It does not exclude the full 813-variable mixed pool.
- Even the best eight-anchor boundary removes more incumbent optionals than it exposes, so this family has not produced a net gain.

## Follow-ups

- Resume at seed 145, retaining all r1--r4 fingerprints, and evaluate larger groups only when their actual boundary yield exceeds the r4 60/125 benchmark.
- Independently scan and run Frontier diagnose/check on any future 513+ decoded candidate.
