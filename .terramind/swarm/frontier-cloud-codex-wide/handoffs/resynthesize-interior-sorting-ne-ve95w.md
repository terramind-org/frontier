Outcome: done

## Done

Created branch `swarm/frontier-cloud-codex-wide--resynthesize-interior-sorting-ne-ve95w-c3` and recovered c2 commit `0361a993`. Its compact manifest validates from `.terramind/scratch/sort18-c2/`. The reused baseline SHA-256 is `ec66245d95a80562ca1a14d05e2650267d38c2d7d20d4b74df422d482c2c23bd`; Frontier diagnosis accepted it on all 262,144 binary inputs at 77 comparators.

`[59,71) -> 11`, seed `5912`, is fresh and not implied by `[60,72)`, `[61,73)`, or `[62,74)` because it extends left of them. Its complete initial CNF contains all 68 reachable prefix states (17,385 variables; 851,433 clauses). On one CPU, CaDiCaL returned UNSAT in 301.598 seconds and the external 600-second supervisor exited 0. Independent DRAT-trim exited 0 with `s VERIFIED` in 127.339 seconds.

The early completion allowed a second fresh outward lane: `[58,70) -> 11`, seed `5812`. Its complete initial CNF contains all 78 reachable prefix states (19,821 variables; 957,551 clauses), but its external supervisor exited 124 at 600 seconds without a solver result. It is unresolved, not UNSAT.

Compact artifacts, commands, logs, exits, compressed CNFs/proof, encoder, baseline, and a validating hash manifest are under `.terramind/scratch/sort18-c3/`. Lossless decompression reproduced every recorded CNF/proof hash before uncompressed copies were excluded. No SAT model or 76-comparator candidate was produced. `[59,75)` and `[42,54)` remain unresolved.

## Deviations

None.

## Concerns

The new certificate excludes only an 11-gate replacement in the fixed `[59,71)` window of this baseline; it is not a global lower bound. `[58,70)` is an incomplete timeout and supplies no exclusion.

## Follow-ups

Choose a fresh interval that extends outside `[59,71)`, `[60,72)`, `[61,73)`, and `[62,74)`. Retain complete-prefix-state encodings and independently replay every UNSAT certificate.
