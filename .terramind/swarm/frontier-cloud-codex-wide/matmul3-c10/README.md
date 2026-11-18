# c10 exact seven-term continuations

## Recovered c9 continuation

`recovery-sha256.txt` verifies the c9 source, screen, checkpoint, and trace.
The exact recovered cursor was neighbour 6, support index 42,387,
`[0,3,6,9,17,21,22]`.  `seven-term-c10-*` completes its 202,770 remaining
seven-subsets on CPU 0.  It found no constructive reduction; its final result
has `resume_cursor.complete: true`.  The temporary overlapping resume was
interrupted and has no role in the authoritative result; its checkpoint and
trace are retained only as audit evidence.

Together with c6--c9, this completes all seven fixed Perminov neighbours at
support size seven: 1,716,099 supports total, 216,593 low-flattening cases,
and zero constructive reductions.  This is only a result for the stated
integral factorization criterion, not a tensor-rank lower bound.

## Distinct public seed

`sun-56a/` preserves the public certificate from
`https://github.com/sunyinqi0508/3by3r23-56a` (retrieved 2026-11-18), which
documents a ternary, exact rank-23, 56-addition scheme.  Its upstream
`verify.py` passes its integer Brent-equation checks.  The converted
`sun-frontier-witness.json` also passes Frontier diagnose and ties the known
rank-23 value.  `shared-factor-analysis.json` finds seven legal projective
single-factor pairs, so this is a distinct seed and rewrite family.

`seven_term_sun.py` is the same constructive-factorization screen with a
Frontier-witness decoder.  Its first Sun neighbour, move `[0,2,18]`, exhausted
all 245,157 seven-subsets on CPU 0: 26,709 low-flattening cases and zero
constructive reductions.  The exact next cursor is neighbour 1, support index
0, `[0,1,2,3,4,5,6]`.

No rank-22 candidate was emitted in either c10 screen, so candidate Frontier
diagnosis/check was not applicable.  The baseline checks and repository gate
are retained in this directory.
