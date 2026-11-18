# r2 resumed recorded-group single substitutions

This batch continues only the r1 single-anchor substitution family. The original mixed-slice generator remains parked at seed **197**. It used the same 47 r1 base groups, ranked by decreasing recomputed eligible/deletion ratio and fingerprint tiebreak; r1 itself was loaded only as a dedup ledger, so completed substitutions cannot alter base-group ordering.

The checkpoint cursor was reconciled against the valid (leading-slice and mutual-compatibility filtered) enumeration before any work: base fingerprint `ed3a9b5bb4c2505f47b06aa9023d61354c0eb6499402b250efec039ef60931de`, dropped `2187`, added `2919`. It was found and processed as the first r2 case; it is a prior-fingerprint duplicate, not a replayed solve. The 48-case CPU-0 batch ran for 541 seconds. Its next unvisited cursor is the same base and dropped IDs with added `3891`.

All substitutions retained leading-slice and mutual-anchor compatibility, recomputed deletion covers and eligibility, passed `125 * eligible > 60 * deletions`, and were deduplicated before solver entry. The batch had 12 novel exact restricted UNSAT cases, 34 prior duplicates, and 2 within-batch duplicates; it had no prunes, SAT outcomes, or timeouts. Novel cases pass planted/direct and 256-assignment direct-vs-clause controls; the positive-gain control passes. These are frozen-neighborhood results only. No 513-point witness was emitted, and the directly verified size remains 512.

Inputs were the vendored fixture (`eb991105b685d77e13acc0d8ae467b9f04db22ca30fb0b3d7a4d656f68a72bf5`), the cached mixed-pool screen, and all r1--r11 ledgers. `run.log` gives the raw outcome and measured wall time; `SHA256SUMS` hashes `ledger.json`.
