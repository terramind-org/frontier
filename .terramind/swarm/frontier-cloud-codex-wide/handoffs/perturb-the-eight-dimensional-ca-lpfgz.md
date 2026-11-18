Outcome: done

## Done

- Recovered PR 156 / `9963f256`; reconciled the r1--r6 aggregate ledgers,
  their checksums, and all 249 r7 atomic case files. r7's durable last item
  is `(734ade..., 2187, 2340)`, so `(734ade9f7438dc97e899e1a70bfd44b899a119badff06537dbf0159c141ca0ae, 2187, 2360)` was the first r8 classification, not a replay.
- Verified fixture SHA-256 `eb991105b685d77e13acc0d8ae467b9f04db22ca30fb0b3d7a4d656f68a72bf5`.
  Frontier diagnose accepts it as a valid 512-cap tying the known value. The original generator remains parked at seed 197.
- Ran r8 on CPU 0, retaining 54 atomic case files: 42 prior duplicates, 2
  within-run duplicates, and 10 new exact restricted UNSAT outcomes; no
  prunes, timeouts, or SAT candidates. Each novel result has planted/direct
  validity and zero mismatches in the exhaustive 256-assignment clause
  control; the evaluator's positive-gain control passes.
- No 513-point candidate was decoded, so candidate-level Frontier validation
  was not applicable. The new atomic-fingerprint loader prevents an
  interrupted batch such as r7 from being re-solved by a continuation.
- A one-item cursor probe, with r7 and r8 atomic cases loaded as prior work,
  establishes the exact next item as `(734ade9f7438dc97e899e1a70bfd44b899a119badff06537dbf0159c141ca0ae, 2187, 3464)`.
  `bun run check` passed: 434 passed, 1 skipped, 0 failed.

## Deviations

- The first invocation used an older anchor-deletion screen and failed its
  invariant assertion before classifying a case. The recorded mixed-pool
  screen (`7ed2e8...60bac`) was then used; it matches the 264-fixed /
  813-optional state.
- Stopped r8 after 54 durable atomic records rather than its 288-case ceiling
  to preserve a compact exact boundary. `CUTOFF.md` and the cursor probe
  record the continuation point; no incomplete aggregate ledger is presented
  as complete.

## Concerns

- This fibre still maps many different added anchors to identical deletion
  covers, frozen sets, optional sets, and fingerprints.
- Restricted UNSAT outcomes do not settle the complete 813-optional pool.

## Follow-ups

- Resume only the substitution family at `(734ade..., 2187, 3464)`, loading
  r1--r11, substitution r1--r6, and the atomic r7/r8 directories while
  keeping seed 197 parked.
- Independently direct-scan and run Frontier diagnose/check on any future
  513+ candidate before making a claim.
