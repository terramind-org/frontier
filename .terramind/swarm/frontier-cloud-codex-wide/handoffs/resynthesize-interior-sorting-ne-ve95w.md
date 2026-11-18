Outcome: done

## Done

Recovered PR 138 commit `4cb4d6f0` and verified the c9 replay bundle. Every retained `SHA256SUMS` entry matched; reassembling its five proof chunks reproduced compressed-proof SHA-256 `b8ff5aeb8b98999a90ffbdec5e88777e1294d779aeb7dd120bfd4577fb1c7f34`, and decompression reproduced raw CNF/DRAT hashes `011f756785d60ced7166c80f40ba3690fadae292b776635dba5209d8fcdf2c8f` and `51d62ee09c09df8a25c5d73f66898a947fe8348f31e840c04a0e39ae9cfa2b69`. The pinned 77-comparator baseline is SHA-256 `ec66245d95a80562ca1a14d05e2650267d38c2d7d20d4b74df422d482c2c23bd`; Frontier diagnosis accepted all 262,144 binary inputs.

`[50,61) -> 10`, seed `5011`, is fresh and non-implied because it begins before certified `[51,62)`. Scalar enumeration, vectorised enumeration, and the actual encoded set each contain 163 prefix states and share SHA-256 `66d46d069fcc41bfc31825487293203887b3b0a204e0dbac2bc654d8213d67db`. The complete initial CNF has 39,200 variables and 1,697,280 clauses.

Under a 600-second external one-core supervisor, CaDiCaL returned UNSAT with exit 0 and 89.132 seconds remaining. Independent DRAT-trim exited 0, reported `s VERIFIED`, and reported 26.499 seconds of verification time. Commit records `.terramind/scratch/sort18-c10-recovery/`: source, baseline, commands, timestamps, solver/checker logs and exits, compressed CNF, raw and compressed hashes, replay instructions, and three lossless proof chunks at most 24 MiB. The raw CNF and 259 MiB DRAT are deliberately not staged. No 76-comparator candidate was produced. `[58,70)`, `[59,75)`, and `[42,54)` remain unresolved. `bun run check` passed: 434 tests passed, 1 skipped, 0 failed.

## Deviations

The requested branch name was occupied, so this work uses `swarm/frontier-cloud-codex-wide--resynthesize-interior-sorting-ne-ve95w-c10-recovery` from `4cb4d6f0`.

## Concerns

This certificate excludes only a ten-comparator replacement for the fixed `[50,61)` window of this particular 77-comparator baseline; it is not a global lower bound.

## Follow-ups

Choose a fresh non-implied interval beginning before `[50,61)` or one outside the certified exterior windows, preserving triple state-set equality auditing and push-safe proof replay.
