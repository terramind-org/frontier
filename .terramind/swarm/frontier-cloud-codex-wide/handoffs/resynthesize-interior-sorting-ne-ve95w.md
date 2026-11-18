Outcome: done

## Done

Recovered PR 150 commit `0266d9d7` and verified every c11 retained object against `MANIFEST.sha256`, including its pinned 77-comparator baseline (`ec66245d95a80562ca1a14d05e2650267d38c2d7d20d4b74df422d482c2c23bd`). I assembled the eight proof chunks in recorded numeric order; the compressed stream hash is `a345e63e01719fd6932e430662ba8888ea0a8122af02f38f63bdd12a30e0ed69`, and decompression reproduces CNF/DRAT hashes `b45d2ea1f3e34dd710d6044758590fbe9a87eece72ed08b3698fff5c943eb5aa` and `052ad0f8701b637fe044b97a809dfebd81116ce2261d78f9699e71440a4734a8`.

Without rerunning CaDiCaL, independent DRAT-trim replay ran on CPU 0 under `timeout --foreground 1350s`. It exited 0 after 384 seconds and emitted `s VERIFIED` (checker-reported verification time 383.731s). The retained CaDiCaL UNSAT result for the complete audited `[49,60) -> 10` query is therefore now a certificate-backed fixed-window exclusion. `.terramind/scratch/sort18-c12-replay/` records the command, checker usage, timestamps, exit, wall time, output, and regenerated raw hashes; c11 retains the compact CNF and eight <=24 MiB lossless proof chunks. No shortened network was found, so no additional Frontier candidate check applies.

## Deviations

The requested branch name was already occupied on the old lineage, so I used `swarm/frontier-cloud-codex-wide--resynthesize-interior-sorting-ne-ve95w-c12-replay` from the supplied c10 recovery head and restored only the c11 bundle from locally available commit `0266d9d7`. The persistent-terminal API failed with an IPC error, so the one replay process was retained from the initial supervised foreground launch; it was confirmed single-core by its `taskset -c 0` command and completed normally. No fresh window was attempted because the replay consumed the available bounded work time.

## Concerns

This certificate excludes only a ten-comparator replacement for fixed `[49,60)` of the pinned 77-comparator baseline; it is not a global lower bound. `[58,70)`, `[59,75)`, and `[42,54)` remain unresolved.

## Follow-ups

Choose a fresh non-implied interval beginning before `[49,60)` (for example `[48,59)`) and retain the triple prefix-state equality audit, external solver deadline, and independent chunked-proof replay.
