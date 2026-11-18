# c16 exact-Q Perminov trace continuation

This package resumes c15's deterministic, stored-trace rational recovery at
order 1920 only.  Its asserted first row is rewrite 1, support index 128548,
`[1,12,14,15,16,18,21]`; it does not enumerate any subset or use rewrite 0.

The recovered seed SHA-256 is
`80bb4187ddf0cfc04654ca3e524f4d311c5a62245ee231a1101280b43fd2ae3a`, and the
screen SHA-256 is
`d869c72bd610fcc70d7d5fdcbb353afebc8c6630d1d03af1e75e6044c58bedcb`.
The four retained trace SHA-256 values are recorded in the batch result.
Rows are sorted per rewrite by
`SHA-256(perminov-q-c15-v1:neighbour:support_index)` then interleaved in the
fixed rewrite order 1--6.

Before production, a synthetic twelve-row interruption control checkpointed
after each row, stopped after row 4, resumed at row 5, and matched the
uninterrupted sequence exactly.  It establishes that a saved cursor is the
actual first unvisited row without evaluating a production trace row.

CPU 0 processed the next 12,000 rows (orders 1920--13919), 2,000 per recorded
rewrite, in 474.504 seconds.  The old integral gate and exact-Q recovery both
found zero reductions.  The append-only record has SHA-256
`ce605b5da2d13fe513c57e9c7d3b4c62872d8ca8e5bc4891bfa424a3da4cd7d5`.
The first unvisited row is order 13920: rewrite 1, support index 62141,
`[0,5,14,15,18,21,22]`.

The inherited exact positive control remains checked: the old gate returns no
replacement for
`4e0⊗e0⊗e0 + 2e0⊗e0⊗e1 + 2e0⊗e1⊗e0 + e0⊗e1⊗e1`, while exact-Q recovery
returns the one-term identity `4e0⊗(e0+e1/2)⊗(e0+e1/2)`.  This is not an
individual summand rescaling because both complementary factors vary.
