Outcome: done

## Done

- Recovered PR 158 / `bdd94258`; reconciled all original r1--r11 witness
  ledgers, substitution r1--r6 ledgers, 249 r7 atomic cases, and 54 r8 atomic
  cases. The matching screen SHA-256 is `7ed2e8b2a4caec32f242a60d461f2d41df706df5ba8d23109997c88d17260bac`,
  evaluator SHA-256 is `52e21e4ade6c47af3d129ae101e77a767018a72a39e6b2f94e5ee17f2493c836`,
  and the r8 cursor probe places `(734ade..., 2187, 3464)` as the first r9 item.
- Verified the planted fixture SHA-256 `eb991105b685d77e13acc0d8ae467b9f04db22ca30fb0b3d7a4d656f68a72bf5`.
  Frontier diagnose accepts it as a valid 512-cap tying the known value. Seed
  cursor 197 remains parked.
- Ran r9 on CPU 0 for 597 seconds, retaining 96 atomic case files: 81 prior
  duplicates, 3 within-run duplicates, and 12 exact restricted UNSAT results;
  no prunes, timeouts, or SAT candidates. Every novel case passed
  planted/direct validity, the exhaustive 256-assignment encoding control,
  and the positive-gain control while preserving the strict yield gate.
- No 513-point witness was decoded, so no candidate-level Frontier diagnose
  or check was applicable. The exact first unvisited cursor is
  `(734ade9f7438dc97e899e1a70bfd44b899a119badff06537dbf0159c141ca0ae, 2187, 3220)`.
  `bun run check` passed: 434 passed, 1 skipped, 0 failed.

## Deviations

- An initial r9 invocation omitted nested r8--r11 witness ledgers and failed
  closed before classifying any case. The completed `r9b` batch discovers all
  witness ledgers recursively; no failed-run checkpoint is used as evidence.

## Concerns

- This fibre still maps many different added anchors to identical deletion
  covers, frozen sets, optional sets, and fingerprints.
- Restricted UNSAT outcomes do not settle the complete 813-optional pool.

## Follow-ups

- Resume only the substitution family at `(734ade..., 2187, 3220)`, loading
  r1--r11, substitution r1--r6, and the atomic r7/r8/r9b directories while
  keeping seed 197 parked.
- Independently direct-scan and run Frontier diagnose/check on any future
  513+ candidate before making a claim.
