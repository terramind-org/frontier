Outcome: done

## Done

Recovered PR 119's `f30d7df6` evidence and verified both retained replay
manifests: every entry in `sort18-c2-2-recovered/SHA256SUMS` and
`sort18-c5/SHA256SUMS` matched. The prior 100-of-104-state result remains an
explicitly invalid control, never certificate evidence.

Audited the state-cap defect and made the new encoder fail closed. It now
enumerates the reachable prefix image over all 262,144 binary inputs by both
the vectorised network evaluator and an independent scalar evaluator, then
requires the set passed to the CNF encoder to equal that independent image.
The audit records cardinalities and stable state-set SHA-256 values before any
SAT call.

`[54,65) -> 10`, seed `5411`, is fresh and non-implied because it begins
before the certified `[55,66)` window. The fixed baseline passed Frontier
diagnosis on all binary inputs. The complete query encoded all 113 reachable
prefix states (vectorised, independent, and encoded sets all had SHA-256
`7314a583fe3ffbd0e26a035707d2038aa4aaa4ba20a610e9af37fce99bd9d4cc`),
with 26,796 variables and 1,211,018 clauses. One-core CaDiCaL returned UNSAT
in 272.332s under a 600s supervisor (exit 0). Independent DRAT-trim returned
`s VERIFIED` in 281.607s (exit 0).

Committed replay artifacts live in `.terramind/scratch/sort18-c6/`: source,
baseline, exact commands, logs/exits, compressed CNF, and eight lossless DRAT
chunks of at most 24 MiB. Hash manifests and reassembly instructions are
included; the raw 687 MiB trace is not staged. No 76-comparator candidate was
produced. `bun run check` passed: 434 tests passed, 1 skipped, 0 failed.

## Deviations

The requested branch name was already occupied, so this work uses
`swarm/frontier-cloud-codex-wide--resynthesize-interior-sorting-ne-ve95w-c2-2-c6`
from recovered PR 119 commit `f30d7df6`.

## Concerns

This excludes only a ten-gate replacement of fixed baseline window `[54,65)`;
it is not a global lower bound. `[58,70)`, `[59,75)`, and `[42,54)` remain
unresolved.

## Follow-ups

Run the repository gate, then choose a fresh non-implied window beginning
before 54 or outside all certified exterior windows. Retain the state-set
equality audit and push-safe chunking discipline.
