Outcome: done

## Done

- Recovered PR 128 / `00c79765`; verified r1--r9 ledgers, cached evaluator, mixed-pool screen, and the planted 512-point fixture. Fixture SHA-256 remains `eb991105b685d77e13acc0d8ae467b9f04db22ca30fb0b3d7a4d656f68a72bf5`; Frontier diagnose accepts it at 512, tying the known value.
- Continued the deterministic 12-anchor mixed-slice search at seeds 181--188 with the unchanged gate `125 * eligible > 60 * deletions`. Each completed seed has an atomic ledger, raw log, and SHA-256 sums; all sums verify.
- Full-ledger deduplication skipped seeds 181--184 and 186--188 before solver work. Seed 185 was the one novel boundary and was exact restricted UNSAT (197 deletions, 115 eligible alternatives, 312 variables, 46,684 line constraints). There were zero yield prunes, cardinality prunes, same-run duplicates, SAT candidates, and timeouts.
- The novel case passed planted/direct scanner controls, all 256 small direct-versus-encoding assignments with zero mismatches, and the positive-gain toy control. No 513-point witness was decoded, so candidate Frontier diagnose/check was not applicable. Best directly verified cap size remains 512; first unvisited seed is 189.
- Preserved compact reproducibility evidence at `search/cap8-witness-neighborhood-r10/`. `bun run check` passed: 434 passed, 1 skipped, 0 failed.

## Deviations

- The initial multi-seed shell command was interrupted after seed 184 while seed 185 was starting. No partial classification was retained; seed 185 was rerun as an independent atomic invocation before the batch continued.

## Concerns

- Each UNSAT result concerns only its fingerprinted restricted neighborhood with other assignments frozen. It does not resolve the complete 813-optional pool.
- The novel seed-185 boundary is net-negative: 115 eligible alternatives for 197 incumbent deletions.

## Follow-ups

- Resume at seed 189 with r1--r10 fingerprint deduplication and the same strict integer gate.
- Independently scan and run Frontier diagnose and check on any future 513+ candidate before making a claim.
