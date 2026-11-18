# r3 atomic recorded-group single substitutions

This continuation resumes only the r1/r2 single-anchor substitution family.
The original mixed-slice generator remains parked at seed **197**. It begins
at the reconciled next valid substitution `(ed3a9b5b..., 2187, 3891)`, ranks
the same 47 recorded 12-anchor groups by decreasing recomputed
eligible/deletion ratio and fingerprint tiebreak, and preserves the leading
slice and mutual-anchor compatibility for every mutation.

The CPU-0 batch screened 48 substitutions. It wrote one atomic JSON file in
`cases/` per classification before continuing, and then wrote the aggregate
ledger. There were 45 prior-fingerprint duplicates and three new exact
restricted UNSAT cases (added IDs 3982, 4131, and 4228); there were no
within-run duplicates, prunes, SAT outcomes, or timeouts. The next unvisited
cursor is `(ed3a9b5b..., 2187, 2674)`.

All cases retained the strict gate `125 * eligible > 60 * deletions`. The
planted and direct controls are valid; each new case passed the exhaustive
256-assignment direct-vs-clause check with zero mismatches, and the
positive-gain control passed. The vendored 512-point fixture has SHA-256
`eb991105b685d77e13acc0d8ae467b9f04db22ca30fb0b3d7a4d656f68a72bf5` and
independently diagnoses as valid with Frontier. No 513-point candidate was
emitted, so the directly verified size remains 512. These are results for
frozen restricted neighborhoods only, not the full 813-optional pool.
