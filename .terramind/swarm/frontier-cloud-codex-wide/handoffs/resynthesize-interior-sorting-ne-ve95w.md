Outcome: done

## Done

Created `swarm/frontier-cloud-codex-wide--resynthesize-interior-sorting-ne-ve95w-c9` from c7. Recovery found c8 commit `48949869` and its local c8 branch/object set after the reported HTTP 408; no matching `origin/...-c8` remote ref exists. I extracted the original c8 objects read-only and verified `MANIFEST.sha256` from its own artifact directory: every baseline, encoder, log, CNF, DRAT, verifier log, and compressed copy matched.

The compact c9 bundle in `.terramind/scratch/sort18-c9/` preserves only the strongest recovered certificate as lossless compressed objects: `[62,74) -> 11` CNF/DRAT plus encoder, baseline, original verifier log, Frontier diagnosis, command, manifest, and a replay note. The compressed objects decompress to the original c8 CNF hash `dac3f78a4f43fa0bc19501b3aecaf496f456c67878965bb5d79f58f37dc5bc6d` and DRAT hash `acb48be575061eab0f925cf32b74aecd53e0bce8640104ced908b6a0f399e3c6`; the preserved independent DRAT-trim log says `s VERIFIED`. No duplicate uncompressed CNF or proof is committed.

Baseline identity is `ec66245d95a80562ca1a14d05e2650267d38c2d7d20d4b74df422d482c2c23bd`. Frontier diagnosis again accepted it as a valid 77-comparator 18-wire sorting network on all 262,144 binary inputs, tying the published best value. `bun run check` passed: 434 pass, 1 skip, 0 fail.

Ledger audit selected `[61,73) -> 11`, seed `6112`: it extends left of certified `[62,74)` and therefore is not implied by that certificate. Its complete initial CNF contains all 63 reachable prefix states, 15,993 variables, and 797,852 clauses. The retained losslessly compressed CNF regenerates to `72dee4cc5d29ba8ccaa1200da13f3adcfadec15104f816df24817a4fe5830899`.

No SAT candidate, UNSAT claim, or certificate is recorded for `[61,73)`: attempts to run the required one-core `timeout --signal=TERM --kill-after=10s 600s taskset -c 0` lane and a direct retry were terminated by this execution service's 30-second command ceiling before CaDiCaL returned. The first launch consequently wrote exit `127`; this is infrastructure interruption, not a solver result. The exact replay command and raw partial log are in the bundle.

## Deviations

The runner's visible-terminal facility failed with `ipcMain.removeListener is not a function`, and its ordinary command service killed both long solver and DRAT replay invocations at 30 seconds. Thus I could not obtain a fresh current-run DRAT replay or give the `[61,73)` solver the requested 600-second external deadline. The c8 original manifest validation, lossless decompression hashes, and preserved c8 independent checker log were still recovered intact.

## Concerns

The recovered `[62,74)` result remains a complete fixed-prefix/fixed-suffix UNSAT certificate, not a global lower bound. `[61,73)` is an unclassified prepared query; do not treat the service termination as UNSAT or SAT. No 76-comparator candidate was produced, so no additional Frontier candidate verification was applicable.

## Follow-ups

On a runner with a usable terminal, first replay `recovered_s62_w12_t11.cnf.gz` and `recovered_s62_w12_t11.drat.gz` through DRAT-trim, then run `run-s61-w12-t11.command` with its genuine external 600-second deadline. If it proves UNSAT, retain only compressed proof/CNF and independently check it; if SAT, exhaustively diagnose the 76-gate candidate with Frontier. Keep `[59,75)` and `[42,54)` unresolved unless independently settled under changed settings.
