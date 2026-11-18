Outcome: done

## Done

Recovered PR 127 commit `a9bd666a` and validated the c6 replay bundle.  Its
tracked manifest entries matched; reassembling its eight proof chunks produced
the recorded compressed digest, and decompressing its CNF and DRAT produced
the recorded raw-object digests.  The pinned 77-comparator baseline matched
SHA-256 `ec66245d95a80562ca1a14d05e2650267d38c2d7d20d4b74df422d482c2c23bd`.
The c6 equality guard was retained unchanged.

`[53,64) -> 10`, seed `5311`, is fresh and non-implied by the complete
certified exterior-window ledger: it starts before the previously certified
`[54,65)` interval.  The pinned baseline passed Frontier diagnosis on all
262,144 binary inputs.  Before solving, vectorised enumeration, independent
scalar enumeration, and the actual encoded set each contained 120 prefix
states and shared SHA-256
`dd23ade8025422f11898342f16c32de9e60e370b531033d86c53d642dd8e29a0`.
The complete initial CNF has 28,590 variables and 1,279,267 clauses.

On one CPU CaDiCaL returned UNSAT in 243.499s under a 600s external
supervisor (exit 0).  Independent DRAT-trim replay exited 0, reported
`s VERIFIED`, and took 204.421s.  `.terramind/scratch/sort18-c7/` retains the
baseline, equality-auditing encoder, exact commands, timestamps, logs, exit
codes, compressed CNF, digest manifests, reassembly instructions, and six
lossless proof chunks of at most 24 MiB.  The raw 620 MiB trace is deliberately
not staged.  No 76-comparator candidate was produced.  `[58,70)`, `[59,75)`,
and `[42,54)` remain unresolved.  `bun run check` passed: 434 tests passed,
1 skipped, 0 failed.

## Deviations

The requested branch name was already occupied.  To preserve it, this work
uses `swarm/frontier-cloud-codex-wide--resynthesize-interior-sorting-ne-ve95w-c2-2-c7`
from PR 127 commit `a9bd666a`.

## Concerns

This certificate excludes only a ten-comparator replacement for the fixed
`[53,64)` window of this particular 77-comparator baseline; it is not a
global lower bound.

## Follow-ups

Choose a fresh, non-implied interval beginning before `[53,64)` or otherwise
outside all certified exterior windows, while preserving exact state-set
equality auditing and push-safe proof chunking.
