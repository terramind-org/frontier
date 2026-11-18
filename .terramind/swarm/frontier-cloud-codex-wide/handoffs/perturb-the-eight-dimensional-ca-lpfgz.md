Outcome: done

## Done

- Recovered PR 143 / `386b0b7c`; verified r1–r11 fingerprints, substitution r2 ledger/cursor, cached evaluator inputs, deterministic order, and the original 512-point fixture. Its SHA-256 remains `eb991105b685d77e13acc0d8ae467b9f04db22ca30fb0b3d7a4d656f68a72bf5`; Frontier diagnose accepts it at 512.
- Kept original generator seed cursor 197 parked. Reconciled and began exactly at `(ed3a9b5bb4c2505f47b06aa9023d61354c0eb6499402b250efec039ef60931de, 2187, 3891)`.
- Ran a CPU-0, 48-case substitution batch in 180 seconds. Each classified substitution has an atomic checkpoint under `search/cap8-anchor-substitution-r3/cases/` before the aggregate ledger is written. The batch had 45 prior duplicates and three new exact restricted UNSAT cases (added IDs 3982, 4131, 4228); no within-run duplicates, mixed/cardinality/yield prunes, SAT, or timeouts.
- All cases preserved compatibility and mixed-slice constraints and cleared `125 * eligible > 60 * deletions`. The three novel cases passed planted/direct, exhaustive 256-assignment encoding (zero mismatches), and positive-gain controls. No 513-point candidate was decoded, so no candidate Frontier diagnose/check was applicable. Best directly verified cap size remains 512.
- Recorded raw run log, per-case checkpoints, ledger checksum `e8de3d7e4708b9df995e8fba4a17f0f3c078ac6271df2e3467016881e85369e2`, fixture diagnosis, and repository gate under `search/cap8-anchor-substitution-r3/`. `bun run check` passed: 434 passed, 1 skipped, 0 failed.
- Next substitution cursor is `(ed3a9b5bb4c2505f47b06aa9023d61354c0eb6499402b250efec039ef60931de, 2187, 2674)`.

## Deviations

- Added atomic per-substitution checkpoint files to the continuation evaluator because prior substitution batches only persisted at aggregate-batch completion.

## Concerns

- Exact UNSAT applies only to each frozen restricted neighborhood and does not resolve the complete 813-optional pool.

## Follow-ups

- Resume only the substitution family at the recorded r3 cursor, loading r1–r11 plus r1–r3 fingerprints, while leaving seed 197 parked.
- Independently direct-scan and run Frontier diagnose/check on any future 513+ candidate before making a claim.
