Outcome: done

## Done

Recovered PR 93 commit `536ea768` and verified the c9 seed, screen, checkpoint, and trace hashes before continuing.  The recovered c9 cursor was exactly neighbour 6, support index 42,387, first unvisited support `[0,3,6,9,17,21,22]`.  On CPU 0, c10 completed all 202,770 remaining seven-term supports for that neighbour in 555.800 seconds.  It found 25,168 low-flattening supports, minimum maximum factor rank 5, and zero constructive reductions.  The planted seven-to-one exact control passed; the authoritative result cursor is complete.  No candidate was emitted, so candidate Frontier diagnose/check was not applicable.

This completes the fixed Perminov seven-neighbour, seven-term screen across c6--c10: 1,716,099 supports, 216,593 low-flattening supports, and zero constructive reductions.  No completed neighbour or prior 3--6 term scan was repeated.

After that exhaustion, downloaded and preserved the distinct public Sun 56-addition rank-23 certificate (`https://github.com/sunyinqi0508/3by3r23-56a`, retrieved 2026-11-18).  The upstream verifier passes all 729 integer Brent equations.  Its converted Frontier witness (SHA-256 `9ee984b5951f000376dbdccbb402fb166b4bd38abc5acc4402b29617a9731b8b`) passed Frontier diagnose as valid at rank 23, tying the known value.  It has seven legal projective shared-factor pairs, unlike the previously ineligible Laderman seed.  The first genuinely separate split/merge rewrite, move `[0,2,18]`, exhausted all 245,157 seven-term supports in 531.206 seconds: 26,709 low-flattening supports, minimum maximum factor rank 5, and zero constructive reductions.  Its planted control passed; the exact next Sun cursor is neighbour 1, support index 0, `[0,1,2,3,4,5,6]`.

`bun run check` passed: 434 pass, 1 skip, 0 fail.  All c10 sources, copied prior evidence, scripts, controls, traces, checkpoints, raw logs, source verification, Frontier diagnosis, and checksums are under `.terramind/swarm/frontier-cloud-codex-wide/matmul3-c10/`.

## Deviations

The first c10 launch was started through a nonpersistent wrapper and returned control while continuing in the sandbox.  After observing its durable 8,000-support checkpoint, I briefly launched an overlapping resume, detected the overlap at its own checkpoint, and interrupted it before it could modify the authoritative c10 output/checkpoint.  The duplicate resume trace/checkpoint are retained as audit evidence; the original CPU-0 process alone completed the required unvisited range.

The source hash in the recovered c9 preflight manifest is `d869c72b...`, while the c9 committed screen currently hashes to that same value; c10 preserves and records the actual recovered hashes rather than relying on a shortened handoff string.

## Concerns

These exhaustive results exclude only the implemented integral constructive-factorization criterion.  They are not tensor-rank lower bounds and do not exclude rational/non-integral replacements, other rank-23 schemes, or other rewrite methods.  The Sun screen covers only its first of seven legal rewrites.

## Follow-ups

If continued, resume only the Sun scheme at neighbour 1, support index 0, then later Sun neighbours in order.  Do not rerun the completed Perminov neighbours 0--6, the completed first Sun neighbour, 3--6 term screens, 15,000-state walk, or exhausted pencil scans.
