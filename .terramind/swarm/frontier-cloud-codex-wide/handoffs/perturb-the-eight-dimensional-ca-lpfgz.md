Outcome: done

## Done

- Recovered PR 145 / `19c45c37`; verified r3 ledger SHA-256
  `e8de3d7e4708b9df995e8fba4a17f0f3c078ac6271df2e3467016881e85369e2`,
  all 48 r3 atomic case checkpoints, prior fingerprints, deterministic
  ordering, cached evaluator inputs, and the vendored 512-point fixture.
- Kept original generator seed 197 parked.  Reconciled r3's first-unvisited
  next-item cursor exactly at `(ed3a9b5bb4c2505f47b06aa9023d61354c0eb6499402b250efec039ef60931de, 2187, 2674)`.
- Ran two disjoint CPU-0 batches in recorded order.  r4 checkpointed 48
  prior duplicates (ledger SHA-256
  `18cb50aa26bfe08df9143af301fc90a56192e3d4d82f02f6c7886fd025f21670`),
  then r5 checkpointed 48 more prior duplicates (ledger SHA-256
  `1162ea94855279a847be8525bac5924e056e3b3b2bbd5d48e58c495203a3ef19`).
  Neither batch reached a solver: no prunes, within-run duplicates,
  restricted SAT/UNSAT outcomes, or timeouts.
- The r5 next unvisited cursor is `(ed3a9b5bb4c2505f47b06aa9023d61354c0eb6499402b250efec039ef60931de, 2187, 2340)`.
  All retained cases preserve compatibility, mixed-slice constraints and the
  strict yield gate.  Ledger controls report planted/direct validity and
  positive gain; no 513-point witness was decoded.
- Frontier independently diagnoses the vendored fixture as a valid 512-cap
  tying the known value.  `bun run check` passed: 434 passed, 1 skipped, 0 failed.


## Deviations

- None.

## Concerns

- The last 96 stream entries all collapsed to already-covered frozen
  assignments before solver entry; continuation should retain cursor order,
  not switch to numeric ID order.
- Restricted outcomes, when reached, apply only to frozen neighborhoods and
  do not resolve the complete 813-optional pool.

## Follow-ups

- Resume only the substitution family at the recorded r5 cursor `(ed3a..., 2187, 2340)`, loading r1--r11 plus r1--r5 fingerprints and leaving seed 197 parked.
- Independently direct-scan and run Frontier diagnose/check on any future 513+ candidate before making a claim.
