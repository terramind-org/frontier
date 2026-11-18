Outcome: done

## Done

Recovered PR 105 commit `db9d6239` and verified the Sun rank-23 witness hash
`9ee984b5951f000376dbdccbb402fb166b4bd38abc5acc4402b29617a9731b8b`, unchanged
screen hash `e01177604eaab6dd1ac401e9d2fada8806aa6543ee60a3da166f7a74e10304b5`,
fixed seven-move order, c11 cursor, and planted seven-to-one exact control.
The inherited Frontier diagnosis accepts the baseline at rank 23, tying the
known value.

On CPU 0, resumed only at neighbour 3, support index 184147
(`[3,6,8,10,13,14,18]`). The 1450.001-second graceful run covered 656,890 new
supports with zero reductions: neighbour 3 remaining 61,010 (7,538
low-flattening), neighbour 4 all 245,157 (27,231), neighbour 5 all 245,157
(26,187), and neighbour 6 first 105,566 (11,853). No rank-22 candidate was
emitted, so no candidate witness required Frontier diagnose/check. The exact
next cursor is neighbour 6, support index 105566, first unvisited
`[1,4,6,11,15,17,19]`.

`bun run check` passed: 434 pass, 1 skip, 0 fail. The c12 sources, inherited
preflight evidence, copied baseline evidence, raw run log, trace, atomic
checkpoint/result, control, and hashes are in
`.terramind/swarm/frontier-cloud-codex-wide/matmul3-c12/`.

## Deviations

None.

## Concerns

This excludes only the implemented integral constructive-factorization
criterion on the screened supports. It is not a tensor-rank lower bound and
does not exclude the remaining neighbour-6 supports, rational/non-integral
replacements, other rank-23 schemes, or different rewrites.

## Follow-ups

Resume only Sun neighbour 6 at `--start-neighbour 6 --start-support-index
105566`, then stop after its remaining 139,591 supports. Do not repeat Sun
neighbours 0--5, their completed supports, the complete Perminov seven-term
screen, the 3--6 term scans, the 15,000-state walk, or exhausted pencil scans.
