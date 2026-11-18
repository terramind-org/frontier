Outcome: done

## Done

Recovered PR 136 commit `bb0867e4` and validated the current c8 `SHA256SUMS` replay ledger: the pinned baseline, equality-auditing encoder, compressed CNF, and all six proof chunks match. Reassembly and decompression reproduce its recorded raw CNF and DRAT digests. The pinned 77-comparator baseline is SHA-256 `ec66245d95a80562ca1a14d05e2650267d38c2d7d20d4b74df422d482c2c23bd`; Frontier diagnosis accepted it on all 262,144 binary inputs.

`[51,62) -> 10`, seed `5111`, is fresh and non-implied by the complete certified exterior-window ledger because it starts before certified `[52,63)`. Scalar enumeration, vectorised enumeration, and the actual encoded set each contain 136 prefix states and share SHA-256 `d0a141e947222e871823ef04ee531b13951af9ee8c2df674ab7b6f75c370b584`. The complete initial CNF has 32,718 variables and 1,435,347 clauses.

Under a 600-second external supervisor on one CPU, CaDiCaL returned UNSAT with exit 0 in 443.376 seconds. Independent DRAT-trim replay exited 0, reported `s VERIFIED`, and took 123.025 seconds. The compact c9 bundle is `.terramind/scratch/sort18-c9-recovery/`: source, baseline, commands, timestamps, solver/checker logs and exits, compressed CNF, raw and compressed hashes, manifest, replay instructions, and five lossless proof chunks of at most 24 MiB. The raw CNF and 483 MiB DRAT are deliberately not staged. No 76-comparator candidate was produced. `[58,70)`, `[59,75)`, and `[42,54)` remain unresolved. `bun run check` passed: 434 tests passed, 1 skipped, 0 failed.

## Deviations

The requested branch name was occupied, so this work uses `swarm/frontier-cloud-codex-wide--resynthesize-interior-sorting-ne-ve95w-c9-recovery` from `bb0867e4`.

## Concerns

This certificate excludes only a ten-comparator replacement for the fixed `[51,62)` window of this particular 77-comparator baseline; it is not a global lower bound.

## Follow-ups

Choose a fresh non-implied interval beginning before `[51,62)` or one outside all certified exterior windows, preserving triple state-set equality auditing and push-safe proof replay.
