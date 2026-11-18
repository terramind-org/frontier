Outcome: done

## Done

- Recovered PR 111 / `7555726f`, retained the r1--r5 fingerprint ledger, and verified the vendored planted cap. Fixture SHA-256 is `eb991105b685d77e13acc0d8ae467b9f04db22ca30fb0b3d7a4d656f68a72bf5`; Frontier diagnose accepts it at 512, tying the known value.
- Resumed the deterministic 12-anchor mixed-slice search at seeds 149--156. Every expansion used the strict integer gate `125 * eligible > 60 * deletions`; prior and same-run fingerprints were checked before solver invocation.
- Screened eight cases: six novel exact restricted UNSAT, one prior duplicate (seed 156, matching the prior seed-147 fingerprint), and one same-run duplicate (seed 153, matching seed 150). There were no yield/cardinality prunes, SAT candidates, or timeouts. Best verified cap size remains 512.
- The strongest boundary was seed 156 (a duplicate): 201 deletions and 182 eligible alternatives. Among novel cases, seed 149 exposed 149 alternatives for 213 deletions. All novel cases passed the planted assignment, direct scanner, 256-assignment direct-versus-encoding controls with zero mismatches, and the positive-gain toy control.
- Cached each completed-boundary calculation before deterministic ordering, preventing repeated full blocker scans while preserving generator order and output. Saved hashes, run log, ledger, fixture check, and repository gate under `search/cap8-witness-neighborhood-r6b/`; next unvisited seed is 157. `bun run check` passed: 434 passed, 1 skipped, 0 failed.

## Deviations

- An initial 16-seed run was stopped before it produced a ledger because its repeated boundary-yield sorting consumed the handoff budget; it made no claims and is not committed. The cache was then added and the completed eight-seed checkpointed run used the same inputs, ordering, gate, and one-core limit.
- No candidate reached 513, so Frontier diagnose/check applied only to the planted 512-point fixture.

## Concerns

- Restricted UNSAT is limited to each recorded frozen fingerprint and does not exclude the full 813-variable mixed pool.
- All completed boundaries continue to delete more incumbent optionals than they expose, so this family has not produced a net exchange.

## Follow-ups

- Resume at seed 157 with all r1--r6b fingerprints and the unchanged strict gate; retain every cursor and classification before broadening the group family.
- Independently scan and run Frontier diagnose/check on any future 513+ decoded candidate.
