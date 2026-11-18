Outcome: done

## Done

Recovered PR 112 commit `9290a378` and verified the pinned Sun rank-23
witness SHA-256 `9ee984b5951f000376dbdccbb402fb166b4bd38abc5acc4402b29617a9731b8b`,
unchanged screen SHA-256
`e01177604eaab6dd1ac401e9d2fada8806aa6543ee60a3da166f7a74e10304b5`,
c12 checkpoint cursor, fixed seven-move order, and the planted seven-to-one
exact control.  The inherited rank-23 Frontier diagnosis remains retained in
the package.

Pinned to CPU 0, resumed only at Sun neighbour 6 / support index 105566,
first unvisited `[1,4,6,11,15,17,19]`.  Atomic support-level checkpoints ran
for all 139591 remaining supports and the run completed in 334.294 seconds.
It found 15541 low-flattening supports, minimum maximum factor rank 5, and
zero integral constructive reductions; no rank-22 candidate existed to
reconstruct or validate with Frontier.  The process result records the
terminal cursor; `terminal-cursor.json` explicitly disambiguates the final
checkpoint's internal neighbour-plus-one sentinel.

`coverage-audit.json` combines c10--c13: each of the seven distinct Sun
rewrites has exactly 245157 tested seven-term supports, for 1716099 total;
187498 are low-flattening and zero produce a constructive reduction.  The raw
trace has 139591 records and SHA-256
`4eff38cb16346a0ad7c8235a97faa3e9bc53326a9028df26777a0c24f83ac3df`.
Source, screen, checkpoint, result, trace, control and audit hashes are in
`matmul3-c13/artifacts-sha256.txt`.  `bun run check` passed: 434 pass, 1 skip,
0 fail.

## Deviations

None.

## Concerns

This exhausts only the implemented integral constructive-factorization
criterion on the seven fixed Sun rewrites.  It is not a tensor-rank lower
bound and does not rule out rational/non-integral replacements, other
rank-23 schemes, or different rewrite techniques.

## Follow-ups

The fixed Sun seven-term screen is complete: do not rerun Sun neighbours 0--6,
the complete Perminov seven-term screen, prior 3--6 term screens, the
15000-state walk, or either exhausted pencil scan.  Any later work must use a
distinct seed and genuinely different criterion.
