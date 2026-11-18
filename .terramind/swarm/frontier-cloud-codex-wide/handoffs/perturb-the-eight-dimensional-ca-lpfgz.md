Outcome: done

## Done

- Recovered PR 121 / `467a97f7`; verified r1--r7 ledger hashes, the planted fixture, mixed-pool screen, and cached evaluator. The fixture SHA-256 is `eb991105b685d77e13acc0d8ae467b9f04db22ca30fb0b3d7a4d656f68a72bf5`; Frontier diagnose accepts the 512-point cap and reports a tie with the known value.
- Resumed deterministic 12-anchor mixed-slice search at seeds 165--172 on CPU 0. Each seed was separately checkpointed before the next began. The strict gate remained `125 * eligible > 60 * deletions`; every screened case passed it, so there were no yield or cardinality prunes.
- Deduplicated every fingerprint against r1--r7 and prior r8 checkpoints before solving. Seeds 165, 169, 171, and 172 were prior duplicates. Seeds 166 (201 deletions, 179 eligible, 380 variables, 68,610 constraints), 167 (173, 125, 298, 41,871), 168 (213, 162, 375, 67,298), and 170 (213, 152, 365, 63,829) were exact restricted UNSAT. There were no same-run duplicates, SAT candidates, or timeouts.
- All four novel cases passed the planted assignment, direct scanner, 256-assignment direct-versus-encoding control with zero mismatches, and positive-gain toy control. No 513-point candidate existed, so no candidate Frontier check was applicable. Best verified cap size remains 512.
- Preserved per-seed commands, raw outputs, ledgers, hashes, and resume state under `cap8-witness-neighborhood-r8/`; next unvisited seed is 173. `bun run check` passed: 434 passed, 1 skipped, 0 failed.

## Deviations

- The visible terminal interface failed before any command started; the same bounded one-core search was run through the workspace shell instead.

## Concerns

- Each UNSAT result applies only to its fingerprinted frozen neighborhood, not to the full 813-optional pool.
- The best r8 boundary is still net-negative: 179 eligible alternatives for 201 incumbent deletions.

## Follow-ups

- Resume at seed 173 with r1--r8 checkpoint fingerprints and the unchanged strict gate.
- Independently scan and run Frontier diagnose/check on any future 513+ candidate before making a claim.
