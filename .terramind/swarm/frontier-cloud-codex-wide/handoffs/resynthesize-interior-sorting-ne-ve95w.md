Outcome: done

## Done

Recovered PR 131 commit `68c63f6f` and validated its current `SHA256SUMS` replay ledger: pinned baseline, equality-auditing encoder, compressed CNF and all six proof chunks match. Reassembly and decompression reproduce its recorded raw CNF and DRAT hashes. The legacy `MANIFEST.sha256` in c7 predates the audited encoder and is not used as its replay ledger. The pinned 77-comparator baseline is SHA-256 `ec66245d95a80562ca1a14d05e2650267d38c2d7d20d4b74df422d482c2c23bd`.

`[52,63) -> 10`, seed `5211`, is fresh and non-implied by the complete certified exterior-window ledger because it starts before certified `[53,64)`. Frontier diagnosis accepted the pinned baseline on all 262,144 binary inputs. Scalar enumeration, vectorised enumeration, and the actual encoded set each contain 121 prefix states and share SHA-256 `215ca982c00343a794bd54a0bad2276bd5d65c487f431ad2ec58a5fa7116daab`. The complete initial CNF has 29,056 variables and 1,289,646 clauses.

Under a 600-second external supervisor on one CPU, CaDiCaL returned UNSAT after 399.128 seconds (exit 0). Independent DRAT-trim replay exited 0, reported `s VERIFIED`, and took 193.052 seconds. The compact c8 bundle is `.terramind/scratch/sort18-c8/`: source, baseline, commands, timestamps, solver/checker logs and exits, compressed CNF, raw and compressed hashes, manifest, replay instructions, and six lossless proof chunks of at most 24 MiB. The raw CNF and 616 MiB DRAT are deliberately not staged. No 76-comparator candidate was produced. `[58,70)`, `[59,75)`, and `[42,54)` remain unresolved. `bun run check` passed: 434 tests passed, 1 skipped, 0 failed.

## Deviations

The requested branch name was occupied, so this work uses `swarm/frontier-cloud-codex-wide--resynthesize-interior-sorting-ne-ve95w-c8-recovery` from `68c63f6f`. The first launch wrapper exited 127 before the encoder ran because this image lacks `/usr/bin/time`; its log is retained, and the only query evidence is the successful rerun under the same external supervisor.

## Concerns

This certificate excludes only a ten-comparator replacement for the fixed `[52,63)` window of this particular 77-comparator baseline; it is not a global lower bound.

## Follow-ups

Choose a fresh non-implied interval beginning before `[52,63)` or one outside all certified exterior windows, preserving triple state-set equality auditing and push-safe proof replay.
