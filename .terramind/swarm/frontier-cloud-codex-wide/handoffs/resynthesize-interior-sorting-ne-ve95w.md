Outcome: done

## Done

Created `swarm/frontier-cloud-codex-wide--resynthesize-interior-sorting-ne-ve95w-c10` from c9 and recovered commit `43641c7b`. The c9 compact manifest was checked before the new run; the original `[62,74) -> 11` compressed CNF and DRAT decompressed to their recorded hashes. A fresh DRAT-trim replay completed with `s VERIFIED` in 129.094 seconds; raw output is preserved.

The 77-comparator baseline remains SHA-256 `ec66245d95a80562ca1a14d05e2650267d38c2d7d20d4b74df422d482c2c23bd`. Its retained Frontier diagnosis says valid on all 262,144 binary inputs and ties the known 77-comparator value.

Ran the retained non-implied `[61,73) -> 11` query (seed `6112`) through the exact matching encoder on one CPU: Python 3.13.5, python-sat 1.9.dev23, CaDiCaL 1.5.3, `taskset -c 0`, and `timeout --signal=TERM --kill-after=10s 600s`. The external supervisor exited 0 after 185 seconds, not by timeout or launcher termination. The solver returned UNSAT in 182.635 seconds, in its first solve, with all 63 reachable prefix states already encoded in the retained 15,993-variable / 797,852-clause initial CNF.

Fresh DRAT-trim independently replayed the new full CNF/DRAT and reported `s VERIFIED` in 229.206 seconds. The compact c10 bundle retains only losslessly compressed CNFs/proofs, encoder, baseline, command, run logs, fresh checker logs, and `MANIFEST.sha256` under `.terramind/scratch/sort18-c10/`. The new decompressed payload hashes are CNF `72dee4cc5d29ba8ccaa1200da13f3adcfadec15104f816df24817a4fe5830899` and DRAT `fbd58de6d405e22bdfa4c17b4670b89eb2d7c7a7becbc0a54f751bf41be17739`; `sha256sum -c MANIFEST.sha256` passes.

`bun run check` passed: 434 tests passed, 1 skipped, 0 failed.

No SAT model or 76-comparator candidate was produced, so no new Frontier candidate diagnosis applies.

## Deviations

The cloud persistent-terminal integration failed with `ipcMain.removeListener is not a function`. I used the managed foreground shell, which returned session IDs and was waited to exit for both solver and checker runs; this delivered the requested externally bounded experiment. The earlier c9 ignored raw log had completed in the restored checkout but had no reliable supervisor status, so it was not used as the c10 result.

## Concerns

The certified result excludes only an 11-gate replacement in the fixed `[61,73)` window of this particular 77-gate baseline. Together with `[62,74) -> 11`, it is not a global lower bound and does not exclude a different 76-comparator network. `[59,75)` and `[42,54)` remain unresolved.

## Follow-ups

Audit the ledger for another interval that extends outside both certified windows before spending another long lane. Preserve the complete-prefix-state condition and proof replay; do not rerun `[59,75)` unchanged.
