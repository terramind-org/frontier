Outcome: done

## Done

Recovered PR 100 commit `adeb3d10` locally and validated the c3 compact
manifest from its own directory; every retained object matched. Reused the
pinned 77-comparator baseline (SHA-256
`ec66245d95a80562ca1a14d05e2650267d38c2d7d20d4b74df422d482c2c23bd`).

`[57,68) -> 10`, seed `5711`, is fresh and non-implied by every certified
window in the complete ledger because it starts before `[59,71)`. Its initial
CNF included all 90 reachable prefix states (21,150 variables; 987,517
clauses). On one CPU CaDiCaL returned UNSAT in 78.711s; the external
600-second supervisor exited 0. Independent DRAT-trim exited 0, reported `s
VERIFIED`, and took 33.374s.

The compact replay bundle is `.terramind/scratch/sort18-c4-recovery/`: it
contains the losslessly compressed CNF and DRAT, encoder, baseline, commands,
timestamps, solver/checker exits and logs, decompression hashes, and a checked
manifest. No 76-comparator candidate was produced. `[58,70)`, `[59,75)`, and
`[42,54)` remain unresolved.

## Deviations

The requested c4 branch name was already occupied locally by an unrelated
older branch. To preserve it, this work used
`swarm/frontier-cloud-codex-wide--resynthesize-interior-sorting-ne-ve95w-c4-recovery`
from the requested c3 commit.

## Concerns

This certificate excludes only a 10-gate replacement for the fixed `[57,68)`
window of this particular 77-gate baseline. It is not a global lower bound.

## Follow-ups

Select a fresh, non-implied interval that extends outside `[57,68)` and the
other certified exterior windows; retain the same complete-prefix-state and
independent-proof-replay discipline.
