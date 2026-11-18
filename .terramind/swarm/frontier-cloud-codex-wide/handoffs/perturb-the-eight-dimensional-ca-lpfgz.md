Outcome: done

## Done

- Recovered PR 147 / `ed124f4b`; verified r4/r5 ledgers, all 96 atomic case
  files, prior fingerprints, recorded ordering, cached evaluator inputs, and
  the original fixture.  The fixture SHA-256 remains
  `eb991105b685d77e13acc0d8ae467b9f04db22ca30fb0b3d7a4d656f68a72bf5`;
  Frontier diagnose accepts it at 512, tying the known value.
- Kept original seed 197 parked and resumed exactly at r5's next item
  `(ed3a9b5bb4c2505f47b06aa9023d61354c0eb6499402b250efec039ef60931de, 2187, 2340)`.
  r6 atomically classified 192 cases in 229 seconds: all were prior
  frozen-assignment duplicates.  Its ledger SHA-256 is
  `220b3d865ac85b71b65e90a184398a6389a12f5ba68a889d36d2062ae0773228`;
  its next cursor was `(ed3a..., 2187, 4133)`.
- Streamed beyond that duplicate block into r7 and retained 249 atomic case
  records before a deliberate cutoff: 228 prior duplicates, 11 within-run
  duplicates, and 10 new exact restricted UNSAT results; no prunes, timeouts,
  or SAT candidates.  Novel cases passed planted/direct and exhaustive
  256-assignment controls with zero mismatches; no 513-point witness existed
  to diagnose or check.
- The r7 exact next unvisited cursor is
  `(734ade9f7438dc97e899e1a70bfd44b899a119badff06537dbf0159c141ca0ae, 2187, 2360)`.
  The preceding base/drop fibre has 110 compatible additions, and its varied
  point IDs often generate identical frozen assignments because the deletion
  cover is identical.
- `bun run check` passed: 434 passed, 1 skipped, 0 failed.

## Deviations

- Cut r7 after its 249th atomic checkpoint rather than completing its planned
  384-case aggregate ledger, because the new fibre was much slower to screen.
  `CUTOFF.md` records the counts, raw boundary, and exact reconstructed next
  cursor; no partial aggregate ledger is presented as complete.

## Concerns

- The substitution family has large many-to-one fibres: different anchors can
  yield the same deletion cover, frozen set, optional set, and fingerprint.
- Restricted UNSAT results do not resolve the complete 813-optional pool.

## Follow-ups

- Resume only the substitution family from the r7 cursor `(734ade..., 2187,
  2360)`, loading all r1--r11 and r1--r6 fingerprints plus r7 atomic cases;
  keep seed 197 parked.
- Independently direct-scan and run Frontier diagnose/check on any future
  513+ candidate before making a claim.
