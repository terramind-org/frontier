# c17 restart-reconciled exact-Q Perminov continuation

c17 recovered the reachable amended c16 commit `8c645ace` as artifact
evidence, not merely from its transcript.  Every c16 manifest entry verifies,
including the 12,000-line append-only record, its atomic cursor, the exact-Q
positive control, and the synthetic interruption control.  The c15 two-part
result (orders 0--1535 and 1536--1919) plus c16 records join without a gap to
orders 0--13919.

The retained order is unchanged: sort low-flattening rows in each recorded
rewrite by `SHA-256(perminov-q-c15-v1:neighbour:support_index)`, then
round-robin rewrites 1--6.  Rewrite 0 remains excluded because it has no
retained trace.  c17 began only at order 13920, the supplied rewrite-1 row
with support index 62141 and support `[0,5,14,15,18,21,22]`.

The c17 writer appends and fsyncs each row before atomically replacing its
cursor.  A restart reconciles every pre-existing JSONL line against the
deterministic order and resumes at the first absent order; the second c17
batch recovered 12,000 prior records and therefore began at order 25920
without replay.

Two fresh 12,000-row batches completed on CPU 0: orders 13920--25919 and
25920--37919, 4,000 rows per rewrite in c17.  Old integral recovery and exact
rational recovery both found zero reductions.  Combined coverage is 6,320
rows per recorded rewrite (37,920 total), with no rank-22 witness to diagnose
or check.  The exact next cursor is order 37920, rewrite 1, support index
174139, `[3,4,8,15,16,18,20]`.

This remains a bounded exact-Q trace sample, not an exhaustive rational
screen or a tensor-rank lower bound.
