# c13 Sun seven-term completion

Recovered c12 commit `9290a378` and verified the pinned Sun rank-23 witness,
unchanged screen, c12 checkpoint cursor, fixed seven-move ordering, and the
planted seven-to-one exact control.  CPU 0 then screened only neighbour 6 from
support index 105566, its first unvisited tuple `[1,4,6,11,15,17,19]`, using
an atomic JSON checkpoint after every support.

All remaining 139591 supports finished in 334.294 seconds.  There were 15541
low-flattening supports, minimum maximum factor rank 5, and zero constructive
reductions; no rank-22 candidate existed to reconstruct or send to Frontier.
The terminal cursor is explicit in `terminal-cursor.json`.  `coverage-audit.json`
combines c10--c13 and establishes exactly 245157 supports per fixed rewrite,
1716099 supports overall, and zero reductions.

This exhausts only the implemented integral constructive-factorization
criterion for this Sun seed.  It is not a tensor-rank lower bound and does not
exclude rational/non-integral replacements, other rank-23 schemes, or other
rewrite techniques.  The raw trace, final atomic checkpoint, result, planted
control, inherited baseline diagnosis, and hashes are retained here.
