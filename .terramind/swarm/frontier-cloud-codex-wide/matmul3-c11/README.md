# c11 Sun seven-term continuation

Recovered c10's public Sun rank-23 witness and verified its SHA-256 as
`9ee984b5951f000376dbdccbb402fb166b4bd38abc5acc4402b29617a9731b8b`.
The screen SHA-256 is `e01177604eaab6dd1ac401e9d2fada8806aa6543ee60a3da166f7a74e10304b5`.
Frontier diagnosis accepts the recovered witness at rank 23, tying the best
known value.  The planted seven-to-one control passed.

The normalized-term-multiset test writes a SHA-256 fingerprint of the sorted,
projectively normalized factor triads for every legal rewrite.  It found no
duplicate among the seven legal Sun moves; that is literal term-multiset
evidence only, and does not establish GL(3)^3 orbit inequivalence.

This CPU-0 continuation starts only at Sun neighbour 1 (move `[0,5,8]`), so
it does not repeat c10's completed neighbour 0.  It uses atomic checkpoints
every 1,000 supports and a 1,450-second graceful cutoff.  It completes
neighbours 1 and 2 and leaves neighbour 3 resumable at support index 184147.
The result is solely for the implemented integral constructive-factorization
criterion, not a tensor-rank lower bound.
