# c15 exact-Q Perminov trace follow-up

This run recovers c14's calibrated exact rational recovery rather than re-enumerating any integral subset screen. The retained Perminov certificate has SHA-256 `80bb4187ddf0cfc04654ca3e524f4d311c5a62245ee231a1101280b43fd2ae3a`; its c4 Frontier diagnosis is valid at rank 23 and ties the known value. The decoded rewrite order is the fixed first seven legal moves from screen SHA-256 `d869c72bd610fcc70d7d5fdcbb353afebc8c6630d1d03af1e75e6044c58bedcb`.

The c14 positive control is recovered from source SHA-256 `7e539670e9eba91eea1e9b0dd437e3d8e102ac337c582b2bbe9d41597e68ba3e`: `4e0⊗e0⊗e0 + 2e0⊗e0⊗e1 + 2e0⊗e1⊗e0 + e0⊗e1⊗e1 = 4e0⊗(e0+e1/2)⊗(e0+e1/2)`. The old integral gate returns no replacement, while exact-Q recovery verifies the identity and returns one term. This is not rescaling: its four input products differ in both complementary factors.

Only rewrites 1--6 have retained per-support JSONL traces; rewrite 0 completed before trace capture. Their hashes and the exact rewrite order are recorded in the result JSON. Per rewrite, rows are sorted by `SHA-256(perminov-q-c15-v1:neighbour:support_index)` and consumed round-robin. CPU 0 processed order indices 0--1919: 320 rows from each recorded rewrite, all previously untested by this rational method. Old and new tests found zero reductions. The per-support atomic checkpoint gives the next untouched row: order 1920, rewrite 1, support index 128548, `[1,12,14,15,16,18,21]`.

This is a bounded exact-Q sample, not a tensor-rank lower bound. Since no rank-22 replacement was found, no new witness exists for Frontier diagnose or check.
