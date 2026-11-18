Outcome: done

## Done

- Recovered PR 137 / `5c780c0b`; verified the r1--r11 fingerprints, deterministic base ordering, cached evaluator inputs, and vendored 512-point fixture. Its SHA-256 is `eb991105b685d77e13acc0d8ae467b9f04db22ca30fb0b3d7a4d656f68a72bf5`; Frontier diagnose accepts it at 512.
- Kept original generator cursor 197 parked. Updated the substitution enumerator to reconcile a checkpoint against the compatibility-filtered deterministic stream and to fail if missing; continuation fingerprints now deduplicate without being allowed to change the 47 recorded base groups or their r1 ordering.
- Reconciled and started exactly at base fingerprint `ed3a9b5bb4c2505f47b06aa9023d61354c0eb6499402b250efec039ef60931de`, dropped 2187, added 2919. It is r2's first processed case and was a prior duplicate. The CPU-0 batch screened 48 substitutions in 541 seconds: 12 novel exact restricted UNSAT, 34 prior duplicates, and 2 same-run duplicates; no yield/mixed-invariant/cardinality prunes, SAT candidates, or timeouts.
- All novel cases passed planted/direct scanning and exhaustive 256-assignment encoding with zero mismatches; the positive-gain scanner control passed. No 513-point candidate existed to scan or check with Frontier. The best directly verified cap remains 512.
- Wrote reproducibility evidence under `search/cap8-anchor-substitution-r2/`; ledger SHA-256 is `32d715359a9466666c2bb3014279ab8e7e057b78bbb444fc72596f1a4ae87d6f`. The exact next substitution cursor is the same base and dropped IDs with added 3891.
- `bun run check` passed: 434 passed, 1 skipped, 0 failed.

## Deviations

- The historical r6b manifest still has its previously recorded stale relative fixture path. I did not alter historical evidence; the current fixture and new ledger checksum verify.

## Concerns

- Exact UNSAT is restricted to each recorded frozen assignment and does not resolve the complete 813-optional pool.
- The r2 substitutions remain net-negative despite clearing the screening ratio; resume the substitution cursor rather than advancing the original generator.

## Follow-ups

- Resume `cap8-anchor-substitution-r2` from base `ed3a9b5bb4c2505f47b06aa9023d61354c0eb6499402b250efec039ef60931de`, dropped 2187, added 3891, with r1--r11 as fixed base groups and both r1/r2 as dedup-only ledgers; keep seed 197 parked.
- Independently direct-scan and run Frontier diagnose/check on any future 513+ candidate before making a claim.
