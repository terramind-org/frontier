Outcome: done
## Done

- Recovered the separate c8 SQLite ledger from PR 148 commit `2265e9b6`. Before resuming, its SHA-256 matched `f063b29ab0b188379dea0e1fd5e74435f1e9bd6facb59ac54fe1752d0e7af1b0`; SQLite `quick_check(1)` returned `ok`; counts were exactly 9,838,037 `pruned` and 1,123,595 `unvisited`, with zero `exhaustive`, `timeout`, or candidate rows. The first unvisited key exactly matched `8,29,43,55,69,92,170,260,261,342,408,426,459,466,492`.
- Revalidated immutable metadata: Station Construction 3 fixture SHA-256 `61b3a572ad194a3b97d8bcae8694d57ae676328a81ef0e4db95e57a2c9d44f37`; 5,156-direction ordering SHA-256 `c5f42ea6ceada60c9465564f4771d9b8fe1ab95179a96ed43e8a98c12cd327ad`; pair cursor 5,156; and 10,961,632 unique pairs/pools. This remains separate from c4's unverified 5,120-direction claim.
- Resumed only durable lexical `unvisited` rows, with no pair regeneration. The single SQLite writer completed the remaining frontier in 632.298 seconds. The source retained the planted K4 and exhaustive 32,768 labelled six-vertex clique controls, and independently compared the integer-mask blocker predicate to the original set predicate on 32 lexical pools.
- At exhaustion, all 10,961,632 pools are durably `pruned` by the sound bound `eligible replacements <= deleted rows`; there are zero `unvisited`, `exhaustive`, `timeout`, or candidate rows. Final `quick_check(1)` is `ok`; final ledger SHA-256 is `3199c1886f168ed44da96759dbd4853e428471576c451291171a1333d843f70c`. The multi-GB ledger remains outside Git. Compact wrapper, raw output, and summary are retained in `.terramind/scratch/kissing11-c9/`.
- Created a clean detached checkout at the same `2265e9b6` checker revision to isolate the inherited dangling attempt reference. The recovered public 604-vector certificate was encoded into a disposable scaffold with both declarations still false; `bun frontier diagnose` reported valid and tying the known value, and `bun frontier check` reported a valid 604-vector witness tying the known bound. The disposable checkout was not committed.
- No pool had more eligible replacements than deletions, so the exact clique branch never ran and no 605+ witness or candidate scan was applicable.

## Deviations

- Used SQLite `quick_check(1)`, rather than the longer full `integrity_check`; it completed cleanly before and after exhaustion.

## Concerns

- This exhausts only the reconstructed 5,156-direction candidate-pair / size-13--20 blocker-union family; it is not an upper bound on 11-dimensional kissing configurations and must not be combined with c4's unverified 5,120 count.
- The exact clique branch was not reached because every pool met the cardinality prune; no direct statement about broader exchange families follows.

## Follow-ups

- Try a non-overlapping shell or a higher-order exchange family; preserve exact checks and independently validate any 605+ witness.
- Recover/audit c4 independently before comparing its 5,120 filter with this 5,156-direction reconstruction.
