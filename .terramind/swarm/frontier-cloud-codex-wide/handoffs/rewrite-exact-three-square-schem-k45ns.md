Outcome: done

## Done

Recovered c10's Sun package and verified the rank-23 Frontier witness SHA-256
`9ee984b5951f000376dbdccbb402fb166b4bd38abc5acc4402b29617a9731b8b`, the
unchanged screen SHA-256
`e01177604eaab6dd1ac401e9d2fada8806aa6543ee60a3da166f7a74e10304b5`, the
seven-move ordering, and the planted seven-to-one exact reduction control.
Frontier diagnose accepts the baseline at rank 23, tying the known value.

The c11 normalized-term-multiset fingerprint test found no duplicate among
the seven legal Sun rewrites.  It covers literal projectively normalized term
multisets only, not tensor orbit equivalence.

On CPU 0, resumed only at Sun neighbour 1 support 0 `[0,1,2,3,4,5,6]` and
ran for 1450.010 seconds with atomic 1,000-support checkpoints.  It covered
674461 supports with zero reductions: neighbour 1, move `[0,5,8]`, complete
at 245157 supports with 27168 low-flattening; neighbour 2, move `[0,6,11]`,
complete at 245157 with 24857 low-flattening; and neighbour 3, move
`[1,6,20]`, partial at 184147 with 20414 low-flattening.  No rank-22
candidate was emitted, so candidate Frontier diagnose/check was not
applicable.  Exact next cursor: neighbour 3, support index 184147, first
unvisited `[3,6,8,10,13,14,18]`.

`bun run check` passed.  Scripts, source, diagnostics, controls, trace,
atomic checkpoint, result, hash manifest, and raw run output are preserved in
`.terramind/swarm/frontier-cloud-codex-wide/matmul3-c11/`.

## Deviations

None.

## Concerns

This excludes only the implemented integral constructive-factorization
criterion for the covered supports.  It is not a tensor-rank lower bound and
does not exclude rational/non-integral replacements, other rank-23 schemes,
other rewrite methods, or unvisited Sun ranges.

## Follow-ups

Resume only the Sun screen at `--start-neighbour 3 --start-support-index
184147`, then neighbours 4–6 in order.  Do not repeat completed Perminov
ranges, Sun neighbour 0 (c10), Sun neighbours 1–2 (c11), three-to-six-term
screens, the 15,000-state walk, or exhausted pencil scans.
