Outcome: done

## Done

Recovered PR 144 commit `5bb9cfc0` and verified every retained object in its c10 `SHA256SUMS` and `MANIFEST.sha256` ledgers. The pinned 77-comparator baseline hash is `ec66245d95a80562ca1a14d05e2650267d38c2d7d20d4b74df422d482c2c23bd`; Frontier diagnosis accepted all 262,144 binary inputs.

`[49,60) -> 10`, seed `4911`, is fresh and non-implied because it begins before certified `[50,61)`. The scalar, vectorised, and actual encoded prefix-state sets each contain 204 states with SHA-256 `9dcfd02d6b550a07a72fbf23fb99c94bb1d63d67e3598e1afc4230810b598563`. The complete initial CNF has 49,038 variables and 2,095,015 clauses.

One-core CaDiCaL returned UNSAT in 191.986 seconds under a 600-second external supervisor (exit 0). The independent DRAT-trim replay reached its separate 300-second supervisor deadline (exit 124) without `s VERIFIED`; this is therefore explicitly retained as unverified solver evidence, not a certified exclusion. `.terramind/scratch/sort18-c11-recovery/` retains source, baseline, commands, timestamps, exits, logs, compact CNF, replay hashes, instructions, and eight lossless proof chunks no larger than 24 MiB. Chunk reassembly and decompression reproduce the recorded raw CNF and DRAT hashes. Raw CNF and 896 MiB DRAT are deliberately not staged. No 76-comparator candidate was produced. `[58,70)`, `[59,75)`, and `[42,54)` remain unresolved. `bun run check` passed: 434 passed, 1 skipped, 0 failed.

## Deviations

The requested `c2-2` branch already resolved to the old `bec2cfd4` lineage, so this work used clean descendant `swarm/frontier-cloud-codex-wide--resynthesize-interior-sorting-ne-ve95w-c11-recovery` from `5bb9cfc0`. The terminal runner failed before starting due to an IPC error; the actual solver was then run once in a foreground external supervisor. The proof checker timed out, so no certificate-backed result is claimed.

## Concerns

The UNSAT solver output is not independently verified because DRAT-trim timed out; it must not be used as a fixed-window exclusion until replay succeeds.

## Follow-ups

Either rerun the retained c11 proof replay with a longer independent deadline, or choose a fresh non-implied interval beginning before `[49,60)`, keeping the triple state-set equality audit and push-safe proof chunks.
