Outcome: done

## Done

Recovered original c13 commit `bcb02c4d2b7eff796c013b4f62aa4159b96b557a` from the reachable local recovery ref and preserved its transcript and replay bundle in a clean descendant of published c12 commit `209a9d68`. The original c13 proof blob is 131,360,533 bytes, above GitHub's 100 MiB object limit; the replacement branch retains the six numbered proof chunks (each no larger than 24 MiB) and the 8,129,401-byte compressed CNF. No persisted push-rejection log was present, but outgoing object inspection identifies that oversized DRAT blob as the transport blocker. No force-push or solver rerun occurred.

Reassembled the six chunks in numeric order and verified the compressed proof SHA-256 `2f70baaebd553cdfeb774f10071ec7886d603a0c657ee1c51dfe075442651850`, compressed CNF SHA-256 `d3b715a7d3912f19f9172cdb1015649722300e5e8583cbdb463529c8aca19922`, raw CNF SHA-256 `020fd77ae28edd952d83f861dc61181d530bb4aacfc6b51bfe0a99e520e633eb`, and raw DRAT SHA-256 `e824a7f526bd2f95c2e993a9b299987c11f5f6244c5fb4f6346f244ac6859085`. The clean `SHA256SUMS` now checks directly after the documented reassembly.

The recovered checker transcript records `timeout --foreground 300s taskset -c 0 drat-trim`, exit 0, 196 wall seconds, and explicit `s VERIFIED` (checker time 195.692 seconds). It certifies only the completed fixed `[48,59) -> 10` exclusion on the pinned baseline, whose SHA-256 is `ec66245d95a80562ca1a14d05e2650267d38c2d7d20d4b74df422d482c2c23bd`. The original encoder transcript records matching scalar/vectorized/encoded prefix-state sets of 218 states, digest `0c134f96b179b59392d657ddd20ee5f2cf946f80240651608d4f8d1c66ce7313`, and a complete 52,722-variable, 2,231,801-clause CNF. The baseline diagnosis is retained; no shortened network was produced.

`.terramind/scratch/sort18-c13-recovery/` now contains the compact replay bundle, original-provenance note, source, logs, commands, hashes and verified chunks. `bun run check` passed: 434 pass, 1 skip, 0 fail. A fresh `[47,58)` query was not started because recovery, integrity verification and packaging used the available window.

## Deviations

The requested `c2-2` branch name was already occupied on an unrelated older lineage, so this clean recovery uses `swarm/frontier-cloud-codex-wide--resynthesize-interior-sorting-ne-ve95w-c14-recovery` from `209a9d68`. The original c13 commit stays locally reachable from its c13 recovery ref, while the clean descendant intentionally omits only its oversized duplicate proof blob. The `SHA256SUMS` proof entry names the documented reassembled file so the compact replay commands validate directly.

## Concerns

This is a fixed-window exclusion for one pinned 77-comparator baseline, not a global lower bound. `[47,58)` remains untested, and `[58,70)`, `[59,75)`, and `[42,54)` remain unresolved.

## Follow-ups

Publish this clean recovery branch through swarm transport, then test a fresh non-implied earlier window such as `[47,58)` with the same triple state audit, external solver deadline and independent proof replay.
