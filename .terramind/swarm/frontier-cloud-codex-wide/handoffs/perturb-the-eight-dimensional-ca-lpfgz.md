Outcome: done

## Done

- Recovered PR 130 / `30a492c1`, parsed r1--r11 ledgers to recover 36 prior frozen-assignment fingerprints, and rechecked the original 512-point fixture. Its SHA-256 is `eb991105b685d77e13acc0d8ae467b9f04db22ca30fb0b3d7a4d656f68a72bf5`; independent Frontier diagnose accepts it at 512, tying the known value.
- Kept original generator cursor 197 parked. Added a reproducible recorded-group substitution enumerator and ran it on CPU 0. It ranks recorded 12-anchor groups by recomputed eligible/deletion ratio with fingerprint tiebreak, then considers deterministic dropped-ID/added-ID substitutions only when the leading mixed slice and anchor mutual compatibility are preserved.
- Screened 48 substitutions from 47 recorded groups. All passed `125 * eligible > 60 * deletions`; 17 novel frozen assignments were exact restricted UNSAT and 31 were within-run fingerprint duplicates before solver work. There were 0 prior duplicates, yield/cardinality or mixed-invariant prunes, SAT candidates, and timeouts.
- All 17 novel cases passed planted/direct scanning and exhaustive 256-assignment encoding with zero mismatches. The positive-gain scanner control passed. The best directly verified cap remains 512; no 513-point candidate existed to scan or check with Frontier.
- Wrote evidence under `search/cap8-anchor-substitution-r1/`, including exact substitution cursor: base fingerprint `ed3a9b5bb4c2505f47b06aa9023d61354c0eb6499402b250efec039ef60931de`, dropped 2187, added 2919. Original seed cursor remains 197. `bun run check` passed: 434 passed, 1 skipped, 0 failed.

## Deviations

- The historical r6b manifest still has its previously recorded stale relative fixture path. I did not alter historical evidence; the current fixture and new ledger checksum verify.

## Concerns

- Exact UNSAT is restricted to each recorded frozen assignment and does not resolve the complete 813-optional pool.
- The first 48 substitutions are net-negative despite clearing the screening ratio; resume the substitution cursor rather than advancing the original generator.

## Follow-ups

- Resume `cap8-anchor-substitution-r1` from its exact dropped/added cursor with all r1--r11 and r1-substitution fingerprints, while keeping seed 197 parked.
- Independently direct-scan and run Frontier diagnose/check on any future 513+ candidate before making a claim.
