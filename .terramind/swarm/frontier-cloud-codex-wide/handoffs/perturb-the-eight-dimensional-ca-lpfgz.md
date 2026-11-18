Outcome: done

## Done

- Recovered PR 125 / `27b35c13`; verified the r1--r8 ledgers, cached evaluator, mixed-pool screen, and planted 512-point fixture. The fixture SHA-256 remains `eb991105b685d77e13acc0d8ae467b9f04db22ca30fb0b3d7a4d656f68a72bf5`; direct Frontier diagnose accepts it at 512, tying the known value.
- Continued the deterministic 12-anchor mixed-slice search at seeds 173--180, with the unchanged exact gate `125 * eligible > 60 * deletions`. Each seed was a separate CPU-0 invocation and atomically checkpointed with raw log, ledger, and SHA-256 sums before the next began.
- Loaded r1--r8 fingerprints and completed-r9 fingerprints before each solve. Seeds 173 (215 deletions, 160 eligible, 375 variables, 67,334 line constraints) and 175 (197, 127, 324, 50,504) were exact restricted UNSAT. Seeds 174, 176, 177, 178, 179, and 180 were prior duplicates, detected before solver work. There were zero yield prunes, cardinality prunes, same-run duplicates, SAT candidates, and timeouts.
- Both novel cases passed planted/direct scanner controls, all 256 small direct-versus-encoding assignments with zero mismatches, and the positive-gain toy exchange. No 513-point witness was decoded, so candidate Frontier check was not applicable. Best directly verified cap size remains 512.
- Preserved compact, reproducible evidence at `search/cap8-witness-neighborhood-r9/`; first unvisited seed is 181. `bun run check` passed: 434 passed, 1 skipped, 0 failed.

## Deviations

- None.

## Concerns

- Each UNSAT result concerns only its fingerprinted restricted neighborhood with other assignments frozen. It does not resolve the complete 813-optional pool.
- Both new boundaries are net-negative: they expose fewer eligible alternatives than incumbent deletions.

## Follow-ups

- Resume at seed 181 with r1--r9 fingerprint deduplication and the same strict integer gate.
- Independently scan and run Frontier diagnose and check on any future 513+ candidate before making a claim.
