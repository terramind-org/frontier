Outcome: done

## Done

- Recovered PR 77 commit `02414cf818e8bb51f929990e817981049a652406` and matched its saved cursor exactly: the vendored 512-point fixture has SHA-256 `eb991105b685d77e13acc0d8ae467b9f04db22ca30fb0b3d7a4d656f68a72bf5`, slices `192/160/160`, fixed count 488, and the same twelve lexicographically first deletions in each mutable slice. This ran on host `modal`, with `taskset -c 0`.
- Re-verified the baseline with Frontier. `frontier diagnose` reports value 512, valid yes, and ties the known value; output is in `search/cap8-expanded-insert-sat/diagnose-baseline.txt`.
- Added the independent Boolean/cardinality experiment `search/cap8_expanded_insert_sat.py`. It uses a deterministic Boolean DPLL solver with native cardinality propagation rather than the earlier SciPy/HiGHS PB model, and encodes every remaining variable-containing affine line as an exact at-most-two clause.
- Expanded each allowed insertion pool to the complete coordinate slice: all 2,027 nonbaseline points in each mutable slice (Hamming radius 7 from the saved deletion seed). Every one is screened against every fixed-point pair. The reproducible certificates are in `full-slice/screen.json`: 2,027 exclusions per slice, each with its blocking pair; no insertion survives.
- The resulting Boolean/cardinality instance has 24 retained-deletion variables, zero line clauses, 488 fixed points, and needs 25 selected variables for total size at least 513. It is conclusively `UNSAT`, not timeout, at the root node in 0.000022 s. This is a cardinality contradiction: at most 24 variables can be selected.
- Positive baseline and small exhaustive controls passed: direct baseline validity and planted line-clause recovery are true; the 256-assignment small-window direct check and encoding agree with zero mismatches. Raw events, exact clauses, screen, controls, environment, command output, hashes, and cursor are retained in `search/cap8-expanded-insert-sat/full-slice/`. Key hashes: script `0fcd5f1c4b5f220b151fef3003207452321020178ded28d935efd6309c58167c`, screen `0d237c71a38ea460940e60312b90f9c9f87bf234aa664032ee103ae588db2884`, result `be7acff6e7db159a6bff3ddccfaf781c6cf829f8cc5229e608af45fc56d27320`.
- No candidate exists in this window, so no candidate Frontier check or diagnose was applicable. No attempt was created or submitted, and no declarations changed.

## Deviations

- The initial radius-4 control run was stopped after 48 seconds because its direct-control implementation redundantly rescanned fixed/fixed pairs. Its partial raw screen is retained. I corrected the control to factor out the known-valid fixed set, then ran the requested expanded full-slice screen. The final decisive run completed before the 30-minute deadline, so no alternate deletion pool was required by the fixed-core-exhaustion condition.
- No external SAT package was installed. The retained solver is an independent, deterministic Boolean DPLL/cardinality implementation whose clauses and raw event stream are included for replay.

## Concerns

- This proves only that the saved 24-deletion configuration admits no *single* insertion in either mutable coordinate slice while the other 488 points stay fixed. It does not rule out a larger simultaneous deletion/replacement or a cap above 512.
- The full-slice certificate is large but intentionally explicit: each exclusion names one fixed blocking pair, allowing a straightforward independent check without trusting the screening code.

## Follow-ups

- Use a different deterministic deletion pool (rather than growing the now-exhausted insertion pools) and repeat the same complete fixed-pair screen.
- For a deletion pool yielding survivors, cross-check this Boolean encoding with a standalone SAT/PB implementation before interpreting any SAT result.
