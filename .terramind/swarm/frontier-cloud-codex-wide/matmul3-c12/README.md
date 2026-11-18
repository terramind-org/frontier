# c12 Sun seven-term continuation

Recovered c11 commit `db9d6239` and verified the inherited Sun witness SHA-256
`9ee984b5951f000376dbdccbb402fb166b4bd38abc5acc4402b29617a9731b8b`, screen
SHA-256 `e01177604eaab6dd1ac401e9d2fada8806aa6543ee60a3da166f7a74e10304b5`,
the seven fixed rewrite moves, c11's checkpoint cursor, and the planted exact
seven-to-one reduction control.  The copied c11 Frontier diagnosis accepts the
rank-23 witness, tying the known value.

Pinned to CPU 0, the unchanged screen resumed only at neighbour 3, support
index 184147 (`[3,6,8,10,13,14,18]`).  It atomically checkpointed every 1,000
supports and stopped gracefully after 1450.001 seconds.  Neighbour 3's
remaining 61,010 supports and all 245,157 supports for each of neighbours 4
and 5 were exhausted; neighbour 6 covered 105,566 supports.  No constructive
reduction was found.  The exact next cursor is neighbour 6, support index
105566, `[1,4,6,11,15,17,19]`.

This only screens the implemented integral constructive-factorization
criterion; it is not a tensor-rank lower bound.  `bun run check` passed (434
pass, 1 skip, 0 fail).  Raw log, trace, atomic checkpoint, result, and hashes
are retained in this directory.
